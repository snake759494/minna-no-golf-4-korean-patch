"""원본 디스크에 함께 들어 있는 온라인판 안내 이미지의 직접 번역."""
def apply(label,column,whole,T):
 from pathlib import Path
 plate=Path(__file__).parent/'online_background.png'
 pages={186:['PlayStation BB Unit에','이상이 발생했을 가능성이 있습니다.','','최신 PlayStation BB Navigator에 포함된','사용 설명서의 지시에 따라','PlayStation BB Unit을 진단·복구해 주세요.'],188:['「모두의 GOLF 온라인」의','게임 데이터가 손상되었습니다.','','이 상태로는 게임을 시작할 수 없습니다.','PlayStation BB Navigator에서','게임 데이터를 삭제한 다음','「모두의 GOLF 온라인」을 다시 설치해 주세요.'],279:['이 PlayStation BB Unit에','설치되어 있는','「모두의 GOLF 온라인」은','다른 PlayStation 2에서','설치된 것이므로','실행할 수 없습니다.'],288:['주의!!','','지난번 게임을 종료할 때','타이틀 화면의 「전원 끄기」를 선택하지 않고','게임을 종료했을 가능성이 있습니다.','타이틀 화면 이외에서 전원을 끄면','PlayStation BB Unit이 고장 날 수 있습니다.','정상 종료하려면 반드시 타이틀 화면에서','「전원 끄기」를 선택해 게임을 종료해 주세요.']}
 for i,ss in pages.items():
  t=T(i);t.plate(Path(__file__).parent/'storm_background.png',[(25,28,614,381)],feather=8)
  for j,s in enumerate(ss):
   if s:label(i,(35,35+j*37,604,70+j*37),s,size=29,fg=(255,176,25) if j>1 else (255,130,10),bg='keep',outline=2,inkbox=False)
  t.plate(Path(__file__).parent/'storm_background.png',[(138,391,509,435)],feather=5);label(i,(145,399,501,429),'○ 버튼을 누르면 전원이 꺼집니다' if i!=288 else '○ 버튼을 눌러 주세요',size=23,fg=(255,255,255),bg='keep',outline=1,inkbox=False)
 data={208:['PlayStation BB Unit이','올바르게 연결되지 않았습니다.','','올바르게 연결하고 다시 시작해 주세요.'],209:['PlayStation BB Unit이 연결되지 않았습니다.','「모두의 GOLF 온라인」을 플레이하려면','PlayStation BB Unit에','MB 이상의 빈 공간이 필요합니다.','올바르게 연결하고 다시 시작해 주세요.'],210:['PlayStation BB Unit의 빈 공간이 부족합니다.','「모두의 GOLF 온라인」을 플레이하려면','PlayStation BB Unit에','MB 이상의 빈 공간이 필요합니다.','빈 공간을 확보하고 다시 시작해 주세요.'],211:['PlayStation BB Unit이 초기화되지 않았습니다.','','PlayStation BB Unit을 초기화한 뒤','다시 시작해 주세요.'],212:['PlayStation 2 전용 네트워크 어댑터가','올바르게 연결되지 않았습니다.','','연결을 확인하고 다시 시작해 주세요.'],213:['「모두의 GOLF 온라인」을 플레이하려면','게임을 설치해야 합니다.','설치하려면 PlayStation BB Unit에','MB 이상의 빈 공간이 필요합니다.','설치를 시작하시겠습니까?'],280:['PlayStation BB Unit이','올바르게 연결되지 않았습니다.','','올바르게 연결하고 다시 시작해 주세요.'],281:['PlayStation BB Unit이','연결되지 않았습니다.','','올바르게 연결하고 다시 시작해 주세요.'],282:['게임 내용이 업데이트되었습니다.','온라인으로 플레이하려면 게임을 업데이트해야 하지만,','PlayStation BB Unit의 빈 공간이 부족합니다.','업데이트하려면 MB 이상의 빈 공간이 필요합니다.','빈 공간을 확보하고 다시 시작해 주세요.'],283:['PlayStation 2 전용 네트워크 어댑터가','올바르게 연결되지 않았습니다.','','연결을 확인하고 다시 시작해 주세요.'],284:['게임 내용이 업데이트되었습니다.','온라인으로 플레이하려면 업데이트가 필요합니다.','업데이트하려면 PlayStation BB Unit에','MB 이상의 빈 공간이 필요합니다.','업데이트하시겠습니까?']}
 for i,ss in data.items():
  t=T(i);t.plate(plate,[(234,8,410,128)],feather=5);t.plate(plate,[(22,128,615,326)],feather=8)
  for j,s in enumerate(ss):
   if s:label(i,(27,140+j*33,608,171+j*33),s,size=25,fg=(255,130,110) if j==0 and i not in [213,282,284] else (245,245,245),bg='keep',outline=1,inkbox=False)
  if i in [213,284]:
   t.plate(plate,[(85,364,558,422)])
   for j,s in enumerate(['「예」를 선택하면 '+('설치' if i==213 else '업데이트')+'를 시작합니다.','「아니요」를 선택하면 '+('전원이 꺼집니다.' if i==213 else '메인 메뉴로 돌아갑니다.')]):label(i,(89,364+j*30,552,393+j*30),s,size=23,fg=(255,245,70),bg='keep',outline=1,inkbox=False)
  else:
   t.plate(plate,[(154,386,489,414)]);label(i,(158,386,485,414),'○ 버튼: 메인 메뉴로' if i==282 else '○ 버튼을 누르면 전원이 꺼집니다',size=22,fg=(255,245,70),bg='keep',outline=1,inkbox=False)
 t=T(207);t.clear_panel((173,61,468,102));label(207,(176,62,465,101),'잠시만 기다려 주세요!',size=31,fg=(220,255,80),bg='keep',outline=2,inkbox=False)
 t.clear_panel((103,125,527,221))
 for j,s in enumerate(['다운로드 중입니다.','데이터가 손상될 수 있으므로','PlayStation 2 본체의 전원을 끄거나 리셋하거나','PlayStation BB Unit을 빼지 마세요.']):label(207,(106,126+j*23,524,149+j*23),s,size=18,fg=(255,255,255),bg='keep',outline=1,inkbox=False)
