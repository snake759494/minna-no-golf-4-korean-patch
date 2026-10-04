"""검증한 이미지와 완전히 같은 원본만 모든 XB 사본에서 교체한다."""
import json,hashlib,struct
from pathlib import Path
import catalog,xb
W=Path(__file__).parent
def norm(s):return s.replace('\\','/').lower().removeprefix('./')
def main():
 changes=json.loads((W/'texture_changes.json').read_text(encoding='utf8'))
 rows=json.loads((W/'texture_index.json').read_text(encoding='utf8'))
 byname={}
 for c in changes:byname.setdefault(norm(rows[c['id']]['name']),[]).append(c)
 records=json.loads((W/'resource_catalog.json').read_text(encoding='utf8'))
 outdir=W/'packed';outdir.mkdir(exist_ok=True)
 manifest=[];variants=[];count=0;seen={};rawcache={}
 with catalog.ISO.open('rb') as f:
  for r in records:
   candidates=[e for e in r['entries'] if norm(e['name']) in byname]
   if not candidates:continue
   f.seek(r['lba']*2048);src=f.read(r['size']);replacements={};ids=[]
   offsets=sorted((e['tag']&0xfffffff)*4 for e in r['entries']);ends=dict(zip(offsets,offsets[1:]+[len(src)]))
   for e in candidates:
    choices=byname[norm(e['name'])];i=e['index'];size,tag=struct.unpack_from('<II',src,8+i*8);off=(tag&0xfffffff)*4
    # 원본 압축 블록이 같으면 이전에 검증한 해제 결과를 재사용.
    key=(size,tag>>28,hashlib.sha256(src[off:ends[off]]).digest())
    if key not in rawcache:rawcache[key]=catalog.entry(src,i)
    raw=rawcache[key]
    rawhash=hashlib.sha256(raw).hexdigest();c=next((c for c in choices if rawhash==c['source_hash']),None)
    if c is None:
     variants.append(dict(path=r['path'],name=e['name'],id=choices[0]['id'],hash=rawhash));continue
    replacements[i]=(W/'textures_ko'/f"{c['id']:04}.bin").read_bytes();ids.append(c['id'])
   if not replacements:continue
   key=hashlib.sha256(src+b''.join(struct.pack('<I',i)+hashlib.sha256(v).digest() for i,v in replacements.items())).hexdigest()
   target=outdir/(key+'.xb')
   if not target.exists():
    packed=xb.repack(src,replacements)
    assert catalog.names(packed)==catalog.names(src)
    for i,raw in replacements.items():assert catalog.entry(packed,i)==raw
    target.write_bytes(packed)
   manifest.append(dict(path=r['path'],file=target.name,ids=ids,size=target.stat().st_size));count+=len(ids)
   if len(manifest)%20==0:print('압축 묶음',len(manifest),'이미지 사본',count,flush=True)
 (W/'texture_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
 (W/'texture_variants.json').write_text(json.dumps(variants,ensure_ascii=False,indent=2),encoding='utf8')
 print('완료',len(manifest),'묶음',count,'사본','별도 확인',len(variants),flush=True)
if __name__=='__main__':main()
