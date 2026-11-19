"""Référence CLI, une instance par état de sélection. Jamais de réseau ni d'upload."""
import argparse,fcntl,hashlib,json,os,subprocess,sys
from pathlib import Path
from jsonschema import validate,ValidationError
from job import lire
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def select(ids,job_id,last=None,requested=None):
 pool=[i for i in ids if i!=last]
 if requested is not None:
  if requested not in pool:raise ValueError('Sélection interdite ou répétée')
  return requested
 return pool[int.from_bytes(hashlib.sha256(job_id.encode()).digest()[:8],'big')%len(pool)]
def atomic(p,value):
 tmp=p.with_name(p.name+'.tmp');tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');os.replace(tmp,p)
def contract(kind,x):validate(x,read(ROOT/'schemas'/f'{kind}.json'));return x
def execute(src,out,jid,mode='silent',state=None,media=None,requested=None):
 out.mkdir(exist_ok=True,parents=True);base=dict(template_id='COMMERCE-T1',version='2.0.0',job_id=jid);stage='INVALID_JOB'
 try:
  if not jid.strip():raise ValueError('Identifiant de rendu requis')
  c=read(ROOT/'montage/contrat-candidat.json');contract('template',c)
  if mode in ('silent','merchant-music'):
   contract('render-job',read(src/'render-job.json'));stage='INVALID_CAPTURE';lire(src,ROOT,c);stage='UNSUPPORTED_MEDIA';import cv2
   for s in c['scenes']:
    cap=cv2.VideoCapture(str(src/(s['id']+'.mp4')));n=cap.get(7);fps=cap.get(5);cap.release();limit=1800 if (src/'decoupe-v2.json').exists() else s['capture_s']*30+1
    if abs(fps-30)>.001 or not s['capture_s']*30<=n<=limit:raise ValueError('Cadence ou durée de prise non conforme')
   stage='RENDER_FAILED';subprocess.run([sys.executable,str(ROOT/'engine/rendre.py'),str(src),str(out)],check=True);p=out/'COMMERCE-T1-sans-voix.mp4'
   if mode=='merchant-music':
    from son_marchand import produire
    state=Path(state);state.parent.mkdir(parents=True,exist_ok=True);ids=[x['id'] for x in read(ROOT/'audio/catalogue.json')['pistes']];stage='INVALID_SELECTION'
    with state.with_name(state.name+'.lock').open('a') as lock:
     fcntl.flock(lock,fcntl.LOCK_EX);last=read(state)['last_success'] if state.exists() else None;i=select(ids,jid,last,requested);stage='RENDER_FAILED';p=produire(p,src,out,media,i,c);result=contract('render-result',{**base,'status':'COMPLETED','mode':mode,'output':p.name,'sha256':sha(p),'bytes':p.stat().st_size});atomic(out/'RenderResult.json',result);atomic(state,{'last_success':i});return result
  elif mode=='demo-approved':
   stage='INVALID_SELECTION';songs={r['id']:r for r in read(ROOT/'audio/catalogue.json')['pistes']};state=Path(state);state.parent.mkdir(parents=True,exist_ok=True)
   with state.with_name(state.name+'.lock').open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX);last=read(state)['last_success'] if state.exists() else None;i=select(list(songs),jid,last,requested);row=songs[i];p=Path(media)/row['fichier_demo'];stage='RENDER_FAILED'
    if sha(p)!=row['sha256_demo']:raise ValueError('Film intégré absent ou non conforme')
    result=contract('render-result',{**base,'status':'COMPLETED','mode':mode,'output':p.name,'sha256':row['sha256_demo'],'bytes':p.stat().st_size});atomic(out/'RenderResult.json',result);atomic(state,{'last_success':i});return result
  else:raise ValueError('Mode inconnu')
  result=contract('render-result',{**base,'status':'COMPLETED','mode':mode,'output':p.name,'sha256':sha(p),'bytes':p.stat().st_size});atomic(out/'RenderResult.json',result);return result
 except (ValueError,ValidationError,KeyError,OSError,subprocess.CalledProcessError) as e:
  err=contract('render-error',{**base,'job_id':jid or 'non-fourni','status':'FAILED','code':stage,'message':str(e)[:500] or stage});atomic(out/'RenderError.json',err);return err
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--job',type=Path,default=Path('.'));p.add_argument('--out',type=Path,required=True);p.add_argument('--id',required=True);p.add_argument('--mode',choices=['silent','demo-approved','merchant-music'],default='silent');p.add_argument('--state',type=Path,default=Path('rotation.json'));p.add_argument('--media',type=Path,default=Path('media/ecoutes'));p.add_argument('--piste',type=int);a=p.parse_args();r=execute(a.job,a.out,a.id,a.mode,a.state,a.media,a.piste);print(json.dumps(r,ensure_ascii=False));sys.exit(r['status']!='COMPLETED')
