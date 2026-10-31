import hashlib,json,re
from pathlib import Path
r=Path(__file__).resolve().parents[1];d=r/'dist'
expected='6d3a92e6054508ab36d61df103fc9dea611676ccbbb822b819102ddaac7fe49f'
for p in [r/'src/brand/mychems-wordmark-ivory.svg',d/'brand/mychems-wordmark-ivory.svg']:
 assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,p
assert hashlib.sha256((r/'src/brand/mychems-wordmark-ivory-1024.png').read_bytes()).hexdigest()=='f1ceb108a91185601869704cd9ee57bb8d507020cb241e68414936dc2675f849'
pages=[p for p in d.rglob('*.html') if p.name != '404.html'];assert len(pages)==218
for p in pages:
 s=p.read_text();assert s.count('class="site-wordmark"')==1,p
 assert 'alt="myChems"' in s and 'aria-label="myChems"' in s
 assert ('非公式' in s or 'unofficial' in s.lower()),p
 assert 'dateModified' in s
 assert 'JST' in s
assert (d/'sitemap.xml').read_text().count('<lastmod>2026-10-31T11:50:00+00:00</lastmod>')==0
assert (d/'sitemap.xml').read_text().count('<lastmod>2026-10-31T12:52:00+00:00</lastmod>')==216
assert (d/'sitemap.xml').read_text().count('<lastmod>2026-10-31T15:25:00+00:00</lastmod>')==2
assert len(json.loads((r/'data/works.json').read_text()))==57
assert len(json.loads((r/'data/people.json').read_text()))==36
print('PASS approved outline hashes, all 218 headers, unofficial notice, actual brand revision dates, 57 works/36 people')
