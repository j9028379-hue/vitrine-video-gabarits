#!/usr/bin/env bash
# Pilote autorisé : le rendu s’exécute sur GitHub. Ne sort le MP4 qu’après confirmation atomique.
set -euo pipefail
run=${1:?identifiant du run GitHub}; sortie=${2:?dossier de livraison}; gh=${GH:-gh}; repo=j9028379-hue/vitrine-video-gabarits
base=$(cd "$(dirname "$0")" && pwd); d=$(mktemp -d); trap 'rm -rf "$d"' EXIT
"$gh" run watch "$run" --repo "$repo" --interval 15 --exit-status
"$gh" run download "$run" --repo "$repo" --pattern 'COMMERCE-T1-sans-voix-*' --dir "$d"
mapfile -t rapports < <(find "$d" -type f -name CQ-pizza.json); [[ ${#rapports[@]} == 1 ]]; film=$(dirname "${rapports[0]}")
GH="$gh" python "$base/confirmer_rotation.py" "$film"; mkdir -p "$sortie"; cp "$film"/* "$sortie/"
