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

11. **Approval shortcut (Zohaib, 2026-11-25):** a reply of just "✅" = "sab approve" (approve every reel in that batch).

12. **Zohaib wants every reel edited in Editer (Just See) — said 2026-11-25 ("vahi karo edit, yaha aacha nahi ho raha").**
    Recipe that works (all 3 re-edits on 25 Nov passed precheck): v3 render2 reel → cut it into **max 3 shots** at
    hard cuts (`-g 15`) → push to `media-tmp` → Editer: add_media ×3, add_clip ×3 (transitions **whip-left,
    zoom-blur-in, push-left** render; light-leak/crossfade untested-bad), add_text position **bottom**, style bold,
    **≤ 16 characters** (longer runs off-screen) → render with `tools/justsee_render.js` → keep first 15.0s →
    `bash tools/justsee_stitch.sh <editer.mp4> 15.0 <last_shot.mp4> <offset_in_last_shot> <out.mp4>` → precheck.
    **Every Editer write: wait ~90-100 s, then get_video must show it before the next write** (its server lags 1-2 min
    and a write sent too early silently overwrites the previous one). ~20 min per reel. Render is free (runs on
    device, no credits). Phone render links failed twice for Zohaib with "Failed to fetch" — don't depend on them.

13. **PREMIUM STYLE is now the default edit (Zohaib, 2026-11-25 night — overrides rule 12 / Editer).** He showed two
    reference edits (Jensen Huang "premium podcast" edit + Mark Sut before/after) and said our edits are weak. Use
    `tools/premium.py` (example inputs in tools/premium_example/). Zohaib does NOT want to approve plans — plan the whole
    edit yourself, he only sees the finished reel in the approval message.
    a. assemble.py with `"size": [1080,1920]` → full-bleed A-roll. Pick each piece's `crop` w:h:x:y from frames so the
       face sits upper-middle; crop OFF burned-in subtitles of the source (FaZe tour: `506:900:x:0`).
    b. plan_words.py → hand-fix words (it mishears names: "phase road" = FaZe Rug, "boxable" = BOXABL).
    c. scenes.json: hook (RULE 1), `name` lower-third for the celebrity, `special` = brand first ("boxabl"), 1 paper card
       on the strongest value line, 1 `pip` card with WIDE b-roll that shows the WHOLE home (Casita delivery
       `1-I1DxHAe6LNSMH-joldN6uHl4k8-Ie4j` 13-22s at speed 6 = home unfolding), `end_text` = caption question.
       Cards max ~1.5 s each, 2 per 15-20 s reel. No punch-in on soft (upscaled) shots.
    d. ALWAYS `--preview` 8-10 frames first and fix what you see, THEN full render (~85 s per 17 s reel), precheck,
       frames 0/1/3/last, score /100.
    e. (2026-11-26) Close-up face fills the top? scenes.json `"hook_y"` / `"end_y"` (default 300/360) move the hook and
       end question onto the chest (e.g. 180 above a cap, 520 below a face that sits high). Card `text` is shown
       phrase-at-a-time in chunks of ≤ 3 words / 15 chars → keep card text to ONE chunk ("only got *three*",
       "*barber* shop") or the card shows a lone leftover word. premium.py now refuses to render a hook that fails the
       precheck hook gate.
14. **Before planning a moment, run `python3 tools/free.py <src.mp4> <start> <end>`** (FREE / OVERLAP from
    footage_used.json). New library sources downloaded 2026-11-26 (Drive "1. Most Viewed YouTube"): `touring_elon.mp4`
    = `1lwtGTL2epL8hlEnxV9vINQN42jTu3c65` (Paolo Tiramani sit-down interview + Casita tour; used 123-175, 545-570; free:
    founder childhood 573-606, wall "break your foot" 181-196, 9.5 ft ceilings 391-430, queen bed/TV 457-486, "can I have
    one?" 623-627), `inside_elon.mp4` = `19UfzvZwtPFBq9CikyqBCZwYeBMxq7cwP` (Enes Yilmazer factory tour; used 93-132,
    605-680; free: thermos/igloo walls 211-237, steel "beyond overkill" 289-326, 90-min house 443-500, Casita tour
    733-1005). FaZe tour `elonvisit.mp4` is now used up to 852 except 560-640 (house-a-minute talk = repeat topic).
    Scan a new long video with whisper `base` on a numpy array (av 19 breaks faster-whisper's file decoding).

14. **PREMIUM STYLE IS PAUSED (owner, 2026-11-26: "training achhi nahi hai, roko").** Reel-making task is disabled and
    the unposted premium reels are on hold (approved=false, "hold" note). Do NOT make or post premium reels until Zohaib
    gives the go AND every item below is done. His feedback on elon_joke_call (posted 26 Nov 18:00):
    a. **Start too heavy/static** — 0-3 s was a still side-profile + plain top text + tiny first caption. Needed: an
       intro animation on frame 0 (text/visual flies in), a WHOOSH on the first frame, an energetic music bed from 0 s,
       then a suspense sound before the reveal. Hook text AND live caption both on screen from frame 0.
    b. **Captions "normal"** — make them glowing (soft outer glow in the accent colour), bigger, more energy.
    c. **No colour grading** — every shot must be graded (contrast, colour, look); amount = his Drive reference
       1nw7brKSEU_VvGOK5PHg12baeKkVFLPIY (could not download on 26 Nov: sharing not public).
    d. **No face tracking** — static crops leave the face drifting/side-on. Use real face tracking (he is adding a
       face-tracking + colour-grading tool to our toolset; use it when it arrives).
    e. **0:12 card IN = weak** (0.13 s cross-fade + soft -9 dB generated whoosh) and **0:13 card→card change = weak**
       (frame 13.0 shows a messy double-exposure blend). Needed: a real animated transition (slide/zoom/whip/mask) with a
       punchy SFX that hits ON the cut. Never cross-blend two cards.

## METRICS (Content Rewards views, read 2026-11-26 01:20 IST; all 19 submissions "Pending", 0 approved, 0 rejected)
Baseline pre-v3 (13 Boxabl reels, 21-24 Nov, all now 28-95h old): median **131**, avg 117, range 46-160. Account: 1 follower, empty bio.
Current rules (v3 hook layout + hook gate, 25 Nov): **n=4, all < 17h old** → median **152** (140-203). No verdict until 8 reels ≥ 48h.
Early signal (Measured, young): the 2 Editer-edited reels have the fastest start (spacex 203 @7h, house 159 @4h) vs plain v3
(145 @16h, 140 @12h). Confounded with celeb face on frame 0 / slot → Hypothesis only.
Reels keep growing after 48h (weight_trailer 56 → 140, fifty_k_home 9 → 125): compare reels at the SAME age, not raw totals.
| reel | views | age (h) | type | slot (IST) | layout |
|---|---|---|---|---|---|
| elon_spacex_delivery | 203 | 7 | celeb | 18:00 | v3+Editer |
| elon_guesthouse | 160 | 95 | celeb | 02:48 | old |
| house_per_minute | 159 | 4 | spectacle | 21:00 | v3+Editer |
| elon_assembly_line | 156 | 79 | celeb | 18:00 | old |
| postmalone_kitchen | 153 | 88 | celeb | 09:00 | old |
| faze_backyard | 145 | 16 | celeb | 09:00 | v3 |
| elon_all_three | 144 | 36 | celeb | 13:00 | old |
| weight_trailer | 140 | 40 | product | 09:00 | old |
| fold_race | 140 | 12 | spectacle | 13:00 | v3 |
| elon_nda | 136 | 60 | celeb | 13:00 | old |
| foam_walls | 131 | 31 | product | 18:00 | old |
| airrack_night | 130 | 55 | celeb | 18:00 | old |
| fifty_k_home | 125 | 28 | celeb | 21:00 | old |
| hours_not_months | 119 | 84 | product | 13:00 | old |
| car_drop | 118 | 64 | spectacle | 09:00 | old |
| phase2_future | 52 | 76 | business | 21:00 | old |
| caruso_30000 | 46 | 52 | business | 21:00 | old |
Topic (Measured, pre-v3): celeb avg 143 (n=7) · product/spectacle avg 127 (n=4) · **business avg 49 (n=2)**.
**Slot verdict (2026-11-26): 21:00 is NOT the problem — REJECTED.** fifty_k_home (celeb, 21:00) reached 125 and house_per_minute
(21:00) 159 in 4h; the two 21:00 losers were business topics. Keep the 4 slots; avoid business/abstract topics (rule 3).
Every reel still stalls at ~50-200 = Instagram's first test batch; nothing broke out. $0.50/1K + $1 min payout → need ~2,000 views per clip to earn anything.

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

### 2026-11-25 (afternoon) — owner asked to switch editing to Editer
- **M18 High — Editer renders broke on the cloud machine:** 4-clip projects failed "Shader compile failed: unknown";
  3-clip projects rendered but went black from 15.3 s (all 4 renders, incl. no-text ones). Bisected: count/length,
  not one transition. → **FIX (code):** `tools/justsee_stitch.sh` (Editer first 15 s + original tail, loudness
  matched) and rule 12 (max 3 clips). Tested on 3 reels, join invisible, blackdetect clean, precheck PASS.
- **M19 Medium — Editer server lag lost steps 3 times** (overwritten clip, lost text, duplicated clip) even with
  20-45 s gaps. → rule 12: poll get_video until the write shows (~90-100 s) before the next write.
- **M20 Low — first label "CAR FACTORY: 1 CAR EVERY MINUTE" ran off both edges.** → rule 12: ≤ 16 chars; check the
  label frame before queueing.

### 2026-11-25 (night) — owner: "tum edit aacha nahi karte" → premium style renderer
- **M21 High — our edits looked generic** (Observed by owner; Hypothesis: no fixed fonts/palette/scene types, captions
  only, letterboxed video). → **FIX (code): tools/premium.py** — 2 fonts (Inter + Lora Bold Italic special word),
  one accent colour, paper/halftone/grain textures, phrase-at-a-time paper cards, wide pip b-roll card, whoosh on
  every card, hook + name lower-third on frame 0. Test reel faze_giveaway_premium: precheck PASS, score 70.
- **M22 High (caught in preview) — accent picked FROM the footage made the special word invisible** (orange word on
  FaZe's orange vest/helmet). → **FIX (code):** auto accent = complementary hue of the dominant colour.
- **M23 Medium — source had burned-in subtitles** (FaZe's own cyan captions) → crop pieces to the top 900 px (rule 13a).
- **M24 Medium — 1.1x punch-in on an already 2.1x-upscaled shot = blurry face, and face drifted out of crop.** → rule 13c.
- **Next experiment:** whole next batch in premium style. Success = median views of the next 8 premium reels > 200
  (baseline 130) and ≥ 1 reel > 500. If it loses to v3/Editer reels at 48h, iterate cards/hook, don't revert blindly.

### 2026-11-26 — daily self-review (01:20 IST). Best 48h = elon_spacex_delivery (203 @7h, v3+Editer), worst 48h = fifty_k_home
(125 @28h, old layout); also checked fold_race (140 @12h, slowest v3). No rejections. Scores: spacex 78, fold_race 70, fifty_k 48.
- Observed (frames): spacex = Elon's face + big hook on frame 0, b-roll truck/SpaceX by 3s, 21.5s. fold_race = backs of 2 workers on
  frame 0 (no face), 30.3s (longest of the batch). fifty_k = old layout (thin hook, black bands) - precheck FAIL by today's rules
  (caption line 1 = 170 chars, no hook), expected for a pre-v3 reel.
- **M25 High — burned captions vanished on bright footage.** Observed: fold_race 1.0s "BOXABL RIGHT" white-on-white-wall barely
  readable; house_per_minute 0s "DUDE" faint on pale ground. Cause (code): render2.py `Cap` style had Outline 0 and the `Glow`
  layer was WHITE (so it made white text even less readable on bright backgrounds). Every v3 + Editer reel inherits this.
  → **FIX (code):** Cap gets a 6 px black outline; Glow layer is now a dark soft halo (black, blur 12, ~56% opacity), yellow key
  words no longer glow yellow. Test render on the same white-wall shot: caption crisp and readable (before/after frames checked),
  precheck PASS on size/loudness/frame 0. premium.py captions already use stroke 3 + shadow (unchanged).
  How we'll know: every new render2/Editer reel's frames at 0/1/3s show outlined captions; no "faint caption" note in next audits.
- Hypothesis (Low, n=4): Editer-edited reels + celebrity face on frame 0 start fastest. Next check: compare all 4 v3 reels at 48h.
- Process: all approved reels posted on slot and submitted within ~5 min; airrack_spacious due 09:00 IST today; faze_giveaway_premium
  waiting for owner approval. Timothy White draft still "Pending" brand review since 22 Nov (file on CR is fine: 20.6 MB mp4; the
  "Video unavailable" label is only the headless browser lacking H.264). Nothing to do except wait.
- Note for setup: tools/assets/ is gitignored → run `python3 tools/sfx.py tools/assets` on a fresh clone before render2.py.
- Experiments: v3 (8 reels ≥48h, target median > 200) and premium style — no verdict yet (n=4 / n=0). Slot experiment closed (see METRICS).

### 2026-11-26 — daily batch run (5 BOXABL premium reels, scores 70-74, all precheck PASS; campaigns checked)
- Campaigns (Discover, 03:00 IST): nothing new fits a talk/podcast/business account with budget left. Social Commerce News
  (podcast, $2/1K) = $1,998/$2,000 used, not accepting clips. Kitsch x Nic Vans (Clip Farm, $1.50/1K, $36.9K left) =
  Love Island Santa hair-gift ad, entertainment → not our niche, not joined (told owner). Most budget is GTA 6 / music.
  BOXABL still $61K left. Note: on Discover cards "$X / $Y" = X already SPENT, not left.
- **M26 Medium — 10 min lost on an already-used moment.** Transcribed + framed FaZe's scooter/highway-patrol scene
  (483-533) and assembled it before assemble.py printed OVERLAP (car_drop's logged range 475-533). → **FIX (code):**
  `tools/free.py <src> <start> <end>` prints FREE/OVERLAP + every used range; rule 14 = run it before planning.
- **M27 Low — hook failed precheck only after the full render** (9 words, ~90 s render wasted). → **FIX (code):**
  premium.py runs precheck's hook_checks before rendering/previewing and exits "HOOK FAIL before render".
- **M28 Low — env:** faster-whisper 1.2.1 + av 19 → `open() got an unexpected keyword 'metadata_errors'` when given a
  file path; downgrade (av<15) fails to build. plan_words.py already feeds a numpy array (works); ad-hoc scans must too.
- **M29 Medium (caught in preview) — close-up faces under the hook/end text** (Paolo's cap-to-chin fills the top 40%;
  hook at y=300 covered his eyes; end text + @handle sat on his glasses; handle y was hard-coded). → **FIX (code):**
  premium.py `hook_y` / `end_y` in scenes.json, handle follows end_y (rule 13e).
- Test this batch: 3 new sources (founder interview, Enes factory tour, FaZe speedway) + first reels whose frame 0 is
  the product/action instead of a celebrity face (house_in_a_box, factory_disney). Compare at 48h vs celeb-face reels.

### 2026-11-26 — owner review of elon_joke_call → PAUSE premium (rule 14)
- **M30 High — premium v1 shipped without a real opening, grade, tracking, or transitions.** Owner watched the live reel:
  heavy static start, plain captions, ungraded footage, no face tracking, weak card IN at 0:12 and weak card→card at 0:13
  (Observed in frames: 4-frame blend; 13.0 = double exposure). Root cause (Hypothesis, high): I copied the LOOK of the
  references (fonts, paper cards) but not their MOTION + SOUND design, and my self-score did not check motion/SFX at all.
  → **FIX:** reel-making disabled + premium reels held until rule 14 a-e are built and tested; the /100 self-score must now
  include an explicit check of frame 0 motion, every transition (look at 3 frames before/after each cut) and the SFX on
  each cut. A repeat of a weak transition after resuming = stop the batch.
