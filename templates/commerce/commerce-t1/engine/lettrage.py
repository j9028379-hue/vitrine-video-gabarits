"""Rendu des seuls glyphes : un calque ajusté par réponse et une horloge par geste."""
from pathlib import Path
from functools import lru_cache
import math,cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
@lru_cache(256)
def font(path,size):return ImageFont.truetype(str(path),size)
def ease(x):x=min(1,max(0,x));return 1-(1-x)**3
def stamp(root,g,c,msg):
 path=root/'assets/fonts'/c['typographie'][g['police']]
 if g['id']=='offre':
  ft=font(path,g['taille_px']);missing=bytes(ft.getmask('\U0010ffff'))
  if any(bytes(ft.getmask(ch))==missing for ch in set(msg) if not ch.isspace()):path=root/'assets/fonts/DejaVuSans.ttf'
 else:msg=' '.join(msg.split())
 limit=g['largeur_max'];words=msg.split();opts=[[msg]]+([[' '.join(words[:k]),' '.join(words[k:])] for k in range(1,len(words))] if g['id']!='offre' else []);
 # Accepte aussi une réponse longue sans espace, sans perdre de caractères.
 if len(words)==1 and len(msg)>16 and g['id'] not in ('numero','offre'):opts.append([msg[:len(msg)//2],msg[len(msg)//2:]])
 for size in range(g['taille_px'],13,-1):
  ft=font(path,size);options=[]
  for lines in opts:
   boxes=[ft.getbbox(l) for l in lines];widths=[b[2]-b[0] for b in boxes];height=sum(b[3]-b[1] for b in boxes)+(len(lines)-1)*10
   if max(widths)<=limit and height<=132:options.append((len(lines),max(widths)-min(widths),lines,boxes,height))
  if options:break
 else:raise ValueError('Réponse hors zone : '+g['id'])
 _,_,lines,boxes,h=min(options);w=max(b[2]-b[0] for b in boxes);im=Image.new('L',(w+24,h+24));d=ImageDraw.Draw(im);y=12
 for l,b in zip(lines,boxes):d.text(((im.width-b[2]+b[0])//2-b[0],y-b[1]),l,font=ft,fill=255);y+=b[3]-b[1]+10
 return np.array(im),{'lignes':lines,'police_effective':path.name,'taille_px':size,'rectangle':[g['centre'][0]-im.width//2,g['centre'][1]-im.height//2,im.width,im.height]}
def paint(frame,n,items,c,save=False):
 mask=np.zeros(frame.shape[:2],np.uint8) if save else None;ids=[]
 for g,base,meta in items:
  a,b=g['images'];
  if not a<=n<b:continue
  ids.append(g['id']);p=ease((n-a+1)/g['entree']);q=min(1,(b-n)/g['sortie']);h,w=base.shape;kind=g['mouvement'];glyph=base
  if kind in ('plume','vague') and p<1:
   yy,xx=np.ogrid[:h,:w];edge=p*(w+40)-20+(yy/h-.5)*(23 if kind=='plume' else -42);glyph=np.uint8(base*np.clip((edge-xx)/8,0,1))
  dx=round(-14*(1-p)) if kind=='vague' else 0;dy=round(28*(1-p)) if kind=='lever' else 0;x,y,_,_=meta['rectangle'];x+=dx;y+=dy;crop=frame[y:y+h,x:x+w];alpha=glyph.astype(np.float32)/255*q*(p if kind=='lever' else 1);rim=cv2.dilate(alpha,np.ones((3,3),np.uint8));shadow=np.roll(cv2.GaussianBlur(rim,(0,0),1.45),(4,2),axis=(0,1));tone=c['typographie'];ink=np.float32(tone['encre_rgb'][::-1]);dark=np.float32(tone['relief_rgb'][::-1]);r=np.maximum(shadow*.92,rim*.83)[:,:,None];under=crop*(1-r)+dark*r;crop[:]=under*(1-alpha[:,:,None])+ink*alpha[:,:,None];
  if save:mask[y:y+h,x:x+w]=np.maximum(mask[y:y+h,x:x+w],np.uint8(alpha*255))
 return mask,ids
