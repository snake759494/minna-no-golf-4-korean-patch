"""MTL의 80바이트 텍스처 기술자를 모두 순회해 MTI 내부 이미지 조사."""
import json,struct,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import catalog,tim2
W=Path(__file__).parent;D=W/'audit'/'planes';D.mkdir(exist_ok=True)
old=json.loads((W/'audit/mti/index.json').read_text(encoding='utf8'));byarchive={}
for r in old:byarchive.setdefault(r['archive'],[]).append(r)
rows=json.loads((W/'resource_catalog.json').read_text(encoding='utf8'));out=[];errors=[];seen=set()
with catalog.ISO.open('rb') as f:
 for row in rows:
  if row['path'] not in byarchive:continue
  f.seek(row['lba']*2048);b=f.read(row['size']);names={e['name'].lower():e for e in row['entries']}
  for r in byarchive[row['path']]:
   try:
    me=names[r['name'][:-4].lower()+'.mtl'];m=catalog.entry(b,me['index']);raw=(W/'audit/mti'/f"{r['id']:04}.bin").read_bytes()
    count=struct.unpack_from('<I',m,16)[0];assert 0<count<100
    off=0
    for plane in range(count):
     d=32+80*plane;colors,width,height=struct.unpack_from('<HHH',m,d);psm=struct.unpack_from('<H',m,d+12)[0];size=struct.unpack_from('<I',m,d+16)[0]
     assert width and height and off+size+colors*4<=len(raw),(plane,off,size,colors,len(raw))
     h=hashlib.sha256(raw[off:off+size+colors*4]).hexdigest()
     if h not in seen:
      if psm in (19,20):
       pal=[tuple(raw[j:j+4]) for j in range(off+size,off+size+colors*4,4)]
       if colors==256:pal=tim2.unswz32(pal)
       a=np.frombuffer(raw[off:off+size],dtype='uint8')
       idx=a[:width*height].reshape(height,width) if psm==19 else np.stack([a&15,a>>4],axis=1).ravel()[:width*height].reshape(height,width)
       p=np.array([(a,b,c,min(255,d*2)) for a,b,c,d in pal],dtype='uint8');im=Image.fromarray(p[idx])
      elif psm==0:
       p=np.frombuffer(raw[off:off+width*height*4],dtype='uint8').reshape(height,width,4).copy();p[:,:,3]=np.minimum(p[:,:,3].astype(int)*2,255);im=Image.fromarray(p)
      else:raise ValueError(('psm',psm))
      i=len(out);im.save(D/f'{i:04}.png');out.append(dict(id=i,source=r['id'],name=r['name'],plane=plane,offset=off,palette_offset=off+size,width=width,height=height,psm=psm));seen.add(h)
     off+=size+colors*4
    assert off==len(raw),(off,len(raw))
   except Exception as ex:errors.append(dict(name=r['name'],error=str(ex)))
(D/'index.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');(D/'errors.json').write_text(json.dumps(errors,ensure_ascii=False,indent=2),encoding='utf8')
for p in range((len(out)+79)//80):
 im=Image.new('RGB',(1600,1600),(55,55,55));dr=ImageDraw.Draw(im)
 for j,r in enumerate(out[p*80:p*80+80]):
  a=Image.open(D/f"{r['id']:04}.png").convert('RGBA');a.thumbnail((158,176));x=j%10*160;y=j//10*200;im.paste(a,(x,y+20),a);dr.text((x+2,y+2),str(r['id']),fill='white')
 im.save(D/f'page_{p:02}.jpg')
print('독립 이미지',len(out),'검토',len(errors),flush=True)
