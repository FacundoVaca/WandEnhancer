import re,json,sys
T='/mnt/user-data/uploads/ProjectZomboid/media/newtiledefinitions.tiles.txt'
tiles={};cur=None;fileName=None;props=None
for line in open(T,encoding='utf-8',errors='replace'):
    s=line.strip()
    if s.startswith('file ='): fileName=s.split('=',1)[1].strip()
    elif s.startswith('// '): cur=s[3:].strip(); props={}
    elif s.startswith('xy =') and cur: props['_xy']=s.split('=',1)[1].strip()
    elif s=='}' and cur is not None and props is not None:
        tiles[cur]=props; cur=None; props=None
    elif props is not None and '=' in s:
        k,v=s.split('=',1); props[k.strip()]=v.strip()
json.dump(tiles,open(sys.argv[1],'w'))
print(len(tiles))
