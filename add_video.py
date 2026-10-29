#!/usr/bin/env python3
"""Optimiza un vídeo para la web en alta definición nítida y extrae su miniatura.

Uso estándar (alta definición, nitidez máxima con filtro CAS y Lanczos):
    python3 add_video.py originals/mi-video.mov reel-02
    python3 add_video.py originals/mi-video.mov reel-02 --poster 2.5

Opciones avanzadas:
    --crf      calidad de compresión (por defecto 19; 18-20 es nitidez cristalina)
    --cas      filtro de nitidez adaptativo por contraste AMD CAS (por defecto 0.45)
    --target   MB límite si se necesita tope de peso estricto
    --poster   segundo exacto del vídeo del que sale la miniatura (por defecto 1.0)

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
    ap = argparse.ArgumentParser(description="Optimiza un reel a 1080x1920 con máxima nitidez.")
    ap.add_argument("source", help="Ruta al archivo original (.mov o .mp4)")
    ap.add_argument("name", help="Nombre identificador, por ejemplo reel-02")
    ap.add_argument("--crf", type=int, default=19, help="Calidad CRF de x264 (18-22, menor = más nítido)")
    ap.add_argument("--cas", type=float, default=0.45, help="Filtro de nitidez CAS (0.0 a 1.0)")
    ap.add_argument("--target", type=float, default=None, help="Límite estricto de MB (opcional)")
    ap.add_argument("--poster", type=float, default=1.0, help="Segundo del vídeo para la miniatura")
    args = ap.parse_args()

    if not os.path.exists(args.source):
        sys.exit("No existe: %s" % args.source)
    if subprocess.run(["which", "ffmpeg"], capture_output=True).returncode != 0:
        sys.exit("Falta ffmpeg. Instálalo con: brew install ffmpeg")

    os.makedirs(MEDIA, exist_ok=True)
    mp4 = os.path.join(MEDIA, args.name + ".mp4")
    jpg = os.path.join(MEDIA, args.name + ".jpg")

    duration = probe_duration(args.source)
    audio_kbps = 128

    # Filtro de video: Lanczos scaling a 1080x1920 + Contrast Adaptive Sharpening (CAS)
    vf_filters = [
        "scale=1080:1920:force_original_aspect_ratio=decrease:flags=lanczos",
        "pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
    ]
    if args.cas > 0:
        vf_filters.append(f"cas={args.cas:.2f}")
    vf_pipeline = ",".join(vf_filters)

    ffmpeg_cmd = [
        "ffmpeg", "-v", "error", "-y", "-i", args.source,
        "-vf", vf_pipeline,
        "-c:v", "libx264", "-profile:v", "high", "-level:v", "4.2", "-preset", "slow",
    ]

    if args.target:
        total_kbps = (args.target * 8192) / duration
        video_kbps = max(800, int(total_kbps - audio_kbps))
        ffmpeg_cmd.extend([
            "-b:v", "%dk" % video_kbps,
            "-maxrate", "%dk" % int(video_kbps * 1.5),
            "-bufsize", "%dk" % int(video_kbps * 2.5),
        ])
    else:
        ffmpeg_cmd.extend([
            "-crf", str(args.crf),
            "-maxrate", "6500k",
            "-bufsize", "10000k",
        ])

    ffmpeg_cmd.extend([
        "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-b:a", "%dk" % audio_kbps, "-ac", "2",
        "-movflags", "+faststart", mp4,
    ])

    print("Procesando vídeo en alta definición (1080x1920, CAS=%.2f)..." % args.cas)
    subprocess.run(ffmpeg_cmd, check=True)

    # Miniatura en calidad fotográfica (-q:v 2)
    poster_cmd = [
        "ffmpeg", "-v", "error", "-y", "-ss", str(args.poster), "-i", args.source,
        "-frames:v", "1",
        "-vf", vf_pipeline,
        "-q:v", "2", jpg,
    ]
    subprocess.run(poster_cmd, check=True)

    mb = os.path.getsize(mp4) / 1048576.0
    mins, secs = divmod(int(duration), 60)
    print("✓ media/%s.mp4  %.2f MB (1080x1920)  %d:%02d [NÍTIDO]" % (args.name, mb, mins, secs))
    print("✓ media/%s.jpg  miniatura HD lista (1080x1920, q=2)" % args.name)
    print()
    print("Pega esto en videos.json (o reemplaza un slot existente):")
    print(json.dumps({
        "id": args.name,
        "file": "media/%s.mp4" % args.name,
        "poster": "media/%s.jpg" % args.name,
        "duration": "%d:%02d" % (mins, secs),
        "category": "tech",
        "title": "Brand Name or Product",
        "kind": "Talking Head + Captions",
    }, indent=2, ensure_ascii=False))
    print()
    print("Luego ejecuta: python3 build.py")


if __name__ == "__main__":
    main()
