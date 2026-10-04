import json,hashlib,io
from pathlib import Path
from PIL import Image
import catalog
W=Path(__file__).parent;rows=json.loads((W/'texture_index.json').read_text(encoding='utf8'));records=json.loads((W/'resource_catalog.json').read_text(encoding='utf8'));variants=json.loads((W/'texture_variants.json').read_text(encoding='utf8'))
with catalog.ISO.open('rb') as f:
 for v in variants:
  if any(r.get('variant_hash')==v['hash'] and r['name']==v['name'] for r in rows):continue
  r=next(r for r in records if r['path']==v['path']);e=next(e for e in r['entries'] if e['name']==v['name']);f.seek(r['lba']*2048);raw=catalog.entry(f.read(r['size']),e['index']);assert hashlib.sha256(raw).hexdigest()==v['hash']
  im=Image.open(io.BytesIO(raw));i=len(rows);rows.append(dict(id=i,name=e['name'],archive=v['path'],index=e['index'],width=im.width,height=im.height,variant_hash=v['hash']));(W/'textures'/f'{i:04}.bin').write_bytes(raw);im.convert('RGBA').save(W/'textures'/f'{i:04}.png');print(i,v['name'])
(W/'texture_index.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
