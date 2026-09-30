#!/usr/bin/env python3
"""BPMとキーを自動で入れる。音源そのものはリポジトリに置かない（読むだけ）。

  1) rekordboxのライブラリから取り込む（DJ Naoyamanの解析値をそのまま使う・推奨）
     rekordbox → ファイル → ライブラリをxml形式でエクスポート
     python3 tools/measure.py --rekordbox ~/Desktop/rekordbox.xml

  2) 音源ファイルを直接解析する（ffmpegが読める形式ならなんでも）
     python3 tools/measure.py --audio ~/Music/ChemicalBrothers
     ファイル名に曲名が入っていれば作品に自動で割り当てる

  どちらも data/works.json の bpm / key / camelot / measure を書き換える。
  --dry-run を付けると、書き込まずに結果だけ表示する。
"""
import argparse, json, os, re, subprocess, sys, unicodedata, urllib.parse, xml.etree.ElementTree as ET
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WJ = os.path.join(ROOT, 'data', 'works.json')
NOTES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
ALIAS = {'Db': 'C#', 'D#': 'Eb', 'Gb': 'F#', 'G#': 'Ab', 'A#': 'Bb', 'Cb': 'B', 'Fb': 'E', 'E#': 'F', 'B#': 'C'}
CAMELOT_MAJ = {'C': '8B', 'G': '9B', 'D': '10B', 'A': '11B', 'E': '12B', 'B': '1B', 'F#': '2B', 'C#': '3B', 'Ab': '4B', 'Eb': '5B', 'Bb': '6B', 'F': '7B'}
CAMELOT_MIN = {'A': '8A', 'E': '9A', 'B': '10A', 'F#': '11A', 'C#': '12A', 'Ab': '1A', 'Eb': '2A', 'Bb': '3A', 'F': '4A', 'C': '5A', 'G': '6A', 'D': '7A'}

def norm(s):
    s = unicodedata.normalize('NFKC', s).lower()
    s = re.sub(r'\((?:feat|ft|featuring)[^)]*\)', ' ', s)
    s = re.sub(r'\b(?:feat|ft|featuring)\.? .*$', ' ', s)
    s = re.sub(r'[’\'`]', '', s)
    s = re.sub(r'[^a-z0-9]+', ' ', s)
    return ' '.join(s.split())

def is_variant(title):
    t = title.lower()
    return any(k in t for k in ['remix', ' rmx', 'edit)', 'dub', 'instrumental', 'live', 'demo', 'reprise', 'mixed', 'version)']) and 'album version' not in t

def key_label(tonic, minor):
    tonic = ALIAS.get(tonic, tonic)
    cam = (CAMELOT_MIN if minor else CAMELOT_MAJ).get(tonic)
    return (tonic + ('m' if minor else '')), cam

def parse_tonality(t):
    t = (t or '').strip()
    if not t: return None
    m = re.fullmatch(r'(\d{1,2})([AB])', t, re.I)
    if m:
        cam = m.group(1) + m.group(2).upper()
        for tbl, minor in ((CAMELOT_MIN, True), (CAMELOT_MAJ, False)):
            for k, v in tbl.items():
                if v == cam: return key_label(k, minor)
        return None
    m = re.fullmatch(r'([A-Ga-g])([#b♯♭]?)\s*(m|min|minor)?', t)
    if not m: return None
    tonic = m.group(1).upper() + m.group(2).replace('♯', '#').replace('♭', 'b')
    return key_label(tonic, bool(m.group(3)))

# ------------------------------------------------------------------ 音源解析
def decode(path, sr=22050, start=20, dur=120):
    cmd = ['ffmpeg', '-v', 'error', '-ss', str(start), '-t', str(dur), '-i', path, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-']
    import numpy as np
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    y = np.frombuffer(raw, dtype=np.float32)
    if len(y) < sr * 10:  # 短い曲は頭から
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
        y = np.frombuffer(raw, dtype=np.float32)
    return y, sr

def analyse(path):
    import numpy as np
    from scipy.signal import stft
    y, sr = decode(path)
    hop, n_fft = 512, 4096
    f, _, Z = stft(y, fs=sr, nperseg=n_fft, noverlap=n_fft - hop, boundary=None, padded=False)
    mag = np.abs(Z)
    # テンポ：スペクトルの立ち上がりの自己相関に、120 BPM中心のゆるい事前分布をかけて選ぶ
    logm = np.log1p(100 * mag)
    flux = np.maximum(0, np.diff(logm, axis=1)).sum(axis=0)
    flux = flux - np.convolve(flux, np.ones(16) / 16, mode='same')
    flux = np.maximum(flux, 0)
    fps = sr / hop
    ac = np.correlate(flux, flux, mode='full')[len(flux) - 1:]
    bpms = np.arange(60.0, 200.0, 0.1)
    lags = fps * 60.0 / bpms
    score = np.zeros_like(bpms)
    for k, wgt in ((1, 1.0), (2, 0.5), (4, 0.25)):
        score += wgt * np.interp(lags * k, np.arange(len(ac)), ac)
    prior = np.exp(-0.5 * (np.log2(bpms / 120.0) / 0.6) ** 2)
    coarse = float(bpms[np.argmax(score * prior)])
    # 事前分布を外して、候補の前後3%を0.01刻みで詰める
    fine = np.arange(coarse * 0.97, coarse * 1.03, 0.01)
    fl = fps * 60.0 / fine
    fs = sum(wgt * np.interp(fl * k, np.arange(len(ac)), ac) for k, wgt in ((1, 1.0), (2, 0.5), (4, 0.25), (8, 0.25)))
    bpm = float(fine[np.argmax(fs)])
    # 整数BPMの得点が最大値とほぼ同じなら整数に寄せる（打ち込みの曲はほとんどが整数テンポ）
    near = float(np.round(bpm))
    fs_int = sum(wgt * np.interp(fps * 60.0 / near * k, np.arange(len(ac)), ac) for k, wgt in ((1, 1.0), (2, 0.5), (4, 0.25), (8, 0.25)))
    if fs_int >= 0.99 * fs.max(): bpm = near
    while bpm < 85: bpm *= 2
    while bpm > 170: bpm /= 2
    # キー：55〜2000 Hzのエネルギーを12の音名に集め、Krumhansl-Kesslerの調性プロファイルと照合
    sel = (f >= 55) & (f <= 2000)
    pc = np.round(12 * np.log2(f[sel] / 440.0)).astype(int) % 12  # 0 = A
    energy = np.log1p(mag[sel] ** 2).sum(axis=1)
    chroma = np.zeros(12)
    np.add.at(chroma, pc, energy)
    chroma = np.roll(chroma, -3)  # A始まりをC始まりに並べ替え
    major = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
    minor = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
    best = None
    for i in range(12):
        for prof, is_min in ((major, False), (minor, True)):
            r = np.corrcoef(chroma, np.roll(prof, i))[0, 1]
            if best is None or r > best[0]: best = (r, NOTES[i], is_min)
    key, cam = key_label(best[1], best[2])
    return round(bpm, 1), key, cam, round(float(best[0]), 3)

# ------------------------------------------------------------------ 割り当て
def match_work(title, works):
    n = norm(title)
    for w in works:
        if norm(w['title']) == n: return w
    cands = [w for w in works if norm(w['title']) and re.search(r'(^| )' + re.escape(norm(w['title'])) + r'( |$)', n)]
    return max(cands, key=lambda w: len(norm(w['title']))) if cands else None

def from_rekordbox(xml, works):
    root = ET.parse(xml).getroot(); out = {}
    for t in root.iter('TRACK'):
        artist = t.get('Artist') or ''
        if 'chemical brothers' not in artist.lower() and 'dust brothers' not in artist.lower(): continue
        name = t.get('Name') or ''
        w = match_work(re.sub(r'\s*[\(\[].*?[\)\]]', '', name), works)
        if not w or w['type'] == 'album': continue
        bpm = float(t.get('AverageBpm') or 0); key = parse_tonality(t.get('Tonality'))
        if not bpm: continue
        rank = (0 if not is_variant(name) else 1)
        loc = urllib.parse.unquote(t.get('Location') or '').rsplit('/', 1)[-1]
        if w['id'] not in out or rank < out[w['id']]['rank']:
            out[w['id']] = {'bpm': round(bpm, 1), 'key': key[0] if key else None, 'camelot': key[1] if key else None, 'rank': rank,
                            'measure': {'method': 'rekordbox', 'track': name, 'file': loc, 'date': date.today().isoformat()}}
    return out

def from_audio(folder, works):
    exts = ('.mp3', '.wav', '.aif', '.aiff', '.flac', '.m4a', '.aac', '.ogg', '.alac')
    out = {}
    for dp, _, fs in os.walk(folder):
        for fn in sorted(fs):
            if not fn.lower().endswith(exts): continue
            base = re.sub(r'^\d+[\s._-]+', '', os.path.splitext(fn)[0])
            w = match_work(re.sub(r'\s*[\(\[].*?[\)\]]', '', base), works)
            if not w or w['type'] == 'album': continue
            rank = 0 if not is_variant(fn) else 1
            if w['id'] in out and out[w['id']]['rank'] <= rank: continue
            bpm, key, cam, conf = analyse(os.path.join(dp, fn))
            out[w['id']] = {'bpm': bpm, 'key': key, 'camelot': cam, 'rank': rank,
                            'measure': {'method': 'analysis', 'track': base, 'file': fn, 'key_confidence': conf, 'date': date.today().isoformat()}}
            print(f'  {w["title"]:<34} {bpm:>6} BPM  {key:<4} {cam}  ← {fn}')
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rekordbox'); ap.add_argument('--audio'); ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--overwrite', action='store_true', help='rekordboxの値も解析値で上書きする')
    a = ap.parse_args()
    if not (a.rekordbox or a.audio): ap.error('--rekordbox か --audio を指定してください')
    works = json.load(open(WJ, encoding='utf-8'))
    got = {}
    if a.audio: got.update(from_audio(a.audio, works))
    if a.rekordbox: got.update(from_rekordbox(a.rekordbox, works))  # rekordboxを優先
    n = 0
    for w in works:
        r = got.get(w['id'])
        if not r: continue
        if w.get('measure', {}).get('method') == 'rekordbox' and r['measure']['method'] == 'analysis' and not a.overwrite: continue
        w['bpm'], w['key'], w['camelot'], w['measure'] = r['bpm'], r['key'], r['camelot'], r['measure']; n += 1
        print(f'{w["id"]:<6} {w["title"]:<34} {r["bpm"]:>6} BPM  {r["key"] or "—":<4} {r["camelot"] or ""}  [{r["measure"]["method"]}]')
    miss = [w['title'] for w in works if w['type'] != 'album' and not w.get('bpm')]
    print(f'\n{n}件を更新。未計測 {len(miss)}件' + (f'：{", ".join(miss[:12])}{" ほか" if len(miss) > 12 else ""}' if miss else ''))
    if not a.dry_run: json.dump(works, open(WJ, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

if __name__ == '__main__':
    main()
