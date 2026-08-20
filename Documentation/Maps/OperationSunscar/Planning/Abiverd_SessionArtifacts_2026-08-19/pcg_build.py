import sys, json
sys.path.insert(0,'/tmp')
from importlib.machinery import SourceFileLoader
ue=SourceFileLoader('ue','/tmp/ue.py').load_module()
PCG='PCGToolset.PCGToolset'
G={'refPath':'/Game/Maps/Sunscar/PCG/PCG_ABV_PoppyField_V1.PCG_ABV_PoppyField_V1'}

def add(node_type, name, params=None, title=None):
    a={'graph':G,'nativeNodeType':node_type,'nodeName':name,'jsonParams':json.dumps(params or {}),'nodeTitle':title or name,'nodeComment':''}


    r=ue.tool(PCG,'AddNode',a)
    v=r.get('returnValue')
    print('  add %-16s -> %s' % (name, json.dumps(v)[:120] if v else json.dumps(r)[:200]))
    return v

nodes={}
print('LANDSCAPE / SURFACE SOURCE')
nodes['land'] = add('Get Landscape Data','ABV_GetLandscape', None, 'Ground')

print('POPPY BRANCH')
nodes['psamp'] = add('Surface Sampler','ABV_PoppySampler', {
    'pointsPerSquaredMeter': 11.0,
    'pointExtents': {'x':10.0,'y':10.0,'z':10.0},
    'looseness': 1.0,
}, 'Poppy Scatter 11/m2')
nodes['pxform'] = add('Transform Points','ABV_PoppyTransform', {
    'rotationMin': {'pitch':-4.0,'yaw':0.0,'roll':-4.0},
    'rotationMax': {'pitch': 4.0,'yaw':360.0,'roll': 4.0},
    'scaleMin': {'x':1.15,'y':1.15,'z':1.15},
    'scaleMax': {'x':1.45,'y':1.45,'z':1.45},
    'bUniformScale': True,
}, 'Poppy Vary 1.15-1.45')
nodes['pspawn'] = add('Static Mesh Spawner','ABV_PoppySpawner', {
    'bSynchronousLoad': True,
}, 'Poppy Meshes')

print('GRASS BRANCH')
nodes['gsamp'] = add('Surface Sampler','ABV_GrassSampler', {
    'pointsPerSquaredMeter': 22.0,
    'pointExtents': {'x':8.0,'y':8.0,'z':8.0},
    'looseness': 1.0,
}, 'Grass Scatter 22/m2')
nodes['gxform'] = add('Transform Points','ABV_GrassTransform', {
    'rotationMin': {'pitch':-6.0,'yaw':0.0,'roll':-6.0},
    'rotationMax': {'pitch': 6.0,'yaw':360.0,'roll': 6.0},
    'scaleMin': {'x':1.5,'y':1.5,'z':1.5},
    'scaleMax': {'x':2.0,'y':2.0,'z':2.0},
    'bUniformScale': True,
}, 'Grass Vary 1.5-2.0')
nodes['gspawn'] = add('Static Mesh Spawner','ABV_GrassSpawner', {
    'bSynchronousLoad': True,
}, 'Grass Meshes')

json.dump({k:v for k,v in nodes.items() if v}, open('/tmp/pcg_nodes_created.json','w'))
print('\nsaved node refs ->', list(nodes.keys()))
