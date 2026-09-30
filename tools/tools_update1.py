"""私見執筆のために確認した事実を data/*.json に追記する（1回だけ使う）"""
import json, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
L = lambda n: json.load(open(os.path.join(D, n), encoding='utf-8'))
def S(n, o): json.dump(o, open(os.path.join(D, n), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
sources, works, people, events = L('sources.json'), L('works.json'), L('people.json'), L('events.json')
W = {w['id']: w for w in works}; SID = {s['id'] for s in sources}

NEW = [
 ('wp-epd', 'Wikipedia', 'en', 'Exit Planet Dust', 'https://en.wikipedia.org/wiki/Exit_Planet_Dust', ''),
 ('nad-epd', 'National Album Day', 'en', 'The Chemical Brothers – Exit Planet Dust', 'https://www.nationalalbumday.co.uk/product/the-chemical-brothers-exit-planet-dust', '2024'),
 ('clash-10', 'Clash', 'en', '10 Things You Never Knew About… The Chemical Brothers', 'https://www.clashmusic.com/?p=84536', '2016'),
 ('trouser', 'Trouser Press', 'en', 'Chemical Brothers', 'https://trouserpress.com/reviews/chemical-brothers/', ''),
 ('wp-dyoh', 'Wikipedia', 'en', 'Dig Your Own Hole', 'https://en.wikipedia.org/wiki/Dig_Your_Own_Hole', ''),
 ('wp-brb', 'Wikipedia', 'en', "Block Rockin' Beats", 'https://en.wikipedia.org/wiki/Block_Rockin%27_Beats', ''),
 ('wp-el', 'Wikipedia', 'en', 'Elektrobank', 'https://en.wikipedia.org/wiki/Elektrobank', ''),
 ('wp-ss', 'Wikipedia', 'en', 'Setting Sun (The Chemical Brothers song)', 'https://en.wikipedia.org/wiki/Setting_Sun_(The_Chemical_Brothers_song)', ''),
 ('wp-domnic', 'Wikipedia', 'en', 'Dom and Nic', 'https://en.wikipedia.org/wiki/Dom_and_Nic', ''),
 ('tower-dyoh', 'TOWER RECORDS ONLINE', 'ja', 'Dig Your Own Hole', 'https://tower.jp/item/175671', ''),
 ('grammy-dyoh', 'Recording Academy', 'en', "The Chemical Brothers' Dig Your Own Hole at 25", 'https://cms.grammy.com/chemical-brothers-dig-your-own-hole-25th-anniversary-block-rockin-beats/', '2022'),
 ('es-surrender', 'Wikipedia (es)', 'es', 'Surrender (álbum de The Chemical Brothers)', 'https://es.wikipedia.com/wiki/Surrender_(album_de_The_Chemical_Brothers)', ''),
 ('sde-surrender', 'SuperDeluxeEdition', 'en', 'Chemical Brothers / Surrender 20th anniversary reissue', 'https://superdeluxeedition.com/?p=150965', '2019'),
 ('nme-1999', 'NME', 'en', 'The Chemical Brothers – Surrender (review)', 'https://www.nme.com/reviews/the-chemical-brothers/1112', '1999'),
 ('wp-sg', 'Wikipedia', 'en', 'Star Guitar', 'https://en.wikipedia.org/wiki/Star_Guitar', ''),
 ('diffuser-cwu', 'Diffuser', 'en', "15 Years Ago: Chemical Brothers Ramp Up Their Sound on 'Come With Us'", 'https://diffuser.fm/chemical-brothers-come-with-us/', '2017'),
 ('ud-cwu', 'uDiscover Music', 'en', "'Come With Us': Behind The Chemical Brothers' Unbeatable Offer", 'https://www.udiscovermusic.com/stories/the-chemical-brothers-come-with-us-album/', ''),
 ('russ-cwu', 'russ.fm', 'en', 'Come With Us (release notes)', 'https://russ.fm/albums/come-with-us-108093', ''),
 ('md-cwu', 'Music Direct', 'en', 'The Chemical Brothers – Come with Us', 'https://www.musicdirect.com/music/vinyl/the-chemical-brothers-come-with-us-vinyl-2lp', ''),
 ('wp-ptb', 'Wikipedia', 'en', 'Push the Button (The Chemical Brothers album)', 'https://en.wikipedia.org/wiki/Push_the_Button_(The_Chemical_Brothers_album)', ''),
 ('ud-ptb', 'uDiscover Music', 'en', "'Push The Button': The Chemical Brothers Keep Their Finger On The Pulse", 'https://www.udiscovermusic.com/?p=2145805', ''),
 ('docomo-ptb', 'dショッピング（発売・販売元提供資料）', 'ja', 'The Chemical Brothers / Push The Button', 'https://dshopping.docomo.ne.jp/products/0081643068', '2016'),
 ('es-ptb', 'Wikipedia (es)', 'es', 'Push the Button (álbum)', 'https://es.wikipedia.com/wiki/Push_the_Button_(%C3%A1lbum)', ''),
 ('wp-watn', 'Wikipedia', 'en', 'We Are the Night (album)', 'https://en.wikipedia.org/wiki/We_Are_the_Night_(album)', ''),
 ('spin-2007', 'SPIN', 'en', 'Chemical Brothers Recruit Klaxons, Midlake for New Album', 'https://www.spin.com/2007/04/chemical-brothers-recruit-klaxons-midlake-new-album/', '2007-04'),
 ('popm-watn', 'PopMatters', 'en', 'The Chemical Brothers: We Are the Night', 'https://popmatters.com/the-chemical-brothers-we-are-the-night-2496234816.html', '2007'),
 ('it-watn', 'Wikipedia (it)', 'it', 'We Are the Night', 'https://it.wikipedia.com/wiki/We_Are_The_Night', ''),
 ('exclaim-watn', 'Exclaim!', 'en', 'The Chemical Brothers – We Are The Night', 'https://exclaim.ca/music/article/chemical_brothers-we_are_night', '2007-07-17'),
 ('wp-brotherhood', 'Wikipedia', 'en', 'Brotherhood (The Chemical Brothers album)', 'https://en.wikipedia.org/wiki/Brotherhood_(The_Chemical_Brothers_album)', ''),
 ('de-wiki', 'Wikipedia (de)', 'de', 'The Chemical Brothers', 'https://de.wikipedia.org/wiki/The_Chemical_Brothers', ''),
 ('es-s9303', 'Wikipedia (es)', 'es', 'Singles 93-03', 'https://wiki.undernet.uy/content/wikipedia_es_all_maxi_2024-02/A/Singles_93-03', ''),
 ('wp-further', 'Wikipedia', 'en', 'Further (The Chemical Brothers album)', 'https://en.wikipedia.org/wiki/Further_(The_Chemical_Brothers_album)', ''),
 ('hmv-further', 'HMV', 'en', 'The Chemical Brothers – Further', 'https://hmv.com/store/music/cd/further-(1)', ''),
 ('fact-2012', 'FACT', 'en', 'Theme For Velodrome: The Chemical Brothers compose official Olympic Games track', 'https://factmag.com/2012/07/19/theme-for-velodrome-the-chemical-brothers-compose-official-olympic-games-track', '2012-07-19'),
 ('stereoboard-2012', 'Stereoboard', 'en', "The Chemical Brothers Release Their Official Olympic Song 'Velodrome'", 'https://www.stereoboard.com/content/view/173900/9', '2012-07-25'),
 ('mxdwn-hanna', 'mxdwn', 'en', 'The Chemical Brothers – Hanna (Original Motion Picture Soundtrack)', 'https://music.mxdwn.com/2011/08/25/reviews/the-chemical-brothers-hanna-original-motion-picture-soundtrack/amp/', '2011-08-25'),
 ('umc-bite', 'Universal Music Canada', 'en', 'The Chemical Brothers to release Born In The Echoes July 17', 'https://universalmusic.ca/press-releases/the-chemical-brothers-to-release-born-in-the-echoes-july-17', '2015-04-23'),
 ('nme-wideopen', 'NME', 'en', "The Chemical Brothers unveil new video for Beck collaboration 'Wide Open'", 'https://www.nme.com/?p=1190843', '2016'),
 ('rs-bite', 'Rolling Stone (via Station Film)', 'en', "Born in the Echoes track 'Wide Open' video by dom&nic", 'https://stationfilm.com/?p=1013', '2016'),
 ('ondarock-unl', 'OndaRock', 'it', 'Chemical Brothers e St. Vincent insieme per il brano "Under The Neon Lights"', 'https://www.ondarock.it/?p=32415', '2015-06-23'),
 ('wp-disc-m', 'Wikipedia (mirror)', 'en', 'The Chemical Brothers discography', 'https://en.wikipedia.com/wiki/Live_05', ''),
 ('apple-ng', 'Apple Music', 'en', 'No Geography (album notes)', 'https://music.apple.com/album/1450389806', '2019'),
 ('quietus-ng', 'The Quietus', 'en', 'The Chemical Brothers – No Geography', 'https://thequietus.com/?p=26319', '2019'),
 ('bb-ng', 'Billboard', 'en', 'The Chemical Brothers Break Down No Geography Track by Track', 'https://www.billboard.com/articles/news/dance/8506929/the-chemical-brothers-no-geography-track-breakdown', '2019-04'),
 ('dummy-ng', 'DUMMY', 'en', 'The Chemical Brothers: No Geography interview', 'https://www.dummymag.com/features/the-chemical-brothers-no-geography-interview/', '2019'),
 ('numero-2019', 'Numéro', 'fr', 'The Chemical Brothers s’invite chez les Power Rangers', 'https://numero.com/culture/musique/the-chemical-brothers-sinvite-chez-les-power-rangers/', '2019-06-11'),
 ('jb-ng', 'JB Hi-Fi', 'en', 'The Chemical Brothers – No Geography', 'https://www.jbhifi.com.au/products/cd-chemical-brothers-the-no-geography-cd', '2019'),
 ('releasemag-ng', 'Release Magazine', 'en', 'Chemical Brothers – No Geography', 'https://www.releasemagazine.net/reviews/chemical-brothers-no-geography/', '2019-05-14'),
 ('umc-dtyf', 'Universal Music Canada', 'en', 'The Chemical Brothers release "The Darkness That You Fear," out today', 'https://www.universalmusic.ca/press-releases/the-chemical-brothers-the-darkness-that-you-fear-out-today', '2021-04-23'),
 ('bv-dtyf', 'BrooklynVegan', 'en', 'The Chemical Brothers bring sunshine to new single "The Darkness That You Fear"', 'https://www.brooklynvegan.com/the-chemical-brothers-bring-sunshine-to-new-single-the-darkness-that-you-fear/', '2021-04'),
 ('umc-ftbf', 'Universal Music Canada', 'en', "The Chemical Brothers' album For That Beautiful Feeling out now", 'https://universalmusic.ca/press-releases/the-chemical-brothers-album-for-that-beautiful-feeling-out-now', '2023-09-08'),
 ('umc-ftbf2', 'Universal Music Canada', 'en', 'The Chemical Brothers – For That Beautiful Feeling', 'https://www.universalmusic.ca/press-releases/the-chemical-brothers-for-that-beautiful-feeling', '2023'),
 ('nialler-ftbf', 'Nialler9', 'en', 'The Chemical Brothers announce tenth album For That Beautiful Feeling', 'https://nialler9.com/the-chemical-brothers-announce-tenth-album-for-that-beautiful-feeling', '2023'),
 ('umc-sls', 'Universal Music Canada', 'en', 'The Chemical Brothers release "Skipping Like A Stone" (featuring Beck)', 'https://www.universalmusic.ca/press-releases/the-chemical-brothers-release-skipping-like-a-stone-featuring-beck', '2023-08-21'),
]
for i, pub, lang, title, url, d in NEW:
    if i not in SID: sources.append({'id': i, 'publisher': pub, 'lang': lang, 'title': title, 'url': url, 'date': d, 'checked': '2026-09-30'})

fact = lambda v, s: {'v': v, 'src': s if isinstance(s, list) else [s]}
# ---- 正確な発売日
DATES = {'lh': ('1995-06-05', 'wp-epd'), 'lis': ('1995-08-28', 'wp-epd'), 'ss': ('1996-09-30', 'wp-dyoh'), 'brb': ('1997-03-24', 'wp-dyoh'),
         'el': ('1997-09-08', 'wp-dyoh'), 'ppr': ('1997-12-01', 'wp-dyoh'), 'hbhg': ('1999-05-26', 'wp-surrender'), 'lfb': ('1999-07-23', 'wp-surrender'),
         'ooc': ('1999-10-08', 'wp-surrender'), 'sg': ('2002-01-14', 'wp-sg'), 'tgp': ('2003-09-15', 'de-wiki'), 'gyh': ('2003-11-24', 'es-s9303'),
         'gal': ('2005-01-17', 'wp-ptb'), 'bel': ('2005-05-02', 'wp-ptb'), 'box': ('2005-07-11', 'wp-ptb'), 'tsd': ('2007-09-10', 'wp-watn'),
         'mm': ('2008-08-03', 'de-wiki'), 'ev': ('2010-04-19', 'wp-further'), 'sw': ('2010-05-09', 'wp-further'), 'aw': ('2010-08-16', 'wp-further'),
         'tfv': ('2012-07-30', 'stereoboard-2012'), 'dtyf': ('2021-04-23', 'umc-dtyf'), 'sls': ('2023-08-21', 'umc-sls'), 'fur': ('2010-06-14', 'wp-further')}
for k, (d, s) in DATES.items(): W[k]['records']['date'] = fact(d, s)

def note(wid, ja, en, src): W[wid]['notes'].append({'ja': ja, 'en': en, 'src': src if isinstance(src, list) else [src]})
def cred(wid, pid, role, src, track=None):
    c = {'person': pid, 'role': role, 'src': src if isinstance(src, list) else [src]}
    if track: c['track'] = track
    W[wid]['credits'].append(c)
def tst(wid, who_ja, who_en, orig, ja, cja, cen, src):
    W[wid]['testimony'].append({'who': {'ja': who_ja, 'en': who_en}, 'orig_lang': 'en', 'orig': orig, 'ja': ja, 'ctx': {'ja': cja, 'en': cen}, 'src': [src]})

# 最多記録の表現を「並んだ」にそろえる（NMEは“equalling the record”）
for n in W['bite']['notes']:
    if n['src'] == ['gn-2015']:
        n.update(ja='全英1位。6作目の1位で、ダンス・アクトとしての最多記録に並んだ（2015年時点）', en='UK No. 1, their sixth, equalling the record for the most No. 1 albums by a dance act (as of 2015)', src=['gn-2015', 'nme-wideopen'])
for c in W['go'].get('context', []):
    if c['src'] == ['gn-2015']:
        c.update(ja='同じ年の『Born in the Echoes』は全英1位。6作目の1位で、ダンス・アクトとしての最多記録に並んだ', en='The same year, Born in the Echoes went to No. 1 in the UK, their sixth, equalling the record for a dance act', src=['gn-2015', 'nme-wideopen'])

note('epd', '1993年8月から1994年11月にかけて録音。題は、ダスト・ブラザーズからの改名にちなむ', 'Recorded August 1993 to November 1994; the title refers to the change of name from the Dust Brothers', 'wp-epd')
note('fcs', '収録曲「Chemical Beats」が、のちのバンド名の由来になった', 'Its track "Chemical Beats" gave the band its later name', ['wp-epd', 'nad-epd'])
note('lh', '冒頭に、クラフトワーク「Ohm Sweet Ohm」の出だしが短くサンプルされている', 'Opens with a short sample from the start of Kraftwerk\'s "Ohm Sweet Ohm"', 'wp-epd')
note('lof', '表題曲に「Chemical Beats」のリミックスと新曲2曲を組み合わせたEP', 'Pairs the title track with a remix of "Chemical Beats" and two new tracks', 'trouser')
note('ss', 'ノエル・ギャラガーは「Life Is Sweet」を聴いて二人との共作を望んだ', 'Noel Gallagher asked to work with the duo after hearing "Life Is Sweet"', 'wp-ss')
note('ss', 'MVの撮影にノエルは参加できず、トムとエドが自分たち役で短く出演した。この出演はのちのMVでも続く', 'Noel could not appear in the video; Tom and Ed made a cameo as themselves, a habit that continued in later videos', 'wp-domnic')
note('ss', 'MTVは、番組の軸をエレクトロニカへ移す際にこのMVをきっかけの一つに挙げた', 'MTV cited the video as an inspiration when it shifted its format towards electronica', 'wp-domnic')
note('brb', '作者はトム・ローランズ、エド・シモンズ、ジェシー・ウィーヴァー（スクーリー・D）。録音はオリノコ・スタジオ', 'Written by Tom Rowlands, Ed Simons and Jesse Weaver (Schoolly D); recorded at Orinoco', 'wp-brb')
note('brb', '1998年のグラミー賞で最優秀ロック・インストゥルメンタル・パフォーマンスを受賞', 'Won Best Rock Instrumental Performance at the 1998 Grammy Awards', ['tower-dyoh', 'clash-10'])
note('dyoh', 'つなぎ目なくミックスされたDJセットのように曲順が組まれている', 'Sequenced like a continuously mixed DJ set', 'grammy-dyoh')
note('dyoh', 'ゲストはノエル・ギャラガー、ベス・オートン。ジョナサン・ドナヒューがクラリネットで参加', 'Guests Noel Gallagher and Beth Orton; Jonathan Donahue on clarinet', 'tower-dyoh')
note('el', 'MVはスパイク・ジョーンズ。ソフィア・コッポラが体操選手を演じた', 'Video by Spike Jonze, with Sofia Coppola as a gymnast', 'wp-el')
note('el', '『Singles 93–03』にも『Brotherhood』にも収録されていない', 'Included on neither Singles 93–03 nor Brotherhood', 'wp-el')
note('ppr', '番号入りの盤だったため、UKシングル・チャートの集計対象外', 'A numbered release, so ineligible for the UK Singles Chart', 'wp-dyoh')
note('sur', '日本では1999年6月7日、UKより2週間早く発売された', 'Released in Japan on 7 June 1999, two weeks ahead of the UK', 'wp-surrender')
note('sur', '2019年、カタログで初めてのデラックス盤として20周年盤が出た', 'In 2019 its 20th-anniversary edition became the first deluxe edition in their catalogue', 'sde-surrender')
note('lfb', 'ビートルズへのオマージュとされる', 'Described as a homage to the Beatles', 'wp-surrender')
note('sg', 'MVはゴンドリー兄弟。同期を方眼紙で設計し、身近な物で景色の模型を組んで撮影したとされる', 'Video by the Gondry brothers, synchronised on graph paper, with the scenery modelled from everyday objects', 'wp-sg')
note('sg', 'パーカーのMIDIフライ・ギターを使い、トムのギターをエフェクト経由でコンピューターに取り込んだ音が使われている', 'Uses Tom\'s guitar, a Parker MIDI Fly, processed into the computer', 'diffuser-cwu')
note('ibia', '2000年末のU2の前座で初演。2001年夏にホワイト・レーベルでDJに配ってから、9月に正式発売', 'Premiered while supporting U2 in late 2000, sent to DJs on white label in summer 2001, released in September', 'diffuser-cwu')
note('cwu', 'サンプル元として、ジム・イングラム、エレクトロニック・システム、ジ・アソシエーション、C・ニエメンらがクレジットされている', 'Sample credits include Jim Ingram, Electronic System, The Association and C. Niemen', 'russ-cwu')
note('cwtt', '「Come with Us」はファットボーイ・スリムが手を入れた版でシングルになった', '"Come with Us" was reworked by Fatboy Slim for the single', 'ud-cwu')
note('gal', 'アメリカでは2004年11月22日に先行発売。曲の土台にモロッコのシャアビの音楽が使われている', 'Released in the US on 22 November 2004; built on a Moroccan chaabi sample', ['wp-ptb', 'ud-ptb'])
note('gal', 'グラミー賞で最優秀ダンス・レコーディングを受賞', 'Won the Grammy for Best Dance Recording', 'docomo-ptb')
note('ptb', '2006年1月、グラミー賞の最優秀エレクトロニック/ダンス・アルバムを受賞。録音はミロコとニューヨークのヒット・ファクトリー', 'Won the Grammy for Best Electronic/Dance Album in January 2006; recorded at Miloco and The Hit Factory, New York', 'wp-ptb')
note('ptb', '一部の地域では、コピー・プロテクション付きのCDで発売された', 'Issued on copy-protected CD in some regions', 'es-ptb')
note('watn', '2006年、南ロンドンの防空壕で録音。5作続けての全英1位', 'Recorded in 2006 in a bomb shelter in South London; their fifth consecutive UK No. 1', ['spin-2007', 'wp-watn'])
note('watn', '第50回グラミー賞で最優秀エレクトロニック/ダンス・アルバムを受賞', 'Won Best Electronic/Dance Album at the 50th Grammy Awards', 'wp-watn')
note('mm', 'ベスト盤『Brotherhood』に新曲として収録', 'A new track on the compilation Brotherhood', 'wp-brotherhood')
note('fur', '全8曲にアダム・スミスとマーカス・ライアルによる専用の映像がある', 'All eight tracks come with films made for them by Adam Smith and Marcus Lyall', 'wp-further')
note('fur', 'グラミー賞の最優秀エレクトロニック/ダンス・アルバムにノミネート', 'Nominated for the Grammy for Best Electronic/Dance Album', 'hmv-further')
note('tfv', '2012年ロンドン・オリンピックのトラック・サイクリング会場のテーマとして作られた', 'Written as the theme for track cycling at the London 2012 Olympics', 'fact-2012')
note('bite', 'グラミー賞で、アルバムと「Go」の2部門にノミネート', 'Two Grammy nominations: the album and "Go"', 'rs-bite')
note('chem', '『Born in the Echoes』日本のツアー記念盤のボーナス・ディスクに収録された曲', 'First included on the bonus disc of the Japanese tour edition of Born in the Echoes', 'wp-disc-m')
note('ng', '最初の2作で使ったサンプラーを並べた「1997年コーナー」で制作。録音はエンジニアのスティーヴ・ダブ・ジョーンズと2016年から2019年にかけて', 'Made using a "1997 corner" of the samplers from their first two albums; recorded 2016–2019 with engineer Steve Dub Jones', ['apple-ng', 'bb-ng'])
note('dtyf', '『No Geography』以来の新曲。Appleの春の発表イベントで初めて流れた。ジャケットは故テリー・フロストの作品', 'Their first new music since No Geography, premiered at Apple\'s spring event; sleeve art by the late Sir Terry Frost', ['umc-dtyf', 'bv-dtyf'])
note('la', 'MVはドム＆ニックにとって10回目の共作。Arri XRのバーチャル・プロダクションのステージで撮影', 'Dom and Nic\'s tenth video with the band, shot on an Arri XR virtual production stage', 'nialler-ftbf')
note('ftbf', '同じ秋、30年を振り返る本『Paused in Cosmic Reflection』がホワイト・ラビットから出た（2023年10月26日）', 'The same autumn, the retrospective book Paused in Cosmic Reflection was published by White Rabbit (26 October 2023)', 'umc-ftbf')

# ---- 人物
NP = [('tim-burgess', 'ティム・バージェス', 'Tim Burgess'), ('beth-orton', 'ベス・オートン', 'Beth Orton'), ('richard-ashcroft', 'リチャード・アシュクロフト', 'Richard Ashcroft'),
      ('bernard-sumner', 'バーナード・サムナー', 'Bernard Sumner'), ('bobby-gillespie', 'ボビー・ギレスピー', 'Bobby Gillespie'), ('hope-sandoval', 'ホープ・サンドヴァル', 'Hope Sandoval'),
      ('jonathan-donahue', 'ジョナサン・ドナヒュー', 'Jonathan Donahue'), ('kele-okereke', 'ケリー・オケレケ', 'Kele Okereke'), ('ali-love', 'アリ・ラヴ', 'Ali Love'), ('nene', 'Nene', 'Nene')]
have = {p['id'] for p in people}
for a, b, c in NP:
    if a not in have: people.append({'id': a, 'name': {'ja': b, 'en': c}, 'notes': []})
cred('lis', 'tim-burgess', 'featured', 'nad-epd'); cred('box', 'tim-burgess', 'featured', 'ud-ptb')
cred('epd', 'beth-orton', 'album-guest', 'nad-epd', 'Alive Alone'); cred('dyoh', 'beth-orton', 'album-guest', 'tower-dyoh', 'Where Do I Begin'); cred('cwu', 'beth-orton', 'album-guest', 'ud-cwu', "The State We're In")
cred('cwtt', 'richard-ashcroft', 'featured', 'russ-cwu'); cred('ooc', 'bernard-sumner', 'featured', 'es-surrender'); cred('ooc', 'bobby-gillespie', 'featured', 'es-surrender')
cred('sur', 'hope-sandoval', 'album-guest', 'es-surrender', 'Asleep from Day'); cred('sur', 'jonathan-donahue', 'album-guest', 'es-surrender', 'Dream On')
cred('ppr', 'jonathan-donahue', 'featured', 'tower-dyoh'); cred('bel', 'kele-okereke', 'featured', 'es-ptb')
cred('dia', 'ali-love', 'featured', ['it-watn', 'spin-2007']); cred('bite', 'ali-love', 'album-guest', 'umc-bite', 'EML Ritual'); cred('ng', 'nene', 'album-guest', ['quietus-ng', 'bb-ng'], 'Eve of Destruction')
for p in people:
    if p['id'] == 'nene': p['notes'] = [{'ja': '日本のラッパー。『No Geography』の「Eve of Destruction」に参加し、MVではオーロラとともに特撮番組のようなヒーローを演じた', 'en': 'Japanese rapper on "Eve of Destruction" from No Geography; in the video she and Aurora play tokusatsu-style heroes', 'src': ['quietus-ng', 'numero-2019']}]
    if p['id'] == 'dom-and-nic': p['notes'] = [{'ja': '1996年の「Setting Sun」から、2023年の「Live Again」で10回目の共作になった', 'en': 'From "Setting Sun" in 1996 to "Live Again" in 2023, their tenth video with the band', 'src': ['wp-domnic', 'nialler-ftbf']}]

# ---- 証言（すべて15語未満）
tst('ibia', 'トム・ローランズ', 'Tom Rowlands', 'The idea was for future primitive', '狙いは「フューチャー・プリミティブ」だった', '2002年のインタビューで、この曲の狙いについて', 'On the idea behind the track, in a 2002 interview', 'diffuser-cwu')
tst('sg', 'エド・シモンズ', 'Ed Simons', 'Star Guitar and Pioneer Skies happened when we got bored with the machines', '「Star Guitar」と「Pioneer Skies」は、機械に飽きたときに生まれた', '『Come with Us』の制作について', 'On making Come with Us', 'diffuser-cwu')
tst('tfv', 'トム・ローランズ', 'Tom Rowlands', 'I have loved cycling since I was a boy', '子どものころから自転車が好きだった', 'オリンピックのテーマを書いたことについて', 'On writing the Olympic theme', 'fact-2012')
tst('bite', 'ケミカル・ブラザーズ', 'The Chemical Brothers', 'there was another good Chemical Brothers album in us', 'まだ、いいケミカル・ブラザーズのアルバムが一枚、自分たちの中にあった', 'Rolling Stoneに、5年ぶりのアルバムについて', 'To Rolling Stone, on their first album in five years', 'rs-bite')
tst('ng', 'トム・ローランズ', 'Tom Rowlands', "I set up a corner of my studio that was 'The 1997 Corner'", 'スタジオの一角に「1997年コーナー」を作った', 'Apple Musicに、制作の始まりについて', 'To Apple Music, on how the record began', 'apple-ng')
tst('dtyf', 'トム・ローランズ', 'Tom Rowlands', "'The Darkness That You Fear' is a hopeful piece of music", '「The Darkness That You Fear」は希望のある音楽だ', '発売時のコメント', 'On release', 'umc-dtyf')
tst('sls', 'ベック', 'Beck', "It's like they have one foot in multiple decades at the same time", '彼らは、いくつもの時代に同時に片足ずつ置いているようだ', 'レーベルの発表資料に寄せたコメント', 'Quoted in the label\'s announcement', 'umc-sls')

# ---- 出来事
for e in events:
    if e['date'] == '2020-07' and e['kind'] == 'scene':
        e['ja'] = 'ロンドンのデザイン・ミュージアムで展覧会『Electronic: From Kraftwerk to The Chemical Brothers』。二人とスミス＆ライアルが閉幕の展示を手がけ、同館で最も多くの来場者を集めた展覧会になった'
        e['en'] = 'The Design Museum in London stages Electronic: From Kraftwerk to The Chemical Brothers. The duo and Smith & Lyall made its closing installation; it became the museum\'s most popular exhibition'
        e['src'] = ['guard-2020', 'umc-dtyf']
events += [
 {'date': '1999-06-07', 'kind': 'japan', 'work': 'sur', 'ja': '『Surrender』が日本で先行発売される。UKより2週間早い', 'en': 'Surrender is released in Japan, two weeks ahead of the UK', 'src': ['wp-surrender']},
 {'date': '2005', 'kind': 'tech', 'work': 'ptb', 'ja': '『Push the Button』の一部の地域向けCDに、コピー・プロテクションが付く', 'en': 'Push the Button is issued on copy-protected CD in some regions', 'src': ['es-ptb']},
 {'date': '2014', 'kind': 'scene', 'ja': 'アイヴァー・ノヴェロ賞の優秀楽曲群部門を受賞', 'en': 'The duo receive the Ivor Novello Award for Outstanding Song Collection', 'src': ['umc-bite']},
 {'date': '2019-11-22', 'kind': 'work', 'work': 'sur', 'ja': '『Surrender』20周年盤。カタログで初めてのデラックス盤', 'en': 'Surrender 20th-anniversary edition, the first deluxe edition in their catalogue', 'src': ['sde-surrender']},
 {'date': '2021-04', 'kind': 'tech', 'work': 'dtyf', 'ja': '新曲「The Darkness That You Fear」が、Appleの春の新製品発表イベントで初めて流れる', 'en': 'The new single "The Darkness That You Fear" premieres at Apple\'s spring product event', 'src': ['bv-dtyf']},
 {'date': '2023-10-26', 'kind': 'work', 'ja': '30年を振り返る本『Paused in Cosmic Reflection』。ノエル・ギャラガー、オーロラ、ベックらが新たなインタビューに応じた', 'en': 'The retrospective book Paused in Cosmic Reflection, with new interviews including Noel Gallagher, Aurora and Beck', 'src': ['umc-ftbf'], 'people': ['noel-gallagher', 'aurora', 'beck']},
]
S('sources.json', sources); S('works.json', works); S('people.json', people); S('events.json', events)
print(len(sources), 'sources', len(people), 'people', len(events), 'events')
