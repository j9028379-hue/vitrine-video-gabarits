# Du formulaire au film · COMMERCE-T1

[Parcours intégré HTML](Parcours-vers-montage.html) (télécharger et ouvrir dans Chrome) : le formulaire accepte les six réponses, puis chaque scène permet d’importer une vidéo MP4. Les écrans A/B/C reprennent les guides et les composants du prototype. B **simule** le temps de prise sur le rush importé ; C relit ce même fichier et permet de le refaire. Il ne s’agit pas d’une caméra Android. Aucun fichier personnel n’est envoyé depuis le navigateur. Après la quatrième validation, le navigateur peut exporter le RenderJob. Le moteur attend ce JSON et les quatre fichiers correspondants nommés S1.mp4 à S4.mp4. La découpe affinée de la démo est propre aux quatre rushs de référence et ne doit pas être appliquée à d’autres vidéos courtes.

Le modèle audité : [liaison des 12 écrans du T1 public](https://github.com/j9028379-hue/vitrine-video-t1-pilot/blob/c656510ab81d31d413dc4dfd74b42671532cd978/reports/T1_CAPTURE_FLOW_12_SCREENS_INTEGRATION.md) et [son RenderJob](https://github.com/j9028379-hue/vitrine-video-t1-pilot/blob/c656510ab81d31d413dc4dfd74b42671532cd978/fixtures/t1-special-menu/render_job.valid.json). Commerce reprend la séparation `merchant_payload` / `captures`, avec six champs obligatoires. Les consignes de capture et phrases facultatives ne sont pas injectées comme slogans. Le CTA fixe vient du contrat ; la voix synthétique est une démonstration séparée et n’est pas recalculée pour une saisie différente.

| Validation | Source | Sortie dans le master |
| --- | --- | --- |
| Écran 3 · 1C | captures.S1 | 0–6 s : nom puis produit |
| Écran 6 · 2C | captures.S2 | 6–14 s : message puis prix formaté |
| Écran 9 · 3C | captures.S3 | 14–21 s : geste sans texte |
| Écran 12 · 4C | captures.S4 | 21–30 s : nom et lieu, puis CTA fixe et numéro saisi |

Avant cette révision, le formulaire prévisualisait les réponses et le master lisait séparément deux fixtures. Aujourd’hui le banc ouvre le parcours dans Chrome sur le runner GitHub, remplit les champs, importe les quatre rushs, teste « Refaire », valide les quatre C et transmet le JSON de sortie au moteur. `formulaire.json` est l’entrée du test navigateur, **plus une entrée du moteur**. Le JSON exporté verrouille les fichiers par SHA-256. `qc_mp4.py` vérifie textes résolus, empreintes des entrées et échantillons du MP4 décodé. Ce parcours de démonstration n’est ni un déploiement en production ni un téléversement automatique des données de vrais commerçants.
