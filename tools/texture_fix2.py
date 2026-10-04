"""2026-10-04 추가 스크린샷: UV 분할, 표 배경, 애니메이션 프레임 보정."""
from pathlib import Path
import json,copy
import numpy as np
from PIL import Image
from scipy.ndimage import binary_propagation
from texture_patch import Texture
import tim2,catalog
W=Path(__file__).parent

def animation(T):
 rows=json.loads((W/'texture_index.json').read_text(encoding='utf8'))
 name='.\\data\\menu\\smf\\playerselect\\pl_sel.TAI'
 row=next((r for r in rows if r['name']==name),None)
 if row is None:
  records=json.loads((W/'resource_catalog.json').read_text(encoding='utf8'))
  arc=next(r for r in records if r['path']=='/MENU/M_MENU1/MENU05.XB;1')
  with catalog.ISO.open('rb') as f:f.seek(arc['lba']*2048);raw=catalog.entry(f.read(arc['size']),32)
  row=dict(id=len(rows),name=name,archive=arc['path'],index=32,width=160,height=64,format='MTI8')
  rows.append(row);(W/'texture_index.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
  (W/'textures'/f"{row['id']:04}.bin").write_bytes(raw)
  Texture(row['id']).im.save(W/'textures'/f"{row['id']:04}.png")
 t=T(row['id']);assert len(t.raw)==7*11264
 colors=[(255,255,255),(248,78,10),(73,92,239),(90,224,0),(255,178,0),(255,255,255),(233,217,137)]
 for frame,s in enumerate(['참가 대기','플레이어 1','플레이어 2','플레이어 3','플레이어 4','컴퓨터','컴퓨터']):
  off=frame*11264;b=t.raw[off:off+11264];p=copy.copy(t)
  p.idx=np.frombuffer(b[:10240],dtype='uint8').reshape(64,160).copy();p.orig=p.idx.copy()
  p.pal=np.array([(r,g,b,min(255,a*2)) for r,g,b,a in tim2.unswz32([tuple(b[j:j+4]) for j in range(10240,11264,4)])],dtype='uint8')
  p.im=Image.fromarray(p.pal[p.idx]);p.regions=[]
  if frame==0:p.text((0,0,160,64),s,size=29,fg=colors[frame],outline=2,inkbox=False)
  else:
   rgba=p.pal[p.orig];white=(rgba[:,:,:3].min(2)>230)&(rgba[:,:,3]>200)
   seed=np.zeros((64,160),bool);seed[0,:]=True;seed[-1,:]=True;seed[:,0]=True;seed[:,-1]=True
   exterior=binary_propagation(seed&~white,mask=~white)
   bg=int(np.sum((p.pal.astype(float)-[255,255,255,255])**2,axis=1).argmin())
   p.text((5,5,155,56),s,size=28,fg=colors[frame],bg=bg,outline=2,inkbox=False)
   p.idx[exterior]=p.orig[exterior]
  if frame==0:t.idx=p.idx.copy()
  else:
   if not hasattr(t,'extra_patches'):t.extra_patches=[]
   t.extra_patches.append((off,p.idx.tobytes()))
  t.regions.append(dict(box=[0,0,160,64],text=s,frame=frame))
  Image.fromarray(p.pal[p.idx]).save(W/'audit'/f'player_frame_{frame}.png')

def apply(label,column,whole,T):
 # 표의 칸과 선은 원본을 복원한 후, 각 칸 내부에서만 글자를 교체한다.
 for i in [818,819]:
  t=T(i);t.__dict__.update(Texture(i).__dict__)
  label(i,(181,4,398,33),'능력치 확인',bg=int(t.orig[20,450]),fg=(255,255,255),outline=1,inkbox=False)
  for box,s,sample in [((189,36,290,58),'최고 기록',(40,184)),((347,36,450,58),'이번 기록',(36,465)),((197,219,289,242),'평생 평균',(220,190)),((347,219,451,242),'이번 기록',(220,470))]:
   label(i,box,s,size=18,bg=int(t.orig[sample]),fg=(66,66,57),outline=0,inkbox=False)
  ss=['스코어','포인트','롱 퍼트','롱 칩인','최장 드라이브' if i==818 else '홀인원 수']
  for j,s in enumerate(ss):
   y=61+j*32;label(i,(12,y,176,y+24),s,size=21,bg=int(t.orig[y,171]),fg=(57,79,70),outline=0,inkbox=False)
  ss=['평균 어프로치','페어웨이 유지율','파 온 유지율','저스트 임팩트율'] if i==818 else ['평균 어프로치','평균 퍼트 수','페어웨이 유지율','홀인원 비율']
  for j,s in enumerate(ss):
   y=245+j*32;label(i,(12,y,176,y+24),s,size=19,bg=int(t.orig[y,172]),fg=(57,79,70),outline=0,inkbox=False)
  for y in ([190,278] if i==819 else []):
   label(i,(272,y,291,y+21),'회',size=17,bg=int(t.orig[y,268]),fg=(68,67,57),outline=0,inkbox=False)
   label(i,(392,y,411,y+21),'회',size=17,bg=int(t.orig[y,418]),fg=(68,67,57),outline=0,inkbox=False)
 # 종료 그림의 위 96픽셀은 배경 조각, 아래 32픽셀은 별도 버튼 안내 UV.
 t=T(538);t.__dict__.update(Texture(538).__dict__)
 label(538,(105,30,426,66),'수고하셨습니다.',size=29,fg=(245,224,177),outline=1,inkbox=False,outline_color=(173,85,20))
 label(538,(0,96,224,128),'○ 버튼을 눌러 주세요',size=20,fg=(235,235,235),outline=1,inkbox=False)
 # 이름 입력 도움말은 화면에서 축소되므로 진한 글씨와 짧은 표현을 사용한다.
 for i in [63,539]:
  for box,s in [((0,224,448,240),'SELECT: 한글 1 / 한글 2 / 영숫자'),((0,240,480,256),'START: 확인   □: 전체 삭제   ×: 한 글자 삭제')]:
   label(i,box,s,size=12,fg=(67,60,49),outline=0,inkbox=False,font_path=W.parent/'NanumSquareNeo-cBd.ttf')
 animation(T)
