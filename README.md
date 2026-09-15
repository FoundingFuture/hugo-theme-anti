# hugo-theme-anti

A Hugo theme that draws the site as a CRT terminal. It has amber, green and light phosphor modes, scanlines, animated noise grain and an occasional sync glitch. The reader switches each of them in a settings menu, and the browser keeps the choice in `localStorage`. The theme loads no JavaScript framework and requests nothing from another host.

## Requirements

- Hugo 0.158.0 or later. The standard edition builds it, extended is not needed.
- Python 3.11 or later, only for `./c check`.

## Installation

```sh
hugo new site mysite
cd mysite
git init
git submodule add https://github.com/FoundingFuture/hugo-theme-anti.git themes/hugo-theme-anti
cp themes/hugo-theme-anti/exampleSite/hugo.toml .
cp -r themes/hugo-theme-anti/exampleSite/content .
hugo server
```

The folder under `themes/` has to be named `hugo-theme-anti`, because Hugo finds a theme by its folder name.

## Site configuration

### Lines only the site can write

Hugo does not merge `markup` or `menus` from a theme's configuration, so the site's `hugo.toml` carries these. `exampleSite/hugo.toml` has both.

```toml
[markup.highlight]
  noClasses = false

[[menus.main]]
  name = "about"
  pageRef = "/about"
  weight = 10
```

- `noClasses = false` makes Chroma write token classes. The stylesheet colours those classes from the active phosphor mode. With Hugo's default, Chroma writes fixed inline colours instead.
- `pageRef` ties a menu entry to a page. The menu marks the current page with `aria-current="page"` only for entries that use `pageRef`. An entry with `url` is never marked.

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
| `homeSections` | `["page"]` | Page types that get a card on the home page |

## Content

- The home page renders `content/_index.md` under the tagline. A card follows for every regular page whose type is listed in `homeSections`.
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
./c check    # build the example site and a bare site, then run tools/check.py
```

`./c check` builds both sites under the base path `/sub/`, with every Hugo warning treated as an error. `tools/check.py` then reads the output and prints PASS or FAIL for each check.

## Structure

| Path | Contents |
|---|---|
| `layouts/baseof.html` | Page shell, the reader settings and their defaults, overlays, script tag |
| `layouts/home.html` | Tagline, home page content, one card per page |
| `layouts/single.html`, `layouts/list.html` | Regular pages, and sections and taxonomies |
| `layouts/_partials/head.html` | Settings script, meta tags, feed and canonical links, font preload, stylesheet |
| `layouts/_partials/header.html` | Logo, live stats, menu window, settings panel |
| `layouts/_partials/footer.html` | Footer line |
| `layouts/_partials/func/font-url.html` | Fingerprinted font URL for the preload and `@font-face` |
| `layouts/_markup/render-link.html` | Resolves Markdown links to pages and resources |
| `assets/css/theme.css` | All styling, with colours as custom properties per `data-mode` |
| `assets/js/theme.js` | Settings panel, live stats, noise tiles, sync glitch |
| `assets/fonts/jetbrains-mono.woff2` | JetBrains Mono, variable weight |
| `static/favicon.svg`, `static/fonts/OFL.txt` | Icon, font licence |
| `i18n/en.toml` | Words the templates print |
| `c`, `tools/check.py` | Serve, build and check the example site |

## Fonts

`assets/fonts/jetbrains-mono.woff2` is JetBrains Mono 2.304 with the weight axis from 100 to 800. It is the release file `JetBrainsMono[wght].ttf` recompressed to WOFF2 without subsetting, 113 KB. The font is licensed under the SIL Open Font License 1.1, in `static/fonts/OFL.txt`.

## License

MIT, see `LICENSE`. The font keeps its own licence, described in [Fonts](#fonts).
