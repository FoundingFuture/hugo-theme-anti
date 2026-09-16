# Theme decisions

Decisions taken on 2026-09-15, when the theme moved into this repository.

## Name and home

- The repository is `github.com/FoundingFuture/hugo-theme-anti`. Commits use `eddie@foundingfuture.com`.
- The theme is called `hugo-theme-anti` everywhere Hugo reads a name. `theme.toml` shows the display name `anti`. The earlier name `anti-terminal` is gone.
- `go.mod` holds the one definition of the name. `./c` reads it from there, and `./c check` fails when `exampleSite/hugo.toml` or `theme.toml` disagree.

## Hugo floor

`hugo.toml` and `theme.toml` both say 0.158.0. That release added the `locale` setting and `site.Language.Locale`, which the theme and the example site use. No older Hugo was tried.

## Font

The owner chose to self-host JetBrains Mono instead of loading it from Google Fonts.

- The file is the full glyph set, not a Latin subset. The theme prints U+2192 in "read more", and Google's Latin subset omits that glyph. Box-drawing characters suit terminal content too.
- The JetBrains release ships the variable font only as TTF. The WOFF2 came from fontTools 4.65 with brotli, with no subsetting:

```python
from fontTools.ttLib import TTFont
f = TTFont("JetBrainsMono[wght].ttf")
f.flavor = "woff2"
f.save("jetbrains-mono.woff2")
```

## Configuration only the site can write

Hugo ignores `markup` in a theme's `hugo.toml`. The README tells a site to write `markup.highlight.noClasses = false`, and the example site does.

## Menu from content directories

The owner decided the menu comes from the top-level content directories, not from `[[menus.main]]`, which the theme does not read. `settings` is theme configuration with no directory, so the theme always renders it last.

- The label is `linkTitle`, else `title`, else the directory name. Without the last fallback Hugo invents a title, such as "Bravoes" for a directory named `bravo`.
- Order is weight first, then directory name. `func/sections.html` relies on `sort` being stable to break weight ties by name. The `alpha` and `mid` directories in `tools/fixtures/sections/` fail the check if it is not.
- The home cards read the same partial, so the menu and the cards cannot disagree.

## Releasing

`./d vX.Y.Z` is the only way a release is made. Push the tag with the commits, which `--follow-tags` does, rather than leaving it on the machine.

Hugo cannot read a zip. A site with `themes/hugo-theme-anti.zip` fails with `module "hugo-theme-anti" not found`, and the same site builds once the file is unzipped. So the archive carries one directory named `hugo-theme-anti`, and `./d` proves it by unzipping into a throwaway site and building with plain `hugo`. GitHub's generated source zip unpacks as `hugo-theme-anti-<version>`, which is why the release attaches its own.

The version is stamped before the gates run, so the checks read the files as they will be tagged. Commit, tag and push happen last, and a failure restores the tree and leaves no tag.

## Phone layout

Under 720px the header stops being sticky. Stacked, it measured 357px on an 844px-tall viewport. The settings panel also anchors to the menu window there, so it stays on screen wherever the menu wraps its button.

## What no automated check covers

`./c check` reads built HTML, so it cannot see these. They were checked by hand in Chrome on 2026-09-15:

- The saved mode applies before first paint.
- The settings panel works from the keyboard, and Escape returns focus to its button.
- Code blocks, tables, lists and quotes render in amber, green and light.
- The page does not scroll sideways at 390px.

Reduced motion was not checked in a browser, because the session tools could not emulate the media query. The rule exists in `theme.css`, and `./c check` confirms it is there.
