"""Assemble un ZIP stable et contrôle la liste complète, les types de chemins, les tailles et les SHA."""
from pathlib import Path,PurePosixPath
import hashlib,json,zipfile,subprocess,sys
from jsonschema import validate
ROOT=Path(__file__).resolve().parents[4];T=Path(__file__).resolve().parents[1];HASH=lambda b:hashlib.sha256(b).hexdigest();jd=lambda o:(json.dumps(o,ensure_ascii=False,indent=2)+'\n').encode()
def verify(z):
 with zipfile.ZipFile(z) as f:
  names=f.namelist();m=json.loads(f.read('MANIFEST.json'));validate(m,json.loads(f.read('templates/commerce/commerce-t1/schemas/package.json')));rows={r['path']:r for r in m['files']};assert len(names)==len(set(names)) and len(rows)==len(m['files']) and set(names)==set(rows)|{'MANIFEST.json'}
  for n,r in rows.items():
   assert not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts and '\\' not in n;b=f.read(n);assert (len(b),HASH(b))==(r['bytes'],r['sha256']),n
 return m

def build(media,evidence,z):
 files={};commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();tracked=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0');
 for n in filter(None,tracked):files[n]=(ROOT/n,'source et documentation')
 for p in [media/'COMMERCE-T1-sans-voix.mp4',*sorted((media/'ecoutes').glob('*.mp4'))]:files['media/'+str(p.relative_to(media))]=(p,'film de référence')
 assert len([n for n in files if n.startswith('media/')])==5
 for n in ('controle.json','manifest.json','render-job.json','preuve-parcours.json','planche-QC.jpg','ecoutes/controle-mixes.json','ecoutes/automation.csv','CQ-architecture.json'):
  files['preuves-ci/'+n]=(evidence/n,'preuve du runner')
 rows=[]
 def save(z,n,b):
  h=zipfile.ZipInfo(n,(2026,1,1,0,0,0));h.compress_type=zipfile.ZIP_DEFLATED;h.external_attr=0o100644<<16;z.writestr(h,b)
 with zipfile.ZipFile(z,'w') as f:
  for n,(p,role) in sorted(files.items()):
   b=p.read_bytes();save(f,n,b);rows.append(dict(path=n,role=role,bytes=len(b),sha256=HASH(b)))
  save(f,'MANIFEST.json',jd(dict(template_id='COMMERCE-T1',version='2.0.0',schema_version='1.0.0',commit=commit,files=rows)))
 return verify(z)
if __name__=='__main__':
 if sys.argv[1]=='verify':print(len(verify(Path(sys.argv[2]))['files']),'fichiers vérifiés')
 else:print(len(build(*map(Path,sys.argv[1:4]))['files']),'fichiers empaquetés')
