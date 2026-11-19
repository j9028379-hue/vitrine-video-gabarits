from pathlib import Path as P
import hashlib,json,string,secrets
from jsonschema import Draft202012Validator as V
root=P(__file__).resolve().parents[1]
def read(p):return json.loads((root/p).read_text())
c=read('montage/contrat-candidat.json');g=read(c['guide']['path']);v=V(read(c['formulaire']['schema']))
# Données techniques changeantes : aucun nom de produit réel ; numéro de fiction réservé.
f={k:k+'_'+secrets.token_hex(4) for k in ['produit','accroche','nom','quartier']};f.update(prix=1520,whatsapp='+12025550142');v.validate(f)
assert not v.is_valid({**f,'whatsapp':'+229 XX XX XX XX'})
assert not v.is_valid({**f,'produit':'   '})
for key in g['required']:assert not v.is_valid({k:val for k,val in f.items() if k!=key})
sc=c['scenes'];assert [x['prise'] for x in sc]==[f'prise_validee_S{i}' for i in range(1,5)];assert [x['sortie_s'] for x in sc]==[[0,6],[6,14],[14,21],[21,30]];assert c['duree_s']==30
for x,guide in zip(sc,g['scenes']):
 begin,end=x['source_s'];assert 0<=begin<end<=guide['capture'] and end-begin==guide['kept']==x['sortie_s'][1]-x['sortie_s'][0]
class F(string.Formatter):
 def format_field(self,v,s):return f'{v:,} F CFA'.replace(',',' ') if s=='fcfa' else super().format_field(v,s)
fmt=F();resolved=[[fmt.format(line,**f) for line in x['textes']] for x in sc];assert resolved==[[f['nom'],f['produit']],[f['accroche'],'1 520 F CFA'],[],[f['nom'],f['quartier'],'Écris-nous sur WhatsApp',f['whatsapp']]];assert c['guide']['sha256']==hashlib.sha256((root/c['guide']['path']).read_bytes()).hexdigest();assert [e['motif'] for e in c['effets']]==list('ABCDEFGH');assert c['reference']['url']==read('research/references.json')[1]['page'];assert all(hashlib.sha256((root/'assets/fonts'/name).read_bytes()).hexdigest()==h for name,h in c['polices'].items());print('PASS — guide, référence 2, six omissions rejetées, numéro masqué rejeté, liaisons avec des valeurs techniques générées, sans produit prédéfini, quatre sources ordonnées, fenêtres, 30 s, huit motifs, empreintes des polices du contrat. Tests locaux de contrat uniquement : aucun rendu ni CI.')

for s in sc:
 layers=[g for g in c['calques'] if g['scene']==s['id']]
 assert [g['texte'] for g in layers]==s['textes']
 for g in layers:
  a,b=g['images']; assert 30*s['sortie_s'][0]<=a<b<=30*s['sortie_s'][1] and b-a-g['entree']-g['sortie']>=30
for n in range(900):assert sum(g['images'][0]<=n<g['images'][1] for g in c['calques'])<=2
html=(root/'form/Formulaire-commerce.html').read_text();assert json.loads(html.split(',C=',1)[1].split(';const f=',1)[0])==c
# Stress de lettrage : valeurs limites, espaces et mot sans coupure.
import sys
sys.path.insert(0,str(root/'engine'))
from lettrage import stamp
for variant in (0,1):
 longest={k:('W'*p['maxLength'] if not variant else ('Été '*p['maxLength'])[:p['maxLength']].strip()) for k,p in v.schema['properties'].items() if 'maxLength' in p};longest.update(prix=999999999,whatsapp='+123456789012345');v.validate(longest)
 for layer in c['calques']:
  msg=fmt.format(layer['texte'],**longest);_,meta=stamp(root,layer,c,msg);x,y,w,h=meta['rectangle'];assert 35<=x and x+w<=685 and y>0 and y+h<1280 and ''.join(''.join(meta['lignes']).split())==''.join(msg.split())
print('PASS — horloge, formulaire synchronisé, maximum deux calques simultanés, réponses aux longueurs limites.')
import subprocess
integrated=root/'integration/Parcours-vers-montage.html';before=integrated.read_bytes();subprocess.run([sys.executable,str(root/'integration/construire.py')],check=True);assert before==integrated.read_bytes();print('PASS — reconstruction déterministe du parcours intégré.')
