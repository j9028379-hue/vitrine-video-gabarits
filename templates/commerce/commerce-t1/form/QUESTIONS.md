# Les informations de ton commerce

Maquette de principe. Les six réponses sont obligatoires. Les exemples ne sont pas des valeurs par défaut. Le numéro masqué ne peut pas être validé.

| Question | Exemple | Clé | Dans Produit vedette |
|---|---|---|---|
| 1. Comment s'appelle ton commerce ? | Restaurant Chez Maman | `nom` | S1 et S4 · signature |
| 2. Qu'est-ce que tu veux présenter dans ta publicité ? | Riz au poulet, tresses, robe, sac... | `produit` | S1 · sous la signature |
| 3. Quel prix veux-tu afficher ? | 1 500 nairas | `prix` | S2 · seul après le message |
| 4. Qu'est-ce que tu veux dire aux clients ? | Disponible dès aujourd’hui ! | `accroche` | S2 · message avant le prix |
| 5. Où peut-on te trouver ? | Abomey-Calavi, Arconville | `quartier` | S4 · sous le nom |
| 6. Quel est ton numéro WhatsApp ? | +229 XX XX XX XX | `whatsapp` | S4 · contact final |

Le prix est un texte (32 caractères maximum) contenant un montant. La devise est facultative et jamais déduite : `1500`, `1 500 francs CFA`, `₦1,500`, `$15` ou `12,50 €` restent tels que saisis.

S3 est sans texte. [Essayer le formulaire](Formulaire-commerce.html).
