#!/usr/bin/env python3
"""Build dist/portfolio.html: bundles videos and assets into an English-only, high-converting UGC portfolio.

Usage:
    python3 build.py
"""

import base64
import glob
import html
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(ROOT, "template.html")
CONFIG = os.path.join(ROOT, "videos.json")
FOTOS = os.path.join(ROOT, "media", "fotos")
OUT = os.path.join(ROOT, "dist", "portfolio.html")
OUT_INDEX = os.path.join(ROOT, "dist", "index.html")
OUT_ARTIFACT = os.path.join(ROOT, "dist", "artifact.html")

DOC_HEAD = (
    "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
    "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
    "<meta name=\"theme-color\" content=\"#FF581A\">\n"
    "<meta name=\"description\" content=\"Selenia Sánchez (Seleedev) - UGC Creator & Software Engineer specializing in Tech, AI apps, and Travel & Lifestyle content.\">\n"
)
DOC_MID = "</head>\n<body>\n"
DOC_TAIL = "\n</body>\n</html>\n"

HARD_LIMIT_MB = 15.0

ICONS = {
    "tiktok": "M16.6 5.82A4.28 4.28 0 0 1 15.54 3h-3.09v12.4a2.59 2.59 0 1 1-1.82-2.48v-3.1a5.66 5.66 0 1 0 4.91 5.6V9.01a7.35 7.35 0 0 0 4.3 1.38V7.3a4.29 4.29 0 0 1-3.24-1.48z",
    "instagram": "M12 2.2c3.2 0 3.58.01 4.85.07 1.17.05 1.8.25 2.23.41.56.22.96.48 1.38.9.42.42.68.82.9 1.38.16.42.36 1.06.41 2.23.06 1.27.07 1.65.07 4.85s-.01 3.58-.07 4.85c-.05 1.17-.25 1.8-.41 2.23-.22.56-.48.96-.9 1.38-.42.42-.82.68-1.38.9-.42.16-1.06.36-2.23.41-1.27.06-1.65.07-4.85.07s-3.58-.01-4.85-.07c-1.17-.05-1.8-.25-2.23-.41a3.8 3.8 0 0 1-1.38-.9 3.8 3.8 0 0 1-.9-1.38c-.16-.42-.36-1.06-.41-2.23C2.21 15.58 2.2 15.2 2.2 12s.01-3.58.07-4.85c.05-1.17.25-1.8.41-2.23.22-.56.48-.96.9-1.38.42-.42.82-.68 1.38-.9.42-.16 1.06-.36 2.23-.41C8.42 2.21 8.8 2.2 12 2.2zm0 3.1a6.7 6.7 0 1 0 0 13.4 6.7 6.7 0 0 0 0-13.4zm0 11.05a4.35 4.35 0 1 1 0-8.7 4.35 4.35 0 0 1 0 8.7zm8.53-11.32a1.57 1.57 0 1 1-3.13 0 1.57 1.57 0 0 1 3.13 0z",
    "youtube": "M23.5 6.5a3 3 0 0 0-2.1-2.1C19.5 3.9 12 3.9 12 3.9s-7.5 0-9.4.5A3 3 0 0 0 .5 6.5C0 8.4 0 12 0 12s0 3.6.5 5.5a3 3 0 0 0 2.1 2.1c1.9.5 9.4.5 9.4.5s7.5 0 9.4-.5a3 3 0 0 0 2.1-2.1C24 15.6 24 12 24 12s0-3.6-.5-5.5zM9.6 15.6V8.4l6.2 3.6-6.2 3.6z",
    "linkedin": "M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9h4v12H3zM9 9h3.8v1.7h.05c.53-.95 1.83-1.95 3.77-1.95 4.03 0 4.78 2.5 4.78 5.76V21h-4v-5.6c0-1.34-.03-3.06-1.9-3.06-1.9 0-2.2 1.45-2.2 2.96V21H9z",
    "email": "M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 4-8 5-8-5V6l8 5 8-5z",
}
LABELS = {
    "tiktok": "TikTok",
    "instagram": "Instagram",
    "youtube": "YouTube",
    "linkedin": "LinkedIn",
    "email": "Email",
}


def data_uri(path, mime):
    with open(path, "rb") as fh:
        return "data:%s;base64,%s" % (mime, base64.b64encode(fh.read()).decode("ascii"))


def esc(value):
    return html.escape(str(value), quote=True)


def socials(links):
    out = []
    for key in ("tiktok", "instagram", "youtube", "linkedin", "email"):
        url = (links.get(key) or "").strip()
        if not url:
            continue
        if key == "email":
            url = "mailto:" + url
        blank = "" if key == "email" else ' target="_blank" rel="noopener noreferrer"'
        out.append(
            '<a href="{url}"{blank} aria-label="{label}">'
            '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="{path}"/></svg></a>'.format(
                url=esc(url), blank=blank, label=LABELS[key], path=ICONS[key]
            )
        )
    return "".join(out)


FLOWER_SVG = (
    '<svg class="flower-icon" viewBox="0 0 100 100" fill="currentColor" aria-hidden="true">'
    '<path d="M50 20 C58 8, 73 14, 70 28 C82 26, 89 40, 80 49 C90 59, 80 73, 68 69 C65 82, 50 84, 44 73 C33 80, 21 69, 28 58 C16 51, 20 37, 32 37 C30 23, 44 14, 50 20 Z"/>'
    '</svg>'
)


def pillars_block():
    """Highlights key creative pillars without showing follower counts or vanity metrics."""
    pillars = [
        {
            "icon": "🤖",
            "title": "Tech & AI UGC",
            "desc": "Engaging product walkthroughs, live workflows & high-retention founder demos.",
            "tag": "SaaS & AI Apps",
        },
        {
            "icon": "✈️",
            "title": "Travel & Lifestyle",
            "desc": "Aesthetic, cinematic storytelling connecting genuine experiences with global brands.",
            "tag": "Global Content",
        },
        {
            "icon": "⚡",
            "title": "High-Converting Creative",
            "desc": "Scroll-stopping hooks and direct-response formats for TikTok & Instagram Reels.",
            "tag": "Direct Response",
        },
    ]

    cards = []
    for p in pillars:
        cards.append(
            '<div class="service-card">'
            '{flower}'
            '<div class="pillar-emoji">{icon}</div>'
            '<div class="service-title">{title}</div>'
            '<p class="pillar-desc">{desc}</p>'
            '<span class="btn-small-pill">{tag}</span>'
            '</div>'.format(
                flower=FLOWER_SVG,
                icon=p["icon"],
                title=esc(p["title"]),
                desc=esc(p["desc"]),
                tag=esc(p["tag"]),
            )
        )
    return '<div class="services-cards">%s</div>' % "".join(cards)


def reel_item(reel, poster_uri):
    if reel.get("placeholder"):
        return (
            '<div class="reel-item reel-item--slot">'
            '<div class="reel reel--slot">'
            '<div class="slot-icon">✦</div>'
            '<p>Open slot</p>'
            "</div>"
            '<div class="reel-cap">'
            '<b>{title}</b>'
            '<span>{kind}</span>'
            "</div></div>"
        ).format(
            title=esc(reel.get("title") or reel.get("title_en", "")),
            kind=esc(reel.get("kind") or reel.get("kind_en", "")),
        )

    title = esc(reel.get("title") or reel.get("title_en", "Reel"))
    kind = esc(reel.get("kind") or reel.get("kind_en", "UGC Video"))
    duration = esc(reel.get("duration", "")).strip()
    cat = esc(reel.get("category", "tech")).strip().lower()

    if cat == "travel":
        cat_badge = "✈️ Travel"
    else:
        cat_badge = "🤖 Tech & AI"

    dur_html = ('<span class="reel-badge reel-duration">⏱ %s</span>' % duration) if duration else ""

    return (
        '<div class="reel-item" data-category="{cat}">'
        '<div class="reel-frame">'
        '<div class="reel">'
        '<div class="reel-island"></div>'
        '<div class="reel-badges">'
        '{dur_html}'
        '<span class="reel-badge reel-cat">{cat_badge}</span>'
        '</div>'
        '<button class="reel-sound-btn" type="button" aria-label="Toggle sound">'
        '<svg class="sound-on" viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>'
        '<svg class="sound-off" viewBox="0 0 24 24"><path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/></svg>'
        '</button>'
        '<video data-reel="{id}" poster="{poster}" loop playsinline preload="none" '
        'aria-label="{title}"></video>'
        '<button class="reel-btn" type="button" aria-label="Play video"><i>'
        '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>'
        '</i></button>'
        '<div class="reel-progress"><div class="reel-progress-bar"></div></div>'
        '</div>'
        '</div>'
        '<div class="reel-cap">'
        '<div class="reel-cap-info">'
        '<b class="reel-title">{title}</b>'
        '<span class="reel-kind-tag">{kind}</span>'
        '</div>'
        '</div></div>'
    ).format(
        id=esc(reel["id"]),
        poster=poster_uri,
        title=title,
        kind=kind,
        cat=cat,
        cat_badge=cat_badge,
        dur_html=dur_html,
    )


def photos_block():
    files = []
    for ext in ("jpg", "jpeg", "png", "webp"):
        files.extend(glob.glob(os.path.join(FOTOS, "*." + ext)))
    if not files:
        return ""
    mimes = {".png": "image/png", ".webp": "image/webp"}
    tiles = "".join(
        '<img src="%s" alt="Instagram photography by Selenia" loading="lazy">' % data_uri(
            f, mimes.get(os.path.splitext(f)[1].lower(), "image/jpeg"))
        for f in sorted(files)
    )
    return (
        '<section class="fotos">'
        '<h2 class="sec-title">Recent Moments on Instagram</h2>'
        '<div class="photos">%s</div></section>' % tiles
    )


def main():
    with open(CONFIG, encoding="utf-8") as fh:
        cfg = json.load(fh)

    reels = [r for r in cfg.get("reels", []) if r.get("category") != "es"]
    links = cfg.get("links", {})
    email = (links.get("email") or "seleniadeveloper@gmail.com").strip()
    booking = (links.get("booking") or "https://cal.com/seleniasanchez").strip()

    videos, posters = {}, {}
    for reel in reels:
        if reel.get("placeholder"):
            continue
        mp4 = os.path.join(ROOT, reel["file"])
        if not os.path.exists(mp4):
            sys.exit("Missing video file: %s" % mp4)
        videos[reel["id"]] = data_uri(mp4, "video/mp4")
        poster = os.path.join(ROOT, reel["poster"]) if reel.get("poster") else None
        posters[reel["id"]] = data_uri(poster, "image/jpeg") if poster and os.path.exists(poster) else ""

    portrait_path = os.path.join(ROOT, cfg.get("portrait", "media/retrato.jpg"))
    portrait = data_uri(portrait_path, "image/jpeg") if os.path.exists(portrait_path) else ""

    items_all = [reel_item(r, posters.get(r.get("id"), "")) for r in reels]

    with open(TEMPLATE, encoding="utf-8") as fh:
        page = fh.read()

    page = page.replace("{{SOCIALS}}", socials(links))
    page = page.replace("{{PORTRAIT}}", portrait)
    page = page.replace("{{PILLARS}}", pillars_block())
    page = page.replace("{{REEL_ITEMS}}", "\n      ".join(items_all))
    page = page.replace("{{PHOTOS}}", photos_block())
    page = page.replace("{{EMAIL}}", esc(email))
    page = page.replace("{{BOOKING_URL}}", esc(booking))
    page = page.replace(
        "<script>\n(function(){",
        "<script>window.__REELS=%s;</script>\n<script>\n(function(){" % json.dumps(videos),
        1,
    )

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT_ARTIFACT, "w", encoding="utf-8") as fh:
        fh.write(page)

    cut = page.index("<style>")
    full_html = DOC_HEAD + page[:cut] + DOC_MID + page[cut:] + DOC_TAIL
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(full_html)
    with open(OUT_INDEX, "w", encoding="utf-8") as fh:
        fh.write(full_html)

    size_mb = os.path.getsize(OUT) / 1048576.0
    n_fotos = len(glob.glob(os.path.join(FOTOS, "*.*")))
    print("dist/portfolio.html + dist/index.html -> %.2f MB "
          "(%d video(s), %d placeholder(s), %d photo(s))" % (
              size_mb, len(videos),
              sum(1 for r in reels if r.get("placeholder")), n_fotos))
    if size_mb > HARD_LIMIT_MB:
        print("WARNING: size is %.2f MB, which exceeds %.0f MB limit for Vercel." % (size_mb, HARD_LIMIT_MB))


if __name__ == "__main__":
    main()
