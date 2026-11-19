# Couche commune Cloudflare — hors du gabarit

Worker sans bindings de production, en lecture seule. `GET /v1/catalogue` lit le catalogue versionné au build ; `GET /v1/health` indique le profil. L’identité/version du gabarit est la clé logique d’attribution. Pas de compte, route de domaine, bucket, jeton, téléchargement OTA ou appels sortants. Aucun rendu FFmpeg dans le Worker. Les écritures (y compris les jobs des commerçants) sont refusées.

Tester sans compte : `node test.mjs`, puis `npx --yes wrangler@4.45.0 deploy --dry-run --outdir /tmp/vitrine-worker`. Ne pas retirer `--dry-run`. Le test confirme le bundling et les handlers, pas la disponibilité d’un service distant. Une intégration future devra définir authentification, stockage, idempotence durable, dispatch GitHub avec callback authentifié et signature des manifests ; secrets exclusivement dans le gestionnaire de secrets. Ces fonctions ne sont ni simulées comme réussies ni accessibles publiquement dans cette version.
