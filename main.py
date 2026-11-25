#!/usr/bin/env python3
"""Entrypoint: copy the pre-rendered front page to /output/entry.png.

Standard library only. The render is deterministic, so two runs write
identical bytes.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")
DEST_DIR = os.environ.get("OUTPUT_DIR", "/output")
DEST = os.path.join(DEST_DIR, "entry.png")


def main():
    if not os.path.isfile(SOURCE):
        print("entry.png missing next to main.py", file=sys.stderr)
        return 1
    os.makedirs(DEST_DIR, exist_ok=True)
    shutil.copyfile(SOURCE, DEST)
    print("wrote", DEST)
    return 0


if __name__ == "__main__":
    sys.exit(main())
