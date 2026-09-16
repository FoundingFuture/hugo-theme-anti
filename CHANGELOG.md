# Changelog

## v0.0.1, 2026-09-16

The first release.

- A CRT terminal in three phosphor modes: amber, green and light. The
  reader switches mode, scanlines, noise and the sync glitch in the
  settings menu, and the browser keeps the choice. A script in the head
  applies it before the first paint.
- The menu lists the top-level directories under `content/`, ordered by
  `weight` and then by directory name, and labelled from `linkTitle` or
  `title`. The home page shows one card per directory in the same
  order. `settings` is the theme's own item and comes last.
- Nothing is requested from another host. JetBrains Mono ships with the
  theme as one variable WOFF2 covering weights 100 to 800. The
  stylesheet and script are fingerprinted and carry an integrity hash.
- Markdown content is styled in the active phosphor colours, Chroma
  tokens included. A site sets `markup.highlight.noClasses = false`,
  which only a site can write.
- Each page has one h1, a skip link, a canonical link, OpenGraph and
  Twitter card tags and an SVG favicon. The settings controls are
  buttons that work from the keyboard.
- Under `prefers-reduced-motion` nothing flickers, blinks or glitches.
- `./c check` builds the example site, a bare site and a fixture site
  under a subpath with warnings as errors, then reads the built pages.
