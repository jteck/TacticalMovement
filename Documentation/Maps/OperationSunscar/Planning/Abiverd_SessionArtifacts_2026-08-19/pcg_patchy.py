import sys, json
sys.path.insert(0,'/tmp')
from importlib.machinery import SourceFileLoader
ue=SourceFileLoader('ue','/tmp/ue.py').load_module()
PCG='PCGToolset.PCGToolset'
GP='/Game/Maps/Sunscar/PCG/PCG_ABV_PoppyField_V1.PCG_ABV_PoppyField_V1'
G={'refPath':GP}
N=lambda n:{'refPath':GP+':'+n}

def add(t,name,params,title):
    r=ue.tool(PCG,'AddNode',{'graph':G,'nativeNodeType':t,'nodeName':name,
        'jsonParams':json.dumps(params),'nodeTitle':title,'nodeComment':''})
    print('  add %-24s %s' % (name, 'OK' if r.get('returnValue') else json.dumps(r)[:160]))
    return r.get('returnValue')

def conn(fn,fp,tn,tp):
    r=ue.tool(PCG,'ConnectNodePins',{'fromNode':N(fn),'fromPinLabel':fp,'toNode':N(tn),'toPinLabel':tp})
    print('  wire %-22s %-14s -> %-24s %-14s %s' % (fn,fp,tn,tp,json.dumps(r)[:60]))

def disc(fn,fp,tn,tp):
    r=ue.tool(PCG,'DisconnectNodePins',{'fromNode':N(fn),'fromPinLabel':fp,'toNode':N(tn),'toPinLabel':tp})
    print('  cut  %-22s %-14s -> %-24s %s' % (fn,fp,tn,json.dumps(r)[:60]))

def thresh(val, inclusive=True):
    return {'bInclusive':inclusive,'bUseConstantThreshold':True,
            'attributeTypes':{'type':'Double','doubleValue':val,'floatValue':val}}

# noise scale: smaller = larger blobs. 0.002 -> features ~5m
def noise_params(offset):
    return {'mode':'FractionalBrownian2D','valueTarget':'$Density','iterations':4,
            'brightness':0.0,'contrast':1.0,
            'transform':{'location':{'x':offset,'y':offset,'z':0.0},
                         'rotation':{'pitch':0.0,'yaw':0.0,'roll':0.0},
                         'scale3D':{'x':0.002,'y':0.002,'z':0.002}}}

print('1) cut sampler -> transform on both branches')
disc('ABV_PoppySampler','Out','ABV_PoppyTransform','In')
disc('ABV_GrassSampler','Out','ABV_GrassTransform','In')

print('2) add noise + density filter nodes')
add('Spatial Noise','ABV_PoppyNoise', noise_params(0.0),    'Poppy Patchiness')
add('Filter Attribute Elements by Range','ABV_PoppyDensity',
    {'targetAttribute':'$Density','minThreshold':thresh(0.42),'maxThreshold':thresh(1.0),
     'bWarnOnDataMissingAttribute':False}, 'Keep Density > 0.42')
add('Spatial Noise','ABV_GrassNoise', noise_params(9137.0), 'Grass Patchiness')
add('Filter Attribute Elements by Range','ABV_GrassDensity',
    {'targetAttribute':'$Density','minThreshold':thresh(0.30),'maxThreshold':thresh(1.0),
     'bWarnOnDataMissingAttribute':False}, 'Keep Density > 0.30')

print('3) rewire through noise + filter')
conn('ABV_PoppySampler','Out','ABV_PoppyNoise','In')
conn('ABV_PoppyNoise','Out','ABV_PoppyDensity','In')
conn('ABV_PoppyDensity','InsideFilter','ABV_PoppyTransform','In')
conn('ABV_GrassSampler','Out','ABV_GrassNoise','In')
conn('ABV_GrassNoise','Out','ABV_GrassDensity','In')
conn('ABV_GrassDensity','InsideFilter','ABV_GrassTransform','In')

print('4) raise sampler density to compensate for what the filter removes')
for node, ppsm, ext in [('ABV_PoppySampler',18.0,10.0), ('ABV_GrassSampler',30.0,8.0)]:
    r=ue.tool(PCG,'UpdateNode',{'node':N(node),
        'jsonParams':json.dumps({'pointsPerSquaredMeter':ppsm,
            'pointExtents':{'x':ext,'y':ext,'z':ext},'looseness':1.0}),
        'nodeTitle':''})
    print('  %-20s -> %.0f/m2  %s' % (node, ppsm, json.dumps(r)[:60]))
