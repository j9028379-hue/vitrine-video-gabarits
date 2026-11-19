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
fmt=F();resolved=[[fmt.format(line,**f) for line in x['textes']] for x in sc];assert resolved==[[f['produit']],[f['accroche']],[],['1 520 F CFA',f['nom']+' · '+f['quartier'],'Contacte-nous sur WhatsApp',f['whatsapp']]];assert c['guide']['sha256']==hashlib.sha256((root/c['guide']['path']).read_bytes()).hexdigest();assert [e['motif'] for e in c['effets']]==list('ABCDEFGH');assert c['reference']['url']==read('research/references.json')[1]['page'];assert all(hashlib.sha256((root/'assets/fonts'/name).read_bytes()).hexdigest()==h for name,h in c['polices'].items());print('PASS — guide, référence 2, six omissions rejetées, numéro masqué rejeté, liaisons avec des valeurs techniques générées, sans produit prédéfini, quatre sources ordonnées, fenêtres, 30 s, huit motifs, empreintes des polices du contrat. Tests locaux de contrat uniquement : aucun rendu ni CI.')
