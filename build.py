#!/usr/bin/env python3
"""Build dist/portfolio.html: Editorial, high-fashion minimalist UGC portfolio for Selenia Sánchez.

Compiles template.html + videos.json into a high-performance, progressive-streaming web bundle.
Copies the media the page uses to dist/media/ for native CDN streaming on Vercel & localhost.
Videos and photos can live in any subfolder of media/: they are found by file name.
"""

import html
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(ROOT, "template.html")
CONFIG = os.path.join(ROOT, "videos.json")
MEDIA = os.path.join(ROOT, "media")
OUT = os.path.join(ROOT, "dist", "portfolio.html")
OUT_INDEX = os.path.join(ROOT, "dist", "index.html")
DIST_MEDIA = os.path.join(ROOT, "dist", "media")

ICON_HEART = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8l1 1.1L12 21l7.8-7.5 1-1.1a5.5 5.5 0 0 0 0-7.8z"/></svg>'
ICON_COMMENT = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.4 8.4 0 0 1-12.2 7.5L3 21l2-5.6A8.4 8.4 0 1 1 21 11.5z"/></svg>'
ICON_SAVE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>'
ICON_SHARE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M22 2L11 13"/><path d="M22 2l-7 20-4-9-9-4 20-7z"/></svg>'


def esc(value):
    return html.escape(str(value or ""), quote=True)


def index_media():
    """Map file name -> path for everything under media/, whatever subfolder it is in."""
    found = {}
    for dirpath, _, filenames in os.walk(MEDIA):
        for fname in sorted(filenames):
            if not fname.startswith("."):
                found.setdefault(fname, os.path.join(dirpath, fname))
    return found


def publish(ref, media_index, missing):
    """Copy a media file into dist/media/ and return its public path ("" if it is not found)."""
    if not ref:
        return ""
    fname = os.path.basename(ref)
    src = media_index.get(fname)
    if not src:
        missing.append(fname)
        return ""
    shutil.copy2(src, os.path.join(DIST_MEDIA, fname))
    return "media/" + fname


def handle_from(links):
    url = (links.get("instagram") or links.get("tiktok") or "").rstrip("/")
    name = url.rsplit("/", 1)[-1].lstrip("@") if url else ""
    return "@" + name if name else ""


def build_socials(links):
    items = []
    if links.get("website"):
        items.append(
            '<a href="%s" target="_blank" rel="noopener noreferrer" class="footer-link">Software &amp; Tech ↗</a>'
            % esc(links["website"])
        )
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


def build_phone_slide(reel, video_src, poster_src, handle):
    rid = esc(reel["id"])
    brand = esc(reel.get("brand", "Brand"))
    return f"""
            <div class="feed-slide" data-reel="{rid}" data-brand="{brand}">
              <video data-src="{esc(video_src)}" data-poster="{esc(poster_src)}" muted playsinline preload="none" aria-hidden="true"></video>
              <div class="feed-ui" aria-hidden="true">
                <div class="feed-actions">{ICON_HEART}{ICON_COMMENT}{ICON_SAVE}{ICON_SHARE}</div>
                <div class="feed-caption">
                  <span class="feed-handle">{esc(handle)}</span>
                  <span class="feed-brand">{brand}</span>
                </div>
                <div class="feed-progress"><span></span></div>
              </div>
            </div>"""


def build_editorial_card(reel, video_src, poster_src):
    rid = esc(reel["id"])
    brand = esc(reel.get("brand", "Brand"))
    title = esc(reel.get("title", ""))
    duration = esc(reel.get("duration", "0:20"))
    cat = esc(reel.get("category", "tech")).lower()
    fmt = esc(reel.get("format", "UGC Video"))

    return f"""
    <article class="gallery-card" data-reel="{rid}" data-category="{cat}">
      <div class="video-box">
        <video data-reel="{rid}" src="{esc(video_src)}" poster="{esc(poster_src)}" loop playsinline preload="metadata" aria-label="{brand} - {title}"></video>
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
        <h3 class="card-brand-title">{brand}</h3>
        <span class="card-format">{fmt}</span>
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

    os.makedirs(DIST_MEDIA, exist_ok=True)
    media_index = index_media()
    missing = []
    no_preview = []
    handle = handle_from(links)

    gallery_cards = []
    phone_slides = []
    for reel in published_reels:
        rid = reel["id"]
        video_src = publish(reel.get("file") or f"media/{rid}.mp4", media_index, missing)
        poster_src = publish(reel.get("poster") or f"media/{rid}.jpg", media_index, missing)
        if not video_src:
            continue

        # The phone plays a light preview clip (make_previews.py); without one it uses the full reel
        preview_name = f"{rid}.preview.mp4"
        if preview_name in media_index:
            phone_src = publish(preview_name, media_index, missing)
        else:
            phone_src = video_src
            no_preview.append(rid)

        gallery_cards.append(build_editorial_card(reel, video_src, poster_src))
        phone_slides.append(build_phone_slide(reel, phone_src, poster_src, handle))

    portrait_uri = esc(publish(creator.get("portrait", "media/retrato.jpg"), media_index, missing))
    email = (links.get("email") or "seleniadeveloper@gmail.com").strip()

    with open(TEMPLATE, encoding="utf-8") as fh:
        page = fh.read()

    page = page.replace("{{PHONE_SLIDES}}", "".join(phone_slides))
    page = page.replace("{{PORTRAIT_URI}}", portrait_uri)
    page = page.replace("{{GALLERY_CARDS}}", "\n".join(gallery_cards))
    page = page.replace("{{EMAIL}}", esc(email))
    page = page.replace("{{SOCIALS}}", build_socials(links))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(page)
    with open(OUT_INDEX, "w", encoding="utf-8") as fh:
        fh.write(page)

    size_kb = os.path.getsize(OUT) / 1024.0
    print(f"dist/portfolio.html + dist/index.html -> {size_kb:.1f} KB (High-speed progressive streaming)")
    print(f"Published videos in editorial gallery: {len(gallery_cards)}")
    if no_preview:
        print("Phone feed uses the full video for: %s  (run: python3 make_previews.py)" % ", ".join(no_preview))
    if missing:
        print("WARNING — not found anywhere in media/: %s" % ", ".join(sorted(set(missing))), file=sys.stderr)


if __name__ == "__main__":
    main()
