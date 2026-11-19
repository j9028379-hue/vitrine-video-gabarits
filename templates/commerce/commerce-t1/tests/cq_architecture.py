from pathlib import Path as P
import json,sys,tempfile,subprocess,hashlib,copy,shutil
import cv2,numpy as np
from jsonschema import validate,ValidationError
r=P(__file__).resolve().parents[1];repo=r.parents[2];sys.path[:0]=[str(r/'engine'),str(r/'package')];from runtime import select,execute,contract,read,sha,atomic
from livrer import build,verify
out=P(sys.argv[1]);checks={};j=read(out/'render-job.json');c=read(r/'montage/contrat-candidat.json');contract('template',c);contract('render-job',j);checks['schemas et job du navigateur']=True
for f in [lambda a:a.update(secret='x'),lambda a:a['captures']['S1'].update(debug=True),lambda a:a['captures']['S1'].update(uri='../m.mp4'),lambda a:a['captures'].pop('S4'),lambda a:a['merchant_payload'].pop('accroche')]:
 x=copy.deepcopy(j);f(x)
 try:contract('render-job',x)
 except ValidationError:continue
 raise AssertionError('Job invalide accepté')
checks['5 mutations de job refusées']=True;catalog=read(repo/'catalogue/catalogue.json')['entries'][0];assert all(c[k]==catalog[k] for k in ['template_id','version','audio_profile']);assert not catalog['ota_implemented'];assert (repo/catalog['contrat']).resolve()==(r/'montage/contrat-candidat.json').resolve();checks['identité catalogue hors ligne']=True
songs=read(r/'audio/catalogue.json')['pistes'];ids=[s['id'] for s in songs];assert len(ids)==len(set(ids))==4;prev=None;seen=set()
for i in range(10000):
 key=f'job-{i}';a=select(ids,key,prev);assert a==select(ids,key,prev) and a!=prev;seen.add(a);prev=a
assert seen==set(ids);checks['rotation déterministe sans répétition']=10000
with tempfile.TemporaryDirectory() as temp:
 q=P(temp);res=execute(q,q/'output','invalide');assert res['code']=='INVALID_JOB';contract('render-error',res)
 # Fichier de démo intègre : cas réussi et échecs sans modifier le dernier succès.
 media=q/'media';media.mkdir();state=q/'state';s=songs[0];p=media/s['fichier_demo'];approved=out/'ecoutes'/p.name
 if sha(approved)==s['sha256_demo']:
  shutil.copyfile(approved,p);res=execute(q,q/'output','ok','demo-approved',state,media,s['id']);assert res['status']=='COMPLETED';contract('render-result',res)
 else:atomic(state,{'last_success':s['id']})
 before=state.read_bytes();assert execute(q,q/'output','bis','demo-approved',state,media,s['id'])['code']=='INVALID_SELECTION';assert execute(q,q/'output','absent','demo-approved',state,media,ids[1])['code']=='RENDER_FAILED';assert state.read_bytes()==before
checks['erreurs typées et dernier succès préservé']=True
v=read(r/'audio/audition-voix.json');assert all(sha(r/'audio/voix'/f"S{g['scene']}.wav")==g['sha256'] for g in v['clips']);assert len(v['clips'])==4;checks['4 clips de la voix choisie : SHA-256']=True
ref=read(r/'golden/reference.json');assert sha(r/'golden/images-900.npz')==ref['miniatures_sha256'];gold=np.load(r/'golden/images-900.npz')['images'];p=out/'COMMERCE-T1-sans-voix.mp4';cap=cv2.VideoCapture(str(p));errors=[]
for g in gold:
 ok,a=cap.read();assert ok;actual=cv2.resize(a,(36,64),interpolation=cv2.INTER_AREA);errors.append(float(np.abs(actual.astype(float)-g).mean()))
assert len(errors)==900 and not cap.read()[0] and max(errors)<=ref['tolerance_mae_par_image'],max(errors);cap.release();checks['900 images contre référence acceptée : MAE maximum']=max(errors);checks['master silencieux identique octet par octet']=sha(p)==ref['mp4_sha256'];m=read(out/'ecoutes/controle-mixes.json');checks['variantes régénérées identiques octet par octet']=[x['sha256']==s['sha256_demo'] for x,s in zip(m['versions'],songs)];assert len(m['versions'])==4
for x,s in zip(m['versions'],songs):assert x['id']==s['id'] and abs(x['aac_lufs']+16)<.75 and x['aac_dbtp']<=-1 and x['rapport_voix_musique_db']>=4
checks['mixes, niveaux AAC, balance, identité du flux vidéo']=4
subprocess.run(['node',str(repo/'shared/cloudflare-control-plane/test.mjs')],check=True);checks['Worker 4 contrôles handlers']=True
with tempfile.TemporaryDirectory() as tmp:subprocess.run(['npx','--yes','wrangler@4.45.0','deploy','--dry-run','--outdir',tmp],cwd=repo/'shared/cloudflare-control-plane',check=True)
checks['Wrangler assemblage dry-run sans déploiement']=True
from cq_marchand import contre_epreuve
checks['Contre-épreuve rendu marchand avec musique du cache local']=contre_epreuve(out)
sha_ci=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip();atomic(out/'CQ-architecture.json',{'commit':sha_ci,'resultat':'PASS contrôles de référence listés','checks':checks,'non_testes':['Android physique, notamment 2 Go','OTA appareil–serveur, signature, activation, rollback','Cloudflare de production et authentification de dispatch','réécoute des quatre auditions vocales initiales (plateforme, pas d’archive de ces quatre démos)']});z=out/'COMMERCE-T1-2.0.0.zip';manifest=build(out,out,z);print('Paquet contrôlé, fichiers:',len(manifest['files']))
