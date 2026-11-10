"""Check generated files and the append-only batch before publishing."""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = "https://dailywellnessnotes.github.io/notes"
SLOTS = (
    ("08:00:00", "kolajen"), ("11:00:00", "sac"), ("14:00:00", "stres"),
    ("17:00:00", "kolajen"), ("20:00:00", "sac"), ("23:00:00", "stres"),
)


def main() -> None:
    pins = json.loads((ROOT / "gecmis.json").read_text(encoding="utf-8"))["pinler"]
    if len(pins) != 42:
        raise ValueError(f"Expected 42 pins, found {len(pins)}")
    dates = sorted({p["tarih"][:10] for p in pins})
    first = date.fromisoformat(dates[0])
    if dates != [(first + timedelta(days=i)).isoformat() for i in range(7)]:
        raise ValueError("Scheduled days are not consecutive.")
    if Counter(p["urun"] for p in pins) != {"kolajen": 14, "sac": 14, "stres": 14}:
        raise ValueError("Product distribution is wrong.")
    for day in dates:
        slots = [(p["tarih"][11:], p["urun"]) for p in pins if p["tarih"].startswith(day)]
        if slots != list(SLOTS):
            raise ValueError(f"Wrong slots for {day}: {slots}")
    if len({p["id"] for p in pins}) != 42 or len({p["baslik"] for p in pins}) != 42:
        raise ValueError("Repeated IDs or titles.")
    if len({p["aciklama"] for p in pins}) != 42 or len({p["gorsel_sha256"] for p in pins}) != 42:
        raise ValueError("Repeated descriptions or image hashes.")
    if any("nplink.net" in p["link"] for p in pins):
        raise ValueError("A pin links directly to an affiliate destination.")
    last_link = defaultdict(lambda: None)
    for p in pins:
        if p["link"] == last_link[p["urun"]]:
            raise ValueError(f"Consecutive duplicate page for {p['urun']}")
        last_link[p["urun"]] = p["link"]
        image = ROOT / p["gorsel_dosya"]
        if not image.is_file():
            raise FileNotFoundError(image)
        digest = hashlib.sha256(image.read_bytes()).hexdigest()
        if digest != p["gorsel_sha256"]:
            raise ValueError(f"Hash mismatch: {image}")
        dims = subprocess.check_output(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height", "-of", "csv=p=0", str(image)],
            text=True,
        ).strip()
        if dims != "1000,1500":
            raise ValueError(f"Wrong image size: {image}: {dims}")
        if not 150 <= len(p["aciklama"]) <= 450 or not p["aciklama"].endswith("#affiliate"):
            raise ValueError(f"Invalid description: {p['id']}")
        if not p["aciklama"].startswith("Affiliate guide: I may earn a commission."):
            raise ValueError(f"Missing upfront disclosure: {p['id']}")
        if len(p["baslik"]) > 100 or len(p["baslik"].split()) > 6:
            raise ValueError(f"Invalid title: {p['id']}")
    articles = sorted((ROOT / "yazi").glob("*.html"))
    if len(articles) != 9:
        raise ValueError(f"Expected nine articles, found {len(articles)}")
    for article in articles:
        content = article.read_text(encoding="utf-8")
        if "This page contains affiliate links." not in content:
            raise ValueError(f"Missing affiliate disclosure: {article}")
        if content.count("affiliate-button") < 4:
            raise ValueError(f"Missing affiliate buttons: {article}")
        if "This content is for general information and is not medical advice." not in content:
            raise ValueError(f"Missing disclaimer: {article}")
    print(f"Validated 42 unique 1000×1500 JPG pins, 9 articles, and {dates[0]} through {dates[-1]} ET.")


if __name__ == "__main__":
    main()
