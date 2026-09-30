# 業務指示書　my Chems　ジャケット画像ほかの作業（Claude Cowork 用）

作成：2026年9月30日　対象：mychems-v5 以降
サイト：my Chems（公開URLは未定。GitHub Pagesに置く予定）
依頼主：宮崎直哉（なおちゃん）。私見の筆名は「DJ Naoyaman」

---

## 0. はじめに読むこと

- 作業するフォルダは `chem/`（サイトの本体）です。この指示書は `chem/notes/cowork-brief.md` にあります。
- 作業は **作業A → 作業B → 作業C** の順です。作業Aは必須、BとCは依頼主が頼んだときだけ行います。それぞれの終わりで報告してください。
- 判断に迷うものは採用しないでください。迷うものの例：
  - 公式のジャケットかどうか確かめられない
  - 動画の一場面、バナー、告知画像である可能性がある
  - 透かしや、他のサイトのロゴが入っている
  - 初回盤と再発盤で絵柄が違い、どちらか分からない

  報告の「採用しなかったもの」に理由とともに回してください。空けておく方が、誤った画像を載せるより害が小さい、というのがこのサイトの方針です。
- 画像の中身を推測で説明しないでください。キャプションは、ビルドが「アートワーク（批評・紹介のための引用）」と出典番号を自動で付けます。
- ページのHTML（`dist/`）は直接直しません。変えてよいのは `art/`、`data/works.json`、`data/sources.json`、`notes/` だけです。ページはすべて `python3 build.py` で作り直します。
- 音源ファイルと rekordbox の書き出しファイルは、`chem/` の中に入れないでください（検証12で止まります）。

---

## 1. 作業A　ジャケット画像を置く（必須）

### 目的
本棚の54作品のジャケットを `art/{作品ID}.jpg` に置き、どこから取ったかを記録します。画像を置くと、ビルドがその画像から版色を抽出し、作品ページ全体がその色に変わります。

### ファイル名の付け方
- `art/{作品ID}.jpg`。作品IDは下の表の1列目（`data/works.json` の `id`）です。例：「Dig Your Own Hole」は `art/dyoh.jpg`
- 形式はJPEG、長い辺は1200px以内。スクリプトで取った画像は自動でそうなります。
- 手で置く場合も、トリミング、色の補正、文字やロゴの消去はしないでください。縮小だけにします。
  `python3 -c "from PIL import Image; im=Image.open('入力ファイル').convert('RGB'); im.thumbnail((1200,1200)); im.save('art/作品ID.jpg', quality=90)"`

### 手順
1. `python3 tools/fetch_art.py --dry-run` を実行し、どのページから何を取るかを確かめる。
2. `python3 tools/fetch_art.py` を実行する。ネットワークの許可を求められたら、次の住所だけを許可する。
   - www.thechemicalbrothers.com（公式サイト）
   - cdn.prod.website-files.com（公式サイトの画像置き場）
3. `notes/art_report.csv` を開き、`status` ごとに次のとおり扱う。
   - `ok`：採用済み。画像を開き、作品名と一致するジャケットであることを目で確かめる。違っていたら `art/` から消し、`works.json` のその作品の `art_src` も消す。
   - `review`：正方形でない、または動画のサムネイルらしい画像です。`notes/art_review/` を開いて確かめ、ジャケットなら `art/{作品ID}.jpg` に移し、下の「出典の記録方法」で出典を入れる。ジャケットでなければ採用しない。
   - `none`／`error`：ブラウザで公式サイトの Music ページ（https://www.thechemicalbrothers.com/music）を開き、その作品のページを探す。見つかったら、ページのURLの最後の部分（スラッグ）を指定して取り直す。
     `python3 tools/fetch_art.py --only fcs --slug fcs=fourteenth-century-sky`
4. 公式サイトにない作品（初期のEP、日本限定盤など）は、次の順で探す。**保存する前に、候補を依頼主に見せて確認を取ってください。**
   1. レーベル（Virgin、EMI、Universal Music）の公式ページ
   2. Discogs の、その作品の初回盤のリリースページ
5. `python3 build.py` を実行し、NGが0件であること、11番の「版色が未抽出の作品数」が減っていることを確かめる。
6. `python3 tools/preview_bundle.py notes/preview.html` でプレビューを作り、画像を置いた作品のページ上部をスクリーンショットで確かめる。アルバム、シングル、EPを少なくとも1枚ずつ。文字が読みにくいページがないかも見る（コントラストは検証6が機械的に確かめますが、目でも確かめます）。

### 採用の基準
- 公式サイト、またはレーベルの公式ページに掲載されている画像を優先する
- 初回盤のジャケットを優先する。再発盤しかない場合は、報告の備考に「再発盤」と書く
- 正方形に近い（縦横の比が0.9〜1.1）
- 透かし、他のサイトのロゴ、文字の加工がない

### 出典の記録方法
スクリプトで取った作品は自動で記録されます。手で置いた作品は、次の2か所に書いてください。

`data/sources.json` に1件追加する：
```json
{"id": "cb-r-fourteenth-century-sky", "publisher": "The Chemical Brothers", "lang": "en",
 "title": "Official site: Fourteenth Century Sky (release page)",
 "url": "https://www.thechemicalbrothers.com/music-videos/fourteenth-century-sky",
 "date": "", "checked": "2026-10-01"}
```
`data/works.json` のその作品に `art_src` を足す：
```json
"art_src": ["cb-r-fourteenth-century-sky"]
```
出典IDは、公式サイトなら `cb-r-{スラッグ}`、レーベルなら `label-{作品ID}`、Discogsなら `discogs-{作品ID}` とします。`art_src` がない画像があると、検証12で止まります。

### 作品IDの一覧（54作品）

| 作品ID | 作品 | 種別 | 年 | 公式サイトのページ |
|---|---|---|---|---|
| `fcs` | Fourteenth Century Sky | EP | 1994 | 一覧から探す |
| `mmm` | My Mercury Mouth E.P | EP | 1994 | 一覧から探す |
| `lh` | Leave Home | シングル | 1995 | `leave-home` |
| `epd` | Exit Planet Dust | アルバム | 1995 | `exit-planet-dust` |
| `lis` | Life Is Sweet | シングル | 1995 | `life-is-sweet` |
| `lof` | Loops of Fury | EP | 1996 | `loops-of-fury` |
| `ss` | Setting Sun | シングル | 1996 | `setting-sun` |
| `brb` | Block Rockin' Beats | シングル | 1997 | `block-rockin-beats-single` |
| `dyoh` | Dig Your Own Hole | アルバム | 1997 | `dig-your-own-hole` |
| `el` | Elektrobank | シングル | 1997 | `elektrobank` |
| `ppr` | The Private Psychedelic Reel | シングル | 1997 | `the-private-psychedelic-reel` |
| `hbhg` | Hey Boy Hey Girl | シングル | 1999 | `hey-boy-hey-girl-single` |
| `sur` | Surrender | アルバム | 1999 | `surrender` |
| `lfb` | Let Forever Be | シングル | 1999 | `let-forever-be` |
| `ooc` | Out of Control | シングル | 1999 | `out-of-control` |
| `mr` | Music:Response | EP | 2000 | `music-response` |
| `ibia` | It Began in Afrika | シングル | 2001 | `it-began-in-afrika` |
| `sg` | Star Guitar | シングル | 2002 | `star-guitar` |
| `cwu` | Come with Us | アルバム | 2002 | `come-with-us` |
| `cwtt` | Come with Us / The Test | シングル | 2002 | `come-wih-us-the-test` |
| `jpep` | Come with Us/Japan Only EP | EP | 2002 | 一覧から探す |
| `amep` | AmericanEP | EP | 2002 | `american-ep` |
| `tgp` | The Golden Path | シングル | 2003 | `the-golden-path-2` |
| `gyh` | Get Yourself High | シングル | 2003 | `get-yourself-high` |
| `gal` | Galvanize | シングル | 2005 | `galvanize-single` |
| `ptb` | Push the Button | アルバム | 2005 | `push-the-button` |
| `bel` | Believe | シングル | 2005 | `believe-single` |
| `box` | The Boxer | シングル | 2005 | `the-boxer` |
| `l05` | Live 05 | EP | 2005 | `live-05` |
| `dia` | Do It Again | シングル | 2007 | `do-it-again-single` |
| `watn` | We Are the Night | アルバム | 2007 | `we-are-the-night` |
| `tsd` | The Salmon Dance | シングル | 2007 | `the-salmon-dance` |
| `mm` | Midnight Madness | シングル | 2008 | `midnight-madness` |
| `ev` | Escape Velocity | シングル | 2010 | 一覧から探す |
| `sw` | Swoon | シングル | 2010 | `swoon` |
| `fur` | Further | アルバム | 2010 | `further` |
| `aw` | Another World | シングル | 2010 | `another-world-single` |
| `cp` | Container Park | シングル | 2011 | 一覧から探す |
| `tfv` | Theme for Velodrome | シングル | 2012 | 一覧から探す |
| `go` | Go | シングル | 2015 | `go-single` |
| `unl` | Under Neon Lights | シングル | 2015 | `under-neon-lights-single` |
| `bite` | Born in the Echoes | アルバム | 2015 | `born-in-the-echoes` |
| `chem` | C-H-E-M-I-C-A-L | シングル | 2016 | 一覧から探す |
| `fy` | Free Yourself | シングル | 2018 | `free-yourself-single` |
| `mah` | MAH | シングル | 2019 | `mah` |
| `gtko` | Got to Keep On | シングル | 2019 | `got-to-keep-on-single` |
| `wgtt` | We've Got to Try | シングル | 2019 | 一覧から探す |
| `ng` | No Geography | アルバム | 2019 | `no-geography` |
| `dtyf` | The Darkness That You Fear | シングル | 2021 | 一覧から探す |
| `nr` | No Reason | シングル | 2023 | 一覧から探す |
| `la` | Live Again | シングル | 2023 | 一覧から探す |
| `gb` | Goodbye | シングル | 2023 | 一覧から探す |
| `sls` | Skipping Like a Stone | シングル | 2023 | 一覧から探す |
| `ftbf` | For That Beautiful Feeling | アルバム | 2023 | 一覧から探す |

「一覧から探す」の作品は、スクリプトが Music ページの一覧から自動で探します。見つからなければ手順3と4に進みます。

---

## 2. 作業B　BPMとキーを入れる（依頼主が頼んだときだけ）

1. 依頼主に、rekordbox のライブラリを書き出したファイルの場所を聞く（rekordbox → ファイル → ライブラリをxml形式でエクスポート）。ファイルは `chem/` の外に置いたまま使う。
2. `python3 tools/measure.py --rekordbox <xmlの場所> --dry-run` で結果を確かめる。
3. 問題がなければ `--dry-run` を外して実行する。
4. rekordbox に入っていない曲は、依頼主が音源フォルダを指定したときだけ `python3 tools/measure.py --audio <フォルダ>` で解析する。音源はコピーせず、読むだけにする。
5. `python3 build.py` を実行する。

---

## 3. 作業C　動画のない17作品を探す（依頼主が頼んだときだけ）

- 環境変数 `YT_API_KEY` がある場合：`python3 tools/yt_resolve.py` で候補を出し、`data/yt_candidates.json` を依頼主に見せてから `--apply` する。
- ない場合：ブラウザで公式チャンネル（https://www.youtube.com/user/thechemicalbrothers）と「The Chemical Brothers - Topic」を検索する。
- 採用するのは、公式チャンネルかTopicの動画だけ。ファンのアップロード、非公式の歌詞動画は採用しない。
- 記録方法：`works.json` のその作品の `embed.mv` を `{"id": "動画ID", "src": ["yt-{作品ID}"], "verified": false}` にし、`sources.json` に動画のURLを出典として登録する。

---

## 4. 完了の条件

- 作業A：54作品すべてについて、`art/` に置いたか、置かなかった理由が報告に書かれている
- 置いた画像すべてに `art_src` があり、`sources.json` に出典が登録されている
- `python3 build.py` のNGが0件
- 変えたファイルが `art/`、`data/works.json`、`data/sources.json`、`notes/` の中だけ
- `chem/` 全体（`dist/` を含む）をZIPにして返す

## 5. 報告の形

```
### 作業A　ジャケット画像
採用：◯/54

| 作品ID | 作品 | 出典ページ | 備考（再発盤など） |
|---|---|---|---|

採用しなかったもの
| 作品ID | 作品 | 理由 |
|---|---|---|

確かめたスクリーンショット：（ファイル名）
build.py の結果：（11番と12番の行をそのまま貼る）
```
作業B・Cを行った場合は、更新した件数と、未計測・未発見の作品名を同じ形で書いてください。

## 6. やってはいけないこと

- `dist/` のHTMLを直接直す
- 画像のトリミング、色の補正、文字やロゴの消去
- 出典の分からない画像を置く
- 音源や rekordbox の書き出しファイルを `chem/` に入れる
- 私見（`texts/`）を書き換える
