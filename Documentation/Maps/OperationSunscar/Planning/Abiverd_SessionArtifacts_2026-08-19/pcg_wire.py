import sys, json
sys.path.insert(0,'/tmp')
from importlib.machinery import SourceFileLoader
ue=SourceFileLoader('ue','/tmp/ue.py').load_module()
PCG='PCGToolset.PCGToolset'
B='/Game/Maps/Sunscar/PCG/PCG_ABV_PoppyField_V1.PCG_ABV_PoppyField_V1:'
N=lambda n:{'refPath':B+n}

EDGES=[
 ('ABV_GetLandscape','Out','ABV_PoppySampler','Surface'),
 ('ABV_PoppySampler','Out','ABV_PoppyTransform','In'),
 ('ABV_PoppyTransform','Out','ABV_PoppySpawner','In'),
 ('ABV_GetLandscape','Out','ABV_GrassSampler','Surface'),
 ('ABV_GrassSampler','Out','ABV_GrassTransform','In'),
 ('ABV_GrassTransform','Out','ABV_GrassSpawner','In'),
]
for fn,fp,tn,tp in EDGES:
    r=ue.tool(PCG,'ConnectNodePins',{'fromNode':N(fn),'fromPinLabel':fp,'toNode':N(tn),'toPinLabel':tp})
    ok = r.get('returnValue') if isinstance(r,dict) else None
    print('%-22s %-8s -> %-22s %-8s : %s' % (fn,fp,tn,tp, json.dumps(r)[:110]))
