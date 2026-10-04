"""화면을 대조하며 직접 작성한 이미지 번역과 원본 UV 영역."""
from texture_patch import Texture,W
import translations as tr
import json
items={}
def T(i):
 if i not in items:items[i]=Texture(i)
 return items[i]
def label(i,box,s,**kw):T(i).text(box,s,**kw)
def whole(i,s,**kw):
 t=T(i);label(i,(0,0,t.im.width,t.im.height),s,**kw)
def column(i,x,y,w,h,ss,**kw):
 for j,s in enumerate(ss):
  if s:label(i,(x,y+j*h,x+w,y+(j+1)*h),s,**kw)
N=list(tr.NAMES.values());C=list(tr.COURSES.values())
R='루키|연습생|일본 아마추어|세계 아마추어|프로|시드 프로|일본 대표|메이저|월드 스타|킹'.split('|')
def main():
 titles='혼자서 GOLF|함께하는 GOLF|캐릭터 선택|1P 캐릭터 선택|2P 캐릭터 선택|3P 캐릭터 선택|4P 캐릭터 선택|코스 선택|데이터|아이템|결과 발표|불러오기|메인 메뉴|미니게임|특전 영상|매치 플레이|전국 대회|플레이 데이터 만들기|옵션|플레이어 선택|최종 확인|저장|상점|스트로크|상태|상급 상태|토너먼트|연습|VS 모드|대전 상대 선택|VTR 재생'.split('|')
 for i,s in enumerate(titles,552):whole(i,s,bevel=True)
 for i,s in enumerate(['실시간 대회','자유 대전','매치 플레이','스트로크','새 전국 대회','니어핀 성적'],906):whole(i,s,bg=-1,fg=(255,255,255),outline=1)
 for i,s in enumerate(N[:24],513):
  if s!='Z':whole(i,s)
 rows,trans=tr.menu()
 for i in range(128):whole(658+i,trans[689+i])
 singles={69:'실시간 대회',70:'제한 대전',71:'자유 대전',72:'매치 플레이',73:'스트로크',74:'새 전국 대회',75:'니어핀 성적',76:'베팅 표',585:'빠직!',586:'퍼덕!',587:'최장 드라이브',588:'최근접 기록',591:'보스',595:'쿵!!',599:'바삭!',600:'철컥!',601:'쿵!',602:'합계',603:'당신의 승리',604:'당신의 패배',605:'무승부',607:'토탈 이븐',608:'포인트 즉결 승부',609:'의 승리',610:'도미 홀',611:'서든데스',612:'무승부여도 승패가 결정됩니다',613:'먼저 1UP한 쪽이 승리',614:'깡',615:'기록 경신!!',616:'툭',617:'경신 찬스!!',618:'빙글',619:'빙글빙글',620:'롱 퍼트',621:'롱 칩인',623:'나이스 인!',624:'컵인',625:'남은 거리',626:'나이스 온!',627:'나이스 어프로치!',628:'프린지',629:'카트 길',630:'베어 그라운드',631:'그린',632:'세미 러프',634:'나이스 터치!',635:'그레이트 샷!!',636:'파인 샷!',637:'슈퍼 샷!',638:'울트라 샷!',639:'페어웨이',640:'러프',641:'벙커',645:'기브업',646:'콜드 게임',649:'워터 해저드',650:'언플레이어블',652:'퐁당',792:'넣으면 무승부',793:'넣으면 승리',794:'승부를 결정할 퍼트',812:'칩인',813:'점'}
 for i,s in singles.items():whole(i,s,bevel=(i not in [602,607,608,609,612,613,617,620,621,625,792,793,794,813]))
 for i in [18,19]:
  k=(i-18)*12;column(i,0,0,128,40,N[k:k+6]);column(i,128,0,128,40,N[k+6:k+12])
 column(2,0,0,128,24,['스탠더드 볼','비기너 볼','빅 에어 볼','핀홀 볼','터보 스핀 볼','인피니티 볼','스트레이트 볼','사이드 스핀 볼'])
 column(2,128,0,128,24,['스탠더드 클럽','모두의 클럽','빅 에어 클럽','핀홀 클럽','터보 스핀 클럽','인피니티 클럽','비기너 클럽','100t 망치'])
 column(38,0,0,312,32,'기대의 신성|중국의 격투 소녀|닌자 골퍼 등장|에도 토박이 아저씨의 귀환|호주의 톱 프로|고운 기모노 아가씨|사무라이 골퍼 등장|황야의 쿨 가이|불굴의 제왕|완·전·부·활!'.split('|'))
 column(38,312,0,312,32,'캔자스의 폭주 트레일러 사나이|어둠의 지배자|아름다운 흑표범|말랑 발바닥의 왕자|골프를 과학하는 여자|북유럽의 요정|러시아에서 사랑을 담아|아름다운 이기주의자|어둠의 저격수|전설의 골프 신선'.split('|'))
 column(39,0,0,312,32,'낮잠은 끝! 꼬마도 진심|중국의 꽃 아가씨 백화난무!|닌법 절대 지지 않는 술법!|웃기지 말라고!|공포! 상처 입은 상어 사나이|때로는 이글! 때로는 보기!|드디어 발견! 멍멍 골퍼?|적? 아군? 떠돌이 골퍼|딥 임팩트!|바이올런스 히어로'.split('|'))
 column(39,312,0,312,32,'시간 무제한 단판 승부!|배틀 사이보그 등장!|파워 엘리트|가까이 오면 물어!|화려한 댄서|매혹의 프리마돈나|절대 영도의 미소|맹독의 장미|쿨 뷰티|페어웨이의 마술사'.split('|'))
 column(40,0,0,128,24,['모두골프 '+s for s in ['5급','4급','3급','2급','1급','초단','2단','3단']])
 column(40,128,0,128,24,['모두골프 '+s for s in ['4단','5단','사범','장군','왕','천사','신','맨']])
 label(94,(0,0,416,32),'처음부터 (플레이 데이터를 만듭니다)',bevel=True)
 label(94,(0,32,200,64),'이어서 플레이',bevel=True)
 label(94,(0,64,120,96),'특전 영상',bevel=True)
 column(460,0,0,128,24,'다음|리플레이|카메라 초기화|건너뛰기|확대|축소|수동 녹화'.split('|'))
 label(538,(0,0,512,64),'수고하셨습니다.')
 label(538,(0,64,512,128),'○ 버튼을 눌러 주세요')
 for i,s in enumerate(R,892):label(i,(18,57,288,108),s,bevel=True,bg=-1,inkbox=False)
 gear=['빅 에어 클럽','핀홀 클럽','터보 스핀 클럽','인피니티 클럽','100t 망치']
 for i in range(827,842):label(i,(0,128,T(i).im.width,152),gear[(i-827)//3]+' ('+['2급품','1급품','특급품'][(i-827)%3]+')')
 rewards={842:'비기너 볼',843:'빅 에어 볼',844:'핀홀 볼',845:'터보 스핀 볼',846:'인피니티 볼',847:'스트레이트 볼',848:'사이드 스핀 볼',849:'가와나 호텔 골프 코스',850:'퍼트 골프 상급 코스',851:'(캐디) 유미',852:'(캐디) 오지',853:'(캐디) 샌디',854:'(캐디) 간테쓰',855:'(캐디) 푸치',856:'(캐디) 할머니',857:'(캐디) 피포사루',858:'아야 특별 의상',859:'가즈마 특별 의상',860:'스즈키 특별 의상',861:'나나코 특별 의상',874:'배경 세트 1',875:'배경 세트 2',876:'모두의 CD / 음악편',877:'모두의 CD / 음성편',878:'특별 규칙',879:'야유 도구',880:'변성 도구',881:'낙하 지점 격자',882:'VTR 증설',883:'리플레이 추가 카메라 A',884:'리플레이 추가 카메라 B',885:'리플레이 추가 카메라 C',886:'세리머니 추가 카메라',887:'어드레스 추가 카메라',888:'메뉴 캐릭터 「아야」',889:'메뉴 캐릭터 「가루다」',890:'메뉴 캐릭터 「니나」',891:'NEW 대타권'}
 rewards.update({i:f'캡슐 {i-861}' for i in range(862,874)})
 for i,s in rewards.items():label(i,(0,128,T(i).im.width,152),s)
 # 보상 문구는 별도 UV 행이다.
 awards={849:'10타 차 승리 기념',850:'퍼트 골프 공략상',855:'칩인 특별상',857:'백 티 라운드 기념',858:'VS 하드 모드 특별상',877:'전 캐릭터 획득 기념',878:'VS 모드 특별상',879:'VS 모드 특별상',880:'VS 하드 모드 특별상',885:'칩인 특별상',886:'홀인원상',887:'앨버트로스상',888:'특별상',889:'VS 모드 특별상',890:'VS 모드 특별상'}
 awards.update({i:'특별상' for i in range(862,874)})
 for i,s in awards.items():label(i,(0,152,T(i).im.width,T(i).im.height),s,bevel=True)
 import texture_atlases
 texture_atlases.apply(label,column,whole,T)
 import texture_more
 texture_more.apply(label,column,whole,T)
 import loading_ko
 loading_ko.apply(label,column,whole,T)
 import texture_final
 texture_final.apply(label,column,whole,T)
 import texture_legacy
 texture_legacy.apply(label,column,whole,T)
 import texture_revision
 texture_revision.apply(label,column,whole,T)
 import texture_mti
 texture_mti.apply(label,column,whole,T)
 import texture_fix2
 texture_fix2.apply(label,column,whole,T)
 if (W/'main_title_ko.png').exists():T(564).compiled_art(W/'main_title_ko.png',(30,7,226,43),'메인 메뉴')
 reports=[t.save() for t in items.values()]
 (W/'texture_changes.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf8')
 print('이미지',len(reports),'번역 영역',sum(len(r['regions']) for r in reports),flush=True)
if __name__=='__main__':main()
