# anti-terminal

A retro CRT-terminal Hugo theme: amber/green/light phosphor modes, scanlines, live noise grain, an occasional sync-glitch, and a settings menu users can toggle (persisted in localStorage). No JS framework — vanilla JS + CSS variables.

## Use

```
hugo new site mysite
cd mysite
git submodule add https://github.com/you/anti-terminal themes/anti-terminal
cp themes/anti-terminal/exampleSite/hugo.toml .
cp -r themes/anti-terminal/exampleSite/content .
hugo server
```

Or just copy `exampleSite/` as your site root and set `theme = "anti-terminal"`.

## Structure

- `layouts/_default/baseof.html` — page shell: scanlines, noise layers, rail, footer
- `layouts/partials/header.html` — logo, live stats (uptime / cores / heap), nav terminal window, settings dropdown
- `layouts/index.html` — home template (renders `content/_index.md` + a card per top-level page)
- `layouts/_default/single.html` / `list.html` — generic page / section templates
- `static/css/theme.css` — all styling, driven by CSS vars swapped via `[data-mode]`
- `static/js/theme.js` — settings persistence, live stats, noise generation (canvas, not static images), random sync-glitch

## Site params (`hugo.toml` `[params]`)

- `logoText` — defaults to `!anti`
- `shortName` — used in the `~/<shortName> $` prompts
- `tagline`, `subtitle` — shown on the home page
- `footerText`
- `description`

## Menu

Nav items come from `[[menu.main]]` entries — add/remove/reorder there, no template edits needed. A `settings` item is appended automatically after the menu.

## Modes

Users can switch amber / green / light phosphor from the settings dropdown (bottom of the nav's `settings` menu). The choice, plus scanlines/noise/sync toggles, persist in `localStorage` under `anti-terminal-settings`.
