# my Chems

日英1対1の静的サイト。`build.py` が `data/` と `texts/` から `dist/` に全ページとOGPを生成し、最後に検証スイート（14項目）を回す。NGが1つでもあれば終了コード1で止まり、GitHub Actionsでは公開されない。

## ビルド

    pip install pillow
    python3 build.py

YouTubeの埋め込み可否と日本での再生制限も確かめる場合は、環境変数 `YT_API_KEY` を渡す。GitHubではリポジトリのSecretsに `YT_API_KEY` を登録すれば、`.github/workflows/pages.yml` が自動で使う。

## 設定（config.json）

- `site_name` … 日英のサイト名
- `site_name_signature` … 署名コメントに入る名前
- `base_url` … 公開URL。入れるとcanonical、hreflang、og:imageが絶対URLになる

## データ

- `data/works.json` … 本棚57作品。事実はすべて `{"v": 値, "src": [出典ID]}` の形で持つ
- `data/people.json` / `events.json` / `now.json` / `shelf.json` / `glossary.json`
- `data/sources.json` … 出典庫。ここにないIDを使うとビルドが止まる
- 版色は `works.json` の `plates` に4色を入れ、`status` を `"extracted"` にする。未抽出の作品は未刷りの紙色で出る

## 本文（texts/ja, texts/en）

作品IDごとに `{id}.md`。1行目の `rev: N` は日英で一致させる（片方だけの更新を検証で弾くため）。

    ## view      私見
    ## music     音楽性
    ## tech      テクノロジー
    ## context   周辺環境

本文中の記法は `{{ref:出典ID}}`（出典の番号付け）と `{{t:2:14}}`（YouTubeの再生点リンク）。

## tools/

私見とデータ追記に使った一回きりのスクリプト。`tools_views_*.py` は texts/ を上書きするので、本文を手で直したあとは実行しないこと。

## アートワーク（art/）

`art/{作品ID}.jpg`（png、webpも可）を置くと、その作品ページにジャケットが出て、版色が画像から自動で抽出される。画像を置いた作品には `works.json` の `art_src` に出典IDを入れること（入っていないと検証12で止まる）。作品IDは `data/works.json` の `id`（例：go、dig-your-own-holeは `dyoh`）。

## YouTube

動画IDは公式サイトの各ビデオページに埋め込まれているものを使っている（出典はそのページ）。動画がない作品は、`YT_API_KEY=... python3 tools/yt_resolve.py` で公式チャンネルとTopicから候補を探せる。`--apply` を付けると候補を works.json に入れる。

## 手元での確認

`dist/`のHTMLをファイルのままブラウザで開くと、YouTubeが「動画プレーヤーの設定エラー（エラー153）」で再生を拒否する（参照元が送られないため）。その場合プレーヤーはYouTubeを別タブで開く。埋め込みのまま確かめるときは、ローカルサーバーを立てて開く。

    cd dist && python3 -m http.server 8000
    # http://localhost:8000/ を開く

## BPMとキー（tools/measure.py）

音源そのものはリポジトリに入れない。手元の音源かrekordboxのライブラリを読んで、works.jsonに書き込む。

    # rekordbox（推奨）：ファイル → ライブラリをxml形式でエクスポート → 読み込む
    python3 tools/measure.py --rekordbox ~/Desktop/rekordbox.xml
    # 音源フォルダを直接解析（ffmpeg、numpy、scipyが必要）
    python3 tools/measure.py --audio ~/Music/TheChemicalBrothers
    # 書き込まずに結果だけ見る
    python3 tools/measure.py --rekordbox ~/Desktop/rekordbox.xml --dry-run

rekordboxの値を優先し、解析値では上書きしない（`--overwrite`で上書き）。リミックスやエディットより原曲を選ぶ。作品ページには値と、その取得方法（rekordboxか自動解析か）が出る。

## プレビュー（tools/preview_bundle.py）

    python3 tools/preview_bundle.py preview.html

全ページを1枚のHTMLにまとめる。スマホなどでページ間リンクを確かめる用。

保存済みの `notes/preview.html` を更新する場合は `python3 tools/preview_bundle.py notes/preview.html` を実行します。ロゴ・favicon・Apple Touch icon は埋め込み式で、HTMLを別の場所に移しても同じデザインを表示します。

## ロゴと関連画像

ヘッダー・404・SNS共有画像・端末用アイコンは、`src/brand/` の承認済み myChems ロゴを共通で使用します。端末用画像は `python3 tools/generate_icons.py` で生成し、`build.py` の画像ハッシュ一覧も更新します。旧アイコンのURLと、ルートの `favicon.ico`・`apple-touch-icon.png`・`apple-touch-icon-precomposed.png` にも同じ画像を配信します。`python3 tests/test-device-icons.py` で全ページの参照先・互換画像・マスク領域を検証できます。

## Evergreen archive (2026-10-31)

News coverage and upcoming-event listings have ended. The bilingual home page now prioritises the listening routes, albums, historical timeline and credited collaborators. Old `now/` URLs remain as a navigation guide, not an active news archive. `data/now.json` is retained as original research material but is never rendered; retired future-event records remain in `notes/retired-news/`. Historical source references and release dates are not rewritten.

The fixed source revision timestamp records this actual shared-navigation and editorial restructuring, not a build/deployment time. Visible JST, WebPage.dateModified and sitemap lastmod agree. Original release/publication and source-check dates are preserved. The separately approved wordmark and compact profile are retained.

Publication dependency: merge the compact-profile PR into main first; retarget this archive PR to main; inspect the final diff and rerun exact-head CI before merging. Merging into a feature branch is not publication.

Run `python3 tests/test-archive.py` after the build, plus the existing Node regression tests.

## Reading utilities and recovery

The 218 editorial pages retain their catalog, audio embeds and sources. Shared controls offer native sharing or copy/manual-select fallback, a back-to-top link and optional home-screen shortcut instructions (online web shortcut, not offline PWA). A bilingual noindex404 uses absolute project URLs and is excluded from the sitemap. `llms-full.txt` exports existing main-page text with canonical page links; it does not introduce new factual claims or grant rights to third-party material. No service worker, advertising, CSP or analytics setting changes. Shared utilities are an actual content/UI revision, so their source date advances the218 page lastmods; original release and profile-author dates are retained.

Run `node tests/test-reading-tools.cjs` and the Playwright browser suite. Clipboard denial, share cancellation/failure, manual copy, keyboard entry, narrow/landscape layout and nested404 recovery are exercised with external requests blocked. Real device installation and real YouTube playback remain outside these tests.

## Official listening pilot

The bilingual works indexes include a visible, click-to-load YouTube player. Existing work-page embeds are unchanged. `data/listening-sources.json` is a separate reviewed source/recording ledger; `tools/listening_catalog.py` joins only exact bindings to the 57 works / 225 track occurrences. Missing tracks remain present rather than being replaced by unofficial uploads or a different mix.

Initial pilot: seven of Exit Planet Dust’s eleven entries are source-matched: In Dust We Trust; Song To The Siren (Sabresonic 1994 live version); Three Little Birdies Down Beats; Chico’s Groove; One Too Many Mornings; Life Is Sweet; Alive Alone. Each has Universal Music Group-delivered, autogenerated Official Artist Channel metadata naming the album. This is not a claim of a physical pressing/master, complete album coverage, or successful playback: the ordinary browser check timed out before Play, and runtime status remains `unchecked`. Digital delivery dates are not substituted for the existing original-release date.

Current source ledger: 47/225 source-matched occurrences (Exit Planet Dust 10, Dig Your Own Hole 10, Surrender 3, Come with Us 10, Push the Button 3, We Are the Night 11), with actual playback still unverified. Optional continuous listening defaults off. After current PLAYING and ENDED, only the immediately following admitted official recording is requested in the visible frame. Missing/unavailable tracks stop without skipping; browser autoplay blocking leaves native manual Play available. Selection/page exit invalidates old callbacks; provenance counts never become playback counts. No source research or API readiness is treated as real playback.

Buffering guidance: after 15 seconds of uninterrupted buffering, one informational notice offers Stop or another track. No retry, automatic skip, availability diagnosis or source-count change. Stop disposes the visible player and cancels continuation; stale timers and callbacks cannot update a newer selection. A live PR9 observation reached buffering but currentTime remained zero; successful playback is still unverified.

Playback usability revision after user feedback: a one-click matched-source entry and direct track-click playback request open a visible lower-right dock inspired by Premium Cuts. YouTube's documented constructor creates its standard iframe, with site origin and playsinline; no permission/branding suppression. Play/pause/Stop, close-with-stop and expanded visible view stay accessible. Missing positions remain explicit and stop continuous playback. This fixes the concrete multi-step/disabled-first-track entry problem; it is not proof that every user's streaming problem is solved. A control observation of Premium Cuts also stalled at currentTime zero in the cloud browser, so that observation alone cannot diagnose a Chems-specific network failure. Real playback remains unverified.
