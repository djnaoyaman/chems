#!/usr/bin/env python3
"""dist/ の全ページを1枚のHTMLにまとめる（スマホやClaudeのプレビューでページ間リンクを確かめるため）。
  python3 tools/preview_bundle.py out.html
リンクはページ内で切り替わる。YouTubeとOGP画像は含まない。"""
import base64, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, 'dist'); out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'preview.html')
pages, css = {}, None
def inline_brand(match):
    asset = os.path.join(DIST, 'brand', 'mychems-wordmark-ivory.svg')
    with open(asset, 'rb') as handle:
        data = base64.b64encode(handle.read()).decode('ascii')
    return 'src="data:image/svg+xml;base64,' + data + '"'

for dp, _, fs in os.walk(DIST):
    for f in fs:
        if f != 'index.html': continue
        p = os.path.relpath(os.path.join(dp, f), DIST).replace(os.sep, '/')
        h = open(os.path.join(dp, f), encoding='utf-8').read()
        if css is None: css = re.search(r'<style>(.*?)</style>', h, re.S).group(1)
        lang = re.search(r'<html lang="(\w+)"', h).group(1)
        title = re.search(r'<title>(.*?)</title>', h, re.S).group(1)
        body = re.search(r'<body\b[^>]*>(.*)</body>', h, re.S).group(1)
        body = re.sub(r'<script>.*?</script>', '', body, flags=re.S)
        body = re.sub(r'src="[^"]*brand/mychems-wordmark-ivory\.svg"', inline_brand, body)
        pages[p] = [lang, title, body]
js = open(os.path.join(ROOT, 'src', 'site.js'), encoding='utf-8').read().strip()
js = 'window.__chemsInit=function(){\n' + js + '\n};'
with open(os.path.join(DIST, 'icons', 'mychems-icon-32.png'), 'rb') as handle:
    favicon = base64.b64encode(handle.read()).decode('ascii')
with open(os.path.join(DIST, 'icons', 'mychems-apple-touch-icon.png'), 'rb') as handle:
    touch_icon = base64.b64encode(handle.read()).decode('ascii')
data = json.dumps(pages, ensure_ascii=False).replace('</', '<\\/')
router = r'''
(function(){
var P=window.__P,cur='index.html',app=document.getElementById('app');
function show(p,frag){if(!P[p])p='index.html';cur=p;var d=P[p];document.documentElement.lang=d[0];document.title=d[1];
  app.innerHTML='<p class="pv">プレビュー版：ページ間のリンクを確かめるための1枚です。YouTubeと画像はここでは表示されません。</p>'+d[2];
  try{window.__chemsInit()}catch(e){}
  if(frag){var t=document.getElementById(frag);if(t){t.scrollIntoView();return}}window.scrollTo(0,0)}
function resolve(href){var u=new URL(href,'https://p.invalid/'+cur);var p=decodeURIComponent(u.pathname.slice(1));if(!p||p.endsWith('/'))p+='index.html';return [p,u.hash.slice(1)]}
document.addEventListener('click',function(e){var a=e.target.closest('a[href]');if(!a)return;var h=a.getAttribute('href');
  if(/^(https?:|mailto:|data:)/.test(h)){a.target='_blank';a.rel='noopener';return}
  e.preventDefault();
  if(h.charAt(0)==='#'){var t=document.getElementById(h.slice(1));if(t)t.scrollIntoView({behavior:'smooth'});return}
  var r=resolve(h);if(P[r[0]]){location.hash='#!/'+r[0]+(r[1]?'#'+r[1]:'')}});
function route(){var m=location.hash.match(/^#!\/([^#]+)(?:#(.*))?/);show(m?m[1]:'index.html',m?m[2]:'')}
window.addEventListener('hashchange',route);route();
})();'''
html = f'''<!DOCTYPE html>
<!-- WELCOME / NAOYA MIYAZAKI LAB. JAPAN / MY CHEMS（全ページ・プレビュー） / URL TBD -->
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="referrer" content="strict-origin-when-cross-origin"><title>my Chems</title>
<meta name="robots" content="noindex,nofollow"><meta name="theme-color" content="#000000">
<link rel="icon" type="image/png" sizes="32x32" href="data:image/png;base64,{favicon}">
<link rel="apple-touch-icon" sizes="180x180" href="data:image/png;base64,{touch_icon}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;600&family=Noto+Sans+JP:wght@400;700;900&display=swap" rel="stylesheet">
<style>{css}
:root{{padding-top:env(safe-area-inset-top,0px)}}
html{{scroll-padding-top:calc(env(safe-area-inset-top,0px) + 3rem)}}
.pv{{margin:0;padding:.45rem 1.25rem;font-size:.72rem;background:#FFDE22;color:#000;font-weight:700}}
</style></head><body><div id="app"></div>
<script>window.__P={data};</script>
<script>{js}</script>
<script>{router}</script>
</body></html>'''
open(out, 'w', encoding='utf-8').write(html)
print(len(pages), 'pages', round(len(html.encode()) / 1024 / 1024, 2), 'MB ->', out)
