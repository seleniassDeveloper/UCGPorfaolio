#!/usr/bin/env python3
"""Monta dist/portfolio.html: mete los vídeos y las fotos de media/ dentro del HTML.

Uso:
    python3 build.py

Para añadir un vídeo nuevo:
    1. python3 add_video.py originals/mi-video.mov reel-02
    2. añade la entrada en videos.json (o edita un hueco)
    3. python3 build.py
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
OUT = os.path.join(ROOT, "dist", "portfolio.html")          # documento completo, para enviar o subir
OUT_INDEX = os.path.join(ROOT, "dist", "index.html")            # documento principal para Vercel / web hosts
OUT_ARTIFACT = os.path.join(ROOT, "dist", "artifact.html")  # fragmento, para publicar como Artifact


DOC_HEAD = (
    "<!doctype html>\n<html lang=\"es\">\n<head>\n<meta charset=\"utf-8\">\n"
    "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
)
DOC_MID = "</head>\n<body>\n"
DOC_TAIL = "\n</body>\n</html>\n"

# Un artifact publicado no puede pasar de 16 MB ya renderizado.
# El base64 pesa 4/3 del archivo original, asi que conviene dejar margen.
HARD_LIMIT_MB = 15.0

ICONS = {
    "tiktok": "M16.6 5.82A4.28 4.28 0 0 1 15.54 3h-3.09v12.4a2.59 2.59 0 1 1-1.82-2.48v-3.1a5.66 5.66 0 1 0 4.91 5.6V9.01a7.35 7.35 0 0 0 4.3 1.38V7.3a4.29 4.29 0 0 1-3.24-1.48z",
    "instagram": "M12 2.2c3.2 0 3.58.01 4.85.07 1.17.05 1.8.25 2.23.41.56.22.96.48 1.38.9.42.42.68.82.9 1.38.16.42.36 1.06.41 2.23.06 1.27.07 1.65.07 4.85s-.01 3.58-.07 4.85c-.05 1.17-.25 1.8-.41 2.23-.22.56-.48.96-.9 1.38-.42.42-.82.68-1.38.9-.42.16-1.06.36-2.23.41-1.27.06-1.65.07-4.85.07s-3.58-.01-4.85-.07c-1.17-.05-1.8-.25-2.23-.41a3.8 3.8 0 0 1-1.38-.9 3.8 3.8 0 0 1-.9-1.38c-.16-.42-.36-1.06-.41-2.23C2.21 15.58 2.2 15.2 2.2 12s.01-3.58.07-4.85c.05-1.17.25-1.8.41-2.23.22-.56.48-.96.9-1.38.42-.42.82-.68 1.38-.9.42-.16 1.06-.36 2.23-.41C8.42 2.21 8.8 2.2 12 2.2zm0 3.1a6.7 6.7 0 1 0 0 13.4 6.7 6.7 0 0 0 0-13.4zm0 11.05a4.35 4.35 0 1 1 0-8.7 4.35 4.35 0 0 1 0 8.7zm8.53-11.32a1.57 1.57 0 1 1-3.13 0 1.57 1.57 0 0 1 3.13 0z",
    "youtube": "M23.5 6.5a3 3 0 0 0-2.1-2.1C19.5 3.9 12 3.9 12 3.9s-7.5 0-9.4.5A3 3 0 0 0 .5 6.5C0 8.4 0 12 0 12s0 3.6.5 5.5a3 3 0 0 0 2.1 2.1c1.9.5 9.4.5 9.4.5s7.5 0 9.4-.5a3 3 0 0 0 2.1-2.1C24 15.6 24 12 24 12s0-3.6-.5-5.5zM9.6 15.6V8.4l6.2 3.6-6.2 3.6z",
    "linkedin": "M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9h4v12H3zM9 9h3.8v1.7h.05c.53-.95 1.83-1.95 3.77-1.95 4.03 0 4.78 2.5 4.78 5.76V21h-4v-5.6c0-1.34-.03-3.06-1.9-3.06-1.9 0-2.2 1.45-2.2 2.96V21H9z",
    "email": "M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 4-8 5-8-5V6l8 5 8-5z",
}
LABELS = {"tiktok": "TikTok", "instagram": "Instagram", "youtube": "YouTube",
          "linkedin": "LinkedIn", "email": "Email"}


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
                url=esc(url), blank=blank, label=LABELS[key], path=ICONS[key])
        )
    return "".join(out)


def stats_block(stats):
    tiles = [s for s in stats if str(s.get("value", "")).strip()]
    if not tiles:
        return "<!-- sin datos todavia: rellena \"stats\" en videos.json -->"
    cells = "".join(
        '<div class="stat"><b>{v}</b><span data-es="{l_es}" data-en="{l_en}">{l_es}</span></div>'.format(
            v=esc(s["value"]), l_es=esc(s.get("label_es", "")), l_en=esc(s.get("label_en", "")))
        for s in tiles
    )
    return '<section class="stats">%s</section>' % cells


def reel_item(reel, poster_uri):
    if reel.get("placeholder"):
        return (
            '<div class="reel-item">'
            '<div class="reel reel--slot">'
            '<p data-es="Espacio libre" data-en="Open slot">Espacio libre</p>'
            "</div>"
            '<div class="reel-cap">'
            '<b data-es="{t_es}" data-en="{t_en}">{t_es}</b>'
            '<span data-es="{k_es}" data-en="{k_en}">{k_es}</span>'
            "</div></div>"
        ).format(
            t_es=esc(reel.get("title_es", "")), t_en=esc(reel.get("title_en", "")),
            k_es=esc(reel.get("kind_es", "")), k_en=esc(reel.get("kind_en", "")),
        )

    views = str(reel.get("views", "")).strip()
    likes = str(reel.get("likes", "")).strip()
    line1_es = esc(views) if views else esc(reel.get("title_es", ""))
    line1_en = esc(views) if views else esc(reel.get("title_en", ""))
    line2_es = esc(likes) if likes else esc(reel.get("kind_es", ""))
    line2_en = esc(likes) if likes else esc(reel.get("kind_en", ""))

    return (
        '<div class="reel-item">'
        '<div class="reel">'
        '<video data-reel="{id}" poster="{poster}" loop playsinline preload="none" '
        'aria-label="{label}"></video>'
        '<button class="reel-btn" type="button" aria-label="Reproducir"><i>'
        '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>'
        "</i></button>"
        "</div>"
        '<div class="reel-cap">'
        '<b data-es="{l1_es}" data-en="{l1_en}">{l1_es}</b>'
        '<span data-es="{l2_es}" data-en="{l2_en}">{l2_es}</span>'
        "</div></div>"
    ).format(
        id=esc(reel["id"]), poster=poster_uri, label=esc(reel.get("title_es", "Reel")),
        l1_es=line1_es, l1_en=line1_en, l2_es=line2_es, l2_en=line2_en,
    )


def photos_block():
    files = []
    for ext in ("jpg", "jpeg", "png", "webp"):
        files.extend(glob.glob(os.path.join(FOTOS, "*." + ext)))
    if not files:
        return "<!-- pon fotos en media/fotos/ con add_photos.py y saldra la cuadricula -->"
    mimes = {".png": "image/png", ".webp": "image/webp"}
    tiles = "".join(
        '<img src="%s" alt="" loading="lazy">' % data_uri(
            f, mimes.get(os.path.splitext(f)[1].lower(), "image/jpeg"))
        for f in sorted(files)
    )
    return (
        '<section class="fotos">'
        '<h2 class="sec-title" data-es="Lo último en Instagram" data-en="Most recent on Instagram">'
        "Lo último en Instagram</h2>"
        '<div class="photos">%s</div></section>' % tiles
    )


def main():
    with open(CONFIG, encoding="utf-8") as fh:
        cfg = json.load(fh)

    reels = cfg.get("reels", [])
    links = cfg.get("links", {})
    email = (links.get("email") or "hola@tuemail.com").strip()

    videos, posters = {}, {}
    for reel in reels:
        if reel.get("placeholder"):
            continue
        mp4 = os.path.join(ROOT, reel["file"])
        if not os.path.exists(mp4):
            sys.exit("Falta el vídeo: %s" % mp4)
        videos[reel["id"]] = data_uri(mp4, "video/mp4")
        poster = os.path.join(ROOT, reel["poster"]) if reel.get("poster") else None
        posters[reel["id"]] = data_uri(poster, "image/jpeg") if poster and os.path.exists(poster) else ""

    portrait_path = os.path.join(ROOT, cfg.get("portrait", "media/retrato.jpg"))
    portrait = data_uri(portrait_path, "image/jpeg") if os.path.exists(portrait_path) else ""

    items = [reel_item(r, posters.get(r.get("id"), "")) for r in reels]

    with open(TEMPLATE, encoding="utf-8") as fh:
        page = fh.read()

    page = page.replace("{{SOCIALS}}", socials(links))
    page = page.replace("{{PORTRAIT}}", portrait)
    page = page.replace("{{STATS}}", stats_block(cfg.get("stats", [])))
    page = page.replace("{{REEL_ITEMS}}", "\n      ".join(items))
    page = page.replace("{{PHOTOS}}", photos_block())
    page = page.replace("{{EMAIL}}", esc(email))
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
    print("dist/portfolio.html + dist/artifact.html -> %.2f MB "
          "(%d vídeo(s), %d hueco(s), %d foto(s))" % (
              size_mb, len(videos),
              sum(1 for r in reels if r.get("placeholder")), n_fotos))
    if not any(str(s.get("value", "")).strip() for s in cfg.get("stats", [])):
        print("Nota: la fila de cifras no sale porque \"stats\" esta vacio en videos.json.")
    if size_mb > HARD_LIMIT_MB:
        print("AVISO: pasa de %.0f MB. Comprime más los vídeos con add_video.py "
              "(baja el --target) antes de publicar." % HARD_LIMIT_MB)


if __name__ == "__main__":
    main()
