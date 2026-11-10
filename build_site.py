"""Build the static article pages and homepage for GitHub Pages."""

from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = "https://dailywellnessnotes.github.io/notes"
AFFILIATE_DISCLOSURE = (
    "This page contains affiliate links. If you shop through these links, "
    "I may earn a commission."
)
DISCLAIMER = (
    "This content is not medical advice. Consult a healthcare professional "
    "before using a supplement."
)

PRODUCTS = {
    "kolajen": {
        "name": "Collagen Select",
        "link": "https://nplink.net/z8oi2hbc",
        "category": "Skin rituals",
        "color": "peach",
    },
    "sac": {
        "name": "Folisin",
        "link": "https://nplink.net/3g8g0etk",
        "category": "Hair care",
        "color": "sage",
    },
    "stres": {
        "name": "Restilen",
        "link": "https://nplink.net/k0tsudy0",
        "category": "Slow living",
        "color": "lilac",
    },
}

# Each article is original editorial copy, with general lifestyle suggestions
# and no asserted benefit for an unverified supplement.
ARTICLES = [
    {
        "product": "kolajen",
        "slug": "morning-skin-ritual",
        "title": "A Gentle Morning Skin Ritual You Can Actually Keep",
        "dek": "A practical start to the day with a few calm, repeatable steps.",
        "sections": [
            ("Start with a clean slate", "A morning routine does not need a crowded shelf. Begin by noticing how your skin feels when you wake up. If it feels comfortable, a gentle rinse may be enough for you; if you prefer a cleanser, choose one that fits your skin and follow its directions. The goal is a calm start, not a complicated checklist."),
            ("Make room for moisture", "After cleansing, apply a moisturizer you already enjoy using. Keep it where you will see it, such as beside your toothbrush, so the step becomes easier to remember. Give the product a moment to settle while you make breakfast or get dressed. Consistency is often simpler when the routine fits the rhythm you already have."),
            ("Bring the outside into the plan", "Before heading out, think about your day: a commute, a walk, errands, or time near a sunny window. Use sun protection that suits your needs and follow the label, including directions for reapplication. A hat or a little shade can also be part of a comfortable outdoor routine. Keep the approach practical for your schedule."),
            ("Add a small kitchen ritual", "A glass of water and a colorful breakfast can make the morning feel more intentional. Try fruit, yogurt, eggs, oats, or another meal you enjoy and can prepare without a rush. There is no single menu that creates a particular look. The useful part is finding a repeatable morning moment that feels good to you."),
            ("Keep the extras optional", "Some readers like to explore wellness products as an optional part of their routine. If you are curious about Collagen Select, read the product information, ingredients, and directions yourself before deciding whether it belongs in your day. A supplement is not a substitute for varied food, sleep, or professional care. Ask a healthcare professional about personal questions."),
        ],
        "closing": "Try this routine for its simplicity: wash or rinse, moisturize, plan for sun exposure, and enjoy a quiet breakfast moment. Change any step that does not fit your skin or your schedule. The full value of a ritual is that you can return to it without pressure.",
    },
    {
        "product": "kolajen",
        "slug": "evening-skin-reset",
        "title": "An Evening Skin Reset for a Slower Night",
        "dek": "A five step wind down that leaves space for rest.",
        "sections": [
            ("Make the room feel quieter", "The first step can happen before you touch a skincare bottle. Put away the items that crowd your sink, set out a clean towel, and soften the lighting if you can. A calmer space makes it easier to follow the routine you chose. Keep only the products you plan to use tonight within reach."),
            ("Wash away the day gently", "If you wore makeup or sunscreen, remove it according to the product directions. Follow with a gentle cleanser when that is part of your routine, and avoid scrubbing just to feel extra clean. Pat skin dry with a soft towel. This is a useful moment to notice whether your usual products still feel comfortable."),
            ("Choose one comfort step", "Apply a moisturizer that works for you while skin is still comfortably damp, if the label allows. You do not have to layer every serum on the shelf. A short routine is easier to keep on a busy night and gives you a chance to pay attention to how your skin responds to each product."),
            ("Set up tomorrow", "Place the morning basics where you will find them, refill a water glass, and fold the towel for the next day. These tiny actions make the following morning less hurried. If you like a journal, write down one thing you appreciated about the day. It can be a simple ritual, not another task to complete perfectly."),
            ("Decide on extras thoughtfully", "If an optional wellness supplement interests you, take time to review its ingredient list and instructions rather than adding it on impulse. The Collagen Select product page is available for readers who want to explore it. Personal health conditions, medications, and dietary needs can change what is appropriate, so ask a healthcare professional before using a supplement."),
        ],
        "closing": "Your evening reset can be as brief as a gentle cleanse, a moisturizer, and a few minutes away from the rush of the day. Keep the steps that feel useful and leave the rest. A quiet, repeatable routine makes more sense than a perfect one you never want to do.",
    },
    {
        "product": "kolajen",
        "slug": "weekend-glow-habits",
        "title": "Weekend Glow Habits Beyond the Bathroom Shelf",
        "dek": "Simple food, water, and downtime ideas for a softer weekend.",
        "sections": [
            ("Begin without a deadline", "On a weekend morning, resist the urge to turn self care into a long list. Open the curtains, make a favorite drink, and give yourself a few minutes before looking at messages. A calmer start helps you choose which activities actually fit your day. There is no need to copy somebody else's ideal routine."),
            ("Build a colorful plate", "Choose foods you enjoy from different colors and textures. A bowl of berries with yogurt, eggs and greens, or toast with fruit can be an easy breakfast. Later, make room for vegetables, beans, grains, or other foods that work for you. Think of variety as a flexible practice rather than a promise about appearance."),
            ("Keep water close", "A reusable bottle or a carafe on the table can serve as a gentle reminder to drink throughout the day. Plain water is enough; mint, citrus, or ice can make it more appealing if you like. Individual needs differ, so follow any guidance you have received for your own health and activity level."),
            ("Plan a small home spa moment", "Set aside a clean towel, a comfortable moisturizer, and perhaps a book or playlist. Use skincare products according to their directions and skip anything that irritates your skin. This moment can be ten minutes rather than an afternoon. The point is to enjoy the pause while taking care of ordinary needs."),
            ("Explore rather than expect", "Readers who are curious about Collagen Select can review its product page as an optional addition to a personal routine. Look at ingredients, directions, and suitability before making a choice. Do not rely on a supplement for a particular cosmetic or health result. A healthcare professional can help with individual questions."),
        ],
        "closing": "A weekend ritual might include breakfast, water within reach, a little time outdoors, and a simple skincare step. Choose the pieces that feel sustainable. The most inviting routine is one that leaves you more room to enjoy your weekend, not less.",
    },
    {
        "product": "sac",
        "slug": "gentle-wash-day",
        "title": "A Gentle Wash Day Plan for Your Hair",
        "dek": "From detangling to drying, a calm routine that fits real life.",
        "sections": [
            ("Prepare before the shower", "Set out a clean towel, the products you already use, and a wide tooth comb if that works for your hair. If you have tangles, start at the ends and move upward slowly rather than pulling from the roots. Different textures need different care, so let your own hair and comfort guide the method."),
            ("Keep washing simple", "Use shampoo as directed and focus on the areas where you prefer to cleanse. Rinse thoroughly and follow with conditioner when it is part of your routine. You do not need to follow an online rule about exactly how many times a week to wash. Your hair type, activity, and preferences all matter."),
            ("Handle wet hair with care", "After washing, gently press out extra water with a soft towel instead of rubbing vigorously. Detangle with a tool and method appropriate for your hair type, or wait until it is less damp if that feels better. A little patience can make the process more comfortable and less hurried."),
            ("Make styling manageable", "Choose a style that fits the time and tools you have today. If you use heat, read the appliance and product directions, and avoid rushing through the process. An air dry day or a loose style can also be a pleasant option. Your routine should serve your schedule rather than take over it."),
            ("Consider optional products carefully", "Some readers explore Folisin while planning a broader hair care routine. Review the product information and ingredients for yourself before deciding whether it is appropriate. A supplement is not a substitute for caring for your hair gently or seeking professional advice about a concern. Speak with a healthcare professional before using a supplement."),
        ],
        "closing": "A useful wash day plan is easy to repeat: prepare, cleanse, condition if desired, dry gently, and style at your own pace. Keep notes on what feels comfortable for your hair. You can change the steps with the weather, your schedule, or your preferences.",
    },
    {
        "product": "sac",
        "slug": "night-hair-ritual",
        "title": "A Softer Night Hair Ritual in Five Steps",
        "dek": "Small bedtime choices for an easier morning.",
        "sections": [
            ("Clear a little space", "Before bed, place a brush or comb, a soft hair tie, and any products you actually plan to use on a clean surface. A simple setup makes the routine feel intentional without filling the night with tasks. If you are tired, choose the one step that matters most to you and leave the rest."),
            ("Detangle in a way that suits you", "Work gently from the ends toward the roots when your hair type allows it. For curls or textures that are usually detangled wet, keep using the approach that feels comfortable instead of forcing a dry brushing habit. Listen to your hair and avoid pulling through knots just to finish quickly."),
            ("Choose a relaxed style", "A loose braid, soft scrunchie, or simply leaving hair down may suit different people. The best choice is comfortable and easy to undo. If a style pulls or bothers your scalp, change it. A nighttime routine should support rest rather than add another thing to worry about."),
            ("Make the bedside inviting", "Set out tomorrow's hair accessory, close the bathroom cabinet, and put your phone aside when you are ready. These quiet signals help mark the end of the day. You might pair the routine with a few pages of a book or another calming habit you enjoy."),
            ("Read before adding an extra", "If you want to learn about Folisin, use the linked product page to review its details, ingredients, and instructions. Be cautious with any product that promises a dramatic result. A supplement may not be suitable for everyone, especially alongside medications or health conditions, so ask a healthcare professional first."),
        ],
        "closing": "Your night routine can stay beautifully short: tidy a little, detangle gently when appropriate, and choose a comfortable style. Let the steps fit your hair texture and your energy. A routine you can enjoy on an ordinary weekday is often the one worth keeping. If one step starts to feel like work, simplify it until the evening feels like yours again.",
    },
    {
        "product": "sac",
        "slug": "scalp-care-pause",
        "title": "A Quiet Scalp Care Pause for Busy Days",
        "dek": "A mindful approach to hair care without a complicated schedule.",
        "sections": [
            ("Pick a convenient moment", "Scalp care does not have to be a separate appointment on your calendar. You might choose a few minutes before washing, while reading, or after putting away your work. The point is to slow down enough to notice comfort. If your scalp is irritated or painful, seek advice rather than pushing through."),
            ("Keep your hands gentle", "Use clean fingertips and a light touch if you enjoy a brief scalp massage. Move slowly and stop if anything feels uncomfortable. There is no need for force, special pressure, or a promise of a particular result. Think of it as a pleasant pause within the routine you already have."),
            ("Simplify the shelf", "Look at the products you use regularly and keep their directions easy to find. If you try a new oil or wash product, introduce it thoughtfully and pay attention to how it feels. More bottles do not automatically make a better routine. Keep only what supports your preferences and your hair type."),
            ("Connect it to wash day", "A clean towel, a suitable brush, and a manageable schedule can make the next wash day easier. Plan around your own needs rather than a rigid rule online. Some people wash frequently; others space washes farther apart. Comfort and personal preference can guide the everyday routine."),
            ("Explore supplements with care", "Folisin is an optional product some readers may wish to research. The linked page lets you look at the current details and ingredients directly. Avoid treating any supplement as a solution to a hair or scalp concern without professional input. A healthcare professional can help evaluate questions that are specific to you."),
        ],
        "closing": "A scalp care pause is most useful when it stays gentle and low pressure. Choose a time that fits, use a comfortable touch, and keep your hair care shelf straightforward. If a new issue persists, ask a qualified professional instead of relying on a self care trend. Your comfort matters more than following a trend perfectly.",
    },
    {
        "product": "stres",
        "slug": "calm-evening-ritual",
        "title": "Build a Calmer Evening Ritual at Home",
        "dek": "A flexible way to step away from the noise of the day.",
        "sections": [
            ("Signal that the day is slowing", "Choose a small transition after work or errands: change into comfortable clothes, lower a lamp, or put a kettle on. A clear signal can help you stop carrying every daytime task into the evening. It does not need to be elaborate. Pick something you can do on an ordinary weeknight."),
            ("Make one corner welcoming", "You do not need to redecorate the whole room. Clear a chair, add a blanket, and keep a book or journal nearby. A candle can be lovely when used safely, but a warm lamp works just as well. The space is simply an invitation to pause for a few minutes."),
            ("Let a screen rest", "If it fits your evening, place your phone out of reach for a short stretch. You can still use it later. Try making tea, listening to music, or reading a few pages before checking messages again. The experiment is about finding a rhythm that feels comfortable rather than imposing a strict rule."),
            ("Give your thoughts a place", "Write down tomorrow's first task, a question on your mind, or one good detail from today. A few lines are enough. You do not need an elegant notebook or a perfect gratitude list. The page is there to hold a thought so your evening can have a little more room."),
            ("Evaluate optional products", "Readers curious about Restilen can review the linked product information and ingredient list. A supplement should never replace professional support for ongoing distress, sleep problems, or other health concerns. Suitability varies by person, especially with medications and health conditions. Ask a healthcare professional before using a supplement."),
        ],
        "closing": "A calmer evening may be as simple as dimming a lamp, making tea, setting down a phone, and writing one line. Use the steps that fit your household and skip the rest. The goal is a kind, repeatable transition into the night. You can make the ritual shorter on busy days and linger with it when you have time.",
    },
    {
        "product": "stres",
        "slug": "screen-free-reset",
        "title": "A Gentle Screen Free Reset for Your Evening",
        "dek": "Trade a little scrolling time for a more intentional pause.",
        "sections": [
            ("Choose a realistic window", "A screen free evening does not need to last from dinner until bedtime. Start with ten or twenty minutes that fit your life. Put your device on silent or in another room if that is practical, and tell anyone who needs to reach you where you will be. Keep the plan flexible."),
            ("Prepare a simple alternative", "A blank journal, a paperback, a puzzle, or a mug of tea gives your hands something else to do. Pick the activity before you put the phone away so the pause feels welcoming. There is no prize for completing a chapter or filling a page. Enjoy the short change of pace."),
            ("Notice the room around you", "Open a window if the weather allows, adjust the lighting, or tidy one small surface. These details can make a familiar space feel new. You do not have to transform the room into a perfect retreat. A comfortable chair and a little quiet can be enough for tonight."),
            ("Return with intention", "When the planned time ends, decide whether you want to check messages, keep reading, or go to bed. Avoid turning the experiment into a strict pass or fail test. Some evenings will need more screen time than others. The value is in being able to choose how the next minutes go."),
            ("Keep product decisions separate", "If you are looking into Restilen, the product page offers details and ingredients to review. Consider it a separate decision from the screen free routine, and do not expect a supplement to resolve persistent stress or sleep concerns. Seek qualified support for individual health questions and consult a healthcare professional before use."),
        ],
        "closing": "A small screen free reset can start with a prepared activity and a realistic time window. Make the room comfortable, let the phone rest, and notice what you enjoy doing instead. Keep the experiment gentle enough that you will want to try it again. Even a brief pause can be a welcome change in the rhythm of an ordinary evening.",
    },
    {
        "product": "stres",
        "slug": "slow-sunday-plan",
        "title": "A Slow Sunday Plan That Leaves Room to Breathe",
        "dek": "A lighter reset for your space, schedule, and attention.",
        "sections": [
            ("Begin with one welcoming task", "Instead of writing a long reset list, choose one action that will make Monday a little easier: clear a table, prepare a bag, or wash a few dishes. Finish that task before deciding whether to do more. A short, completed action can feel more satisfying than an ambitious list left unfinished."),
            ("Make a comfortable meal", "Choose a simple meal you enjoy, perhaps soup, toast with vegetables, or a colorful grain bowl. Keep preparation realistic for your energy and budget. There is no ideal Sunday menu. The point is to enjoy a little time at the table without turning food into another performance."),
            ("Step outside if you can", "A short walk, a few minutes on a balcony, or simply opening a window can break up the day. Notice the light, weather, or sounds around you. Adapt the idea to your mobility and circumstances. This is an invitation to pause, not a requirement to complete a particular distance."),
            ("Plan only the first steps", "Look at the week ahead and write down the next useful action for Monday. Leave room for changes, rest, and the unexpected. A plan can be brief and still helpful. Once you have captured the essentials, close the notebook and let the rest of Sunday belong to you."),
            ("Be thoughtful with wellness extras", "Some readers may explore Restilen as an optional product. Review the current ingredient list and directions on the linked page before deciding anything. A supplement does not replace care for ongoing mental or physical health concerns. Check with a healthcare professional, especially if you take medication or have a medical condition."),
        ],
        "closing": "A slower Sunday can hold one small household task, a comfortable meal, a bit of fresh air, and a short look at Monday. Use only what supports your life right now. Leave enough space to enjoy the day itself. If the week ahead feels full, choose one helpful preparation and let that be enough for now.",
    },
]

CSS = """
:root{--ink:#26312e;--muted:#66716c;--paper:#fbfaf7;--line:#e8e7df;--sage:#d9e2d4;--peach:#f5e4d8;--lilac:#ebe6ef}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.7 Georgia,serif}
a{color:inherit}nav,.wrap,footer{max-width:1080px;margin:auto;padding:0 24px}nav{min-height:76px;display:flex;align-items:center;justify-content:space-between;gap:20px;border-bottom:1px solid var(--line)}
.brand{font:700 20px/1.2 system-ui,sans-serif;text-decoration:none;letter-spacing:-.03em}.navlinks{display:flex;gap:20px;font:600 13px system-ui,sans-serif}.navlinks a{text-decoration:none}
.hero{padding:74px 0 60px}.eyebrow,.pill{font:700 11px/1.4 system-ui,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:#53675b}.hero h1,article h1{font-size:clamp(40px,6vw,72px);line-height:1.08;letter-spacing:-.05em;margin:12px 0 20px;font-weight:500;max-width:840px}
.lede{font-size:21px;line-height:1.55;color:var(--muted);max-width:650px}.disclosure{background:#f4efe5;border:1px solid #e9dcc5;border-radius:12px;padding:12px 16px;font:600 13px/1.5 system-ui,sans-serif;color:#514633;margin:28px 0}
.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px;padding:0 0 80px}.card{display:block;text-decoration:none;border:1px solid var(--line);border-radius:18px;overflow:hidden;background:#fff;transition:transform .2s,box-shadow .2s}.card:hover{transform:translateY(-3px);box-shadow:0 12px 35px #20382a17}
.visual{height:190px;display:flex;align-items:end;padding:22px;background:var(--sage);font:500 28px/1.1 Georgia,serif;letter-spacing:-.04em}.visual.peach{background:linear-gradient(135deg,#f6e6d9,#f3d9c7)}.visual.sage{background:linear-gradient(135deg,#e5eadf,#cadbcd)}.visual.lilac{background:linear-gradient(135deg,#f0eaf2,#e0d9e8)}
.cardbody{padding:21px}.card h2{font-size:24px;line-height:1.2;letter-spacing:-.03em;margin:9px 0}.card p{font-size:15px;line-height:1.55;color:var(--muted);margin:0 0 15px}.read{font:700 13px system-ui,sans-serif;color:#37634c}
.article{max-width:760px;padding:54px 24px 80px;margin:auto}.article h1{font-size:clamp(39px,5vw,62px)}.article h2{font-size:27px;line-height:1.2;letter-spacing:-.025em;margin:40px 0 12px}.article p{margin:0 0 18px}.article .lede{font-size:21px}.cta{display:inline-block;background:#365b47;color:white;text-decoration:none;border-radius:999px;padding:13px 22px;font:700 14px system-ui,sans-serif;margin:16px 0 24px}.cta:hover{background:#284638}.product-note{background:#edf1e9;padding:24px;border-radius:16px;margin:28px 0}.product-note p{margin:0}.disclaimer{border-top:1px solid var(--line);padding-top:22px;margin-top:48px;color:var(--muted);font:13px/1.6 system-ui,sans-serif}footer{border-top:1px solid var(--line);padding-top:28px;padding-bottom:38px;color:var(--muted);font:13px system-ui,sans-serif}
@media(max-width:720px){nav{min-height:66px}.navlinks{gap:12px}.hero{padding:52px 0 42px}.grid{grid-template-columns:1fr;gap:16px}.visual{height:150px}.article{padding-top:38px}body{font-size:16px}}
"""


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def document(title: str, description: str, body: str, canonical: str) -> str:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{esc(description)}"><link rel="canonical" href="{esc(canonical)}">
<title>{esc(title)} | Daily Wellness Notes</title><style>{CSS}</style></head>
<body><nav><a class="brand" href="{SITE}/">Daily Wellness Notes</a><div class="navlinks"><a href="{SITE}/#skin">Skin</a><a href="{SITE}/#hair">Hair</a><a href="{SITE}/#slow">Slow living</a></div></nav>{body}
<footer>Daily Wellness Notes · Gentle ideas for everyday routines</footer></body></html>"""


def render_article(article: dict) -> str:
    product = PRODUCTS[article["product"]]
    paras = []
    for i, (heading, paragraph) in enumerate(article["sections"]):
        paras.append(f"<section><h2>{esc(heading)}</h2><p>{esc(paragraph)}</p></section>")
        if i == 2:
            paras.append(f'<a class="cta" href="{esc(product["link"])}" target="_blank" rel="sponsored nofollow noopener noreferrer">Explore the product ↗</a>')
    words = re.findall(r"\b[\w’'-]+\b", " ".join(p for _, p in article["sections"]) + " " + article["closing"])
    if not 300 <= len(words) <= 600:
        raise ValueError(f'{article["slug"]}: {len(words)} words')
    body = (
        f'<main class="article"><div class="pill">{esc(product["category"])}</div>'
        f'<div class="disclosure">{esc(AFFILIATE_DISCLOSURE)}</div>'
        f'<h1>{esc(article["title"])}</h1><p class="lede">{esc(article["dek"])}</p>'
        + "".join(paras)
        + f'<p>{esc(article["closing"])}</p><div class="product-note"><p>Curious about {esc(product["name"])}? Review the current details and ingredients before deciding whether it fits your routine.</p></div>'
        + f'<a class="cta" href="{esc(product["link"])}" target="_blank" rel="sponsored nofollow noopener noreferrer">Explore the product ↗</a>'
        + f'<div class="disclaimer">{esc(DISCLAIMER)}</div></main>'
    )
    url = f'{SITE}/yazi/{article["slug"]}.html'
    return document(article["title"], article["dek"], body, url)


def render_home() -> str:
    cards = []
    seen_anchors = set()
    for article in ARTICLES:
        product = PRODUCTS[article["product"]]
        anchor = {"kolajen": "skin", "sac": "hair", "stres": "slow"}[article["product"]]
        anchor_attr = f' id="{anchor}"' if anchor not in seen_anchors else ""
        seen_anchors.add(anchor)
        cards.append(
            f'<a class="card"{anchor_attr} href="{SITE}/yazi/{article["slug"]}.html">'
            f'<div class="visual {product["color"]}">{esc(product["category"])}</div>'
            f'<div class="cardbody"><div class="pill">{esc(product["category"])}</div>'
            f'<h2>{esc(article["title"])}</h2><p>{esc(article["dek"])}</p>'
            '<span class="read">Read the guide →</span></div></a>'
        )
    body = (
        '<main class="wrap"><header class="hero"><div class="eyebrow">Everyday wellness, thoughtfully</div>'
        '<h1>Gentle rituals for real life.</h1><p class="lede">Explore approachable ideas for skin care, hair care, and quieter moments at home. Start with one small step and make it your own.</p>'
        f'<div class="disclosure">{esc(AFFILIATE_DISCLOSURE)}</div></header>'
        '<div class="grid">' + "".join(cards) + '</div></main>'
    )
    return document("Home", "Gentle skin care, hair care, and slow living ideas.", body, SITE + "/")


def main() -> None:
    output = ROOT / "yazi"
    output.mkdir(exist_ok=True)
    for article in ARTICLES:
        (output / f'{article["slug"]}.html').write_text(render_article(article), encoding="utf-8")
    (ROOT / "index.html").write_text(render_home(), encoding="utf-8")
    print(f"Built {len(ARTICLES)} articles and the homepage.")


if __name__ == "__main__":
    main()
