"""Finds every PZ sprite that still has no model and generates one.
Order of preference: the tile's own tileGeometry, the geometry of the tile its
depth texture is borrowed from, a plate on the wall it hangs on, and for
anything else two crossed upright planes carrying its art."""
import json,sys,os,re,glob
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from pack import Pack
from PIL import Image
import gen
VS='/home/claude/WandEnhancer/PZVoxelStudioViewpoint/common/media/voxel-studio'
OUT='generated';CHUNK=700
p2=Pack('/mnt/user-data/uploads/ProjectZomboid/media/texturepacks/Tiles2x.pack')
p1=Pack('/mnt/user-data/uploads/ProjectZomboid/media/texturepacks/Tiles1x.pack')
g=json.load(open('geom.json'));t=json.load(open('tiles.json'));dep=json.load(open('dep.json'))

# what is bound already, and in which manifest
binds={};where={}
for f in sorted(glob.glob(os.path.join(VS,'package*.properties'))):
    if os.path.basename(f).startswith('package-generated'): continue
    for l in open(f):
        if l.startswith('bind.'):
            k,v=l.strip()[5:].split('=',1);binds[k]=v;where[k]=f

# Natively drawn by Viewpoint / ViewpointSurface / ViewpointDoor / ViewpointFences, or flat ground art.
SKIP=('walls_','roofs_','floors_','blends_','street_curbs','street_trafficlines','overlay_','fixtures_doors','fixtures_windows',
      'fencing','e_','d_streetcracks','d_floorleaves','d_plants','object_snow_overlay','invisible','underground','ceilings',
      'location_community_school_overlays','vegetation_groundcover','brokenglass','carpentry_01_')
STRUCT={'WallN','WallW','WallNW','WallNTrans','WallWTrans','WallNWTrans','doorN','doorW','DoorWallN','DoorWallW','windowN','windowW',
        'WindowN','WindowW','wall','floor','solidfloor','solidtrans','HoppableN','HoppableW','CantClimb','FloorOverlay','WallOverlay','attachedFloor'}
TILE=re.compile(r'.+_\d+$')
names=sorted(set(n for n in t)|set(n for n in p2.index if TILE.match(n)))
todo=[];stats={}
def note(k): stats[k]=stats.get(k,0)+1
for n in names:
    if n in binds: continue
    if n.startswith(SKIP) or '_depth' in n or 'test' in n.lower(): note('native/flat');continue
    if not re.fullmatch(r'[A-Za-z0-9_&+-]+',n) or n.lower().startswith(('fire','alokin','d_wallcracks','d_generic')): note('editor/effect art');continue
    p=t.get(n,{})
    if set(p)&STRUCT: note('structural');continue
    todo.append(n)

def sprite(n):
    im=p2.sprite(n)
    if im is None and n in p1.index:
        im=p1.sprite(n).resize((128,256),Image.NEAREST)
    return im

made={};mirrors={}
for n in todo:
    m=re.match(r'(.*)_on_(\d+)$',n)
    if m and '%s_%s'%m.groups() in binds:      # lit sprite: share the unlit model
        off='%s_%s'%m.groups();mirrors.setdefault(where[off],[]).append((n,binds[off]));note('lit->unlit');continue
    img=sprite(n)
    if img is None: note('no art');continue
    p=t.get(n,{});uv=None
    walls=[s for s in 'NWSE' if 'attached'+s in p]
    if g.get(n): tris=gen.shapes_mesh(g[n]);kind='geometry';msg='generated from the game tile geometry'
    elif walls:
        tris=gen.wall_mesh(img,walls[0]);kind='wall';msg='a plate on its %s wall'%walls[0]
    elif g.get(dep.get(n,'')):
        tris=gen.shapes_mesh(g[dep[n]]);kind='geometry-of-'+re.sub(r'_\d+$','',dep[n]);msg='generated from the tile geometry of %s, whose depth art it shares'%dep[n]
    else:
        tris,uv=gen.cross_mesh(img);kind='cross';msg='two crossed upright planes'
    if not tris: note('empty art');continue
    tris=tris+[(a,c,b) for a,b,c in tris]
    if gen.write_model(n,tris,img,os.path.join(VS,OUT,n),uv,msg): made[n]=kind;note(kind.split('-of-')[0] if kind.startswith('geometry') else kind)
    else: note('empty art')

# lit sprites whose unlit sprite got a model just now
for n in todo:
    m=re.match(r'(.*)_on_(\d+)$',n)
    if m and n not in made and '%s_%s'%m.groups() in made and n not in sum(([x for x,_ in v] for v in mirrors.values()),[]):
        made_off='%s_%s'%m.groups();made[n]=('alias',made_off);note('lit->unlit')

for f,items in mirrors.items():
    with open(f,'a') as fh:
        if not open(f).read().endswith('\n'): fh.write('\n')
        fh.write('# Lit (_on) sprites share the model of their unlit sprite.\n')
        for n,v in items: fh.write('bind.%s=%s\n'%(n,v))

def key(n):
    m=re.match(r'(.*)_(\d+)$',n);return (m.group(1),int(m.group(2)))
real=sorted([n for n,k in made.items() if not isinstance(k,tuple)],key=key)
for f in glob.glob(os.path.join(VS,'package-generated-*.properties')): os.remove(f)
manifests=[]
for i in range(0,len(real),CHUNK):
    part=real[i:i+CHUNK];idx=i//CHUNK+1
    fn='package-generated-%d.properties'%idx;manifests.append(fn)
    with open(os.path.join(VS,fn),'w') as f:
        f.write('id=pz-voxel-studio-generated-%d\nname=PZ Voxel Studio models: generated %d\nversion=1\n'%(idx,idx))
        f.write('# Sprites that had no model, generated from the game tile geometry and sprites (tools/house-models).\n')
        for n in part: f.write('model.%s=%s/%s/model.obj\n'%(n,OUT,n))
        for n in part: f.write('bind.%s=%s,0,0,0,0,1\n'%(n,n))
        partset=set(part)
        for n,k in sorted(made.items()):
            if isinstance(k,tuple) and k[1] in partset: f.write('bind.%s=%s,0,0,0,0,1\n'%(n,k[1]))
json.dump({'stats':stats,'manifests':manifests,'made':made},open('build_all_result.json','w'))
print(stats);print(manifests)
