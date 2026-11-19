from pathlib import Path
import json,hashlib,tempfile,subprocess,urllib.request,shutil
base=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as scratch:
 for row in json.loads((base/'sources.json').read_text()):
  raw=Path(scratch)/'origine.mp4';subprocess.run(['curl','--fail','--silent','--show-error','--location','--retry','3','--max-time','90','--output',str(raw),row['url']],check=True);assert hashlib.sha256(raw.read_bytes()).hexdigest()==row['sha256'],row['scene']+' : source modifiée ; contrôle requis';subprocess.run(['ffmpeg','-loglevel','error','-y','-ss',str(row['start']),'-i',str(raw),'-t',str(row['duration']),'-vf','fps=30','-an','-c:v','libx264','-preset','veryfast','-crf','17','-pix_fmt','yuv420p',str(base/(row['scene']+'.mp4'))],check=True)
