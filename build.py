#!/usr/bin/env python3
"""Build dist/portfolio.html: Minimalist, editorial UGC portfolio for Selenia Sánchez.

Compiles template.html + videos.json + media assets into a single high-performance bundle.
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
OUT = os.path.join(ROOT, "dist", "portfolio.html")
OUT_INDEX = os.path.join(ROOT, "dist", "index.html")
OUT_ARTIFACT = os.path.join(ROOT, "dist", "artifact.html")

HARD_LIMIT_MB = 15.0

ICONS = {
    "tiktok": "M16.6 5.82A4.28 4.28 0 0 1 15.54 3h-3.09v12.4a2.59 2.59 0 1 1-1.82-2.48v-3.1a5.66 5.66 0 1 0 4.91 5.6V9.01a7.35 7.35 0 0 0 4.3 1.38V7.3a4.29 4.29 0 0 1-3.24-1.48z",
    "instagram": "M12 2.2c3.2 0 3.58.01 4.85.07 1.17.05 1.8.25 2.23.41.56.22.96.48 1.38.9.42.42.68.82.9 1.38.16.42.36 1.06.41 2.23.06 1.27.07 1.65.07 4.85s-.01 3.58-.07 4.85c-.05 1.17-.25 1.8-.41 2.23-.22.56-.48.96-.9 1.38-.42.42-.82.68-1.38.9-.42.16-1.06.36-2.23.41-1.27.06-1.65.07-4.85.07s-3.58-.01-4.85-.07c-1.17-.05-1.8-.25-2.23-.41a3.8 3.8 0 0 1-1.38-.9 3.8 3.8 0 0 1-.9-1.38c-.16-.42-.36-1.06-.41-2.23C2.21 15.58 2.2 15.2 2.2 12s.01-3.58.07-4.85c.05-1.17.25-1.8.41-2.23.22-.56.48-.96.9-1.38.42-.42.82-.68 1.38-.9.42-.16 1.06-.36 2.23-.41C8.42 2.21 8.8 2.2 12 2.2zm0 3.1a6.7 6.7 0 1 0 0 13.4 6.7 6.7 0 0 0 0-13.4zm0 11.05a4.35 4.35 0 1 1 0-8.7 4.35 4.35 0 0 1 0 8.7zm8.53-11.32a1.57 1.57 0 1 1-3.13 0 1.57 1.57 0 0 1 3.13 0z",
    "email": "M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 4-8 5-8-5V6l8 5 8-5z",
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
            '<a href="%s" target="_blank" rel="noopener noreferrer" aria-label="Instagram" class="social-icon-link">'
            '<svg viewBox="0 0 24 24"><path d="%s"/></svg></a>' % (esc(links["instagram"]), ICONS["instagram"])
        )
    if links.get("tiktok"):
        items.append(
            '<a href="%s" target="_blank" rel="noopener noreferrer" aria-label="TikTok" class="social-icon-link">'
            '<svg viewBox="0 0 24 24"><path d="%s"/></svg></a>' % (esc(links["tiktok"]), ICONS["tiktok"])
        )
    if links.get("email"):
        items.append(
            '<a href="mailto:%s" aria-label="Email" class="social-icon-link">'
            '<svg viewBox="0 0 24 24"><path d="%s"/></svg></a>' % (esc(links["email"]), ICONS["email"])
        )
    return "".join(items)


def build_hero_reel(reel, poster_uri):
    """Builds a hero featured video phone mockup card."""
    rid = esc(reel["id"])
    brand = esc(reel.get("brand", "Featured"))
    title = esc(reel.get("title", ""))
    duration = esc(reel.get("duration", "0:20"))
    cat = esc(reel.get("category", "tech")).lower()
    cat_name = "Tech & AI" if cat == "tech" else "Travel"

    return f"""
    <div class="hero-phone-item" data-reel-id="{rid}">
      <div class="hero-phone-shell">
        <div class="hero-phone-screen">
          <div class="phone-dynamic-notch"></div>
          <div class="phone-top-badges">
            <span class="badge-pill badge-dur">⏱ {duration}</span>
            <span class="badge-pill badge-cat">{cat_name}</span>
          </div>
          <button class="sound-toggle-btn" type="button" aria-label="Toggle Sound">
            <svg class="icon-sound-on" viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>
            <svg class="icon-sound-off" viewBox="0 0 24 24"><path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/></svg>
          </button>
          <video data-reel="{rid}" poster="{poster_uri}" loop playsinline preload="none" aria-label="{brand} - {title}"></video>
          <button class="play-trigger-btn" type="button" aria-label="Play Video">
            <span class="play-icon-circle"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></span>
          </button>
          <div class="video-progress-line"><div class="video-progress-fill"></div></div>
        </div>
        <div class="hero-phone-caption">
          <div class="hero-phone-brand">{brand}</div>
          <div class="hero-phone-title">{title}</div>
        </div>
      </div>
    </div>
    """


def build_gallery_reel(reel, poster_uri):
    """Builds a gallery video card with narrative structure label."""
    rid = esc(reel["id"])
    brand = esc(reel.get("brand", "Brand"))
    title = esc(reel.get("title", ""))
    duration = esc(reel.get("duration", "0:20"))
    cat = esc(reel.get("category", "tech")).lower()
    cat_label = "Tech & AI" if cat == "tech" else "Travel"
    fmt = esc(reel.get("format", "UGC Video"))
    structure = esc(reel.get("structureLabel", "Hook → Demo → CTA"))

    return f"""
    <div class="reel-card" data-category="{cat}">
      <div class="reel-media-wrapper">
        <div class="reel-media-inner">
          <div class="reel-dynamic-island"></div>
          <div class="reel-floating-tags">
            <span class="badge-pill badge-dur">⏱ {duration}</span>
            <span class="badge-pill badge-cat">{cat_label}</span>
          </div>
          <button class="sound-toggle-btn" type="button" aria-label="Toggle Sound">
            <svg class="icon-sound-on" viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>
            <svg class="icon-sound-off" viewBox="0 0 24 24"><path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/></svg>
          </button>
          <video data-reel="{rid}" poster="{poster_uri}" loop playsinline preload="none" aria-label="{brand} - {title}"></video>
          <button class="play-trigger-btn" type="button" aria-label="Play Video">
            <span class="play-icon-circle"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></span>
          </button>
          <div class="video-progress-line"><div class="video-progress-fill"></div></div>
        </div>
      </div>
      <div class="reel-details">
        <div class="reel-meta-row">
          <span class="reel-brand">{brand}</span>
          <span class="reel-format-pill">{fmt}</span>
        </div>
        <h3 class="reel-card-title">{title}</h3>
        <div class="reel-structure-tag">
          <span class="structure-icon">✦</span>
          <span class="structure-text">{structure}</span>
        </div>
      </div>
    </div>
    """


def main():
    with open(CONFIG, encoding="utf-8") as fh:
        cfg = json.load(fh)

    creator = cfg.get("creator", {})
    links = cfg.get("links", {})
    all_reels = cfg.get("reels", [])

    # ONLY published reels are rendered in the public portfolio
    published_reels = [r for r in all_reels if r.get("status") == "published"]

    # The 3 featured videos in Hero
    featured_reels = [r for r in published_reels if r.get("featured")]
    if len(featured_reels) < 3:
        # Fallback to first 3 published reels if not enough marked featured
        featured_reels = published_reels[:3]
    else:
        featured_reels = featured_reels[:3]

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

    hero_reels_html = "\n".join([build_hero_reel(r, posters.get(r["id"], "")) for r in featured_reels])
    gallery_reels_html = "\n".join([build_gallery_reel(r, posters.get(r["id"], "")) for r in published_reels])

    tech_count = sum(1 for r in published_reels if r.get("category") == "tech")
    travel_count = sum(1 for r in published_reels if r.get("category") == "travel")
    all_count = len(published_reels)

    booking_url = links.get("booking", "").strip()
    email = (links.get("email") or "seleniadeveloper@gmail.com").strip()

    with open(TEMPLATE, encoding="utf-8") as fh:
        page = fh.read()

    page = page.replace("{{PORTRAIT_URI}}", portrait_uri)
    page = page.replace("{{HERO_REELS}}", hero_reels_html)
    page = page.replace("{{GALLERY_REELS}}", gallery_reels_html)
    page = page.replace("{{ALL_COUNT}}", str(all_count))
    page = page.replace("{{TECH_COUNT}}", str(tech_count))
    page = page.replace("{{TRAVEL_COUNT}}", str(travel_count))
    page = page.replace("{{EMAIL}}", esc(email))
    page = page.replace("{{BOOKING_URL}}", esc(booking_url))
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
    print(f"Published videos: {len(published_reels)} (Hero featured: {len(featured_reels)})")
    if size_mb > HARD_LIMIT_MB:
        print(f"WARNING: Bundle size {size_mb:.2f} MB exceeds {HARD_LIMIT_MB} MB limit.")


if __name__ == "__main__":
    main()
