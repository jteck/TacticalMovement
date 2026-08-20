import sys, json, time
sys.path.insert(0,'/tmp')
from importlib.machinery import SourceFileLoader
ue=SourceFileLoader('ue','/tmp/ue.py').load_module()
A=SourceFileLoader('audit','/tmp/audit.py').load_module()
PCG='PCGToolset.PCGToolset'; ACTOR='editor_toolset.toolsets.actor.ActorTools'
OBJ='editor_toolset.toolsets.object.ObjectTools'
GP='/Game/Maps/Sunscar/PCG/PCG_ABV_PoppyField_V1.PCG_ABV_PoppyField_V1'

old=open('/tmp/pcg_volume_ref.txt').read().strip()
print('removing old volume ...', ue.tool(ue.SCENE,'remove_from_scene',{'actor':{'refPath':old}}))

r=ue.tool(PCG,'SpawnGraphInstance',{'graph':{'refPath':GP},
    'name':'ABV_PCG_PoppyField_South_V1',
    'transform':{'location':{'x':1900.0,'y':5400.0,'z':34890.0},
                 'rotation':{'pitch':0.0,'yaw':0.0,'roll':0.0},
                 'scale3D':{'x':1.0,'y':1.0,'z':1.0}},
    'jsonParams':'{}'})
new=r['returnValue']['actor']['refPath']
open('/tmp/pcg_volume_ref.txt','w').write(new)
print('new volume:', new.split('.')[-1])

ue.tool(ACTOR,'set_actor_transform',{'actor':{'refPath':new},
   'xform':{'location':{'x':1900.0,'y':5400.0,'z':34890.0},
            'rotation':{'pitch':0.0,'yaw':0.0,'roll':0.0},
            'scale':{'x':15.0,'y':9.0,'z':10.0}},'worldspace':True})
print('bounds:', json.dumps(A.bounds(new)))

t0=time.time()
print('exec ->', ue.tool(PCG,'ExecuteGraphInstance',{'pCGVolume':{'refPath':new}}), '%.1fs'%(time.time()-t0))

pop=gr=0; rows=[]
for n in ['SM_FieldPoppy_Var'+v for v in 'ABCDEFGH']+['SM_WildGrass_Var'+v for v in 'ABCDE']:
    v=ue.tool(OBJ,'get_properties',{'instance':{'refPath':new+'.ISM_'+n+'_0'},'properties':['perInstanceSMData']}).get('returnValue')
    k=len(json.loads(v)['perInstanceSMData']) if v else 0
    rows.append((n,k))
    if 'Poppy' in n: pop+=k
    else: gr+=k
for n,k in rows: print('   %-24s %6d'%(n,k))
print('poppies %d (%.1f/m2)  grass %d (%.1f/m2)  TOTAL %d'%(pop,pop/540.0,gr,gr/540.0,pop+gr))
