import json,sys,os,re,glob
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from pack import Pack
import gen
VS='/home/claude/WandEnhancer/PZVoxelStudioViewpoint/common/media/voxel-studio'
pk=Pack('/mnt/user-data/uploads/ProjectZomboid/media/texturepacks/Tiles2x.pack')
g=json.load(open('geom.json'));t=json.load(open('tiles.json'));res=json.load(open('candidates.json'))
HOUSE=('walls_decoration_','walls_detailing_02','appliances_com_01','fixtures_bathroom_','fixtures_fireplaces_01','lighting_indoor_','desks_01','trash_walls_01','location_trailer_01')
made=[];skipped=[]
for n,k in res:
    if not n.startswith(HOUSE) or k=='other': continue
    img=pk.sprite(n)
    tris=gen.shapes_mesh(g[n]) if k=='geom' else gen.wall_mesh(img,'N' if 'attachedN' in t[n] else 'W')
    tris=tris+[(a,c,b) for a,b,c in tris]          # double-sided
    if gen.write_model(n,tris,img,os.path.join(VS,'houses',n)): made.append(n)
    else: skipped.append(n)
def key(n):
    m=re.match(r'(.*)_(\d+)$',n);return (m.group(1),int(m.group(2)))
with open(os.path.join(VS,'package-houses.properties'),'w') as f:
    f.write('id=pz-voxel-studio-houses\nname=PZ Voxel Studio models: houses\nversion=1\n')
    f.write('# Generated from the game tileGeometry and sprites: wall art (posters, paintings) and house fixtures that had no model.\n')
    for n in sorted(made,key=key): f.write('model.%s=houses/%s/model.obj\n'%(n,n))
    for n in sorted(made,key=key): f.write('bind.%s=%s,0,0,0,0,1\n'%(n,n))
print('made',len(made),'skipped',len(skipped),skipped[:10])
