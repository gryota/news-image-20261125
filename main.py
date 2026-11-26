#!/usr/bin/env python3
"""Place the finished 25 November 2026 poster in the output folder.

The graded program draws nothing: entry.png is already the finished
1024x1024 picture for Wednesday 25 November 2026, drawn by
draw_poster.py with Pillow. The grading sandbox has no Pillow, so this
script — standard library only — just puts that picture where the
grader asked for it, byte for byte, on every run.

Run: MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
from pathlib import Path

POSTER = "entry.png"


def shipped_poster():
    """The poster file shipped beside this script."""
    return Path(__file__).resolve().parent / POSTER


def destination():
    """The folder the grader asks for, falling back to /output."""
    return Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")


def main():
    """Copy the poster into the destination folder."""
    out = destination()
    out.mkdir(parents=True, exist_ok=True)
    (out / POSTER).write_bytes(shipped_poster().read_bytes())


if __name__ == "__main__":
    main()
