# LESSONS — clip machine self-improvement log

Every run that makes or reviews reels MUST read this file first and follow the RULES.
Framework: `skills/creator-audit-master/SKILL.md`. Rule of this log: a mistake is allowed, a weak fix is not —
every repeat of a mistake must get a STRONGER fix than the last one (code/check that makes it impossible > rule > note).

## RULES (current — apply to every new reel)
1. **Hook headline on frame 0.** `render2.py --top` is the hook, shown big from frame 0 (v3 layout). ≤ 8 words,
   curiosity/stakes, not a topic label. Mark 1 key word with [brackets] → yellow.
   Bad: "How heavy is a BOXABL home?", "BOXABL is more than tiny homes". Good: "They dropped a [CAR] on this house",
   "Elon Musk [sleeps] in this $50K box", "This house [unfolds] in 1 hour".
2. **Frame 0 = the most interesting visual** (celebrity face, the home unfolding, the action). Never a random host,
   a static exterior, or a slow lead-in. Start the cut on the payoff, explain after.
3. **Prefer celebrity / spectacle moments** (Elon, Post Malone, Airrack, FaZe Rug, car drop). Data below: celeb hooks
   avg ~147 views vs ~86 for business/abstract topics (Hypothesis, n=12, keep testing).
4. **Caption:** first line ≤ 125 chars and = the hook (it's all that shows before "more"); details on line 2;
   end with a SPECIFIC low-friction question, different from the last 6 captions (not "Would you live in one?" again).
   e.g. "$50K for this — worth it or no?", "Elon's guest house or your apartment?". 3-5 niche hashtags + campaign tags.
5. **Gate:** run `python3 tools/precheck.py clips/<file>.mp4 --caption "<caption>" --hook "<--top text>"` on every render
   (it now FAILS bad hooks: > 8 words, no [keyword], question/"How/What/Why" openers, "X on Y" / "is more than" labels). Any FAIL → fix
   and re-render before it goes into queue.json. Then look at frames 0s / 1s / 3s / last yourself.
6. Change ONE big variable per batch and log it below with the baseline, so we learn what works.
7. **Animation layer (Just See "Editer" connector, `mcp__Editer__*`) — HYBRID only.** Zohaib connected it 2026-11-25.
   Its own layout repeats our old mistakes (small letterboxed video + black bands, small hook card near IG header,
   -22 LUFS), so never use it as the base. Recipe that works (tested, precheck PASS):
   a. Make the speech part with render2.py v3 (big hook, burned captions). Make b-roll shots 9:16 with the same
      blurred-bg look (ffmpeg: split → bg scale 1080x1920 crop boxblur=28:2 eq=brightness=-0.36 ; fg scale/crop
      1080x1350 overlay at y=470 ; add silent audio). All sources 1080p H.264 `-g 15` (4K sources render BLACK).
   b. Host them on branch `media-tmp` of this repo (orphan branch, raw URL
      https://raw.githubusercontent.com/MDZohaibParwez/Reels/media-tmp/<file>) → `add_media`.
   c. Build: add_clip per shot (transitions: whip-left / zoom-blur-in / light-leak work), `label-pop` on b-roll
      (sits in the hook band) with ONLY facts visible in that shot, `end-card` (@mictalkclips + the caption question),
      sfx whoosh-fast/swish on cuts, music mood cinematic volume 0.3 duck. NO Just See captions (ours are burned in;
      its auto captions need WebGPU and take 7+ min).
   d. **One Editer write at a time, 20 s apart, then `get_video` and verify every step is there.** Parallel or fast
      writes silently overwrite each other; `remove_step` says "Removed" but doesn't persist → if a step is wrong,
      start a new project.
   e. Render: `render_video` → `node tools/justsee_render.js "<render link>" out.mp4` (local Chromium + software
      WebGPU; grabs the finished MP4 in-page; its upload to vercel.com fails through our proxy — expected, ignore).
      ~3 min per 18 s reel. Then `python3 tools/loudfix.py out.mp4 final.mp4` (it exports ~-22 LUFS) → precheck.
   f. Check label timing on frames: transitions overlap 0.5 s, so put a label ≥0.4 s after its shot starts and
      verify the label frame shows that thing. `delete_video` the project afterwards.

8. **Footage = the FULL BOXABL Drive library, not the 14 short clips.** Library folder `14hsa8iKW0kFY9yAZBTsTUvxr_lgoGelk`
   (hidden behind the "GOOGLE DRIVE" link in the footage doc; list it with `python3 tools/drive_ls.py <id>`, gdown one
   file at a time). Best so far: FaZe Rug full tour `1B5ongVEt8FqerK0hfQw2VVhyb5S_E-xc` (fold race 640-783s, interior
   360-410s, house-per-minute 106-126s used; giveaway idea 455-475s, scooter ride 482-600s, Las Vegas speedway 782-840s
   still free), Elon Casita delivery b-roll `1-I1DxHAe6LNSMH-joldN6uHl4k8-Ie4j` (36s, no speech - perfect cutaways),
   Airrack full `18BL24uFGteI0gef07zToTupnbdSJtJEg` (only 0-108s is in the BOXABL), "I Built a HOME in 48 Minutes"
   `1n00gNsWGgFvdKcWIZ0fmn0cT3c5drFeA`, KVUE news `1bdrteAX8d77iMco3Kf87J52cmPfFH9bT`. The 14 short clips in folder
   1XrfBd… are fully used.
9. **Always pass the reel id to assemble.py** (`assemble.py plan.json out.mp4 <reel_id>`): it prints OVERLAP if a piece
   re-uses a logged moment (footage_used.json) and records the new one. OVERLAP = pick another moment.
10. **Never work around YouTube's bot block** (third-party downloaders through the remote browser were refused by the
    safety check 2026-11-25). YouTube-only campaigns need Zohaib to drop files in Drive.

## METRICS (Content Rewards views, read 2026-11-25 01:25 IST; all 15 submissions "Pending", 0 approved, 0 rejected)
Baseline pre-v3 (12 mature Boxabl reels, 21-24 Nov): median **130**, avg 117, range 46-160. Account: 1 follower, empty bio.
Current rules (v3 layout + hook gate): **0 reels posted yet** (first batch = 2026-11-25) → no verdict.
| reel | views | type | slot (IST) |
|---|---|---|---|
| elon_guesthouse | 160 | celeb | 02:48 |
| elon_assembly_line | 156 | celeb | 18:00 |
| postmalone_kitchen | 153 | celeb | 09:00 |
| elon_all_three | 144 | celeb | 13:00 |
| elon_nda | 136 | celeb | 13:00 |
| airrack_night | 130 | celeb | 18:00 |
| foam_walls | 130 | product | 18:00 |
| hours_not_months | 119 | product | 13:00 |
| car_drop | 118 | spectacle | 09:00 |
| weight_trailer | 56 | product | 09:00 |
| phase2_future | 52 | business | 21:00 |
| caruso_30000 | 46 | business | 21:00 |
| fifty_k_home | 9 (only 4.5h old) | celeb | 21:00 |
By slot (Measured, mature reels): 18:00 avg 139 (n=3) · 13:00 avg 133 (n=3) · 09:00 avg 109 (n=3) · **21:00 avg 49 (n=2)**.
Hypothesis (Low confidence): the 21:00 slot is weak — BUT both 21:00 reels were also business topics (confounded). fifty_k_home
(celeb, 21:00) is the de-confounding test: if it stays < 60 at 48h, the slot is suspect; if it reaches ~130, topic was the cause.
Every reel stalls at ~50-160 = Instagram's first test batch; nothing broke out. $0.50/1K + $1 min payout → need ~2,000 views per clip to earn anything.

## MISTAKE LOG
### 2026-11-24 — full audit with creator-audit-master (score of a typical pre-v3 reel: 45/100 — hook 6/20, retention 10/20, edit 12/20, story 9/15, caption 5/10, profile 3/15)
- **M1 Critical — no hook on frame 0.** Observed: the `--top` headline was 44px thin italic, faded in over 300ms
  (frame 0 = invisible), and sat at y=215 = under Instagram's Reels header. Viewer's first frame = a talking head
  with zero reason to stay. → **FIX (code): render2.py v3** — 104px ExtraBold white + yellow keyword, outline +
  shadow, pops in from frame 0, 2 lines max, at y≈335 (safe zone). `--hook-style classic` keeps the old look.
- **M2 Critical — 44% of the screen was dead black** (16:9 sources at --vh 1080: black 0-330 and 1410-1920).
  → **FIX (code):** blurred, dimmed copy of the footage fills the whole 9:16 frame behind the video.
- **M3 High — informational hooks** ("How heavy is…", "Rick Caruso on…", "This is the future…") = lowest views.
  → **FIX (rule 1-3)** + precheck reminds; batch reviewer must reject topic-label hooks.
- **M4 Medium — caption hook buried:** first paragraph 150-200 chars, same CTA "Would you live in one?" on 4+ reels,
  0 comments on all 13. → **FIX (code + rule 4):** precheck fails captions with first line > 125 chars or a question
  reused in the last 6 captions.
- **M5 Medium — profile doesn't convert:** 1 follower, no bio, no name keyword. Can't be changed via API →
  Zohaib must paste bio manually (sent to him).
- **Next experiment:** v3 layout + hook rules from the 2026-11-25 batch. Success = median views of the next 8 reels
  > 200 (baseline 130) and at least one reel > 500. If not, next lever: hook wording A/B (same moment, 2 hooks).
- Not available: IG insights (connection lacks instagram_manage_insights) → no retention/watch-time data. Content
  Rewards view counts are the only metric.

### 2026-11-25 — daily self-review (01:25 IST). Audited best 48h = elon_all_three (144), worst mature = caruso_30000 (46), lowest = fifty_k_home (9, 4.5h old). Scores: 48 / 38 / 46 (all pre-v3).
- Observed (frames): best = face on frame 0 (host in hard hat) → Elon's face by 3s; worst = static exterior on frame 0, no face, no
  readable hook, 1s subtitle low-contrast on grass. fifty_k = FaZe Rug face on frame 0 but CTA "Would you live in a BOXABL?" again.
  All three: hook headline tiny + 44% black screen → already fixed by v3 (M1/M2), not yet live.
- **M6 High (repeat of M3, so stronger fix) — hook gate was only a written rule.** LESSONS said "precheck reminds" about bad hooks,
  but precheck.py had NO hook check at all. → **FIX (code):** precheck.py now FAILS a hook that is > 8 words, has no single
  [keyword], starts with How/What/Why/Is… or contains "?", or is a topic label ("Rick Caruso on…", "…is more than…", "This is…").
  Reads the hook from `--hook` or queue.json "hook"; missing hook = FAIL. Tested: all 4 old bad hooks FAIL, the 3 good examples PASS.
- **M7 Medium — question-reuse check was leaky.** It allowed `used <= 1` and counted the reel's own caption, so a question already
  used once before still PASSED (fifty_k_home "Would you live in one?"). → **FIX (code):** own queue entry excluded, must be 0.
- **M8 High (latent, caught before it happened) — v3 renders would fail the 30 MB gate.** Old reels already sat at the 10 Mbps
  cap (26-29 MB at 21-23s); v3 adds a full blurred background + grain, so any reel > ~24s would be > 30 MB → precheck FAIL /
  re-render loop in the 02:45 batch. → **FIX (code):** render2.py budgets bitrate from length (≤ ~27 MB). Test: 34.9s v3 render
  = 26.5 MB PASS, 16.9s = 21.2 MB PASS; frames checked (hook visible frame 0, captions, end text OK).
- Process: all 13 approved reels posted on slot and submitted within ~6 min. No render failures logged. No rejections.
- **How we'll know:** next batch's queue entries all carry "hook" + precheck PASS; v3 experiment verdict when 8 v3 reels have
  ≥ 48h of views (target median > 200 vs 130). Slot hypothesis: read fifty_k_home at 48h (see METRICS).

### 2026-11-25 — first test of the Just See animation editor
- **M9 High — Just See default layout = our old M1/M2 mistakes back** (Observed: 16:9 b-roll at ~35% of screen,
  black bands, small hook card at y≈120-190 under the IG header, -22 LUFS). → **FIX (rule 7):** hybrid only — v3 base
  + Just See animations on top; loudfix.py after render. Hybrid test: precheck PASS, rough score ~68/100 vs 45 before.
- **M10 High — my own process mistake: parallel Editer calls overwrote each other** (4 clips → 1). Then even 8 s gaps
  lost steps. → **FIX (rule 7d):** strictly sequential, 20 s gaps, verify with get_video; new project instead of remove.
- **M11 Medium — 4K sources rendered as black frames** in headless Chromium. → **FIX:** transcode to 1080p H.264 -g 15.
- **M12 Medium — label "Bunk beds + closet" landed on a different shot** (transition overlap). → **FIX (rule 7f).**
- **M13 Medium — my precheck had 2 bugs:** "ends with a question" only read the first paragraph; "frame 0 dark" flagged
  normal dark footage (YAVG 33). → **FIX (code):** question searched in the whole caption minus tag lines; black
  threshold YAVG > 22. Loudness added as tools/loudfix.py (two-pass) because one-pass loudnorm landed at -16.2.
- **Next experiment (after the v3 batch):** same moments, half the batch with the animation layer, half plain v3 →
  compare median views. Keep the animation layer only if it wins.

### 2026-11-25 — daily batch run (5 BOXABL reels, scores 70-75, all precheck PASS; joined Jason Wojo campaign)
- **M14 High — footage ran dry and nothing told me.** All 14 short Drive clips had already been cut (checked by
  transcribing every old reel = 6 min wasted), and no log said which moments were used. → **FIX (code):** assemble.py
  now logs every reel's source ranges in `footage_used.json` and prints OVERLAP on re-use (old reels back-filled,
  approx). **FIX (rule 8):** the real library is the linked Drive folder (60+ full videos) — listed with new
  `tools/drive_ls.py` (gdown --folder timed out on it).
- **M15 Medium — plan_words.py lost the last word of most pieces and doubled words at back-to-back cuts**
  ("minute?", "true?", "it." missing; "the the", "in in"); every reel needed 5-8 hand fixes. → **FIX (code):** a word
  belongs to the piece where it STARTS (+0.12s tolerance), same source word is never captioned twice, "U" ".S." joins
  to "U.S.", and it prints `CHECK piece N` when a piece's last word ends > 0.35s before the cut. Tested on two
  plans: all end words present, no duplicates.
- **M16 Medium — lip-sync/frame-0 trade-off.** Two reels needed re-cuts because frame 0 was the wrong face (Galiano
  instead of FaZe) or a busy mirror shot. Fix used: start the piece's VIDEO 0.3-0.4s later than its audio (`vs`) when
  the face appears just after the cut, or reorder so a piece that opens on the celebrity's face goes first.
  Always sample frames at 0/1/3s BEFORE writing captions (cheap) — done for all 5.
- **M17 Low — blocked step:** tried a YouTube→MP4 site in the remote browser for Jason Wojo footage; refused as
  bypassing YouTube's bot block. → rule 10. Asked Zohaib for Drive copies + bio link instead.
- Scores honestly capped by the profile (6/15: 1 follower, empty bio) — every reel loses ~9 pts there until the bio is fixed.
- **Test this batch:** first v3 reels with FaZe/Elon/Airrack spectacle + number hooks ("23 minutes", "every minute").
  Read views at 48h vs baseline median 130.
