#!/usr/bin/env python3
"""Check the built example site, a bare site and the repo metadata.

Run through ./c check, which builds both sites first. Each check prints PASS or
FAIL with its findings. The exit code is 1 when any check fails.
"""

import argparse
import re
import sys
import tomllib
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit

VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "source", "track", "wbr",
}
FOCUSABLE = {"a", "button", "input", "select", "textarea"}


class Element:
    def __init__(self, tag, attrs, ancestors, index):
        self.tag = tag
        self.attrs = {k: (v if v is not None else "") for k, v in attrs}
        self.ancestors = ancestors
        self.index = index
        self.text = ""

    def within(self, tag):
        return tag in self.ancestors


class Page(HTMLParser):
    """Parse one HTML file into a flat list of elements in document order."""

    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.elements = []
        self._stack = []
        self._open = []
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attrs):
        el = Element(tag, attrs, tuple(self._stack), len(self.elements))
        self.elements.append(el)
        if tag not in VOID:
            self._stack.append(tag)
            self._open.append(el)

    def handle_startendtag(self, tag, attrs):
        self.elements.append(Element(tag, attrs, tuple(self._stack), len(self.elements)))

    def handle_endtag(self, tag):
        if tag in self._stack:
            while self._stack:
                self._open.pop()
                if self._stack.pop() == tag:
                    break

    def handle_data(self, data):
        if self._open:
            self._open[-1].text += data

    def all(self, tag=None, **attrs):
        out = []
        for el in self.elements:
            if tag and el.tag != tag:
                continue
            if all(el.attrs.get(k.replace("_", "-")) == v for k, v in attrs.items()):
                out.append(el)
        return out

    def ids(self):
        return [el.attrs["id"] for el in self.elements if "id" in el.attrs]


class Report:
    def __init__(self):
        self.failed = False

    def run(self, name, findings):
        findings = list(findings)
        if findings:
            self.failed = True
            print(f"FAIL  {name}")
            for f in findings[:12]:
                print(f"      {f}")
            if len(findings) > 12:
                print(f"      and {len(findings) - 12} more")
        else:
            print(f"PASS  {name}")


def pages(public):
    return sorted(public.rglob("*.html"))


def page_url(public, base, path):
    rel = path.relative_to(public).as_posix()
    if rel.endswith("index.html"):
        rel = rel[: -len("index.html")]
    return urljoin(base, rel)


def resolve(public, base, url):
    """Return the built file an internal URL points at, or None."""
    path = urlsplit(url).path
    base_path = urlsplit(base).path
    if not path.startswith(base_path):
        return None
    rel = path[len(base_path):]
    target = public / rel
    if rel == "" or rel.endswith("/"):
        target = target / "index.html"
    elif target.is_dir():
        target = target / "index.html"
    return target if target.is_file() else None


def one_h1(site):
    for path, page in site:
        count = len(page.all("h1"))
        if count != 1:
            yield f"{rel_name(site, path)}: {count} h1 elements"


def ids_valid(site):
    for path, page in site:
        ids = page.ids()
        if "" in ids:
            yield f"{rel_name(site, path)}: empty id"
        dupes = sorted({i for i in ids if i and ids.count(i) > 1})
        if dupes:
            yield f"{rel_name(site, path)}: duplicate ids {dupes}"


def no_inline_style(site):
    for path, page in site:
        styled = [el.tag for el in page.elements if "style" in el.attrs]
        if styled:
            yield f"{rel_name(site, path)}: style attribute on {sorted(set(styled))}"


def html_lang(site):
    for path, page in site:
        html = page.all("html")
        if not html or not html[0].attrs.get("lang"):
            yield f"{rel_name(site, path)}: html has no lang"


def head_links(site, want_description):
    for path, page in site:
        name = rel_name(site, path)
        head = [el for el in page.elements if el.within("head")]
        rels = {el.attrs.get("rel") for el in head if el.tag == "link"}
        for rel in ("canonical", "icon"):
            if rel not in rels:
                yield f"{name}: no link rel={rel}"
        if not any(el.attrs.get("property") == "og:title" for el in head):
            yield f"{name}: no og:title"
        if want_description:
            desc = [el for el in head if el.attrs.get("name") == "description"]
            if not desc or not desc[0].attrs.get("content", "").strip():
                yield f"{name}: no meta description"


def home_feed(public, base):
    page = Page(public / "index.html")
    feeds = [el for el in page.all("link", rel="alternate")
             if el.attrs.get("type") == "application/rss+xml"]
    if not feeds:
        yield "home page has no RSS link rel=alternate"
    for el in feeds:
        if resolve(public, base, el.attrs.get("href", "")) is None:
            yield f"RSS link does not resolve: {el.attrs.get('href')}"


def links_resolve(site, public, base):
    host = urlsplit(base).netloc
    for path, page in site:
        name = rel_name(site, path)
        here = page_url(public, base, path)
        for el in page.elements:
            attr = "href" if el.tag in ("a", "link") else "src" if el.tag in ("script", "img", "source") else None
            if not attr or attr not in el.attrs:
                continue
            raw = el.attrs[attr]
            if el.tag == "a" and raw.startswith("#"):
                if raw == "#" or raw[1:] not in page.ids():
                    yield f"{name}: fragment {raw!r} names no element"
                continue
            parts = urlsplit(raw)
            if parts.scheme in ("mailto", "tel", "data"):
                continue
            if parts.netloc and parts.netloc != host:
                if el.tag != "a":
                    yield f"{name}: <{el.tag}> requests another host: {raw}"
                continue
            url = urljoin(here, raw)
            if resolve(public, base, url) is None:
                yield f"{name}: <{el.tag} {attr}={raw!r}> does not resolve under {urlsplit(base).path}"


def menu_current(site, public, base):
    for path, page in site:
        name = rel_name(site, path)
        here = urlsplit(page_url(public, base, path)).path
        navs = page.all("nav")
        if not navs:
            yield f"{name}: no nav element"
            continue
        links = [el for el in page.elements if el.tag == "a" and el.within("nav")]
        if not links:
            yield f"{name}: nav holds no links"
        for a in links:
            target = urlsplit(urljoin(page_url(public, base, path), a.attrs.get("href", ""))).path
            current = a.attrs.get("aria-current") == "page"
            if target == here and not current:
                yield f"{name}: menu link to this page has no aria-current=page"
            if current and target != here:
                yield f"{name}: aria-current=page on a link to {target}"


def assets_fingerprinted(site):
    path, page = site[0]
    sheets = page.all("link", rel="stylesheet")
    scripts = [el for el in page.all("script") if el.attrs.get("src")]
    if not sheets:
        yield "no stylesheet link"
    for el in sheets + scripts:
        url = el.attrs.get("href") or el.attrs.get("src")
        if not re.search(r"\.[0-9a-f]{16,}\.(css|js)$", url):
            yield f"not fingerprinted: {url}"
        if not el.attrs.get("integrity"):
            yield f"no integrity attribute: {url}"


def mode_before_paint(site):
    for path, page in site:
        head = [el for el in page.elements if el.within("head")]
        first_sheet = next((el.index for el in head if el.tag == "link" and el.attrs.get("rel") == "stylesheet"), None)
        inline = [el for el in head if el.tag == "script" and not el.attrs.get("src") and "localStorage" in el.text]
        if first_sheet is None or not inline or inline[0].index > first_sheet:
            yield f"{rel_name(site, path)}: no inline settings script ahead of the stylesheet"


def settings_controls(site):
    for path, page in site:
        name = rel_name(site, path)
        ids = page.ids()
        toggles = [el for el in page.elements if "data-settings-toggle" in el.attrs]
        if not toggles:
            yield f"{name}: no settings toggle"
        for el in toggles:
            if el.tag != "button" or el.attrs.get("type") != "button":
                yield f"{name}: settings toggle is <{el.tag}>, not a button"
            if el.attrs.get("aria-expanded") not in ("true", "false"):
                yield f"{name}: settings toggle has no aria-expanded"
            if el.attrs.get("aria-controls") not in ids:
                yield f"{name}: settings toggle aria-controls names no element"
        rows = [el for el in page.elements if "data-toggle" in el.attrs or "data-set-mode" in el.attrs]
        if not rows:
            yield f"{name}: no settings rows"
        for el in rows:
            if el.tag != "button" or el.attrs.get("type") != "button":
                yield f"{name}: settings row is <{el.tag}>, not a button"
            if el.attrs.get("aria-pressed") not in ("true", "false"):
                yield f"{name}: settings row has no aria-pressed"


def skip_link(site):
    for path, page in site:
        name = rel_name(site, path)
        body = [el for el in page.elements if el.within("body") and el.tag in FOCUSABLE]
        if not body or body[0].tag != "a" or body[0].attrs.get("href") != "#main":
            yield f"{name}: first focusable element is not a skip link to #main"
        mains = page.all("main")
        if len(mains) != 1 or mains[0].attrs.get("id") != "main":
            yield f"{name}: no single <main id=main>"


def css_files(public):
    return sorted(public.rglob("*.css"))


def fonts_local(public, base):
    sheets = css_files(public)
    if not sheets:
        yield "no stylesheet in the build"
    faces = 0
    for css in sheets:
        text = css.read_text(encoding="utf-8")
        if re.search(r"@import|url\(\s*['\"]?(https?:)?//", text):
            yield f"{css.name}: loads from another host"
        css_url = urljoin(base, css.relative_to(public).as_posix())
        for block in re.findall(r"@font-face\s*\{[^}]*\}", text):
            faces += 1
            for url in re.findall(r"url\(\s*['\"]?([^'\")]+)", block):
                if resolve(public, base, urljoin(css_url, url)) is None:
                    yield f"{css.name}: font {url} is not in the build"
    if sheets and faces == 0:
        yield "no @font-face in the stylesheet"


def reduced_motion(public):
    text = "".join(css.read_text(encoding="utf-8") for css in css_files(public))
    if not re.search(r"prefers-reduced-motion:\s*reduce", text):
        yield "stylesheet has no prefers-reduced-motion: reduce rule"


def no_site_copy(public):
    for path in sorted(public.rglob("*")):
        if path.is_file() and path.suffix in (".html", ".xml", ".css", ".js"):
            if "antic" in path.read_text(encoding="utf-8"):
                yield f"{path.relative_to(public)}: the theme prints the example site's copy"


def name_seams(repo, name):
    gomod = (repo / "go.mod").read_text(encoding="utf-8") if (repo / "go.mod").is_file() else ""
    if f"module github.com/FoundingFuture/{name}" not in gomod:
        yield f"go.mod module is not github.com/FoundingFuture/{name}"
    site = tomllib.loads((repo / "exampleSite/hugo.toml").read_text(encoding="utf-8"))
    if site.get("theme") != name:
        yield f"exampleSite theme is {site.get('theme')!r}, the module is {name!r}"
    meta = tomllib.loads((repo / "theme.toml").read_text(encoding="utf-8"))
    for key in ("homepage", "licenselink"):
        if f"FoundingFuture/{name}" not in meta.get(key, ""):
            yield f"theme.toml {key} does not name FoundingFuture/{name}"
    config = repo / "hugo.toml"
    minimum = None
    if config.is_file():
        minimum = tomllib.loads(config.read_text(encoding="utf-8")).get("module", {}).get("hugoVersion", {}).get("min")
    if not minimum:
        yield "hugo.toml has no module.hugoVersion.min"
    elif meta.get("min_version") != minimum:
        yield f"theme.toml min_version {meta.get('min_version')!r} differs from hugo.toml {minimum!r}"


def rel_name(site, path):
    root = site.root
    rel = path.relative_to(root).as_posix()
    return "/" + rel[: -len("index.html")] if rel.endswith("index.html") else "/" + rel


class Site(list):
    def __init__(self, public):
        super().__init__((p, Page(p)) for p in pages(public))
        self.root = public


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--example", type=Path, required=True)
    ap.add_argument("--bare", type=Path, required=True)
    args = ap.parse_args()

    report = Report()
    report.run("repo: theme name and Hugo version agree", name_seams(args.repo, args.name))

    for label, public, full in (("example", args.example, True), ("bare", args.bare, False)):
        site = Site(public)
        report.run(f"{label}: one h1 per page", one_h1(site))
        report.run(f"{label}: ids are non-empty and unique", ids_valid(site))
        report.run(f"{label}: no style attributes", no_inline_style(site))
        report.run(f"{label}: html lang", html_lang(site))
        report.run(f"{label}: head carries canonical, icon, og:title", head_links(site, want_description=full))
        report.run(f"{label}: home page links its RSS feed", home_feed(public, args.base))
        report.run(f"{label}: links and assets resolve under the base path", links_resolve(site, public, args.base))
        report.run(f"{label}: assets fingerprinted with integrity", assets_fingerprinted(site))
        report.run(f"{label}: saved mode applied before the stylesheet", mode_before_paint(site))
        report.run(f"{label}: settings controls are buttons with state", settings_controls(site))
        report.run(f"{label}: skip link to main", skip_link(site))
        report.run(f"{label}: fonts served from the site", fonts_local(public, args.base))
        report.run(f"{label}: reduced motion honoured", reduced_motion(public))
        if full:
            report.run(f"{label}: menu marks the current page", menu_current(site, public, args.base))
        else:
            report.run(f"{label}: no example-site copy in the theme", no_site_copy(public))

    return 1 if report.failed else 0


if __name__ == "__main__":
    sys.exit(main())
