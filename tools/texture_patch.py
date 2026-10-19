"""한국어 UI 글립을 원본 TIM2/BMP 색상표에 컴파일한다.
이미지 크기, CLUT, UV, 원본의 글자 이외 픽셀은 유지한다.
"""
from pathlib import Path
import json,struct,io,hashlib
import numpy as np
from scipy.spatial import cKDTree
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import tim2
W=Path(__file__).parent
FONT=W.parent/'NanumSquareNeo-eHv.ttf'
def mip_updates(idx,orig,pal,mips,raw,eight):
 """수정 영역에 대응하는 축소 단계만 갱신하며 원본 팔레트를 유지한다."""
 changed=Image.fromarray(((idx!=orig)*255).astype('uint8'))
 im=Image.fromarray(pal[idx]);tree=cKDTree(pal.astype(float))
 for level in mips[1:]:
  w,h,off=level['width'],level['height'],level['offset'];size=level['size']
  a=np.frombuffer(raw[off:off+size],dtype='uint8')
  dest=a.reshape(h,w).copy() if eight else np.stack([a&15,a>>4],axis=1).reshape(h,w).copy()
  mask=np.asarray(changed.resize((w,h),Image.Resampling.BOX))>0
  rgba=np.asarray(im.resize((w,h),Image.Resampling.LANCZOS))
  dest[mask]=tree.query(rgba[mask].astype(float))[1]
  px=dest.ravel();yield off,px.tobytes() if eight else (px[::2]|(px[1::2]<<4)).tobytes()
class Texture:
 def __init__(self,i):
  self.id=i;self.raw=(W/'textures'/f'{i:04}.bin').read_bytes();b=self.raw
  if b[:4]==b'TIM2':
   self.g=tim2.parse(b)[0];self.im,idx,cl=tim2.to_image(b,self.g)
   assert idx is not None
   self.pal=np.array([(r,g,b,min(255,a*2)) for r,g,b,a in cl],dtype=np.uint8)
   self.idx=np.frombuffer(idx,dtype=np.uint8).reshape(self.im.height,self.im.width).copy()
  elif b[:2]!=b'BM':
   meta=json.loads((W/'texture_index.json').read_text(encoding='utf8'))[i]
   assert meta.get('format') in ('MTI8','MTI4')
   eight=meta['format']=='MTI8';w,h=meta['width'],meta['height'];po=meta.get('palette_offset',w*h if eight else w*h//2)
   self.g={'mti':True,'img_off':0,'w':w,'h':h,'itype':5 if eight else 4,'mips':meta.get('mips',[])}
   cl=[tuple(b[j:j+4]) for j in range(po,po+(1024 if eight else 64),4)]
   if eight:cl=tim2.unswz32(cl)
   self.pal=np.array([(r,g,b,min(255,a*2)) for r,g,b,a in cl],dtype=np.uint8)
   if eight:self.idx=np.frombuffer(b[:w*h],dtype=np.uint8).reshape(h,w).copy()
   else:
    a=np.frombuffer(b[:w*h//2],dtype=np.uint8);self.idx=np.stack([a&15,a>>4],axis=1).reshape(h,w).copy()
   self.im=Image.fromarray(self.pal[self.idx])
  else:
   self.g=None;im=Image.open(io.BytesIO(b));assert im.mode=='P'
   self.idx=np.array(im);self.im=im.convert('RGBA');p=im.getpalette();self.pal=np.array([p[j:j+3]+[255] for j in range(0,len(p),3)],dtype=np.uint8)
  self.orig=self.idx.copy();self.regions=[]
 def text(self,box,s,size=None,align='center',bevel=False,fg=None,bg=None,outline=None,inkbox=True,font_path=None,outline_color=None):
  x0,y0,x1,y1=map(int,box);assert 0<=x0<x1<=self.im.width and 0<=y0<y1<=self.im.height,(self.id,box)
  old=self.idx[y0:y1,x0:x1];rgba=self.pal[old];h,w=old.shape
  cachedir=W/'render_cache';cachedir.mkdir(exist_ok=True)
  settings=(box,s,size,align,bevel,fg,bg,outline,inkbox,'uv-fit-v5')
  if font_path:settings+=(str(font_path),)
  if outline_color:settings+=(tuple(outline_color),)
  cachekey=hashlib.sha256(self.pal.tobytes()+old.tobytes()+repr(settings).encode()).hexdigest()
  cachefile=cachedir/(cachekey+'.bin')
  if cachefile.exists():
   self.idx[y0:y1,x0:x1]=np.frombuffer(cachefile.read_bytes(),dtype=np.uint8).reshape(h,w)
   self.regions.append(dict(box=list(box),text=s));return
  transparent=self.pal[:,3].min()==0
  bgindex=int(np.bincount(old.ravel(),minlength=len(self.pal)).argmax())
  if transparent:bgindex=int(np.argmin(self.pal[:,3]))
  if bg is not None and bg!='keep':bgindex=int(np.bincount(np.concatenate([old[0],old[-1],old[:,0],old[:,-1]]),minlength=len(self.pal)).argmax()) if bg==-1 else int(bg)
  mask=(old!=bgindex)&(rgba[:,:,3]>32)
  ys,xs=np.where(mask)
  if not len(xs):
   if fg is None:raise ValueError(('빈 글자 영역',self.id,box,s))
   mask[:]=True;ys,xs=np.where(mask)
  if inkbox:
   bx0,bx1=int(xs.min()),int(xs.max())+1;by0,by1=int(ys.min()),int(ys.max())+1
  else:bx0,bx1,by0,by1=1,w-1,1,h-1
  # 원본 글자의 높이와 중심, UV 영역을 보존한다.
  gh=by1-by0;gw=bx1-bx0;fs=size or max(8,round(gh*.91));scale=4
  font=ImageFont.truetype(str(font_path or FONT),fs*scale)
  border=(max(1,round(gh*.065)) if bevel or transparent and len(self.pal)>16 else 0) if outline is None else outline
  bb=font.getbbox(s);mw=bb[2]-bb[0];mh=bb[3]-bb[1]
  m=Image.new('L',(mw+scale*2,mh+scale*2));ImageDraw.Draw(m).text((scale-bb[0],scale-bb[1]),s,font=font,fill=255,stroke_width=1)
  targeth=max(3,gh-2*border) if size is None else min(gh-2*border,max(5,round(m.height/scale)))
  targetw=min(gw-2*border if inkbox else w-2*border-2,max(2,round(m.width/m.height*targeth)))
  targetw=max(2,targetw)
  m=m.resize((targetw,targeth),Image.Resampling.LANCZOS)
  xx=(bx0+bx1-targetw)//2 if align=='center' else bx0
  xx=max(border,min(w-border-targetw,xx));yy=max(border,min(h-border-targeth,(by0+by1-targeth)//2))
  canvas=Image.fromarray(rgba) if bg=='keep' else Image.new('RGBA',(w,h),tuple(self.pal[bgindex]));a=Image.new('L',(w,h));a.paste(m,(xx,yy))
  pixels=rgba[mask].astype(float);lum=pixels[:,:3]@np.array([.299,.587,.114])
  dark=tuple(pixels[int(np.argmin(lum))].astype(int));dark=dark[:3]+(255,)
  if outline_color is not None:dark=tuple(outline_color)+(255,)
  if border:
   outer=a.filter(ImageFilter.MaxFilter(border*2+1));canvas.alpha_composite(Image.composite(Image.new('RGBA',(w,h),dark),Image.new('RGBA',(w,h)),outer))
  if fg is not None:colors=np.tile(np.array(fg[:3]),(h,1))
  else:
   brightest=pixels[lum>=np.quantile(lum,.72),:3].mean(axis=0);colors=np.tile(brightest,(h,1))
   if bevel:
    for y in range(h):
     q=max(0,min(1,(y-by0)/max(1,gh-1)))
     v=np.interp(q,[0,.35,.55,1],[1.12,1,.73,.88]);colors[y]=brightest*v
  fill=np.zeros((h,w,4),dtype=np.uint8);fill[:,:,:3]=np.clip(colors[:,None,:],0,255);fill[:,:,3]=np.array(a)
  canvas.alpha_composite(Image.fromarray(fill))
  if bevel:
   aa=np.array(a).astype(float)/255;dy=np.maximum(0,aa-np.roll(aa,1,axis=0))*.42
   hl=np.zeros_like(fill);hl[:,:,:3]=255;hl[:,:,3]=(dy*255).astype('uint8');canvas.alpha_composite(Image.fromarray(hl))
  dest=np.array(canvas).reshape(-1,4).astype(float);pal=self.pal.astype(float)
  dest[:,:3]*=dest[:,3:4]/255;pal[:,:3]*=pal[:,3:4]/255
  dest[:,3]*=1.4;pal[:,3]*=1.4
  self.idx[y0:y1,x0:x1]=cKDTree(pal).query(dest)[1].reshape(h,w)
  cachefile.write_bytes(self.idx[y0:y1,x0:x1].tobytes())
  self.regions.append(dict(box=list(box),text=s))
 def plate(self,path,boxes,feather=0):
  """복원한 배경의 지정 영역만 원본 CLUT와 픽셀 형식으로 컴파일."""
  im=Image.open(path).convert('RGBA').resize(self.im.size,Image.Resampling.LANCZOS)
  rgba=np.asarray(im);tree=cKDTree(self.pal.astype(float))
  for box in boxes:
   x,y,xx,yy=box
   dest=rgba[y:yy,x:xx].astype(float)
   if feather:
    h,w=yy-y,xx-x;gy,gx=np.mgrid[:h,:w]
    weight=np.clip(np.minimum.reduce([gx,gy,w-1-gx,h-1-gy])/feather,0,1)[:,:,None]
    dest=dest*weight+self.pal[self.orig[y:yy,x:xx]]*(1-weight)
   self.idx[y:yy,x:xx]=tree.query(dest.reshape(-1,4))[1].reshape(yy-y,xx-x)
   self.regions.append(dict(box=list(box),text='복원 배경'))
 def art_region(self,path,source_box,target_box,source_size=(640,448)):
  """이미 검수한 그림을 작은 포스터 등 동일 도안의 UV 영역에 삽입."""
  im=Image.open(path).convert('RGBA').resize(source_size,Image.Resampling.LANCZOS).crop(source_box)
  x,y,xx,yy=target_box;im=im.resize((xx-x,yy-y),Image.Resampling.LANCZOS)
  self.idx[y:yy,x:xx]=cKDTree(self.pal.astype(float)).query(np.asarray(im).reshape(-1,4).astype(float))[1].reshape(yy-y,xx-x)
  self.regions.append(dict(box=list(target_box),text='동일 로고 한글화'))
 def plane_text(self,meta,box,text,**kwargs):
  """한 MTI 안의 별도 팔레트를 가진 이미지에 글립을 컴파일."""
  p=Texture.__new__(Texture);p.id=self.id;p.regions=[]
  w,h=meta['width'],meta['height'];off=meta['offset'];po=meta['palette_offset'];eight=meta['psm']==19
  n=256 if eight else 16;cl=[tuple(self.raw[j:j+4]) for j in range(po,po+n*4,4)]
  if eight:cl=tim2.unswz32(cl)
  p.pal=np.array([(r,g,b,min(255,a*2)) for r,g,b,a in cl],dtype=np.uint8)
  original=self.raw[off:off+(w*h if eight else w*h//2)]
  prior=next((data for offset,data in reversed(getattr(self,'extra_patches',[])) if offset==off),original)
  a=np.frombuffer(prior,dtype=np.uint8)
  p.idx=a.reshape(h,w).copy() if eight else np.stack([a&15,a>>4],axis=1).reshape(h,w).copy()
  p.orig=p.idx.copy();p.im=Image.fromarray(p.pal[p.idx]);p.text(box,text,**kwargs)
  x,y,xx,yy=box;mask=np.zeros((h,w),bool);mask[y:yy,x:xx]=True;assert not np.any((p.orig!=p.idx)&~mask)
  pixels=p.idx.ravel();data=pixels.tobytes() if eight else (pixels[::2]|(pixels[1::2]<<4)).tobytes()
  if not hasattr(self,'extra_patches'):self.extra_patches=[]
  self.extra_patches.append((off,data))
  mipraw=bytearray(self.raw)
  for patchoff,patchdata in self.extra_patches:mipraw[patchoff:patchoff+len(patchdata)]=patchdata
  self.extra_patches.extend(mip_updates(p.idx,p.orig,p.pal,meta.get('mips',[]),mipraw,eight))
  self.regions.append(dict(box=[0,0,self.im.width,self.im.height],text=text,plane=meta['plane'],plane_box=list(box)))
  Image.fromarray(p.pal[p.idx]).save(W/'audit'/f"plane_ko_{self.id}_{meta['plane']}.png")
 def sideways_text(self,box,text,fg,bg):
  """세로 현수막용으로 UV에 맞춰 각 글립을 반시계 방향으로 저장."""
  x,y,xx,yy=box;self.idx[y:yy,x:xx]=bg
  self.regions.append(dict(box=list(box),text=text))
  cell=min(yy-y,(xx-x)//len(text));start=x+(xx-x-cell*len(text))//2;top=y+(yy-y-cell)//2
  for j,c in enumerate(text):
   left=start+j*cell
   self.text((left,top,left+cell,top+cell),c,size=cell-2,fg=fg,bg=bg,outline=0,inkbox=False,font_path=W.parent/'SeoulHangangEB.ttf')
   self.idx[top:top+cell,left:left+cell]=np.rot90(self.idx[top:top+cell,left:left+cell])
 def rotated_labels(self,labels):
  """시계 방향으로 회전해 그려지는 정사각형 UV의 문구 배치."""
  assert self.im.width==self.im.height
  size=self.im.width;start=len(self.regions)
  self.idx=np.rot90(self.idx,-1).copy();self.orig=np.rot90(self.orig,-1).copy()
  for box,s,kwargs in labels:self.text(box,s,**kwargs)
  self.idx=np.rot90(self.idx).copy();self.orig=np.rot90(self.orig).copy()
  for r in self.regions[start:]:
   x,y,xx,yy=r['box'];r['box']=[y,size-xx,yy,size-x]
 def copy_sprite(self,source,source_box,target_box):
  im=Image.fromarray(source.pal[source.idx]).crop(source_box)
  x,y,xx,yy=target_box;im=im.resize((xx-x,yy-y),Image.Resampling.LANCZOS)
  self.idx[y:yy,x:xx]=cKDTree(self.pal.astype(float)).query(np.asarray(im).reshape(-1,4).astype(float))[1].reshape(yy-y,xx-x)
  self.regions.append(dict(box=list(target_box),text='번역된 동일 소품'))
 def save(self):
  b=bytearray(self.raw)
  if self.g:tim2.set_indices(b,self.g,self.idx.ravel())
  else:
   off=struct.unpack_from('<I',b,10)[0];bits=struct.unpack_from('<H',b,28)[0];stride=((self.im.width*bits+31)//32)*4
   for y,row in enumerate(self.idx[::-1]):
    if bits==8:data=row.tobytes()
    elif bits==4:data=((row[0::2]<<4)|row[1::2]).tobytes()
    else:raise ValueError(bits)
    b[off+y*stride:off+y*stride+len(data)]=data
  if self.g and self.g.get('mti'):
   for offset,data in mip_updates(self.idx,self.orig,self.pal,self.g.get('mips',[]),self.raw,self.g['itype']==5):b[offset:offset+len(data)]=data
  for offset,data in getattr(self,'extra_patches',[]):b[offset:offset+len(data)]=data
  allowed=np.zeros(self.idx.shape,dtype=bool)
  for r in self.regions:
   x,y,xx,yy=r['box'];allowed[y:yy,x:xx]=True
  assert not np.any((self.idx!=self.orig)&~allowed)
  assert len(b)==len(self.raw)
  out=W/'textures_ko';out.mkdir(exist_ok=True)
  (out/f'{self.id:04}.bin').write_bytes(b)
  Image.fromarray(self.pal[self.idx]).save(out/f'{self.id:04}.png')
  return dict(id=self.id,regions=self.regions,source_hash=hashlib.sha256(self.raw).hexdigest(),output_hash=hashlib.sha256(b).hexdigest())
 def compiled_art(self,path,box,text):
  """이미지 생성 도구의 검수된 타이틀을 원본 콘솔 색상표로 변환."""
  im=Image.open(path).convert('RGBA');p=np.array(im);ys,xs=np.where((p[:,:,3]>128)&(p[:,:,:3].max(2)>24))
  im=im.crop((max(0,int(xs.min())-8),max(0,int(ys.min())-8),int(xs.max())+9,int(ys.max())+9))
  x,y,xx,yy=box;im.thumbnail((xx-x,yy-y),Image.Resampling.LANCZOS)
  canvas=Image.new('RGBA',self.im.size);canvas.alpha_composite(im,(x+(xx-x-im.width)//2,y+(yy-y-im.height)//2))
  a=np.array(canvas).astype(float).reshape(-1,4);p=self.pal.astype(float)
  a[:,:3]*=a[:,3:4]/255;p[:,:3]*=p[:,3:4]/255;a[:,3]*=1.4;p[:,3]*=1.4
  self.idx[:]=cKDTree(p).query(a)[1].reshape(self.idx.shape)
  self.regions=[dict(box=[0,0,self.im.width,self.im.height],text=text)]
 def erase_ink(self,box):
  """상자에 걸친 원본 글자 덩어리를 상자 밖 테두리까지 투명색으로 지운다."""
  from scipy import ndimage
  bg=int(np.argmin(self.pal[:,3]));ink=self.pal[self.orig][:,:,3]>0
  lab,_=ndimage.label(ink,structure=np.ones((3,3)))
  x,y,xx,yy=box;ids=set(np.unique(lab[y:yy,x:xx]))-{0}
  m=np.isin(lab,list(ids))
  if not m.any():return
  self.idx[m]=bg;ys,xs=np.where(m)
  self.regions.append(dict(box=[int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1],text='원본 글자 잔상 제거'))
 def clear_panel(self,box):
  x,y,xx,yy=box;p=self.pal[self.idx].astype(float)
  left=p[y:yy,max(0,x-4):x].mean(1);right=p[y:yy,xx:min(self.im.width,xx+4)].mean(1)
  a=np.linspace(0,1,xx-x)[None,:,None];pix=left[:,None,:]*(1-a)+right[:,None,:]*a
  self.idx[y:yy,x:xx]=cKDTree(self.pal.astype(float)).query(pix.reshape(-1,4))[1].reshape(yy-y,xx-x)
  self.regions.append(dict(box=list(box),text='배경 복원'))
