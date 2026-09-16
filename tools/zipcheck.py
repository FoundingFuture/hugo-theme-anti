#!/usr/bin/env python3
"""Check a release zip against package.txt.

The archive must hold one top-level directory named after the theme, every
path package.txt ships, and none it keeps. Hugo cannot read a zip, so the
directory name is what a reader ends up with under themes/.
"""

import argparse
import sys
import zipfile
from pathlib import Path


def lists(package):
    ship, keep = [], []
    for line in package.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("ship "):
            ship.append(line[5:])
        elif line.startswith("keep "):
            keep.append(line[5:])
    return ship, keep


def findings(zip_path, name, package):
    ship, keep = lists(package)
    if not ship:
        yield f"{package} ships nothing"
    names = zipfile.ZipFile(zip_path).namelist()
    roots = sorted({n.split("/")[0] for n in names})
    if roots != [name]:
        yield f"the zip holds {roots}, expected one directory named {name!r}"
        return
    inside = {n[len(name) + 1:].split("/")[0] for n in names if len(n) > len(name) + 1}
    for path in ship:
        if path not in inside:
            yield f"the zip is missing {path}"
    for path in keep:
        if path in inside:
            yield f"the zip carries {path}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", type=Path, required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--package", type=Path, required=True)
    args = ap.parse_args()

    found = list(findings(args.zip, args.name, args.package))
    for line in found:
        print(f"FAIL  {line}")
    if not found:
        print(f"PASS  {args.zip.name} installs as {args.name}/")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
