"""Check rich article structure and affiliate destinations before deployment."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LINKS = {
    "kolajen": "https://nplink.net/z8oi2hbc",
    "sac": "https://nplink.net/3g8g0etk",
    "stres": "https://nplink.net/k0tsudy0",
}
PAGES = {
    "kolajen": ("morning-skin-ritual", "evening-skin-reset", "weekend-glow-habits"),
    "sac": ("gentle-wash-day", "night-hair-ritual", "scalp-care-pause"),
    "stres": ("calm-evening-ritual", "screen-free-reset", "slow-sunday-plan"),
}


def attributes(tag: str) -> dict[str, str]:
    return dict(re.findall(r'([\w-]+)="([^"]*)"', tag))


def validate_article(product: str, slug: str) -> int:
    path = ROOT / "yazi" / f"{slug}.html"
    content = path.read_text(encoding="utf-8")
    if 'href="../style.css"' not in content:
        raise ValueError(f"{slug}: missing shared stylesheet")
    if 'http-equiv="refresh"' in content.lower() or "<script" in content.lower():
        raise ValueError(f"{slug}: forbidden automatic navigation or script")
    if 'class="affiliate-disclosure"' not in content:
        raise ValueError(f"{slug}: missing top disclosure")
    if "This content is for general information and is not medical advice." not in content:
        raise ValueError(f"{slug}: missing medical note")
    if content.count('class="step-card"') != 5:
        raise ValueError(f"{slug}: expected five numbered steps")
    if content.count("<details>") != 3:
        raise ValueError(f"{slug}: expected three FAQ entries")
    if 'class="tip-box"' not in content or 'class="pullquote"' not in content:
        raise ValueError(f"{slug}: missing tip or pull quote")
    if 'class="product-card"' not in content or 'class="final-cta"' not in content:
        raise ValueError(f"{slug}: missing product card or final CTA")
    if 'class="mobile-shop"' not in content or content.count('class="related-card"') != 3:
        raise ValueError(f"{slug}: missing mobile bar or related cards")
    images = [attributes(tag) for tag in re.findall(r"<img\b[^>]*>", content)]
    if len(images) < 8:
        raise ValueError(f"{slug}: expected hero, section, and related images")
    for image in images:
        if not image.get("alt") or image.get("loading") != "lazy":
            raise ValueError(f"{slug}: image needs alt and lazy loading")
        if f"-{product}-" not in image.get("src", ""):
            raise ValueError(f"{slug}: image belongs to another product")
    affiliates = []
    buttons = 0
    for tag in re.findall(r"<a\b[^>]*>", content):
        attr = attributes(tag)
        href = attr.get("href", "")
        if href.startswith("https://nplink.net/"):
            affiliates.append(href)
            if href != LINKS[product]:
                raise ValueError(f"{slug}: wrong product link {href}")
            if attr.get("target") != "_blank" or attr.get("rel") != "sponsored nofollow noopener":
                raise ValueError(f"{slug}: missing affiliate link attributes")
            if "affiliate-button" in attr.get("class", ""):
                buttons += 1
    if not 10 <= len(affiliates) <= 15:
        raise ValueError(f"{slug}: {len(affiliates)} affiliate links")
    if buttons < 4:
        raise ValueError(f"{slug}: only {buttons} affiliate buttons")
    for paragraph in re.findall(r"<p\b[^>]*>.*?</p>", content, flags=re.DOTALL):
        if len(re.findall(r"https://nplink\.net/", paragraph)) > 2:
            raise ValueError(f"{slug}: too many links in one paragraph")
    return len(affiliates)


def main() -> None:
    for product, slugs in PAGES.items():
        for slug in slugs:
            print(f"{slug}: {validate_article(product, slug)} affiliate links")
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    if 'href="style.css"' not in home or home.count('class="home-card"') != 9:
        raise ValueError("Homepage must use the shared stylesheet and list all nine articles.")
    if "<script" in home.lower() or 'http-equiv="refresh"' in home.lower():
        raise ValueError("Homepage contains forbidden navigation.")
    print("Homepage: 9 articles listed")


if __name__ == "__main__":
    main()
