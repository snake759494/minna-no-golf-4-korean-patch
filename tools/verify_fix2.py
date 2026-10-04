"""추가 수정의 잘림, 글자 여백, 애니메이션 CLUT/밉맵 경계 회귀 검사."""
from pathlib import Path
import json,io,numpy as np
from PIL import Image
import tim2,compact_ko
from texture_patch import Texture
W=Path(__file__).parent
def indices(i):
 t=Texture(i);b=(W/'textures_ko'/f'{i:04}.bin').read_bytes()
 return t,np.array(Image.open(io.BytesIO(b))) if t.g is None else np.frombuffer(tim2.to_image(b,t.g)[1],dtype='uint8').reshape(t.idx.shape)
t,idx=indices(538);allowed=np.zeros(idx.shape,bool);allowed[30:66,105:426]=True;allowed[96:128,0:224]=True
assert not np.any((idx!=t.orig)&~allowed),'종료 그림 UV 밖 변경'
for i in [55,336,337,450,540]:
 t,idx=indices(i);cell=t.im.width//16
 for slot in compact_ko.mapping():
  x=slot%16*cell;y=slot//16*cell
  if t.g is None:
   rgb=t.pal[idx[y:y+cell,x:x+cell],:3];a=rgb.max(2)>80
  else:a=t.pal[idx[y:y+cell,x:x+cell],3]>80
  ys,xs=np.where(a)
  assert len(xs)>0 and xs.min()>=1 and xs.max()<cell-1 and ys.min()>=1 and ys.max()<cell-1,(i,slot,'글자 칸 경계')
rows=json.loads((W/'texture_index.json').read_text(encoding='utf8'))
layouts=json.loads((W/'audit/mti_layout_fixed.json').read_text(encoding='utf8'))
for row in rows:
 aid=str(row.get('mti_audit'))
 if aid not in layouts:continue
 src=(W/'textures'/f"{row['id']:04}.bin").read_bytes();out=(W/'textures_ko'/f"{row['id']:04}.bin")
 if not out.exists():continue
 dst=out.read_bytes();assert len(src)==len(dst)
 for p in layouts[aid]:
  off=p['palette_offset'];n=1024 if p['psm']==19 else 64
  assert src[off:off+n]==dst[off:off+n],(aid,p['plane'],'색상표 변경')
for frame in range(7):
 row=next(x for x in rows if x['name'].endswith('pl_sel.TAI'))
 src=(W/'textures'/f"{row['id']:04}.bin").read_bytes();dst=(W/'textures_ko'/f"{row['id']:04}.bin").read_bytes();off=frame*11264
 assert src[off+10240:off+11264]==dst[off+10240:off+11264],('TAI 팔레트',frame)
 assert src[off:off+10240]!=dst[off:off+10240],('TAI 미처리 프레임',frame)
print('종료 UV·한글 칸 여백·MTI 색상표·TAI 7프레임 검사 통과')
