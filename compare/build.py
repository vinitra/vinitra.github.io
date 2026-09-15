#!/usr/bin/env python3
"""Generate Scholé vs <competitor> comparison pages at /<slug>/index.html.
Run: python3 compare/build.py
"""
import html, json, os, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "competitors.json")
TODAY = datetime.date.today().strftime("%B %Y")

SCHOLE = {
    "model": "AI-generated lessons built from your own docs, tools, and workflows, updated as they change",
    "personal": "Adapts in real time to each learner's role, prior answers, and pace",
    "modal": "24 modalities (explanations, video, audio, quizzes, code checkers, role-plays, decision trees, work upload and review), chosen on the fly",
    "grounding": "Grounded in the company's own materials; Olé answers questions from your documents",
    "assess": "Graded free text, code checkers, hands-on checklists, and mastery tracking",
    "setup": "Free trial in about 3 minutes, no credit card",
    "ai": "Multi-model: Claude, GPT, Gemini, Whisper; no one trains on your data",
    "lang": "English, French, German, Italian",
    "research": "Built on 40+ peer-reviewed papers from EPFL and UC Berkeley",
}

ROWS = [
    ("model", "Content model"),
    ("personal", "Personalization"),
    ("modal", "Learning formats"),
    ("grounding", "Grounded in your work"),
    ("assess", "Assessment"),
    ("setup", "Time to first lesson"),
    ("ai", "AI and data"),
    ("lang", "Languages"),
    ("research", "Research basis"),
]

CSS = """
:root{--teal:#008080;--teal-dark:#006666;--teal-soft:#e6f2f2;--ink:#22282e;--ink-2:#4b545c;--muted:#6f7981;--line:#e3e7ea;--page:#fafbfb;--card:#fff;--win:#0a7d3d;--win-soft:#e7f5ec}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--page);color:var(--ink-2);font-family:'Open Sans',system-ui,-apple-system,Segoe UI,Roboto,sans-serif;line-height:1.6}
a{color:var(--teal)}a:hover{color:var(--teal-dark)}
h1,h2,h3{font-family:'Saira Extra Condensed',sans-serif;text-transform:uppercase;font-weight:700;color:var(--ink);line-height:1.05;margin:0 0 .6rem}
h1{font-size:clamp(2.6rem,6vw,4.6rem)}h2{font-size:2.1rem;position:relative;padding-bottom:.5rem;margin-top:0}
h2::after{content:'';position:absolute;left:0;bottom:0;width:3rem;height:4px;border-radius:2px;background:var(--teal)}
h3{font-size:1.35rem;text-transform:none;letter-spacing:0}
.top{background:linear-gradient(180deg,#008a8a,#006e6e);color:#fff;padding:.75rem 0}
.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:1rem;flex-wrap:wrap}
.top a{color:#fff;text-decoration:none;font-family:'Saira Extra Condensed',sans-serif;text-transform:uppercase;letter-spacing:.08em;font-weight:700}
.top .brand{display:flex;align-items:center;gap:.5rem;font-size:1.2rem}.top .brand img{width:22px;height:22px}
.top nav a{margin-left:1.2rem;font-size:.95rem;opacity:.85}.top nav a:hover{opacity:1}
.wrap{max-width:66rem;margin:0 auto;padding:0 1.25rem}
.hero{padding:4rem 0 2.5rem}
.eyebrow{display:inline-block;font-family:'Saira Extra Condensed',sans-serif;text-transform:uppercase;letter-spacing:.08em;font-weight:700;color:var(--teal);background:var(--teal-soft);border-radius:999px;padding:.25rem .8rem;font-size:.95rem;margin-bottom:1rem}
.hero .vs{color:var(--teal)}
.lede{font-size:1.15rem;max-width:44rem;margin:0 0 1.5rem}
.cta{display:inline-block;background:var(--teal);color:#fff;text-decoration:none;font-weight:600;padding:.75rem 1.4rem;border-radius:8px;margin:.25rem .5rem .25rem 0;transition:transform .15s ease,box-shadow .15s ease}
.cta:hover{color:#fff;transform:translateY(-2px);box-shadow:0 10px 24px rgba(0,128,128,.25)}
.cta.ghost{background:#fff;color:var(--teal);border:1px solid var(--teal)}
section{padding:2.5rem 0}
.verdict{display:grid;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));gap:1rem;margin-top:1.25rem}
.vcard{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--teal);border-radius:8px;padding:1.1rem 1.25rem}
.vcard h3{margin-bottom:.35rem}.vcard p{margin:0;font-size:.95rem}
.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:var(--card)}
table{width:100%;border-collapse:collapse;min-width:44rem;font-size:.93rem}
th,td{padding:.9rem 1rem;vertical-align:top;border-bottom:1px solid var(--line);text-align:left}
th{font-family:'Saira Extra Condensed',sans-serif;text-transform:uppercase;letter-spacing:.05em;font-size:1.05rem;color:var(--ink);background:#f3f6f6}
th.schole{color:var(--teal)}td.row{font-weight:600;color:var(--ink);width:11rem}
td.schole{background:#f5fafa}
tr:last-child td{border-bottom:0}
.win{display:inline-block;font-family:'Saira Extra Condensed',sans-serif;text-transform:uppercase;letter-spacing:.06em;font-size:.8rem;font-weight:700;color:var(--win);background:var(--win-soft);border-radius:4px;padding:.05rem .4rem;margin-left:.4rem;vertical-align:middle}
.two{display:grid;grid-template-columns:repeat(auto-fit,minmax(18rem,1fr));gap:1.25rem}
.panel{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:1.4rem 1.5rem}
.panel ul{padding-left:1.2rem;margin:.5rem 0 0}.panel li{margin-bottom:.45rem}
.panel.good{border-top:4px solid var(--teal)}.panel.fair{border-top:4px solid #b9c2c8}
.faq details{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:.8rem 1.1rem;margin-bottom:.6rem}
.faq summary{cursor:pointer;font-weight:600;color:var(--ink)}
.faq p{margin:.6rem 0 0;font-size:.95rem}
.band{background:linear-gradient(135deg,#008080,#005f5f);color:#fff;border-radius:14px;padding:2.25rem 2rem;text-align:center;margin:1rem 0 2rem}
.band h2{color:#fff}.band h2::after{background:#fff;left:50%;transform:translateX(-50%)}.band p{max-width:38rem;margin:.75rem auto 1.25rem}
.band .cta{background:#fff;color:var(--teal)}
.others{display:flex;flex-wrap:wrap;gap:.5rem}
.others a{background:var(--card);border:1px solid var(--line);border-radius:999px;padding:.3rem .85rem;text-decoration:none;font-size:.9rem;color:var(--ink-2)}
.others a:hover{border-color:var(--teal);color:var(--teal)}
footer{border-top:1px solid var(--line);padding:1.5rem 0 2.5rem;font-size:.85rem;color:var(--muted)}
footer p{margin:.3rem 0}
@media (max-width:600px){.hero{padding:2.5rem 0 1.5rem}section{padding:1.75rem 0}}
"""

def esc(s): return html.escape(s, quote=True)

def page(c, all_slugs):
    name = c["name"]; slug = c["slug"]
    title = f"Scholé vs {name}"
    desc = f"How Scholé AI compares with {name} for workforce and enterprise learning: personalization, learning formats, grounding in your own work, assessment, and setup time."
    rows = []
    for key, label in ROWS:
        them = c["rows"].get(key, "Not a focus")
        win = key in c.get("wins", [])
        badge = '<span class="win">Scholé</span>' if win else ''
        rows.append('<tr><td class="row">%s</td><td class="schole">%s%s</td><td>%s</td></tr>' % (esc(label), esc(SCHOLE[key]), badge, esc(them)))
    strengths = "".join(f"<li>{esc(s)}</li>" for s in c["their_strengths"])
    wins = "".join(f"<li>{esc(s)}</li>" for s in c["schole_wins"])
    faqs = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in c["faq"])
    others = "".join(f"<a href=\"/{s}/\">Scholé vs {n}</a>" for s, n in all_slugs if s != slug)
    ld = json.dumps({
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in c["faq"]]
    })
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}: which is better for workforce learning?</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="https://vinitra.github.io/{slug}/">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="article">
<meta property="og:url" content="https://vinitra.github.io/{slug}/">
<meta property="og:image" content="https://vinitra.github.io/img/press/funding.jpg">
<link rel="icon" href="/img/schole.png">
<link href="https://fonts.googleapis.com/css?family=Saira+Extra+Condensed:500,700|Open+Sans:400,400i,600,700&display=swap" rel="stylesheet">
<script type="application/ld+json">{ld}</script>
<style>{CSS}</style>
</head>
<body>
<div class="top"><div class="wrap">
  <a class="brand" href="https://schole.ai"><img src="/img/schole.png" alt="">Scholé AI</a>
  <nav><a href="/">Vinitra Swamy</a><a href="https://schole.ai">schole.ai</a><a href="https://app.schole.ai/signup">Try free</a></nav>
</div></div>

<header class="hero"><div class="wrap">
  <span class="eyebrow">Comparison · {esc(c['category'])}</span>
  <h1>Scholé <span class="vs">vs</span> {esc(name)}</h1>
  <p class="lede">{esc(c['lede'])}</p>
  <a class="cta" href="https://app.schole.ai/signup">Try Scholé free</a>
  <a class="cta ghost" href="https://schole.ai/book-a-demo">Book a demo</a>
</div></header>

<section><div class="wrap">
  <h2>The short version</h2>
  <div class="verdict">
    <div class="vcard"><h3>What {esc(name)} is</h3><p>{esc(c['what'])}</p></div>
    <div class="vcard"><h3>What Scholé is</h3><p>An AI-native learning platform that builds adaptive, role-specific lessons from a company's own tools, documents, and workflows. Spun out of EPFL and UC Berkeley research, launched #1 on Product Hunt, and used by learners at Bank of America, NASA, Microsoft, Apple, NVIDIA, and Decathlon.</p></div>
    <div class="vcard"><h3>Pick Scholé if</h3><p>{esc(c['pick_schole'])}</p></div>
  </div>
</div></section>

<section><div class="wrap">
  <h2>Side by side</h2>
  <div class="tablewrap"><table>
    <thead><tr><th></th><th class="schole">Scholé</th><th>{esc(name)}</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table></div>
</div></section>

<section><div class="wrap">
  <h2>Where each one wins</h2>
  <div class="two">
    <div class="panel good"><h3>Where Scholé wins</h3><ul>{wins}</ul></div>
    <div class="panel fair"><h3>Where {esc(name)} is strong</h3><ul>{strengths}</ul></div>
  </div>
</div></section>

<section><div class="wrap faq">
  <h2>Common questions</h2>
  {faqs}
</div></section>

<section><div class="wrap">
  <div class="band">
    <h2>See it on your own material</h2>
    <p>Upload a doc, a process, or a tool guide and Scholé turns it into an adaptive lesson in minutes. Free trial, no credit card.</p>
    <a class="cta" href="https://app.schole.ai/signup">Start free</a>
  </div>
  <h3>Other comparisons</h3>
  <div class="others">{others}</div>
</div></section>

<footer><div class="wrap">
  <p>Written by <a href="/">Vinitra Swamy</a>, co-founder and CEO of Scholé AI. Comparison reflects publicly available information as of {TODAY}; {esc(name)} features and pricing change, so verify with the vendor. {esc(name)} is a trademark of its owner and is not affiliated with Scholé.</p>
</div></footer>
</body>
</html>
"""

def main():
    comps = json.load(open(DATA))
    all_slugs = [(c["slug"], c["name"]) for c in comps]
    for c in comps:
        d = os.path.join(ROOT, c["slug"]); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w").write(page(c, all_slugs))
    # index of all comparisons
    items = "".join(f"<li><a href=\"/{s}/\">Scholé vs {esc(n)}</a></li>" for s, n in all_slugs)
    os.makedirs(os.path.join(ROOT, "compare"), exist_ok=True)
    open(os.path.join(ROOT, "compare", "index.html"), "w").write(f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Scholé AI comparisons</title><meta name="description" content="How Scholé AI compares with other workforce learning platforms."><link href="https://fonts.googleapis.com/css?family=Saira+Extra+Condensed:700|Open+Sans:400,600&display=swap" rel="stylesheet"><style>{CSS}ul.list{{columns:2;padding-left:1.2rem}}ul.list li{{margin-bottom:.4rem}}</style></head><body>
<div class="top"><div class="wrap"><a class="brand" href="https://schole.ai"><img src="/img/schole.png" alt="">Scholé AI</a><nav><a href="/">Vinitra Swamy</a><a href="https://schole.ai">schole.ai</a></nav></div></div>
<header class="hero"><div class="wrap"><h1>Scholé <span class="vs">vs</span> everyone</h1><p class="lede">Honest, side-by-side comparisons of Scholé AI with the learning platforms companies usually shortlist.</p></div></header>
<section><div class="wrap"><ul class="list">{items}</ul></div></section>
<footer><div class="wrap"><p>Written by <a href="/">Vinitra Swamy</a>, co-founder and CEO of Scholé AI.</p></div></footer></body></html>""")
    # sitemap
    urls = ["https://vinitra.github.io/", "https://vinitra.github.io/compare/"] + [f"https://vinitra.github.io/{s}/" for s, _ in all_slugs]
    open(os.path.join(ROOT, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    open(os.path.join(ROOT, "robots.txt"), "w").write("User-agent: *\nAllow: /\nSitemap: https://vinitra.github.io/sitemap.xml\n")
    print(f"built {len(comps)} pages")

if __name__ == "__main__":
    main()
