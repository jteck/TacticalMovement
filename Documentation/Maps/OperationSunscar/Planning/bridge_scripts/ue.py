#!/usr/bin/env python3
import json,sys
sys.path.insert(0,'/tmp')
from importlib.machinery import SourceFileLoader
mcp=SourceFileLoader('mcp','/tmp/mcp.py').load_module()
def tool(ts, name, args=None):
    r=mcp.call("tools/call",{"name":"call_tool","arguments":{"toolset_name":ts,"tool_name":name,"arguments":args or {}}})
    c=r.get('result',{}).get('content',[])
    txt=''.join(x.get('text','') for x in c)
    try: return json.loads(txt)
    except Exception: return {"_text":txt, "_err":r.get('error')}
SCENE="editor_toolset.toolsets.scene.SceneTools"
if __name__=="__main__":
    print(json.dumps(tool(sys.argv[1], sys.argv[2], json.loads(sys.argv[3]) if len(sys.argv)>3 else {}), indent=1))
