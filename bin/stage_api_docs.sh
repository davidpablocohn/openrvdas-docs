#!/usr/bin/env bash
# Stage the OpenRVDAS API reference into _site/api/ for local preview.
#
# The published site serves the pdoc-generated API reference at /api/, but that
# content lives in the OpenRVDAS source repo, not here -- the deploy workflow
# copies it into _site/ at build time (see .github/workflows/jekyll.yml).
# A local `jekyll build`/`serve` therefore leaves /api/ empty; run this script
# to fill it in.
#
# Usage:
#   ./bin/stage_api_docs.sh                     # use a local openrvdas checkout,
#                                               # falling back to a shallow clone
#   OPENRVDAS_SRC=~/openrvdas ./bin/stage_api_docs.sh
#
# `keep_files: [api]` in _config.yml keeps Jekyll from deleting the staged copy
# on rebuild, so this only needs to be run once per session.

set -euo pipefail

SITE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$SITE_ROOT/_site/api"

find_local_checkout() {
    local candidate
    for candidate in "${OPENRVDAS_SRC:-}" /opt/openrvdas "$HOME/openrvdas" "$SITE_ROOT/../openrvdas"; do
        [[ -n "$candidate" && -d "$candidate/docs/html" ]] && { echo "$candidate"; return 0; }
    done
    return 1
}

if SRC="$(find_local_checkout)"; then
    echo "Staging API docs from $SRC/docs/html"
    SRC_HTML="$SRC/docs/html"
    CLEANUP=""
else
    echo "No local openrvdas checkout found; fetching docs/html from GitHub..."
    CLEANUP="$(mktemp -d)"
    git clone --depth 1 --filter=blob:none --sparse \
        https://github.com/OceanDataTools/openrvdas.git "$CLEANUP/openrvdas" >/dev/null 2>&1
    git -C "$CLEANUP/openrvdas" sparse-checkout set docs/html >/dev/null
    SRC_HTML="$CLEANUP/openrvdas/docs/html"
fi

mkdir -p "$DEST"
cp -r "$SRC_HTML/." "$DEST/"
[[ -n "$CLEANUP" ]] && rm -rf "$CLEANUP"

echo "Done. Browse the API reference at http://localhost:4000/api/"
