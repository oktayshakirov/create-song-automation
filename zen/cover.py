"""Album cover with the tinnitushelp.me promo bar, and the site image.

    .venv/bin/python -m zen.cover zen/albums/colors_of_calm.py

Reads `~/Desktop/<SLUG>/cover/square` and `.../landscape` (the user saves the
ChatGPT images there, any image format, with or without an extension) and
writes:

- `~/Desktop/<SLUG>/cover/<SLUG>-cover-3000.jpg`: 3000x3000 RGB JPEG with the
  bar, for DistroKid;
- `~/Coding/tinnitus-blog/public/images/<SITE_SLUG>.jpg`: 1200x800, no bar,
  quality 80 (~80 KB), for the /zen page.

The bar is measured off an existing cover (Jungle Stillness at 800 px) and
scaled, not eyeballed: black, 42/800 of the height, `www.tinnitushelp.me` in
Courier New regular, grey 214, the text running from x 103 to 691 of 800 with
its x-height centred on row 23.5. Glyph start positions came out within 1 px
of the reference, and the last glyph ends at 687 against 691 (the reference
is a soft, upscaled webp, so its edges measure wider). A stroke made the text too heavy (ink 2526 and 3049 px against the
reference's 2031), so there is none.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from zen.album import load_spec

FONT = "/System/Library/Fonts/Supplemental/Courier New.ttf"
TEXT = "www.tinnitushelp.me"
GREY = (214, 214, 214)
REF = 800                                   # the reference cover's size
BAR, X0, X1, XMID = 42, 103, 691, 23.5      # in reference pixels
SITE = Path("~/Coding/tinnitus-blog/public/images").expanduser()


def add_bar(img: Image.Image) -> Image.Image:
    W = img.width
    k = W / REF
    f = ImageFont.truetype(FONT, round(159 * W / 3000))
    widths = [f.getlength(c) for c in TEXT]
    first_l, last_r = f.getbbox(TEXT[0])[0], f.getbbox(TEXT[-1])[2]
    track = ((X1 - X0) * k - (sum(widths[:-1]) - first_l + last_r)) / (len(TEXT) - 1)
    wt, wb = f.getbbox("w")[1], f.getbbox("w")[3]
    x, y = X0 * k - first_l, XMID * k - (wt + wb) / 2
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, round(BAR * k) - 1], fill=(0, 0, 0))
    for c, w in zip(TEXT, widths):
        d.text((x, y), c, font=f, fill=GREY)
        x += w + track
    return img


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", type=Path)
    a = ap.parse_args()
    spec = load_spec(a.spec)
    d = Path(f"~/Desktop/{spec.SLUG}/cover").expanduser()
    src = lambda stem: next(p for p in d.iterdir() if p.stem == stem)

    sq = Image.open(src("square")).convert("RGB")
    if sq.width != sq.height:
        raise SystemExit(f"square is {sq.width}x{sq.height}, not square")
    cover = add_bar(sq.resize((3000, 3000), Image.LANCZOS))
    out = d / f"{spec.SLUG}-cover-3000.jpg"
    cover.save(out, quality=95, subsampling=0)
    print(out)

    ls = Image.open(src("landscape")).convert("RGB")
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
