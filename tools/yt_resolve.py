#!/usr/bin/env python3
"""動画IDがない作品について、YouTube Data APIで公式チャンネルと「- Topic」チャンネルから候補を探す。
  YT_API_KEY=... python3 tools/yt_resolve.py          … data/yt_candidates.json に候補を書き出す（works.jsonは変えない）
  YT_API_KEY=... python3 tools/yt_resolve.py --apply  … 候補1件目を works.json に入れる（公式チャンネルかTopicのものだけ）
"""
import json, os, sys, urllib.request, urllib.parse
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY = os.environ.get('YT_API_KEY') or sys.exit('YT_API_KEY がありません')
API = 'https://www.googleapis.com/youtube/v3/'
get = lambda ep, **q: json.load(urllib.request.urlopen(API + ep + '?' + urllib.parse.urlencode({**q, 'key': KEY})))
ch = get('channels', part='id', forUsername='thechemicalbrothers')['items'][0]['id']
W = json.load(open(os.path.join(ROOT, 'data/works.json'), encoding='utf-8'))
out = {}
for w in W:
    if w['embed']['mv']: continue
    found = []
    for params in ({'channelId': ch}, {}):
        r = get('search', part='snippet', type='video', maxResults=6, q=f'The Chemical Brothers {w["title"]}', **params)
        for it in r.get('items', []):
            sn = it['snippet']; ct = sn['channelTitle']
            official = sn.get('channelId') == ch or ct == 'The Chemical Brothers - Topic'
            if official and w['title'].lower().split(' (')[0] in sn['title'].lower():
                found.append({'id': it['id']['videoId'], 'title': sn['title'], 'channel': ct, 'kind': 'official' if sn.get('channelId') == ch else 'topic'})
        if found: break
    out[w['id']] = found
json.dump(out, open(os.path.join(ROOT, 'data/yt_candidates.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n'.join(f'{k}: ' + (f'{v[0]["id"]} {v[0]["title"]} [{v[0]["channel"]}]' if v else '候補なし') for k, v in out.items()))
if '--apply' in sys.argv:
    for w in W:
        c = out.get(w['id'])
        if c: w['embed']['mv'] = {'id': c[0]['id'], 'src': ['yt-api'], 'verified': False, 'via': c[0]['kind']}
    S = json.load(open(os.path.join(ROOT, 'data/sources.json'), encoding='utf-8'))
    if not any(s['id'] == 'yt-api' for s in S):
        S.append({'id': 'yt-api', 'publisher': 'YouTube', 'lang': 'en', 'title': 'The Chemical Brothers official channel / Topic (YouTube Data API search)', 'url': 'https://www.youtube.com/user/thechemicalbrothers', 'date': '', 'checked': ''})
    json.dump(W, open(os.path.join(ROOT, 'data/works.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(S, open(os.path.join(ROOT, 'data/sources.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('works.json に反映しました')
