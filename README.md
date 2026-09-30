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

- `data/works.json` … 本棚54作品。事実はすべて `{"v": 値, "src": [出典ID]}` の形で持つ
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
