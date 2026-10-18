"""Builds Viewpoint pack models (OBJ+MTL+PNG) for PZ tiles from the game's
tileGeometry shapes (or the wall a WallObject hangs on), textured by
projecting each vertex back onto the tile's own isometric sprite."""
import math,json,os,sys
import numpy as np
from PIL import Image
U=10000.0              # tileGeometry units per tile
LEVEL=2.44949          # one storey, in tiles (192 px at 2x)
ZPX=192/LEVEL          # screen px per tile of height at 2x
WALL=0.05              # wall face inset from the tile edge (wall half-thickness ~0.0235)

def proj(X,Y,Z):
    """PZ frame (x east, y south, z up; tile-centre origin) -> 2x sprite px."""
    return 64+64*(X-Y), 224+32*(X+Y)-ZPX*Z

def rot_matrix(r):
    ax,ay,az=(math.radians(v/U) for v in r)
    cx,sx,cy,sy,cz,sz=math.cos(ax),math.sin(ax),math.cos(ay),math.sin(ay),math.cos(az),math.sin(az)
    Rx=np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]]);Ry=np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]]);Rz=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])
    return Rx@Ry@Rz

def to_pz(p):
    """tileGeometry (x, y up, z south) in units -> PZ frame in tiles."""
    return (p[0]/U, p[2]/U, p[1]/U)

def box(sh):
    mn,mx=np.array(sh['min'],float),np.array(sh['max'],float)
    c=[np.array([mx[0] if i&1 else mn[0], mx[1] if i&2 else mn[1], mx[2] if i&4 else mn[2]]) for i in range(8)]
    quads=[(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)]
    return c,quads

def cylinder(sh,seg=12):
    r1,r2,h=sh.get('radius1',0),sh.get('radius2',0),sh.get('height',0)
    c=[];quads=[]
    for i in range(seg):
        a=2*math.pi*i/seg
        c.append(np.array([r1*math.cos(a),r1*math.sin(a),-h/2]));c.append(np.array([r2*math.cos(a),r2*math.sin(a),h/2]))
    for i in range(seg):
        j=(i+1)%seg;quads.append((2*i,2*j,2*j+1,2*i+1))
    quads.append(tuple(2*i for i in reversed(range(seg))));quads.append(tuple(2*i+1 for i in range(seg)))
    return c,quads

def polygon(sh):
    pts=sh['points'];plane=sh.get('plane','XY')
    c=[]
    for a,b in pts:
        c.append(np.array([a,b,0.0]) if plane=='XY' else np.array([a,0.0,b]) if plane=='XZ' else np.array([0.0,a,b]))
    return c,[tuple(range(len(c)))]

def ear_clip(poly2d):
    idx=list(range(len(poly2d)));tris=[]
    area=sum(poly2d[i][0]*poly2d[(i+1)%len(poly2d)][1]-poly2d[(i+1)%len(poly2d)][0]*poly2d[i][1] for i in range(len(poly2d)))
    sgn=1 if area>0 else -1
    def inside(p,a,b,c):
        d=lambda u,v,w:(u[0]-w[0])*(v[1]-w[1])-(v[0]-w[0])*(u[1]-w[1])
        d1,d2,d3=d(p,a,b),d(p,b,c),d(p,c,a)
        return not((d1<0 or d2<0 or d3<0) and (d1>0 or d2>0 or d3>0))
    guard=0
    while len(idx)>3 and guard<10000:
        guard+=1
        for k in range(len(idx)):
            i0,i1,i2=idx[k-1],idx[k],idx[(k+1)%len(idx)]
            a,b,c=poly2d[i0],poly2d[i1],poly2d[i2]
            cr=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
            if cr*sgn<=0: continue
            if any(inside(poly2d[j],a,b,c) for j in idx if j not in(i0,i1,i2)): continue
            tris.append((i0,i1,i2));idx.pop(k);break
        else: break
    if len(idx)==3: tris.append(tuple(idx))
    return tris

def shapes_mesh(shapes):
    """-> list of triangles, each 3 PZ-frame points; polygons double-sided."""
    tris=[]
    for sh in shapes:
        t=sh['type']
        c,faces=box(sh) if t=='box' else cylinder(sh) if t=='cylinder' else polygon(sh)
        R=rot_matrix(sh.get('rotate',(0,0,0)));T=np.array(sh.get('translate',(0,0,0)),float)
        w=[to_pz(R@p+T) for p in c]
        for f in faces:
            if t=='polygon':
                pl=sh.get('plane','XY');ax=(0,1) if pl=='XY' else (0,2) if pl=='XZ' else (1,2)
                for a,b,cc in ear_clip([(c[i][ax[0]],c[i][ax[1]]) for i in f]):
                    tris.append((w[f[a]],w[f[b]],w[f[cc]]));tris.append((w[f[a]],w[f[cc]],w[f[b]]))
            else:
                for k in range(1,len(f)-1): tris.append((w[f[0]],w[f[k]],w[f[k+1]]))
    return tris

def wall_mesh(img,side):
    """A plate on the north (side 'N') or west ('W') wall covering the sprite's art."""
    a=np.asarray(img)[:,:,3];ys,xs=np.nonzero(a>8)
    if len(xs)==0: return []
    sx,sy=xs+0.5,ys+0.5;c=-0.5+WALL
    if side=='N':   # plane Y=c: X from sx, Z from sy
        u=(sx-64)/64+c; Z=(224+32*(u+c)-sy)/ZPX; P=lambda u,z:(u,c,z)
    else:           # plane X=c: Y from sx
        u=c-(sx-64)/64; Z=(224+32*(c+u)-sy)/ZPX; P=lambda u,z:(c,u,z)
    u0,u1=max(u.min()-0.01,-0.5),min(u.max()+0.01,0.5);z0,z1=max(Z.min()-0.01,0.0),Z.max()+0.01
    q=[P(u0,z0),P(u1,z0),P(u1,z1),P(u0,z1)]
    return [(q[0],q[1],q[2]),(q[0],q[2],q[3]),(q[0],q[2],q[1]),(q[0],q[3],q[2])]

def write_model(name,tris,img,outdir):
    """Writes outdir/model.obj, model.mtl, texture.png. Returns False if empty."""
    if not tris: return False
    a=np.asarray(img)[:,:,3];ys,xs=np.nonzero(a>0)
    if len(xs)==0: return False
    x0,y0,x1,y1=max(xs.min()-1,0),max(ys.min()-1,0),min(xs.max()+2,img.width),min(ys.max()+2,img.height)
    tex=img.crop((x0,y0,x1,y1));tw,th=tex.size
    os.makedirs(outdir,exist_ok=True);tex.save(os.path.join(outdir,'texture.png'),optimize=True)
    with open(os.path.join(outdir,'model.mtl'),'w') as f: f.write('newmtl atlas\nKd 1 1 1\nd 1\nmap_Kd texture.png\n')
    vs={};vl=[];tl=[];fl=[]
    def vid(p):
        k=tuple(round(v,5) for v in p)
        if k not in vs:
            vs[k]=len(vl)+1;vl.append(k);sx,sy=proj(*p)
            tl.append((min(max((sx-x0)/tw,0),1),min(max(1-(sy-y0)/th,0),1)))
        return vs[k]
    for t in tris:
        ids=[vid(p) for p in t]
        if len(set(ids))==3: fl.append(ids)
    with open(os.path.join(outdir,'model.obj'),'w') as f:
        f.write('# %s: generated from the game tile geometry, textured by iso projection of its sprite; pz frame, tile-centre origin\nmtllib model.mtl\n'%name)
        for v in vl: f.write('v %g %g %g\n'%v)
        for t in tl: f.write('vt %.5f %.5f\n'%t)
        f.write('usemtl atlas\n')
        for a,b,c in fl: f.write('f %d/%d %d/%d %d/%d\n'%(a,a,b,b,c,c))
    return True
