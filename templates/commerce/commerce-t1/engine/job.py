import hashlib,json
from jsonschema import validate

def lire(job,root,c):
 j=json.loads((job/'render-job.json').read_text());schema=json.loads((root/'form/schema-v0.1.json').read_text());validate(j['merchant_payload'],schema)
 if set(j)!={'template_id','template_version','merchant_payload','captures'} or (j['template_id'],j['template_version'])!=('COMMERCE-T1',c['version']):raise ValueError('Contrat de job incorrect')
 records=j['captures'];assets={};seen=set();ids=set()
 if set(records)!={s['id'] for s in c['scenes']}:raise ValueError('Quatre scènes requises')
 for s in c['scenes']:
  a=records[s['id']];name=s['id']+'.mp4';path=job/name
  if a['validation']!='C' or a['uri']!=name or type(a['prise']) is not int or a['prise']<=0 or a['prise'] in ids:raise ValueError('Prise non valide')
  ids.add(a['prise']);digest=hashlib.sha256(path.read_bytes()).hexdigest()
  if a['sha256']!=digest or digest in seen:raise ValueError('Rush modifié ou dupliqué')
  assets[s['prise']]=name;seen.add(digest)
 return j['merchant_payload'],assets
