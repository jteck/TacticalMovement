import sys, math, zlib, struct, random
sys.path.insert(0,'/tmp')

# --- core region, matching District_Old_Town_Core ---
X0,X1,Y0,Y1 = -16000,16000,-12500,12500
W,H = 512,400                      # ~62 cm/px, 2x the 125 cm quad density
AMP  = 150.0                       # +/-150 cm -> 3 m peak-to-trough (plan: 1-3 m)
SCALE= 2*AMP                       # worldSpaceEncodingScale
SITE_MARGIN = 800.0                # zero-height zone beyond each footprint
FEATHER     = 1200.0               # smooth ramp from protected to full amplitude

SITES={
 'SS_003':(-11575,-9232,-7212,-5160),'SS_004':(-9728,-7000,-4103,-1300),
 'SS_005':(-6828,-3200,-1528,1800),  'SS_006':(-7440,-4984,3691,5716),
 'SS_007':(-3804,1400,1072,4372),    'SS_010':(-504,5610,6285,11910),
 'SS_011':(6347,9404,4065,6800),     'SS_012':(10722,13900,3801,6700),
 'SS_013':(9276,13080,-2194,1924),   'SS_015':(11576,14624,-5858,-2675),
 'SS_016':(4536,8600,-8158,-5000),   'SS_017':(976,5536,-10652,-8008),
 'SS_018':(-6683,-3500,-10161,-7300),'SS_008':(-3454,784,-4454,-972),
 'SS_009':(-1000,3032,-1800,1476),   'SS_014':(5200,10744,-3450,960)}
def rect_dist(x,y,r):
    x0,x1,y0,y1=r
    return math.hypot(max(x0-x,0,x-x1), max(y0-y,0,y-y1))

# --- value noise with fBm, deterministic ---
rnd=random.Random(1071)
def make_grid(n):
    return [[rnd.uniform(-1,1) for _ in range(n+1)] for _ in range(n+1)]
def smooth(t): return t*t*(3-2*t)
def sample(gr,u,v,n):
    x=u*n; y=v*n
    xi=int(x)%n; yi=int(y)%n
    xf=x-int(x); yf=y-int(y)
    a=gr[yi][xi]; b=gr[yi][xi+1]; c=gr[yi+1][xi]; d=gr[yi+1][xi+1]
    sx=smooth(xf); sy=smooth(yf)
    return (a*(1-sx)+b*sx)*(1-sy) + (c*(1-sx)+d*sx)*sy

OCT=[(4,1.0),(8,0.5),(16,0.28),(32,0.14),(64,0.07)]
grids={n:make_grid(n) for n,_ in OCT}
norm=sum(w for _,w in OCT)

rows=[]
for j in range(H):
    y = Y0 + (Y1-Y0)*j/(H-1)
    row=[]
    for i in range(W):
        x = X0 + (X1-X0)*i/(W-1)
        v = sum(sample(grids[n],i/W,j/H,n)*w for n,w in OCT)/norm
        # protection mask: 0 inside site+margin, ramping to 1 over FEATHER
        d = min(rect_dist(x,y,r) for r in SITES.values())
        if d <= SITE_MARGIN: m=0.0
        elif d >= SITE_MARGIN+FEATHER: m=1.0
        else: m=smooth((d-SITE_MARGIN)/FEATHER)
        h = v*m                                   # -1..1
        val = int(round((0.5 + 0.5*h)*65535))     # 0.5 == zero height
        row.append(max(0,min(65535,val)))
    rows.append(row)

# --- write 16-bit grayscale PNG (no PIL) ---
raw=b''
for row in rows:
    raw += b'\x00' + b''.join(struct.pack('>H',v) for v in row)
def chunk(t,d):
    c=struct.pack('>I',len(d))+t+d
    return c+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
png = b'\x89PNG\r\n\x1a\n'
png += chunk(b'IHDR', struct.pack('>IIBBBBB',W,H,16,0,0,0,0))
png += chunk(b'IDAT', zlib.compress(raw,9))
png += chunk(b'IEND', b'')
out='/Users/jasonteck/UnrealEngine/_worktrees/map-development/Documentation/Maps/OperationSunscar/SourceArt/Heightmaps/HM_Sunscar_CoreRelief.png'
import os; os.makedirs(os.path.dirname(out),exist_ok=True)
open(out,'wb').write(png)

flat=[v for r in rows for v in r]
zero=sum(1 for v in flat if abs(v-32768)<200)
print('wrote %s  (%dx%d, 16-bit)'%(out,W,H))
print('  amplitude +/- %.0f cm   worldSpaceEncodingScale %.0f   zeroInEncoding 0.5'%(AMP,SCALE))
print('  value range %d..%d  (32768 = zero height)'%(min(flat),max(flat)))
print('  pixels at zero height (site-protected): %d / %d = %.1f%%'%(zero,len(flat),100*zero/len(flat)))
