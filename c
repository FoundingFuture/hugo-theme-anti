#!/usr/bin/env bash
# Serve, build or check the example site against this checkout.
#
# Usage: ./c [serve|build|check] [hugo options]
#
#   ./c            same as ./c serve
#   ./c serve      hugo server on exampleSite with live reload, http://localhost:1313/
#   ./c build      static example site in dist/example-site/
#   ./c check      build the example site and a bare site, then run tools/check.py on both
#
# Hugo finds a theme by its folder name, and a clone can sit in a folder with
# any name. Link the checkout into a temporary themes directory under the name
# go.mod gives the module, so the name has one definition.

set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(pwd -P)"
SITE="$ROOT/exampleSite"
# Serve the checks from a subpath so a link that ignores baseURL breaks here.
CHECK_BASE="https://example.org/sub/"

command -v hugo >/dev/null 2>&1 || { echo "hugo not found"; exit 3; }
[ -f go.mod ] || { echo "go.mod not found, and the theme name comes from it"; exit 2; }
NAME="$(sed -n 's|^module .*/||p' go.mod)"
[ -n "$NAME" ] || { echo "go.mod has no module path"; exit 2; }

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
mkdir "$tmp/themes"
ln -s "$ROOT" "$tmp/themes/$NAME"

verb="${1:-serve}"
[ $# -gt 0 ] && shift

case "$verb" in
  serve)
    exec hugo server -s "$SITE" --themesDir "$tmp/themes" --theme "$NAME" \
      --disableFastRender "$@"
    ;;
  build)
    out="$ROOT/dist/example-site"
    rm -rf "$out"
    hugo -s "$SITE" --themesDir "$tmp/themes" --theme "$NAME" -d "$out" --gc "$@"
    echo "Static site in dist/example-site"
    ;;
  check)
    command -v python3 >/dev/null 2>&1 || { echo "python3 not found"; exit 3; }
    # Warnings fail the build: deprecations and missing i18n keys included.
    strict=(--panicOnWarning --printI18nWarnings --logLevel warn)

    hugo -s "$SITE" --themesDir "$tmp/themes" --theme "$NAME" \
      -d "$tmp/example" --baseURL "$CHECK_BASE" --cacheDir "$tmp/cache" "${strict[@]}" "$@"

    mkdir "$tmp/bare"
    printf 'title = "Bare"\n' > "$tmp/bare/hugo.toml"
    hugo -s "$tmp/bare" --themesDir "$tmp/themes" --theme "$NAME" \
      -d "$tmp/bare-public" --baseURL "$CHECK_BASE" --cacheDir "$tmp/cache" "${strict[@]}" "$@"

    python3 tools/check.py --repo "$ROOT" --name "$NAME" --base "$CHECK_BASE" \
      --example "$tmp/example" --bare "$tmp/bare-public"
    ;;
  *)
    echo "usage: ./c [serve|build|check] [hugo options]"
    exit 2
    ;;
esac
