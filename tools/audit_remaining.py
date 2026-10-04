"""기존 UI 색인 밖의 BMP/TIM2를 원본 데이터 해시 기준으로 전수 추출한다."""
import json,hashlib,io,struct
from pathlib import Path
from PIL import Image,ImageDraw
import catalog,tim2
W=Path(__file__).parent;D=W/'audit'/'remaining';D.mkdir(exist_ok=True)
def norm(s):return s.replace('\\','/').lower().removeprefix('./')
rows=json.loads((W/'resource_catalog.json').read_text(encoding='utf8'))
known={norm(r['name']) for r in json.loads((W/'texture_index.json').read_text(encoding='utf8'))}
seen=set();hashes=set();out=[];errors=[]
with catalog.ISO.open('rb') as f:
 for r in rows:
  es=[e for e in r['entries'] if e['name'].lower().endswith(('.bmp','.tm2')) and norm(e['name']) not in known and norm(e['name']) not in seen]
  if not es:continue
  f.seek(r['lba']*2048);b=f.read(r['size'])
  for e in es:
   seen.add(norm(e['name']))
   raw=catalog.entry(b,e['index']);h=hashlib.sha256(raw).hexdigest()
   if h in hashes:continue
   hashes.add(h)
   try:
    im=tim2.to_image(raw,tim2.parse(raw)[0])[0] if raw[:4]==b'TIM2' else Image.open(io.BytesIO(raw)).convert('RGBA')
    i=len(out);(D/f'{i:04}.bin').write_bytes(raw);im.save(D/f'{i:04}.png')
    out.append(dict(id=i,name=e['name'],archive=r['path'],index=e['index'],width=im.width,height=im.height,hash=h))
   except Exception as ex:errors.append(dict(name=e['name'],error=str(ex)))
  if len(out)%100<5:print('추가 이미지',len(out),flush=True)
(D/'index.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
(D/'errors.json').write_text(json.dumps(errors,ensure_ascii=False,indent=2),encoding='utf8')
for p in range((len(out)+63)//64):
 im=Image.new('RGB',(1600,1440),(55,55,55));d=ImageDraw.Draw(im)
 for j,r in enumerate(out[p*64:p*64+64]):
  a=Image.open(D/f"{r['id']:04}.png").convert('RGBA');a.thumbnail((198,157));x=j%8*200;y=j//8*180;im.paste(a,(x,y+20),a);d.text((x+2,y+2),str(r['id']),fill='white')
 im.save(D/f'page_{p:02}.jpg')
print('완료',len(out),'종',len(errors),'오류',flush=True)
