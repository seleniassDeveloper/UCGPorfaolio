#!/usr/bin/env python3
"""Prepara una foto tuya para el circulo del perfil.

Uso:
    python3 set_foto.py                       # coge la imagen mas reciente de esta carpeta
    python3 set_foto.py ~/Desktop/mi-foto.jpg
    python3 set_foto.py ~/Desktop/mi-foto.jpg --alto 0.15

Recorta un cuadrado centrado horizontalmente. --alto dice desde que parte de la
foto empieza el recorte (0 = arriba del todo, 0.5 = el centro). Por defecto 0.08,
que suele dejar la cara bien en una foto vertical.

Deja media/retrato.jpg. Luego: python3 build.py
"""

import argparse
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DST = os.path.join(ROOT, "media", "retrato.jpg")
LADO = 560


def medidas(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "json", path],
        capture_output=True, text=True, check=True,
    ).stdout
    s = json.loads(out)["streams"][0]
    return int(s["width"]), int(s["height"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", nargs="?",
                    help="ruta de la foto; si no la pones, coge la imagen mas "
                         "reciente que haya en esta carpeta")
    ap.add_argument("--alto", type=float, default=0.08,
                    help="desde donde empieza el recorte, de 0 (arriba) a 1")
    ap.add_argument("--zoom", type=float, default=1.0,
                    help="1 = recorte completo, 0.85 = mas cerca de la cara")
    args = ap.parse_args()

    if args.source:
        src = os.path.expanduser(args.source)
        if not os.path.exists(src):
            sys.exit("No existe: %s" % src)
    else:
        sueltas = []
        for ext in ("jpg", "jpeg", "png", "webp", "heic",
                    "JPG", "JPEG", "PNG", "WEBP", "HEIC"):
            sueltas.extend(glob.glob(os.path.join(ROOT, "*." + ext)))
        if not sueltas:
            sys.exit("Deja la foto en %s y vuelve a ejecutarlo, o pasame la ruta." % ROOT)
        src = max(sueltas, key=os.path.getmtime)
        print("Uso: %s" % os.path.basename(src))

    w, h = medidas(src)
    lado = max(16, int(min(w, h) * max(0.2, min(1.0, args.zoom))))
    x = (w - lado) // 2
    y = max(0, min(int(h * args.alto), h - lado))

    os.makedirs(os.path.dirname(DST), exist_ok=True)
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-i", src,
        "-vf", "crop=%d:%d:%d:%d,scale=%d:%d" % (lado, lado, x, y, LADO, LADO),
        "-q:v", "3", DST,
    ], check=True)

    print("media/retrato.jpg  %dx%d  %.0f KB" % (LADO, LADO, os.path.getsize(DST) / 1024.0))
    print("Si la cara sale mal encuadrada, prueba con --alto 0.02 o --alto 0.2")
    print()
    print("Ahora: python3 build.py")


if __name__ == "__main__":
    main()
