"""원본 위치를 유지하는 모두의 골프 4 한국어 시험판 빌드."""
from pathlib import Path
import json,struct,re,hashlib,shutil,sys
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import xb,translations as tr,iso_layout
W=Path(__file__).parent;ROOT=W.parent
SOURCE=ROOT/'Minna no Golf 4 (Japan) (v2.00).iso'
TARGET=ROOT/'Minna no Golf 4 (Japan) (v2.00) (Korean).iso'
FINAL_TARGET=TARGET
TARGET=ROOT/'Minna no Golf 4 (Japan) (v2.00) (Korean).building.iso'

def glyph_unpack(b):
    out=bytearray();p=0
    while p<len(b):
        n=b[p];p+=1
        if n&128:n&=127;out.extend(b[p:p+n]);p+=n
        else:out.extend(bytes(n))
    assert len(out)==132
    return bytes(out)
def glyph_pack(b):
    out=bytearray();p=0
    while p<len(b):
        zero=b[p]==0;q=p+1
        while q<len(b) and (b[q]==0)==zero and q-p<127:q+=1
        out.append((q-p)|(0 if zero else 128))
        if not zero:out.extend(b[p:q])
        p=q
    assert glyph_unpack(out)==b
    return bytes(out)
def glyph_render(c,font):
    """원본 글꼴처럼 2픽셀 외곽선(값 1)과 굵은 획(값 2·3)으로 그린다."""
    im=Image.new('L',(24,22));d=ImageDraw.Draw(im)
    box=d.textbbox((0,0),c,font=font)
    x=(24-(box[2]-box[0]))//2-box[0];y=(22-(box[3]-box[1]))//2-box[1]
    d.text((x,y),c,font=font,fill=255)
    edge=im.point(lambda v:255 if v>=96 else 0).filter(ImageFilter.MaxFilter(5))
    vals=[3 if v>=170 else 2 if v>=96 else 1 if e or v>=40 else 0 for v,e in zip(im.tobytes(),edge.tobytes())]
    return bytes(sum(vals[i+j]<<(6-2*j) for j in range(4)) for i in range(0,len(vals),4))
def sjis(idx):
    row,col=divmod(idx,94);lead=row//2+0x81
    if lead>0x9f:lead+=0x40
    trail=col+0x40
    if row&1:trail+=0x5f
    elif trail>=0x7f:trail+=1
    return bytes((lead,trail))
def gather():
    rows,trans=tr.menu();changes=[]
    trans.update({1027:'(1급품)',1028:'(특급품)',1109:'(현재',1110:'장 보유)',1185:'VTR 증설'})
    for i,s in trans.items():changes.append(dict(file='MENU.BIN',offset=rows[i]['offset'],original=rows[i]['text'],korean=s,id=i))
    import game_ko
    gamerows=json.loads((W/'GAME.BIN.texts.json').read_text(encoding='utf8'))
    for i,s in game_ko.KO.items():changes.append(dict(file='GAME.BIN',offset=gamerows[i]['offset'],original=gamerows[i]['text'],korean=s,id=i))
    b=(W/'SYSTEM.BIN').read_bytes()
    for m in re.finditer(rb'[^\x00]+',b[0x125270:0x126430]):
        try:s=m[0].decode('cp932')
        except UnicodeError:continue
        ko=tr.glossary(s)
        if ko!=s and not re.search('[\u3040-\u30ff\u4e00-\u9fff]',ko):
            changes.append(dict(file='SYSTEM.BIN',offset=0x125270+m.start(),original=s,korean=ko))
    for r in changes:r['korean']=r['korean'].replace('·','・')
    return changes
def main():
    changes=gather();hangul=sorted(set(c for r in changes for c in r['korean'] if '가'<=c<='힣'))
    fontsrc=(W/'GFFONT.0.raw').read_bytes();n=struct.unpack_from('<I',fontsrc)[0];offsets=struct.unpack_from('<'+str(n+1)+'I',fontsrc,4);base=4+4*(n+1)
    glyphs=[fontsrc[base+offsets[i]:base+offsets[i+1]] for i in range(n)]
    reference_bytes=b'\0'.join(r['text'].encode('cp932') for name in ['SYSTEM.BIN','MENU.BIN','GAME.BIN'] for r in json.loads((W/(name+'.texts.json')).read_text(encoding='utf8')) if len(r['text'])>3 and r['offset']>dict(zip(['SYSTEM.BIN','MENU.BIN','GAME.BIN'],[0x125270,516992,0x16c6b8]))[name])
    available=[i for i in range(8*94,n) if not any(glyph_unpack(glyphs[i])) and sjis(i) not in reference_bytes]
    assert len(hangul)<=len(available),(len(hangul),len(available))
    cmap={c:sjis(i) for c,i in zip(hangul,available)}
    def encode(s):return b''.join(cmap[c] if c in cmap else c.encode('cp932') for c in s)
    reverse={v:k for k,v in cmap.items()}
    def decode(b):
        out='';p=0
        while p<len(b):
            if b[p:p+2] in reverse:out+=reverse[b[p:p+2]];p+=2
            elif 0x81<=b[p]<=0x9f or 0xe0<=b[p]<=0xef:out+=b[p:p+2].decode('cp932');p+=2
            else:out+=b[p:p+1].decode('cp932');p+=1
        return out
    binaries={name:bytearray((W/name).read_bytes()) for name in ['MENU.BIN','SYSTEM.BIN','GAME.BIN']}
    ranges=[];errors=[]
    for r in changes:
        b=binaries[r['file']];p=r['offset'];old=r['original'].encode('cp932');new=encode(r['korean']);z=p+len(old)
        assert b[p:z]==old
        while z<len(b) and b[z]==0:z+=1
        capacity=z-p-1
        if len(new)>capacity:errors.append((r.get('id'),r['original'],len(new),capacity,r['korean']));continue
        assert decode(new)==r['korean'],(r.get('id'),r['korean'],decode(new))
        assert re.findall(rb'[\x07\x0b].',old)==re.findall(rb'[\x07\x0b].',new)
        assert re.findall(rb'%[a-z]',old)==re.findall(rb'%[a-z]',new)
        b[p:p+max(len(old),len(new))+1]=new+bytes(max(len(old),len(new))+1-len(new))
        r['encoded_hex']=new.hex();r['capacity']=capacity
    if errors:print(json.dumps(errors,ensure_ascii=False,indent=2));raise RuntimeError('문자열 공간 초과')
    import compact_ko
    compact_records=compact_ko.patch(binaries)
    print('경기용 고정 글자판 번역',len(compact_records),flush=True)
    font=ImageFont.truetype(str(ROOT/'NanumSquareNeo-cBd.ttf'),18)
    for c,i in zip(hangul,available):glyphs[i]=glyph_pack(glyph_render(c,font))
    newoffs=[0]
    for g in glyphs:newoffs.append(newoffs[-1]+len(g))
    fontraw=struct.pack('<I',n)+struct.pack('<'+str(n+1)+'I',*newoffs)+b''.join(glyphs)
    print('문자열',len(changes),'한글',len(hangul),'폰트원시',len(fontraw),flush=True)
    packed=xb.repack_one((W/'GFFONT.XB').read_bytes(),fontraw)
    print('폰트압축',len(packed),'기존',len((W/'GFFONT.XB').read_bytes()),flush=True)
    inventory=json.loads((W/'iso_inventory.json').read_text(encoding='utf8'))
    files={r['path']:r for r in inventory if not r['directory']}
    outputs={'/ZZBIN/MENU.BIN;1':bytes(binaries['MENU.BIN']),'/ZZBIN/SYSTEM.BIN;1':bytes(binaries['SYSTEM.BIN']),'/ZZBIN/GAME.BIN;1':bytes(binaries['GAME.BIN']),'/CMN/GFFONT.XB;1':packed}
    if (W/'texture_manifest.json').exists():
        for r in json.loads((W/'texture_manifest.json').read_text(encoding='utf8')):outputs[r['path']]=(W/'packed'/r['file']).read_bytes()
    relocations={};next_lba=SOURCE.stat().st_size//2048
    for path,b in outputs.items():
        r=files[path]
        if len(b)>r['size']:
            sectors=(len(b)+2047)//2048;oldsectors=(r['size']+2047)//2048
            pattern=struct.pack('<QQQ',r['lba'],r['lba']+oldsectors-1,oldsectors)
            system=bytearray(outputs['/ZZBIN/SYSTEM.BIN;1']);assert system.count(pattern)==1
            at=system.index(pattern);system[at:at+24]=struct.pack('<QQQ',next_lba,next_lba+sectors-1,sectors)
            outputs['/ZZBIN/SYSTEM.BIN;1']=bytes(system)
            relocations[path]=dict(lba=next_lba,size=len(b));next_lba+=sectors
    (W/'hangul_map.json').write_text(json.dumps({c:dict(code=cmap[c].hex(),index=i) for c,i in zip(hangul,available)},ensure_ascii=False,indent=2),encoding='utf8')
    (W/'translations_applied.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf8')
    if '--no-iso' in sys.argv:return
    shutil.copyfile(SOURCE,TARGET)
    with TARGET.open('r+b') as f:
        if relocations:f.truncate((next_lba+1)*2048)
        for path,b in outputs.items():
            r=relocations.get(path,files[path]);f.seek(r['lba']*2048);f.write(b);f.write(bytes(r['size']-len(b)))
        for path,r in relocations.items():iso_layout.relocate(f,files[path],r['lba'],r['size'],inventory)
        if relocations:iso_layout.resize(f,SOURCE.stat().st_size//2048,next_lba+1)
    allowed=sorted((files[p]['lba']*2048,files[p]['lba']*2048+files[p]['size']) for p in outputs)
    if relocations:allowed.append((0,7321*2048))
    hs=hashlib.sha256();ht=hashlib.sha256();pos=0;changed_blocks=0
    with SOURCE.open('rb') as a,TARGET.open('rb') as b:
        while x:=a.read(1<<20):
            y=b.read(len(x));hs.update(x);ht.update(y)
            if x!=y:
                changed_blocks+=1
                checkx=bytearray(x);checky=bytearray(y)
                for lo,hi in allowed:
                    a0=max(pos,lo)-pos;a1=min(pos+len(x),hi)-pos
                    if a0<a1:checkx[a0:a1]=bytes(a1-a0);checky[a0:a1]=bytes(a1-a0)
                assert checkx==checky,('허용 범위 외 변경',pos)
            pos+=len(x)
        tail=b.read();ht.update(tail);pos+=len(tail)
    with TARGET.open('rb') as f:
        for path,data in outputs.items():
            r=relocations.get(path,files[path]);f.seek(r['lba']*2048);assert f.read(len(data))==data,path
    textures=json.loads((W/'texture_changes.json').read_text(encoding='utf8'))
    report=dict(status='정적 검증 통과, 실행 검증 전',source_sha256=hs.hexdigest(),target_sha256=ht.hexdigest(),translated_strings=len(changes),compact_strings=len(compact_records),hangul_glyphs=len(hangul),compact_glyphs=len(compact_ko.mapping()),translated_textures=len(textures),translated_regions=sum(len(t['regions']) for t in textures),font='NanumSquareNeo-cBd.ttf / NanumSquareNeo-eHv.ttf',changed_files=list(outputs),relocations=relocations,changed_megabyte_blocks=changed_blocks,iso_bytes=pos,limitations=['실행 화면 검증 및 전체 플레이 검증 필요','동영상 자막과 모든 3D 배경 장식의 번역 여부는 별도 검증 필요'])
    TARGET.replace(FINAL_TARGET)
    (W/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
