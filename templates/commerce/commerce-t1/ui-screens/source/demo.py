"""Generate original, illustrative capture fixtures, not an advertising render. Usage: FFMPEG=... python demo.py DIR"""
import numpy as np,math,os,sys,subprocess
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
out=Path(sys.argv[1]);out.mkdir(exist_ok=True,parents=True); F=os.environ.get('FFMPEG','ffmpeg');font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',19)
for i,secs in enumerate([8,10,9,11],1):
 w,h=360,540;y,x=np.mgrid[:h,:w];v=np.clip((x/360*.42+y/540*.4),0,1)[:,:,None];colors=[([252,207,153],[211,119,95]),([217,237,225],[114,173,162]),([255,221,157],[229,162,98]),([199,225,233],[121,171,183])][i-1];base=Image.fromarray(np.uint8(np.array(colors[0])*(1-v)+np.array(colors[1])*v));d=ImageDraw.Draw(base);d.ellipse((150,-70,490,280),fill=tuple(colors[0]));d.polygon([(0,383),(360,345),(360,540),(0,540)],fill='#b66a50' if i!=4 else '#567e80');d.polygon([(0,391),(360,353),(360,359),(0,399)],fill='#d49776');
 if i==4:d.rounded_rectangle((15,163,130,202),8,fill='#36686b');d.text((25,169),'BOUTIQUE',font=font,fill='white')
 proc=subprocess.Popen([F,'-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','360x540','-r','12','-i','-','-f','lavfi','-i','sine=frequency=220:sample_rate=24000','-af','volume=0.055','-t',str(secs),'-c:v','libvpx-vp9','-deadline','realtime','-cpu-used','8','-crf','37','-b:v','0','-c:a','libopus','-b:a','12k',str(out/f'{i}.webm')],stdin=subprocess.PIPE)
 for j in range(secs*12):
  im=base.copy();d=ImageDraw.Draw(im);u=min(1,max(0,(j/12-2)/2)) if i==3 else .3;dx=round(19*u);dy=round(15*u);d.ellipse((75,365,286,392),fill='#865d50');d.ellipse((100,360,220,382),fill='#293e40');d.ellipse((100,354,220,376),fill='#466366');d.line([(156,359),(122,262),(204,203)],fill='#213d41',width=11);d.line([(161,357),(131,265),(205,212)],fill='#71888a',width=4);d.ellipse((113,253,133,273),fill='#293e40',outline='#98a7a3',width=3);d.ellipse((195,195,212,212),fill='#263d40');d.polygon([(198,207),(213,193),(249+dx,208+dy),(211+dx,249+dy)],fill='#176464');d.polygon([(204,204),(212,198),(241+dx,210+dy),(226+dx,225+dy)],fill='#428987');d.line((211+dx,249+dy,249+dx,208+dy),fill='#fff0aa',width=5)
  if i==3 and j/12<5.5: d.line([(360,280),(289,231+dy),(253+dx,218+dy)],fill='#884e36',width=22);d.ellipse((246+dx,207+dy,269+dx,227+dy),fill='#a86e4e')
  if i==2:im=im.crop((92,137,280,419)).resize((360,540),Image.Resampling.LANCZOS)
  if j==0:im.save(out/f'{i}.jpg',quality=88)
  proc.stdin.write(im.tobytes())
 proc.stdin.close();assert proc.wait()==0
from PIL import ImageOps,ImageFilter
for i in range(1,5):
 im=Image.open(out/f'{i}.jpg');crop=im.crop((0,134,360,418) if i!=2 else (20,55,335,365));bg=ImageOps.fit(crop,(790,244)).filter(ImageFilter.GaussianBlur(16));fg=ImageOps.contain(crop,(790,244));bg.paste(fg,((790-fg.width)//2,0));bg.save(out/f'guide{i}.jpg',quality=88)
