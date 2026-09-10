import sys, json, math
sys.path.insert(0,'/tmp')
from importlib.machinery import SourceFileLoader
T=SourceFileLoader('tl','/tmp/terrain_lib.py').load_module()

SITES={
 'SS_003':(-11575,-9232,-7212,-5160),'SS_004':(-9728,-7000,-4103,-1300),
 'SS_005':(-6828,-3200,-1528,1800),  'SS_006':(-7440,-4984,3691,5716),
 'SS_007':(-3804,1400,1072,4372),    'SS_010':(-504,5610,6285,11910),
 'SS_011':(6347,9404,4065,6800),     'SS_012':(10722,13900,3801,6700),
 'SS_013':(9276,13080,-2194,1924),   'SS_015':(11576,14624,-5858,-2675),
 'SS_016':(4536,8600,-8158,-5000),   'SS_017':(976,5536,-10652,-8008),
 'SS_018':(-6683,-3500,-10161,-7300),'SS_008':(-3454,784,-4454,-972),
 'SS_009':(-1000,3032,-1800,1476),   'SS_014':(5200,10744,-3450,960)}
BUF=800.0
PROT=json.load(open('/tmp/protect_xy.json')); PROT_R=1400.0
def free(x,y):
    for (x0,x1,y0,y1) in SITES.values():
        if x0-BUF<=x<=x1+BUF and y0-BUF<=y<=y1+BUF: return False
    return not any(math.hypot(x-px,y-py)<PROT_R for px,py in PROT)

def check_line(ax,ay,bx,by,n=14):
    bad=[]
    for i in range(n+1):
        x=ax+(bx-ax)*i/n; y=ay+(by-ay)*i/n
        if not free(x,y): bad.append((round(x),round(y)))
    return bad

def build_bund(prefix, ax, ay, bx, by, height=165.0, radius=620.0, dry=False):
    """Low earth bank: chain of circle patches raised above local grade, tapered at ends."""
    L=math.hypot(bx-ax,by-ay)
    n=max(3,int(L//(radius*0.7)))
    base=[(ax+(bx-ax)*i/n, ay+(by-ay)*i/n) for i in range(n+1)]
    gs=T.grounds_batch(base)
    made=[]
    for i,((x,y),g) in enumerate(zip(base,gs)):
        if g is None: continue
        t=i/n
        taper=math.sin(t*math.pi)**0.5          # 0 at ends, 1 mid
        h=height*(0.35+0.65*taper)
        rad=radius*(0.85+0.25*taper)
        nm='%s_%02d'%(prefix,i)
        if dry:
            made.append({'name':nm,'x':round(x),'y':round(y),'grade':round(g),'top':round(g+h),'h':round(h),'r':round(rad)})
        else:
            ref=T.patch_actor(nm, x, y, g+h, rad, rad*0.5)
            if ref: made.append({'name':nm,'ref':ref,'x':x,'y':y,'grade':g,'h':h})
    return made
