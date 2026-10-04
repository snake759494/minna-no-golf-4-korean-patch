"""xdelta 복원 결과를 임시 ISO 없이 검증한다."""
import argparse,hashlib,json,subprocess
from pathlib import Path

def sha256(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(8<<20),b''):h.update(b)
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path)
    p.add_argument('patch',type=Path)
    p.add_argument('--xdelta',default='xdelta3')
    a=p.parse_args()
    m=json.loads((Path(__file__).parent.parent/'release_manifest.json').read_text(encoding='utf8'))
    for path,entry in [(a.source,m['source']),(a.patch,m['patch'])]:
        if path.stat().st_size!=entry['size'] or sha256(path)!=entry['sha256']:
            raise SystemExit(f'해시 또는 크기 불일치: {path}')
    proc=subprocess.Popen([a.xdelta,'-d','-c','-s',str(a.source),str(a.patch)],stdout=subprocess.PIPE)
    h=hashlib.sha256();size=0
    while b:=proc.stdout.read(8<<20):h.update(b);size+=len(b)
    if proc.wait()!=0 or size!=m['target']['size'] or h.hexdigest()!=m['target']['sha256']:
        raise SystemExit('복원 검증 실패')
    print('복원 검증 통과:',h.hexdigest())

if __name__=='__main__':main()
