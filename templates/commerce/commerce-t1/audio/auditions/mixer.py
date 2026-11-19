"""Banc d’écoute Commerce : 4 éditions temporaires, jamais d’original musical dans l’artefact."""
from pathlib import Path as P
import sys,os,re,json,hashlib,tempfile,subprocess,math
import numpy as np
D=P(__file__).resolve().parent;R=48000;F=os.environ.get('FFMPEG','ffmpeg');H=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest();I=lambda p:json.loads(P(p).read_text());run=lambda a,**kw:subprocess.run(a,check=True,**kw)
def decode(p):return np.frombuffer(subprocess.check_output([F,'-v','error','-i',str(p),'-map','0:a:0','-ar',str(R),'-ac','2','-f','f32le','-']),'<f4').reshape(-1,2)
def level(x):
 s=run([F,'-hide_banner','-nostats','-f','f32le','-ar',str(R),'-ac','2','-i','-','-af','loudnorm=print_format=json','-f','null','-'],input=np.asarray(x,'<f4').tobytes(),capture_output=True).stderr.decode();j=json.loads(re.findall(r'\{[^{}]+\}',s)[-1]);return float(j['input_i']),float(j['input_tp'])
def db(x):return 10**(x/20)
def vh(p):return subprocess.check_output([F,'-v','error','-i',str(p),'-map','0:v','-c','copy','-f','hash','-hash','sha256','-']).decode().strip()
def main(video,dest):
 dest.mkdir(exist_ok=True,parents=True);orig=vh(video);v=decode(D/'voix-demo.flac');assert v.shape==(30*R,2);N=len(v);vtime=np.arange(N)/R;block=v.reshape(-1,480,2);active=np.sqrt((block**2).mean(axis=(1,2)))>.005;idx=np.flatnonzero(active);ranges=np.split(idx,np.flatnonzero(np.diff(idx)>48)+1);env=np.zeros(N)
 for r in ranges:
  start=r[0]/100;end=(r[-1]+1)/100;env=np.maximum(env,np.minimum(np.clip((vtime-start+.12)/.12,0,1),np.clip((end+.45-vtime)/.45,0,1)))
 envelope=-3-7*env;res=[];voiced=np.repeat(active,480);prefix='COMMERCE-T1';songs=I(D/'sources.json');assert len(songs)==4
 with tempfile.TemporaryDirectory() as tmp:
  for n,t in enumerate(songs,1):
   mid=t['id'];mp=P(tmp)/f'{mid}.mp3'
   if os.environ.get('COMMERCE_MUSIC_CACHE'):mp=P(os.environ['COMMERCE_MUSIC_CACHE'])/f'{mid}.mp3'
   else:run(['curl','--fail','--silent','--show-error','--retry','2','-L',t['source_mp3'],'-o',str(mp)])
   assert H(mp)==t['sha256'];full=decode(mp);start=round(t['source_debut_s']*R);m=full[start:start+N].copy();assert m.shape==v.shape;m*=db(-18-level(m)[0]);m*=db(envelope[:,None]);m*=np.minimum(np.clip(vtime/.025,0,1),np.clip((30-vtime)/.35,0,1))[:,None];balance=10*math.log10(np.mean(v[voiced]**2)/np.mean(m[voiced]**2));
   if balance<4:m*=db(balance-4);balance=4
   x=v+m;li,tp=level(x);x*=db(-16-li);# Seulement les pointes dépassant -2.65 dBFS sont limitées ; pas de changement de débit.
   peak=np.max(abs(x),axis=1,keepdims=True);x*=np.minimum(1,db(-2.65)/np.maximum(peak,1e-12));li,tp=level(x)
   if tp>-2:x*=db(-2-tp);li,tp=level(x)
   assert np.all(np.isfinite(x)) and np.max(abs(x))<1 and -16.65<=li<=-15.35 and tp<=-1.95,(n,li,tp);out=dest/f'{n:02}-{t["artiste"]}.mp4';run([F,'-v','error','-y','-i',str(video),'-f','f32le','-ar',str(R),'-ac','2','-i','-','-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',str(out)],input=np.asarray(x,'<f4').tobytes());audio=decode(out);ai,ap=level(audio);assert vh(out)==orig and abs(len(audio)/R-30)<.025 and ap<=-1 and abs(ai+16)<.75,(ai,ap);res.append(dict(numero=n,id=mid,titre=t['titre'],mp4=out.name,sha256=H(out),source_s=t['source_debut_s'],source_duree_s=round(len(full)/R,2),wav_lufs=li,wav_dbtp=tp,aac_lufs=ai,aac_dbtp=ap,rapport_voix_musique_db=round(balance,2)));print(n,t['titre'],ai,ap,flush=True)
 (dest/'controle-mixes.json').write_text(json.dumps(dict(resultat='PASS technique ; écoute propriétaire en attente',video_originale=orig,musique_ouverte_db=-3,musique_sous_parole_db=-10,attaque_ms=120,relachement_ms=450,voix_vitesse=1,versions=res),ensure_ascii=False,indent=2)+'\n');np.savetxt(dest/'automation.csv',np.c_[vtime[::480],envelope[::480]],delimiter=',',header='temps_s,gain_musique_db',comments='',fmt='%.3f')
if __name__=='__main__':main(P(sys.argv[1]),P(sys.argv[2]))
