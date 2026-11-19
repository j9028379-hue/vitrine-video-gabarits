"""Test client distinct ; exécuté sur GitHub, quatre MP4 importés via le vrai parcours navigateur."""
from pathlib import Path as P
import hashlib,json,os,subprocess,sys,tempfile,shutil,wave
import numpy as np
D=P(__file__).resolve().parent;R=D.parents[1];sys.path.insert(0,str(R/'engine'));from runtime import execute,read,sha,atomic,select
run=lambda args,**kw:subprocess.run(args,check=True,**kw)
def get(url,path):run(['curl','--fail','--silent','--show-error','-L','--retry','3',url,'-o',str(path)])
def main(dest):
 dest.mkdir(parents=True,exist_ok=True);jobid='braise-ronde-'+os.environ['GITHUB_RUN_ID']+'-'+os.environ['GITHUB_RUN_ATTEMPT'];sources=read(D/'sources.json');sc=read(R/'montage/contrat-candidat.json')['scenes'];plan=[]
 with tempfile.TemporaryDirectory() as td:
  q=P(td);src=q/'prises';src.mkdir();shutil.copy(D/'formulaire.json',src/'formulaire.json')
  for row,s in zip(sources,sc):
   k=s['id'];p=q/'original.mp4';get(row['source_url'],p);assert sha(p)==row['sha256'];vo=D/'voix'/f'{k}.wav';assert sha(vo)==row['voix_sha256'];chunk=subprocess.check_output(['ffmpeg','-v','error','-i',str(vo),'-ar','48000','-ac','1','-f','f32le','-']);x=np.frombuffer(chunk,'<f4');t=row['pause_position_s'];gap=row['pause_ajoutee_s'];cut=round(t*48000)
   if gap:
    assert np.max(abs(x[cut-100:cut+100]))<.025;x=np.r_[x[:cut],np.zeros(round(gap*48000),np.float32),x[cut:]]
   dur=s['capture_s'];audio=np.zeros(dur*48000,np.float32);begin=row['debut_voix_depuis_scene'];assert begin+len(x)/48000<s['sortie_s'][1]-s['sortie_s'][0];offset=round((s['source_s'][0]+begin)*48000);audio[offset:offset+len(x)]=x;plan.append({'scene':k,'debut_clip_s':s['sortie_s'][0]+begin,'fin_clip_s':s['sortie_s'][0]+begin+len(x)/48000,'vitesse':1})
   run(['ffmpeg','-v','error','-y','-i',str(p),'-f','f32le','-ar','48000','-ac','1','-i','-','-map','0:v','-map','1:a','-vf',f"setpts={row['facteur_duree_images']}*(PTS-STARTPTS),fps=30,tpad=stop_mode=clone:stop_duration=0.12",'-t',str(dur),'-c:v','libx264','-threads','2','-preset','veryfast','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k',str(src/(k+'.mp4'))],input=audio.tobytes())
  # Générer le RenderJob via formulaire, A/B/C et reprise 1C (aucune validation falsifiée).
  run(['npm','install','--prefix',str(q/'tools'),'--no-audit','--no-fund','--ignore-scripts','puppeteer-core@23.11.1']);run(['node',str(R/'integration/banc.cjs')],env={**os.environ,'NODE_PATH':str(q/'tools/node_modules'),'COMMERCE_JOB_DIR':str(src)})
  # Chaque runner relit le journal public durable. La publication compare la révision avant d’accepter la proposition.
  # Une seule révision immuable pour le contenu et le SHA de comparaison.
  # Échec fermé si la branche est absente : ne jamais réinitialiser la rotation.
  ref='refs/commerce-test/rotation';run(['git','fetch','--quiet','--no-tags','--depth=1','origin','+refs/heads/state/commerce-autoplay:'+ref],cwd=R)
  blob=subprocess.check_output(['git','rev-parse','--verify',ref+':autoplay/etat.json'],cwd=R,text=True).strip()
  last=json.loads(subprocess.check_output(['git','cat-file','blob',blob],cwd=R))['last_success']
  state=q/'etat.json';atomic(state,{'last_success':last});catalog=read(R/'audio/catalogue.json')['pistes'];ids=[e['id'] for e in catalog];assert len(ids)==len(set(ids))==4 and last in ids;expected=select(ids,jobid,last);assert expected!=last;track=next(e for e in read(R/'audio/auditions/sources.json') if e['id']==expected);get(track['source_mp3'],q/f'{expected}.mp3');assert sha(q/f'{expected}.mp3')==track['sha256']
  result=execute(src,q/'output',jobid,'merchant-music',state,q);assert result['status']=='COMPLETED',result;selected=read(state)['last_success'];mix=read(q/'output/mix-marchand.json');assert expected==selected==mix['music_id'] and mix['active_blocks']>500;mp=dest/'La-Braise-Ronde-Pizza.mp4';shutil.copyfile(q/'output'/result['output'],mp);assert sha(mp)==result['sha256'];mf=read(q/'output/manifest.json');a=read(src/'formulaire.json');assert mf['textes_affiches']==[[a['nom'],a['produit']],[a['accroche'],a['prix']],[],[a['nom'],a['quartier'],'Écris-nous sur WhatsApp',a['whatsapp']]]
  info=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(mp)]));v,au=info['streams'];assert (v['width'],v['height'],v['nb_read_frames'],au['codec_name'],au['sample_rate'])==(720,1280,'900','aac','48000') and float(info['format']['duration'])==30
  for f in ['render-job.json','preuve-parcours.json']:shutil.copyfile(src/f,dest/f)
  atomic(dest/'CQ-pizza.json',dict(job=jobid,run_id=int(os.environ['GITHUB_RUN_ID']),commit=os.environ['GITHUB_SHA'],sha256=result['sha256'],libelle='Restaurant fictif, quatre rushs importés et voix IA française',images=900,duree_s=30,textes=mf['textes_affiches'],voix=plan,son=mix,stock_sha256=[s['sha256'] for s in sources],rotation={'revision_precedente':blob,'precedente':last,'numero_precedent':ids.index(last)+1,'choisie':selected,'numero_choisi':ids.index(selected)+1,'titre':track['titre'],'artiste':track['artiste'],'candidates':ids,'choix_manuel':False}));print('PASS rendu pizza + rotation automatique',last,selected,flush=True)
if __name__=='__main__':main(P(sys.argv[1]))
