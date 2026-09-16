# hugo-theme-anti

A Hugo theme that draws the site as a CRT terminal. It has amber, green and light phosphor modes, scanlines, animated noise grain and an occasional sync glitch. The reader switches each of them in a settings menu, and the browser keeps the choice in `localStorage`. The theme loads no JavaScript framework and requests nothing from another host.

## Requirements

- Hugo 0.158.0 or later. The standard edition builds it, extended is not needed.
- Python 3.11 or later, only for `./c check`.

## Installation

Download `hugo-theme-anti-vX.Y.Z.zip` from the [releases page](https://github.com/FoundingFuture/hugo-theme-anti/releases) and unzip it inside your site's `themes/` folder:

```sh
cd mysite
unzip ~/Downloads/hugo-theme-anti-v0.0.1.zip -d themes/
cp themes/hugo-theme-anti/exampleSite/hugo.toml .
cp -r themes/hugo-theme-anti/exampleSite/content .
hugo server
```

Hugo reads a theme from a directory, never from a zip file, and it finds the theme by that directory's name. The release zip holds one directory, `hugo-theme-anti`, so unzipping into `themes/` gives Hugo what it expects. Do not use GitHub's own "Source code" zip: it unpacks as `hugo-theme-anti-0.0.1`, a name Hugo does not match.

As a Git submodule instead:

```sh
git submodule add https://github.com/FoundingFuture/hugo-theme-anti.git themes/hugo-theme-anti
```

## Site configuration

### Line only the site can write

Hugo does not merge `markup` from a theme's configuration, so the site's `hugo.toml` carries this. `exampleSite/hugo.toml` has it.

```toml
[markup.highlight]
  noClasses = false
```

`noClasses = false` makes Chroma write token classes. The stylesheet colours those classes from the active phosphor mode. With Hugo's default, Chroma writes fixed inline colours instead.

### Parameters

All parameters sit under `[params]`.

| Parameter | Default | Effect |
|---|---|---|
| `logoText` | `!anti` | Text of the logo in the header |
| `shortName` | `anti` | Directory name in the `~/<shortName> $` prompts |
| `tagline` | home page title | The home page `h1` |
| `subtitle` | none | Line under the tagline |
| `description` | none | Meta description for pages without their own description or summary |
| `footerText` | `copyright`, then `© <year> <title>` | Footer line |

## Menu and home page

The menu lists the top-level directories under `content/`, followed by `settings`. `settings` belongs to the theme and has no directory. The home page renders `content/_index.md` under the tagline, then one card per directory in the same order as the menu.

- Order: directories whose `_index.md` sets `weight` come first, by weight. The rest follow by directory name, which also breaks ties between equal weights.
- Label: `linkTitle` from the directory's `_index.md`, else its `title`. A directory without `_index.md` shows its own name.
- Card: the label, the summary of `_index.md` when it has content, and a link to the directory.
- Marking: the directory's own page gets `aria-current="page"` on its item. Every page inside the directory gets `aria-current="true"` on the same item.
- `[[menus.main]]` in the site configuration is not read.

```toml
+++
title = "Documentation"
linkTitle = "docs"
weight = 20
+++
```

## Content

- A Markdown link such as `[build](/build/)` resolves to the page. When the site is served from a subpath, the link gets that subpath.
- Every page carries a canonical link, OpenGraph and Twitter card tags, and the RSS link where the page has a feed.

## Reader settings

The settings menu stores its state under the `localStorage` key `hugo-theme-anti-settings`. A script in `<head>` applies the stored values before the stylesheet loads, so a reader who picked green or light never sees an amber first paint.

When the system asks for reduced motion, the noise stops flickering, the cursor stops blinking and the sync glitch never runs. One still noise layer remains. The menu hides its settings button when JavaScript is off, because nothing could act on it.

## Customisation

- Put a `favicon.svg` in the site's `static/` folder to replace the theme's icon.
- Add `i18n/<language>.toml` with the ids from `i18n/en.toml` to translate the words the templates print.
- Copy any template to the same path under the site's `layouts/` to override it.

## Development

```sh
./c          # serve exampleSite at http://localhost:1313/ with live reload
./c build    # write the example site to dist/example-site/
./c check    # build the example site, a bare site and the fixtures, then run tools/check.py
./d vX.Y.Z --dry-run   # everything a release does, then undo it and stop
./d vX.Y.Z   # release: stamp, check, zip, commit, tag, push, publish
```

`./c check` builds every site under the base path `/sub/`, with every Hugo warning treated as an error. `tools/check.py` then reads the output and prints PASS or FAIL for each check.

`./d` stamps the version into `theme.toml` and the stylesheet before the checks run, so the gates read what will be tagged. It writes `dist/hugo-theme-anti-vX.Y.Z.zip`, checks it against `package.txt`, installs it into a throwaway site and builds that with plain `hugo`. Only then does it commit, tag, push and create the GitHub release. Any failure undoes the stamp and leaves no tag. The version needs a `## vX.Y.Z, YYYY-MM-DD` entry in `CHANGELOG.md`.

## Structure

| Path | Contents |
|---|---|
| `layouts/baseof.html` | Page shell, the reader settings and their defaults, overlays, script tag |
| `layouts/home.html` | Tagline, home page content, one card per directory |
| `layouts/single.html`, `layouts/list.html` | Regular pages, and sections and taxonomies |
| `layouts/_partials/head.html` | Settings script, meta tags, feed and canonical links, font preload, stylesheet |
| `layouts/_partials/header.html` | Logo, live stats, menu of directories, settings panel |
| `layouts/_partials/func/sections.html` | Top-level directories in menu order |
| `layouts/_partials/func/section-label.html` | A directory's menu and card label |
| `layouts/_partials/footer.html` | Footer line |
| `layouts/_partials/func/font-url.html` | Fingerprinted font URL for the preload and `@font-face` |
| `layouts/_markup/render-link.html` | Resolves Markdown links to pages and resources |
| `assets/css/theme.css` | All styling, with colours as custom properties per `data-mode` |
| `assets/js/theme.js` | Settings panel, live stats, noise tiles, sync glitch |
| `assets/fonts/jetbrains-mono.woff2` | JetBrains Mono, variable weight |
| `static/favicon.svg`, `static/fonts/OFL.txt` | Icon, font licence |
| `i18n/en.toml` | Words the templates print |
| `c`, `tools/check.py` | Serve, build and check the example site |
| `d`, `tools/zipcheck.py`, `package.txt` | Release: what ships, and the zip a reader installs |
| `CHANGELOG.md` | One entry per release |
| `tools/fixtures/sections/` | Content whose menu order and labels `tools/check.py` asserts |

## Fonts

`assets/fonts/jetbrains-mono.woff2` is JetBrains Mono 2.304 with the weight axis from 100 to 800. It is the release file `JetBrainsMono[wght].ttf` recompressed to WOFF2 without subsetting, 113 KB. The font is licensed under the SIL Open Font License 1.1, in `static/fonts/OFL.txt`.

## License

MIT, see `LICENSE`. The font keeps its own licence, described in [Fonts](#fonts).
