import re
def parse(path):
    """tile name -> list of shapes (dict)"""
    out={};cur=None;shape=None;depth=0;stack=[]
    for line in open(path):
        s=line.strip()
        m=re.match(r'/\* (\S+) \*/',s)
        if m: cur=m.group(1); out[cur]=[]; continue
        if s in('box','cylinder','polygon','properties','tile','tileset','tileGeometry'):
            stack.append(s)
            if s in('box','cylinder','polygon'): shape={'type':s}
            continue
        if s=='{': continue
        if s=='}':
            t=stack.pop() if stack else None
            if t in('box','cylinder','polygon') and cur: out[cur].append(shape); shape=None
            continue
        if shape is not None and '=' in s:
            k,v=s.rstrip(',').split('=',1);k=k.strip();v=v.strip()
            if k=='points': shape[k]=[tuple(int(a) for a in p.split('x')) for p in v.split()]
            elif k=='plane': shape[k]=v
            elif 'x' in v: shape[k]=tuple(int(a) for a in v.split('x'))
            else: shape[k]=int(v)
    return out
