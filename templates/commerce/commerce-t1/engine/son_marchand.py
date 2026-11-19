"""Audio pour un vrai job local : jamais de voix ou de texte de la démo dans ce chemin."""
import subprocess,sys,json,hashlib
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'audio/auditions'))
from mixer import R,F,db,decode,level,vh

def produire(video,src,out,cache,piste,contrat):
 from jsonschema import validate
 root=Path(__file__).resolve().parents[1];sources=json.loads((root/'audio/auditions/sources.json').read_text());meta=next(x for x in sources if x['id']==piste);p=Path(cache)/f'{piste}.mp3'
 if hashlib.sha256(p.read_bytes()).hexdigest()!=meta['sha256']:raise ValueError('Mauvaise source musicale')
 # Le profil marchand n'utilise pas les longs rushs recoupés de la démonstration.
 if (src/'decoupe-v2.json').exists():raise ValueError('Découpe démo non applicable au profil marchand')
 m=decode(p);i=round(meta['source_debut_s']*R);m=m[i:i+30*R].copy();v=np.zeros_like(m);t=np.arange(len(v))/R;env=np.zeros(len(v));assert m.shape==(30*R,2)
 for sc in contrat['scenes']:
  source=src/(sc['id']+'.mp4');streams=subprocess.check_output(['ffprobe','-v','error','-select_streams','a:0','-show_entries','stream=index','-of','csv=p=0',str(source)],text=True).strip()
  if streams:
   a=decode(source);start,end=sc['sortie_s'];offset=sc['source_s'][0]*R;audio=a[offset:offset+(end-start)*R];v[start*R:start*R+len(audio)]=audio
 # Détection d'activité par blocs, pas de reconnaissance de langue ; silences longs laissés à la musique.
 energy=np.sqrt(np.mean(v.reshape(-1,480,2)**2,axis=(1,2)));idx=np.flatnonzero(energy>.005)
 if len(idx):
  for block in np.split(idx,np.flatnonzero(np.diff(idx)>48)+1):env=np.maximum(env,np.minimum(np.clip((t-block[0]/100+.12)/.12,0,1),np.clip(((block[-1]+1)/100+.45-t)/.45,0,1)))
  vol,_=level(v)
  if np.isfinite(vol):v*=db(-20-vol)
 m*=db(-18-level(m)[0]);m*=db(-3-7*env[:,None]);m*=np.minimum(np.clip(t/.025,0,1),np.clip((30-t)/.35,0,1))[:,None];x=m+v;x*=db(-16-level(x)[0]);peak=np.max(abs(x),axis=1,keepdims=True);x*=np.minimum(1,db(-2.7)/np.maximum(peak,1e-12));path=out/'COMMERCE-T1-musique.mp4'
 subprocess.run([F,'-v','error','-y','-i',str(video),'-f','f32le','-ar',str(R),'-ac','2','-i','-','-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',str(path)],input=np.asarray(x,'<f4').tobytes(),check=True);a=decode(path);li,tp=level(a)
 if vh(video)!=vh(path) or abs(len(a)/R-30)>.025 or not np.isfinite(a).all() or abs(li+16)>.75 or tp>-1:raise ValueError('CQ audio marchand refusé')
 (out/'mix-marchand.json').write_text(json.dumps(dict(music_id=piste,source_voice='captures',vitesse=1,active_blocks=len(idx),aac_lufs=li,aac_dbtp=tp),indent=2));return path
