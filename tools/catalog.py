"""ISO 내 XB 파일 이름과 번역 대상 리소스 조사."""
import json,struct
from pathlib import Path
import xb
W=Path(__file__).parent
ISO=W.parent/'Minna no Golf 4 (Japan) (v2.00).iso'
def names(b):
    n=struct.unpack_from('<I',b,4)[0];raw=xb.block(b[8+n*8:],xb.lz);out=[];p=0
    for _ in range(n):
        end=raw.index(0,p+2);out.append(raw[p+2:end].decode('cp932'));p=end+1
    assert p==len(raw),(p,len(raw))
    return out
def entry(b,i):
    size,tag=struct.unpack_from('<II',b,8+i*8);off=(tag&0xfffffff)*4;mode=tag>>28;body=b[off:]
    if mode==0:raw=xb.block(xb.block(body,xb.huffman),xb.lz)
    elif mode==1:raw=xb.block(body,xb.huffman)
    elif mode==2:raw=xb.block(body,xb.lz)
    elif mode==3:raw=body[:size]
    else:raise ValueError(mode)
    assert len(raw)==size
    return raw
if __name__=='__main__':
    rows=json.loads((W/'iso_inventory.json').read_text());out=[];errors=[]
    with ISO.open('rb') as f:
        for r in rows:
            if r['directory'] or not r['path'].endswith('.XB;1'):continue
            f.seek(r['lba']*2048);head=f.read(8)
            if head[:4]!=b'xe\x00\x01':continue
            n=struct.unpack_from('<I',head,4)[0];table=f.read(n*8);sizes=f.read(8)
            rawsz,packsz=struct.unpack('<II',sizes);body=f.read(packsz or rawsz)
            try:
                ns=names(head+table+sizes+body)
                entries=[dict(index=i,name=name,size=struct.unpack_from('<I',table,i*8)[0],tag=struct.unpack_from('<I',table,i*8+4)[0]) for i,name in enumerate(ns)]
                out.append(dict(**r,entries=entries))
            except Exception as ex:errors.append((r['path'],str(ex)))
    (W/'resource_catalog.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
    print('묶음',len(out),'리소스',sum(len(r['entries']) for r in out),'오류',errors[:15])
    from collections import Counter
    print(Counter(Path(e['name']).suffix.lower() for r in out for e in r['entries']))
