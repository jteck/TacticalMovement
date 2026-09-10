#!/usr/bin/env python3
"""MCP bridge client for the UE editor (curl transport, cached session)."""
import json, subprocess, sys

URL = "http://127.0.0.1:8000/mcp"

def _curl(payload, sid=None, timeout=600):
    cmd = ["curl","-s","-X","POST",URL,
           "-H","Content-Type: application/json",
           "-H","Accept: application/json, text/event-stream"]
    if sid: cmd += ["-H", f"Mcp-Session-Id: {sid}"]
    cmd += ["-d", json.dumps(payload)]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout).stdout
    if not out.strip():
        return None
    # SSE framing: collect data: payloads (may themselves span lines)
    if "data:" in out:
        chunks, cur = [], []
        for line in out.split("\n"):
            if line.startswith("data:"):
                if cur: chunks.append("\n".join(cur))
                cur = [line[5:].strip()]
            elif cur:
                cur.append(line)
        if cur: chunks.append("\n".join(cur))
        for c in reversed(chunks):
            try: return json.loads(c)
            except json.JSONDecodeError: continue
    # plain JSON body, possibly pretty-printed across many lines
    try: return json.loads(out)
    except json.JSONDecodeError: pass
    i = out.find("{")
    if i >= 0:
        try: return json.loads(out[i:])
        except json.JSONDecodeError: pass
    return None

def session():
    cmd = ["curl","-s","-D-","-X","POST",URL,
           "-H","Content-Type: application/json",
           "-H","Accept: application/json, text/event-stream",
           "-d", json.dumps({"jsonrpc":"2.0","id":1,"method":"initialize",
                             "params":{"protocolVersion":"2025-06-18","capabilities":{},
                                       "clientInfo":{"name":"cc","version":"1"}}}),
           "-o","/dev/null"]
    hdr = subprocess.run(cmd, capture_output=True, text=True, timeout=120).stdout
    sid = None
    for line in hdr.split("\n"):
        if line.lower().startswith("mcp-session-id:"):
            sid = line.split(":",1)[1].strip()
    _curl({"jsonrpc":"2.0","method":"notifications/initialized"}, sid)
    return sid

_SID = [None]
_n = [1]
def _sid():
    if _SID[0] is None: _SID[0] = session()
    return _SID[0]

def call(method, params=None):
    """Generic JSON-RPC call with a cached session."""
    _n[0] += 1
    return _curl({"jsonrpc":"2.0","id":_n[0],"method":method,"params":params or {}}, _sid())

def call_tool(name, args):
    return call("tools/call", {"name":name,"arguments":args})

def text(r):
    if not r: return "<empty>"
    if "error" in r: return "ERROR: " + json.dumps(r["error"])
    res = r.get("result", {})
    parts = [c["text"] for c in res.get("content", []) if c.get("type")=="text"]
    if parts: return "\n".join(parts)
    return json.dumps(res, indent=2)
