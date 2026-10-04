"""고정 1바이트 글자판의 원본 문자 순서. 일반 Shift-JIS 폰트와 별개."""
ROWS=[
 ' !?*+-/.,:~"°&\' ','0123456789%±:;  ','ABCDEFGHIJKLMNOP','QRSTUVWXYZymc__▶',
 'あいうえおかきくけこさしすせそ◀','ぁぃぅぇぉがぎぐげござじずぜぞ▼','たちつてとなにぬねのはひふへほ▲','だぢづでどぱぴぷぺぽばびぶべぼ回',
 'まみむめもや録ゆ画よらりるれろ水','わ っ攻をゃ略ゅ度ょん率現在位切',
 'アイウエオカキクケコサシスセソ旗','ァィゥェォガギグゲゴザジズゼゾ包','タチツテトナニヌネノハヒフヘホ失','ダヂヅデドパピプペポバビブベボ敗',
 'マミムメモヤ★ユ入ヨラリルレロ風','ワ木ッ当ヲャ点ュ第ョンヴ残り打目']
ALPHA=''.join(ROWS)
assert len(ALPHA)==256
def decode(b):return ''.join(ALPHA[c] for c in b)

if __name__=='__main__':
 import re
 from pathlib import Path
 for name,start in [('SYSTEM.BIN',0x120000),('GAME.BIN',0x164000),('MENU.BIN',0x7d000)]:
  b=(Path(__file__).parent/name).read_bytes()
  for m in re.finditer(rb'[^\x00]{2,40}\x00',b[start:]):
   q=m[0][:-1]
   if q.count(0xff)>2 or len(q)<3 or not any(c>=0xa0 for c in q):continue
   s=decode(q)
   if sum('ァ'<=c<='ヴ' or 'あ'<=c<='ん' for c in s)<len(q)*.65:continue
   print(name,hex(start+m.start()),q.hex(),s)
