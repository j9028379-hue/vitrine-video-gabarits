"""Contre-épreuve bout en bout : autre formulaire, rushs courts et son capté simulé. Aucun média de test publié."""
from pathlib import Path as P
import json,sys,subprocess,hashlib,tempfile,os
r=P(__file__).resolve().parents[1];sys.path.insert(0,str(r/'engine'));from runtime import execute,read,sha,atomic

def contre_epreuve(out):
 with tempfile.TemporaryDirectory() as tmp:
  q=P(tmp);src=q/'job';src.mkdir();dest=q/'out';d=read(out/'render-job.json');d['merchant_payload']={'nom':'Atelier essai','produit':'Article contrôle','prix':7625,'accroche':'Message distinct','quartier':'Lieu test','whatsapp':'+12025550143'}
  for n,dur in enumerate([8,10,9,11],1):
   k=f'S{n}';f=src/(k+'.mp4');cmd=['ffmpeg','-v','error','-i',str(r/'fixtures/rushs'/(k+'.mp4'))]
   if n==2:cmd+=['-f','lavfi','-i','sine=frequency=350:sample_rate=48000','-map','0:v:0','-map','1:a:0','-c:a','aac']
   else:cmd+=['-an']
   subprocess.run(cmd+['-t',str(dur),'-vf','scale=320:180','-threads','2','-c:v','libx264','-preset','ultrafast',str(f)],check=True);d['captures'][k]['sha256']=sha(f)
  atomic(src/'render-job.json',d);piste=623364;t=next(x for x in read(r/'audio/auditions/sources.json') if x['id']==piste);p=q/f'{piste}.mp3';subprocess.run(['curl','--fail','--silent','--show-error','--retry','2',t['source_mp3'],'-o',str(p)],check=True);assert sha(p)==t['sha256'];state=q/'etat.json';res=execute(src,dest,'cq-nouvelle-saisie','merchant-music',state,q,piste);assert res['status']=='COMPLETED',res;data=read(dest/'mix-marchand.json');assert 700<=data['active_blocks']<=810 and read(state)['last_success']==piste;assert read(dest/'manifest.json')['textes_affiches']==[['Atelier essai','Article contrôle'],['Message distinct','7 625 F CFA'],[],['Atelier essai','Lieu test','Écris-nous sur WhatsApp','+12025550143']];return {'render_result':res,'son':data,'saisie_distincte':True,'source_audio_test':'signal de contrôle seulement en scène 2','fichier_de_test_non_distribue':True}
