#!/usr/bin/env python3
"""Comprime un vídeo para la web y saca su miniatura.

Uso:
    python3 add_video.py originals/mi-video.mov reel-02
    python3 add_video.py originals/mi-video.mov reel-02 --target 3.5 --poster 1.2

--target  MB que debe pesar el mp4 final (por defecto 3.5)
--poster  segundo del vídeo del que sale la miniatura (por defecto 1.0)

Deja media/<nombre>.mp4 y media/<nombre>.jpg listos para videos.json.
"""

import argparse
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
MEDIA = os.path.join(ROOT, "media")


def probe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", path],
        capture_output=True, text=True, check=True,
    ).stdout
    return float(json.loads(out)["format"]["duration"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("name", help="nombre del reel, por ejemplo reel-02")
    ap.add_argument("--target", type=float, default=3.5, help="MB que debe pesar el mp4 final")
    ap.add_argument("--poster", type=float, default=1.0, help="segundo de la miniatura")
    args = ap.parse_args()

    if not os.path.exists(args.source):
        sys.exit("No existe: %s" % args.source)
    if subprocess.run(["which", "ffmpeg"], capture_output=True).returncode != 0:
        sys.exit("Falta ffmpeg. Instálalo con: brew install ffmpeg")

    os.makedirs(MEDIA, exist_ok=True)
    mp4 = os.path.join(MEDIA, args.name + ".mp4")
    jpg = os.path.join(MEDIA, args.name + ".jpg")

    duration = probe_duration(args.source)
    audio_kbps = 96
    total_kbps = (args.target * 8192) / duration
    video_kbps = max(500, int(total_kbps - audio_kbps))

    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-i", args.source,
        "-vf", "scale=720:-2",
        "-c:v", "libx264", "-profile:v", "main", "-preset", "slow",
        "-b:v", "%dk" % video_kbps,
        "-maxrate", "%dk" % int(video_kbps * 1.45),
        "-bufsize", "%dk" % int(video_kbps * 2.5),
        "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-b:a", "%dk" % audio_kbps, "-ac", "1",
        "-movflags", "+faststart", mp4,
    ], check=True)

    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-ss", str(args.poster), "-i", args.source,
        "-frames:v", "1", "-vf", "scale=540:-2", "-q:v", "5", jpg,
    ], check=True)

    mb = os.path.getsize(mp4) / 1048576.0
    mins, secs = divmod(int(duration), 60)
    print("media/%s.mp4  %.2f MB  %d:%02d" % (args.name, mb, mins, secs))
    print("media/%s.jpg  miniatura lista" % args.name)
    print()
    print("Pega esto en videos.json (sustituye un hueco con \"placeholder\": true):")
    print(json.dumps({
        "id": args.name,
        "file": "media/%s.mp4" % args.name,
        "poster": "media/%s.jpg" % args.name,
        "duration": "%d:%02d" % (mins, secs),
        "title_es": "Nombre de la marca",
        "title_en": "Brand name",
        "kind_es": "Demo de producto",
        "kind_en": "Product demo",
        "lang_es": "Español, subtítulos quemados",
        "lang_en": "Spanish, burned-in captions",
    }, indent=2, ensure_ascii=False))
    print()
    print("Luego: python3 build.py")


if __name__ == "__main__":
    main()
