import cv2,json,subprocess,hashlib,sys
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
out=Path(sys.argv[1]);p=out/'COMMERCE-T1-sans-voix.mp4';m=json.loads((out/'manifest.json').read_text());info=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p)]));s,=info['streams'];assert (s['codec_name'],s['width'],s['height'],s['avg_frame_rate'],s['nb_read_frames'],s['pix_fmt'])==('h264',720,1280,'30/1','900','yuv420p');assert float(info['format']['duration'])==30;assert hashlib.sha256(p.read_bytes()).hexdigest()==m['sha256'];assert len(m['inputs'])==4 and len(set(m['inputs'].values()))==4;assert list(m['effets'])==list('ABCDEFGH');cap=cv2.VideoCapture(str(p));times=[.54,1.95,4.7,5.98,8,10.26,12,14.2,16,17.6,19,21.58,24,27.7,29.65];sheet=Image.new('RGB',(5*155,3*289),'#192b29');draw=ImageDraw.Draw(sheet)
def at(t):
 cap.set(1,int(round(t*30)));ok,a=cap.read();assert ok;return a
for j,t in enumerate(times):
 a=at(t);img=Image.fromarray(cv2.cvtColor(a,cv2.COLOR_BGR2RGB)).resize((150,266));x=j%5*155;y=j//5*289;sheet.paste(img,(x,y));draw.text((x+3,y+268),f'{t:.2f} s',fill='white')
sheet.save(out/'planche-QC.jpg',quality=90)
root=Path(__file__).resolve().parents[1]; caps={}; records=[];planes={};
contract=json.loads((root/'montage/contrat-candidat.json').read_text()); target=np.array(contract['typographie']['encre_rgb'][::-1]);
for key,rec in m['temoins_plein_cadre'].items():
 idx=int(key);i=rec['clip'];actual=at(idx/30);
 if i not in caps:caps[i]=cv2.VideoCapture(str(root/'fixtures/rushs'/f'S{i}.mp4'))
 c0=caps[i];c0.set(1,rec['source_frame']);ok,raw=c0.read();assert ok;M=np.float64(rec['matrix']);expected=cv2.warpAffine(raw,M,(720,1280),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE);glyph=cv2.imread(str(out/f'lettres-{idx:03}.png'),0);ids=[g['id'] for g in contract['calques'] if g['images'][0]<=idx<g['images'][1]];assert m['horloge_temoin'][key]==ids and bool(glyph.any())==bool(ids);ink=cv2.erode(glyph,np.ones((3,3),np.uint8))>253;outside=cv2.dilate(glyph,np.ones((35,35),np.uint8))==0;err=np.abs(actual.astype('int16')-expected.astype('int16')).mean(axis=2);err_bg=float(err[outside].mean());err_bottom=float(err[-144:][outside[-144:]].mean());assert err_bg<6.0 and err_bottom<6.0,(idx,err_bg,err_bottom);white=float((np.abs(actual[ink]-target).max(axis=1)<27).mean()) if ink.any() else None
 if white is not None: assert white>.90,(idx,white)
 records.append({'image':idx,'calques':ids,'scene':i,'ecart_moyen_hors_lettres':round(err_bg,2),'ecart_bas_vs_rush':round(err_bottom,2),'fraction_encre_ivoire':white})
assert len(records)==15 and all(any(g['id'] in r['calques'] and r['fraction_encre_ivoire'] is not None for r in records) for g in contract['calques']);assert all(np.std(at(t))>18 for t in [2,8,16,25]);(out/'controle.json').write_text(json.dumps(dict(resultat='PASS',dimensions=[720,1280],fps=30,images_decodees=900,duree_s=30,pistes_audio=0,sha256=m['sha256'],effets=m['effets'],controle_image=records,observations='Quinze images hors transition confrontées aux pixels des rushs recadrés, y compris les 144 dernières lignes ; contrôle de la présence chronométrée et de l’ivoire des lettres. Ces vérifications ne valent pas validation du style ou des raccords.'),ensure_ascii=False,indent=2))

j=json.loads((out/'render-job.json').read_text());d=j['merchant_payload'];prix=f"{d['prix']:,} F CFA".replace(',',' ');assert m['textes_affiches']==[[d['nom'],d['produit']],[d['accroche'],prix],[],[d['nom'],d['quartier'],'Écris-nous sur WhatsApp',d['whatsapp']]];assert m['inputs']=={v['uri']:v['sha256'] for v in j['captures'].values()};print('PASS — entrées du RenderJob du navigateur reliées aux rushs et aux textes du MP4 contrôlé.')

# Porte d'audition : comparer les 4 musiques uniquement pour la démo dont provient cette voix.
# Préserve le master silencieux contrôlé ci-dessus ; tous les fichiers musicaux sont des variantes séparées.
if j['merchant_payload']==json.loads((root/'fixtures/rushs/formulaire.json').read_text()) and (root/'audio/auditions/voix-demo.flac').exists():
 subprocess.run([sys.executable,str(root/'audio/auditions/mixer.py'),str(p),str(out/'ecoutes')],check=True)
