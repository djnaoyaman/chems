#!/usr/bin/env python3
"""公式サイトの各リリースページからジャケット画像を取り、art/{作品ID}.jpg に置く（Cowork用）。

  python3 tools/fetch_art.py --dry-run     何をするかだけ表示（ダウンロードしない）
  python3 tools/fetch_art.py               実行（正方形に近い画像だけ採用。それ以外は notes/art_review/ へ）
  python3 tools/fetch_art.py --only go,dyoh   指定した作品だけ
  python3 tools/fetch_art.py --only fcs --slug fcs=fourteenth-century-sky   手で見つけたページで取る

採用した作品は data/works.json の art_src に出典ID（公式サイトのそのページ）を入れ、
data/sources.json に出典を登録する。結果は notes/art_report.csv に書く。
"""
import argparse, csv, html, io, json, os, re, sys, time, urllib.request, urllib.parse
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, 'art'); REVIEW = os.path.join(ROOT, 'notes', 'art_review')
BASE = 'https://www.thechemicalbrothers.com'
UA = {'User-Agent': 'Mozilla/5.0 (my Chems artwork check; contact via note.com/djnaoyaman)'}

# 公式サイトで確認済みのリリースページ（music-videos/ 以下のスラッグ）。未確認の作品は /music の一覧から探す
KNOWN = {
 'epd': 'exit-planet-dust', 'lh': 'leave-home', 'lis': 'life-is-sweet', 'lof': 'loops-of-fury',
 'ss': 'setting-sun', 'brb': 'block-rockin-beats-single', 'dyoh': 'dig-your-own-hole', 'el': 'elektrobank',
 'ppr': 'the-private-psychedelic-reel', 'hbhg': 'hey-boy-hey-girl-single', 'sur': 'surrender', 'lfb': 'let-forever-be',
 'ooc': 'out-of-control', 'mr': 'music-response', 'ibia': 'it-began-in-afrika', 'sg': 'star-guitar',
 'cwu': 'come-with-us', 'cwtt': 'come-wih-us-the-test', 'amep': 'american-ep', 'tgp': 'the-golden-path-2',
 'gyh': 'get-yourself-high', 'gal': 'galvanize-single', 'ptb': 'push-the-button', 'bel': 'believe-single',
 'box': 'the-boxer', 'l05': 'live-05', 'dia': 'do-it-again-single', 'watn': 'we-are-the-night',
 'tsd': 'the-salmon-dance', 'mm': 'midnight-madness', 'fur': 'further', 'aw': 'another-world-single',
 'sw': 'swoon', 'go': 'go-single', 'unl': 'under-neon-lights-single', 'bite': 'born-in-the-echoes',
 'fy': 'free-yourself-single', 'mah': 'mah', 'gtko': 'got-to-keep-on-single', 'ng': 'no-geography',
}
SKIP_WORDS = ('video', 'remix', 'rmx', '-mix', 'demo', 'the-remixes', 'remixes')

def get(url, binary=False):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    return data if binary else data.decode('utf-8', 'replace')

def slugify(t):
    t = t.lower().replace('&', 'and').replace("'", '').replace('’', '')
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')

def find_slugs(base):
    page = get(base + '/music')
    return sorted(set(re.findall(r'href="/music-videos/([a-z0-9-]+)"', page)) | set(re.findall(r'/music-videos/([a-z0-9-]+)', page)))

def guess(w, slugs):
    s = slugify(w['title'])
    cands = [x for x in slugs if (x == s or x.startswith(s + '-')) and not any(k in x for k in SKIP_WORDS)]
    order = lambda x: (0 if x == s else 1 if x == s + '-single' else 2 if re.fullmatch(re.escape(s) + r'-\d+', x) else 3, len(x))
    return sorted(cands, key=order)[0] if cands else None

def meta_image(page):
    for pat in (r'<meta[^>]+(?:name|property)="twitter:image"[^>]+content="([^"]+)"', r'<meta[^>]+content="([^"]+)"[^>]+(?:name|property)="twitter:image"',
                r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', r'<meta[^>]+content="([^"]+)"[^>]+property="og:image"'):
        m = re.search(pat, page)
        if m and m.group(1).strip(): return html.unescape(m.group(1).strip())
    return None

def page_title(page):
    m = re.search(r'<title>(.*?)</title>', page, re.S)
    return html.unescape(m.group(1).strip()) if m else ''

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true'); ap.add_argument('--only'); ap.add_argument('--base', default=BASE)
    ap.add_argument('--force', action='store_true', help='既に art/ にある作品も取り直す')
    ap.add_argument('--slug', action='append', default=[], help='手で見つけたページを指定する 例：--slug fcs=fourteenth-century-sky')
    a = ap.parse_args()
    from PIL import Image
    W = json.load(open(os.path.join(ROOT, 'data', 'works.json'), encoding='utf-8'))
    S = json.load(open(os.path.join(ROOT, 'data', 'sources.json'), encoding='utf-8')); sid = {s['id'] for s in S}
    only = set(a.only.split(',')) if a.only else None
    for kv in a.slug:
        k, v = kv.split('=', 1); KNOWN[k.strip()] = v.strip().rsplit('/', 1)[-1]
    try: slugs = find_slugs(a.base)
    except Exception as e: slugs = []; print('一覧ページを読めませんでした：', e)
    os.makedirs(ART, exist_ok=True); os.makedirs(REVIEW, exist_ok=True)
    rows = []
    for w in W:
        if only and w['id'] not in only: continue
        have = [f for f in os.listdir(ART) if f.rsplit('.', 1)[0] == w['id']]
        if have and not a.force: rows.append([w['id'], w['title'], 'skip', '', '', '', 'art/に既にある']); continue
        slug = KNOWN.get(w['id']) or guess(w, slugs)
        if not slug: rows.append([w['id'], w['title'], 'none', '', '', '', '公式サイトにリリースページが見つからない']); print(f'{w["id"]:<6} 見つからない'); continue
        url = f'{a.base}/music-videos/{slug}'
        try:
            page = get(url); img = meta_image(page)
        except Exception as e:
            rows.append([w['id'], w['title'], 'error', url, '', '', f'ページを読めない：{e}']); continue
        if not img: rows.append([w['id'], w['title'], 'none', url, '', '', '画像の指定がない']); continue
        if 'maxresdefault' in img or 'ytimg' in img or 'placeholder' in img:
            rows.append([w['id'], w['title'], 'review', url, img, '', '動画のサムネイルか仮画像の可能性']); print(f'{w["id"]:<6} 要確認（サムネイルらしい） {img}'); continue
        if a.dry_run: rows.append([w['id'], w['title'], 'plan', url, img, '', page_title(page)]); print(f'{w["id"]:<6} {url}  →  {img}'); continue
        try:
            raw = get(urllib.parse.quote(img, safe=':/%?=&'), binary=True)
            im = Image.open(io.BytesIO(raw)).convert('RGB')
        except Exception as e:
            rows.append([w['id'], w['title'], 'error', url, img, '', f'画像を読めない：{e}']); continue
        ratio = im.width / im.height; size = f'{im.width}x{im.height}'
        im.thumbnail((1200, 1200))
        if not 0.9 <= ratio <= 1.1:
            im.save(os.path.join(REVIEW, f'{w["id"]}.jpg'), quality=90)
            rows.append([w['id'], w['title'], 'review', url, img, size, '正方形でない（ジャケット以外の可能性）→ notes/art_review/']); print(f'{w["id"]:<6} 要確認 {size}'); continue
        im.save(os.path.join(ART, f'{w["id"]}.jpg'), quality=90)
        s_id = 'cb-r-' + slug
        if s_id not in sid:
            S.append({'id': s_id, 'publisher': 'The Chemical Brothers', 'lang': 'en', 'title': f'Official site: {w["title"]} (release page)', 'url': url, 'date': '', 'checked': date.today().isoformat()}); sid.add(s_id)
        w['art_src'] = [s_id]
        rows.append([w['id'], w['title'], 'ok', url, img, size, page_title(page)]); print(f'{w["id"]:<6} 採用 {size}  ← {url}')
        time.sleep(1.0)  # 相手のサーバーに負担をかけない
    if not a.dry_run:
        json.dump(W, open(os.path.join(ROOT, 'data', 'works.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        json.dump(S, open(os.path.join(ROOT, 'data', 'sources.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    os.makedirs(os.path.join(ROOT, 'notes'), exist_ok=True)
    with open(os.path.join(ROOT, 'notes', 'art_report.csv'), 'w', newline='', encoding='utf-8') as f:
        cw = csv.writer(f); cw.writerow(['id', 'title', 'status', 'page', 'image', 'size', 'note']); cw.writerows(rows)
    n = {k: sum(1 for r in rows if r[2] == k) for k in ('ok', 'review', 'none', 'error', 'skip', 'plan')}
    print('\n' + '　'.join(f'{k} {v}' for k, v in n.items() if v) + '　→ notes/art_report.csv')

if __name__ == '__main__':
    main()
