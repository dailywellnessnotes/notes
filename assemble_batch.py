"""Turn generated pin art into a seven-day schedule and append-only history."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import date, datetime, timedelta
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = "https://dailywellnessnotes.github.io/notes"
PRODUCTS = ("kolajen", "sac", "stres")
SLOTS = (
    ("08:00:00", "kolajen"),
    ("11:00:00", "sac"),
    ("14:00:00", "stres"),
    ("17:00:00", "kolajen"),
    ("20:00:00", "sac"),
    ("23:00:00", "stres"),
)
PAGES = {
    "kolajen": ("morning-skin-ritual", "evening-skin-reset", "weekend-glow-habits"),
    "sac": ("gentle-wash-day", "night-hair-ritual", "scalp-care-pause"),
    "stres": ("calm-evening-ritual", "screen-free-reset", "slow-sunday-plan"),
}
KEYWORDS = {
    "kolajen": ("skin care ideas", "simple skincare", "self care routine"),
    "sac": ("hair care tips", "hair routine", "self care ideas"),
    "stres": ("slow living", "evening routine", "self care ideas"),
}


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", text.lower()).strip()


def prompt(spec: dict) -> str:
    if spec["product"] == "sac" and spec["index"] == 1:
        return (
            "Create one complete 2:3 portrait Pinterest pin, polished editorial "
            "lifestyle photography plus clean magazine layout. Main photo: a wooden "
            "wide-tooth comb, unlabelled amber hair oil bottle, soft towel and loose "
            "silk scrunchie on a sunlit vanity, warm honey and cream tones. Use photo "
            "across upper 62% and a warm ivory information panel across lower 38%; "
            "thin sage divider, restrained typography, generous but not empty spacing. "
            'Exact text only: heading "A Simple Hair Care Routine" in large elegant '
            'high-contrast serif; smaller insight "Begin with a gentle detangling step."; '
            'small bottom call to action "Explore the full routine →". Make all text '
            "crisp, accurately spelled and readable at phone size. No logo, no brand, "
            "no product box, no other text, no watermark, no medical claims, no before-and-after."
        )
    return (
        "Create one complete 2:3 portrait Pinterest pin, polished editorial "
        "lifestyle photography plus clean magazine layout. Main photo: "
        f'{spec["scene"]}. Give this scene a distinct composition and camera angle. '
        "Use photo across upper 62% and a warm ivory information panel across "
        "lower 38%; thin tasteful divider, sophisticated restrained typography, "
        "filled but uncluttered layout. Exact text only: heading "
        f'"{spec["heading"]}" in large elegant high-contrast serif; smaller insight '
        f'"{spec["tip"]}"; small bottom call to action "Explore the full guide →". '
        "Make all text crisp, accurately spelled and readable at phone size. "
        "No logo, brand, product box, supplement packaging, other text, watermark, "
        "medical claims, before-and-after, nudity, sad person, weight or body measurement."
    )


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def convert(source: Path, target: Path) -> None:
    if target.exists():
        raise FileExistsError(target)
    target.parent.mkdir(exist_ok=True)
    subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(source),
            "-vf", "scale=1000:1500:flags=lanczos", "-frames:v", "1",
            "-q:v", "2", "-y", str(target),
        ],
        check=True,
    )
    dims = subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0", str(target)],
        text=True,
    ).strip()
    if dims != "1000,1500":
        raise ValueError(f"{target}: unexpected dimensions {dims}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--first-date", help="First batch start date when no history exists")
    args = parser.parse_args()
    specs = json.loads((ROOT / "pin_specs.json").read_text(encoding="utf-8"))
    sources = json.loads((ROOT / "asset_sources.json").read_text(encoding="utf-8"))
    if len(specs) != 42 or len(sources) != 42:
        raise ValueError("Need exactly 42 specs and 42 generated images.")
    spec_by_key = {(s["product"], s["index"]): s for s in specs}
    if len(spec_by_key) != 42:
        raise ValueError("Pin specs are not unique.")
    history_path = ROOT / "gecmis.json"
    history = json.loads(history_path.read_text(encoding="utf-8")) if history_path.exists() else {"pinler": []}
    old = history["pinler"]
    if old:
        start = max(date.fromisoformat(p["tarih"][:10]) for p in old) + timedelta(days=1)
    elif args.first_date:
        start = date.fromisoformat(args.first_date)
    else:
        raise ValueError("Pass --first-date for the first run.")
    csv_rel = f"csv/pinler-{start.isoformat()}.csv"
    old_hashes = {p["gorsel_sha256"] for p in old}
    old_titles = [norm(p["baslik"]) for p in old]
    old_descriptions = {p["aciklama"] for p in old}
    new = []
    used_themes = {p: set() for p in PRODUCTS}
    last_link = {p: None for p in PRODUCTS}
    for p in old:
        last_link[p["urun"]] = p["link"]

    for day in range(7):
        publish_day = start + timedelta(days=day)
        for slot_no, (clock, product) in enumerate(SLOTS):
            ordinal = day * 2 + (1 if slot_no >= 3 else 0)
            spec = spec_by_key[product, ordinal + 1]
            theme = spec["theme"]
            if theme in used_themes[product]:
                raise ValueError(f"Repeated theme this week: {product} {theme}")
            used_themes[product].add(theme)
            title = spec["heading"]
            if len(title) > 100 or len(title.split()) > 6:
                raise ValueError(f"Invalid title: {title}")
            normalized = norm(title)
            if any(SequenceMatcher(None, normalized, prev).ratio() > 0.86 for prev in old_titles):
                raise ValueError(f"Similar title: {title}")
            old_titles.append(normalized)
            description = spec["description"]
            if not 150 <= len(description) <= 450 or not description.endswith("#affiliate"):
                raise ValueError(f"Invalid description: {title}")
            if description in old_descriptions:
                raise ValueError(f"Repeated description: {title}")
            old_descriptions.add(description)
            page = PAGES[product][ordinal % 3]
            link = f"{SITE}/yazi/{page}.html"
            if link == last_link[product]:
                raise ValueError(f"Repeated consecutive link: {product}")
            last_link[product] = link
            source = Path(sources[f"{product}-{ordinal+1}"])
            if not source.is_file():
                raise FileNotFoundError(source)
            pin_id = f"{publish_day.isoformat()}-{product}-{1 if slot_no < 3 else 2:02d}"
            image_rel = f"images/{pin_id}.jpg"
            target = ROOT / image_rel
            convert(source, target)
            digest = sha256(target)
            if digest in old_hashes:
                raise ValueError(f"Repeated image: {source}")
            old_hashes.add(digest)
            new.append({
                "id": pin_id,
                "tarih": f"{publish_day.isoformat()}T{clock}",
                "saat_dilimi": "America/New_York",
                "urun": product,
                "tema": theme,
                "baslik": title,
                "aciklama": description,
                "gorsel_dosya": image_rel,
                "gorsel_sha256": digest,
                "gorsel_prompt": prompt(spec),
                "link": link,
                "csv_dosyasi": csv_rel,
                "keywords": [theme, *KEYWORDS[product]],
            })
    history["pinler"].extend(new)
    history_path.write_text(json.dumps(history, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Added {len(new)} pins for {start} through {start + timedelta(days=6)}.")


if __name__ == "__main__":
    main()
