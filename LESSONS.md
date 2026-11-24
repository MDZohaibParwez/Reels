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
5. **Gate:** run `python3 tools/precheck.py clips/<file>.mp4 --caption "<caption>"` on every render. Any FAIL → fix
   and re-render before it goes into queue.json. Then look at frames 0s / 1s / 3s / last yourself.
6. Change ONE big variable per batch and log it below with the baseline, so we learn what works.

## METRICS (Content Rewards views, read 2026-11-24 ~23:10 IST; all 15 submissions "Pending", 0 approved)
Baseline pre-v3 (12 Boxabl reels, 21-24 Nov): median **130**, avg 116, range 46-160. Account: 1 follower, empty bio.
| reel | views | type |
|---|---|---|
| elon_guesthouse | 160 | celeb |
| elon_assembly_line | 156 | celeb |
| postmalone_kitchen | 153 | celeb |
| elon_all_three | 144 | celeb |
| elon_nda | 136 | celeb |
| airrack_night | 130 | celeb |
| foam_walls | 130 | product |
| hours_not_months | 119 | product |
| car_drop | 118 | spectacle |
| weight_trailer | 53 | product |
| phase2_future | 52 | business |
| caruso_30000 | 46 | business |
| fifty_k_home | (new) | celeb |
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
