# Mission 1 — préparation du canon Commerce (pas de système OTA)

**Décision : aucun champ à ajouter au canon.** Le moteur `engine/rendre.py` charge `montage/contrat-candidat.json` ; `engine/runtime.py` le valide avec `schemas/template.json`. C'est aussi le fichier désigné dans `catalogue/catalogue.json`.

| Champ unique | Restauration, référence | Commerce, contrat existant |
|---|---|---|
| `template_id` | `T1` | `COMMERCE-T1` |
| `version` (gabarit) | `1.0.0` | `2.0.0` |
| `audio_profile` | `afrobeat_amapiano` | `afrobeat_amapiano_commerce` |

Sources Restauration inspectées en lecture seule : [stable silencieuse](https://github.com/j9028379-hue/vitrine-video-t1-pilot/releases/tag/t1-special-menu-template-v1.0.0-silent), [successeur musical](https://github.com/j9028379-hue/vitrine-video-t1-pilot/releases/tag/t1-special-menu-music-v1.0.0), [canon du pilote préparé](https://github.com/j9028379-hue/vitrine-video-t1-pilot/blob/c656510ab81d31d413dc4dfd74b42671532cd978/config/T1_special_menu_template_v1_0_0.json). Ni l'identifiant du pilote ni l'exemple `food_energetic_120bpm` ne doivent écraser l'identité Commerce. Chaque canon conserve son `id` historique ; ne pas en recréer un ni retirer un champ exigé du schéma.

Le catalogue audio Commerce porte sa propre `pack_version: 1.0.0`. Les titres et les quatre IDs restent hors du canon. La piste 573944 est absente de la rotation. La référence visuelle documentaire du canon est un lien de provenance, pas un téléchargement OTA. Aucun client réseau ni service Cloudflare ajouté.

**Changements du commit :** ce rapport ; `tests/cq_preparation_catalogue.py` (nouveau contrôle hors ligne) ; `tests/cq_architecture.py` (appel dans la suite du runner et résultat dans `CQ-architecture.json`). Aucun changement de JSON canonique, schéma, moteur, calibration, partition, scènes, parcours, sources média ou release.

**Validation :** contrôle local des clés JSON uniques, schéma, pointeur de catalogue, identité/version/profil, sélection autorisée et séparation OTA. Le CI exécute ensuite le parcours, le rendu silencieux, le contrôle des 900 images, les quatre mixes, le rendu marchand et la pizza. Comparaison avant/après sur la même fixture et les quatre mêmes pistes ; ne pas comparer directement les deux pizzas comme si la rotation musicale devait rester fixe. Témoin avant : [run 44613392868](https://github.com/j9028379-hue/vitrine-video-gabarits/actions/runs/44613392868). Résultats après et comparaison attachés à la PR nº 2 à l'issue du run, distincts de la décision de fusion. Aucune livraison OTA ni validation mobile revendiquée.
