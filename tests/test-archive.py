"""Offline contract: evergreen navigation, retained research, dates and Japanese-only publication."""
import json,re,unittest,sys,subprocess,tempfile,os
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
EXPECTED='2026-10-31T11:50:00+00:00'
EDITORIAL='2026-11-01T08:22:00+00:00'
LISTENING='2026-11-01T09:23:00+00:00'
PROFILE='2026-11-01T10:08:00+00:00'
LABELS='2026-11-01T12:38:00+00:00'
JAPANESE='2026-11-01T12:30:00+00:00'
DISCLOSURE=LABELS
class Archive(unittest.TestCase):
 def test_home(self):
  for prefix in ('',):
   h=(ROOT/'dist'/prefix/'index.html').read_text()
   self.assertIn('archive-routes',h);self.assertIn('archive-albums',h)
   self.assertNotIn('class="nowlist"',h);self.assertNotIn('11年前',h);self.assertNotIn('eleven-',h)
   self.assertNotIn('now/index.html',h);self.assertIn('57',h)
 def test_old_urls(self):
  for prefix in ('',):
   h=(ROOT/'dist'/prefix/'now/index.html').read_text()
   self.assertTrue('ニュースの掲載は終了' in h or 'News coverage has ended' in h)
   self.assertNotIn('class="nowlist"',h);self.assertNotIn('TOMORA at Tokyo Garden',h)
 def test_dates(self):
  expected=EXPECTED;pages=[p for p in (ROOT/'dist').rglob('*.html') if p.name != '404.html'];self.assertEqual(len(pages),109)
  for p in pages:
   h=p.read_text();self.assertIn(f'<time datetime="{LABELS}">',h)
   expected=LABELS if p.relative_to(ROOT/'dist').as_posix() in ('works/index.html','about/index.html') else JAPANESE
   blocks=[json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>',h)]
   self.assertTrue(any(x.get('@type')=='WebPage' and x.get('dateModified')==expected for x in blocks),p)
  tree=ET.parse(ROOT/'dist/sitemap.xml');ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
  self.assertEqual({x.text for x in tree.findall('.//s:lastmod',ns)},{JAPANESE,LABELS})
  self.assertEqual(len(tree.findall('.//s:lastmod',ns)),len(pages))
  for url in tree.findall('s:url',ns):
   loc=url.find('s:loc',ns).text
   relative=loc.removeprefix('https://djnaoyaman.github.io/chems/')
   expected=LABELS if relative in ('works/index.html','about/index.html') else JAPANESE
   self.assertEqual(url.find('s:lastmod',ns).text,expected)
 def test_editorial_scope(self):
  llms=(ROOT/'dist/llms.txt').read_text()
  self.assertIn('公開本文は日本語のみです',llms)
  self.assertNotIn('Japanese pages are canonical',llms)
  self.assertNotIn('complete discography',llms)
  for name in ('index.html','about/index.html'):
   h=(ROOT/'dist'/name).read_text()
   for phrase in ('全アルバム、全シングル、全EP','Every album, single and EP'):
    self.assertNotIn(phrase,h)
  for prefix in ('',):
   self.assertIn('data-k="all"',(ROOT/'dist'/prefix/'works/index.html').read_text())
 def test_research_preserved(self):
  self.assertEqual(len(json.loads((ROOT/'data/works.json').read_text())),57)
  self.assertEqual(len(json.loads((ROOT/'data/people.json').read_text())),36)
  self.assertEqual(len(json.loads((ROOT/'data/now.json').read_text())['items']),9)
  self.assertEqual(json.loads((ROOT/'config.json').read_text())['checked'],'2026-10-01')
  self.assertFalse(any('予定' in x['ja'] for x in json.loads((ROOT/'data/events.json').read_text())))
  self.assertEqual(len(json.loads((ROOT/'notes/retired-news/events-before-20261031.json').read_text())),22)
 def test_footer_and_noncommercial_links(self):
  self.assertNotIn('amazon_associate_tag',json.loads((ROOT/'config.json').read_text()))
  purchase_pages=0
  for p in (ROOT/'dist').rglob('*.html'):
   if p.name=='404.html':continue
   h=p.read_text()
   footer=re.search(r'<footer class="gf">(.*?)</footer>',h,re.S).group(1)
   self.assertNotIn('thechemicalbrothers.com',footer)
   self.assertNotIn('Amazon',footer)
   for banned in ('ad-disclosure','Amazonアソシエイト','Amazon Associate','tag=naoyaman-22','rel="nofollow sponsored noopener"'):
    self.assertNotIn(banned,h)
   if 'class="own-link"' in h:
    purchase_pages+=1
    self.assertIn('https://www.amazon.co.jp/s?k=',h)
    self.assertNotRegex(h,r'(?:[?&]|&amp;)tag=')
  self.assertEqual(purchase_pages,57)
  for prefix in ('',):
   work=(ROOT/'dist'/prefix/'works/come-with-us/index.html').read_text()
   self.assertIn('https://www.thechemicalbrothers.com/',work)
 def test_japanese_only_publication(self):
  d=ROOT/'dist'
  self.assertFalse((d/'en').exists())
  self.assertFalse((d/'ogp/en').exists())
  self.assertTrue((ROOT/'texts/en').is_dir())
  for p in d.rglob('*.html'):
   h=p.read_text()
   self.assertIn('<html lang="ja">',h)
   self.assertNotIn('class="lang"',h)
   self.assertNotIn('hreflang="en"',h)
   self.assertNotIn('og:locale:alternate',h)
   for url in re.findall(r'(?:href|src)="([^"#]+)',h):
    self.assertNotIn('/chems/en/',url)
    self.assertFalse(url.startswith('en/') or '/en/' in url and not url.startswith(('http','data:')))
  for name in ('sitemap.xml','llms.txt','llms-full.txt'):
   self.assertNotIn('/chems/en/',(d/name).read_text())
  for release in json.loads((d/'listening/catalog.json').read_text())['releases']:
   self.assertEqual(set(release['articlePath']),{'ja'})
  preview=(ROOT/'notes/preview.html').read_text()
  self.assertNotIn('"en/index.html"',preview)
 def test_catalog_covers(self):
  h=(ROOT/'dist/works/index.html').read_text()
  cards=re.findall(r'<a class="el [^"\n]*catalog-cover-card".*?</a>',h,re.S)
  self.assertEqual(len(cards),57)
  self.assertEqual(sum('<img ' in x for x in cards),46)
  self.assertEqual(sum('catalog-cover-missing' in x for x in cards),11)
  for card in cards:
   self.assertIn('class="catalog-card-meta"',card)
   self.assertIn('class="nm"',card)
   self.assertEqual(card.count('<a '),1)
   self.assertNotRegex(card,r'art/(?:gtko|wgtt)\.jpg')
   if '<img ' in card:
    self.assertIn('alt=""',card);self.assertIn('loading="lazy"',card);self.assertIn('decoding="async"',card)
  self.assertNotRegex((ROOT/'dist/index.html').read_text(),r'<a class="[^"]*catalog-cover-card')
if __name__=='__main__':unittest.main()
