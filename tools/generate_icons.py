#!/usr/bin/env python3
"""Export device icons from the approved myChems raster without redrawing it.

Run from any directory with Pillow installed. The full wordmark keeps its aspect
ratio on black; maskable exports fit inside the central 80% safe circle.
"""
import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'src/icons'
SOURCE = ROOT / 'src/brand/mychems-wordmark-ivory-1024.png'
SOURCE_SHA256 = 'f1ceb108a91185601869704cd9ee57bb8d507020cb241e68414936dc2675f849'


def render(size, maskable=False):
    mark = Image.open(SOURCE).convert('RGBA')
    width = round(size * (0.70 if maskable else 0.92))
    mark = mark.resize((width, round(width * mark.height / mark.width)), Image.Resampling.LANCZOS)
    icon = Image.new('RGBA', (size, size), '#000000')
    icon.alpha_composite(mark, ((size - mark.width) // 2, (size - mark.height) // 2))
    return icon.convert('RGB')


if __name__ == '__main__':
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_SHA256
    DEST.mkdir(exist_ok=True)
    for size in (16, 32, 48, 192, 512):
        render(size).save(DEST / f'mychems-icon-{size}.png')
    render(180).save(DEST / 'mychems-apple-touch-icon.png')
    for size in (192, 512):
        render(size, maskable=True).save(DEST / f'mychems-maskable-{size}.png')
    render(48).save(DEST / 'mychems-favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)],
                    append_images=[render(16), render(32)])
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(DEST.glob('mychems-*.png'))}
    print(json.dumps(hashes, indent=2))
