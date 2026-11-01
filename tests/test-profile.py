import json,re,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
r=Path(__file__).resolve().parents[1];d=r/'dist'
pages=[p for p in d.rglob('*.html') if p.name != '404.html'];assert len(pages)==218
for name in ['profile/index.html','en/profile/index.html']:
 s=(d/name).read_text();assert 'https://djnaoyaman.github.io/profile.html' in s
 assert 'DJ Naoyaman' in s and 'dateModified' in s and 'brand-updated' in s
 for banned in ['50 brands','50ブランド','職歴','学歴','講演','足立区','15歳','education','employment']:
  assert banned not in s,(name,banned)
 schemas=[json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>',s,re.S)]
 assert any(x.get('@type')=='ProfilePage' and x['mainEntity']['url']=='https://djnaoyaman.github.io/profile.html' for x in schemas)
 assert ('世界一の非公式ファンサイトを目指して' in s if name.startswith('profile') else 'With the aim of building the world’s best unofficial fan site' in s)
 assert ('事実には出典' in s if name.startswith('profile') else 'Facts carry sources' in s)
assert (d/'sitemap.xml').read_text().count('<lastmod>2026-10-31T11:50:00+00:00</lastmod>')==0
assert (d/'sitemap.xml').read_text().count('<lastmod>2026-11-01T07:57:00+00:00</lastmod>')==218
print('PASS compact bilingual profile, central author, 218 pages, two profile-specific source dates')
