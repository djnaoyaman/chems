"""Offline contract: evergreen navigation, retained research, dates and bilingual links."""
import json,re,unittest,sys,subprocess,tempfile,os
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
EXPECTED='2026-10-31T11:50:00+00:00'
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
  expected=EXPECTED;pages=list((ROOT/'dist').rglob('*.html'));self.assertGreater(len(pages),200)
  for p in pages:
   h=p.read_text();self.assertIn(f'<time datetime="{expected}">',h)
   blocks=[json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>',h)]
   self.assertTrue(any(x.get('@type')=='WebPage' and x.get('dateModified')==expected for x in blocks),p)
  tree=ET.parse(ROOT/'dist/sitemap.xml');ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
  self.assertEqual({x.text for x in tree.findall('.//s:lastmod',ns)},{expected})
  self.assertEqual(len(tree.findall('.//s:lastmod',ns)),len(pages))
 def test_research_preserved(self):
  self.assertEqual(len(json.loads((ROOT/'data/works.json').read_text())),57)
  self.assertEqual(len(json.loads((ROOT/'data/people.json').read_text())),36)
  self.assertEqual(len(json.loads((ROOT/'data/now.json').read_text())['items']),9)
  self.assertEqual(json.loads((ROOT/'config.json').read_text())['checked'],'2026-10-01')
  self.assertFalse(any('予定' in x['ja'] for x in json.loads((ROOT/'data/events.json').read_text())))
  self.assertEqual(len(json.loads((ROOT/'notes/retired-news/events-before-20261031.json').read_text())),22)
if __name__=='__main__':unittest.main()
