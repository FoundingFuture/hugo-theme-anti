#!/usr/bin/env bash
# Validate the theme, write the release zip, tag and publish.
#
# Usage: ./d vX.Y.Z [--dry-run]
#
#   ./d v0.0.2             stamp, check, zip, commit, tag, push, release
#   ./d v0.0.2 --dry-run   everything up to the zip, then undo and stop
#
# The order matters. The version is stamped before the checks run, so
# the gates read the files exactly as they will be tagged. The commit,
# the tag and the push come last, and a failure leaves no tag behind.
#
# The zip is tested the way a reader installs it: unzipped into themes/
# of a site with no tooling, built with plain hugo. Hugo cannot read a
# zip, so the archive holds one directory named after the theme.

set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(pwd -P)"
NAME="$(sed -n 's|^module .*/||p' go.mod)"
OWNER="$(sed -n 's|^module github.com/\([^/]*\)/.*|\1|p' go.mod)"
[ -n "$NAME" ] && [ -n "$OWNER" ] || { echo "go.mod has no module path"; exit 2; }

VERSION="${1:-}"
DRY=0
[ "${2:-}" = "--dry-run" ] && DRY=1
case "$VERSION" in
  v[0-9]*.[0-9]*.[0-9]*) ;;
  *) echo "usage: ./d vX.Y.Z [--dry-run]"; exit 2 ;;
esac
NUMBER="${VERSION#v}"
ZIP="$ROOT/dist/$NAME-$VERSION.zip"

committed=0
tmp=""
restore() {
  [ "$committed" = "1" ] || git checkout -q -- theme.toml assets/css/theme.css
  [ -z "$tmp" ] || rm -rf "$tmp"
}
trap restore EXIT

fail() { [ "$committed" = "1" ] || rm -f "$ZIP"; echo "FAIL  $*"; exit 1; }
step() { echo "==  $*"; }
listed() { sed -n "s|^$1 ||p" package.txt; }

# --- refuse to start -------------------------------------------------
step "checking the repository"
[ "$(git rev-parse --abbrev-ref HEAD)" = "main" ] || fail "not on main"
[ -z "$(git status --porcelain)" ] || fail "the working tree has changes"
git fetch -q origin
[ "$(git rev-list --count HEAD..origin/main)" = "0" ] || fail "main is behind origin"
if git rev-parse -q --verify "refs/tags/$VERSION" >/dev/null; then
  fail "tag $VERSION exists here"
fi
[ -z "$(git ls-remote --tags origin "refs/tags/$VERSION")" ] || fail "tag $VERSION exists on origin"
grep -q "^## $VERSION, [0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}\$" CHANGELOG.md \
  || fail "CHANGELOG.md has no '## $VERSION, YYYY-MM-DD' entry"
if [ "$DRY" = "0" ]; then
  command -v gh >/dev/null 2>&1 || fail "gh not found"
  gh repo view "$OWNER/$NAME" >/dev/null 2>&1 || fail "gh cannot reach $OWNER/$NAME"
fi

# --- stamp -----------------------------------------------------------
# python3 rather than sed -i, whose argument differs between BSD and GNU.
step "stamping $VERSION"
python3 - "$NUMBER" "$NAME" "$VERSION" <<'PY'
import re, sys
number, name, version = sys.argv[1:4]
meta = open("theme.toml").read()
if re.search(r"(?m)^version = ", meta):
    meta = re.sub(r"(?m)^version = .*", f'version = "{number}"', meta)
else:
    meta = re.sub(r"(?m)^(min_version = .*)$", rf'\1\nversion = "{number}"', meta)
open("theme.toml", "w").write(meta)
css = open("assets/css/theme.css").read().split("\n")
css[0] = f"/* ===== {name} {version} ===== */"
open("assets/css/theme.css", "w").write("\n".join(css))
PY
grep -q "version = \"$NUMBER\"" theme.toml || fail "theme.toml was not stamped"
head -1 assets/css/theme.css | grep -q "$VERSION" || fail "the stylesheet was not stamped"

# --- checks ----------------------------------------------------------
step "running ./c check"
./c check

step "writing $ZIP"
tmp="$(mktemp -d)"
stage="$tmp/stage/$NAME"
mkdir -p "$stage" "$ROOT/dist"

# package.txt lists every root path as shipped or kept, so a new file
# cannot slip into the zip or go missing from it unnoticed.
for path in $(git ls-tree --name-only HEAD); do
  grep -q "^\(ship\|keep\) $path\$" package.txt || fail "package.txt does not list $path"
done
for path in $(listed ship); do
  [ -e "$path" ] || fail "package.txt ships $path, which does not exist"
  cp -R "$ROOT/$path" "$stage/$path"
done
rm -rf "$stage/exampleSite/public" "$stage/exampleSite/resources" "$stage/exampleSite/.hugo_build.lock"
rm -f "$ZIP"
(cd "$tmp/stage" && zip -qr "$ZIP" "$NAME")

step "checking the zip"
python3 tools/zipcheck.py --zip "$ZIP" --name "$NAME" --package package.txt || fail "the zip is wrong"

# The reader's own steps: unzip into themes/, copy the demo, build.
step "installing the zip into a site and building it"
site="$tmp/site"
mkdir -p "$site/themes"
(cd "$site/themes" && unzip -q "$ZIP")
cp -R "$site/themes/$NAME/exampleSite/." "$site/"
(cd "$site" && hugo --panicOnWarning --printI18nWarnings --logLevel warn >/dev/null)
[ -f "$site/public/index.html" ] || fail "the installed theme built no home page"
css="$(sed -n 's|.*<link rel="stylesheet" href="\([^"]*\)".*|\1|p' "$site/public/index.html")"
[ -n "$css" ] || fail "the installed page links no stylesheet"
[ -f "$site/public$css" ] || fail "the installed theme published no $css"

if [ "$DRY" = "1" ]; then
  echo
  echo "Dry run. $ZIP is written. Nothing was committed, tagged or pushed."
  exit 0
fi

# --- publish ---------------------------------------------------------
step "committing, tagging and pushing"
git add theme.toml assets/css/theme.css
git commit -q -m "Release $VERSION"
committed=1
git tag -a "$VERSION" -m "$NAME $VERSION"
git push -q --follow-tags origin main

step "creating the GitHub release"
notes="$tmp/notes.md"
awk -v v="## $VERSION," 'index($0,v)==1{f=1;next} f&&/^## v/{exit} f' CHANGELOG.md > "$notes"
gh release create "$VERSION" "$ZIP" --repo "$OWNER/$NAME" --title "$VERSION" --notes-file "$notes"

echo
echo "Released $VERSION. The zip is in dist/ and on the release page."
