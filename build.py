#!/usr/bin/env python3
"""Build dist/portfolio.html: Editorial, high-fashion minimalist UGC portfolio for Selenia Sánchez.

Compiles template.html + videos.json into a high-performance, progressive-streaming web bundle.
Copies media files to dist/media/ for native CDN streaming on Vercel & localhost.
"""

import html
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(ROOT, "template.html")
CONFIG = os.path.join(ROOT, "videos.json")
OUT = os.path.join(ROOT, "dist", "portfolio.html")
OUT_INDEX = os.path.join(ROOT, "dist", "index.html")
DIST_MEDIA = os.path.join(ROOT, "dist", "media")


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


def build_editorial_card(reel, index):
    rid = esc(reel["id"])
    brand = esc(reel.get("brand", "Brand"))
    title = esc(reel.get("title", ""))
    duration = esc(reel.get("duration", "0:20"))
    cat = esc(reel.get("category", "tech")).lower()
    fmt = esc(reel.get("format", "UGC Video"))
    structure = esc(reel.get("structureLabel", ""))
    video_src = esc(reel.get("file", f"media/{rid}.mp4"))
    poster_src = esc(reel.get("poster", f"media/{rid}.jpg"))

    return f"""
    <article class="gallery-card" data-reel="{rid}" data-category="{cat}">
      <div class="video-box">
        <video data-reel="{rid}" src="{video_src}" poster="{poster_src}" loop playsinline preload="none" aria-label="{brand} - {title}"></video>
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

    # Copy media directory to dist/media for progressive streaming
    media_src_dir = os.path.join(ROOT, "media")
    os.makedirs(DIST_MEDIA, exist_ok=True)
    for fname in os.listdir(media_src_dir):
        s = os.path.join(media_src_dir, fname)
        d = os.path.join(DIST_MEDIA, fname)
        if os.path.isfile(s):
            shutil.copy2(s, d)

    # Locate primary and secondary hero visuals
    hero_primary = published_reels[0] if published_reels else None
    hero_secondary = published_reels[1] if len(published_reels) > 1 else None

    gallery_cards_html = "\n".join(
        [build_editorial_card(r, i) for i, r in enumerate(published_reels)]
    )

    primary_id = esc(hero_primary["id"]) if hero_primary else ""
    primary_src = esc(hero_primary.get("file", "")) if hero_primary else ""
    primary_poster = esc(hero_primary.get("poster", "")) if hero_primary else ""
    primary_brand = esc(hero_primary.get("brand", "")) if hero_primary else ""
    primary_format = esc(hero_primary.get("format", "")) if hero_primary else ""
    primary_structure = esc(hero_primary.get("structureLabel", "")) if hero_primary else ""
    primary_duration = esc(hero_primary.get("duration", "0:20")) if hero_primary else ""

    secondary_id = esc(hero_secondary["id"]) if hero_secondary else ""
    secondary_src = esc(hero_secondary.get("file", "")) if hero_secondary else ""
    secondary_poster = esc(hero_secondary.get("poster", "")) if hero_secondary else ""
    secondary_brand = esc(hero_secondary.get("brand", "")) if hero_secondary else ""
    secondary_format = esc(hero_secondary.get("format", "")) if hero_secondary else ""
    secondary_structure = esc(hero_secondary.get("structureLabel", "")) if hero_secondary else ""
    secondary_duration = esc(hero_secondary.get("duration", "0:20")) if hero_secondary else ""

    portrait_uri = esc(creator.get("portrait", "media/retrato.jpg"))
    email = (links.get("email") or "seleniadeveloper@gmail.com").strip()

    with open(TEMPLATE, encoding="utf-8") as fh:
        page = fh.read()

    page = page.replace("{{HERO_PRIMARY_ID}}", primary_id)
    page = page.replace("{{HERO_PRIMARY_SRC}}", primary_src)
    page = page.replace("{{HERO_PRIMARY_POSTER}}", primary_poster)
    page = page.replace("{{HERO_PRIMARY_BRAND}}", primary_brand)
    page = page.replace("{{HERO_PRIMARY_FORMAT}}", primary_format)
    page = page.replace("{{HERO_PRIMARY_STRUCTURE}}", primary_structure)
    page = page.replace("{{HERO_PRIMARY_DURATION}}", primary_duration)

    page = page.replace("{{HERO_SECONDARY_ID}}", secondary_id)
    page = page.replace("{{HERO_SECONDARY_SRC}}", secondary_src)
    page = page.replace("{{HERO_SECONDARY_POSTER}}", secondary_poster)
    page = page.replace("{{HERO_SECONDARY_BRAND}}", secondary_brand)
    page = page.replace("{{HERO_SECONDARY_FORMAT}}", secondary_format)
    page = page.replace("{{HERO_SECONDARY_STRUCTURE}}", secondary_structure)
    page = page.replace("{{HERO_SECONDARY_DURATION}}", secondary_duration)

    page = page.replace("{{PORTRAIT_URI}}", portrait_uri)
    page = page.replace("{{GALLERY_CARDS}}", gallery_cards_html)
    page = page.replace("{{EMAIL}}", esc(email))
    page = page.replace("{{SOCIALS}}", build_socials(links))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(page)
    with open(OUT_INDEX, "w", encoding="utf-8") as fh:
        fh.write(page)

    size_kb = os.path.getsize(OUT) / 1024.0
    print(f"dist/portfolio.html + dist/index.html -> {size_kb:.1f} KB (High-speed progressive streaming)")
    print(f"Published videos in editorial gallery: {len(published_reels)}")
    print(f"Media files copied to dist/media/: {len(os.listdir(DIST_MEDIA))}")


if __name__ == "__main__":
    main()
