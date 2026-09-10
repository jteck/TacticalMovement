import sys, json, math, time, subprocess
sys.path.insert(0,'/tmp')
from importlib.machinery import SourceFileLoader
ue=SourceFileLoader('ue','/tmp/ue.py').load_module()
A=SourceFileLoader('audit','/tmp/audit.py').load_module()
SCENE=ue.SCENE
ACTOR='editor_toolset.toolsets.actor.ActorTools'
OBJ='editor_toolset.toolsets.object.ObjectTools'
AT='editor_toolset.toolsets.asset.AssetTools'
PROG='editor_toolset.toolsets.programmatic.ProgrammaticToolset'
REPO='/Users/jasonteck/UnrealEngine/_worktrees/map-development'

def ground(x,y):
    d=ue.tool(SCENE,'trace_world',{'start':{'x':float(x),'y':float(y),'z':45000.0},
                                   'end':{'x':float(x),'y':float(y),'z':30000.0}}).get('returnValue')
    return None if d is None else 45000.0-d

def ground_under(actor_ref, x, y, z, tools):
    """TRUE terrain height under an actor, by lifting it clear and tracing.

    A plain trace hits the actor itself. An offset trace hits neighbours or reads
    a different point on undulating terrain. This is the only reliable method.

    WARNING: lifts the actor. Always restore in a finally block - if the process
    dies mid-lift the actor is stranded 500 m in the air.
    """
    ACTOR, ue_tool = tools
    LIFT = 50000.0
    try:
        ue_tool(ACTOR,'set_actor_transform',{'actor':{'refPath':actor_ref},
            'xform':{'location':{'x':x,'y':y,'z':z+LIFT}}})
        return ground(x,y)
    finally:
        ue_tool(ACTOR,'set_actor_transform',{'actor':{'refPath':actor_ref},
            'xform':{'location':{'x':x,'y':y,'z':z}}})

def ground_clear(x,y,r=200.0):
    """Ground height AVOIDING the object at (x,y).

    A plain downward trace hits whatever is first - including the very actor you
    are trying to seat, which makes re-grounding chase itself upward forever.
    Samples 4 points r cm out and takes the median. Use this whenever seating
    an object, never plain ground()."""
    vals=[ground(x+dx,y+dy) for dx,dy in ((r,0),(-r,0),(0,r),(0,-r))]
    vals=[v for v in vals if v is not None]
    if not vals: return None
    vals.sort()
    return vals[len(vals)//2]

def grounds_batch(pts):
    S='''
import json
def tr(x,y):
    r=execute_tool("editor_toolset.toolsets.scene.SceneTools.trace_world",
        json.dumps({"start":{"x":x,"y":y,"z":45000.0},"end":{"x":x,"y":y,"z":30000.0}}))
    return r.get("returnValue")
def run():
    out=[]
    for p in %s:
        d=tr(float(p[0]),float(p[1]))
        out.append(None if d is None else round(45000.0-d,1))
    return {"g":out}
''' % json.dumps([[p[0],p[1]] for p in pts])
    r=ue.tool(PROG,'execute_tool_script',{'script':S})
    v=r.get('returnValue',r); d=json.loads(v) if isinstance(v,str) else v
    return d['g']

def patch_actor(name, x, y, z, radius, falloff):
    r=ue.tool(SCENE,'add_to_scene_from_class',{'actor_type':{'refPath':'/Script/Engine.StaticMeshActor'},
       'name':name,'xform':{'location':{'x':float(x),'y':float(y),'z':float(z)},
       'rotation':{'pitch':0.0,'yaw':0.0,'roll':0.0},'scale':{'x':1.0,'y':1.0,'z':1.0}}})
    host=(r.get('returnValue') or {}).get('refPath')
    if not host: return None
    ue.tool(ACTOR,'set_label',{'actor':{'refPath':host},'label':name})
    ue.tool(ACTOR,'add_component',{'owner':{'refPath':host},
        'component_type':{'refPath':'/Script/LandscapePatch.LandscapeCircleHeightPatch'},'name':'Patch'})
    ue.tool(OBJ,'set_properties',{'instance':{'refPath':host+'.Patch'},
        'values':json.dumps({'radius':float(radius),'falloff':float(falloff),'bIsEnabled':True})})
    return host

def build_gully(prefix, ax, ay, bx, by, depth=190.0, radius=700.0, mean_amp=520.0, seed=0.0):
    L=math.hypot(bx-ax,by-ay); ux,uy=(bx-ax)/L,(by-ay)/L; px,py=-uy,ux
    n=max(3,int(L//(radius*0.8)))
    base=[(ax+(bx-ax)*i/n, ay+(by-ay)*i/n) for i in range(n+1)]
    gs=grounds_batch(base)
    made=[]
    for i,((x,y),g) in enumerate(zip(base,gs)):
        if g is None: continue
        t=i/n
        off = mean_amp*math.sin(t*math.pi*2.3+seed) + mean_amp*0.5*math.sin(t*math.pi*5.1+1.1+seed)
        nx,ny = x+px*off, y+py*off
        taper = math.sin(t*math.pi)**0.45
        d = depth*(0.45+0.55*taper); rad = radius*(0.82+0.30*taper)
        h=patch_actor('%s_%02d'%(prefix,i), nx, ny, g-d, rad, rad*0.38)
        if h: made.append({'name':'%s_%02d'%(prefix,i),'ref':h,'x':nx,'y':ny,'grade':g,'depth':d})
    return made

def save_terrain(actor_refs):
    """The rule: save actors, force landscape dirty, save landscape, CONFIRM disk changed."""
    before=int(subprocess.run(['git','-C',REPO,'status','--porcelain'],capture_output=True,text=True).stdout.count('\n'))
    if actor_refs:
        ue.tool(AT,'save_assets',{'asset_paths':list(actor_refs)})
    L=sorted(set(A.find('LandscapeStreamingProxy')+[m for m in A.find('Landscape') if 'StreamingProxy' not in m]))
    touched=0
    for p in L:
        cur=ue.tool(OBJ,'get_properties',{'instance':{'refPath':p},'properties':['streamingDistanceMultiplier']}).get('returnValue')
        try: val=json.loads(cur)['streamingDistanceMultiplier']
        except Exception: continue
        if ue.tool(OBJ,'set_properties',{'instance':{'refPath':p},'values':json.dumps({'streamingDistanceMultiplier':val})}).get('returnValue'):
            touched+=1
    ue.tool(AT,'save_assets',{'asset_paths':L})
    after=int(subprocess.run(['git','-C',REPO,'status','--porcelain'],capture_output=True,text=True).stdout.count('\n'))
    # git count only rises for NEW files; re-saving already-modified proxies shows no delta.
    # Check mtime instead - that is what actually proves the heights baked.
    import time, os
    now=time.time(); fresh=0
    for root,_,files in os.walk(REPO+'/Content/__ExternalActors__'):
        for f in files:
            if not f.endswith('.uasset'): continue
            fp=os.path.join(root,f)
            try:
                if os.path.getsize(fp)>100_000 and now-os.path.getmtime(fp)<120: fresh+=1
            except OSError: pass
    print('save_terrain: dirtied %d landscape actors; git %d -> %d; landscape proxies rewritten in last 2 min: %d'%(touched,before,after,fresh))
    if fresh==0:
        print('  *** WARNING: no landscape proxy rewritten - heights did NOT bake ***')
    return fresh
