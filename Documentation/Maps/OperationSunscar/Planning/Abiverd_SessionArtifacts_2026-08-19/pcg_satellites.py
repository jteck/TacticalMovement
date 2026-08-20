import sys, json, time
sys.path.insert(0,'/tmp')
from importlib.machinery import SourceFileLoader
ue=SourceFileLoader('ue','/tmp/ue.py').load_module()
A=SourceFileLoader('audit','/tmp/audit.py').load_module()
PCG='PCGToolset.PCGToolset'; ACTOR='editor_toolset.toolsets.actor.ActorTools'
OBJ='editor_toolset.toolsets.object.ObjectTools'
GP='/Game/Maps/Sunscar/PCG/PCG_ABV_PoppyField_V1.PCG_ABV_PoppyField_V1'

# Straddle the main field's edges (X 400..3400, Y 4500..6300) with rotated lobes
# on the open-sand sides, so the boundary stops reading as a straight line.
SATS=[
 ('ABV_PCG_PoppyField_LobeS_V1',  1150.0, 4470.0, 22.0, 5.0, 2.0),
 ('ABV_PCG_PoppyField_LobeSW_V1',  520.0, 4760.0, -28.0, 3.0, 2.5),
 ('ABV_PCG_PoppyField_LobeW_V1',   430.0, 5650.0, 15.0, 2.0, 4.0),
 ('ABV_PCG_PoppyField_LobeSE_V1', 3180.0, 4820.0, 35.0, 2.5, 2.0),
]
refs=[]
for name, x, y, yaw, sx, sy in SATS:
    r=ue.tool(PCG,'SpawnGraphInstance',{'graph':{'refPath':GP},'name':name,
        'transform':{'location':{'x':x,'y':y,'z':34890.0},
                     'rotation':{'pitch':0.0,'yaw':0.0,'roll':0.0},
                     'scale3D':{'x':1.0,'y':1.0,'z':1.0}},'jsonParams':'{}'})
    rv=r.get('returnValue')
    if not rv: print('%-32s SPAWN FAIL %s'%(name,json.dumps(r)[:140])); continue
    ref=rv['actor']['refPath']
    ue.tool(ACTOR,'set_actor_transform',{'actor':{'refPath':ref},
        'xform':{'location':{'x':x,'y':y,'z':34890.0},
                 'rotation':{'pitch':0.0,'yaw':yaw,'roll':0.0},
                 'scale':{'x':sx,'y':sy,'z':10.0}},'worldspace':True})
    ue.tool(PCG,'ExecuteGraphInstance',{'pCGVolume':{'refPath':ref}})
    refs.append((name,ref))
    b=A.bounds(ref)
    print('%-32s yaw %+5.0f  bounds X %.0f..%.0f  Y %.0f..%.0f'
          % (name, yaw, b['min']['x'], b['max']['x'], b['min']['y'], b['max']['y']))

def count(ref):
    tot=0
    for c in A.comps(ref):
        cn=c.split('.')[-1]
        if not cn.startswith('ISM_'): continue
        d=ue.tool(OBJ,'get_properties',{'instance':{'refPath':c},'properties':['perInstanceSMData']}).get('returnValue')
        tot+= len(json.loads(d)['perInstanceSMData']) if d else 0
    return tot

grand=0
for name, ref in refs:
    k=count(ref); grand+=k
    print('  %-32s %6d instances'%(name,k))
open('/tmp/pcg_sat_refs.json','w').write(json.dumps(refs))
print('satellite instances total:', grand)
