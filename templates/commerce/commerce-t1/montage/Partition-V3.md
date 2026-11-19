# Produit vedette — partition de lecture V3

Le plan reste visible sur toute la hauteur. La signature appartient au commerce, les empattements au produit et aux informations à lire. Aucun exemple du guide de tournage ne devient un slogan. Les réponses gardent leur casse, le montant reçoit son unité. Le numéro filmé dans cette démo est fictif.

| Scène | Entrée → sortie (secondes) | Lecture et mouvement |
|---|---|---|
| 1 · découverte | 1,50–5,70 ; 2,40–5,70 | La signature du commerce se découvre de gauche à droite sur le corps de la tasse. Le produit se pose en dessous, sans masquer le dessin à la surface. |
| 2 · détail | 6,47–9,83 ; 10,70–13,57 | Le détail saisi suit une vague douce dans le tiers inférieur. Il disparaît **avant** la poussée du plan. Après celle-ci, le prix prend sa place, seul. |
| 3 · geste | 14–21 | Aucun lettrage. Le changement d’échelle et la tranche animée portent l’attention sur la main et sur le résultat. |
| 4 · contact | 22,20–25,43 ; quartier dès 22,73 | L’enseigne se signe, le quartier remonte dessous. Le bas du plan reste libre pour la tasse. |
| 4 · deuxième temps | 25,50–29,30 ; numéro dès 25,90 | La signature et le quartier ont disparu. « Écris-nous sur WhatsApp » invite à agir ; le numéro remonte puis reste immobile jusqu’à la sortie, avant la fermeture en lamelles. |

**Trois références, trois usages distincts.** [Le JSON public de T1](https://github.com/j9028379-hue/vitrine-video-t1-pilot/blob/c656510ab81d31d413dc4dfd74b42671532cd978/config/T1_special_menu_template_v1_0_0.json) sépare les entrées, les compositions nommées, leurs fenêtres en images, leur ancrage et leur révélation. Son [moteur](https://github.com/j9028379-hue/vitrine-video-t1-pilot/blob/c656510ab81d31d413dc4dfd74b42671532cd978/engine/special_menu_style.py) ajuste les lignes au cadre et révèle le masque. Commerce reprend ce principe, pas sa publicité de restaurant : les six réponses restent obligatoires et la scène du geste reste sans texte. [New Drink Product](https://www.capcut.com/template-detail/New-Drink-Product/7641833250612137223) fournit les huit motifs et les ruptures de plan, pas les polices. Le spécimen fourni guide la signature et le relief : Great Vibes et DM Serif Display, sous OFL, sont un rapprochement visuel, pas une identification de la police originale.

Le JSON fait foi à l’image près (30 i/s, fin exclue). Le moteur lit chaque valeur, position, fenêtre, taille et mouvement depuis `calques`. Les rushs réels et la découpe à sept temps sont inchangés. Aucun accord créatif ni publication ne découle du test technique.
