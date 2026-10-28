#!/usr/bin/env python3
"""Build dist/portfolio.html: Editorial, high-fashion minimalist UGC portfolio for Selenia Sánchez.

Compiles template.html + videos.json + media assets into an ultra-clean, zero-runtime-dependency bundle.
"""

import base64
import html
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(ROOT, "template.html")
CONFIG = os.path.join(ROOT, "videos.json")
OUT = os.path.join(ROOT, "dist", "portfolio.html")
OUT_INDEX = os.path.join(ROOT, "dist", "index.html")
OUT_ARTIFACT = os.path.join(ROOT, "dist", "artifact.html")

HARD_LIMIT_MB = 15.0

ICONS = {
    "tiktok": "M16.6 5.82A4.28 4.28 0 0 1 15.54 3h-3.09v12.4a2.59 2.59 0 1 1-1.82-2.48v-3.1a5.66 5.66 0 1 0 4.91 5.6V9.01a7.35 7.35 0 0 0 4.3 1.38V7.3a4.29 4.29 0 0 1-3.24-1.48z",
    "instagram": "M12 2.2c3.2 0 3.58.01 4.85.07 1.17.05 1.8.25 2.23.41.56.22.96.48 1.38.9.42.42.68.82.9 1.38.16.42.36 1.06.41 2.23.06 1.27.07 1.65.07 4.85s-.01 3.58-.07 4.85c-.05 1.17-.25 1.8-.41 2.23-.22.56-.48.96-.9 1.38-.42.42-.82.68-1.38.9-.42.16-1.06.36-2.23.41-1.27.06-1.65.07-4.85.07s-3.58-.01-4.85-.07c-1.17-.05-1.8-.25-2.23-.41a3.8 3.8 0 0 1-1.38-.9 3.8 3.8 0 0 1-.9-1.38c-.16-.42-.36-1.06-.41-2.23C2.21 15.58 2.2 15.2 2.2 12s.01-3.58.07-4.85c.05-1.17.25-1.8.41-2.23.22-.56.48-.96.9-1.38.42-.42.82-.68 1.38-.9.42-.16 1.06-.36 2.23-.41C8.42 2.21 8.8 2.2 12 2.2zm0 3.1a6.7 6.7 0 1 0 0 13.4 6.7 6.7 0 0 0 0-13.4zm0 11.05a4.35 4.35 0 1 1 0-8.7 4.35 4.35 0 0 1 0 8.7zm8.53-11.32a1.57 1.57 0 1 1-3.13 0 1.57 1.57 0 0 1 3.13 0z",
}


def data_uri(path, mime):
    with open(path, "rb") as fh:
        return "data:%s;base64,%s" % (mime, base64.b64encode(fh.read()).decode("ascii"))


def esc(value):
    return html.escape(str(value or ""), quote=True)


def build_socials(links):
    items = []
    if links.get("instagram"):
        items.append(
            '<a href="%s" target="_blank" rel="noopener noreferrer" class="footer-link">Instagram ↗</a>'
            % esc(links["instagram"])
        )
    if links.get("tiktok"):
        items.append(
            '<a href="%s" target="_blank" rel="noopener noreferrer" class="footer-link">TikTok ↗</a>'
            % esc(links["tiktok"])
        )
    return "".join(items)


def build_editorial_card(reel, poster_uri, index):
    rid = esc(reel["id"])
    brand = esc(reel.get("brand", "Brand"))
    title = esc(reel.get("title", ""))
    duration = esc(reel.get("duration", "0:20"))
    cat = esc(reel.get("category", "tech")).lower()
    fmt = esc(reel.get("format", "UGC Video"))
    structure = esc(reel.get("structureLabel", ""))

    return f"""
    <article class="gallery-card" data-reel="{rid}" data-category="{cat}">
      <div class="video-box">
        <video data-reel="{rid}" poster="{poster_uri}" loop playsinline preload="none" aria-label="{brand} - {title}"></video>
        <div class="video-overlay">
          <button class="sound-toggle-btn" type="button" aria-label="Toggle sound">
            <svg class="sound-icon-muted" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M11 5L6 9H2v6h4l5 4V5z"/><line x1="23" y1="9" x2="17" y2="15"/><line x1="17" y1="9" x2="23" y2="15"/></svg>
            <svg class="sound-icon-unmuted" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M11 5L6 9H2v6h4l5 4V5z"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>
          </button>
          <button class="play-trigger-btn" type="button" aria-label="Play video">
            <span class="play-glyph">
              <svg class="play-icon" viewBox="0 0 24 24" fill="currentColor"><polygon points="6 3 20 12 6 21 6 3"/></svg>
              <svg class="pause-icon" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
            </span>
          </button>
          <span class="video-duration-pill">{duration}</span>
          <div class="video-progress-track"><div class="video-progress-fill"></div></div>
        </div>
      </div>
      <div class="card-meta">
        <div class="card-meta-head">
          <h3 class="card-brand-title">{brand}</h3>
          <span class="card-num-index">0{index + 1}</span>
        </div>
        <p class="card-structure-text">{structure}</p>
      </div>
    </article>
    """


def main():
    with open(CONFIG, encoding="utf-8") as fh:
        cfg = json.load(fh)

    creator = cfg.get("creator", {})
    links = cfg.get("links", {})
    all_reels = cfg.get("reels", [])

    published_reels = [r for r in all_reels if r.get("status") == "published"]

    # Locate primary and secondary hero visuals
    hero_primary = published_reels[0] if published_reels else None
    hero_secondary = published_reels[1] if len(published_reels) > 1 else None

    videos = {}
    posters = {}
    for reel in published_reels:
        mp4_path = os.path.join(ROOT, reel["file"])
        if not os.path.exists(mp4_path):
            sys.exit(f"Missing video file: {mp4_path}")
        videos[reel["id"]] = data_uri(mp4_path, "video/mp4")

        poster_path = os.path.join(ROOT, reel.get("poster", ""))
        if os.path.exists(poster_path):
            posters[reel["id"]] = data_uri(poster_path, "image/jpeg")
        else:
            posters[reel["id"]] = ""

    portrait_path = os.path.join(ROOT, creator.get("portrait", "media/retrato.jpg"))
    portrait_uri = data_uri(portrait_path, "image/jpeg") if os.path.exists(portrait_path) else ""

    gallery_cards_html = "\n".join(
        [build_editorial_card(r, posters.get(r["id"], ""), i) for i, r in enumerate(published_reels)]
    )

    primary_id = esc(hero_primary["id"]) if hero_primary else ""
    primary_poster = posters.get(hero_primary["id"], "") if hero_primary else ""
    primary_brand = esc(hero_primary.get("brand", "")) if hero_primary else ""
    primary_format = esc(hero_primary.get("format", "")) if hero_primary else ""
    primary_structure = esc(hero_primary.get("structureLabel", "")) if hero_primary else ""
    primary_duration = esc(hero_primary.get("duration", "0:20")) if hero_primary else ""

    secondary_id = esc(hero_secondary["id"]) if hero_secondary else ""
    secondary_poster = posters.get(hero_secondary["id"], "") if hero_secondary else ""
    secondary_brand = esc(hero_secondary.get("brand", "")) if hero_secondary else ""
    secondary_format = esc(hero_secondary.get("format", "")) if hero_secondary else ""
    secondary_structure = esc(hero_secondary.get("structureLabel", "")) if hero_secondary else ""
    secondary_duration = esc(hero_secondary.get("duration", "0:20")) if hero_secondary else ""

    email = (links.get("email") or "seleniadeveloper@gmail.com").strip()

    with open(TEMPLATE, encoding="utf-8") as fh:
        page = fh.read()

    page = page.replace("{{HERO_PRIMARY_ID}}", primary_id)
    page = page.replace("{{HERO_PRIMARY_POSTER}}", primary_poster)
    page = page.replace("{{HERO_PRIMARY_BRAND}}", primary_brand)
    page = page.replace("{{HERO_PRIMARY_FORMAT}}", primary_format)
    page = page.replace("{{HERO_PRIMARY_STRUCTURE}}", primary_structure)
    page = page.replace("{{HERO_PRIMARY_DURATION}}", primary_duration)

    page = page.replace("{{HERO_SECONDARY_ID}}", secondary_id)
    page = page.replace("{{HERO_SECONDARY_POSTER}}", secondary_poster)
    page = page.replace("{{HERO_SECONDARY_BRAND}}", secondary_brand)
    page = page.replace("{{HERO_SECONDARY_FORMAT}}", secondary_format)
    page = page.replace("{{HERO_SECONDARY_STRUCTURE}}", secondary_structure)
    page = page.replace("{{HERO_SECONDARY_DURATION}}", secondary_duration)

    page = page.replace("{{PORTRAIT_URI}}", portrait_uri)
    page = page.replace("{{GALLERY_CARDS}}", gallery_cards_html)
    page = page.replace("{{EMAIL}}", esc(email))
    page = page.replace("{{SOCIALS}}", build_socials(links))

    page = page.replace(
        "<script>\n(function(){",
        "<script>window.__REELS=%s;</script>\n<script>\n(function(){" % json.dumps(videos),
        1,
    )

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT_ARTIFACT, "w", encoding="utf-8") as fh:
        fh.write(page)

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(page)
    with open(OUT_INDEX, "w", encoding="utf-8") as fh:
        fh.write(page)

    size_mb = os.path.getsize(OUT) / 1048576.0
    print(f"dist/portfolio.html + dist/index.html -> {size_mb:.2f} MB")
    print(f"Published videos in editorial gallery: {len(published_reels)}")
    if size_mb > HARD_LIMIT_MB:
        print(f"WARNING: Bundle size {size_mb:.2f} MB exceeds {HARD_LIMIT_MB} MB limit.")


if __name__ == "__main__":
    main()
