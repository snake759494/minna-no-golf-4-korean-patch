"""2026-10-04 실기 스크린샷 및 전체 텍스처 대조 수정.
독립적으로 그려지는 숫자/단위/제목 조각의 UV 경계를 보존한다.
"""
import numpy as np
from scipy.spatial import cKDTree
from texture_patch import Texture

def apply(label,column,whole,T):
 from pathlib import Path
 T(1011).plate(Path(__file__).parent/'wall_title4_ko.png',[(64,43,381,125)],feather=3)
 for i in [1012,1013]:
  T(i).plate(Path(__file__).parent/'wall_title3_ko.png',[(114,50,371,111),(265,194,548,261)],feather=2)
 for i in range(323,335):
  T(i).plate(Path(__file__).parent/'online_title_ko.png',[(196,26,447,86),(197,144,444,202)])
 for i in [16,290]:
  T(i).art_region(Path(__file__).parent/'online_title_ko.png',(193,26,447,87),(513,80,564,92))
  T(i).art_region(Path(__file__).parent/'online_title_ko.png',(191,141,448,202),(509,101,566,115))
 for box in [(59,59,99,74),(3,155,43,170),(3,252,43,267),(3,294,43,309),(59,389,99,404)]:
  T(15).art_region(Path(__file__).parent/'loading_logo_ko.png',(208,21,351,63),box)
 T(10).plate(Path(__file__).parent/'rules_book_ko.png',[(26,151,94,193)])
 T(11).plate(Path(__file__).parent/'technique_books_ko.png',[(298,17,367,103),(426,17,495,103),(43,145,111,231),(170,145,239,231),(298,145,367,231),(406,290,473,347)])
 for target,source,box in [(878,10,(0,128,128,256)),(891,11,(384,256,512,384))]:
  t=T(target);src=T(source);x,y,xx,yy=box
  t.idx[:128,:128]=cKDTree(t.pal.astype(float)).query(src.pal[src.idx[y:yy,x:xx]].reshape(-1,4).astype(float))[1].reshape(128,128)
  t.regions.append(dict(box=[0,0,128,128],text='번역 소품 표지'))
 from texture_words import R
 # 빈 표지판은 같은 디스크의 원본. 외곽/나뭇결/색상표를 유지한다.
 blank=Texture(924);wood=blank.pal[blank.idx]
 signs={912:('혼자서 GOLF',(48,76,164)),913:('함께하는 GOLF',(178,28,28)),914:('데이터',(31,106,44)),915:('상점',(21,125,148)),916:('옵션',(95,47,126)),917:('토너먼트',(39,93,165)),918:('VS 모드',(177,32,35)),919:('트레이닝',(27,104,43)),920:('미니게임',(166,29,99)),921:('전국 대회',(97,44,126)),922:('스트로크',(39,93,165)),923:('매치 플레이',(175,38,43)),925:('상태',(33,83,150)),927:('아이템',(170,37,39))}
 for i,(s,color) in signs.items():
  t=T(i);box=(16,20,242,77);x,y,xx,yy=box
  t.idx[y:yy,x:xx]=cKDTree(t.pal.astype(float)).query(wood[y:yy,x:xx].astype(float).reshape(-1,4))[1].reshape(yy-y,xx-x)
  t.regions.append(dict(box=list(box),text='원본 빈 표지판 배경'))
  label(i,(23,27,233,69),s,bg='keep',fg=color,size=37,outline=0,inkbox=False)
 # 경기 시작 제목: '제', '회', '(통산', '회)'는 따로 잘라 그린다.
 T(656).__dict__.update(Texture(656).__dict__)
 column(656,0,0,192,40,R,outline=2)
 fragments=[((200,0,232,40),'제'),((236,0,264,40),'회'),((266,0,320,40),'(통산'),((324,0,360,40),'회)'),((400,0,464,40),'대회'),
 ((200,40,372,80),'쇼트 코스'),((384,40,512,80),'홀 승부'),((200,80,350,120),'매치 플레이'),((354,80,512,120),'스트로크'),
 ((200,120,408,160),'승급 시험'),((200,160,320,200),'VS 모드'),((324,160,420,200),'노멀'),((428,160,512,200),'하드'),
 ((200,240,288,264),'평균 타수'),((292,240,410,264),'최고 스코어'),((444,240,468,264),'타'),
 ((200,332,348,368),'퍼트 골프'),((352,332,408,368),'초급'),((412,332,468,368),'상급'),
 ((0,400,128,432),'앨버트로스'),((184,400,272,432),'이글'),((328,400,416,432),'버디'),((0,432,48,464),'파'),((104,432,176,464),'보기'),((232,432,352,464),'더블 보기'),((0,464,152,496),'트리플 보기')]
 for box,s in fragments:label(656,box,s,outline=2 if box[3]-box[1]>=32 else 1)
 # 상자 밖으로 삐져나온 원본 글자 테두리(잔상)를 지우고 번역 글자는 복원한다.
 t=T(656);done=t.idx.copy()
 for box,s in fragments:t.erase_ink(box)
 for (x,y,xx,yy),s in fragments:t.idx[y:yy,x:xx]=done[y:yy,x:xx]
 # 메뉴 및 시상식의 같은 형식도 함께 수정.
 for i in [93,824]:
  t=T(i)
  for box in [(0,320,104,346),(176,308,200,365)]:
   x,y,xx,yy=box;t.idx[y:yy,x:xx]=t.orig[y:yy,x:xx]
  label(i,(0,320,64,346),'(통산',outline=0)
  label(i,(64,320,104,346),'회)',outline=0)
  label(i,(176,308,200,338),'제',outline=0)
  label(i,(176,340,200,365),'회',outline=0)
 # 그림자/테두리까지 원본 셀 안에서 지우고 다시 그린다.
 label(64,(160,480,224,512),'랜덤',fg=(8,8,8),outline=0)
 label(46,(152,344,176,368),'높',outline=0)
 label(46,(200,344,224,368),'낮',outline=0)
 label(89,(240,0,256,24),'회',outline=0)
 label(89,(304,48,320,72),'회',outline=0)
 label(91,(160,456,192,480),'코스',outline=0)
 for i in [58,80,89,91,92,95,818,819,820,822,824,826]:
  # 나머지 숫자/기호는 원본 셀 그대로 유지.
  pass
 # 2D 상점/옵션/보상에 반복되는 책 표지.
 for i,box,color in [(65,(15,162,90,192),(255,232,112)),(10,(17,35,81,64),(255,230,110)),(10,(144,34,207,63),(72,246,245)),(14,(274,76,298,91),(255,236,110)),(14,(334,76,360,91),(72,246,245)),(874,(22,35,86,63),(255,230,110)),(875,(22,35,86,63),(72,246,245))]:
  t=T(i);t.clear_panel(box)
  label(i,box,'배경',fg=color,bg='keep',outline=1,inkbox=False)
 # 캐디 조작용 안내: 원래 서로 다른 문구를 같은 번역으로 덮었던 행.
 column(459,0,168,128,24,['으로 예고','칩인','예고!'],outline=0)
 label(459,(128,96,256,120),'메뉴로',outline=0)
 label(459,(128,120,256,144),'건너뛰기',outline=0)
 # 원본 글자판을 쓰는 경기 중 메시지와 COM 이름 203개.
 import compact_ko
 compact_ko.apply_textures(label,T)
 for i in [63,539]:
  for j,s in [(0,'한글 1'),(1,'한글 2')]:label(i,(405,8+j*32,492,37+j*32),s,bg=-1,fg=(255,255,255),outline=1)
  label(i,(0,224,448,240),'SELECT: 문자 전환 (한글 1 · 한글 2 · 영숫자)',outline=0)
 # 상 이름 오역: 10타 차 승리와 10경기 도달은 다르다.
 label(849,(0,152,T(849).im.width,T(849).im.height),'10경기 도달 기념',bevel=True)
 # 배경에 구워진 베팅 표는 단독 글자판과 좌표가 다르다.
 T(67).__dict__.update(Texture(67).__dict__)
 green=int(np.sum((T(67).pal[:,:3].astype(float)-[75,119,70])**2,axis=1).argmin())
 for box,s in [((375,59,465,84),'총상금'),((530,59,603,84),'포인트'),((23,134,122,161),'상금'),((23,165,122,192),'설정')]:label(67,box,s,bg=green,fg=(245,245,230),outline=0)
 for j,s in enumerate(['스코어','스킨스','나소','올림픽','니어핀','드라이브']):label(67,(135+j*82,104,204+j*82,129),s,bg=-1,fg=(245,245,230),outline=0)
 label(81,(175,162,471,190),'칩인 (버디 이상)',outline=0)
 label(81,(234,195,394,221),'승급 조건',outline=0)
 label(81,(0,293,47,316),'성적',bg=-1,fg=(70,70,50),outline=0)
 label(81,(374,292,432,317),'홀',bg=-1,fg=(70,70,50),outline=0)
 label(81,(4,320,113,342),'최고 기록',bg=-1,fg=(70,70,50),outline=0)
 label(81,(246,437,394,463),'파 온 유지율',bg=-1,fg=(70,70,50),outline=0)
 T(901).__dict__.update(Texture(901).__dict__)
 label(901,(70,53,230,108),'킹',bg=-1,fg=(255,210,20),outline=2,inkbox=False)
 label(58,(160,0,188,24),'점',outline=0)
 label(58,(160,24,188,48),'점',outline=0)
 # 대형 소품과 소형 목록 아이콘의 도안을 일치시킨다.
 white=int(((T(10).pal[:,:3].astype(float)-[246,246,224])**2).sum(1).argmin())
 column(10,84,292,25,18,['고','화','질'],size=17,fg=(60,24,150),bg=white,outline=0,inkbox=False)
 T(882).copy_sprite(T(10),(0,256,128,384),(0,0,128,128))
 for j in range(4):T(14).copy_sprite(T(10),(j*128,0,j*128+128,128),(192+j*64,64,256+j*64,128))
 T(14).copy_sprite(T(10),(0,128,128,256),(448,64,512,128))
 T(14).copy_sprite(T(10),(0,256,128,384),(192,128,256,192))
 for j,box in enumerate([(256,0,384,128),(384,0,512,128),(0,128,128,256),(128,128,256,256),(256,128,384,256)]):T(14).copy_sprite(T(11),box,(64+j*64,192,128+j*64,256))
 T(14).copy_sprite(T(11),(384,256,512,384),(192,256,256,320))
 label(14,(134,269,188,289),'예비',fg=(255,255,255),outline=0,inkbox=False)
 label(14,(128,288,192,310),'아이템',fg=(255,255,255),outline=0,inkbox=False)
