from pathlib import Path
import json,hashlib,tempfile,subprocess,urllib.request,shutil
base=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as scratch:
 for row in json.loads((base/'sources.json').read_text()):
  raw=Path(scratch)/'origine.mp4';subprocess.run(['curl','--fail','--silent','--show-error','--location','--retry','3','--max-time','90','--output',str(raw),row['url']],check=True);assert hashlib.sha256(raw.read_bytes()).hexdigest()==row['sha256'],row['scene']+' : source modifiée ; contrôle requis';subprocess.run(['ffmpeg','-loglevel','error','-y','-i',str(raw),'-vf','setpts=PTS-STARTPTS,fps=30:start_time=0','-an','-c:v','libx264','-preset','veryfast','-crf','17','-pix_fmt','yuv420p',str(base/(row['scene']+'.mp4'))],check=True)
# La préparation des rushs de démonstration livre un vrai RenderJob émis en 4C.
# Les six réponses de la fixture servent uniquement à remplir le formulaire du navigateur.
import os
root=base.parents[1]
with tempfile.TemporaryDirectory() as tools:
 subprocess.run(['npm','install','--prefix',tools,'--no-audit','--no-fund','--ignore-scripts','puppeteer-core@23.11.1'],check=True)
 subprocess.run(['node',str(root/'integration/banc.cjs')],check=True,env={**os.environ,'NODE_PATH':tools+'/node_modules'})
