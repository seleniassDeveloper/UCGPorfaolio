#!/usr/bin/env python3
"""Crea los clips cortos que se ven dentro del teléfono del inicio.

Uso:
    python3 make_previews.py              # todos los reels publicados
    python3 make_previews.py reel-01      # solo uno
    python3 make_previews.py --seconds 5

Cada clip son los primeros segundos del reel (el hook), sin audio, a 540x960.
Pesan unos cientos de KB, así el teléfono arranca rápido sin bajar el vídeo HD.
Deja media/previews/<id>.preview.mp4. Luego: python3 build.py
"""

import argparse
import json
import os
import subprocess
import sys

from build import CONFIG, MEDIA, index_media

PREVIEWS = os.path.join(MEDIA, "previews")


def main():
    ap = argparse.ArgumentParser(description="Clips del teléfono del inicio.")
    ap.add_argument("ids", nargs="*", help="Reels a procesar (por defecto, todos los publicados)")
    ap.add_argument("--seconds", type=float, default=6.0, help="Duración del clip (por defecto 6)")
    ap.add_argument("--crf", type=int, default=26, help="Calidad CRF de x264 (menor = más nítido)")
    args = ap.parse_args()

    if subprocess.run(["which", "ffmpeg"], capture_output=True).returncode != 0:
        sys.exit("Falta ffmpeg. Instálalo con: brew install ffmpeg")

    with open(CONFIG, encoding="utf-8") as fh:
        cfg = json.load(fh)
    reels = cfg.get("reels", []) + cfg.get("reels_es", [])
    if args.ids:
        reels = [r for r in reels if r["id"] in args.ids]
    else:
        reels = [r for r in reels if r.get("status") == "published"]

    os.makedirs(PREVIEWS, exist_ok=True)
    media_index = index_media()

    for reel in reels:
        rid = reel["id"]
        src = media_index.get(os.path.basename(reel.get("file") or f"{rid}.mp4"))
        if not src:
            print("✗ %s: no encuentro el vídeo en media/" % rid)
            continue
        out = os.path.join(PREVIEWS, f"{rid}.preview.mp4")
        subprocess.run([
            "ffmpeg", "-v", "error", "-y", "-t", str(args.seconds), "-i", src,
            "-an", "-vf", "scale=540:960:flags=lanczos", "-r", "30",
            "-c:v", "libx264", "-profile:v", "high", "-preset", "slow", "-crf", str(args.crf),
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", out,
        ], check=True)
        print("✓ media/previews/%s.preview.mp4  %d KB" % (rid, os.path.getsize(out) // 1024))

    print()
    print("Luego ejecuta: python3 build.py")


if __name__ == "__main__":
    main()
