"""Album cover for DistroKid, and the site image.

    .venv/bin/python -m zen.cover zen/albums/colors_of_calm.py

Reads `~/Desktop/<SLUG>/cover/square` and `.../landscape` (the user saves the
ChatGPT images there, any image format, with or without an extension) and
writes:

- `~/Desktop/<SLUG>/cover/<SLUG>-cover-3000.jpg`: 3000x3000 RGB JPEG, the
  picture alone, for DistroKid;
- `~/Coding/tinnitus-blog/public/images/<SITE_SLUG>.jpg`: 1200x800, quality
  80 (~80 KB), for the /zen page.

No text goes on the cover. Albums up to Colors of Calm carried a black
`www.tinnitushelp.me` bar on top; stores reject artwork with a URL in it and
the last one was rejected for it, so the bar was dropped (2026-11-22).
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from zen.album import load_spec

SITE = Path("~/Coding/tinnitus-blog/public/images").expanduser()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", type=Path)
    a = ap.parse_args()
    spec = load_spec(a.spec)
    d = Path(f"~/Desktop/{spec.SLUG}/cover").expanduser()
    src = lambda stem: next((p for p in d.iterdir() if p.stem == stem), None)

    sq = Image.open(src("square")).convert("RGB")
    if sq.width != sq.height:
        raise SystemExit(f"square is {sq.width}x{sq.height}, not square")
    cover = sq.resize((3000, 3000), Image.LANCZOS)
    out = d / f"{spec.SLUG}-cover-3000.jpg"
    cover.save(out, quality=95, subsampling=0)
    print(out)

    # No landscape (Breath and Bell, 2026-11-22: only the square came back):
    # centre-crop the square to 3:2. Fine when the subject sits mid-height,
    # as the prompt asks; the ChatGPT extension keeps more of the scene.
    if src("landscape") is None:
        print("no landscape: cropping the square to 3:2 for the site image")
    ls = Image.open(src("landscape") or src("square")).convert("RGB")
    w, h = ls.size
    if abs(w / h - 1.5) > 0.01:            # centre-crop to 3:2
        nw, nh = (round(h * 1.5), h) if w / h > 1.5 else (w, round(w / 1.5))
        ls = ls.crop(((w - nw) // 2, (h - nh) // 2, (w + nw) // 2, (h + nh) // 2))
    site = SITE / f"{spec.SITE_SLUG}.jpg"
    ls.resize((1200, 800), Image.LANCZOS).save(site, quality=80, optimize=True,
                                               progressive=True)
    print(site, f"{site.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
