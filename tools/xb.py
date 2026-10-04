"""모두의 골프 4 XB 해제. SYSTEM.BIN 0x193800/0x193900/0x193a00 분석."""
import struct
from pathlib import Path
from functools import lru_cache

@lru_cache(maxsize=1024)
def compress_lz(src):
    from collections import defaultdict,deque
    chains=defaultdict(deque);out=bytearray();literal=bytearray();p=0
    def flush():
        if literal:out.append((len(literal)-1)<<2);out.extend(literal);literal.clear()
    def add(i):
        k=src[i:i+3];q=chains[k];q.append(i)
        while q and (len(q)>64 or i-q[0]>4095):q.popleft()
    while p<len(src):
        best=0;dist=0
        for q in reversed(chains.get(src[p:p+3],())):
            if p-q>4095:break
            n=3;maximum=min(1026,len(src)-p)
            while n<maximum and src[q+n]==src[p+n]:n+=1
            if n>best:best=n;dist=p-q
            if best==maximum:break
        if best>=3:
            flush()
            if best<=10:out.extend(((dist<<4)|((best-3)<<1)|1).to_bytes(2,'little'))
            else:out.extend(((dist<<12)|((best-3)<<2)|2).to_bytes(3,'little'))
            for i in range(p,p+best):add(i)
            p+=best
        else:
            literal.append(src[p]);add(p);p+=1
            if len(literal)==64:flush()
    flush();return bytes(out)

def compress_huffman(src,template):
    p=1;code=0;codes={};escape=None
    for bits in range(1,template[0]+1):
        n=template[p];p+=1
        for _ in range(n):
            sym=template[p];p+=1;rev=int(f'{code:0{bits}b}'[::-1],2)
            if bits<11:codes[sym]=(rev,bits);code+=1
            else:escape=rev&1023
        code<<=1
    header=template[:(p+1)&~1];out=bytearray(header);buf=0;n=0
    for sym in src:
        if sym in codes:v,bits=codes[sym]
        else:
            assert escape is not None
            v=escape|(sym<<10);bits=18
        buf|=v<<n;n+=bits
        while n>=8:out.append(buf&255);buf>>=8;n-=8
    if n:out.append(buf&255)
    if len(out)&1:out.append(0)
    return bytes(out)

def repack_one(src,raw):
    assert struct.unpack_from('<I',src,4)[0]==1
    off=(struct.unpack_from('<I',src,12)[0]&0xfffffff)*4
    compressed=compress_lz(raw)
    mid=struct.pack('<II',len(raw),len(compressed))+compressed
    if len(mid)&1:mid+=b'\0'
    packed=compress_huffman(mid,src[off+8:])
    result=bytearray(src[:off]);struct.pack_into('<II',result,8,len(raw),off//4)
    result.extend(struct.pack('<II',len(mid),len(packed))+packed)
    assert unpack(result)==[raw]
    return bytes(result)

def repack(src,replacements):
    """지정한 항목만 재압축하고 나머지 압축 블록은 원본 그대로 보존한다."""
    n=struct.unpack_from('<I',src,4)[0]
    records=[struct.unpack_from('<II',src,8+i*8) for i in range(n)]
    offsets=[(tag&0xfffffff)*4 for size,tag in records]
    assert len(set(offsets))==n
    ends={a:b for a,b in zip(sorted(offsets),sorted(offsets)[1:]+[len(src)])}
    out=bytearray(src[:min(offsets)])
    for i,(size,tag) in enumerate(records):
        while len(out)%4:out.append(0)
        off=len(out);oldoff=offsets[i]
        if i in replacements:
            raw=replacements[i];compressed=compress_lz(raw)
            blockdata=struct.pack('<II',len(raw),len(compressed))+compressed;mode=2
            # 기존 허프먼 테이블을 활용할 수 있으면 두 압축 방식 중 작은 것을 선택한다.
            if tag>>28==0 and struct.unpack_from('<I',src,oldoff+4)[0]>0:
                mid=blockdata
                if len(mid)&1:mid+=b'\0'
                try:hc=compress_huffman(mid,src[oldoff+8:])
                except AssertionError:hc=None
                if hc is not None:
                    candidate=struct.pack('<II',len(mid),len(hc))+hc
                    if len(candidate)<len(blockdata):blockdata=candidate;mode=0
            size=len(raw)
        else:mode=tag>>28;blockdata=src[oldoff:ends[oldoff]]
        struct.pack_into('<II',out,8+i*8,size,(mode<<28)|(off//4));out.extend(blockdata)
    return bytes(out)

def huffman(src, size):
    p=1; code=0; table=[None]*1024
    for bits in range(1,src[0]+1):
        count=src[p];p+=1
        for _ in range(count):
            sym=src[p];p+=1
            rev=int(f'{code:0{bits}b}'[::-1],2)
            for j in range(rev,1024,1<<bits):table[j]=(bits,sym)
            if bits<11:code+=1
        code<<=1
    p=(p+1)&~1;buf=0;n=0;out=bytearray()
    while len(out)<size:
        while n<18:
            buf|=(src[p] if p<len(src) else 0)<<n;p+=1;n+=8
        entry=table[buf&1023]
        if entry is None:raise ValueError('허프먼 테이블 누락')
        bits,sym=entry
        if bits>=11:sym=(buf>>10)&255;bits=18
        out.append(sym);buf>>=bits;n-=bits
    return bytes(out)

def lz(src,size):
    out=bytearray();p=0
    while len(out)<size:
        tag=src[p];p+=1
        if tag&3==0:
            n=(tag>>2)+1;out.extend(src[p:p+n]);p+=n
        else:
            if tag&1:
                v=tag|(src[p]<<8);p+=1;distance=v>>4;n=((v>>1)&7)+3
            else:
                v=tag|(src[p]<<8)|(src[p+1]<<16);p+=2;distance=v>>12;n=((v>>2)&1023)+3
            assert 0<distance<=len(out),(p,distance,len(out))
            for _ in range(n):out.append(out[-distance])
        assert len(out)<=size
    return bytes(out)

def block(src,decoder):
    size,packed=struct.unpack_from('<II',src)
    return decoder(src[8:],size) if packed else src[8:8+size]

def unpack(src):
    assert src[:4]==b'xe\x00\x01'
    count=struct.unpack_from('<I',src,4)[0];out=[]
    for i in range(count):
        size,tag=struct.unpack_from('<II',src,8+i*8)
        off=(tag&0xfffffff)*4;mode=tag>>28;body=src[off:]
        if mode==0:raw=block(block(body,huffman),lz)
        elif mode==1:raw=block(body,huffman)
        elif mode==2:raw=block(body,lz)
        elif mode==3:raw=body[:size]
        else:raise ValueError(mode)
        assert len(raw)==size,(len(raw),size)
        out.append(raw)
    return out

if __name__=='__main__':
    import sys
    p=Path(sys.argv[1])
    for i,b in enumerate(unpack(p.read_bytes())):
        q=p.with_suffix(f'.{i}.raw');q.write_bytes(b);print(q,len(b),b[:48].hex())
