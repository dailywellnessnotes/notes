"""Render the shared magazine layout using the current article content."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

from rich_content import RICH

DISCLOSURE = (
    "This page contains affiliate links. If you buy through them, "
    "I may earn a commission at no extra cost to you."
)
DISCLAIMER = (
    "This content is for general information and is not medical advice. "
    "Talk to a healthcare professional before starting any supplement."
)
THEME_CLASS = {"kolajen": "theme-skin", "sac": "theme-hair", "stres": "theme-calm"}
CATEGORY = {"kolajen": ("skin", "Skin"), "sac": ("hair", "Hair"), "stres": ("calm", "Calm")}


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def affiliate(url: str, label: str, css_class: str = "text-link") -> str:
    return (
        f'<a class="{css_class}" href="{esc(url)}" target="_blank" '
        f'rel="sponsored nofollow noopener">{esc(label)}</a>'
    )


def image_catalog(root: Path) -> dict:
    history = json.loads((root / "gecmis.json").read_text(encoding="utf-8"))["pinler"]
    specs = json.loads((root / "pin_specs.json").read_text(encoding="utf-8"))
    scenes = {(s["product"], s["theme"]): s["scene"].split(";")[0] for s in specs}
    catalog = {}
    for pin in history:
        key = (pin["urun"], pin["tema"])
        if key not in catalog:
            catalog[key] = {
                "url": pin["gorsel_dosya"],
                "alt": f'Editorial pin artwork showing {scenes.get(key, pin["tema"])}.',
            }
    return catalog


def media(catalog: dict, product: str, theme: str, site: str) -> dict:
    result = catalog.get((product, theme))
    if result is None:
        raise ValueError(f"Missing image for {product}: {theme}")
    return {"url": f'{site}/{result["url"]}', "alt": result["alt"], "theme": theme}


def nav(site: str) -> str:
    return (
        '<nav class="site-nav"><div class="wrap site-nav__inner">'
        f'<a class="brand" href="{site}/">Daily Wellness Notes</a>'
        '<div class="nav-links">'
        f'<a href="{site}/#skin">Skin</a>'
        f'<a href="{site}/#hair">Hair</a>'
        f'<a href="{site}/#calm">Calm</a>'
        '</div></div></nav>'
    )


def footer() -> str:
    return (
        '<footer class="site-footer"><div class="wrap">'
        f'<p class="medical-note">{esc(DISCLAIMER)}</p>'
        '<p>Daily Wellness Notes · Gentle ideas for everyday routines.</p>'
        '</div></footer>'
    )


def document(
    *, title: str, description: str, canonical: str, site: str,
    body: str, theme: str = "", article_page: bool = False, css_href: str,
) -> str:
    body_class = " ".join(x for x in (theme, "article-page" if article_page else "") if x)
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<meta name="description" content="{esc(description)}">'
        f'<link rel="canonical" href="{esc(canonical)}">'
        f'<link rel="stylesheet" href="{esc(css_href)}">'
        f'<title>{esc(title)} | Daily Wellness Notes</title></head>'
        f'<body class="{body_class}">{nav(site)}{body}{footer()}</body></html>'
    )


def linked_product_mention(text: str, name: str, url: str) -> str:
    escaped = esc(text)
    token = esc(name)
    if token not in escaped:
        raise ValueError(f"Missing product mention: {name}")
    return escaped.replace(token, affiliate(url, name), 1)


def article_image(image: dict) -> str:
    return f'<img src="{esc(image["url"])}" alt="{esc(image["alt"])}" loading="lazy">'


def render_article(article: dict, articles: list, products: dict, catalog: dict, site: str) -> str:
    product_code = article["product"]
    product = products[product_code]
    name, link = product["name"], product["link"]
    rich = RICH[article["slug"]]
    pictures = [media(catalog, product_code, theme, site) for theme in rich["media"]]
    headings = [heading for heading, _ in article["sections"]]
    section_ids = [f"step-{i+1}" for i in range(5)]
    toc = "".join(
        f'<li><a href="#{section_ids[i]}">{esc(heading)}</a></li>'
        for i, heading in enumerate(headings)
    )
    hero = (
        f'<div class="affiliate-disclosure">{esc(DISCLOSURE)}</div>'
        '<header class="wrap article-hero">'
        '<div class="hero-copy">'
        f'<div class="eyebrow">{esc(product["category"])} / Daily rituals</div>'
        f'<h1>{esc(article["title"])}</h1>'
        f'<p class="lede">{esc(article["dek"])}</p>'
        '<div class="read-meta"><span>4 min read</span><span>Practical guide</span></div>'
        '</div>'
        f'<figure class="hero-media">{article_image(pictures[0])}'
        f'<div class="hero-actions">{affiliate(link, f"Shop {name}", "btn affiliate-button")}</div>'
        f'<figcaption>{esc(pictures[0]["theme"].title())} · A gentle starting point</figcaption></figure>'
        '</header>'
    )
    sections = []
    for i, (heading, paragraph) in enumerate(article["sections"]):
        first = linked_product_mention(paragraph, name, link) if i == 4 else esc(paragraph)
        second = esc(rich["extra"][i])
        if i == 1:
            second += (
                " For an optional addition, take time to read "
                + affiliate(link, "the current product details")
                + " before deciding."
            )
        sections.append(
            f'<section class="step-card" id="{section_ids[i]}">'
            f'<div class="step-badge">{i+1:02d}</div>'
            f'<div><h2>{esc(heading)}</h2><p>{first}</p><p>{second}</p></div></section>'
        )
        if i == 0:
            sections.append(
                '<aside class="tip-box"><strong>Tip</strong><p>'
                + esc(rich["tip"])
                + " If you are comparing extras, check "
                + affiliate(link, "the current product label")
                + " separately.</p></aside>"
            )
        if i == 1:
            sections.append(
                '<div class="article-figure"><figure>'
                + article_image(pictures[1])
                + f'<figcaption>{esc(pictures[1]["theme"].title())}</figcaption></figure>'
                '<figure>'
                + article_image(pictures[2])
                + f'<figcaption>{esc(pictures[2]["theme"].title())}</figcaption></figure></div>'
            )
            sections.append(
                '<section class="product-card" aria-label="Featured product">'
                '<div class="eyebrow">Optional product to research</div>'
                f'<h2>{affiliate(link, name)}</h2>'
                '<p><strong>What it is:</strong> a product some readers may want to compare '
                'with their personal routine. See '
                + affiliate(link, "the current listing")
                + ' for exact ingredients, directions, and availability.</p>'
                '<p><strong>Why it appears here:</strong> it is an optional consideration, '
                'not a required step or a promise of results.</p>'
                '<ul><li>Review '
                + affiliate(link, "ingredients and directions")
                + ' before deciding.</li><li>Consider your own preferences and schedule.</li>'
                '<li>Ask a healthcare professional about personal suitability.</li></ul>'
                + affiliate(link, "Check price & details", "btn affiliate-button")
                + '</section>'
            )
        if i == 2:
            sections.append(f'<blockquote class="pullquote">“{esc(rich["quote"])}”</blockquote>')
        if i == 3:
            sections.append(
                '<div class="article-figure article-figure--single"><figure>'
                + article_image(pictures[3])
                + f'<figcaption>{esc(pictures[3]["theme"].title())}</figcaption></figure></div>'
            )
    section_html = "".join(sections)
    faq = (
        '<section class="faq" id="faq"><div class="eyebrow">Good to know</div><h2>Frequently asked questions</h2>'
        '<details><summary>Do I need every step in this routine?</summary>'
        '<p>No. Start with the part that fits your day and adjust the rest to your preferences. '
        'A comfortable, repeatable routine is more useful than a perfect checklist.</p></details>'
        '<details><summary>What should I check before considering the featured product?</summary>'
        '<p>Read the current '
        + affiliate(link, name)
        + ' ingredients and directions. Your medications, health conditions, and personal needs may affect whether a supplement is appropriate.</p></details>'
        '<details><summary>Where can I see current price and details?</summary>'
        '<p>Use '
        + affiliate(link, "the current product page")
        + ' to review up-to-date information. Ask a healthcare professional before starting any supplement.</p></details></section>'
    )
    related = []
    for other in [a for a in articles if a["product"] == product_code]:
        other_media = media(catalog, product_code, RICH[other["slug"]]["media"][0], site)
        related.append(
            f'<a class="related-card" href="{site}/yazi/{other["slug"]}.html">'
            + article_image(other_media)
            + '<div class="related-card__body">'
            + f'<span>{"Current guide" if other["slug"] == article["slug"] else "More to explore"}</span>'
            + f'<h3>{esc(other["title"])}</h3></div></a>'
        )
    body = (
        hero
        + '<main class="wrap article-layout"><div class="article-main">'
        + '<section class="toc" aria-label="In this guide"><h2>In this guide</h2><ol>'
        + toc
        + '</ol></section>'
        + section_html
        + f'<p class="closing-copy">{esc(article["closing"])}</p>'
        + faq
        + '<section class="final-cta"><div class="eyebrow">Make it your own</div>'
        + '<h2>Keep the routine gentle.</h2>'
        + '<p>Take the ideas that fit your day. If you would like to research '
        + affiliate(link, name)
        + ', review its current details and ask a professional about personal questions.</p>'
        + affiliate(link, f"Shop {name}", "btn btn--light affiliate-button")
        + '</section>'
        + '<section class="related"><div class="eyebrow">Read next</div>'
        + '<h2>More from this collection</h2><div class="related-grid">'
        + "".join(related)
        + '</div></section></div>'
        + '<aside class="article-aside"><div class="aside-card">'
        + article_image(pictures[0])
        + '<div class="kicker">A small reminder</div><p>Choose the steps that fit your day. '
        + 'Keep extras optional and check current product details before deciding.</p>'
        + '</div></aside></main>'
        + '<div class="mobile-shop"><span>Explore the optional product</span>'
        + affiliate(link, f"Shop {name}", "btn affiliate-button")
        + '</div>'
    )
    editorial_text = (
        " ".join(p for _, p in article["sections"])
        + " ".join(rich["extra"])
        + article["closing"]
        + rich["tip"] + rich["quote"] + article["dek"]
        + " ".join(headings)
    )
    words = len(re.findall(r"\b[\w’'-]+\b", editorial_text))
    if not 600 <= words <= 900:
        raise ValueError(f'{article["slug"]}: {words} editorial words')
    return document(
        title=article["title"], description=article["dek"],
        canonical=f'{site}/yazi/{article["slug"]}.html',
        site=site, body=body, theme=THEME_CLASS[product_code],
        article_page=True, css_href="../style.css",
    )


def render_home(articles: list, products: dict, catalog: dict, site: str) -> str:
    selected = [articles[0], articles[3], articles[6]]
    mosaic = "".join(
        article_image(media(catalog, article["product"], RICH[article["slug"]]["media"][0], site))
        for article in selected
    )
    groups = []
    for code in ("kolajen", "sac", "stres"):
        anchor, label = CATEGORY[code]
        group = [a for a in articles if a["product"] == code]
        cards = []
        for article in group:
            picture = media(catalog, code, RICH[article["slug"]]["media"][0], site)
            cards.append(
                f'<a class="home-card" href="{site}/yazi/{article["slug"]}.html">'
                + article_image(picture)
                + '<div class="home-card__body">'
                + f'<div class="eyebrow">{esc(label)} / Guide</div>'
                + f'<h3>{esc(article["title"])}</h3>'
                + f'<p>{esc(article["dek"])}</p><span>Read the guide →</span></div></a>'
            )
        groups.append(
            f'<section class="category-block {THEME_CLASS[code]}" id="{anchor}">'
            '<div class="category-head">'
            + f'<h2>{esc(products[code]["category"])}</h2>'
            + '<p>Thoughtful, realistic ideas to make an everyday routine feel a little easier.</p>'
            + '</div><div class="home-grid">' + "".join(cards) + '</div></section>'
        )
    body = (
        f'<div class="affiliate-disclosure">{esc(DISCLOSURE)}</div>'
        '<main class="wrap"><header class="home-hero"><div>'
        '<div class="eyebrow">Everyday wellness, thoughtfully</div>'
        '<h1>Gentle rituals for real life.</h1>'
        '<p class="lede">Explore approachable ideas for skin care, hair care, and quieter moments at home. '
        'Start with one small step and make it your own.</p>'
        '<a class="btn" href="#skin">Explore the guides</a></div>'
        + f'<div class="home-mosaic">{mosaic}</div></header>'
        + "".join(groups) + '</main>'
    )
    return document(
        title="Home", description="Gentle skin care, hair care, and slow living ideas.",
        canonical=site + "/", site=site, body=body, css_href="style.css",
    )
