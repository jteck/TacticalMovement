import json,sys
from importlib.machinery import SourceFileLoader
ue=SourceFileLoader('ue','/tmp/ue.py').load_module()
SCENE="editor_toolset.toolsets.scene.SceneTools"
ACTOR="editor_toolset.toolsets.actor.ActorTools"
OBJ="editor_toolset.toolsets.object.ObjectTools"
def find(name):
    r=ue.tool(SCENE,"find_actors",{"name":name,"tag":"","collision_channels":[]})
    return [a["refPath"] for a in r.get("returnValue",[])]
def rep(ref): return {"refPath":ref}
def label(ref): return ue.tool(ACTOR,"get_label",{"actor":rep(ref)}).get("returnValue")
def xform(ref): return ue.tool(ACTOR,"get_actor_transform",{"actor":rep(ref)}).get("returnValue")
def bounds(ref): return ue.tool(ACTOR,"get_actor_bounds",{"actor":rep(ref)}).get("returnValue")
def tags(ref):  return ue.tool(ACTOR,"get_tags",{"actor":rep(ref)}).get("returnValue")
def props(ref,names): return ue.tool(OBJ,"get_properties",{"instance":rep(ref),"properties":names}).get("returnValue")
def listprops(ref): return ue.tool(OBJ,"list_properties",{"instance":rep(ref)}).get("returnValue")
def comps(ref,ct=None):
    a={"actor":rep(ref)}
    if ct: a["component_type"]=ct
    return [c["refPath"] for c in (ue.tool(ACTOR,"get_components",a).get("returnValue") or [])]
