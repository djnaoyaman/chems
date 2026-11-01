# myChems usability validation — 2026-11-01

Owner: sole delegated UI writer. Baseline remote main verified as `60471b4894a3d43616da23f8e5f2b8ad83cebe0f`; open PR list empty; fresh local checkout clean. No other checkout changed. Logo, icons, 57 works, 36 people, 225 track slots and 54 official bindings are protected.

Method: actual local Windows desktop Chromium with Playwright route fulfillment from built files; all external resources blocked. This is responsive emulation, not physical iPhone Safari. Baseline captures at 320/375/390/430/768/844-landscape/1280/1440. Local OGP build uses Windows Yu Gothic substitution for Linux Noto paths; CI retains its original Noto build. No YouTube network/playback tests. Unit player events and later browser transport are mocked and cannot establish real playback.

## Batch 1: discovery and reading

| Round | Target / hypothesis and operation | Observed baseline | Change | Retest / limits |
|---|---|---|---|---|
| 1 | Mobile navigation; inspect 320/375/390/430 and open all destinations | Horizontal nav clips destinations with no visible scroll cue | Explicit Menu disclosure, wrapped links, Escape returns focus; no-JS nav remains available | Bilingual browser open/Escape and focus passed; no physical touch device |
| 2 | Catalog legibility; measure text and inspect 320/1440 | Title/year 9.6px; symbols dominate | Title/year 13–14px, relaxed leading; larger metadata | Computed type size >=13px and real captures pass |
| 3 | EP discovery; filter to seven EPs | Empty album/single columns occupy most width | Filtered cards use available width with no empty eras | Seven visible EPs in both languages, eight widths |
| 4 | All releases; compare chronological and periodic views | Narrow three-column table fragments long English names | Default chronological grid plus explicit periodic-table view | Toggle list/table repeatedly retains 57 tiles and all 33 era stacks |
| 5 | Find a known title/year | No text search | Labeled Unicode-normalized title/year search combined with format | Full-width ＤＩＧ resolves Dig Your Own Hole; no overflow |
| 6 | Recover from no matches | No count or recovery path | Live result count, empty guidance and Reset returning focus | Empty query journey → reset restores all 57 |
| 7 | Detail → Back / reload | Existing filter preservation depended on browser state | URL stores query/format/view; restore on pageshow and popstate | Filtered detail → Back and reload preserve one-result context |
| 8 | Keyboard/mobile touch targets | Filters and language utility below 44px; year links densely packed | 44px controls and separated year links, anchor clearance | Navigation/filter actions pass; timeline-specific check scheduled in next batch |

First batch browser suite: 136 assertions across both languages and eight widths. Original pure listening suites: 42 passing. Protected source test initially exposed Windows checkout CRLF differences; restored Git blob line endings without changing any protected content. No research dates or official bindings changed.

Rounds 9–20 are recorded separately in draft PR #22, `notes/usability-player-rounds-20261101.md`. The batches are based independently on main; parent owns integration, merge and publication.

Aggregate follow-up: maintained the original 180px logo minimum after a mobile sizing regression; menu now opens in a deliberate row below logo/language. Preserved the wordmark shape/hash test. Added explicit release-format labels and moved periodic-table instructions into an optional disclosure so the default chronological view is described accurately. The 218-page rendered audit passed normal-width overflow and one-main-heading checks. At 200% text enlargement the timeline exposed narrow date/art/text columns; mobile dates now stack above each event and long titles wrap. The ten bilingual enlargement cases then passed. These are follow-up retests within rounds 1/4/8, not additional rounds.

Evidence: `test-artifacts/baseline/` contains pre-change 390/1440 works and EP screenshots. CI artifacts include `menu-{lang}-{width}.png`, `ep-filter-{lang}-{width}.png`, `usability-{lang}-{width}.png`, enlarged-reading screenshots and the existing regression captures. All external fonts/media are blocked in browser checks. The locally built OGP uses a Windows font substitute; Linux CI uses its original Noto fonts. No device-specific load-speed, real seek or audio-playback claim.
