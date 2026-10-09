"""매 릴리즈에 와이드 자산, 해시 및 상세 설명을 함께 준비한다."""
from pathlib import Path
import hashlib,json,shutil,argparse

def prepare(repo,notes,assets):
    manifest=repo/'release_manifest.json'
    m=json.loads(manifest.read_text(encoding='utf8'))
    name=m.get('widescreen',{}).get('name','SCPS-15059_BC4C7335.pnach')
    patch=repo/'patches'/name
    data=patch.read_bytes()
    if b'[Widescreen 16:9]' not in data:raise ValueError('와이드 패치 섹션 누락')
    crc=patch.stem.rsplit('_',1)[-1]
    m['widescreen']=dict(name=name,crc=crc,size=len(data),sha256=hashlib.sha256(data).hexdigest(),required_release_asset=True)
    manifest.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    assets.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(patch,assets/name)
    body=notes.read_text(encoding='utf-8-sig').replace('최초 공개 테스트 릴리즈입니다.','공개 릴리즈입니다.').replace('릴리즈 첨부는 xdelta 차분 하나입니다.','릴리즈에는 xdelta 차분과 선택형 PCSX2 와이드 패치를 첨부합니다.')
    body=body.split('\n<!-- WIDESCREEN -->')[0].rstrip()
    detail=(repo/'docs/WIDESCREEN.md').read_text(encoding='utf8')
    body+='\n\n<!-- WIDESCREEN -->\n'+detail+f'\n와이드 패치 SHA-256: `{m["widescreen"]["sha256"]}`\n'
    notes.write_text(body,encoding='utf8')
    return m['widescreen']

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--notes',type=Path,required=True)
    p.add_argument('--assets',type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(prepare(Path(__file__).resolve().parent.parent,a.notes,a.assets),ensure_ascii=False))
