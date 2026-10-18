import struct,io,json,sys
from PIL import Image
class Pack:
    def __init__(s,path):
        s.f=open(path,'rb');f=s.f
        assert f.read(4)==b'PZPK';ver,=struct.unpack('<i',f.read(4));assert ver==1
        n,=struct.unpack('<i',f.read(4))
        s.pages=[];s.index={}
        for p in range(n):
            name=s._str();cnt,mask=struct.unpack('<ii',f.read(8))
            for _ in range(cnt):
                en=s._str();vals=struct.unpack('<8i',f.read(32))
                s.index[en]=(p,vals)
            ln,=struct.unpack('<i',f.read(4));off=f.tell();f.seek(ln,1)
            s.pages.append((name,off,ln))
        s.cache={}
    def _str(s):
        l,=struct.unpack('<i',s.f.read(4));return s.f.read(l).decode('utf-8','replace')
    def page(s,p):
        if p not in s.cache:
            if len(s.cache)>6: s.cache.clear()
            name,off,ln=s.pages[p];s.f.seek(off)
            s.cache[p]=Image.open(io.BytesIO(s.f.read(ln))).convert('RGBA')
        return s.cache[p]
    def sprite(s,name):
        """Full-frame RGBA image of the sprite (fw x fh), or None."""
        if name not in s.index: return None
        p,(x,y,w,h,ox,oy,fw,fh)=s.index[name]
        img=Image.new('RGBA',(fw,fh),(0,0,0,0))
        img.paste(s.page(p).crop((x,y,x+w,y+h)),(ox,oy))
        return img
if __name__=='__main__':
    pk=Pack(sys.argv[1]);print(len(pk.pages),len(pk.index))
    for n in sys.argv[2:]:
        print(n,pk.index.get(n))
