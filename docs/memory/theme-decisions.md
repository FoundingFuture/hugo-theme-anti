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

## Only the site can configure these

Hugo ignores `markup` and `menus` in a theme's `hugo.toml`. The README tells a site to write `markup.highlight.noClasses = false`, and to give menu entries a `pageRef`. The example site does both.

## Phone layout

Under 720px the header stops being sticky. Stacked, it measured 357px on an 844px-tall viewport. The settings panel also anchors to the menu window there, so it stays on screen wherever the menu wraps its button.

## What no automated check covers

`./c check` reads built HTML, so it cannot see these. They were checked by hand in Chrome on 2026-09-15:

- The saved mode applies before first paint.
- The settings panel works from the keyboard, and Escape returns focus to its button.
- Code blocks, tables, lists and quotes render in amber, green and light.
- The page does not scroll sideways at 390px.

Reduced motion was not checked in a browser, because the session tools could not emulate the media query. The rule exists in `theme.css`, and `./c check` confirms it is there.
