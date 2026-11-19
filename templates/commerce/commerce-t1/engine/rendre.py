"""Render four validated clips. Usage: python engine/rendre.py JOB-DIRECTORY OUTPUT-DIRECTORY."""
import cv2,numpy as np,json,hashlib,sys,math,subprocess,textwrap
from PIL import Image,ImageDraw,ImageFont
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
def read(i,t):
 s=sc[i];n=round((s['source_s'][0]+t-s['sortie_s'][0])*F);n=int(np.clip(n,0,s['capture_s']*F-1));source_used[s['id']].add(n);cap=caps[i];old,a=cache.get(i,(-1000,None));
 if n!=old:
  if n!=old+1:cap.set(1,n)
  ok,a=cap.read();assert ok;cache[i]=(n,a)
 return a
def view(i,t,z=1,pan=0):
 a=read(i,t);hh,ww=a.shape[:2];wide=min(ww,hh*W/H)/z;high=wide*H/W;x=(ww-wide)/2;y=(hh-high)*(.5+pan);
 # Protéger la tasse et les mains dans les rushs horizontaux. Le plan reste animé, pas de photographie.
 if ww>hh:
  top,ph=([196,710],[132,785],[130,910],[94,625])[i];ratio=W/ph;sw=int(min(ww,hh*ratio)/z);sh=int(sw/ratio);focus=[.51,.54,.51,.53][i];sx=int(np.clip(ww*focus-sw/2,0,ww-sw));sy=(hh-sh)//2;shot=cv2.resize(a[sy:sy+sh,sx:sx+sw],(W,ph));bg=cv2.resize(cv2.GaussianBlur(cv2.resize(a,(36,64)),(13,13),0),(W,H));bg=cv2.addWeighted(bg,.43,np.full_like(bg,(32,40,36)),.57,0);bg[top:top+ph]=shot;cv2.line(bg,(0,top+ph),(W,top+ph),(139,191,180),2);return bg
 return cv2.resize(a[round(y):max(round(y)+1,round(y+high)),round(x):max(round(x)+1,round(x+wide))],(W,H),interpolation=cv2.INTER_LINEAR)
def mat(a,b,m):return cv2.blendLinear(a,b,np.ascontiguousarray(1-m,dtype='float32'),np.ascontiguousarray(m,dtype='float32'))
def fade(a,b,q):return cv2.addWeighted(a,1-q,b,q,0)
def circle(a,t,r=66):
 for k in range(14):
  v=k*math.pi/7+t*.8;cx,cy=W//2,H//2;cv2.line(a,(round(cx+r*math.cos(v)),round(cy+r*math.sin(v))),(round(cx+(r+5+(k%3)*3)*math.cos(v)),round(cy+(r+5+(k%3)*3)*math.sin(v))),(198,247,230),3,cv2.LINE_AA)
def scene(i,t,stage):
 z=[1.02,1.02,1.01,1.0][i]+[.09,.16,.10,0][i]*stage;pic=view(i,t,z,.04 if i==2 else 0)
 if i==0 and stage: # seven graphic tableaux from four sources; alternating graphic treatment
  # split colour surrounds at the edges, keep the product in the middle untouched
  pts=np.int32([(0,0),(round(W*.54),0),(0,round(H*.28))]);cv2.fillPoly(pic,[pts],(96,58,195),cv2.LINE_AA);cv2.line(pic,(0,round(H*.28)),(round(W*.54),0),(157,231,255),5,cv2.LINE_AA)
 return pic
def stage(i,t):return int(i<3 and t>=effects[['B','D','F'][i]][1])
# Pre-render the commercial text only, separate from the reference effects and on-screen guide.
ft=lambda size,b:ImageFont.truetype(str(root/'assets/fonts'/('DejaVuSans-Bold.ttf' if b else 'DejaVuSans.ttf')),size)
def label(i):
 img=Image.new('RGBA',(W,H));d=ImageDraw.Draw(img);fcolor='#fcf5db';ink='#173a37';lime='#ddfa71';left=52;right=W-52
 def text(x,y,msg,size,b=0,col=fcolor):
  while size>20 and d.textlength(msg,font=ft(size,b))>right-x-12:size-=1
  if d.textlength(msg,font=ft(size,b))>right-x-12:raise ValueError('Texte trop long pour la zone sûre')
  d.text((x,y),msg,font=ft(size,b),fill=col,anchor='lt')
 if i in (0,1):
  d.rounded_rectangle((left,948,right,1128),radius=22,fill=ink);d.rectangle((left+26,980,left+75,986),fill=lime);d.ellipse((left+86,978,left+96,988),fill='#87bbaa');text(left+26,1023,texts[i][0],61 if i==0 else 55,1 if i==0 else 0)
 if i==3:
  d.rounded_rectangle((left,752,right,1149),radius=26,fill=ink);d.rectangle((left+30,786,left+92,792),fill=lime);text(left+29,824,texts[i][0],72,1,lime);text(left+30,920,texts[i][1],34,0);d.line((left+30,981,right-30,981),fill='#68968c',width=2);text(left+30,1005,texts[i][2],30,0);text(left+30,1062,texts[i][3],43,0)
 ar=np.asarray(img);return cv2.cvtColor(ar[:,:,:3],cv2.COLOR_RGB2BGR),np.ascontiguousarray(ar[:,:,3].astype('float32')/255)
labels=[label(i) for i in range(4)];
def compose(t):
 i=next(s for s in range(4) if t<sc[s]['sortie_s'][1]);key=next((k for k,(a,b) in effects.items() if a<=t<b),None)
 if not key:v=scene(i,t,stage(i,t))
 else:
  lo,hi=effects[key];p=(t-lo)/(hi-lo);q=ease(p);events[key].append(round(t*F));
  if key in 'AH':
   a=scene(0 if key=='A' else 3,t,0);b=black.copy();circle(b,t,56+int(16*q));openq=ease((p-.06)/.79) if key=='A' else 1-ease(p/.9);lines=(nx+ny*.68)*8-bands;mask=np.clip((openq*1.2-lines-(bands%3)*.07)*70,0,1);v=mat(b,a,mask) if 0<openq<1 else (a if openq>=1 else b);v=fade(v,black,sat((p-.76)/.24)) if key=='H' else fade(v,accent,.10*math.exp(-((p-.87)/.045)**2))
  elif key=='B':
   v=fade(scene(0,t,0),scene(0,t,1),q);wave=np.exp(-((rad-p*.85)/.095)**2)*math.sin(p*math.pi)*.82;v=mat(v,accent,wave.astype('float32'))
  elif key=='C':
   m=np.clip((q*1.08-diag-edge)*90,0,1);v=mat(scene(0,t,1),scene(1,t,0),m);curl=np.clip(1-abs(q*1.08-diag-edge)/.035,0,1)*math.sin(p*math.pi);v=mat(v,np.full_like(v,(214,238,255)),curl.astype('float32'))
  elif key=='D':
   v=view(1,t,1.02+.16*q+.12*math.sin(p*math.pi));v=fade(v,np.full_like(v,(214,238,252)),.63*math.sin(math.pi*p)**2)
  elif key=='E':
   m=np.clip((q*.56-abs(ny-.50-edge*1.8))*100,0,1);v=mat(scene(1,t,1),scene(2,t,0),m);v=fade(v,accent,.24*math.exp(-((p-.1)/.08)**2))
  elif key=='F':
   v=scene(2,t,0);halfW=.51*q;halfH=.10*ease(p/.25)+.41*q;dist=np.maximum(abs(nx-.5)-halfW,abs(ny-.48)-halfH);m=np.clip(-dist*150,0,1);v=mat(v,scene(2,t,1),m);border=np.clip(1-abs(dist)*200,0,1)*math.sin(p*math.pi);v=mat(v,accent,border.astype('float32'))
  elif key=='G':
   a=fade(scene(2,t,1),black,.48*ease(p/.48));b=view(3,t,1+.38*(1-q));m=np.clip((q*1.08-(.72*nx+.28*(1-ny)))*90,0,1);v=mat(a,b,m)
 # Keep text independent of graphic effects. CTA fully stable after 22.3 seconds.
 alpha=0
 if i==0:alpha=ease((t-1.38)/.32)*ease((5.80-t)/.25)
 if i==1:alpha=ease((t-6.25)/.25)*ease((13.75-t)/.24)
 if i==3:alpha=ease((t-22.20)/.10)*ease((29.30-t)/.00001) if t<29.30 else 0
 if alpha>0:v=mat(v,labels[i][0],labels[i][1]*alpha)
 return v
mp=out/'COMMERCE-T1-sans-voix.mp4';proc=subprocess.Popen(['ffmpeg','-loglevel','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(F),'-i','-','-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(mp)],stdin=subprocess.PIPE)
for frame in range(N):proc.stdin.write(compose(frame/F).tobytes())
proc.stdin.close();assert proc.wait()==0
for cap in caps:cap.release()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();report={'sha256':sha(mp),'contrat_sha256':sha(root/'montage/contrat-candidat.json'),'inputs':{p.name:sha(p) for p in files},'textes_resolus':texts,'polices':c['polices'],'effets':{k:{'premiere_image':min(v),'derniere_image':max(v),'images':len(v)} for k,v in events.items()},'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()};(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
