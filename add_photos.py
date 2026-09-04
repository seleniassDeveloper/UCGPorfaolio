#!/usr/bin/env python3
"""Prepara fotos para la cuadricula de Instagram de la pagina.

Uso:
    python3 add_photos.py foto1.jpg foto2.png ...
    python3 add_photos.py ~/Desktop/insta/*.jpg

Las deja redimensionadas en media/fotos/ y numeradas por orden. Luego:
    python3 build.py
"""

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
FOTOS = os.path.join(ROOT, "media", "fotos")
ANCHO = 620  # pixeles; suficiente para una cuadricula de 3 columnas


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    os.makedirs(FOTOS, exist_ok=True)
    existentes = len([f for f in os.listdir(FOTOS) if f.lower().endswith(".jpg")])

    for i, src in enumerate(sys.argv[1:], start=existentes + 1):
        if not os.path.exists(src):
            print("No existe, la salto: %s" % src)
            continue
        dst = os.path.join(FOTOS, "%02d.jpg" % i)
        subprocess.run([
            "ffmpeg", "-v", "error", "-y", "-i", src,
            "-vf", "scale=%d:-2" % ANCHO, "-q:v", "5", dst,
        ], check=True)
        print("media/fotos/%02d.jpg  %.0f KB" % (i, os.path.getsize(dst) / 1024.0))

    print()
    print("Ahora: python3 build.py")


if __name__ == "__main__":
    main()
