#!/usr/bin/env python
"""Non-recursive syntax compile for a Calibre plugin folder.

- Compiles all top-level .py files in the current folder
- Excludes this script itself
- Does NOT recurse into subfolders

Usage:
  python compile.py
"""

from __future__ import annotations

import os
import sys
import py_compile
from pathlib import Path


def iter_top_level_py_files(folder: Path) -> list[Path]:
    script_name = Path(__file__).name.casefold()
    out: list[Path] = []
    for p in folder.iterdir():
        if not p.is_file():
            continue
        if p.suffix.lower() != ".py":
            continue
        if p.name.casefold() == script_name:
            continue
        out.append(p)
    return sorted(out, key=lambda x: x.name.casefold())


def main(argv: list[str]) -> int:
    # Default to the folder this script lives in, so it works even when invoked
    # from other working directories.
    folder = Path(__file__).resolve().parent
    if len(argv) >= 2 and argv[1].strip():
        folder = Path(argv[1]).expanduser().resolve()

    files = iter_top_level_py_files(folder)
    if not files:
        print(f"No top-level .py files found in: {folder}")
        return 0

    failures: list[tuple[Path, str]] = []

    print(f"Compiling {len(files)} file(s) in: {folder}")
    for f in files:
        rel = f.name
        try:
            # Default behavior writes into __pycache__.
            py_compile.compile(str(f), doraise=True)
            print(f"  OK  {rel}")
        except py_compile.PyCompileError as e:
            msg = getattr(e, "msg", None) or str(e)
            failures.append((f, msg))
            print(f"  ERR {rel}")
            print(f"      {msg}")
        except Exception as e:
            failures.append((f, repr(e)))
            print(f"  ERR {rel}")
            print(f"      {e!r}")

    if failures:
        print("\nFailures:")
        for f, msg in failures:
            print(f"- {f.name}: {msg}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
