import sys, json
sys.path.insert(0,'/tmp')
from importlib.machinery import SourceFileLoader
ue=SourceFileLoader('ue','/tmp/ue.py').load_module()
PCG='PCGToolset.PCGToolset'; OBJ='editor_toolset.toolsets.object.ObjectTools'
GP='/Game/Maps/Sunscar/PCG/PCG_ABV_PoppyField_V1.PCG_ABV_PoppyField_V1:'
vol=open('/tmp/pcg_volume_ref.txt').read().strip()

def settings(node):
    si=ue.tool(OBJ,'get_properties',{'instance':{'refPath':GP+node},'properties':['settingsInterface']}).get('returnValue')
    return (json.loads(si) if isinstance(si,str) else si)['settingsInterface']['refPath']

def thresh(val, inc=True):
    return {'bInclusive':inc,'bUseConstantThreshold':True,
            'attributeTypes':{'type':'Double','doubleValue':val,'floatValue':val}}

# 1. put both noise nodes on the only setting that produces real spread
for node, off in [('ABV_PoppyNoise',0.0),('ABV_GrassNoise',9137.0)]:
    ue.tool(OBJ,'set_properties',{'instance':{'refPath':settings(node)},'values':json.dumps({
        'mode':'FractionalBrownian2D','iterations':4,'contrast':1.0,'brightness':0.0,
        'transform':{'location':{'x':off,'y':off,'z':0.0},
                     'rotation':{'pitch':0.0,'yaw':0.0,'roll':0.0},
                     'scale':{'x':1.0,'y':1.0,'z':1.0}}})})
ue.tool(PCG,'ExecuteGraphInstance',{'pCGVolume':{'refPath':vol}})

# 2. measure each branch's real distribution, pick the threshold that hits the target cull
TARGET={'ABV_PoppyNoise':0.40, 'ABV_GrassNoise':0.27}
picked={}
for node, filt in [('ABV_PoppyNoise','ABV_PoppyDensity'),('ABV_GrassNoise','ABV_GrassDensity')]:
    r=ue.tool(PCG,'GetNodeDataView',{'pCGVolume':{'refPath':vol},'node':{'refPath':GP+node},
        'attributeName':'$Density','pinLabel':'Out','startIndex':0,'count':20000})
    vals=sorted(e['$Density'] for k,e in json.loads(r['returnValue']).items() if k.startswith('element_'))
    n=len(vals); t=TARGET[node]
    cut=vals[int(n*t)]
    picked[filt]=cut
    print('%-16s n=%-6d range %.3f..%.3f  -> threshold %.4f for %.0f%% cull'
          % (node, n, vals[0], vals[-1], cut, t*100))
    ue.tool(OBJ,'set_properties',{'instance':{'refPath':settings(filt)},'values':json.dumps({
        'targetAttribute':'$Density','minThreshold':thresh(cut),'maxThreshold':thresh(2.0),
        'bWarnOnDataMissingAttribute':False})})

# 3. regenerate and count
ue.tool(PCG,'ExecuteGraphInstance',{'pCGVolume':{'refPath':vol}})
pop=gr=0
for n in ['SM_FieldPoppy_Var'+v for v in 'ABCDEFGH']+['SM_WildGrass_Var'+v for v in 'ABCDE']:
    v=ue.tool(OBJ,'get_properties',{'instance':{'refPath':vol+'.ISM_'+n+'_0'},'properties':['perInstanceSMData']}).get('returnValue')
    k=len(json.loads(v)['perInstanceSMData']) if v else 0
    if 'Poppy' in n: pop+=k
    else: gr+=k
print('\nAFTER: poppies %d (%.1f/m2)  grass %d (%.1f/m2)  total %d'%(pop,pop/540.0,gr,gr/540.0,pop+gr))
print('unfiltered was: poppies 9856 (18.3), grass 16256 (30.1)')
