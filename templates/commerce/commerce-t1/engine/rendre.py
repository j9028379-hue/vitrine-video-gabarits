"""Render four validated clips. Usage: python engine/rendre.py JOB-DIRECTORY OUTPUT-DIRECTORY."""
import cv2,numpy as np,json,hashlib,sys,math,subprocess,textwrap
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from pathlib import Path
from jsonschema import validate
root=Path(__file__).resolve().parents[1];job=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(exist_ok=True,parents=True);cv2.setNumThreads(1)
def load(p):return json.loads(p.read_text())
c=load(root/'montage/contrat-candidat.json');spec=load(root/'engine/format.json');form=load(job/'formulaire.json');validate(form,load(root/c['formulaire']['schema']));assets=load(job/'prises.json');sc=c['scenes'];assert set(assets)==set(x['prise'] for x in sc);W,H,F,N=[spec[k] for k in ('width','height','fps','frames')];assert N==F*c['duree_s'];caps=[];cache={};files=[]
for s in sc:
 p=job/assets[s['prise']];cap=cv2.VideoCapture(str(p));assert cap.isOpened() and abs(cap.get(5)-F)<.001 and cap.get(7)>=s['capture_s']*F,(s['id'],p);caps.append(cap);files.append(p)
for name,h in c['polices'].items():assert hashlib.sha256((root/'assets/fonts'/name).read_bytes()).hexdigest()==h
class FC(int):
 def __format__(self,key):return f'{int(self):,} F CFA'.replace(',',' ') if key=='fcfa' else super().__format__(key)
values={**form,'prix':FC(form['prix'])};texts=[[s.format_map(values) for s in item['textes']] for item in sc];effects={e['motif']:e['sortie_s'] for e in c['effets']};Y,X=np.mgrid[0:H,0:W].astype('float32');nx=X/W;ny=Y/H;diag=.62*nx+.38*ny;bands=np.floor((nx+ny*.68)*8);rad=((nx-.5)**2+(ny-.46)**2)**.5;edge=(np.sin(X*.027)*5+np.sin(X*.107)*2+np.sin(X*.37))/H;black=np.full((H,W,3),(22,26,19),np.uint8);accent=np.full_like(black,(117,244,219));source_used={s['id']:set() for s in sc};events={k:[] for k in effects}
def sat(x):return min(1,max(0,x))
def ease(x):x=sat(x);return x*x*(3-2*x)
# Four moving clips, seven editorial beats. No stills, matte, or background duplication.
edl={ (o['scene']-1,o['tableau']):o for o in load(job/'decoupe-v2.json') } if (job/'decoupe-v2.json').exists() else {}
trace={};
def timed(i,t,k):
 s=sc[i];default=dict(repere_montage=s['sortie_s'][0],repere_rush=s['source_s'][0],cx=.5,cy=.5,zoom_debut=1.,zoom_fin=1.05,angle_debut=0.,angle_fin=0.);o=edl.get((i,k),default);dur=s['kept'] if 'kept' in s else s['sortie_s'][1]-s['sortie_s'][0];w=ease((t-o['repere_montage'])/(dur if i==3 else dur*.55));n=round((o['repere_rush']+t-o['repere_montage'])*F);assert 0<=n<int(caps[i].get(7)),(i,k,t,n);old,a=cache.get((i,k),(-100,None));cap=caps[i];
 if old!=n:
  if int(cap.get(1))!=n:cap.set(1,n)
  ok,a=cap.read();assert ok;cache[(i,k)]=(n,a)
 return o,w,n,a

def view(i,t,k=0,push=0,shift=0,tilt=0):
 o,w,n,a=timed(i,t,k);hh,ww=a.shape[:2];ang=(1-w)*o['angle_debut']+w*o['angle_fin']+tilt;z=(1-w)*o['zoom_debut']+w*o['zoom_fin']+push;theta=math.radians(ang);co,si=abs(math.cos(theta)),abs(math.sin(theta));scale=max((W*co+H*si)/ww,(H*co+W*si)/hh)*max(1.003,z);hx=(W*co+H*si)/scale/2;hy=(H*co+W*si)/scale/2;cx=float(np.clip(ww*(o['cx']+shift),hx,ww-hx));cy=float(np.clip(hh*o['cy'],hy,hh-hy));M=cv2.getRotationMatrix2D((cx,cy),ang,scale);M[:,2]+=[W/2-cx,H/2-cy];v=cv2.warpAffine(a,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE);source_used[sc[i]['id']].add(n)
 if round(t*F) in (64,147,237,356,476,581,721,845):trace[str(round(t*F))]=dict(clip=i+1,source_frame=n,matrix=M.tolist())
 return v
def mat(a,b,m):return cv2.blendLinear(a,b,np.ascontiguousarray(1-m,dtype='float32'),np.ascontiguousarray(m,dtype='float32'))
def fade(a,b,q):return cv2.addWeighted(a,1-q,b,q,0)
def circle(a,t,r=66):
 for k in range(14):
  v=k*math.pi/7+t*.8;cx,cy=W//2,H//2;cv2.line(a,(round(cx+r*math.cos(v)),round(cy+r*math.sin(v))),(round(cx+(r+5+(k%3)*3)*math.cos(v)),round(cy+(r+5+(k%3)*3)*math.sin(v))),(198,247,230),3,cv2.LINE_AA)
def scene(i,t,stage):return view(i,t,stage)
def stage(i,t):return int(i<3 and t>=effects[['B','D','F'][i]][1])
# Pre-render the commercial text only, separate from the reference effects and on-screen guide.
ft=lambda size:ImageFont.truetype(str(root/'assets/fonts'/'poppins/Poppins-ExtraBold.ttf'),size)
def label(i):
 img=Image.new('L',(W,H));d=ImageDraw.Draw(img)
 def line(x,y,msg,size,maxw):
  while size>18 and d.textlength(msg,font=ft(size))>maxw:size-=1
  assert d.textlength(msg,font=ft(size))<=maxw;d.text((x,y),msg,font=ft(size),fill=255,anchor='lt')
 def wrap(msg,limit=15):
  import textwrap
  return textwrap.wrap(msg,width=limit,break_long_words=False,break_on_hyphens=False)
 msg=[x.upper() for x in texts[i]]
 if i==0:line(46,939,msg[0],108,628)
 if i==1:
  lines=wrap(msg[0],15);y0=96
  for j,l in enumerate(lines):line(44,y0+j*78,l,78,632)
 if i==3:
  line(48,104,msg[0],90,624);line(51,213,msg[1],38,617);line(51,283,msg[2],33,618);line(48,332,msg[3],59,625)
 glyph=np.asarray(img).astype('float32')/255.;shadow=np.asarray(img.filter(ImageFilter.GaussianBlur(4))).astype('float32')/255.;shadow=np.roll(shadow,4,axis=0)*.82;return glyph,shadow
labels=[label(i) for i in range(4)]; white=np.full_like(black,255); dark=np.full_like(black,10)
for idx,(glyph,_) in enumerate(labels):
 if glyph.max()>0:cv2.imwrite(str(out/f'masque-lettres-S{idx+1}.png'),np.uint8(glyph*255))
def compose(t):
 i=next(s for s in range(4) if t<sc[s]['sortie_s'][1]);key=next((k for k,(a,b) in effects.items() if a<=t<b),None)
 if not key:v=scene(i,t,stage(i,t))
 else:
  lo,hi=effects[key];p=(t-lo)/(hi-lo);q=ease(p);events[key].append(round(t*F));
  if key in 'AH':
   a=scene(0 if key=='A' else 3,t,0);b=black.copy();circle(b,t,67+round(8*q));op=ease((p-.10)/.75) if key=='A' else 1-ease(p/.83);wedge=nx*.80+ny*.91;stripe=np.floor(wedge*3.65);phase=wedge*3.65-stripe;gate=np.clip((op*1.27-phase-.052*stripe)*135,0,1);v=mat(b,a,gate) if 0<op<1 else (a if op>=1 else b)
   if key=='H':v=fade(v,black,ease((p-.78)/.22))
   else:v=fade(v,white,.27*math.exp(-((p-.87)/.037)**2))
  elif key=='B':
   # The cup settles: rush from the saucer to a new, tilted crop of its rim. Coloured highlight moves with the rim; no graphic ring.
   a=view(0,t,0,push=.21*q);b=view(0,t,1,push=.22*(1-q),tilt=5*(1-q));v=fade(a,b,ease((p-.31)/.32));strength=math.sin(math.pi*p)**2;dx=round(20*strength);v[:,:,0]=np.roll(v[:,:,0],dx,axis=1);v[:,:,2]=np.roll(v[:,:,2],-dx,axis=1);lum=cv2.cvtColor(v,cv2.COLOR_BGR2GRAY).astype('float32')/255.;hl=np.clip((lum-.24)*1.65,0,1)*strength;glow=cv2.GaussianBlur(v,(0,0),6);glow=cv2.addWeighted(glow,.77,np.full_like(v,(218,112,233)),.53,25);v=mat(v,glow,hl)
  elif key=='C':
   # Oblique paper peels from the centre of the saucer, exposing the next live shot on both sides of the fold.
   a=scene(0,t,1);b=view(1,t,0,push=.08*(1-q));axis=.5*nx+.5*ny-.53;dist=abs(axis)-q*.59+edge*1.8;v=mat(a,b,np.clip(-dist*145,0,1));lip=np.clip(1-abs(dist+.007)/.024,0,1)*math.sin(p*math.pi);v=mat(v,np.full_like(v,(224,235,249)),lip);shade=np.clip(1-abs(dist-.028)/.024,0,1)*math.sin(p*math.pi)*.52;v=mat(v,dark,shade)
  elif key=='D':
   # Push follows the milk stream, bloom cuts to a later stroke, then resolves on the foam.
   a=view(1,t,0,push=.42*q,shift=.055*q);b=view(1,t,1,push=.28*(1-q),shift=-.035*(1-q));v=fade(a,b,ease((p-.37)/.30));v=fade(v,np.full_like(v,(237,248,255)),.73*math.sin(p*math.pi)**3)
  elif key=='E':
   a=scene(1,t,1);b=scene(2,t,0);dist=abs(ny-.55-edge*1.8)-.60*q;v=mat(a,b,np.clip(-dist*160,0,1));rim=np.clip(1-abs(dist)/.014,0,1)*math.sin(p*math.pi);v=mat(v,white,rim);v=fade(v,white,.36*math.exp(-((p-.11)/.045)**2))
  elif key=='F':
   # Actual scaled picture-in-picture: the result from a later take moment grows out of the pour.
   v=scene(2,t,0);incoming=scene(2,t,1);rw=max(1,min(W,round(W*ease((p-.045)/.93))));rh=max(1,min(H,round(H*(.11*ease(p/.17)+.89*ease(p)))));x0=round((W-rw)*.5);y0=round((H-rh)*.56);srcw=max(1,round(W*min(1,rw/max(1,rh)*H/W)));cx=W//2;tile=cv2.resize(incoming[:,cx-srcw//2:cx-srcw//2+srcw],(rw,rh));v[y0:y0+rh,x0:x0+rw]=tile
  elif key=='G':
   a=fade(scene(2,t,1),black,.56*ease(p/.44));b=view(3,t,0,push=.62*(1-q),shift=.035*(1-q),tilt=-14*(1-q));axis=.72*nx+.28*(1-ny);m=np.clip((q*1.035-axis)*98,0,1);v=mat(a,b,m)
 # Keep text independent of graphic effects. CTA fully stable after 22.3 seconds.
 alpha=0
 if i==0:alpha=ease((t-1.38)/.32)*ease((5.80-t)/.25)
 if i==1:alpha=ease((t-6.25)/.25)*ease((13.75-t)/.24)
 if i==3:alpha=ease((t-22.20)/.10)*ease((29.30-t)/.00001) if t<29.30 else 0
 if alpha>0:
  glyph,shadow=labels[i];v=mat(mat(v,dark,shadow*alpha),white,glyph*alpha)
 return v
mp=out/'COMMERCE-T1-sans-voix.mp4';proc=subprocess.Popen(['ffmpeg','-loglevel','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(F),'-i','-','-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(mp)],stdin=subprocess.PIPE)
for frame in range(N):proc.stdin.write(compose(frame/F).tobytes())
proc.stdin.close();assert proc.wait()==0
for cap in caps:cap.release()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();report={'edition':'V2 plein cadre','temoins_plein_cadre':trace,'textes_affiches':[[l.upper() for l in ls] for ls in texts],'sha256':sha(mp),'contrat_sha256':sha(root/'montage/contrat-candidat.json'),'inputs':{p.name:sha(p) for p in files},'textes_resolus':texts,'polices':c['polices'],'effets':{k:{'premiere_image':min(v),'derniere_image':max(v),'images':len(v)} for k,v in events.items()},'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()};(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
