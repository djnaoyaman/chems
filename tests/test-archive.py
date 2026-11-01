"""Offline contract: evergreen navigation, retained research, dates and bilingual links."""
import json,re,unittest,sys,subprocess,tempfile,os
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
EXPECTED='2026-10-31T11:50:00+00:00'
EDITORIAL='2026-10-31T12:52:00+00:00'
LISTENING='2026-11-01T00:42:00+00:00'
class Archive(unittest.TestCase):
 def test_home(self):
  for prefix in ('','en/'):
   h=(ROOT/'dist'/prefix/'index.html').read_text()
   self.assertIn('archive-routes',h);self.assertIn('archive-albums',h)
   self.assertNotIn('class="nowlist"',h);self.assertNotIn('11年前',h);self.assertNotIn('eleven-',h)
   self.assertNotIn('now/index.html',h);self.assertIn('57',h)
 def test_old_urls(self):
  for prefix in ('','en/'):
   h=(ROOT/'dist'/prefix/'now/index.html').read_text()
   self.assertTrue('ニュースの掲載は終了' in h or 'News coverage has ended' in h)
   self.assertNotIn('class="nowlist"',h);self.assertNotIn('TOMORA at Tokyo Garden',h)
 def test_dates(self):
  expected=EXPECTED;pages=[p for p in (ROOT/'dist').rglob('*.html') if p.name != '404.html'];self.assertGreater(len(pages),200)
  for p in pages:
   h=p.read_text();self.assertIn(f'<time datetime="{LISTENING}">',h)
   expected=LISTENING if p.relative_to(ROOT/'dist').as_posix() in ('works/index.html','en/works/index.html') else EDITORIAL
   blocks=[json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>',h)]
   self.assertTrue(any(x.get('@type')=='WebPage' and x.get('dateModified')==expected for x in blocks),p)
  tree=ET.parse(ROOT/'dist/sitemap.xml');ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
  self.assertEqual({x.text for x in tree.findall('.//s:lastmod',ns)},{EDITORIAL,LISTENING})
  self.assertEqual(len(tree.findall('.//s:lastmod',ns)),len(pages))
  for url in tree.findall('s:url',ns):
   loc=url.find('s:loc',ns).text
   relative=loc.removeprefix('https://djnaoyaman.github.io/chems/')
   expected=LISTENING if relative in ('works/index.html','en/works/index.html') else EDITORIAL
   self.assertEqual(url.find('s:lastmod',ns).text,expected)
 def test_editorial_scope(self):
  llms=(ROOT/'dist/llms.txt').read_text()
  self.assertIn('Each language page has its own canonical URL.',llms)
  self.assertNotIn('Japanese pages are canonical',llms)
  self.assertNotIn('complete discography',llms)
  for name in ('index.html','en/index.html','about/index.html','en/about/index.html'):
   h=(ROOT/'dist'/name).read_text()
   for phrase in ('全アルバム、全シングル、全EP','Every album, single and EP'):
    self.assertNotIn(phrase,h)
  for prefix in ('','en/'):
   self.assertIn('data-k="all"',(ROOT/'dist'/prefix/'works/index.html').read_text())
 def test_research_preserved(self):
  self.assertEqual(len(json.loads((ROOT/'data/works.json').read_text())),57)
  self.assertEqual(len(json.loads((ROOT/'data/people.json').read_text())),36)
  self.assertEqual(len(json.loads((ROOT/'data/now.json').read_text())['items']),9)
  self.assertEqual(json.loads((ROOT/'config.json').read_text())['checked'],'2026-10-01')
  self.assertFalse(any('予定' in x['ja'] for x in json.loads((ROOT/'data/events.json').read_text())))
  self.assertEqual(len(json.loads((ROOT/'notes/retired-news/events-before-20261031.json').read_text())),22)
if __name__=='__main__':unittest.main()
