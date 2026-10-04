import json
from pathlib import Path
from PIL import Image,ImageDraw
D=Path(__file__).parent/'audit/planes';out=D/'candidates';out.mkdir(exist_ok=True)
rs=json.loads((D/'ocr.json').read_text(encoding='utf-8-sig'))
for p in range((len(rs)+79)//80):
 im=Image.new('RGB',(1600,1600),(55,55,55));draw=ImageDraw.Draw(im)
 for j,r in enumerate(rs[p*80:p*80+80]):
  a=Image.open(D/r['file']).convert('RGBA');a.thumbnail((158,178));x=j%10*160;y=j//10*200
  im.paste(a,(x,y+20),a);draw.text((x+2,y+2),r['file'],fill='white')
 im.save(out/f'page_{p:02}.jpg')
print(len(rs))
