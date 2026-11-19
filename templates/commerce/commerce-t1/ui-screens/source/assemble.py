from pathlib import Path as P
import json,base64,sys
root=P(__file__).resolve().parents[2];d=P(sys.argv[1]);src=P(__file__).with_name('prototype.tpl').read_text();g=(root/'capture-guide/guide.json').read_text();uri=lambda p,m:'data:'+m+';base64,'+base64.b64encode(p.read_bytes()).decode();media=[{'guide':uri(d/f'guide{i}.jpg','image/jpeg'),'img':uri(d/f'{i}.jpg','image/jpeg'),'vid':uri(d/f'{i}.webm','video/webm')} for i in range(1,5)];(root/'simulation/Parcours-12-ecrans.html').write_text(src.replace('__GUIDE__',g).replace('__MEDIA__',json.dumps(media)))
