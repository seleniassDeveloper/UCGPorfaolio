# Portfolio UGC — Selenia

Página de una sola pieza para enviar a marcas. El vídeo y las fotos van **dentro**
del HTML (en base64), así que el archivo funciona solo: se puede enviar por email,
subir a cualquier hosting o publicar como artifact. No hay servidor ni CDN.

## Archivos

| Archivo | Para qué sirve |
|---|---|
| `videos.json` | Los datos: enlaces y vídeos. `reels` es la página en inglés, `reels_es` la de español |
| `i18n.json` | Todos los textos de la página, en inglés (`en`) y español (`es`) |
| `template.html` | El diseño. Los textos van como `{{t.clave}}` y salen de `i18n.json` |
| `build.py` | Junta plantilla + vídeos + fotos y escribe `dist/` (inglés) y `dist/es/` (español) |
| `vercel.json` | Hace que `ugc-es.iamselenia.com` muestre `dist/es/` |
| `add_video.py` | Comprime un vídeo nuevo y le saca la miniatura |
| `make_previews.py` | Saca el clip corto (el hook) que se ve dentro del teléfono del inicio |
| `add_photos.py` | Prepara fotos para la cuadrícula de Instagram |
| `set_foto.py` | Recorta tu foto de perfil para el círculo |
| `serve.py` | Abre la página en el navegador para verla antes de enviarla |
| `originals/` | Los vídeos tal como salen del móvil. No se publican |
| `media/` | Vídeos comprimidos, miniaturas, retrato y `fotos/`. Puedes ordenarlos en subcarpetas: `build.py` los busca por nombre |
| `media/photos/` | Fotos del diseño (recorte del inicio, moodboard, polaroids, contacto). Cualquier `media/<nombre>` que use `template.html` se publica solo |
| `dist/portfolio.html` | **El archivo que envías o subes** |
| `dist/artifact.html` | La misma página en formato artifact de Claude |

## Las cifras del perfil

En `videos.json`, en `"stats"`, hay tres huecos con el valor vacío. Mientras estén
vacíos **la fila de cifras no aparece** (mejor eso que enseñar números inventados).
Rellénalos con tus datos reales de TikTok:

```json
"stats": [
  { "value": "41.1K", "label_es": "Seguidores", "label_en": "Followers" },
  { "value": "5.2M",  "label_es": "Me gusta",   "label_en": "Likes" },
  { "value": "157K",  "label_es": "Visitas al perfil / mes", "label_en": "Monthly profile views" }
]
```

Lo mismo con cada vídeo: si rellenas `"views"` y `"likes"`, salen en grande debajo
de la miniatura, como en el diseño de referencia. Si los dejas vacíos sale el título.

## Añadir un vídeo nuevo

```bash
python3 add_video.py originals/mi-video.mov reel-02
```

Te dice cuánto pesa y te imprime el bloque JSON. Cópialo en `videos.json`
sustituyendo uno de los huecos (`"placeholder": true`), y luego:

```bash
python3 make_previews.py reel-02
python3 build.py
```

`make_previews.py` crea el clip ligero del teléfono del inicio. Si te lo saltas,
el teléfono usa el vídeo completo (funciona, pero carga más lento).

El orden de los vídeos en la página es el orden en `videos.json`. Para quitar uno
sin borrarlo, pon `"status": "hidden"`.

## Cambiar la foto de perfil

```bash
python3 set_foto.py ~/Desktop/mi-foto.jpg
python3 build.py
```

Recorta un cuadrado centrado. Si la cara queda mal encuadrada, ajusta `--alto 0.02`
(sube el recorte) o `--alto 0.2` (lo baja).

## Añadir fotos de Instagram

```bash
python3 add_photos.py ~/Desktop/insta/*.jpg
python3 build.py
```

La cuadrícula de fotos solo aparece si hay imágenes en `media/fotos/`.

## Ver la página antes de enviarla

```bash
python3 serve.py
```

## Límite de peso

Un artifact publicado no puede pasar de 16 MB, y el base64 engorda cada archivo un
33 %. Ahora la página pesa ~9,9 MB con un vídeo. Con más vídeos hay que comprimirlos
más (`--target 3`) y no pasarse con las fotos. `build.py` avisa si superas 15 MB.

## Antes de enviarla

- [ ] Pon tu foto de perfil con `set_foto.py` (ahora hay un fotograma del vídeo)
- [ ] Cambia el email en `videos.json` → `links.email` (ahora pone `hola@tuemail.com`)
- [ ] Añade tu Instagram en `links.instagram` si quieres que salga el icono
- [ ] Rellena `stats` con tus cifras reales
- [ ] Pon el nombre real de la marca del primer vídeo en `title_es` / `title_en`
- [ ] `python3 build.py` y revisa con `python3 serve.py`

## Idiomas

La página sale en español y tiene un botón ES / EN arriba a la derecha. Los textos
llevan `data-es` y `data-en` en `template.html`; si cambias uno, cambia los dos.
