"""MTL의 크기/픽셀 형식으로 3D MTI 텍스처를 조사한다."""
import json,hashlib,struct
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
import catalog,tim2
W=Path(__file__).parent;D=W/'audit'/'mti';D.mkdir(exist_ok=True)
out=json.loads((D/'index.json').read_text(encoding='utf8')) if (D/'index.json').exists() else []
rows=json.loads((W/'resource_catalog.json').read_text(encoding='utf8'));seen={r['name'].lower() for r in out};hashes={r['hash'] for r in out};errors=[]
with catalog.ISO.open('rb') as f:
 for r in rows:
  es=[e for e in r['entries'] if e['name'].lower().endswith('.mti') and e['name'].lower() not in seen]
  if not es:continue
  names={e['name'].lower():e for e in r['entries']};f.seek(r['lba']*2048);b=f.read(r['size'])
  for e in es:
   seen.add(e['name'].lower());raw=catalog.entry(b,e['index']);h=hashlib.sha256(raw).hexdigest()
   if h in hashes:continue
   hashes.add(h)
   try:
    me=names[e['name'][:-4].lower()+'.mtl'];m=catalog.entry(b,me['index'])
    width,height=struct.unpack_from('<HH',m,34);psm=struct.unpack_from('<H',m,44)[0]
    assert width>0 and height>0 and width<2048 and height<2048,(width,height)
    if psm==19:
     assert len(raw)>=width*height+1024,(width,height,psm,len(raw))
     pal=tim2.unswz32([tuple(raw[j:j+4]) for j in range(len(raw)-1024,len(raw),4)])
     idx=np.frombuffer(raw[:width*height],dtype='uint8').reshape(height,width)
    elif psm==20:
     assert len(raw)>=width*height//2+64,(width,height,psm,len(raw))
     pal=[tuple(raw[j:j+4]) for j in range(len(raw)-64,len(raw),4)]
     a=np.frombuffer(raw[:width*height//2],dtype='uint8');idx=np.stack([a&15,a>>4],axis=1).reshape(height,width)
    else:raise ValueError(('지원 외 픽셀 형식',psm,width,height,len(raw)))
    p=np.array([(a,b,c,min(255,d*2)) for a,b,c,d in pal],dtype='uint8');im=Image.fromarray(p[idx]);i=len(out)
    (D/f'{i:04}.bin').write_bytes(raw);im.save(D/f'{i:04}.png');out.append(dict(id=i,name=e['name'],archive=r['path'],index=e['index'],width=width,height=height,psm=psm,hash=h))
   except Exception as ex:errors.append(dict(name=e['name'],archive=r['path'],error=str(ex)))
(D/'index.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');(D/'errors.json').write_text(json.dumps(errors,ensure_ascii=False,indent=2),encoding='utf8')
for p in range((len(out)+47)//48):
 im=Image.new('RGB',(1600,1440),(55,55,55));d=ImageDraw.Draw(im)
 for j,r in enumerate(out[p*48:p*48+48]):
  a=Image.open(D/f"{r['id']:04}.png").convert('RGBA');a.thumbnail((198,216));x=j%8*200;y=j//8*240;im.paste(a,(x,y+20),a);d.text((x+2,y+2),str(r['id']),fill='white')
 im.save(D/f'page_{p:02}.jpg')
print('MTI',len(out),'종',len(errors),'미해석',flush=True)
