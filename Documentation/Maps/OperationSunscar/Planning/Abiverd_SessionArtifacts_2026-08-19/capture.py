import sys, json, base64, os
sys.path.insert(0,'/tmp')
from importlib.machinery import SourceFileLoader
ue=SourceFileLoader('ue','/tmp/ue.py').load_module()
APP='EditorToolset.EditorAppToolset'
OUT='/private/tmp/claude-502/-Users-jasonteck/7171f2c1-16c4-42ad-9e77-15e303855105/scratchpad'
os.makedirs(OUT, exist_ok=True)

# eye height ~160cm above ground (~34890) = 35050
SHOTS=[
 ('01_across_field_eye', {'x':250.0,'y':5400.0,'z':35050.0}, {'pitch':-3.0,'yaw':0.0,'roll':0.0}),
 ('02_crouch_height',    {'x':900.0,'y':4700.0,'z':34980.0}, {'pitch':-2.0,'yaw':35.0,'roll':0.0}),
 ('03_oblique_overview', {'x':-400.0,'y':3900.0,'z':35600.0},{'pitch':-18.0,'yaw':40.0,'roll':0.0}),
]
for name, loc, rot in SHOTS:
    ue.tool(APP,'SetCameraTransform',{'transform':{'location':loc,'rotation':rot,'scale3D':{'x':1.0,'y':1.0,'z':1.0}}})
    img=None
    for attempt in range(2):          # first frame is a warm-up; keep the second
        r=ue.tool(APP,'CaptureViewport',{'annotations':[],
              'captureTransform':{'location':loc,'rotation':rot,'scale3D':{'x':1.0,'y':1.0,'z':1.0}}})
        v=(((r or {}).get('returnValue') or {}).get('image') or {}).get('data')

        img=v
    if not img:
        print('%-22s FAILED: %s' % (name, json.dumps(r)[:220])); continue
    try:
        raw=base64.b64decode(img)
    except Exception as e:
        print('%-22s decode err %s' % (name,e)); continue
    p=os.path.join(OUT,'poppyfield_%s.png'%name)
    open(p,'wb').write(raw)
    print('%-22s -> %s (%d KB)' % (name, p, len(raw)//1024))
