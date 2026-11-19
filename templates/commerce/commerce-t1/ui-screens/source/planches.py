"""Assembler les captures Chromium sans rogner les pages longues."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[1];D=root.parent/'assets/fonts';font=lambda n,b=False:ImageFont.truetype(str(D/('DejaVuSans-Bold.ttf' if b else 'DejaVuSans.ttf')),n)
for guides in [True,False]:
 stages='A' if guides else 'ABC';imgs={(i,j):Image.open(root/f'captures/S{i}{j}.png').convert('RGB') for j in stages for i in range(1,5)};col=max(im.width for im in imgs.values())+20;heights=[max(imgs[i,j].height for i in range(1,5))+67 for j in stages];plate=Image.new('RGB',(4*col+26,147+sum(heights)), '#f6f4ec');d=ImageDraw.Draw(plate);d.text((22,14),'VITRINE VIDÉO   /   COMMERCE   /   SOCLE 01',font=font(17,True),fill='#376459');d.text((22,42),'Les quatre guides de tournage' if guides else 'Produit vedette · Les douze écrans',font=font(37,True),fill='#163d36');d.text((23,100),'Une colonne par scène. '+('Les exemples illustrés ne limitent pas ce que tu peux présenter.' if guides else 'Lis de haut en bas : guide, enregistrement, vérification.'),font=font(20),fill='#405c50');y=147
 for j,hh in zip(stages,heights):
  for i in range(1,5):
   x=18+(i-1)*col;n=(i-1)*3+'ABC'.index(j)+1;d.text((x,y),f'{n:02d}   /   SCÈNE {i}   ·   '+{'A':'Guide','B':'Enregistrement','C':'Vérification'}[j],font=font(18,True),fill='#235c50');plate.paste(imgs[i,j],(x,y+31))
  y+=hh
 plate.save(root/('Planche-4-guides.png' if guides else 'Planche-12-ecrans.png'),optimize=True)
