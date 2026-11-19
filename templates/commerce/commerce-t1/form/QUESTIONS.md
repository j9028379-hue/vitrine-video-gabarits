# COMMERCE-T1 · Ce que le commerçant renseigne

**Proposition de saisie · 30 secondes imposées · quatre scènes.** Les six clés viennent du socle décrit dans `autonome.md`, étape 5. Leur caractère obligatoire et leurs limites ci-dessous sont des propositions pour COMMERCE-T1, pas un schéma publié.

| Question affichée | Clé | Règle proposée | Exemple fictif | Utilisation exacte |
|---|---|---|---|---|
| Comment s’appelle ton commerce ? | `nom` | Obligatoire · 1–40 caractères | Boutique Démo | S4, signature au-dessus du contact. |
| Quel produit ou service veux-tu mettre en avant ? | `produit` | Obligatoire · 1–45 caractères | Lampe de bureau | S1, titre après l’ouverture. |
| Quel est son prix en F CFA ? | `prix` | Obligatoire · montant entier de 1 à 9 chiffres ; unité déjà affichée. | 7500 | S4, mis en forme : 7 500 F CFA. |
| Sur quel numéro WhatsApp peut-on te contacter ? | `whatsapp` | Obligatoire pour cette fin de vidéo · indicatif pays et numéro professionnel autorisé ; 15 chiffres max., hors « + ». Espaces tolérés à la saisie. | +229 01 XX XX XX XX | S4, instruction de contact + numéro. Exemple masqué, jamais accepté en production. |
| Dans quel quartier se trouve ton commerce ? | `quartier` | Facultatif · 1–40 caractères si renseigné | Akpakpa | S4 après le nom ; si vide, ni quartier ni séparateur. |
| Quel détail veux-tu montrer sur ce produit ou ce service ? | `accroche` | Facultatif · 1–55 caractères si renseigné ; une phrase courte et vérifiable. | Tête orientable | S2 ; si vide, le détail est montré sans texte de remplacement. |

### Exemple : tous les textes effectivement montrés

Données fictives, numéro délibérément non composable. Les intitulés de scènes ne sont pas incrustés.

| Scène proposée | Texte exact à l’écran |
|---|---|
| S1 · 0–6 s | **Lampe de bureau** |
| S2 · 6–14 s | **Tête orientable** |
| S3 · 14–21 s | Aucun texte : la main oriente la tête de la lampe. |
| S4 · 21–30 s | **7 500 F CFA**<br>**Boutique Démo · Akpakpa**<br>**Contacte-nous sur WhatsApp**<br>**+229 01 XX XX XX XX** |

Les quatre lignes finales restent immobiles de 22,3 à 29,3 s. Si le quartier est vide, la deuxième ligne devient uniquement « Boutique Démo ». Si une donnée obligatoire manque, indiquer la question à compléter avant de préparer le montage. Aucun CTA, script, décor, transition ou prompt à rédiger par le commerçant. Le montage utilise uniquement les réponses et les quatre prises ; il n’invente aucun avantage, tarif, lieu ni numéro. Pas de moteur, de police finale ou d’écran validé à cette étape.
