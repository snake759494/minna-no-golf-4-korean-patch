"""MTL의 밉 레벨 기술자를 반영하여 기존 조사 메타데이터를 교정한다."""
import json,struct,sys
from pathlib import Path
import catalog
W=Path(__file__).parent
rows=json.loads((W/'texture_index.json').read_text(encoding='utf8'))
audit=json.loads((W/'audit/mti/index.json').read_text(encoding='utf8'))
planes=json.loads((W/'audit/planes/index.json').read_text(encoding='utf8'))
records={r['path']:r for r in json.loads((W/'resource_catalog.json').read_text(encoding='utf8'))}
ids=sorted({r['mti_audit'] for r in rows if 'mti_audit' in r}|{1147,1148})
cache={};result={}
with catalog.ISO.open('rb') as f:
 for aid in ids:
  a=audit[aid];r=records[a['archive']]
  if r['path'] not in cache:f.seek(r['lba']*2048);cache[r['path']]=f.read(r['size'])
  e=next(e for e in r['entries'] if e['name'].lower()==a['name'][:-4].lower()+'.mtl')
  m=catalog.entry(cache[r['path']],e['index']);count=struct.unpack_from('<I',m,16)[0];off=0;out=[]
  for p in range(count):
   d=m[32+80*p:112+80*p];psm=struct.unpack_from('<H',d,12)[0];levels=d[15]+1
   if psm not in [19,20]:raise ValueError((aid,p,psm))
   mip=[];start=off
   for lev in range(levels):
    size,w,h=struct.unpack_from('<IHH',d,16+lev*8)
    assert size==w*h//(2 if psm==20 else 1),(aid,p,lev,size,w,h)
    mip.append(dict(offset=off,width=w,height=h,size=size));off+=size
   po=off;off+=1024 if psm==19 else 64
   meta=dict(source=aid,name=a['name'],plane=p,offset=start,palette_offset=po,width=mip[0]['width'],height=mip[0]['height'],psm=psm,mips=mip)
   out.append(meta)
   old=next((x for x in planes if x['source']==aid and x['plane']==p),None)
   if old is not None:old.update(meta)
  raw=(W/'audit/mti'/f'{aid:04}.bin').read_bytes()
  assert off==len(raw),(aid,off,len(raw))
  result[str(aid)]=out
  row=next((x for x in rows if x.get('mti_audit')==aid),None)
  if row is not None:row.update(palette_offset=out[0]['palette_offset'],mips=out[0]['mips'])
(W/'texture_index.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
(W/'audit/planes/index.json').write_text(json.dumps(planes,ensure_ascii=False,indent=2),encoding='utf8')
(W/'audit/mti_layout_fixed.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print('MTI 구조 교정',len(result),flush=True)
