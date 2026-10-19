def apply(label,column,whole,T):
 from pathlib import Path
 from texture_words import C
 column(1,444,400,68,24,['2급품','1급품','특급품'])
 label(68,(341,1,378,27),'남은',bg=-1,fg=(255,255,255),outline=0)
 label(68,(430,1,451,27),'초',outline=0)
 label(452,(0,0,40,20),'남은',outline=0);label(452,(72,12,96,32),'초',outline=0)
 for box,s in [((13,12,53,36),'순위'),((82,12,172,36),'플레이어'),((216,12,272,36),'스코어'),((326,12,392,36),'포인트')]:label(83,box,s,bg=-1,fg=(60,60,55),outline=0)
 for i in range(214,223):
  for j,s in enumerate(['클럽','볼','코스','캐디','의상','의상','캡슐','기타','기타']):label(i,(40+j*64,88,89+j*64,110),s,bg=-1,fg=(66,55,44),outline=0,inkbox=False)
 column(187,16,97,72,24,['파워','컨트롤','임팩트','스핀'],bg=-1,fg=(104,107,69),outline=0)
 label(187,(16,198,58,219),'휘기',bg=-1,fg=(104,107,69),outline=0)
 label(187,(126,198,177,219),'비거리',bg=-1,fg=(104,107,69),outline=0)
 for i in range(293,312):
  n=5+(i-293)//2
  label(i,(101,20,527,53),f'능력치 · 코스 {n} (                  )',bg=-1,fg=(245,245,245),outline=1)
  label(i,(32,107,125,127),'최고 기록',bg=-1,fg=(75,75,52),outline=0)
  label(i,(408,85,533,107),'18홀 라운드 수:',bg=-1,fg=(75,75,52),outline=0)
  label(i,(592,86,612,108),'회',bg=-1,fg=(75,75,52),outline=0)
  column(i,34,129,73,24,['스코어','포인트','롱 퍼트','롱 칩인','최장 드라이브','평균 퍼트 수','페어웨이 유지율','파 온 유지율'],bg=-1,fg=(92,108,122),outline=0)
  if i%2:
   for x in [248,432]:
    for dx,ww,s in [(0,48,'홀'),(74,31,'최고'),(107,66,'평균 스코어')]:label(i,(x+dx,129,x+dx+ww,152),s,bg=-1,fg=(92,108,122),outline=0)
   label(i,(56,328,124,348),'앨버트로스',bg=-1,fg=(113,95,44),outline=0)
  else:
   label(i,(346,109,376,128),'명 중',bg=-1,fg=(90,90,65),outline=0)
   label(i,(414,109,477,128),'전국 1위',bg=-1,fg=(90,90,65),outline=0)
   label(i,(536,109,591,128),'편차치',bg=-1,fg=(90,90,65),outline=0)
   label(i,(436,326,506,346),'종합 평가',bg=-1,fg=(92,108,122),outline=0)
   for y in [130,154,178,202,226]:label(i,(351,y,372,y+22),'위',bg=-1,fg=(90,90,65),outline=0)
 for i,s in enumerate(C,265):
  T(i).plate(Path(__file__).parent/f'course_bg_{i}.png',[(18,12,555,56)],feather=6)
  label(i,(28,20,360,48),s,size=23,fg=(255,255,255),bg='keep',outline=1,inkbox=False,align='left')
 from pathlib import Path
 t=T(278);t.plate(Path(__file__).parent/'loading_background.png',[(48,126,598,378)])
 lines=['쇼트 코스는 모든 홀이 PAR 3이므로','어느 홀에서든 홀인원을 노릴 수 있어요.','각 홀에는 니어핀 거리가 기록됩니다.','가장 좋은 기록은 홀인원 (0m)입니다.','1타로 그린에 올리지 못했을 때는','15.0m로 기록됩니다.']
 for j,s in enumerate(lines):label(278,(70,138+j*38,576,168+j*38),s,size=23,fg=(245,245,245),bg='keep',outline=1,inkbox=False)
 import numpy as np
 t.plate(Path(__file__).parent/'loading_logo_ko.png',[(208,21,351,63)])
 label(550,(20,112,216,136),'월  일까지 남은    회',outline=0)
 label(550,(20,136,216,160),'월  일  시  분 ~',outline=0)
 label(550,(0,160,224,184),'참가 횟수   회 신청 스코어',outline=0)
 label(550,(0,184,176,208),'개최 기간  기타',outline=0)
 label(550,(0,208,112,232),'개최 코스',outline=0)
 label(550,(4,248,148,272),'대회에 참가',outline=0)
 label(550,(4,280,148,305),'중간 순위 확인',outline=0)
 label(550,(177,240,249,268),'개최 중!',bg=-1,fg=(255,255,255),outline=0)
 label(550,(3,310,109,338),'상품 있음!!',bg=-1,fg=(255,255,255),outline=0)
 column(550,0,416,88,24,['대회 선택','내용 표시','돌아가기'],outline=0)
 column(550,96,416,80,24,['결정','상품 표시'],outline=0)
 label(550,(256,442,371,501),'제한 대회',outline=0)
 label(598,(64,0,128,40),'짝짝!',size=20,outline=1)
 label(598,(0,32,48,80),'아~',size=20,outline=1)
 label(598,(0,88,128,126),'아~아',size=20,outline=1)
 # 전국 대회는 원본 서비스 안내를 한국어로 충실하게 옮긴다.
 label(549,(142,18,501,62),'전국 대회 모드란?',bg=-1,fg=(255,255,255),outline=2,inkbox=False)
 t=T(549);t.clear_panel((46,75,601,337))
 ss=['전국 대회 모드는 모두의 GOLF 4에서 열리는','대회에 참가해 일본 전역의 플레이어와 겨루는 모드입니다.','메일 주소가 있고 휴대전화 또는 PC로','인터넷을 이용할 수 있다면 누구나 참가할 수 있습니다.','홈페이지에서 등록한 뒤 발급받은 참가 암호를 입력하세요.','상위 입상 시 메모리 카드 (PS2)가 필요할 수 있으니','플레이 데이터를 지우지 말고 보관해 주세요.']
 for j,s in enumerate(ss):label(549,(50,78+j*35,590,108+j*35),s,size=22,fg=(245,245,245),bg='keep',outline=1,inkbox=False)
 label(549,(229,334,411,360),'↓ 자세한 안내 ↓',bg=-1,fg=(255,255,255),outline=1)
 label(549,(100,399,553,430),'○ 버튼: 다음   × 버튼: 메뉴로 돌아가기',bg=-1,fg=(255,255,255),outline=1)
