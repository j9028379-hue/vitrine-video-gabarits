import cv2,json,subprocess,hashlib,sys
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
out=Path(sys.argv[1]);p=out/'COMMERCE-T1-sans-voix.mp4';m=json.loads((out/'manifest.json').read_text());info=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p)]));s,=info['streams'];assert (s['codec_name'],s['width'],s['height'],s['avg_frame_rate'],s['nb_read_frames'],s['pix_fmt'])==('h264',720,1280,'30/1','900','yuv420p');assert float(info['format']['duration'])==30;assert hashlib.sha256(p.read_bytes()).hexdigest()==m['sha256'];assert len(m['inputs'])==4 and len(set(m['inputs'].values()))==4;assert list(m['effets'])==list('ABCDEFGH');cap=cv2.VideoCapture(str(p));times=[.54,1.8,3.05,5.98,7.2,10.26,12,14.2,16,17.6,19,21.58,24,28.9,29.65];sheet=Image.new('RGB',(5*155,3*289),'#192b29');draw=ImageDraw.Draw(sheet)
def at(t):
 cap.set(1,int(round(t*30)));ok,a=cap.read();assert ok;return a
for j,t in enumerate(times):
 a=at(t);img=Image.fromarray(cv2.cvtColor(a,cv2.COLOR_BGR2RGB)).resize((150,266));x=j%5*155;y=j//5*289;sheet.paste(img,(x,y));draw.text((x+3,y+268),f'{t:.2f} s',fill='white')
sheet.save(out/'planche-QC.jpg',quality=90)
root=Path(__file__).resolve().parents[1]; caps={}; records=[];planes={};
for s in (1,2,4): planes[s]=cv2.imread(str(out/f'masque-lettres-S{s}.png'),cv2.IMREAD_GRAYSCALE)
for key,rec in m['temoins_plein_cadre'].items():
 idx=int(key);i=rec['clip'];actual=at(idx/30);c0=caps.setdefault(i,cv2.VideoCapture(str(root/'fixtures/rushs'/f'S{i}.mp4')));c0.set(1,rec['source_frame']);ok,raw=c0.read();assert ok;M=np.float64(rec['matrix']);expected=cv2.warpAffine(raw,M,(720,1280),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE);glyph=planes.get(i,np.zeros((1280,720),np.uint8));ink=glyph>253;outside=cv2.dilate(glyph,np.ones((35,35),np.uint8))==0;err=np.abs(actual.astype('int16')-expected.astype('int16')).mean(axis=2);err_bg=float(err[outside].mean());err_bottom=float(err[-144:][outside[-144:]].mean());assert err_bg<6.0 and err_bottom<6.0,(idx,err_bg,err_bottom);white=float((actual[ink].min(axis=1)>237).mean()) if ink.any() else None
 if white is not None: assert white>.90,(idx,white)
 records.append({'image':idx,'scene':i,'ecart_moyen_hors_lettres':round(err_bg,2),'ecart_bas_vs_rush':round(err_bottom,2),'fraction_lettres_blanches':white})
assert len(records)==8;assert all(np.std(at(t))>18 for t in [2,8,16,25]);(out/'controle.json').write_text(json.dumps(dict(resultat='PASS',dimensions=[720,1280],fps=30,images_decodees=900,duree_s=30,pistes_audio=0,sha256=m['sha256'],effets=m['effets'],controle_image=records,observations='Huit images hors transition confrontées aux pixels des rushs recadrés, y compris les 144 dernières lignes ; contrôle du blanc des lettres. Ces vérifications ne valent pas validation du style ou des raccords.'),ensure_ascii=False,indent=2))
