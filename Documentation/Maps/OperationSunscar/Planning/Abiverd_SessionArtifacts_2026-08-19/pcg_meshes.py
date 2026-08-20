import sys, json
sys.path.insert(0,'/tmp')
from importlib.machinery import SourceFileLoader
ue=SourceFileLoader('ue','/tmp/ue.py').load_module()
OBJ='editor_toolset.toolsets.object.ObjectTools'
BASE='/Game/Maps/Sunscar/PCG/PCG_ABV_PoppyField_V1.PCG_ABV_PoppyField_V1:'

def mesh(folder, name):
    p='/Game/Maps/Sunscar/Art/Heritage/Foliage/%s/%s' % (folder, name)
    return {'refPath': p+'.'+name}

def entry(folder, name, weight):
    return {'descriptor': {'staticMesh': mesh(folder,name)},
            'weight': weight, 'displayName': name}

# Poppies: measured heights VarA 64.4, VarC 69.1, VarF 49 (s6).
# Favour the tall ones for crouch concealment; VarF (shortest) down-weighted.
POPPY=[entry('FieldPoppy','SM_FieldPoppy_Var'+v,w) for v,w in
       [('A',18),('B',14),('C',18),('D',14),('E',12),('F',6),('G',10),('H',8)]]
# Grass: VarA is the only tall one (~35cm); rest are 10-19cm low filler.
GRASS=[entry('WildGrass','SM_WildGrass_Var'+v,w) for v,w in
       [('A',60),('B',10),('C',10),('D',10),('E',10)]]

TARGETS=[('ABV_PoppySpawner', POPPY, 'poppy'), ('ABV_GrassSpawner', GRASS, 'grass')]
# resolve each spawner's selector subobject path from the graph itself
gs=ue.tool('PCGToolset.PCGToolset','GetGraphStructure',
           {'graph':{'refPath':'/Game/Maps/Sunscar/PCG/PCG_ABV_PoppyField_V1.PCG_ABV_PoppyField_V1'}})
gv=gs.get('returnValue',gs); gd=json.loads(gv) if isinstance(gv,str) else gv
SEL={n['name']: n['paramOverrides']['meshSelectorParameters']['refPath']
     for n in gd['nodes'] if n['nodeType']=='Static Mesh Spawner'}
print('resolved selectors:', json.dumps(SEL, indent=1))

for node, entries, tag in TARGETS:
    sel = SEL[node]
    payload = json.dumps({'meshEntries': entries})     # values MUST be a JSON string
    r = ue.tool(OBJ,'set_properties',{'instance':{'refPath':sel},'values':payload})
    print('%s set_properties -> %s' % (tag, json.dumps(r)[:150]))
    back = ue.tool(OBJ,'get_properties',{'instance':{'refPath':sel},'properties':['meshEntries']})
    v = back.get('returnValue')
    d = json.loads(v) if isinstance(v,str) else v
    got = d.get('meshEntries') or []
    print('   readback: %d entries' % len(got))
    for e in got:
        sm = (e.get('descriptor') or {}).get('staticMesh') or ''
        sm = sm.get('refPath','?') if isinstance(sm,dict) else str(sm)
        print('     w=%-3s %s' % (e.get('weight'), sm.split('/')[-1]))
