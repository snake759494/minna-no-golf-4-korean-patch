"""1바이트 이름·경기 메시지 직접 번역. 코드/포인터에는 손대지 않는다."""
from pathlib import Path
import json
from compact_font import ALPHA,decode
W=Path(__file__).parent
NAMES='''기스케|기요시|히사오|아키요시|쓰네히코|쇼고|야와라|분타|히로에|시바쿄|류노스케|가즈히로|다이스케|루미코|센다히사미|후지노리카|다이키|교코|가즈키치|히로노리
마사미|반초|진이치|도시아키|아케본|미키|고지고지|아이코|시게짱|치아키|아유무|이사오|고노스케|후미히코|히데키|아이|다쿠미|야나아쓰|다쓰요리|유키코
왕짱|겐타로|미카|다쓰노리|하마라|하지메|도시유키|마차키|도모미|게이이치로|다카시|헤짱|히로유키|다레오|마사아키|산짱|다이사쿠|데쓰야|우에스기|오타니
사노|시이나|후타무라|모리야|하야카와|히데쿠라|후지와라|이소베|미치로|영맨|히데|순스케|기바짱|마사시|미즈노|미야키|아사카와|이치시게|마스모토|구라이시
마쓰조|다쓰카와|다케짱|가네코|에가오|도미카와|고바야시|딕|리|아폴리|로버트|박|첸|알베르토|론|리처드|폴|기리타|모리스|다케노
스콧|탄|디아스|도쿠나카|사모르|에번스|마루야마|김|제이콥|스티브|해리슨|아키라|스파이크|사에키|카를로스|켄|고마쓰|사토|체스바|기무라
고다|조셉|마루카와|피에르|고사카|나카니시|이노우에|마쓰모토|니시무라|사와무라|나가세|손|요코자와|모리에|가젬|가와사키|페이|노부타|김다쿠|요네고
샤빈|다니테쓰|양|스메스메|가세키|야부타|노무라|시라키|곤살레스|도조|하세베|야스오카|이나가키|제이크|아리가|워런|미쓰이시|길버트|오바야시|무로이
마이어|실버|다자와|바넷|나가누마|아키야마|뮐러|이마이치|스미스|로베르토|구로사카|모토쿠라|크로켓|다테니|쓰쓰미|세키구치|시바타|노자와|나이토|나카무라
후지타|미타무라|핫토리|쓰노다|야마쿠라|가타오카|다카하시|데즈카|와다|구로카와|모리나가|이시하라|야부키|오가와|하야세|사카이|와카바야시|쓰지|나오치루|다케이
스즈토|휴가|미야후민'''.replace('\n','|').split('|')
assert len(NAMES)==203
# 서로 다른 표현식과 고정 글자 호출에 쓰이는 슬롯은 고정한다.
FIXED={0x7f:'회',0x86:'녹',0x88:'화',0x8b:'음',0x8f:'물',0x93:'공',0x96:'략',0x98:'도',0x9b:'률',0x9c:'현',0x9d:'재',0x9e:'위',0x9f:'수',0xaf:'성',0xbf:'공',0xcf:'실',0xdf:'패',0xe8:'입',0xef:'풍',0xf1:'목',0xf3:'적',0xf6:'점',0xf8:'제',0xfc:'남',0xfd:'음',0xfe:'타',0xff:'째'}
MESSAGES={0x16e820:'드라이브',0x16e828:'니어핀',0x16e900:'페어웨이 유지',0x16e908:'파 온 유지',0x16e910:'원더풀',0x16e918:'미러클!',0x16e920:'핀 샷!',0x16e928:'파',0x16e930:'버디!',0x16e938:'이글!',0x16e940:'홀인원!',0x16e950:'앨버트로스!',0x16e958:'칩인',0x16e960:'칩인!',0x16e968:'롱 퍼트',0x16e970:'물수 성공!',0x16e978:'물수 실패',0x16e988:'언플레이어블',0x16e990:'워터 해저드',0x16e998:'벙커',0x16e9c0:'페어웨이 유지!',0x16e9d0:'파 온 유지!',0x16e9e0:'언더 파 온!',0x16e9f0:'파!',0x16e9f8:'롱 퍼트!',0x16ea00:'워터 해저드',0x16ea10:'물수 횟수!',0x16ea18:'물수 실패...',0x16ea28:'감쌌다!',0x16ea30:'라이징 볼!',0x16ea40:'호밍!',0x16ea48:'빙글 샷!',0x16ea58:'빙글 퍼트!'}
MESSAGES.update({0x16ede8:'페어웨이',0x16edf0:'파 온',0x16edf8:'언더 파 온',0x16ee08:'홀 최고',0x16ee70:'나무에 맞아 +2타',0x16ee80:'러프에 들어 +2타',0x16ee90:'벙커에 들어 +2타',0x16eea8:' 획득',0x16eeb0:'코스 공략도 상승'})

def mapping():
 base=set(''.join(NAMES)+''.join(s for p,s in MESSAGES.items() if p<0x16ede8))-set(' !.-')-set(FIXED.values())
 added=set(''.join(MESSAGES.values()))-base-set(' !.-+2')-set(FIXED.values())
 chars=sorted(base)+sorted(added)
 reserved=set(FIXED)|{0x4f,0x5f,0x6f,0xe6}
 slots=[i for i in range(64,256) if i not in reserved]
 assert len(chars)<=len(slots),(len(chars),len(slots))
 result={**FIXED,**dict(zip(slots,chars))}
 extras=iter(chr(c) for c in range(0xac00,0xd7a4) if chr(c) not in result.values())
 for slot in slots[len(chars):]:result[slot]=next(extras)
 return result
def patch(binaries):
 cmap=mapping();inv={c:i for i,c in cmap.items()};inv.update({' ':15,'!':1,'.':7,'-':5,'+':4,'2':0x12})
 records=[]
 def put(name,p,s,capacity):
  b=binaries[name];old=bytes(b[p:p+capacity]);new=bytes(inv[c] for c in s)
  assert len(new)<capacity,(hex(p),s,capacity)
  b[p:p+capacity]=new+bytes(capacity-len(new));records.append(dict(file=name,offset=p,original=decode(old.split(b'\0')[0]),korean=s,original_hex=old.hex(),new_hex=b[p:p+capacity].hex()))
 for i,s in enumerate(NAMES):put('SYSTEM.BIN',0x123580+8*i,s,8)
 source=(W/'GAME.BIN').read_bytes()
 for p,s in MESSAGES.items():
  end=source.index(0,p)
  while end<len(source) and source[end]==0:end+=1
  put('GAME.BIN',p,s,end-p)
 (W/'compact_applied.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
 return records
def apply_textures(label,T):
 for i in [55,336,337,450,540]:
  t=T(i);cell=t.im.width//16
  for slot,s in mapping().items():
   x=slot%16*cell;y=slot//16*cell
   label(i,(x,y,x+cell,y+cell),s,size=round(cell*.70),fg=(255,255,255),outline=0,inkbox=False,font_path=W.parent/'NanumSquareNeo-bRg.ttf')
