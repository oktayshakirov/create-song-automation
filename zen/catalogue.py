"""What is already on /zen: every album page, its store title, date and tracks.

    .venv/bin/python -m zen.catalogue

Reads `~/Coding/tinnitus-blog/content/zen/*.mdx`. The store title (what the
album is called on Spotify and DistroKid) often differs from the page's own
name: `--store` looks it up from Spotify's public oEmbed endpoint (the Apple
link slugs are wrong on two pages). Albums made here but not yet on the site
are listed from `zen/albums/`.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path

ZEN = Path("~/Coding/tinnitus-blog/content/zen").expanduser()
SPECS = Path(__file__).parent / "albums"


def main() -> None:
    pages = sorted(ZEN.glob("*.mdx"))
    live = set()
    for p in pages:
        s = p.read_text()
        live.add(p.stem)
        date = re.search(r"^date:\s*'?\"?([^'\"\n#]+)", s, re.M)
        spotify = re.search(r"open\.spotify\.com/album/(\w+)", s)
        # dict.fromkeys: a page with a band table names each track twice
        tracks = list(dict.fromkeys(re.findall(r"^\|\s*\*\*(.+?)\*\*\s*\|", s, re.M)))
        store = "-"
        if "--store" in sys.argv and spotify:
            url = ("https://open.spotify.com/oembed?url=https://open.spotify.com/album/"
                   + spotify.group(1))
            try:
                store = json.load(urllib.request.urlopen(url, timeout=10))["title"]
            except Exception:
                store = "?"
        print(f"/zen/{p.stem:18} {date.group(1).strip() if date else '?':18} "
              f"store: {store:22} {len(tracks)} tracks: {', '.join(tracks)}")

    print("\nMade here, not on the site yet:")
    for spec in sorted(SPECS.glob("*.py")):
        m = re.search(r'SITE_SLUG\s*=\s*"([^"]+)"', spec.read_text())
        if m and m.group(1) not in live:
            print(f"  {spec.stem} -> /zen/{m.group(1)}")


if __name__ == "__main__":
    main()
