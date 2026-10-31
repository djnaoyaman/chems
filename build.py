#!/usr/bin/env python3
"""ケミカル・ブラザーズ全史 ビルドスクリプト
  python3 build.py            … dist/ に日英の全ページとOGPを生成し、検証スイートを実行
  YT_API_KEY=... python3 build.py … YouTube埋め込み可否と日本での再生制限も確認
"""
import json, os, re, sys, math, shutil, posixpath, hashlib, html as H
from urllib.parse import quote
from datetime import date, datetime, timedelta, timezone
from tools.listening_catalog import catalog as listening_catalog
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, 'dist')
# This source revision changes shared archive navigation and the site-wide editorial structure.
BRAND_UPDATED = '2026-10-31T11:50:00+00:00'
# Only the bilingual home/about descriptions changed in this editorial correction.
EDITORIAL_UPDATED = '2026-10-31T12:39:00+00:00'
# Shared reading controls and accessibility additions change every content page.
SHARED_TOOLS_UPDATED = '2026-10-31T12:52:00+00:00'
LISTENING_UPDATED = '2026-10-31T16:10:00+00:00'
def page_modified(key):
    return max(SHARED_TOOLS_UPDATED, LISTENING_UPDATED if key == 'works' else (EDITORIAL_UPDATED if key in ('top', 'about') else BRAND_UPDATED))
J = lambda n: json.load(open(os.path.join(ROOT, 'data', n), encoding='utf-8'))
CFG = json.load(open(os.path.join(ROOT, 'config.json'), encoding='utf-8'))
WORKS, PEOPLE, SOURCES = J('works.json'), J('people.json'), J('sources.json')
EVENTS, NOW, SHELF, GLOSS = J('events.json'), J('now.json'), J('shelf.json'), J('glossary.json')
W = {w['id']: w for w in WORKS}
P = {p['id']: p for p in PEOPLE}
SRC = {s['id']: s for s in SOURCES}
LANGS = ['ja', 'en']
CSS = open(os.path.join(ROOT, 'src', 'site.css'), encoding='utf-8').read() + '\n' + open(os.path.join(ROOT, 'src', 'launch-tools.css'), encoding='utf-8').read()
JS = open(os.path.join(ROOT, 'src', 'premium-playback-hint.js'), encoding='utf-8').read() + '\n' + open(os.path.join(ROOT, 'src', 'site.js'), encoding='utf-8').read() + '\n' + open(os.path.join(ROOT, 'src', 'launch-tools.js'), encoding='utf-8').read()
esc = lambda s: H.escape(str(s), quote=True)
PAPER, BLACK = '#F2F1EC', '#000000'
UNPRINTED = ['#F2F1EC', '#000000', '#8A8A85', '#000000']

# ---------------------------------------------------------------- 文言
UI = {
 'ja': {'works': '作品・周期表', 'timeline': '年表', 'equations': '共作者', 'chain': '関係図', 'now': 'アーカイブへの案内', 'shelf': '別棚', 'about': 'このサイトについて', 'sources': '出典庫', 'profile': 'プロフィール',
        'lang_other': 'EN', 'album': 'スタジオアルバム', 'single': 'シングル', 'ep': 'EP',
        'listen': '聴く', 'record': '記録', 'tracklist': '収録曲', 'music': '音楽性', 'tech': 'テクノロジー', 'context': '周辺環境', 'testimony': '証言', 'reviews': 'レビュー', 'view': '私見', 'after': 'その後', 'own': '持つ', 'src': '出典',
        'date': '発売日', 'year': '発売', 'on': '収録', 'label': 'レーベル', 'formats': '形態', 'uk': 'UK最高位', 'charts': '各国の最高位', 'certs': '認定', 'featured': '参加', 'mv': 'MV監督', 'artwork': 'アートワーク', 'notes': '注記', 'guest': 'アルバムへの参加', 'singles_from': 'このアルバムのシングル', 'album_mv': 'アルバム収録曲のMV',
        'nochart': 'チャート入りなし', 'inelig': '集計対象外', 'bpm': 'BPM', 'key': 'キー', 'wait_measure': '計測待ち', 'm_rb': 'DJ Naoyamanのrekordboxによる解析値', 'm_an': '音源からの自動解析', 'm_album': 'アルバム単位では計測しません。各曲のページで表示します。',
        'todo_music': '構成、ビート、サンプル、音色、前作からの変化を書く枠。サンプル元と構成の秒数は出典付きで書き、聴感の描写は私見に回します。',
        'todo_tech': '制作機材、スタジオ、録音・編集の手法。本人とエンジニアの発言が見つかりしだい記載します。',
        'todo_context': '同時期のクラブ、レーベル、チャート、同時代の作品、社会の動きを書く枠。',
        'todo_testimony': '出典のある発言が見つかりしだい、原語と訳で載せます。',
        'todo_tracklist': '公式サイト等で確認でき次第、収録曲を記載します。',
        'todo_reviews': '出典のある批評家・メディアのレビューが見つかりしだい、原語と訳で載せます。',
        'todo_view': 'DJ Naoyamanの執筆待ち。',
        'todo_after': 'その後の使われ方や評価の変化を、出典がそろいしだい記載します。',
        'todo_own': 'Amazon・楽天のリンク枠。アソシエイト登録後に、広告表記とあわせて設置します。',
        'todo_listen': '公式動画の確認待ち', 'yt_channel': '公式YouTubeチャンネルを開く',
        'facade': '公式MV', 'from_album_mv': 'アルバムからの公式MV', 'official_src': '公式サイトが埋め込んでいる動画', 'open_yt': 'YouTubeで開く', 'art_cap': 'アートワーク（批評・紹介のための引用）', 'art_alt': 'のアートワーク', 'art_wait': 'ジャケット画像は準備中', 'facade_dir': '監督', 'facade_tap': 'タップでYouTubeの公式MVを読み込みます',
        'plates_ok': '版色（アートワークから抽出）', 'plates_no': '未刷り（版色は抽出待ち）', 'plate_names': ['地', 'インク1', 'インク2', '差し色'],
        'contrast': '文字コントラスト', 'body': '本文', 'heading': '見出し', 'fixed': 'インク1が基準の3:1に届かないため、見出しを文字色に補正',
        'pulse': '脈動 {bpm} BPM（仮。計測前）', 'pulse_ok': '脈動 {bpm} BPM（実測）',
        'from_album': '所属アルバム', 'included': '収録', 'nonalbum': 'アルバム未収録',
        'prev': '前の作品', 'next': '次の作品', 'atomic': '原子番号',
        'unofficial': 'このサイトはThe Chemical Brothersの公式サイトではありません。ファンによる非公式のアーカイブです。',
        'noads': 'DJ Naoyamanは、Amazonアソシエイト・プログラムの参加者です。このプログラムは、サイトがAmazon.co.jpへのリンクを通じて紹介料を得られる手段を提供することを目的としています。', 'checked': '確認日',
        'own_link': 'Amazon.co.jpで探す', 'own_note': '上記はAmazonアソシエイトのリンクです。',
        'kinds': {'all': 'すべて', 'work': '作品', 'live': 'ライブ', 'japan': '日本', 'society': '社会', 'scene': 'シーン', 'tech': '技術'}},
 'en': {'works': 'Works / periodic table', 'timeline': 'Timeline', 'equations': 'Collaborators', 'chain': 'Connections', 'now': 'Archive guide', 'shelf': 'Annex', 'about': 'About', 'sources': 'Sources', 'profile': 'Profile',
        'lang_other': '日本語', 'album': 'Studio album', 'single': 'Single', 'ep': 'EP',
        'listen': 'Listen', 'record': 'Record', 'tracklist': 'Tracklist', 'music': 'Music', 'tech': 'Technology', 'context': 'Context', 'testimony': 'Testimony', 'reviews': 'Reviews', 'view': 'View', 'after': 'Afterwards', 'own': 'Own', 'src': 'Sources',
        'date': 'Released', 'year': 'Released', 'on': 'On', 'label': 'Label', 'formats': 'Formats', 'uk': 'UK peak', 'charts': 'Peak positions', 'certs': 'Certifications', 'featured': 'Featuring', 'mv': 'Video', 'artwork': 'Artwork', 'notes': 'Notes', 'guest': 'Guest on the album', 'singles_from': 'Singles from the album', 'album_mv': 'Videos for album tracks',
        'nochart': 'Did not chart', 'inelig': 'Ineligible', 'bpm': 'BPM', 'key': 'Key', 'wait_measure': 'Not yet measured', 'm_rb': "From DJ Naoyaman's rekordbox analysis", 'm_an': 'Automatic analysis of the audio', 'm_album': 'Not measured for whole albums; see each track page.',
        'todo_music': 'Space for structure, beats, samples, sounds and what changed from the last record. Samples and timings go in with sources; how it sounds goes in the View.',
        'todo_tech': 'Gear, studio, recording and editing methods, added once statements from the band or engineers are found.',
        'todo_context': 'Space for the clubs, labels, charts, records and events around it.',
        'todo_testimony': 'Quotes go here with sources, in the original language with a translation, once found.',
        'todo_tracklist': 'The tracklist goes here once confirmed from the official site or another source.',
        'todo_reviews': 'Sourced critic and press reviews go here, in the original language with a translation, once found.',
        'todo_view': "Awaiting DJ Naoyaman's view.",
        'todo_after': 'Later uses and shifts in reputation, added once sourced.',
        'todo_own': 'Space for Amazon and Rakuten links, to be added with an advertising disclosure once registered.',
        'todo_listen': 'Official video not yet confirmed', 'yt_channel': 'Open the official YouTube channel',
        'facade': 'Official video', 'from_album_mv': 'Official video from the album:', 'official_src': 'The video embedded on the official site', 'open_yt': 'Open on YouTube', 'art_cap': 'Artwork (quoted for review and commentary)', 'art_alt': 'artwork', 'art_wait': 'Sleeve image to come', 'facade_dir': 'directed by', 'facade_tap': 'Tap to load the official video from YouTube',
        'plates_ok': 'Plate colours (taken from the artwork)', 'plates_no': 'Unprinted (plate colours pending)', 'plate_names': ['Ground', 'Ink 1', 'Ink 2', 'Accent'],
        'contrast': 'Contrast', 'body': 'body', 'heading': 'heading', 'fixed': 'Ink 1 falls short of 3:1, so the heading uses the text colour',
        'pulse': 'Pulse {bpm} BPM (provisional, not yet measured)', 'pulse_ok': 'Pulse {bpm} BPM (measured)',
        'from_album': 'From the album', 'included': 'Included on', 'nonalbum': 'Non-album single',
        'prev': 'Previous', 'next': 'Next', 'atomic': 'Atomic number',
        'unofficial': 'This is not the official site of The Chemical Brothers. It is an unofficial fan archive.',
        'noads': 'DJ Naoyaman is a participant in the Amazon Associates Program, an affiliate advertising program designed to provide a means for sites to earn fees by linking to Amazon.co.jp.', 'checked': 'Checked',
        'own_link': 'Find it on Amazon.co.jp', 'own_note': 'The link above is an Amazon Associates affiliate link.',
        'kinds': {'all': 'All', 'work': 'Work', 'live': 'Live', 'japan': 'Japan', 'society': 'Society', 'scene': 'Scene', 'tech': 'Technology'}},
}
KC = {'work': '#F2F1EC', 'live': '#FFDE22', 'japan': '#FF3355', 'society': '#A9A9A2', 'scene': '#3DE0E0', 'tech': '#9EF01A'}
CN = {'uk': 'UK', 'aus': 'AUS', 'aut': 'AUT', 'bel': 'BEL', 'fra': 'FRA', 'irl': 'IRL', 'nld': 'NLD', 'nz': 'NZ', 'swi': 'SWI', 'us': 'US', 'swe': 'SWE', 'usdance': 'US Dance'}
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
ERAS = [('dust', '1994', 'ダスト・ブラザーズ期', 'Dust Brothers era'), ('epd', '1995', '', ''), ('dyoh', '1997', '', ''), ('sur', '1999', '', ''), ('cwu', '2002', '', ''), ('ptb', '2005', '', ''), ('watn', '2007', '', ''), ('fur', '2010', '', ''), ('bite', '2015', '', ''), ('ng', '2019', '', ''), ('ftbf', '2023', '', '')]

def fdate(s, lang):
    if not s: return ''
    p = str(s).split('-')
    if lang == 'ja':
        return p[0] + '年' + (str(int(p[1])) + '月' if len(p) > 1 else '') + (str(int(p[2])) + '日' if len(p) > 2 else '')
    if len(p) == 1: return p[0]
    if len(p) == 2: return f'{MONTHS[int(p[1]) - 1]} {p[0]}'
    return f'{int(p[2])} {MONTHS[int(p[1]) - 1]} {p[0]}'

def lum(h):
    h = h.lstrip('#'); f = lambda i: (lambda v: v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4)(int(h[i:i + 2], 16) / 255)
    return .2126 * f(0) + .7152 * f(2) + .0722 * f(4)
def cr(a, b):
    x, y = lum(a), lum(b); return (max(x, y) + .05) / (min(x, y) + .05)
def text_on(bg): return PAPER if cr(PAPER, bg) >= cr(BLACK, bg) else BLACK
ART = os.path.join(ROOT, 'art')
def art_file(w):
    for ext in ('jpg', 'jpeg', 'png', 'webp'):
        f = os.path.join(ART, f"{w['id']}.{ext}")
        if os.path.exists(f): return f
    return None
def extract_plates(path):
    """アートワークから版色4色を取る：地＝最も面積の大きい色、インク1＝地との対比が最大の色、インク2＝次点、差し色＝最も彩度の高い色"""
    from PIL import Image
    import colorsys
    im = Image.open(path).convert('RGB'); im.thumbnail((160, 160))
    q = im.quantize(colors=8, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()[:24]; counts = sorted(q.getcolors(), reverse=True)
    cols = ['#%02X%02X%02X' % tuple(pal[i * 3:i * 3 + 3]) for _, i in counts]
    bg = cols[0]; rest = cols[1:] or [text_on(bg)]
    by_c = sorted(rest, key=lambda c: -cr(c, bg))
    ink1 = by_c[0]; ink2 = by_c[1] if len(by_c) > 1 else text_on(bg)
    sat = lambda c: colorsys.rgb_to_hsv(*[int(c[i:i + 2], 16) / 255 for i in (1, 3, 5)])[1]
    acc = max(rest, key=sat)
    return {'bg': bg, 'ink1': ink1, 'ink2': ink2, 'accent': acc, 'status': 'extracted', 'from': os.path.basename(path)}
def load_art_plates():
    for w in WORKS:
        f = art_file(w)
        if f and w['plates'].get('status') != 'manual': w['plates'] = extract_plates(f)
def palette(w):
    p = w['plates']
    return [p['bg'], p['ink1'], p['ink2'], p['accent']] if p['status'] == 'extracted' else UNPRINTED
def hsh(s): return int(hashlib.md5(s.encode()).hexdigest()[:8], 16)

# ---------------------------------------------------------------- ルーティング
def path(lang, key, arg=None):
    pre = '' if lang == 'ja' else 'en/'
    m = {'top': 'index.html', 'works': 'works/index.html', 'shelf': 'shelf/index.html', 'timeline': 'timeline/index.html',
         'equations': 'equations/index.html', 'chain': 'chain/index.html', 'now': 'now/index.html', 'sources': 'sources/index.html', 'about': 'about/index.html', 'profile': 'profile/index.html'}
    if key == 'work': return pre + f"works/{W[arg]['slug']}/index.html"
    if key == 'cat': return pre + f'shelf/{arg}/index.html'
    if key == 'person': return pre + f'equations/{arg}/index.html'
    return pre + m[key]
def rel(frm, to):
    r = posixpath.relpath(to, posixpath.dirname(frm) or '.')
    return r

def title_of(w, lang): return w['title']
def name_of(pid, lang): return P[pid]['name'][lang]

class Refs:
    def __init__(s): s.ids = []
    def __call__(s, ids):
        out = []
        for i in (ids if isinstance(ids, list) else [ids]):
            if i not in SRC: raise SystemExit(f'未登録の出典: {i}')
            if i not in s.ids: s.ids.append(i)
            n = s.ids.index(i) + 1
            out.append(f'<sup><a href="#src-{n}" aria-label="source {n}">{n}</a></sup>')
        return ''.join(out)
    def html(s, lang):
        if not s.ids: return ''
        li = ''.join(f'<li id="src-{n + 1}"><a href="{esc(SRC[i]["url"])}" target="_blank" rel="noopener">{esc(SRC[i]["publisher"])}「{esc(SRC[i]["title"])}」</a></li>' if lang == 'ja' else
                     f'<li id="src-{n + 1}"><a href="{esc(SRC[i]["url"])}" target="_blank" rel="noopener">{esc(SRC[i]["publisher"])}, “{esc(SRC[i]["title"])}”</a></li>' for n, i in enumerate(s.ids))
        return f'<ol class="srcs" aria-label="{UI[lang]["src"]}">{li}</ol>'

USAGE = {}  # 出典の逆リンク
PAGES = {}  # path -> dict(lang, key, html, ogp)

# ---------------------------------------------------------------- 署名
BANNER_FONT = {
 'W': ['##   ##', '##   ##', '##   ##', '## # ##', '#######', '### ###', '##   ##'],
 'E': ['#######', '##     ', '##     ', '#####  ', '##     ', '##     ', '#######'],
 'L': ['##     ', '##     ', '##     ', '##     ', '##     ', '##     ', '#######'],
 'C': [' ##### ', '##   ##', '##     ', '##     ', '##     ', '##   ##', ' ##### '],
 'O': [' ##### ', '##   ##', '##   ##', '##   ##', '##   ##', '##   ##', ' ##### '],
 'M': ['##   ##', '### ###', '#######', '## # ##', '##   ##', '##   ##', '##   ##'],
 'N': ['##   ##', '###  ##', '#### ##', '## ####', '##  ###', '##   ##', '##   ##'],
 'A': ['  ###  ', ' ## ## ', '##   ##', '##   ##', '#######', '##   ##', '##   ##'],
 'Y': ['##   ##', '##   ##', ' ## ## ', '  ###  ', '   ##  ', '   ##  ', '   ##  '],
 'I': ['####', ' ## ', ' ## ', ' ## ', ' ## ', ' ## ', '####'],
 'Z': ['#######', '     ##', '    ## ', '   ##  ', '  ##   ', ' ##    ', '#######'],
 'K': ['##   ##', '##  ## ', '## ##  ', '####   ', '## ##  ', '##  ## ', '##   ##'],
 'B': ['###### ', '##   ##', '##   ##', '###### ', '##   ##', '##   ##', '###### '],
 'J': ['     ##', '     ##', '     ##', '     ##', '##   ##', '##   ##', ' ##### '],
 'P': ['###### ', '##   ##', '##   ##', '###### ', '##     ', '##     ', '##     '],
 '.': ['  ', '  ', '  ', '  ', '  ', '##', '##'], ' ': ['   '] * 7,
}
def banner(text):
    return '\n'.join(' '.join(BANNER_FONT[c][r] for c in text).rstrip() for r in range(7))
def signature(is_top, lang):
    name, url = CFG['site_name_signature'], CFG['base_url'] or 'URL TBD'
    if is_top:
        body = '\n\n'.join(banner(t) for t in ['WELCOME', 'NAOYA MIYAZAKI', 'LAB. JAPAN'])
        return f'<!--\n{body}\n\n{name} / {url}\nUnofficial fan archive. Not affiliated with The Chemical Brothers.\n-->'
    return f'<!-- WELCOME / NAOYA MIYAZAKI LAB. JAPAN / {name} / {url} -->'

# ---------------------------------------------------------------- 共通レイアウト
FONTS = {'ja': 'family=Anton&family=IBM+Plex+Mono:wght@400;500&family=Noto+Sans+JP:wght@400;700;900',
         'en': 'family=Anton&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;600'}
NAV = ['works', 'timeline', 'equations', 'chain', 'shelf']
CRUMB_PARENT = {'work': 'works', 'cat': 'shelf', 'person': 'equations'}

def breadcrumb_ld(lang, key, arg, title, pg, base):
    if key == 'top': return None
    u = UI[lang]
    items = [{'@type': 'ListItem', 'position': 1, 'name': CFG['site_name'][lang], 'item': base + path(lang, 'top')}]
    if key in CRUMB_PARENT:
        pkey = CRUMB_PARENT[key]
        items.append({'@type': 'ListItem', 'position': 2, 'name': u[pkey], 'item': base + path(lang, pkey)})
    items.append({'@type': 'ListItem', 'position': len(items) + 1, 'name': title, 'item': base + pg})
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': items}

def reading_tools(lang):
    en = lang == 'en'
    return f'''<aside class="reading-tools" aria-label="{'Reading tools' if en else '読むための道具'}"><div class="reading-tools-actions"><button type="button" data-share>{'Share' if en else '共有'}</button><button type="button" data-copy>{'Copy link' if en else 'リンクをコピー'}</button><a href="#top">{'Back to top' if en else 'ページ上部へ'}</a></div><p role="status" aria-live="polite"></p><div class="manual-copy" hidden><label>{'Page address' if en else 'ページのURL'}<input type="text" readonly aria-label="{'Page address' if en else 'ページのURL'}"></label></div><details><summary>{'Keep this site handy' if en else 'ホーム画面から開く'}</summary><p>{'On iPhone or iPad, open this site in Safari and choose Add to Home Screen from Share. On Android, check your browser menu for Add to Home screen. Availability and wording vary by browser. This is a web shortcut; an internet connection is needed.' if en else 'iPhone・iPadではSafariの共有メニューから「ホーム画面に追加」を選びます。Androidではブラウザのメニューにある「ホーム画面に追加」を確認してください。表示や対応状況はブラウザにより異なります。Webサイトへのショートカットです。利用にはインターネット接続が必要です。'}</p></details></aside>'''

def layout(lang, key, arg, pg, title, desc, body, ogp, jsonld=None, cur=None):
    u = UI[lang]; other = 'en' if lang == 'ja' else 'ja'
    alt = {l: path(l, key, arg) for l in LANGS}
    site = CFG['site_name'][lang]
    full = site if key == 'top' else f'{title}｜{site}' if lang == 'ja' else f'{title} | {site}'
    base = CFG['base_url'].rstrip('/') + '/' if CFG['base_url'] else ''
    og_url = (base + ogp) if base else rel(pg, ogp)
    nav = ''.join(f'<a href="{rel(pg, path(lang, n))}"{" aria-current=\"page\"" if n == (cur or key) else ""}>{u[n]}</a>' for n in NAV)
    modified = page_modified(key)
    site_modified = max(SHARED_TOOLS_UPDATED, LISTENING_UPDATED)
    modified_jst = datetime.fromisoformat(site_modified).astimezone(timezone(timedelta(hours=9))).strftime('%Y-%m-%d %H:%M JST')
    listening_assets = (f'<link rel="stylesheet" href="{rel(pg, "listening/listening.css")}"><script type="module" src="{rel(pg, "listening/listening.mjs")}"></script>' if key == 'works' else '')
    page_ld = {'@context': 'https://schema.org', '@type': 'WebPage', 'url': base + pg, 'name': title, 'inLanguage': lang, 'dateModified': modified}
    lds = [page_ld] + [x for x in (jsonld, breadcrumb_ld(lang, key, arg, title, pg, base) if base else None) if x]
    ld = ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in lds)
    hre = ''.join(f'<link rel="alternate" hreflang="{l}" href="{(base + alt[l]) if base else rel(pg, alt[l])}">' for l in LANGS)
    hre += f'<link rel="alternate" hreflang="x-default" href="{(base + alt["ja"]) if base else rel(pg, alt["ja"])}">'
    canon = f'<link rel="canonical" href="{base + pg}">' if base else ''
    ga = CFG.get('ga_measurement_id', '')
    gtag = f'''<script async src="https://www.googletagmanager.com/gtag/js?id={ga}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{ga}');</script>''' if ga else ''
    og_locale_alt = 'en_GB' if lang == 'ja' else 'ja_JP'
    return f'''<!DOCTYPE html>
{signature(key == 'top', lang)}
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{gtag}
<title>{esc(full)}</title>
<meta name="description" content="{esc(desc)}">
{canon}{hre}
<meta property="og:type" content="{'website' if key == 'top' else 'article'}">
<meta property="og:site_name" content="{esc(site)}">
<meta property="og:title" content="{esc(full)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{og_url}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:type" content="image/png">
<meta property="og:image:alt" content="{esc(full)}">
<meta property="og:url" content="{(base + pg) if base else rel(pg, pg)}">
<meta property="og:locale" content="{'ja_JP' if lang == 'ja' else 'en_GB'}">
<meta property="og:locale:alternate" content="{og_locale_alt}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(full)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{og_url}">
<meta name="twitter:image:alt" content="{esc(full)}">
<meta name="theme-color" content="#000000">
<meta name="author" content="{esc(CFG['author'])}">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>⚗️</text></svg>">
<link rel="icon" href="{rel(pg, 'icons/favicon.ico')}" sizes="16x16 32x32 48x48">
<link rel="icon" type="image/png" sizes="32x32" href="{rel(pg, 'icons/icon-32.png')}">
<link rel="apple-touch-icon" href="{rel(pg, 'icons/apple-touch-icon.png')}" sizes="180x180">
<link rel="manifest" href="{rel(pg, 'site.webmanifest')}">
<meta name="apple-mobile-web-app-title" content="my Chems">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?{FONTS[lang]}&display=swap" rel="stylesheet">
<style>{CSS}</style>{ld}{listening_assets}
</head>
<body id="top">
<a class="skip-link" href="#main">{'本文へ' if lang == 'ja' else 'Skip to content'}</a>
<header class="gh"><div class="gh-in"><a class="home" href="{rel(pg, path(lang, 'top'))}" aria-label="myChems"><img class="site-wordmark" src="{rel(pg, 'brand/mychems-wordmark-ivory.svg')}" alt="myChems" width="1799" height="504"></a><nav aria-label="{'サイト内' if lang == 'ja' else 'Site'}">{nav}</nav><a class="lang" href="{rel(pg, alt[other])}" hreflang="{other}" lang="{other}">{u['lang_other']}</a></div></header>
<main id="main" tabindex="-1">
{body}
</main>
{reading_tools(lang)}
<footer class="gf"><div class="gf-in"><nav><a href="{rel(pg, path(lang, 'about'))}">{u['about']}</a><a href="{rel(pg, path(lang, 'profile'))}">{u['profile']}</a><a href="{rel(pg, path(lang, 'sources'))}">{u['sources']}</a><a href="https://www.thechemicalbrothers.com/" target="_blank" rel="noopener">thechemicalbrothers.com</a></nav><p>{u['unofficial']}</p><p class="brand-updated small">{'サイト最終更新' if lang == 'ja' else 'Site last updated'}: <time datetime="{site_modified}">{modified_jst}</time></p><p id="ad-disclosure">{u['noads']}</p></div></footer>
<script>{JS}</script>
</body>
</html>
'''

def emit(lang, key, arg, title, desc, body, ogp_spec, jsonld=None, cur=None, refs=None):
    pg = path(lang, key, arg)
    ogp = f"ogp/{lang}/{pg.replace('en/', '').replace('/index.html', '').replace('index.html', 'top') or 'top'}.png"
    PAGES[pg] = {'lang': lang, 'key': key, 'arg': arg, 'ogp': ogp, 'ogp_spec': ogp_spec,
                 'html': layout(lang, key, arg, pg, title, desc, body, ogp, jsonld, cur)}
    if refs:
        for i in refs.ids: USAGE.setdefault(i, set()).add((lang, pg, title))

# ---------------------------------------------------------------- 部品
def tile(w, lang, pg, cls='', show_name=True):
    bg, i1, i2, _ = palette(w); fg = text_on(bg); sc = i1 if cr(i1, bg) >= 3 else fg
    band = ''
    if w['type'] == 'single' and w.get('album'):
        band = f';--band:{palette(W[w["album"]])[0]}'
        if palette(W[w['album']])[0] == bg: band = f';--band:{UNPRINTED[2]}'
    nm = f'<span class="nm">{esc(w["title"])}<br>{w["year"]}</span>' if show_name else ''
    no = f'<span class="no">{w["atomic"]}</span>' if show_name else ''
    return (f'<a class="el {w["type"]} {cls}" data-kind="{w["type"]}" href="{rel(pg, path(lang, "work", w["id"]))}" style="--bg:{bg};--fg:{fg};--ink2:{i2};--sc:{sc}{band}" '
            f'aria-label="{esc(w["title"])}（{w["year"]}）">{no}<span class="sym">{esc(w["symbol"])}</span>{nm}</a>')

def ptable(lang, pg):
    u = UI[lang]
    h = f'<div class="ph">{"時代" if lang == "ja" else "Era"}</div><div class="ph">{u["album"] if lang == "en" else "アルバム"}</div><div class="ph">{u["single"]}</div><div class="ph">EP</div>'
    for k, y, lj, le in ERAS:
        cols = []
        for t in ['album', 'single', 'ep']:
            ws = [w for w in WORKS if w['era'] == k and w['type'] == t]
            cols.append(''.join(tile(w, lang, pg) for w in ws) or '<div class="none"></div>')
        lab = lj if lang == 'ja' else le
        h += f'<div class="era">{y}{f"<small>{lab}</small>" if lab else ""}</div>' + ''.join(f'<div class="stack">{c}</div>' for c in cols)
    return f'<div class="ptable" id="ptable">{h}</div>'

def people_links(ids, lang, pg):
    return '、'.join(f'<a href="{rel(pg, path(lang, "person", i))}">{esc(name_of(i, lang))}</a>' for i in ids) if lang == 'ja' else \
           ', '.join(f'<a href="{rel(pg, path(lang, "person", i))}">{esc(name_of(i, lang))}</a>' for i in ids)

def text_blocks(wid, lang):
    fp = os.path.join(ROOT, 'texts', lang, f'{wid}.md')
    if not os.path.exists(fp): return {}, None
    raw = open(fp, encoding='utf-8').read()
    m = re.match(r'rev:\s*(\d+)\s*\n', raw); rev = int(m.group(1)) if m else None
    out = {}
    for sec in re.split(r'\n## ', '\n' + raw.split('\n', 1)[1] if m else raw)[1:]:
        k, _, body = sec.partition('\n'); out[k.strip()] = body.strip()
    return out, rev

def md(body, refs, lang):
    paras = [p.strip() for p in body.split('\n\n') if p.strip()]
    def sub(t):
        t = esc(t)
        t = re.sub(r'\{\{ref:([\w-]+)\}\}', lambda m: refs(m.group(1)), t)
        def ts(m):
            mm, ss = int(m.group(1)), int(m.group(2)); sec = mm * 60 + ss
            lab = f'{mm}分{ss:02d}秒' if lang == 'ja' else f'{mm}:{ss:02d}'
            return f'<a class="ts" href="#listen" data-t="{sec}">{lab}</a>'
        return re.sub(r'\{\{t:(\d+):(\d{2})\}\}', ts, t)
    return ''.join(f'<p>{sub(p)}</p>' for p in paras)

# ---------------------------------------------------------------- 作品ページ
def work_page(w, lang):
    u = UI[lang]; pg = path(lang, 'work', w['id']); refs = Refs(); R = w['records']
    bg, i1, i2, ac = palette(w); fg = text_on(bg); t_ok = cr(i1, bg) >= 3; tt = i1 if t_ok else fg
    blend = 'multiply' if lum(bg) > .3 else 'screen'
    h = hsh(w['id']); mx = f'{.02 + (h % 31) / 1000:.3f}em'; my = f'{((h >> 5) % 41 - 20) / 1000:.3f}em'
    rep = W[w['embed']['mv']['from_work']] if w['embed']['mv'] and w['embed']['mv'].get('from_work') else w
    bpm = w.get('bpm') or rep.get('bpm') or 120; eff = bpm / 2 if bpm > 180 else bpm
    n = len(w['title']); ts = 'clamp(7rem,40vw,14rem)' if n <= 3 else 'clamp(3.6rem,17vw,8.5rem)' if n <= 10 else 'clamp(3rem,13vw,7rem)' if n <= 17 else 'clamp(2.5rem,10.5vw,6rem)'
    tri = i1 if cr(i1, '#000000') >= 3 else PAPER
    style = f'--tri:{tri};--bg:{bg};--ink1:{i1};--ink2:{i2};--acc:{ac};--fg:{fg};--tt:{tt};--blend:{blend};--mx:{mx};--my:{my};--bpm-eff:{eff};--ts:{ts}'
    band = ''
    if w['type'] == 'single':
        if w.get('album'):
            a = W[w['album']]; ab = palette(a)[0]; ab = UNPRINTED[2] if ab == bg else ab
            style += f';--band:{ab};--bandfg:{text_on(ab)}'
            band = f'<div class="band"><div class="wrap">{u["from_album"]}{"『" if lang == "ja" else " "}<a href="{rel(pg, path(lang, "work", a["id"]))}">{esc(a["title"])}</a>{"』" if lang == "ja" else ""}</div></div>'
    # 見出し周り
    kind = u[w['type']] if w['type'] != 'album' else (f'{u["album"]} {sum(1 for x in WORKS if x["type"] == "album" and x["atomic"] <= w["atomic"])}作目' if lang == 'ja' else f'{u["album"]} no. {sum(1 for x in WORKS if x["type"] == "album" and x["atomic"] <= w["atomic"])}')
    if 'date' in R: dtxt = fdate(R['date']['v'], lang)
    elif 'date_note' in R: dtxt = R['date_note']['v'][lang]
    else: dtxt = fdate(str(w['year']), lang)
    names = u['plate_names']; pal = palette(w)
    plates = ''.join(f'<span class="sw"><i style="background:{c}"></i>{names[k]} {c}</span>' for k, c in enumerate(pal))
    ptag = u['plates_ok'] if w['plates']['status'] == 'extracted' else u['plates_no']
    readout = f'{u["contrast"]}　{u["body"]} {cr(fg, bg):.1f}:1　{u["heading"]} {cr(tt, bg):.1f}:1' + ('' if t_ok else f'　{u["fixed"]}')
    tempo = (u['pulse_ok'] if (w.get('bpm') or rep.get('bpm')) else u['pulse']).format(bpm=f'{bpm:g}')
    # 聴く
    emb = w['embed']['mv']
    if emb:
        src_w = W[emb['from_work']] if emb.get('from_work') else w
        mvdir = [c['person'] for c in src_w['credits'] if c['role'] == 'mv']
        dirs = people_links(mvdir, lang, pg) if mvdir else ''
        dirs_plain = re.sub('<[^>]+>', '', dirs)
        head = (f'{u["from_album_mv"]}「{emb["track"]}」' if lang == 'ja' else f'{u["from_album_mv"]} "{emb["track"]}"') if emb.get('track') else u['facade']
        lab = (f'{head}（{dirs_plain}{u["facade_dir"]}）' if lang == 'ja' else f'{head}, {u["facade_dir"]} {dirs_plain}') if dirs_plain else head
        thumb = f'https://i.ytimg.com/vi/{esc(emb["id"])}/hqdefault.jpg'
        listen = (f'<div class="player" id="listen" data-yt="{esc(emb["id"])}" data-title="{esc(w["title"])}">'
                  f'<button class="facade" type="button" data-yt="{esc(emb["id"])}" aria-label="{esc(lab)}">'
                  f'<img class="poster" src="{thumb}" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer" onerror="this.remove()">'
                  f'<span class="play" aria-hidden="true"></span><span class="cap">{esc(lab)}<small>{u["facade_tap"]}</small></span></button>'
                  f'<p class="alt">{u["official_src"]}{refs(emb["src"])}　<a href="https://www.youtube.com/watch?v={esc(emb["id"])}" target="_blank" rel="noopener">{u["open_yt"]}</a></p></div>')
    else:
        listen = f'<div class="player" id="listen"><p><a href="{esc(CFG["youtube_channel"])}" target="_blank" rel="noopener">{u["yt_channel"]}</a></p></div>'
    # アートワーク
    art = art_file(w)
    if art:
        asrc = w.get('art_src') or []
        cap = (u['art_cap'] + (refs(asrc) if asrc else '')) 
        artwork = f'<figure class="art"><img src="{rel(pg, "art/" + os.path.basename(art))}" alt="{esc(w["title"])} {u["art_alt"]}" width="600" height="600" loading="eager"><figcaption>{cap}</figcaption></figure>'
    else:
        artwork = f'<figure class="art none" aria-label="{u["art_wait"]}"><span class="sym">{esc(w["symbol"])}</span><figcaption>{u["art_wait"]}</figcaption></figure>'
    # 記録
    rows = []
    def row(k, v): rows.append(f'<div><dt>{k}</dt><dd>{v}</dd></div>')
    if 'date' in R: row(u['date'], fdate(R['date']['v'], lang) + refs(R['date']['src']))
    if 'date_note' in R: row(u['date'], esc(R['date_note']['v'][lang]) + refs(R['date_note']['src']))
    if 'year' in R and 'date' not in R: row(u['year'], fdate(str(R['year']['v']), lang) + refs(R['year']['src']))
    if w['type'] == 'single':
        if w.get('album'):
            a = W[w['album']]; row(u['on'], f'<a href="{rel(pg, path(lang, "work", a["id"]))}">{esc(a["title"])}</a>' + refs(R['year']['src']))
        elif 'album_note' in R:
            v = R['album_note']['v']
            row(u['on'], (esc(v) if v else u['nonalbum']) + refs(R['album_note']['src']))
    if 'label' in R: row(u['label'], esc(R['label']['v']) + refs(R['label']['src']))
    if 'formats' in R: row(u['formats'], esc(R['formats']['v']) + refs(R['formats']['src']))
    if 'uk_history' in R:
        hist = R['uk_history']['v']
        row(u['uk'], '<br>'.join((f'{x["peak"]}位（{fdate(x["when"], lang)}）' if lang == 'ja' else f'No. {x["peak"]} ({fdate(x["when"], lang)})') + refs(x['src']) for x in hist))
    elif 'uk' in R:
        v = R['uk']['v']; row(u['uk'], ((f'{v}位' if lang == 'ja' else f'No. {v}') if v else u['nochart']) + refs(R['uk']['src']))
    if 'uk_sub' in R: row(u['notes'], esc(R['uk_sub']['v'][lang]) + refs(R['uk_sub']['src']))
    if 'charts' in R:
        ch = R['charts']['v']
        if w['type'] == 'album':
            cells = ''.join(f'<span><b>{CN[c]}</b>{(v if v else ("—" if not (c == "uk" and w["id"] == "fur") else u["inelig"]))}</span>' for c, v in ch.items())
            row(u['charts'], f'<div class="charts">{cells}</div>' + refs(R['charts']['src']))
        else:
            cells = ''.join(f'<span><b>{CN[c]}</b>{v if v else "—"}</span>' for c, v in ch.items())
            if cells: row(u['charts'], f'<div class="charts">{cells}</div>' + refs(R['charts']['src']))
    if 'certs' in R: row(u['certs'], esc(R['certs']['v']) + refs(R['certs']['src']))
    for role, lab in [('featured', u['featured']), ('album-guest', u['guest']), ('mv', u['mv']), ('artwork', u['artwork'])]:
        cs = [c for c in w['credits'] if c['role'] == role]
        if cs:
            ids = []; srcs = []
            for c in cs: ids.append(c['person']); srcs += c['src']
            extra = ''
            if role == 'album-guest': extra = '（' + '、'.join(esc(c.get('track', '')) for c in cs) + '）' if lang == 'ja' else ' (' + ', '.join(esc(c.get('track', '')) for c in cs) + ')'
            row(lab, people_links(ids, lang, pg) + extra + refs(list(dict.fromkeys(srcs))))
    for nt in w['notes']: row(u['notes'], esc(nt[lang]) + refs(nt['src']))
    if w['type'] == 'album':
        sg = [x for x in WORKS if x.get('album') == w['id']]
        if sg: row(u['singles_from'], ('、' if lang == 'ja' else ', ').join(f'<a href="{rel(pg, path(lang, "work", x["id"]))}">{esc(x["title"])}</a>' for x in sg) + refs('wp-disc'))
        if w.get('album_mv'):
            row(u['album_mv'], '<br>'.join(f'{esc(m["title"])}：{people_links(m["directors"], lang, pg)}' if lang == 'ja' else f'{esc(m["title"])}: {people_links(m["directors"], lang, pg)}' for m in w['album_mv']) + refs('wp-disc'))
    rec = f'<section class="blk rec"><h2>{u["record"]}</h2><dl>{"".join(rows)}</dl></section>'
    if w.get('tracklist'):
        trows = ''
        for t in w['tracklist']:
            no = f'<span class="n">{esc(str(t.get("no", "")))}</span>' if t.get('no') is not None else ''
            if t.get('work') and t['work'] in W:
                tw = W[t['work']]
                main = f'<a href="{rel(pg, path(lang, "work", tw["id"]))}">{esc(t["title"])}</a>'
            else:
                main = f'<span>{esc(t["title"])}</span>'
            trows += f'<li>{no}{main}{refs(t.get("src", []))}</li>'
        tracklist = f'<section class="blk"><h2>{u["tracklist"]}</h2><ol class="tracklist">{trows}</ol></section>'
    else:
        tracklist = ''
    tx, _ = text_blocks(w['id'], lang)
    wm_ = u['wait_measure']
    if w['type'] == 'album':
        mrows = f'<p class="muted small">{u["m_album"]}</p>'
    else:
        how = {'rekordbox': u['m_rb'], 'analysis': u['m_an']}.get((w.get('measure') or {}).get('method'), '')
        bpm_v = (f'{w["bpm"]:g} BPM' if w.get('bpm') else f'<span class=todo>{wm_}</span>')
        key_v = (f'{w["key"]}' + (f'（{w["camelot"]}）' if lang == 'ja' and w.get('camelot') else f' ({w["camelot"]})' if w.get('camelot') else '') if w.get('key') else f'<span class=todo>{wm_}</span>')
        mrows = (f'<dl><div><dt>{u["bpm"]}</dt><dd>{bpm_v}</dd></div><div><dt>{u["key"]}</dt><dd>{key_v}</dd></div>'
                 + (f'<div><dt>{u["notes"]}</dt><dd>{how}</dd></div>' if how else '') + '</dl>')
    music = f'<section class="blk rec"><h2>{u["music"]}</h2>{mrows}' + (md(tx['music'], refs, lang) if 'music' in tx else '') + '</section>'
    tech = f'<section class="blk"><h2>{u["tech"]}</h2>' + (md(tx['tech'], refs, lang) if 'tech' in tx else '') + '</section>'
    if w.get('context'):
        ctx = '<ul>' + ''.join(f'<li>{esc(c[lang])}{refs(c["src"])}</li>' for c in w['context']) + '</ul>'
    elif 'context' in tx:
        ctx = md(tx['context'], refs, lang)
    else:
        ctx = ''
    context = f'<section class="blk"><h2>{u["context"]}</h2>{ctx}</section>'
    if w['testimony']:
        tq = ''
        for t in w['testimony']:
            tr = f'<p class="tr">「{esc(t["ja"])}」</p>' if lang == 'ja' and t['orig_lang'] != 'ja' else ''
            tq += f'<blockquote><p class="o" lang="{t["orig_lang"]}">“{esc(t["orig"])}”</p>{tr}<footer>{esc(t["who"][lang])}{"。" if lang == "ja" else ". "}{esc(t["ctx"][lang])}{refs(t["src"])}</footer></blockquote>'
    else:
        tq = ''
    testimony = f'<section class="blk"><h2>{u["testimony"]}</h2>{tq}</section>'
    if w.get('reviews'):
        rq = ''
        for rv in w['reviews']:
            tr = f'<p class="tr">「{esc(rv["ja"])}」</p>' if lang == 'ja' and rv.get('orig_lang') != 'ja' else ''
            rating = f'<span class="rating">{esc(rv["rating"])}</span>' if rv.get('rating') else ''
            who = esc(rv['publication']) + (f'　{esc(rv["critic"])}' if lang == 'ja' and rv.get('critic') else f', {esc(rv["critic"])}' if rv.get('critic') else '')
            rq += f'<blockquote><p class="o" lang="{rv.get("orig_lang", "en")}">“{esc(rv["orig"])}”</p>{tr}<footer>{who}{rating}{refs(rv.get("src", []))}</footer></blockquote>'
        reviews = f'<section class="blk"><h2>{u["reviews"]}</h2>{rq}</section>'
    else:
        reviews = ''
    tn = '<p class="tn">Translated from the Japanese original.</p>' if lang == 'en' and 'view' in tx else ''
    view_body = md(tx['view'], refs, lang) if 'view' in tx else ''
    view = (f'<section class="blk view"><h2><span>{u["view"]}（<a href="{rel(pg, path(lang, "profile"))}">DJ Naoyaman</a>）</span></h2>{view_body}{tn}</section>' if lang == 'ja' else
            f'<section class="blk view"><h2><span>{u["view"]} (<a href="{rel(pg, path(lang, "profile"))}">DJ Naoyaman</a>)</span></h2>{view_body}{tn}</section>')
    if w['after']:
        af = '<ul class="after">' + ''.join(f'<li><span class="d">{fdate(a["when"], lang)}</span><span>{esc(a[lang])}{refs(a["src"])}</span></li>' for a in w['after']) + '</ul>'
    else:
        af = ''
    after = f'<section class="blk"><h2>{u["after"]}</h2>{af}</section>'
    tag = CFG.get('amazon_associate_tag')
    if tag:
        q = quote(f'{w["title"]} The Chemical Brothers')
        az_url = f'https://www.amazon.co.jp/s?k={q}&tag={quote(tag)}'
        own_body = (f'<p><a class="own-link" href="{az_url}" target="_blank" rel="nofollow sponsored noopener">{u["own_link"]}</a></p>'
                    f'<p class="muted small">{u["own_note"]}</p>')
    else:
        own_body = ''
    own = f'<section class="blk"><h2>{u["own"]}</h2>{own_body}</section>'
    # 前後
    k = WORKS.index(w)
    prv = WORKS[k - 1] if k > 0 else None; nxt = WORKS[k + 1] if k < len(WORKS) - 1 else None
    pn = '<nav class="pn" aria-label="prev/next">' + (f'<a href="{rel(pg, path(lang, "work", prv["id"]))}"><span>{u["prev"]}</span>{esc(prv["title"])}</a>' if prv else '<span></span>') + \
         (f'<a href="{rel(pg, path(lang, "work", nxt["id"]))}" style="text-align:right"><span>{u["next"]}</span>{esc(nxt["title"])}</a>' if nxt else '<span></span>') + '</nav>'
    body = f'''<article class="work" style="{style}">{band}<div class="ht pulse" aria-hidden="true"></div>
<div class="work-in">
<div class="wm" aria-hidden="true">{esc(w["symbol"])}<small>{w["atomic"]}</small></div>
<p class="kind"><span>{kind}</span><span>{dtxt}</span><span>{u["atomic"]} {w["atomic"]}</span></p>
<h1 class="wtitle print">{esc(w["title"])}</h1>
{artwork}
<p class="plates-row">{plates}<span class="tag">{ptag}</span></p>
<p class="readout">{readout}</p>
<p class="tempo"><span>{tempo}</span><button class="motion" type="button"></button></p>
<div class="blocks"><section class="blk"><h2>{u['listen']}</h2>{listen}</section>{rec}{tracklist}{music}{tech}{context}{testimony}{reviews}{view}{after}{own}</div>
{refs.html(lang)}
{pn}
</div></article>'''
    base_ = CFG['base_url'].rstrip('/') + '/' if CFG['base_url'] else ''
    art_f = art_file(w)
    ld = {'@context': 'https://schema.org', '@type': 'MusicAlbum' if w['type'] != 'single' else 'MusicRecording', 'name': w['title'],
          'url': base_ + pg, 'genre': ['Electronic', 'Big Beat'],
          'byArtist': {'@type': 'MusicGroup', 'name': 'The Chemical Brothers', 'sameAs': ['https://www.thechemicalbrothers.com/', 'https://en.wikipedia.org/wiki/The_Chemical_Brothers']},
          'datePublished': str(R['date']['v'] if 'date' in R else w['year'])}
    if art_f: ld['image'] = base_ + 'art/' + os.path.basename(art_f)
    if R.get('label', {}).get('v'): ld['recordLabel'] = str(R['label']['v'])
    desc = (f'{w["title"]}（{w["year"]}年、{u[w["type"]]}）の記録、収録曲、音楽性、周辺環境、証言、レビュー、私見、その後。' if lang == 'ja' else
            f'{w["title"]} ({w["year"]}, {u[w["type"]].lower()}): record, tracklist, music, context, testimony, reviews, view and afterwards.')
    emit(lang, 'work', w['id'], w['title'], desc, body, {'type': 'work', 'w': w['id']}, ld, cur='works', refs=refs)

# ---------------------------------------------------------------- 各ページ
def all_events(lang):
    ev = []
    for w in WORKS:
        R = w['records']; d = R['date']['v'] if 'date' in R else str(w['year'])
        uk = None
        if 'uk_history' in R: uk = R['uk_history']['v'][0]['peak']
        elif 'uk' in R: uk = R['uk']['v']
        elif 'charts' in R: uk = R['charts']['v'].get('uk')
        kind = 'japan' if w['id'] == 'jpep' else 'work'
        ja = f'{UI["ja"][w["type"]]}『{w["title"]}』' + (f'。UK最高位{uk}位' if uk else '')
        en = f'{UI["en"][w["type"]]} {w["title"]}' + (f', UK No. {uk}' if uk else '')
        ev.append({'date': d, 'kind': kind, 'work': w['id'], 'ja': ja, 'en': en, 'src': ['wp-disc'] if 'date' not in R or R['date']['src'] == ['wp-disc'] else R['date']['src'], 'atomic': w['atomic'], 'auto': True})
    for e in EVENTS: ev.append({**e, 'atomic': 999})
    def key(e):
        p = e['date'].split('-'); y = int(p[0])
        return (y, 0 if e.get('auto') else 1, e['atomic'] if e.get('auto') else int(p[1]) if len(p) > 1 else 0, int(p[2]) if len(p) > 2 else 0)
    return sorted(ev, key=key)

def ev_li(e, lang, pg, refs=None):
    u = UI[lang]; dc = palette(W[e['work']])[0] if e.get('work') else KC[e['kind']]
    if dc == UNPRINTED[0] and e['kind'] != 'work': dc = KC[e['kind']]
    txt = esc(e[lang])
    if e.get('work'):
        t = W[e['work']]['title']
        link = f'<a class="w" href="{rel(pg, path(lang, "work", e["work"]))}">{esc(t)}</a>'
        txt = txt.replace(esc(t), link, 1) if esc(t) in txt else txt + f'（{link}）'
    for pid in e.get('people', []):
        nm = esc(name_of(pid, lang))
        if nm in txt: txt = txt.replace(nm, f'<a class="w" href="{rel(pg, path(lang, "person", pid))}">{nm}</a>', 1)
    p = e['date'].split('-')
    small = '' if len(p) == 1 else (fdate(e['date'], lang).split('年', 1)[1] if lang == 'ja' else ((p[2].lstrip('0') + ' ') if len(p) > 2 else '') + MONTHS[int(p[1]) - 1][:3])
    src = '、'.join(f'<a href="{esc(SRC[s]["url"])}" target="_blank" rel="noopener">{esc(SRC[s]["publisher"])}</a>' for s in e['src'])
    if refs is not None:
        for s in e['src']:
            if s not in refs.ids: refs.ids.append(s)
    art_html = ''
    if e.get('work'):
        af = art_file(W[e['work']])
        if af:
            art_html = f'<a class="tl-art" href="{rel(pg, path(lang, "work", e["work"]))}" tabindex="-1" aria-hidden="true"><img src="{rel(pg, "art/" + os.path.basename(af))}" alt="" width="80" height="80" loading="lazy" decoding="async"></a>'
    body = f'<div class="tl-body"><span class="chip">{u["kinds"][e["kind"]]}</span><p>{txt}</p><p class="src">{src}</p></div>'
    return f'<li data-kind="{e["kind"]}" style="--kc:{KC[e["kind"]]};--dc:{dc}"><span class="yr" id="y{p[0]}-{abs(hash(e[lang])) % 100000}">{p[0]}{f"<small>{small}</small>" if small else ""}</span><div class="tl-row">{art_html}{body}</div></li>'

def top_page(lang):
    u = UI[lang]; pg = path(lang, 'top'); refs = Refs()
    q = ['作品を聴く。', '反応をたどる。'] if lang == 'ja' else ['Listen to the works.', 'Trace the connections.']
    intro = ('ケミカル・ブラザーズの作品、音、映像と、それを生んだ人びと。ニュースの速さではなく、一作ずつ深く読み、聴くためのアーカイブ。' if lang == 'ja' else
             'The Chemical Brothers: records, sounds, images and the people behind them. An archive for listening closely, one work at a time—not a news feed.')
    counts = {k: sum(w['type'] == k for w in WORKS) for k in ('album', 'single', 'ep')}
    stats = (' / '.join(f'{counts[k]} {u[k]}' for k in counts))
    hero = f'''<section class="hero"><div class="ht pulse" aria-hidden="true" style="--bpm-eff:120"></div><div class="wrap">
<p class="archive-kicker">THE CHEMICAL BROTHERS / LISTENING ARCHIVE</p>
<h1 class="q">{''.join(f'<span class="print">{esc(x)}</span>' for x in q)}</h1><p class="archive-intro">{intro}</p>
<p class="archive-stats">{stats}</p><div class="hero-foot"><a class="jump" href="{rel(pg, path(lang, 'works'))}">{'作品から探す' if lang == 'ja' else 'Explore the works'}</a><a class="more" href="#start">{'どこから聴く？' if lang == 'ja' else 'Where to begin?'}</a><button class="motion" type="button"></button></div></div></section>'''
    routes = [
        ('epd', 'はじまりから' if lang == 'ja' else 'Start at the beginning', '最初のスタジオアルバムから、次の作品へ。' if lang == 'ja' else 'Begin with the first studio album, then follow the next work.'),
        ('dyoh', 'アルバムを深く' if lang == 'ja' else 'Go inside an album', '収録曲、参加者、制作の記録を行き来する。' if lang == 'ja' else 'Move between tracks, collaborators and production notes.'),
        ('sg', '映像から聴く' if lang == 'ja' else 'Listen through film', 'MVと楽曲、監督のほかの仕事をたどる。' if lang == 'ja' else 'Connect the video, the track and the director’s other work.')]
    starts = ''.join(f'<article class="archive-route">{tile(W[wid], lang, pg)}<h3>{title}</h3><p>{text}</p><a class="more" href="{rel(pg, path(lang, "work", wid))}">{esc(W[wid]["title"])}</a></article>' for wid, title, text in routes)
    albums = ''.join(tile(w, lang, pg) for w in WORKS if w['type'] == 'album')
    guides = [('timeline', '発売順と時代背景を読む。' if lang == 'ja' else 'Read releases alongside their historical context.'), ('equations', '声、演奏、映像、アートワークを担う人びと。' if lang == 'ja' else 'Meet the voices, players, filmmakers and visual artists.'), ('chain', '出典のあるクレジットから作品同士をつなぐ。' if lang == 'ja' else 'Follow connections grounded in credited collaborations.'), ('shelf', 'ミックス、ライブ映画、リミックス、別名義の作品へ。' if lang == 'ja' else 'Explore mixes, concert films, remixes and side projects.')]
    guide_html = ''.join(f'<a class="archive-guide" href="{rel(pg, path(lang, key))}"><h3>{u[key]}</h3><p>{text}</p></a>' for key, text in guides)
    body = hero + f'''<div class="wrap">
<section class="s" id="start"><h2 class="sh">{'聴き始める、3つの入口' if lang == 'ja' else 'Three ways into the music'}</h2><p class="muted">{'順位ではなく、読み方の提案です。' if lang == 'ja' else 'Reading routes, not a ranking.'}</p><div class="archive-routes">{starts}</div></section>
<section class="s"><h2 class="sh">{'アルバムでたどる' if lang == 'ja' else 'Follow the albums'}</h2><div class="archive-albums">{albums}</div><p><a class="more" href="{rel(pg, path(lang, 'works'))}">{'全' + str(len(WORKS)) + '作品を周期表で見る' if lang == 'ja' else 'Explore all ' + str(len(WORKS)) + ' works in the periodic table'}</a></p></section>
<section class="s"><h2 class="sh">{'作品の向こう側へ' if lang == 'ja' else 'Beyond the record'}</h2><div class="archive-guides">{guide_html}</div></section>
<section class="s"><h2 class="sh">{'記録と私見を分けて読む' if lang == 'ja' else 'Facts and personal views, kept apart'}</h2><p>{'発売・制作の事実には出典を。DJ Naoyamanの私見は独立した欄へ。速報や公演予定の配信は行わず、作品と歴史を読み直す場所として編集しています。' if lang == 'ja' else 'Release and production facts carry sources. DJ Naoyaman’s personal views have their own space. This site does not publish news or upcoming-event listings; it is edited as a record of the music and its history.'}</p><p><a class="more" href="{rel(pg, path(lang, 'about'))}">{u['about']}</a></p></section></div>'''
    desc = 'ケミカル・ブラザーズのアルバム、シングル、EPを、出典付きの記録と私見で読むアーカイブ。' if lang == 'ja' else 'An archive of albums, singles and EPs by The Chemical Brothers, read through sourced records and personal views.'
    base_ = CFG['base_url'].rstrip('/') + '/' if CFG['base_url'] else ''
    ld = {'@context': 'https://schema.org', '@type': 'WebSite', 'name': CFG['site_name'][lang], 'url': base_ + pg, 'inLanguage': lang, 'description': desc,
          'about': {'@type': 'MusicGroup', 'name': 'The Chemical Brothers', 'sameAs': ['https://www.thechemicalbrothers.com/', 'https://en.wikipedia.org/wiki/The_Chemical_Brothers']},
          'author': {'@type': 'Person', 'name': 'DJ Naoyaman', 'alternateName': ['宮崎直哉', 'Naoya Miyazaki'], 'url': 'https://djnaoyaman.github.io/profile.html'}}
    emit(lang, 'top', None, CFG['site_name'][lang], desc, body, {'type': 'top'}, ld, refs=refs)

def listening_section(lang):
    ja = lang == 'ja'
    matched = len(J('listening-sources.json')['bindings'])
    total = sum(len(w.get('tracklist', [])) for w in WORKS)
    title = '公式音源で聴く' if ja else 'Listen to official recordings'
    intro = (f'発売順で作品を選び、確認できた公式YouTube音源を聴くための棚です。現在は{total}曲枠のうち{matched}曲で公式配信と録音版を照合済み。実再生は未確認です。未照合の曲を別版や非公式投稿で埋めません。' if ja else
             f'Choose a release chronologically and listen through official YouTube sources. {matched} of {total} track entries currently have official-source and recording matches; playback remains untested. Missing tracks are not replaced with other versions or unofficial uploads.')
    return f'''<section id="listening" class="listening-shell" aria-labelledby="listening-title"><h2 id="listening-title">{title}</h2><p>{intro}</p>
<button type="button" data-listening="start">{'▶ 照合済みの公式音源から聴く' if ja else '▶ Start with a matched official recording'}</button>
<div class="listening-grid"><div><label>{'種類' if ja else 'Release type'}<select data-listening="type"><option value="all">{'収録作品すべて' if ja else 'All cataloged releases'}</option><option value="album">{'アルバム' if ja else 'Albums'}</option><option value="ep">EP</option><option value="single">{'シングル' if ja else 'Singles'}</option></select></label>
<label>{'作品' if ja else 'Release'}<select data-listening="release"><option value="">{'作品を選ぶ' if ja else 'Choose a release'}</option></select></label>
<ol class="listening-tracklist" data-listening="tracks"></ol></div>
<aside class="listening-dock" data-listening="dock" aria-label="{'音楽プレイヤー' if ja else 'Music player'}" hidden><div class="listening-dock-top"><span>MYCHEMS / LISTENING</span><button type="button" data-listening="close" aria-label="{'停止して閉じる' if ja else 'Stop and close'}">×</button></div><h3 data-listening="heading">{'作品を選んでください' if ja else 'Choose a release'}</h3><p data-listening="edition"></p><p data-listening="coverage"></p>
<div class="listening-visual" data-listening="visual" aria-label="YouTube player">{'動画はまだ読み込んでいません。' if ja else 'No video loaded.'}</div>
<p data-listening="now" class="listening-now"></p><p class="listening-continuity"><label><input type="checkbox" data-listening="continuous"> {'この作品を曲順に続けて聴く（未照合・再生不可の曲で停止）' if ja else 'Continue in this release (stop at unmatched or unavailable tracks)'}</label></p><p class="listening-status" data-listening="status" role="status" aria-live="polite"></p><div class="listening-controls"><button type="button" data-listening="previous" disabled>{'前の曲' if ja else 'Previous track'}</button><button type="button" data-listening="load" disabled>{'▶ 再生' if ja else '▶ Play'}</button><button type="button" data-listening="pause" disabled>{'一時停止' if ja else 'Pause'}</button><button type="button" data-listening="stop" disabled>{'停止' if ja else 'Stop'}</button><button type="button" data-listening="next" disabled>{'次の曲' if ja else 'Next track'}</button><button type="button" data-listening="full" aria-expanded="false">{'拡大' if ja else 'Expand'}</button></div><p class="listening-sources" data-listening="sources"></p>
<p class="small">{'動画を読み込むとYouTubeに接続します。再生可否は地域・環境・時期によって変わります。ページを移動すると再生は終了します。' if ja else 'Loading a video connects to YouTube. Availability depends on region, environment and time. Navigating away stops playback.'}</p></aside></div>
<noscript>{'このプレイヤーにはJavaScriptが必要です。作品の記事と既存のYouTubeリンクをご利用ください。' if ja else 'This player needs JavaScript. Articles and their existing YouTube links remain available.'}</noscript></section>'''

def works_page(lang):
    u = UI[lang]; pg = path(lang, 'works')
    kinds = [('all', u['kinds']['all']), ('album', u['album']), ('single', u['single']), ('ep', 'EP')]
    fl = f'<div class="filters" data-target="ptable" role="group">' + ''.join(f'<button type="button" data-k="{k}" aria-pressed="{"true" if k == "all" else "false"}">{t}</button>' for k, t in kinds) + '</div>'
    lead = ('行は時代（スタジオアルバム期）、列は種別。時代は所属アルバムを優先し、所属のない作品は直前のスタジオアルバム期に置いています。原子番号は発売順で、発売日の確定前の仮です。' if lang == 'ja' else
            'Rows are eras (studio album periods), columns are formats. A work sits in the era of its album, or of the latest studio album if it has none. Atomic numbers follow release order and are provisional until release dates are confirmed.')
    legend = ('白い枠線はEP、左の帯は所属アルバムの版色。版色が未抽出の作品は未刷りの紙色で表示しています。' if lang == 'ja' else
              'Dashed outlines mark EPs; the band on the left is the plate colour of the parent album. Works without extracted plate colours are shown unprinted.')
    body = f'''<div class="wrap"><header class="page-h"><h1>{u['works']}</h1><p class="lead">{lead}</p></header><p><a href="#listening">{'公式音源で聴く' if lang == 'ja' else 'Listen to official recordings'} ↓</a></p>{fl}{ptable(lang, pg)}<p class="legend">{legend}</p>
<p><a class="more" href="{rel(pg, path(lang, 'shelf'))}">{'別棚（プロモ盤、ミックス、コンピ、サントラ、リミックス、TOMORA）' if lang == 'ja' else 'Annex (promos, mixes, compilations, soundtracks, remixes, TOMORA)'}</a></p></div>'''
    body += '<div class="wrap">' + listening_section(lang) + '</div>'
    emit(lang, 'works', None, u['works'], lead, body, {'type': 'plain', 'title': u['works'], 'sub': str(len(WORKS))}, cur='works')

def shelf_pages(lang):
    u = UI[lang]; pg = path(lang, 'shelf')
    cats = ''.join(f'<li><a href="{rel(pg, path(lang, "cat", k))}">{esc(v[lang])}<span>{len(v["items"])}{"件" if lang == "ja" else " items"}</span></a></li>' for k, v in SHELF.items())
    lead = '本棚（アルバム、シングル、EP）の外にある作品の一覧です。' if lang == 'ja' else 'Everything outside the main shelf of albums, singles and EPs.'
    emit(lang, 'shelf', None, u['shelf'], lead, f'<div class="wrap"><header class="page-h"><h1>{u["shelf"]}</h1><p class="lead">{lead}</p></header><ul class="cats">{cats}</ul></div>', {'type': 'plain', 'title': u['shelf']}, cur='shelf')
    for k, v in SHELF.items():
        cp = path(lang, 'cat', k); refs = Refs(); r = refs(v['src'])
        has_note = any(it[lang] for it in v['items'])
        rows = ''.join(f'<tr><td class="d">{fdate(it["date"], lang)}</td><td>{esc(it["title"])}</td>' + (f'<td>{esc(it[lang])}</td>' if has_note else '') + '</tr>' for it in v['items'])
        th = ('<tr><th>年</th><th>作品</th>' + ('<th>注記</th>' if has_note else '') + '</tr>' if lang == 'ja' else '<tr><th>Date</th><th>Title</th>' + ('<th>Note</th>' if has_note else '') + '</tr>')
        body = f'''<div class="wrap"><header class="page-h"><h1>{esc(v[lang])}</h1><p class="lead"><a href="{rel(cp, path(lang, 'shelf'))}">{u['shelf']}</a>{r}</p></header>
<div class="scroll"><table class="t"><thead>{th}</thead><tbody>{rows}</tbody></table></div>{refs.html(lang)}</div>'''
        emit(lang, 'cat', k, v[lang], f'{v[lang]}（{u["shelf"]}）' if lang == 'ja' else f'{v[lang]} ({u["shelf"]})', body, {'type': 'plain', 'title': v[lang], 'sub': u['shelf']}, cur='shelf', refs=refs)

def timeline_page(lang):
    u = UI[lang]; pg = path(lang, 'timeline'); refs = Refs()
    evs = all_events(lang)
    fl = '<div class="filters" data-target="tl" role="group">' + ''.join(f'<button type="button" data-k="{k}" aria-pressed="{"true" if k == "all" else "false"}">{t}</button>' for k, t in u['kinds'].items()) + '</div>'
    years = sorted({e['date'][:4] for e in evs})
    items = ''; seen = set()
    for e in evs:
        li = ev_li(e, lang, pg, refs); y = e['date'][:4]
        if y not in seen: li = li.replace('<li ', f'<li id="year-{y}" ', 1); seen.add(y)
        items += li
    yj = '<nav class="years" aria-label="years">' + ''.join(f'<a href="#year-{y}">{y}</a>' for y in years) + '</nav>'
    lead = '1本の線に、作品と出来事を並べています。種別はラベルで区別し、絞り込めます。' if lang == 'ja' else 'Works and events on a single line. Labels mark the kind, and you can filter by them.'
    body = f'<div class="wrap"><header class="page-h"><h1>{u["timeline"]}</h1><p class="lead">{lead}</p></header>{fl}{yj}<ol class="tl" id="tl">{items}</ol></div>'
    emit(lang, 'timeline', None, u['timeline'], lead, body, {'type': 'plain', 'title': u['timeline'], 'sub': f'{years[0]}–{years[-1]}'}, refs=refs)

def person_works(pid):
    out = []
    for w in WORKS:
        for c in w['credits']:
            if c['person'] == pid: out.append((w, c))
        for m in w.get('album_mv', []):
            if pid in m['directors']: out.append((w, {'role': 'album-mv', 'track': m['title'], 'src': m['src']}))
    return out

ROLE = {'ja': {'featured': '参加', 'mv': 'MV監督', 'artwork': 'アートワーク', 'album-guest': 'アルバムへの参加', 'album-mv': '収録曲のMV'},
        'en': {'featured': 'Featured', 'mv': 'Video director', 'artwork': 'Artwork', 'album-guest': 'Guest on the album', 'album-mv': 'Video for an album track'}}

def equations_pages(lang):
    u = UI[lang]; pg = path(lang, 'equations')
    groups = [('featured', '声と演奏' if lang == 'ja' else 'Voices'), ('mv', '映像' if lang == 'ja' else 'Film'), ('artwork', 'アートワーク' if lang == 'ja' else 'Artwork')]
    def main_role(pid):
        rs = [c['role'] for _, c in person_works(pid)]
        if 'artwork' in rs: return 'artwork'
        if any(r in ('featured', 'album-guest') for r in rs): return 'featured'
        return 'mv'
    html_ = ''
    for g, lab in groups:
        ps = [p for p in PEOPLE if main_role(p['id']) == g]
        html_ += f'<section class="s"><h2 class="sh">{lab}</h2><ul class="people">' + ''.join(
            f'<li><a href="{rel(pg, path(lang, "person", p["id"]))}"><b>{esc(p["name"][lang])}</b><span>{len({w["id"] for w, _ in person_works(p["id"])})}{"作品" if lang == "ja" else " works"}</span></a></li>' for p in ps) + '</ul></section>'
    lead = ('Tom＋Ed＋誰か→作品。クレジットで確認できた関わりを、人ごとの反応式として並べています。' if lang == 'ja' else
            'Tom + Ed + someone → a work. Each person\'s part, as confirmed by the credits, written as an equation.')
    emit(lang, 'equations', None, u['equations'], lead, f'<div class="wrap"><header class="page-h"><h1>{u["equations"]}</h1><p class="lead">{lead}</p></header>{html_}</div>', {'type': 'plain', 'title': u['equations'], 'sub': str(len(PEOPLE))})
    for p in PEOPLE:
        pp = path(lang, 'person', p['id']); refs = Refs(); pw = person_works(p['id'])
        ws = list(dict.fromkeys(w['id'] for w, _ in pw))
        eq = f'<p class="eq">Tom <span class="op">+</span> Ed <span class="op">+</span> {esc(p["name"]["en"])} <span class="op">→</span> {len(ws)}</p>'
        lis = ''
        for w, c in pw:
            extra = f'：{esc(c["track"])}' if lang == 'ja' and c.get('track') else f': {esc(c["track"])}' if c.get('track') else ''
            lis += f'<li>{tile(w, lang, pp, show_name=False)}<div><a class="t" href="{rel(pp, path(lang, "work", w["id"]))}">{esc(w["title"])}</a>{refs(c["src"])}<small>{w["year"]}　{ROLE[lang][c["role"]]}{extra}</small></div></li>'
        notes = ''.join(f'<li>{esc(n[lang])}{refs(n["src"])}</li>' for n in p['notes'])
        evs = [e for e in EVENTS if p['id'] in e.get('people', [])]
        evh = ('<section class="s"><h2 class="sh">' + u['timeline'] + '</h2><ol class="tl">' + ''.join(ev_li(e, lang, pp, refs) for e in evs) + '</ol></section>') if evs else ''
        nm = p['name'][lang]; sub = f'（{p["name"]["en"]}）' if lang == 'ja' and nm != p['name']['en'] else ''
        body = f'''<div class="wrap"><header class="page-h"><p class="muted small"><a href="{rel(pp, path(lang, 'equations'))}">{u['equations']}</a></p><h1>{esc(nm)}{esc(sub)}</h1>{eq}</header>
{f'<section class="s"><ul class="plain">{notes}</ul></section>' if notes else ''}
<section class="s"><h2 class="sh">{'関わった作品' if lang == 'ja' else 'Works'}</h2><ul class="worklist">{lis}</ul></section>{evh}{refs.html(lang)}</div>'''
        desc = f'{nm}とケミカル・ブラザーズの反応式。関わった作品と出典。' if lang == 'ja' else f'{nm} and The Chemical Brothers: the works they made together, with sources.'
        emit(lang, 'person', p['id'], nm, desc, body, {'type': 'plain', 'title': p['name']['en'], 'sub': u['equations']}, cur='equations', refs=refs)

def chain_page(lang):
    u = UI[lang]; pg = path(lang, 'chain'); refs = Refs(); refs('wp-disc')
    cx = cy = 400; R1, R2 = 355, 190; pos = {}
    for k, w in enumerate(WORKS):
        a = -math.pi / 2 + 2 * math.pi * k / len(WORKS); pos[w['id']] = (cx + R1 * math.cos(a), cy + R1 * math.sin(a), a)
    for k, p in enumerate(PEOPLE):
        a = -math.pi / 2 + 2 * math.pi * (k + .5) / len(PEOPLE); pos[p['id']] = (cx + R2 * math.cos(a), cy + R2 * math.sin(a), a)
    edges = []
    for p in PEOPLE:
        for w, c in person_works(p['id']):
            for s in c['src']:
                if s not in refs.ids: refs.ids.append(s)
            edges.append((p['id'], w['id'], c['role']))
    col = {'featured': '#F2F1EC', 'album-guest': '#F2F1EC', 'mv': '#FFDE22', 'album-mv': '#FFDE22', 'artwork': '#3DE0E0'}
    svg = [f'<svg viewBox="0 0 800 800" role="img" aria-label="{u["chain"]}">']
    for a_, b_, r in edges:
        x1, y1, _ = pos[a_]; x2, y2, _ = pos[b_]
        svg.append(f'<path d="M{x1:.1f},{y1:.1f} Q{cx},{cy} {x2:.1f},{y2:.1f}" fill="none" stroke="{col[r]}" stroke-opacity=".45" stroke-width="1"/>')
    for w in WORKS:
        x, y, a = pos[w['id']]; bg = palette(w)[0]
        svg.append(f'<a href="{rel(pg, path(lang, "work", w["id"]))}"><rect x="{x - 11:.1f}" y="{y - 11:.1f}" width="22" height="22" fill="{bg}"/><text x="{x:.1f}" y="{y + 3.5:.1f}" text-anchor="middle" style="fill:{text_on(bg)};font-family:Anton,Impact,sans-serif;font-size:11px">{esc(w["symbol"])}</text></a>')
    for p in PEOPLE:
        x, y, a = pos[p['id']]; anchor = 'start' if math.cos(a) >= 0 else 'end'; dx = 7 if anchor == 'start' else -7
        svg.append(f'<a href="{rel(pg, path(lang, "person", p["id"]))}"><circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#F2F1EC"/><text class="pl" x="{x + dx:.1f}" y="{y + 3:.1f}" text-anchor="{anchor}">{esc(p["name"]["en"])}</text></a>')
    svg.append('</svg>')
    legend = [('#F2F1EC', '参加' if lang == 'ja' else 'Featured'), ('#FFDE22', 'MV' if lang == 'ja' else 'Video'), ('#3DE0E0', 'アートワーク' if lang == 'ja' else 'Artwork')]
    lg = '<p class="legend">' + '　'.join(f'<span class="chip" style="--kc:{c}">{t}</span>' for c, t in legend) + '</p>'
    lead = (f'外周が本棚の{len(WORKS)}作品（発売順）、内側が人物。線はクレジットで確認できた共演とMV制作、アートワークだけです。サンプリングや言及など影響の線は、出典がそろいしだい足します。' if lang == 'ja' else
            f'The outer ring is the {len(WORKS)} works of the main shelf in release order; the inner ring is people. Lines show only collaborations, videos and artwork confirmed by the credits. Lines of influence, such as samples and citations, will be added once sourced.')
    lst = ''.join(f'<li><a href="{rel(pg, path(lang, "person", p["id"]))}">{esc(p["name"][lang])}</a> → ' + ('、' if lang == 'ja' else ', ').join(f'<a href="{rel(pg, path(lang, "work", i))}">{esc(W[i]["title"])}</a>' for i in dict.fromkeys(w["id"] for w, _ in person_works(p["id"]))) + '</li>' for p in PEOPLE)
    body = f'''<div class="wrap"><header class="page-h"><h1>{u['chain']}</h1><p class="lead">{lead}</p></header>{lg}<div class="chain">{''.join(svg)}</div>
<section class="s"><h2 class="sh">{'線の一覧' if lang == 'ja' else 'All lines'}</h2><ul class="plain">{lst}</ul></section>{refs.html(lang)}</div>'''
    emit(lang, 'chain', None, u['chain'], lead, body, {'type': 'plain', 'title': u['chain'], 'sub': f'{len(edges)}'}, refs=refs)

def now_page(lang):
    u = UI[lang]; pg = path(lang, 'now')
    lead = ('ニュースの掲載は終了しました。作品と歴史を読むアーカイブへ再構成しています。' if lang == 'ja' else 'News coverage has ended. The site is now organised around the music and its history.')
    links = ''.join(f'<li><a href="{rel(pg, path(lang, k))}">{u[k]}</a></li>' for k in NAV)
    body = f'<div class="wrap"><header class="page-h"><h1>{u["now"]}</h1><p class="lead">{lead}</p></header><section class="s"><h2 class="sh">{"次に読む" if lang == "ja" else "Continue exploring"}</h2><ul>{links}</ul></section></div>'
    emit(lang, 'now', None, u['now'], lead, body, {'type': 'plain', 'title': u['now']})

def sources_page(lang):
    u = UI[lang]; pg = path(lang, 'sources')
    rows = ''
    for s in SOURCES:
        used = sorted({(t, p_) for l, p_, t in USAGE.get(s['id'], set()) if l == lang})
        back = ('、' if lang == 'ja' else ', ').join(f'<a href="{rel(pg, p_)}">{esc(t)}</a>' for t, p_ in used[:12]) + (f' ほか{len(used) - 12}件' if lang == 'ja' and len(used) > 12 else f' and {len(used) - 12} more' if len(used) > 12 else '')
        rows += f'<tr><td>{esc(s["publisher"])}</td><td><a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["title"])}</a></td><td class="d">{esc(s["date"])}</td><td class="d">{s["lang"]}</td><td class="d">{s["checked"]}</td><td>{back}</td></tr>'
    th = '<tr><th>媒体</th><th>記事・ページ</th><th>日付</th><th>言語</th><th>確認日</th><th>使っているページ</th></tr>' if lang == 'ja' else '<tr><th>Publisher</th><th>Title</th><th>Date</th><th>Lang</th><th>Checked</th><th>Used on</th></tr>'
    lead = f'{len(SOURCES)}件。事実の根拠にしたページの一覧と、それを使っているページへの逆リンクです。' if lang == 'ja' else f'{len(SOURCES)} sources behind the facts, with links back to the pages that use them.'
    body = f'<div class="wrap"><header class="page-h"><h1>{u["sources"]}</h1><p class="lead">{lead}</p></header><div class="scroll"><table class="t"><thead>{th}</thead><tbody>{rows}</tbody></table></div></div>'
    emit(lang, 'sources', None, u['sources'], lead, body, {'type': 'plain', 'title': u['sources'], 'sub': str(len(SOURCES))}, cur='sources')

def about_page(lang):
    u = UI[lang]
    if lang == 'ja':
        secs = [('方針', 'ニュース速報・今後の公演予定は扱いません。作品、制作、共作者、歴史を中心に編集します。ケミカル・ブラザーズを「触媒」として読むアーカイブです。触媒は反応を起こしても、自分は消費されずに残る。このサイトで取り上げるアルバム、シングル、EPを本棚に、それ以外を別棚に置き、反応の記録として並べています。'),
                ('事実と私見', '事実には必ず出典を付けます。出典のない事実は載せず、空欄の枠のまま残します。私見はDJ Naoyaman名義で書き、色を反転させたブロックに分けています。英語版の私見は日本語の原文からの翻訳です。'),
                ('出典の扱い', '出典庫に全出典の媒体、日付、言語、確認日を記録し、使っているページへ逆リンクを張っています。'),
                ('引用', '証言は短く引用し、原語と訳を並べます。歌詞は載せません。'),
                ('画像と色', 'ジャケット画像は、各作品ページでの紹介と批評のための引用として掲載し、出典を示します。公式ロゴは使いません。版色はアートワークから抽出し、画像がまだない作品は未刷りの紙色で表示します。'),
                ('埋め込み', '埋め込みはYouTubeの公式動画だけです。優先順は公式MV、公式ライブ映像、公式音源（Topic）です。'),
                ('広告表記', 'アフィリエイトのリンクは各作品ページの「持つ」欄にだけ置き、レビュー本文には入れません。リンクの近くと共通フッターに広告である旨を表示し、Amazonアソシエイトの定型文を掲載しています。'),
                ('制作', 'DJ Naoyaman（宮崎直哉）。プロフィールは別ページにまとめています。')]
        gl = '<dl class="gloss">' + ''.join(f'<dt>{esc(g["ja"])}</dt><dd>{esc(g["en"])}</dd>' for g in GLOSS) + '</dl>'
        gh = '用語集（日英）'
    else:
        secs = [('Policy', 'This site does not cover news or upcoming events. It focuses on works, production, collaborators and history. This archive reads The Chemical Brothers as a catalyst: something that starts a reaction and comes out of it unchanged. The albums, singles and EPs covered here sit on the main shelf, everything else in the annex, laid out as a record of the reactions.'),
                ('Facts and views', 'Every fact carries a source. Facts without one are left out, and their place stays marked as an empty slot. Views are written by DJ Naoyaman and set apart in inverted blocks. English views are translated from the Japanese original.'),
                ('Sources', 'The Sources page records each source\'s publisher, date, language and the date it was checked, with links back to the pages that use it.'),
                ('Quotes', 'Testimony is quoted briefly, in the original language with a translation. No lyrics are reproduced.'),
                ('Images and colour', 'Sleeve images appear on each work page as quotations for review and commentary, with their source shown. No official logos are used. Plate colours are taken from the artwork; works without an image yet are shown unprinted.'),
                ('Embeds', 'Only official YouTube videos are embedded, in this order of preference: official video, official live footage, official audio (Topic).'),
                ('Advertising', 'Affiliate links appear only in the Own section of each work page, never inside the text. A disclosure sits next to them and in the site footer, together with the standard Amazon Associates statement.'),
                ('Made by', 'DJ Naoyaman (Naoya Miyazaki). See the profile page for more.')]
        gl = '<dl class="gloss">' + ''.join(f'<dt>{esc(g["en"])}</dt><dd lang="ja">{esc(g["ja"])}</dd>' for g in GLOSS) + '</dl>'
        gh = 'Glossary (English and Japanese)'
    body = '<div class="wrap"><header class="page-h"><h1>' + u['about'] + '</h1></header>' + ''.join(f'<section class="s"><h2 class="sh">{t}</h2><p>{esc(x)}</p></section>' for t, x in secs) + f'<section class="s"><h2 class="sh">{gh}</h2>{gl}</section></div>'
    emit(lang, 'about', None, u['about'], secs[0][1][:120], body, {'type': 'plain', 'title': u['about']}, cur='about')


PROFILE_MODIFIED = '2026-10-31T12:52:00+00:00'

def profile_page(lang):
    u = UI[lang]; pg = path(lang, 'profile')
    if lang == 'ja':
        lead = '世界一の非公式ファンサイトを目指して。The Chemical Brothersの作品を調べ、聴き、少しずつ記録する。myChemsは、日々育て続ける私のライフワークです。'
        policy = '事実には出典を添え、私見とは分けて記しています。'
        label = '作者について'
        desc = 'myChemsを日々育てる想い。DJ Naoyamanによる非公式ファンアーカイブのライフワーク。'
    else:
        lead = "With the aim of building the world’s best unofficial fan site, I study and listen to The Chemical Brothers’ work, building a record little by little. myChems is my life’s work, growing day by day."
        policy = 'Facts carry sources; personal views are kept separate.'
        label = 'About the author'
        desc = 'The idea behind myChems: a lifelong, evolving unofficial fan archive by DJ Naoyaman.'
    # Editorial revision date: only this profile changes, never a build-time clock.
    updated = PROFILE_MODIFIED
    updated_label = '最終更新' if lang == 'ja' else 'Last updated'
    body = f'<div class="wrap"><header class="page-h"><p class="muted small">{u["profile"]}</p><h1>DJ Naoyaman</h1></header><section class="s"><p>{esc(lead)}</p><p>{esc(policy)}</p><p><a class="more" href="https://djnaoyaman.github.io/profile.html">{label}</a></p></section></div>'
    ld = {'@context': 'https://schema.org', '@type': 'ProfilePage', 'dateModified': updated, 'mainEntity': {'@type': 'Person', 'name': 'DJ Naoyaman', 'url': 'https://djnaoyaman.github.io/profile.html'}}
    emit(lang, 'profile', None, u['profile'], desc, body, {'type': 'plain', 'title': 'DJ Naoyaman', 'sub': u['profile']}, ld, cur='about')

# ---------------------------------------------------------------- OGP
def make_ogp(pg, spec, lang):
    from PIL import Image, ImageDraw, ImageFont
    B = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'; Rg = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
    F = lambda p, s: ImageFont.truetype(p, s, index=0)
    im = Image.new('RGB', (1200, 630), (0, 0, 0)); d = ImageDraw.Draw(im)
    hexrgb = lambda h: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
    site = CFG['site_name'][lang]
    def wordmark(x, y, width):
        mark = Image.open(os.path.join(ROOT, 'src', 'brand', 'mychems-wordmark-ivory-1024.png')).convert('RGBA')
        mark = mark.resize((width, round(mark.height * width / mark.width)), Image.Resampling.LANCZOS)
        im.paste(mark, (x, y), mark)
    def halftone(x0, y0, x1, y1, col, step=14):
        for yy in range(y0, y1, step):
            for xx in range(x0, x1, step):
                t = ((xx - x0) / max(1, x1 - x0))
                r = 1 + 3.2 * t
                d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=col)
    def wrap_text(text, font, maxw):
        words = text.split(' ') if ' ' in text else list(text); lines = ['']; sep = ' ' if ' ' in text else ''
        for wd in words:
            t = (lines[-1] + sep + wd) if lines[-1] else wd
            if d.textlength(t, font=font) <= maxw: lines[-1] = t
            else: lines.append(wd)
        return lines
    if spec['type'] == 'work':
        w = W[spec['w']]; bg, i1, i2, _ = palette(w); fg = text_on(bg)
        d.rectangle([0, 0, 420, 630], fill=hexrgb(bg))
        halftone(0, 0, 420, 630, hexrgb(i2) if w['plates']['status'] == 'extracted' else (215, 214, 208))
        d.text((36, 36), str(w['atomic']), font=F(Rg, 34), fill=hexrgb(fg))
        sym = F(B, 190); d.text((38 + 6, 150 + 5), w['symbol'], font=sym, fill=hexrgb(i2)); d.text((38, 150), w['symbol'], font=sym, fill=hexrgb(i1 if cr(i1, bg) >= 3 else fg))
        d.text((36, 540), UI[lang][w['type']], font=F(B, 30), fill=hexrgb(fg))
        size = 96
        while size > 40:
            f = F(B, size); lines = wrap_text(w['title'].upper(), f, 700)
            if len(lines) <= 3: break
            size -= 6
        y = 315 - (len(lines) * size * 1.08) / 2
        for ln in lines:
            d.text((470 + 5, y + 4), ln, font=f, fill=(228, 0, 124)); d.text((470, y), ln, font=f, fill=(242, 241, 236)); y += size * 1.08
        wordmark(470, 30, 200)
        yr = fdate(w['records']['date']['v'], lang) if 'date' in w['records'] else str(w['year'])
        d.text((470, 560), yr, font=F(Rg, 28), fill=(170, 170, 165))
    else:
        halftone(760, 0, 1200, 630, (26, 26, 255))
        wordmark(64, 48, 240)
        if spec['type'] == 'top':
            lines = ['作品を聴く。', '反応をたどる。'] if lang == 'ja' else ['LISTEN TO THE WORKS.', 'TRACE THE CONNECTIONS.']
            f = F(B, 84 if lang == 'ja' else 62)
        else:
            f = F(B, 104); lines = wrap_text(spec['title'], f, 1000)
            while len(lines) > 2: f = F(B, f.size - 8); lines = wrap_text(spec['title'], f, 1000)
        y = 230
        for ln in lines:
            d.text((64 + 5, y + 4), ln, font=f, fill=(228, 0, 124)); d.text((64, y), ln, font=f, fill=(242, 241, 236)); y += f.size * 1.2
        if spec.get('sub'): d.text((64, 540), spec['sub'], font=F(Rg, 30), fill=(170, 170, 165))
    out = os.path.join(DIST, PAGES[pg]['ogp']); os.makedirs(os.path.dirname(out), exist_ok=True)
    im.save(out, optimize=True)

# ---------------------------------------------------------------- 検証スイート
def verify():
    res = []; ok = lambda n, t, c, detail='': res.append((n, t, 'OK' if c is True else ('WARN' if c == 'warn' else 'NG'), detail))
    # 1 出典のない事実
    bad = []
    for w in WORKS:
        for k, v in w['records'].items():
            if not v.get('src') or any(s not in SRC for s in v['src']): bad.append(f'{w["id"]}.{k}')
        for c in w['credits'] + w['notes'] + w['testimony'] + w['after'] + w.get('context', []) + w.get('tracklist', []) + w.get('reviews', []):
            if not c.get('src') or any(s not in SRC for s in c['src']): bad.append(w['id'])
        if w['embed']['mv'] and not w['embed']['mv'].get('src'): bad.append(w['id'] + '.embed')
    for e in EVENTS + NOW['items'] + NOW['delayed']:
        if not e.get('src') or any(s not in SRC for s in e['src']): bad.append(e['date'])
    ok(1, '出典のない事実項目が0件', not bad, ', '.join(bad[:5]))
    # 2 日英のペアと改訂番号
    pairs = []
    for pg, v in PAGES.items():
        other = path('en' if v['lang'] == 'ja' else 'ja', v['key'], v['arg'])
        if other not in PAGES: pairs.append(pg)
    revs = []
    for f in os.listdir(os.path.join(ROOT, 'texts', 'ja')):
        a = text_blocks(f[:-3], 'ja')[1]; b = text_blocks(f[:-3], 'en')[1]
        if a != b: revs.append(f)
    for f in os.listdir(os.path.join(ROOT, 'texts', 'en')):
        if not os.path.exists(os.path.join(ROOT, 'texts', 'ja', f)): revs.append(f)
    ok(2, '日英がそろい、片方だけの更新がない', not pairs and not revs, ', '.join(pairs + revs))
    # 3 内部リンク切れ
    broken = []
    for pg, v in PAGES.items():
        for m in re.finditer(r'(?:href|src)="([^"#:]+?)(#[^"]*)?"', v['html']):
            u_ = m.group(1)
            if u_.startswith(('http', 'data:', 'mailto:')) or u_ == '': continue
            tgt = posixpath.normpath(posixpath.join(posixpath.dirname(pg), u_))
            if not os.path.exists(os.path.join(DIST, tgt)): broken.append(f'{pg} → {u_}')
    ok(3, '内部リンクの切れがない', not broken, '; '.join(broken[:5]))
    # 4 OGP
    miss = [pg for pg, v in PAGES.items() if not os.path.exists(os.path.join(DIST, v['ogp'])) or 'og:image' not in v['html']]
    ok(4, '全ページに専用のOGP画像がある', not miss, ', '.join(miss[:5]))
    # 5 広告表記
    ad = [pg for pg, v in PAGES.items() if 'class="own-link' in v['html'] and 'id="ad-disclosure"' not in v['html']]
    ok(5, '「持つ」リンクのあるページに広告表記がある', not ad, ', '.join(ad))
    # 6 コントラスト
    cbad = []
    for w in WORKS:
        bg, i1, i2, _ = palette(w); fg = text_on(bg); tt = i1 if cr(i1, bg) >= 3 else fg
        if cr(fg, bg) < 4.5 or cr(tt, bg) < 3: cbad.append(w['id'])
    ok(6, '本文4.5:1、見出し3:1を満たす', not cbad, ', '.join(cbad))
    # 7 YouTube
    ids = {w['id']: w['embed']['mv']['id'] for w in WORKS if w['embed']['mv']}
    key = os.environ.get('YT_API_KEY')
    if not key:
        ok(7, 'YouTube埋め込みの可否と日本での再生', 'warn', f'未実施（YT_API_KEYなし）。埋め込み{len(ids)}件、動画なし{len(WORKS) - len(ids)}件')
    else:
        import urllib.request
        q = ','.join(ids.values())
        data = json.load(urllib.request.urlopen(f'https://www.googleapis.com/youtube/v3/videos?part=status,contentDetails&id={q}&key={key}'))
        got = {it['id']: it for it in data.get('items', [])}; ng = []
        for wid, vid in ids.items():
            it = got.get(vid)
            if not it or not it['status'].get('embeddable'): ng.append(f'{wid}:embed'); continue
            rr = it['contentDetails'].get('regionRestriction', {})
            if 'JP' in rr.get('blocked', []) or ('allowed' in rr and 'JP' not in rr['allowed']): ng.append(f'{wid}:JP')
        ok(7, 'YouTube埋め込みの可否と日本での再生', not ng, ', '.join(ng))
    # 8 署名
    sig = []
    for pg, v in PAGES.items():
        head = v['html'][:4000]
        if v['key'] == 'top':
            if '##   ## ####### ##' not in head: sig.append(pg)
        elif not re.search(r'<!DOCTYPE html>\n<!-- WELCOME / NAOYA MIYAZAKI LAB\. JAPAN / ', head): sig.append(pg)
    ok(8, '署名コメント（トップはbanner、下層は1行）', not sig, ', '.join(sig[:5]))
    # 9 hreflang
    hb = []
    for pg, v in PAGES.items():
        for l in LANGS:
            m = re.search(rf'hreflang="{l}" href="([^"]+)"', v['html'])
            if not m: hb.append(pg); continue
            tgt = posixpath.normpath(posixpath.join(posixpath.dirname(pg), m.group(1))) if not m.group(1).startswith('http') else None
            if tgt and tgt not in PAGES: hb.append(pg)
    ok(9, 'hreflangが日英で相互に張られている', not hb, ', '.join(hb[:5]))
    # 10 JSON-LD
    jl = 0
    for v in PAGES.values():
        for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', v['html'], re.S):
            try: json.loads(m.group(1))
            except Exception: jl += 1
    ok(10, '構造化データ（JSON-LD）が正しく読める', jl == 0, str(jl))
    # 11 版色
    un = [w['id'] for w in WORKS if w['plates']['status'] != 'extracted']
    ok(11, '版色が未抽出の作品数', 'warn' if un else True, f'{len(un)}/{len(WORKS)}件が未抽出')
    # 12 アートワーク
    bad_img = []
    # Existing alembic identity rendered as UI icons, not record artwork.
    device_icon_sha256 = {'src/icons/icon-192.png': '8fd5bde9676f540161f2d843c23fb360e22ff6b3176e208b706332aeb2b23fa5', 'src/icons/maskable-512.png': '80be30ed85f78baa85d24308cba458532016b31fc516e72e145dfe23ef83d9c9', 'src/icons/icon-32.png': '5877c53a02186d60c0f90181bc803915bcc4f2face09e05d527ff09468259b86', 'src/icons/maskable-192.png': '7f2eb0c4c7ef28f685538a835f2883120b14e4246a1c82b11ed781d68874361f', 'src/icons/icon-16.png': '4e7d798e68bd242c107695e8b4623c033b856c61a00d7c1d17c5d602a7e72925', 'src/icons/icon-48.png': '62e521d1e9b72247a6dd1db79f8448e1638e33a85c39a5bb98a897901882497b', 'src/icons/apple-touch-icon.png': 'c7fd81a273c1a5b0f79b348c9e2a1159799089821087b1999ad68cb32a418694', 'src/icons/icon-512.png': 'eb61dbe67d80fe46e051d18e68dce02b97b291c7724458c8cc3b10e3a8200930'}
    # Owner-approved custom wordmark, not Chemical Brothers artwork or official logo.
    device_icon_sha256['src/brand/mychems-wordmark-ivory-1024.png'] = 'f1ceb108a91185601869704cd9ee57bb8d507020cb241e68414936dc2675f849'
    for r_, _, fs in os.walk(ROOT):
        if '.git' in r_ or os.path.sep + 'dist' in r_ or r_.startswith(DIST) or 'art_review' in r_: continue
        for f in fs:
            if f.lower().endswith(('.jpg', '.jpeg', '.webp', '.gif', '.png')):
                relative = os.path.join(os.path.relpath(r_, ROOT), f).replace(os.path.sep, '/')
                if relative in device_icon_sha256:
                    with open(os.path.join(r_, f), 'rb') as icon_file:
                        if hashlib.sha256(icon_file.read()).hexdigest() != device_icon_sha256[relative]: bad_img.append(relative)
                elif os.path.abspath(r_) != ART or f.rsplit('.', 1)[0] not in W: bad_img.append(relative)
    for r_, _, fs in os.walk(ROOT):
        if '.git' in r_: continue
        bad_img += [os.path.join(os.path.relpath(r_, ROOT), f) for f in fs if f.lower().endswith(('.mp3', '.wav', '.aif', '.aiff', '.flac', '.m4a', '.aac', '.ogg'))]
    no_src = [w['id'] for w in WORKS if art_file(w) and not w.get('art_src')]
    n_art = sum(1 for w in WORKS if art_file(w))
    ok(12, '作品画像は出典付き、UIアイコンは既知ハッシュ一致。音源なし', True if not bad_img and not no_src else False, (', '.join(bad_img[:5] + no_src[:5])) or f'掲載 {n_art}/{len(WORKS)}件')
    # 13 脈動
    fast = [w['id'] for w in WORKS if ((w['bpm'] or 120) / 2 if (w['bpm'] or 120) > 180 else (w['bpm'] or 120)) / 60 > 3]
    ok(13, '脈動の変化が1秒に3回以下', not fast, ', '.join(fast))
    # 14 用語集
    gb = []
    for pg, v in PAGES.items():
        if v['lang'] != 'ja': continue
        en = PAGES.get(path('en', v['key'], v['arg']))
        if not en: continue
        tj = re.sub(r'<[^>]+>', ' ', v['html'].split('<main id="main" tabindex="-1">')[1]); te = re.sub(r'<[^>]+>', ' ', en['html'].split('<main id="main" tabindex="-1">')[1]).lower()
        for g in GLOSS:
            if g['ja'] in tj and g['en'].lower() not in te: gb.append(f'{pg}:{g["ja"]}')
    ok(14, '造語の訳語が用語集と一致している', not gb, ', '.join(gb[:6]))
    return res

# ---------------------------------------------------------------- SEO/LLMO
def write_seo_files():
    base = CFG['base_url'].rstrip('/') + '/' if CFG['base_url'] else ''
    if not base: return
    # sitemap.xml（hreflangの相互リンク付き）
    urls = []
    for pg, v in sorted(PAGES.items()):
        alts = ''.join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{base}{path(l, v["key"], v["arg"])}"/>' for l in LANGS)
        alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{base}{path("ja", v["key"], v["arg"])}"/>'
        prio = '1.0' if v['key'] == 'top' else ('0.8' if v['key'] == 'work' else '0.6')
        urls.append(f'<url><loc>{base}{pg}</loc><lastmod>{page_modified(v["key"])}</lastmod>{alts}<priority>{prio}</priority></url>')
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
               + ''.join(urls) + '\n</urlset>\n')
    open(os.path.join(DIST, 'sitemap.xml'), 'w', encoding='utf-8').write(sitemap)
    # robots.txt
    robots = f'User-agent: *\nAllow: /\n\nSitemap: {base}sitemap.xml\n'
    open(os.path.join(DIST, 'robots.txt'), 'w', encoding='utf-8').write(robots)
    # llms.txt（llmstxt.org準拠。LLM/検索エンジンの要約用に英語で用意）
    u = UI['en']
    disc = []
    for w in WORKS:
        r = w['records']; yr = r.get('date', {}).get('v', str(w['year']))
        disc.append(f'- [{w["title"]}]({base}{path("en", "work", w["id"])}) — {u[w["type"]]}, {str(yr)[:4]}')
    pages_md = '\n'.join(f'- [{u[k]}]({base}{path("en", k)})' for k in NAV) + f'\n- [{u["sources"]}]({base}{path("en", "sources")})\n- [{u["about"]}]({base}{path("en", "about")})\n- [{u["profile"]}]({base}{path("en", "profile")})'
    llms = f'''# {CFG['site_name']['en']}

> An unofficial fan archive documenting albums, singles and EPs by The Chemical Brothers, with sourced release records, music and technology notes, context, testimony and a personal view by DJ Naoyaman (Naoya Miyazaki). Every factual claim on this site is tied to a cited source (see /sources/); opinion is always labelled as such and kept separate from fact. Available in Japanese (default) and English.

## Key pages

{pages_md}

## Discography ({len(WORKS)} works, in release order)

{chr(10).join(disc)}

## Full text

- [Full bilingual page text]({base}llms-full.txt)

## Notes for automated readers

- This is a fan-made archive, not affiliated with or endorsed by The Chemical Brothers or their label.
- Each work page cites its sources inline; the sources index is at /sources/.
- Each language page has its own canonical URL. Japanese and English counterparts are connected with hreflang; English pages use /en/.
'''
    open(os.path.join(DIST, 'llms.txt'), 'w', encoding='utf-8').write(llms)

# ---------------------------------------------------------------- 実行
class MainText(HTMLParser):
    def __init__(self):
        super().__init__(); self.inside = False; self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag == 'main': self.inside = True
        if self.inside and tag in ('p','h1','h2','h3','li','dt','dd','tr','section'): self.parts.append('\n')
    def handle_endtag(self, tag):
        if tag == 'main': self.inside = False
    def handle_data(self, text):
        if self.inside: self.parts.append(text)

def write_full_text_and_recovery():
    base = CFG['base_url'].rstrip('/') + '/'
    blocks = ['# my Chems — full archive text', 'Unofficial archive. Existing page text follows in Japanese and English. Facts and personal views retain their page labels. Citations are resolved on the linked source pages. This file does not grant rights to third-party material.']
    for pg, v in sorted(PAGES.items()):
        parser = MainText(); parser.feed(v['html'])
        text = re.sub(r'\n[ \t]*\n+', '\n\n', ''.join(parser.parts)).strip()
        blocks.append('## ' + base + pg + '\n\n' + text)
    open(os.path.join(DIST, 'llms-full.txt'), 'w', encoding='utf-8').write('\n\n'.join(blocks) + '\n')
    # Absolute project URLs work even when GitHub serves this file for a deeply nested missing URL.
    recovery = f'''<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="robots" content="noindex,follow"><meta name="referrer" content="strict-origin-when-cross-origin"><title>ページが見つかりません / Page not found | my Chems</title><meta name="description" content="my Chemsの作品・歴史アーカイブへ戻る案内。"><link rel="icon" href="{base}icons/favicon.ico"><link rel="apple-touch-icon" href="{base}icons/apple-touch-icon.png"><link rel="manifest" href="{base}site.webmanifest"><meta name="theme-color" content="#000000"><style>{CSS}</style></head><body><main class="wrap page-h" id="main"><a href="{base}" aria-label="myChems"><img src="{base}brand/mychems-wordmark-ivory.svg" alt="myChems" width="1799" height="504" style="width:180px;height:auto"></a><h1>ページが見つかりません</h1><p>URLが変わったか、入力が違っている可能性があります。作品や年表から探してみてください。</p><p><a href="{base}">ホーム</a> · <a href="{base}works/">作品・周期表</a> · <a href="{base}timeline/">年表</a></p><section class="s" lang="en"><h2>Page not found</h2><p>The address may have changed or been mistyped. Browse the archive instead.</p><p><a href="{base}en/">English home</a> · <a href="{base}en/works/">Works</a> · <a href="{base}en/timeline/">Timeline</a></p></section><p class="small">非公式のファンアーカイブ / An unofficial fan archive.</p></main></body></html>'''
    open(os.path.join(DIST, '404.html'), 'w', encoding='utf-8').write(recovery)

def main():
    if os.path.exists(DIST): shutil.rmtree(DIST)
    os.makedirs(DIST)
    load_art_plates()
    if os.path.isdir(ART):
        os.makedirs(os.path.join(DIST, 'art'), exist_ok=True)
        for w in WORKS:
            f = art_file(w)
            if f: shutil.copy(f, os.path.join(DIST, 'art', os.path.basename(f)))
    for lang in LANGS:
        top_page(lang); works_page(lang); shelf_pages(lang); timeline_page(lang); equations_pages(lang); chain_page(lang); now_page(lang); about_page(lang); profile_page(lang)
        for w in WORKS: work_page(w, lang)
    for lang in LANGS: sources_page(lang)   # 逆リンクのため最後
    for pg, v in PAGES.items():
        out = os.path.join(DIST, pg); os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, 'w', encoding='utf-8').write(v['html'])
        make_ogp(pg, v['ogp_spec'], v['lang'])
    open(os.path.join(DIST, '.nojekyll'), 'w').close()
    write_seo_files()
    write_full_text_and_recovery()
    listening = listening_catalog(WORKS, J('listening-sources.json'))
    for release in listening['releases']:
        release['articlePath'] = {lang: rel(path(lang, 'works'), path(lang, 'work', release['id'])) for lang in LANGS}
    shutil.copytree(os.path.join(ROOT, 'src', 'listening'), os.path.join(DIST, 'listening'))
    with open(os.path.join(DIST, 'listening', 'catalog.json'), 'w', encoding='utf-8') as handle:
        json.dump(listening, handle, ensure_ascii=False, separators=(',', ':'))
    shutil.copytree(os.path.join(ROOT, "src", "brand"), os.path.join(DIST, "brand"))
    shutil.copytree(os.path.join(ROOT, "src", "icons"), os.path.join(DIST, "icons"))
    shutil.copy(os.path.join(ROOT, "src", "site.webmanifest"), DIST)
    res = verify()
    print(f'ページ {len(PAGES)}（日 {sum(1 for v in PAGES.values() if v["lang"] == "ja")} ／ 英 {sum(1 for v in PAGES.values() if v["lang"] == "en")}）')
    for n, t, s, dt in res: print(f'{n:>2} {s:<4} {t}' + (f'　{dt}' if dt else ''))
    if any(s == 'NG' for *_, s, _ in res): sys.exit(1)

if __name__ == '__main__':
    main()

