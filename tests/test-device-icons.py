"""Check every published icon URL, legacy alias and maskable safe area."""
import base64
import json
import math
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
BASE = 'https://djnaoyaman.github.io/chems/'


class Icons(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'link' and attrs.get('rel') in ('icon', 'apple-touch-icon', 'manifest'):
            self.links.append(attrs)


pages = list(DIST.rglob('*.html'))
assert len(pages) == 110
for page in pages:
    source = page.read_text()
    assert '⚗' not in source, page
    parsed = Icons()
    parsed.feed(source)
    assert {'icon', 'apple-touch-icon', 'manifest'} <= {a['rel'] for a in parsed.links}, page
    url = urljoin(BASE, page.relative_to(DIST).as_posix())
    for attrs in parsed.links:
        resolved = urljoin(url, attrs['href'])
        assert resolved.startswith(BASE), (page, resolved)
        assert (DIST / resolved.removeprefix(BASE)).is_file(), (page, resolved)

manifest = json.loads((DIST / 'site.webmanifest').read_text())
for entry in manifest['icons']:
    image = Image.open(DIST / entry['src'])
    assert f'{image.width}x{image.height}' == entry['sizes']

for path in (DIST / 'icons').glob('mychems-*'):
    alias = path.with_name(path.name.removeprefix('mychems-'))
    assert path.read_bytes() == alias.read_bytes(), alias
    if path.suffix != '.png':
        continue
    image = Image.open(path)
    assert image.mode == 'RGB' and image.width == image.height, path
    assert image.getpixel((0, 0)) == (0, 0, 0), path
    # Tiny favicons are antialiased down to a few rows; still require visible ink.
    assert max(image.convert('L').getextrema()) > 64, path
    if 'maskable' in path.name:
        size = image.width
        for y in range(size):
            for x in range(size):
                if image.getpixel((x, y)) != (0, 0, 0):
                    assert math.hypot(x - size / 2, y - size / 2) <= size * .4, path

for name, source in [('favicon.ico', 'mychems-favicon.ico'),
                     ('apple-touch-icon.png', 'mychems-apple-touch-icon.png'),
                     ('apple-touch-icon-precomposed.png', 'mychems-apple-touch-icon.png')]:
    assert (DIST / name).read_bytes() == (DIST / 'icons' / source).read_bytes(), name
assert Image.open(DIST / 'favicon.ico').ico.sizes() == {(16, 16), (32, 32), (48, 48)}

preview = (ROOT / 'notes/preview.html').read_text()
logo = base64.b64encode((ROOT / 'src/brand/mychems-wordmark-ivory.svg').read_bytes()).decode()
assert 'data:image/svg+xml;base64,' + logo in preview
assert 'brand/mychems-wordmark-ivory.svg' not in preview
assert 'noindex,nofollow' in preview
for name in ('mychems-icon-32.png', 'mychems-apple-touch-icon.png'):
    embedded = base64.b64encode((DIST / 'icons' / name).read_bytes()).decode()
    assert 'data:image/png;base64,' + embedded in preview
print('PASS 110 pages, manifest, current/legacy/root icons, safe circles, standalone preview branding')
