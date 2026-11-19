import cv2,json,subprocess,hashlib,sys
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
out=Path(sys.argv[1]);p=out/'COMMERCE-T1-sans-voix.mp4';m=json.loads((out/'manifest.json').read_text());info=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p)]));s,=info['streams'];assert (s['codec_name'],s['width'],s['height'],s['avg_frame_rate'],s['nb_read_frames'],s['pix_fmt'])==('h264',720,1280,'30/1','900','yuv420p');assert float(info['format']['duration'])==30;assert hashlib.sha256(p.read_bytes()).hexdigest()==m['sha256'];assert len(m['inputs'])==4 and len(set(m['inputs'].values()))==4;assert list(m['effets'])==list('ABCDEFGH');cap=cv2.VideoCapture(str(p));times=[.54,1.8,3.05,5.98,7.2,10.26,12,14.2,16,17.6,19,21.58,24,28.9,29.65];sheet=Image.new('RGB',(5*155,3*289),'#192b29');draw=ImageDraw.Draw(sheet)
def at(t):
 cap.set(1,int(round(t*30)));ok,a=cap.read();assert ok;return a
for j,t in enumerate(times):
 a=at(t);img=Image.fromarray(cv2.cvtColor(a,cv2.COLOR_BGR2RGB)).resize((150,266));x=j%5*155;y=j//5*289;sheet.paste(img,(x,y));draw.text((x+3,y+268),f'{t:.2f} s',fill='white')
sheet.save(out/'planche-QC.jpg',quality=90);a,b=at(23),at(28);diff=float(np.abs(a[790:1110,100:600].astype('int16')-b[790:1110,100:600]).mean());assert diff<2;assert any(np.std(at(t))>18 for t in [2,8,16,25]);(out/'controle.json').write_text(json.dumps(dict(resultat='PASS',dimensions=[720,1280],fps=30,images_decodees=900,duree_s=30,pistes_audio=0,sha256=m['sha256'],effets=m['effets'],difference_moyenne_zone_CTA_23_28=diff,observations='Vérifications techniques ; appréciation créative réservée au propriétaire.'),ensure_ascii=False,indent=2))
