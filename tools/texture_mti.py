"""MTI 결과 화면, 참가 안내 및 코스 소품의 직접 번역."""
import json,shutil
from pathlib import Path
W=Path(__file__).parent
WORDS={5:'멧비둘기',8:'휘파람새',29:'큰 파도 소리',39:'나뭇잎 소리',99:'까마귀',104:'뻐꾸기',125:'딱따구리',126:'트랙터',138:'닭',147:'군고구마 장수',175:'옛 우물',179:'베틀',183:'대나무 물받이',188:'개구리',189:'한밤중',190:'원숭이 무리',192:'호랑이',194:'열대의 새',197:'타잔',201:'고함원숭이',212:'와불상',216:'대나무자고',227:'학',257:'붉은배지빠귀',276:'울새',320:'박새',329:'두견새',330:'참매미',331:'유지매미',333:'애매미',334:'쓰르라미',338:'곰매미',339:'귀뚜라미',340:'방울벌레',341:'개 울음소리',2073:'— 최강판 —',2075:'참가 대기',2166:'스코어',2167:'포인트',2168:'핸디'}
for i,s in enumerate('아야|가즈마|푸린|무사시|사쿠라|가루다|브론슨|도기|마리온|팔콘|니나|Z|스즈키|히토미|실비아|레이라|쿠거|베이더|나나코|곤조|샤크|글로리아|린|로즈'.split('|'),2169):
 if s!='Z':WORDS[i]=s
EXTRA=[61,292,295,387,390,400,401,402,403,409,748,1147,1148,1192,1682,1960,2045,2100,2103,2193,2194]
def register():
 rows=json.loads((W/'texture_index.json').read_text(encoding='utf8'));audit=json.loads((W/'audit/mti/index.json').read_text(encoding='utf8'));mapping={}
 for aid in sorted(set(WORDS)|set(EXTRA)):
  r=audit[aid];found=next((x for x in rows if x.get('mti_audit')==aid),None)
  if found is None:
   i=len(rows);found={k:r[k] for k in ['name','archive','index','width','height']};found.update(id=i,format='MTI8' if r['psm']==19 else 'MTI4',mti_audit=aid)
   corrected=json.loads((W/'audit/mti_layout_fixed.json').read_text(encoding='utf8')) if (W/'audit/mti_layout_fixed.json').exists() else {}
   if str(aid) in corrected:
    first=corrected[str(aid)][0];found.update(palette_offset=first['palette_offset'],mips=first['mips'])
   rows.append(found)
   shutil.copyfile(W/'audit/mti'/f'{aid:04}.bin',W/'textures'/f'{i:04}.bin')
   shutil.copyfile(W/'audit/mti'/f'{aid:04}.png',W/'textures'/f'{i:04}.png')
  mapping[aid]=found['id']
 (W/'texture_index.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
 return mapping
def apply(label,column,whole,T):
 import numpy as np
 ids=register()
 for aid,s in WORDS.items():
  i=ids[aid];t=T(i)
  label(i,(0,0,t.im.width,t.im.height),s,outline=0,fg=(0,0,0) if aid<350 else None)
 i=ids[61];label(i,(5,8,59,33),'연못 주의!',size=17,fg=(255,255,255),bg=-1,outline=1,inkbox=False)
 i=ids[2194];column(i,0,0,128,64,['업','다운'],outline=0)
 label(ids[2193],(82,202,126,255),'점',outline=0)
 planes=json.loads((W/'audit/planes/index.json').read_text(encoding='utf8'))
 for aid,pid in [(1147,5440),(1148,5449)]:
  t=T(ids[aid]);meta=planes[pid];po=meta['palette_offset']
  palette=np.array([list(t.raw[j:j+3]) for j in range(po,po+64,4)],dtype=float)
  white=int(((palette-[238,237,225])**2).sum(1).argmin())
  bg=int(((palette-([164,42,61] if aid==1147 else [66,82,130]))**2).sum(1).argmin())
  for j,s in enumerate(['야키소바','음료','아이스크림','기타']):t.plane_text(meta,(0,j*16,46,j*16+16),s,size=10,fg=(190,81,80),bg=white,outline=0,inkbox=False,font_path=W.parent/'NanumSquareNeo-bRg.ttf')
  t.plane_text(meta,(47,0,128,17),'어서 오세요',size=10,fg=(25,25,35),bg=bg,outline=0,inkbox=False)
  t.plane_text(meta,(47,17,128,64),'해변 매점',size=22,fg=(241,240,227),bg=bg,outline=0,inkbox=False,font_path=W.parent/'SeoulHangangEB.ttf')
 for pid,s in [(9841,'어떤 걸로 할까요?'),(9842,'골라 주세요♪')]:
  T(ids[2045]).plane_text(planes[pid],(18,31,243,88),s,size=32,fg=(68,121,243),outline=1,bg=-1,inkbox=False)
 T(ids[748]).plane_text(planes[3956],(0,0,128,32),'사쿠라야마 미술관',size=22,fg=(157,157,157),outline=1)
 for box,s in [((47,9,211,52),'야키소바'),((9,4,41,50),'특제'),((219,4,250,50),'특제')]:
  T(ids[1192]).plane_text(planes[5635],box,s,size=32,fg=(244,235,211),bg=-1,outline=1,inkbox=False)
 for box,s in [((150,63,174,94),'어깨'),((198,61,222,94),'어깨'),((229,67,256,86),'목심'),((214,94,256,114),'꽃등심'),((165,110,199,133),'안심'),((109,97,135,115),'갈비'),((110,147,137,166),'갈비'),((222,136,256,156),'등심'),((226,170,256,191),'우둔')]:
  T(ids[1682]).plane_text(planes[7503],box,s,size=12,fg=(0,0,0),bg=-1,outline=0,inkbox=False)
 for box,s in [((28,7,48,37),'어깨'),((76,8,99,37),'어깨'),((164,8,185,37),'어깨'),((211,6,233,35),'어깨'),((238,10,256,32),'목심'),((92,40,155,59),'양지'),((47,57,82,78),'안심'),((181,54,215,77),'안심'),((111,109,160,128),'갈비'),((223,40,256,59),'꽃등심')]:
  T(ids[1960]).plane_text(planes[9047],box,s,size=12,fg=(0,0,0),bg=-1,outline=0,inkbox=False)
 i=ids[292]
 for box,s in [((58,54,194,69),'후지산케이 클래식'),((44,139,209,152),'대회 4일째 한정 · 복수 달성 시 균등 배분'),((31,159,226,193),'모두의 GOLF')]:label(i,box,s,fg=(255,255,255) if box[1]<159 else (44,73,157),bg=-1,outline=0,inkbox=False)
 label(ids[295],(28,103,145,117),'마쓰조노 골프 클럽',fg=(0,0,0),bg=-1,outline=0,inkbox=False)
 import numpy as np
 for aid,s,box,color,target in [(390,'오늘의주인공',(12,8,245,57),(14,14,75),(240,240,240)),(400,'사랑과분투',(9,4,120,29),(250,230,60),(174,0,0)),(401,'봉인금지',(9,4,120,29),(250,230,60),(174,0,0)),(402,'기사회생',(9,4,120,29),(250,230,60),(174,0,0)),(403,'일발역전',(9,4,120,29),(250,230,60),(174,0,0))]:
  t=T(ids[aid]);bg=int(((t.pal[:,:3].astype(float)-target)**2).sum(1).argmin());t.sideways_text(box,s,color,bg)
 t=T(ids[387]);bg=int(((t.pal[:,:3].astype(float)-[102,48,67])**2).sum(1).argmin())
 t.sideways_text((6,20,121,48),'골프대백과',(243,237,211),bg)
 opts=dict(size=11,fg=(242,235,208),bg=bg,outline=0,inkbox=False)
 t.rotated_labels([((3,79,35,93),'노려라',opts),((2,93,36,108),'버디!',opts),((41,76,73,90),'골프',opts),((41,90,73,106),'대백과',opts)])
 T(ids[295]).plate(W/'course_poster_ko.png',[(6,3,35,103),(148,3,191,99),(27,103,145,117),(205,51,251,124)])
 label(ids[295],(47,96,148,106),'가족 할인 시작!',size=8,fg=(0,0,0),bg=-1,outline=0,inkbox=False)
 for aid in [409,2100,2103]:T(ids[aid]).plate(W/'winner_banner_ko.png',[(0,0,256,98)])
