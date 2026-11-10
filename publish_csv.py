"""Write the Pinterest upload CSV only after every published URL is live."""

from __future__ import annotations

import csv
import json
import shutil
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = "https://dailywellnessnotes.github.io/notes"
DEST = Path(r"C:\Users\ik_ej\Documents\pinterest-csv")
BOARD = {
    "kolajen": "Glow Skin Routine Ideas",
    "sac": "Healthy Hair Care Tips",
    "stres": "Calm Evening Rituals",
}
HEADERS = (
    "Title", "Media URL", "Pinterest board", "Thumbnail",
    "Description", "Link", "Publish date", "Keywords",
)


def check_url(url: str) -> tuple[str, str | None]:
    try:
        request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(request, timeout=20) as response:
            kind = response.headers.get("Content-Type", "").split(";", 1)[0]
            if response.status != 200:
                return url, f"HTTP {response.status}"
            if url.endswith(".jpg") and kind != "image/jpeg":
                return url, f"unexpected content type {kind}"
            if url.endswith(".html") and kind != "text/html":
                return url, f"unexpected content type {kind}"
            return url, None
    except Exception as exc:
        return url, str(exc)


def main() -> None:
    history = json.loads((ROOT / "gecmis.json").read_text(encoding="utf-8"))["pinler"]
    if not history:
        raise ValueError("No pins in history.")
    csv_rel = history[-1]["csv_dosyasi"]
    batch = [p for p in history if p["csv_dosyasi"] == csv_rel]
    if len(batch) != 42:
        raise ValueError(f"Expected 42 pins for {csv_rel}, found {len(batch)}")
    urls = {f"{SITE}/{p['gorsel_dosya']}" for p in batch}
    urls.update(p["link"] for p in batch)
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(check_url, sorted(urls)))
    errors = [(url, issue) for url, issue in results if issue]
    if errors:
        for url, issue in errors:
            print(f"NOT LIVE: {url}: {issue}")
        raise SystemExit(f"{len(errors)} URLs are not live; CSV was not written.")
    path = ROOT / csv_rel
    path.parent.mkdir(exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(HEADERS)
        for p in batch:
            writer.writerow((
                p["baslik"],
                f"{SITE}/{p['gorsel_dosya']}",
                BOARD[p["urun"]],
                "",
                p["aciklama"],
                p["link"],
                p["tarih"],
                ", ".join(p["keywords"]),
            ))
    DEST.mkdir(exist_ok=True)
    shutil.copy2(path, DEST / path.name)
    print(f"Verified {len(urls)} URLs and wrote {len(batch)} pins to {path}")
    print(f"Copied to {DEST / path.name}")


if __name__ == "__main__":
    main()
