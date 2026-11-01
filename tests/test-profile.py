import json,re,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
r=Path(__file__).resolve().parents[1];d=r/'dist'
pages=[p for p in d.rglob('*.html') if p.name != '404.html'];assert len(pages)==218
for name in ['profile/index.html','en/profile/index.html']:
 s=(d/name).read_text();assert 'https://djnaoyaman.github.io/profile.html' in s
 assert 'DJ Naoyaman' in s and 'dateModified' in s and 'brand-updated' in s
 for banned in ['50 brands','50ブランド','職歴','学歴','講演','足立区','15歳','education','employment','世界一','world’s best','life’s work']:
  assert banned not in s,(name,banned)
 schemas=[json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>',s,re.S)]
 assert any(x.get('@type')=='ProfilePage' and x['mainEntity']['url']=='https://djnaoyaman.github.io/profile.html' for x in schemas)
 assert ('これからも育てていきたいと思います' in s if name.startswith('profile') else 'I hope to keep adding to it' in s)
 assert ('事実には出典' in s if name.startswith('profile') else 'Facts carry sources' in s)
assert (d/'sitemap.xml').read_text().count('<lastmod>2026-10-31T11:50:00+00:00</lastmod>')==0
assert (d/'sitemap.xml').read_text().count('<lastmod>2026-11-01T08:22:00+00:00</lastmod>')==98
assert (d/'sitemap.xml').read_text().count('<lastmod>2026-11-01T09:23:00+00:00</lastmod>')==2
print('PASS compact bilingual profile, central author, 218 pages, two profile-specific source dates')

assert (d/'sitemap.xml').read_text().count('<lastmod>2026-11-01T10:08:00+00:00</lastmod>')==2

for p in pages:
 s=p.read_text(); label="Editor" if p.relative_to(d).parts[0]=="en" else "編者"
 assert re.search(r'<a href="[^\"]+">'+label+r'</a>',s),p

assert (d/'sitemap.xml').read_text().count('<lastmod>2026-11-01T12:24:00+00:00</lastmod>')==116
