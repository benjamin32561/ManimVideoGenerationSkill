# 3Blue1Brown — style study (phase 1)

Research date: 2026-11-21. Scope: how Grant Sanderson goes from idea to finished
video, and what the words, pictures and motion look like. Render engines are out
of scope here.

**How to read the tags.** `[verified: X]` means I (or, where marked †, the research
sub-agent) read it in source X, listed in §10. `[inferred: …]` is my reasoning from
the evidence named. `[measured: …]` is a number produced by my own scripts over the
sample (method in §10). Anything not found says so.

**Sample (8 videos, 2016–2026).** All on youtube.com/@3blue1brown.

| ID | Video | Date | Length |
|---|---|---|---|
| V1 | [Vectors, Ch. 1 Essence of linear algebra](https://www.youtube.com/watch?v=fNk_zzaMoSs) | 2016-08-06 | 9:51 |
| V2 | [But what is a neural network? (DL ch. 1)](https://www.youtube.com/watch?v=aircAruvnKk) | 2017-10-05 | 18:40 |
| V3 | [But what is the Fourier Transform?](https://www.youtube.com/watch?v=spUNpyF58BY) | 2018-01-26 | 19:41 |
| V4 | [Bayes theorem, the geometry of changing beliefs](https://www.youtube.com/watch?v=HZGCoVF3YvM) | 2019-12-22 | 15:11 |
| V5 | [But what is a convolution?](https://www.youtube.com/watch?v=KuXjwB4LzSA) | 2022-11-18 | 23:01 |
| V6 | [Transformers, the tech behind LLMs (DL ch. 5)](https://www.youtube.com/watch?v=wjZofJX0v4M) | 2024-04-01 | 27:14 |
| V7 | [Why you can't comb a hairy ball, and why we care](https://www.youtube.com/watch?v=BHdbsHFs2P0) | 2026-01-31 | 29:39 |
| V8 | [Reinventing Entropy / Shannon's dream (Information theory, part 1)](https://www.youtube.com/watch?v=l6DKRf-fAAM) | 2026-06-07 | 31:23 |

---

## 1. Snapshot

- **Who.** Grant Sanderson, writing, animating, narrating and editing alone for
  most of the channel's life: "the writing, animating, and editing of a typical
  3bluebrown video is a one-man shop" [verified: W12, Dec 2025]. In 2026 he began
  "to take on more of a team" [verified: W13]; the about page now lists animators,
  illustrators, an operations lead and the composer [verified: W1].
- **Topics.** Undergraduate-to-research math (linear algebra, calculus,
  probability, topology, complex analysis, number theory), CS/ML (neural networks,
  transformers, information theory, quantum computing) and physics (light,
  holograms) [verified: channel video list via yt-dlp]. Puzzles, SoME results and
  guest videos fill the gaps [verified: same list].
- **Audience.** Curious viewers from strong high-schoolers to working engineers;
  his own judge is "the version of myself … who doesn't yet understand the thing"
  [verified: W6†]. The SoME criteria ask for "empathy for people unfamiliar with
  the topic" [verified: W3†]. Series chapters flag the background they cover so
  experts can skip it: V6 at 6:42 says it will "spend a lot of time reviewing some
  important bits of background knowledge", adding that "If you're comfortable with
  that background knowledge and a little impatient, you could probably feel free to
  skip to the next chapter" [verified: V6 transcript].
- **Length.** Videos keep getting longer [measured: yt-dlp metadata for all 154
  long-form uploads; main videos exclude guest, Q&A and SoME videos]:

  | Era | Main videos | Median length | Middle half |
  |---|---|---|---|
  | 2015–17 | 57 | 13.7 min | 8.9–17.6 min |
  | 2018–20 | 38 | 15.8 min | 11.4–20.1 min |
  | 2021–23 | 21 | 23.0 min | 13.4–27.6 min |
  | 2024–26 | 25 | 29.6 min | 26.1–37.4 min |

  The 2026 median so far is 39 min.
- **Cadence.**
  - 154 long-form videos from 2015-03-05 to 2026-11-17; ~8.77 M subscribers on
    2026-11-21 [measured: same metadata].
  - Uploads peaked at 24–28 a year in 2016–17. Since 2021 it has been 7–13 a
    year, counting guest videos [measured].
  - Time per video:
    - "like three weeks" (2018) [verified: P4 09:06]
    - scripts take "one afternoon" to "3 months", and animating a 12-minute video
      "roughly one week" (2021) [verified: W10†]
- **Money.** Viewer-funded, no sponsorships or brand integrations [verified: W1].
  Patrons see an early release and can change the final cut [verified: W1; V6
  ends by saying the public version "depends on how much I end up changing based
  on that review"].

## 2. Production pipeline & tools

| Stage | What happens | Tools / people | Evidence |
|---|---|---|---|
| Idea | Topics come from "ambient learning", not project research; a topic waits on a list until he has the "aha" that "ties this whole story together". Prefers niche, fresh angles. | Pad scraps, a text file of topics with bullets; notes "about 50% sketches". | [verified: W7†, W6, W9†, W1 "Be niche"] |
| Research | First works through the *non*-intuitive standard explanation, then looks for the intuitive path. For a "distanced narrator" video you "should probably know 10 times as much" as you say. | Reading, papers, his own derivations. | [verified: W9†; P2 15:01] |
| Sample lessons | Teaches the topic live to friends / tutoring students to find what is confusing; ~12 sessions for quaternions. Mostly for expository videos, rarely for puzzle videos. | Whiteboard, "terrible drawings". | [verified: W8, W9†] |
| Script | Usually a full script before animating, built around the core visual and the aha. He notices his *first drafts* go abstract→concrete and flips them. Writing is "the worst" / "most painful" part. | Plain text, internet off. | [verified: W6, W8, P2 10:20, W7†] |
| Storyboard | No formal storyboard found. Sketches live in notes and sample lessons. | — | [verified: W8, W9†; not found: any storyboard] |
| Animation | Each shot is a Python `Scene` class in his own Manim (ManimGL), developed interactively: `manimgl file.py Scene -se <line>` drops into IPython at that line; `checkpoint_paste()` re-runs copied code from a saved state; `record=True` renders. Driven from Sublime Text via custom Terminus plugins and hotkeys. Script wording and even structure change while animating. | ManimGL (OpenGL), Sublime Text + Terminus, IPython, MathPix (screenshot→LaTeX), assets in Dropbox. For plain text moves he recommends Keynote/PowerPoint over Manim ("do as I say, not as I do"). | [verified: P1 02:45, 06:15, 43:50, 44:50; C1 README.md, custom_config.yml; W6; W14†; W7†; W2†] |
| Render | 4K (3840×2160) at 30 fps, black background, `saturation: 1.5` in the file writer, `CMU Serif` for `Text`. Scenes render as separate clips; `stage_scenes.py` orders a module's clips for the editor. Overlay-only scenes (e.g. a corner readout) can render with `--transparent`. | ManimGL file writer, ffmpeg. | [verified: C1 custom_config.yml, stage_scenes.py; C2 config.py]; overlay use [inferred: §8 item 8] |
| Timeline + VO | Lays the animations into an editing timeline, then records the voiceover, then cuts — "once I record the voiceover, the actual editing is like a day". Narration was on a Blue Yeti USB mic (2020). | Blue Yeti; editor below. | [verified: W5, W6, W7] |
| Edit | Grant edits himself; the "little cuts … are my way of even thinking" about the piece. Manim is "a tool for making individual clips to be edited together later" (2021 FAQ: for "spitting out the individual mathematical animations"). Early videos were cut in iMovie; by 2024 he drops renders "into Final Cut". | iMovie → Final Cut. | [verified: W5, W1, W2†, P2 07:17, P1 44:29] |
| Music | "Almost all" by Vincent Rubinetti; Grant wrote the piano pieces in the linear-algebra and calculus series. His advice: once you're in the technical meat, music should be "decidedly in the background". | Licensed score. | [verified: W1, P4 09:39, P3 12:26] |
| Review | Patreon early release; patrons' questions can change the public cut. | Patreon. | [verified: W1, V6 ending] |
| Who | Solo for writing, animation, editing, VO through 2025; contractors for music, hand-drawn illustration, SoME; co-authored videos (e.g. holograms with Paul Dancstep); 2026 team of animators/illustrators. | — | [verified: W12, W13, W1] |

Two further code-level facts:

- **Sync lives in the editor, not the code.** The scene code contains no
  narration hooks: the only `add_sound` calls are sound effects (clacks, Galton
  board) [verified: C1 grep]. 73–77% of `self.wait()` calls are 1 s, mostly the
  bare default [measured: code_stats.py over C1], so the timing to speech must be
  adjusted in the timeline [inferred: from the bare waits, W5's "timeline then VO
  then edit", and W1's "clips to be edited together later"].
- **Grant's repo now carries a `CLAUDE.md`** describing the workflow for Claude
  Code [verified: C1 CLAUDE.md]. How much he uses it is not documented [not found].

What is not found anywhere: number of script drafts, whether he re-records VO
lines, whether animation is retimed to VO or VO to animation (beyond the order
above), which tool makes the photoreal fur in V7 (it is not in the repo code
[verified: C1 grep]).

## 3. Script writing process & structure

**How drafts get made** (Grant's own account)

- The gate is an aha: "I want there to be some kind of aha moment … then
  hopefully the script can revolve around" it [verified: W6]. Without one he
  doesn't start [verified: W7†].
- Visuals lead: think "this is the core visual around which the narrative will
  revolve", and let "what I discover while creating the visuals change what the
  words will be" [verified: W8].
- Concrete before abstract, against his own instinct: "I find myself doing this in
  pretty much any first draft of a script" (going abstract-first) [verified: P2
  10:20]. Populate the learner's mind with examples so the definition "articulat[es]
  something … already sitting there" [verified: P2 10:50].
- Definitions must feel discovered: "Explain why that's the definition, what else
  it could have been" [verified: P2 16:47]. The 2026 entropy video is framed as
  leading the viewer "to (hopefully) rediscover the core idea" [verified: W16†].
- Motivation fast, then substance: he names "over-philosophiz[ing] in the
  video's introduction" as his own past mistake; "motivate using clear examples,
  not sweeping statements" [verified: P3 07:46–08:06].
- Micro-motivation: every new idea needs a reason to be there; a "naive but flawed
  solution" refined step by step is a good template [verified: P3 08:10, 09:44].
- Keep "one or two examples front and center" and let the on-screen example carry
  general points without talking about it [verified: P3 11:41–12:18].
- Don't go fire-hose: talking "faster than is comfortable" was a mistake in his
  first video [verified: P2 16:04–16:30].
- Invention as the goal: "it's easiest to remember a piece of math if you feel
  like you invented it yourself" [verified: W15†]. If an animation isn't visually
  compelling, he restructures the explanation, not the animation [verified: W11†,
  a paraphrase].

**SoME guidance — what he judges exposition by**
- Four criteria: motivation, clarity, novelty, memorability. "The first two are
  probably the most important" [verified: P3 02:54–03:01; W3†, W4†].
  - Motivation: "within the first 30 seconds" the viewer should know why to care
    (SoME1 rules) [verified: W3†].
  - Clarity: "Jargon should be explained" [verified: W3†]. Clarity "determines
    how quickly you burn through that focus" [verified: P3 11:00].
  - Novelty: mostly a fresh topic or perspective; a fresh *look* matters less.
    He wrote Manim partly as "a forcing function for originality" and asks
    creators to find their own aesthetic [verified: P3 12:58–13:53].
  - Memorability: a question "so fun to think about" or an aha that sticks
    [verified: P3 14:26].
- His advice list on the about page [verified: W1]:
  - "Just start"
  - "Concrete before abstract"
  - "Topic choice matters way more than production quality."
  - "Be niche"
  - "Know your genre"
  - "Never start with definitions"
  - "Be visual"
  - "Avoid pointless animations"
- Genre choice:
  - the "distanced" narrator "standing on top of a hill", who must know ~10× as
    much as they say
  - "discovery journalism", learning alongside the viewer
  - the worked example
  - the inspiring demo

  Copy only from creators in your own lane [verified: P2 14:51–16:01].
- Production quality is secondary to content, but sound matters: "get a good
  microphone and learn how to use it" [verified: W1; P2 18:14].

**Structural templates seen in the sample** [verified: transcripts; labels are mine]

| Template | Spine | Example |
|---|---|---|
| Phenomenon → challenge → build | Show an effortless everyday feat, then ask the viewer to program it; build the machine piece by piece. | V2 "This is a 3." |
| Preview the destination | Open on the final animation ("This right here is what we're going to build to"), then the central example, build the "machine", formalize, tease extensions. | V3 |
| Puzzle → expert result → representative sample → formula → return | Steve the librarian/farmer, Kahneman & Tversky, 210 people, the formula assembled from the counts, a second example (Linda), back to Steve. | V4 |
| Familiar op → new op → many views | Add/multiply lists, then "another kind of combination", dice, sliding windows, then a fast algorithm. Ends on an exercise. | V5 |
| Acronym unpack → roadmap → walkthrough | "The initials GPT stand for…", follow the data step by step, prerequisites, next chapter. | V6 |
| Personal hook → playful statement → why care → proof | Baby's hair swirl → theorem → game-dev plane orientation, wind, radio → proof by contradiction via a physical fluid model → higher dimensions. | V7 |
| Practical question → numbers → history → reinvent | "Is there some kind of fundamental limit on how efficiently text can be compressed?" → ASCII 8 bits → Shannon 1940s → a toy robot world. | V8 |

**Hooks** [verified: transcripts, frames]
- Concrete in the first sentence in 7/8: a digit, a baby's head, two lists, a
  compression number, a formula's real-world uses. Only V1 opens with a topic
  statement.
- The hook is short: the central question or challenge lands within the first
  0:05–1:30 (V8 0:04, V5 0:30, V2 0:49, V7 1:00, V4 1:27).
- Cold opens replaced the logo-first open. V1–V3 start on the animated logo at
  0:00. From 2019 on, every sampled video runs a 1–3 minute cold open: hook,
  stakes, often the central puzzle. The logo then marks the end of the hook:
  V4 1:10, V5 1:55, V7 1:40, V8 2:20, V6 3:00 [measured: template correlation of
  every 5-s frame against the logo, ±5 s].

**Introducing jargon and math**
- Operate first, name second: compute 4/24 from the sampled people, *then* "This
  number is known as the prior", then the formula ("this, my friends, is Bayes'
  theorem") [verified: V4 05:35, 07:15].
- New terms appear on screen in quotation marks with an arrow to the symbol:
  "Prior", "Likelihood", "Posterior", "Hidden layers", "Activation", "Scalars"
  [verified: frames V1, V2, V4].
- Explicit naming moves ("called", "known as", "the name") run 0.3–3.4 per 1,000
  words [measured: regex over transcripts], i.e. one explicitly named term every
  ~2–20 minutes. Names are scarce; most new ideas are described, not named.
- Symbols get a spoken gloss the first time: "This funny little elbow symbol is
  commonly used in probability to mean not" [verified: V4 06:14].

**Story and history.** Real people anchor many videos: Kahneman & Tversky (V4),
Shannon (V8), a 1980s treasure hunt (V4), whoever sent him the proof ("Sent my
way via Senia Sheydvasser", V7 on screen). History is motivation, not a
chronology [verified: transcripts, frames].

**Humour.** Dry asides in the narration ("and I'm not making up that name", V4;
"comically trivial", V2), pi creatures reacting ("Boring!", "Isn't it…") and
self-aware objections ("viewers of classic math YouTube will be yelling at their
screens", V7). No jokes in on-screen text beyond the characters [verified:
transcripts, frames].

**The viewer's voice.** Objections are voiced for the viewer: "But I hear some of
you asking, how does the robot know how to decode this?" (V8); a student pi
creature asks "Are people expected to know that?" (V4). Invitations to stop and
think recur: "please do pause and ponder whenever you feel like you see the key
idea" (V7) [verified: transcripts, frames].

**Endings** [verified: transcripts]
- Return to the opening anchor with a portable principle: V4 ends on Steve and
  "evidence should not determine beliefs, but update them".
- Open puzzle / exercise: V5 (multiplication as convolution), V7 (comb a 4-D
  hypersphere).
- Next-chapter tease: V1, V3, V5, V6.
- No recap lists in any of the eight.
- 2026 videos add a non-sponsored "career fair" segment after the content (V7, V8).

## 4. Language profile

All rates come from YouTube captions (the creator's manual `en` track for
punctuation; the auto track for word timing; V7 has no manual track) and from the
audio track [measured: lang_metrics.py, pauses_audio.py].

| | V1 | V2 | V3 | V4 | V5 | V6 | V7 | V8 |
|---|---|---|---|---|---|---|---|---|
| Year | 2016 | 2017 | 2018 | 2019 | 2022 | 2024 | 2026 | 2026 |
| Words | 1,792 | 3,357 | 3,528 | 2,650 | 4,614 | 5,137 | 5,689 | 5,764 |
| WPM, whole video | 182 | 179 | 179 | 175 | 199 | 191 | 192 | 183 |
| WPM, excl. pauses ≥0.5 s | 232 | 223 | 228 | 224 | 240 | 219 | 221 | 217 |
| Audio pauses ≥1 s / min | 1.73 | 1.72 | 1.78 | 1.38 | 0.96 | 0.88 | 0.54 | 0.45 |
| Pauses ≥2 s (count) | 7 | 7 | 12 | 5 | 6 | 1 | 0 | 1 |
| Silence share (gaps ≥0.3 s) | 19% | 15% | 19% | 16% | 13% | 11% | 10% | 10% |
| Median pause (≥0.3 s) | 0.43 s | 0.48 s | 0.50 s | 0.48 s | 0.42 s | 0.40 s | 0.40 s | 0.40 s |
| 90th-pct pause | 0.96 s | 1.07 s | 1.03 s | 0.96 s | 0.84 s | 0.78 s | 0.75 s | 0.76 s |
| Mean sentence (words) | 24.9 | 25.6 | 25.8 | 22.6 | 28.3 | 31.3 | 24.7* | 24.6 |
| Sentences > 30 words | 31% | 33% | 32% | 20% | 39% | 43% | 26%* | 33% |
| Sentences ≤ 8 words | 6% | 11% | 5% | 12% | 3% | 2% | 9%* | 8% |
| Questions / min | 0.30 | 0.75 | 0.41 | 0.59 | 0.13 | 0.00 | 0.27* | 0.25 |
| Questions, % of sentences | 4% | 11% | 6% | 8% | 2% | 0% | 4%* | 3% |
| Flesch–Kincaid grade | 11.5 | 11.8 | 11.0 | 11.7 | 12.8 | 14.2 | 10.9* | 12.0 |
| "I/me/my" per 1k words | 11.7 | 13.4 | 7.4 | 7.5 | 13.0 | 9.9 | 12.8 | 9.5 |
| "we/us/let's" per 1k | 6.7 | 8.6 | 17.0 | 10.6 | 17.1 | 8.4 | 9.8 | 7.8 |
| "you/your" per 1k | 26.2 | 20.0 | 20.1 | 23.0 | 27.5 | 19.3 | 29.2 | 20.0 |
| Contractions per 1k | 17.9 | 17.6 | 18.4 | 23.8 | 25.1 | 20.1 | 16.7 | 21.7 |
| Sentences opening with and/but/so/or/now/then | 19% | 34% | 40% | 24% | 36% | 12% | 32% | 27% |

\* V7 uses YouTube's punctuated auto captions, so its sentence and question
counts are less reliable. V2 includes a short interview with Lisha Li at the end.
Pause figures use an adaptive RMS threshold (18 dB under the 70th-percentile
frame); background music fills some gaps, so they are lower bounds.

**What the numbers say**

1. **Fast, steady, conversational.** ~175–200 WPM including pauses, ~220–240 WPM
   while talking. That is brisk for narration, yet the videos don't feel rushed,
   because sentences carry one idea each and the picture does the rest.
2. **Pauses got shorter and rarer.** Pauses of 1 s or more fell from ~1.7/min
   (2016–18) to ~0.5/min (2026); pauses of 2 s or more almost vanished. The typical
   gap is 0.4 s and 90% are under ~0.8 s in recent videos.
3. **Long, compound sentences.** Mean 23–31 words, a third over 30 words,
   grade 11–14 reading level. Commas, "and then", "which means" chain clauses;
   the voice keeps one thought moving rather than stacking short declaratives.
4. **Few questions.** 0–0.75 per minute. When they come they are *motivating*
   ("How does this network learn the appropriate weights and biases just by
   looking at data?") or *anticipating* ("Now why am I telling you this, you might
   ask?"), plus tag questions ("Pretty interesting, right?"). V6 asks none.
5. **"You" first, then "I", then "we".** Second person is ~2× first person.
   "You" is usually hypothetical ("If you take…", "Suppose I give you…"), and
   "you and I" appears for shared work ("you and I are going to tackle these in
   reverse order", V4).

**Recurring phrases** [measured: n-grams found in ≥5 of 8 videos]
- "for example, let's say" — the standard way into a concrete case.
- "if you take the …" — a hands-on operation.
- "I want you to …" — a direct request to notice or imagine.
- "a little bit (of)", "each one of those", "what I mean (by)", "by the way",
  "in this case", "think about / think of".
- Top sentence openers: "If you…" (27), "For example…" (23), "This is…" (15),
  "And then…" (12), "I mean…" (7), "You might…" (6).

**Patterns with short examples** [verified: transcripts]
- *Appreciation before analysis:* "And I want you to take a moment to appreciate
  how crazy it is that brains can do this so effortlessly." (V2)
- *Stating the mantra:* "The upshot, and this is the key mantra underlying Bayes'
  theorem, is that new evidence does not completely determine your beliefs in a
  vacuum. It should update prior beliefs." (V4)
- *Voicing the viewer:* "Now why am I telling you this, you might ask?" (V3)
- *Owning uncertainty:* "I'm in no position to say whether this does or does not
  run against natural human instinct." (V4)
- *Signposting the arc without a menu:* "For the moment though, I imagine there's
  a more burning question…" (V7). "In other words" never appears in the sample.
- *Enthusiasm in plain words:* "Really, it's crazy just how ubiquitous this idea
  is." (V3). Evaluative words ("nice", "beautiful", "cool") appear 0–2.2 per 1k.

## 5. Flow

Two beat sheets: V4 (classic era, 15 min) and V7 (current era, 30 min).
Timestamps from the manual / auto caption track; pictures from 5-s frames.

### V4 — Bayes theorem, the geometry of changing beliefs (2019)

| Time | Said | Shown | On-screen text |
|---|---|---|---|
| 0:00 | Goal: understand Bayes' theorem; why it matters (science, ML, a 1980s treasure hunt). | Pi creature on a Now→Later timeline; gold bars; ship. | "1988 / Tommy Thompson and friends" |
| 0:31 | Three levels of understanding; "you and I are going to tackle these in reverse order". | Underlined title; three bullet questions with icons; formula parked top-right. | "Levels of understanding", "What is it saying? / Why is it true? / When is it useful?" |
| 1:04 | "I'd like to tell you about a man named Steve." Cut to the logo at ~1:12 (end of cold open), then the description. Librarian or farmer? | Logo; Steve icon; description paragraph with coloured phrases; split bar Librarian / Farmer with "???" | The quoted description (6 lines, keywords blue/yellow) |
| 1:33 | Kahneman & Tversky's study; most people say librarian. | Photos and book covers; pi creature thinks "Librarian". | Names under photos |
| 2:30 | The missed fact: ~20 farmers per librarian. Objection: is that fair? | Ratio icons; student pi creature speech bubble. | "Are people expected to know that?" |
| 3:15 | Representative sample: 10 librarians, 200 farmers; 40% vs 10% fit. | Grid of 210 person icons; braces count 4 and 20; highlight sweep. | "10", "200", "40%", "10%", P(Librarian given description) = 4/(4+20) ≈ 16.7% |
| 4:09 | Mantra: evidence updates prior beliefs; it restricts the space of possibilities. | Description crossed out in red → icon. | (none) |
| 4:30 | "Heart of Bayes' theorem": all possibilities → those fitting evidence → ratio. | Three diagrams side by side. | Underlined title; "Write this more mathematically" (red) |
| 4:52 | When to use it: hypothesis, evidence, want P(H|E). | Steve icon, description card. | "When to use Bayes' rule", "You have a hypothesis…" |
| 5:15 | Prior = 1/21, named "the prior"; likelihood 0.4; P(E|¬H) = 0.1. | Grid shrinks to a column of icons; quoted labels with arrows to symbols. | "Prior" → P(H) = 1/21, "Likelihood" → P(E|H) = 0.4, "¬ means not" |
| 6:19 | Rebuild 4/24 symbolically; 210 cancels; "this, my friends, is Bayes' theorem". | Formula assembled piece by piece above a dashed divider, each piece lit as spoken; icons inside the fraction. | Full formula, colour-coded H/E |
| 7:24 | P(E) expands; final name: posterior. | Formula extended right; label added. | "Posterior" |
| 7:50 | Why write it abstractly: scientists, ML, quantifying belief change. | Scientist and programmer icons with formula cards. | Formula on cards |
| 8:37 | Don't memorize — think of a 1×1 square of possibilities. | Square; yellow prior strip; teal restricted areas; arrow from formula. | "Remember this" |
| 10:14 | Step back: Linda the bank teller experiment; 85% pick the conjunction. | Photos, Linda icon, paragraph, numbered options, Venn ellipse. | The Linda paragraph; "1) … 2) …"; "85% chose this!" (red) |
| 11:34 | Asking "how many of 100" fixes it. | Same layout, reworded prompt. | "100 people fit this description. How many are…" |
| 12:09 | Samples vs. continuous; probability as the math of proportions. | Pi creature with "40%" vs "40 out of 100"; rain square. | "Probability → Uncertainty", P(Rain) = 36.26% |
| 12:51 | Bayes as a statement about proportions. | Formula annotated top and bottom. | "How often is H true… / …among cases where E is true" |
| 13:22 | Back to Steve: who is he, really? | Steve, photos, student pi creatures. | (none) |
| 14:21 | Portable principle; reprogram intuition. | Brain ↔ formula; thought bubble with the square. | Formula only |
| 15:00 | End screen. | Patron list. | "Clicky Stuffs", patron names |

### V7 — Why you can't comb a hairy ball, and why we care (2026)

| Time | Said | Shown | On-screen text |
|---|---|---|---|
| 0:00 | His baby's hair swirl → "the hairy ball theorem". | Home video of the baby; furry sphere render. | "The Hairy Ball Theorem" |
| 0:30 | Informal statement; combing around an axis leaves two swirls. | Furry sphere close-ups. | (none) |
| 1:00 | Puzzle for the viewer: can you leave just one tuft? | Smooth teal sphere. | "Puzzle: Can you get the hairs flat at all but one point?" ("all but one" red) |
| 1:15 | "a more burning question": why care? | Pi creatures. | Speech bubble "Topology has more subtle utility" |
| 1:30 | Logo at ~1:40 ends the cold open. You're a game developer orienting a plane model along a path. | Logo; 3D plane on a grid flying a curve; heading and wing vectors. | Code snippet `def wing_vect(heading_vect)` (top-left) |
| 3:30 | Choosing a wing vector for each heading = a vector field on a sphere. | Sphere of headings, pink perpendicular vectors, tangent plane. | (none) |
| 4:30 | Formal statement; tangent vectors; drawing many arrows "to avoid clutter". | Dense arrow field on the sphere. | "Tangent Vector"; then underlined title + statement, keywords coloured |
| 5:45 | The animation code he used glitches at the poles — the theorem in action. | Plane flipping; code snippet. | Code snippet |
| 6:45 | Wind on Earth always has a calm point; uniform radio broadcast is impossible. | Textured Earth with flow; radio tower with rings and field arrows. | (none) |
| 9:00 | "So, to the puzzle." Do null points come in pairs? | Inset of the earlier puzzle on a grey backdrop; two spheres. | "Hypothesis: Null points come in pairs" |
| 9:45 | Stereographic projection turns a constant plane field into a one-null-point field. | Sphere over a plane, projection rays, flow lines. | "Stereographic Projection", "Before map / After map" |
| 12:00 | Zero null points? Proof by contradiction, credit to who sent it. | Three spheres: 2 / 1 / 0 nulls. Pi creatures. | "Obvious / Clever / ~~Very clever~~?", "Proof by Contradiction", "Goal: A feeling of rediscovery" |
| 13:00 | Each point walks a great circle to its antipode; motion is continuous. | Patterned sphere turning inside out; one point → several → all. | "1) p → −p  2) Motion varies continuously with p", "One point / Several points / All points" |
| 16:30 | Two facts: it turns inside out; it avoids the origin. | Numbered list beside the sphere; the inactive item dims. | "1) Inside out  2) Avoids the origin", "Why?" |
| 17:00 | What does "inside out" even mean? Orientation via coordinates and the right-hand rule. | Lat/long grid, tangent vectors, antipodal map. | "How to orient a surface", "Lat: 30° Lon: 45°" |
| 21:15 | Contrast with the classic sphere-eversion film. | Clip from *Outside In* (attributed). | "'Outside In' by Thurston, Levy, Maxwell, Munzner, et al." |
| 22:00 | Physical model: a fountain at the origin; flux through the surface. | Particle fluid, surface patches, live readout. | "Flux: +0.080 L/s" (sign coloured green/red) |
| 25:00 | The contradiction: flux must be −1 and +1. | Both claims with implications. | "1) Inside out ⟹ Final Flux = −1.0", "2) Avoids the origin ⟹ Final flux = +1.0", "Contradiction!" |
| 25:30 | Reflection: intuitive idea vs clever proof. | Two panels. | "Intuitive idea / Clever proof" |
| 26:00 | Non-sponsored career-fair segment. | Web screenshots. | "3b1b.co/talent" |
| 27:45 | Higher dimensions; pause-and-ponder puzzle. | Spheres. | (none) |

**Flow patterns across both** [inferred: from both beat sheets and the other six
contact sheets]
- One anchor carries most of the video (Steve and the 210 people; the sphere).
  The anchor's layout persists while its state changes: V3 keeps the same
  signal / winding / frequency-plot layout from 3:00 to 7:45.
- New sections open with an underlined title or a "Puzzle:"/"Hypothesis:" line,
  then the title leaves and the figure takes the stage.
- Claims needed later are written as a short numbered list that stays on screen
  and dims the items not in play.
- Earlier figures come back as insets on a dark-grey backdrop ("screen in
  screen") rather than being redrawn.

## 6. Visual system

**Background** — black. `background_color: "#000000"` in Grant's config
[verified: C1 custom_config.yml] (ManimGL's own default is `#333333` [verified:
C2 default_config.yml]). Corner pixels are pure black in 65–100% of frames per
video; the rest is a dark grey of ~#202020 [measured: bg_color.py], which matches
`GREY_E #222222`. `TeacherStudentsScene` hard-codes that grey as a full-screen
background with a black 16:9 "screen" rectangle in the upper-left
[verified: C1 custom/characters/pi_creature_scene.py]; the same grey sits behind
insets elsewhere [inferred: frames + `FullScreenRectangle` 0.5–0.7 per 1k code
lines]. Photographic textures appear as backdrops when the story needs a place,
e.g. a moon surface at 40% opacity under V8's robot [verified: C1
_2026/cross_entropy/robot.py].

**Palette** — ManimGL's named colours [verified: C2 default_config.yml], ranked by
use in 2024–26 scene code [measured: code_stats.py]:

| Name | Hex | Uses (2024–26) | Typical role in frames |
|---|---|---|---|
| YELLOW (= YELLOW_C) | `#FFFF00` | 977 | Highlight, "the thing in question", key result |
| WHITE | `#FFFFFF` | 819 | Default text and math |
| BLUE (= BLUE_C) | `#58C4DD` | 589 | Primary objects, first variable |
| RED (= RED_C) | `#FC6255` | 490 | Second variable, negatives, wrong |
| BLACK | `#000000` | 452 | Backstroke behind text |
| TEAL (= TEAL_C) | `#5CD0B3` | 421 | Primary objects (newer videos) |
| GREEN (= GREEN_C) | `#83C167` | 309 | Positive / correct |
| PINK | `#D147BD` | 277 | Third variable / accents |
| GREY_B / GREY_C / GREY_D / GREY_E | `#BBBBBB` / `#888888` / `#444444` / `#222222` | 150 / 62 / 69 / 50 | Axes, dimmed items, backdrops |
| BLUE_E (pi creature body) | `#1C758A` | 79 | Randolph (student) |
| GREY_BROWN (pi creature) | `#736357` | — | Mortimer (teacher) |

- In the frames, teal/blue is the dominant hue in every video (35–82% of
  saturated pixels); yellow comes next, then red/orange/pink [measured:
  palette.py].
- The file writer applies `saturation: 1.5`, so rendered colours are punchier
  than the hex values [verified: C1 config; effect inferred].
- **Watch out:** ManimCE's `YELLOW_C` is `#F7D96F` and `BLUE_E` is `#236B8E`
  [verified: vendor/manim colours], so CE constant names do not give the 3b1b hues.

**Colour as meaning.** One quantity keeps one colour everywhere: in text, in
formulas and in the figure.
- V5: the blue die is `a_i` and the red die is `b_i`, in the formula and in the
  dice.
- V4: H is yellow and E is teal in every formula and on the square.
- V7: the statement colours "continuous" blue and "one null vector" yellow to
  match the yellow null point on the sphere.

The tools are `t2c=` / `tex_to_color_map` (≈4 per 1k code lines in 2024–26) and
icons inside formulas, e.g. dice in P(■+■=2) and a person icon in (#🧍)P(H)
[verified: frames, C1 code; measured: code_stats.py].

**Typography**
- Math is LaTeX (Computer Modern). Prose is `Text` in **CMU Serif**, the same
  family, so labels and equations look like one typeface [verified: C1
  custom_config.yml]. In the contact sheets I read, no sans-serif text appears
  outside screenshots and code snippets [verified: contact sheets].
- Sizes (ManimGL `font_size`, where `font_size/144` = glyph height in units of an
  8-unit-high frame) [measured: code_stats.py, 2024–26]:
  - 72 (280 uses) — titles
  - 36 (239), 30 (142), 24 (139) — labels
  - 60 (193), 42–48 — body and readouts
  - Default 48 ≈ 4.2% of frame height.
- Titles: `to_corner(UL)` + `Underline`, or `to_edge(UP)` centred.
- Body text: left-aligned blocks, hand-broken at a median of 30 characters per
  line [verified: C1 hairy_ball/supplements.py StatementOfTheorem, bayes part1;
  measured: text_lines.py].

**On-screen text: how much and where.** I ran OCR on frames every 10 s (V1, V2)
or 20 s (V3–V8) [measured: ocr_text.py with RapidOCR; it misses tiny labels and
reads TeX poorly, so treat counts as lower bounds]. "Prose" means a frame with
≥ 8 ordinary words (alphabetic, ≥ 3 letters), so formulas and numbers are
excluded.

| | V1 | V2 | V3 | V4 | V5 | V6 | V7 | V8 |
|---|---|---|---|---|---|---|---|---|
| Frames with any text | 66% | 91% | 98% | 98% | 88% | 98% | 56% | 87% |
| Frames with prose | 0% | 8% | 5% | 22% | 7% | 33% | 10% | 2% |
| Text boxes in top ¼ / middle ½ / bottom ¼ of height | 21/60/19 | 31/56/12 | 35/50/16 | 34/44/22 | 34/53/14 | 18/65/17 | 44/44/12 | 27/57/16 |
| Median text-box height (% of frame) | 6.9 | 5.3 | 5.3 | 6.4 | 3.9 | 3.1 | 4.4 | 4.7 |

- Text is almost always present, but it is labels and math. Prose is rare
  (median ~7% of frames). It peaks where the prose *is* the subject: V4's
  quoted descriptions of Steve and Linda, V6's model inputs and outputs.
- There is no text band. Most text sits in the middle half of the frame, next to
  its object, and horizontally it splits roughly into thirds.
- The top quarter carries titles and "Puzzle:/Hypothesis:" lines (18–44% of
  boxes). The bottom quarter is the least used (12–22%), and never for
  subtitles.
- Labels dominate: 74% of single-line `Text` strings in 2022–26 code are ≤ 3
  words and 94% ≤ 6 words (median 2) [measured: text_lines.py].
- Kinds of text seen [verified: contact sheets]:
  - object labels and quoted term names ("Prior", "Hidden layers")
  - underlined section titles and "Puzzle:/Hypothesis:/Quiz:" lines
  - numbered claims
  - live numeric readouts ("3.00 cycles/second", "Flux: +1.000 L/s")
  - speech/thought bubbles
  - quoted source text the story is about (Steve's description, generated LLM text)
  - code snippets in V7
- The narration is never captioned on screen, and key sentences are spoken, not
  displayed.

**Equations**
- `Tex` with colour maps; parts are indexed by substring (`tex["x"]`) for
  highlighting and morphing [verified: P1 46:13, C1].
- Built up while narrated (V4 assembles the fraction piece by piece).
- Kept in a zone apart from the diagram (V4 draws a dashed divider between the
  formula row and the diagram).
- Earlier forms stay dimmed rather than deleted (V5's general sum is dimmed while
  the cases list is active) [verified: frames V4 6:45, V5 5:45].

**Characters**
- Pi creatures are SVG designs loaded from Grant's Dropbox, so the art is not in
  the repo [verified: C1 custom_config.yml `pi_creature_images`, pi_creature.py].
- `TeacherStudentsScene` is the stock "classroom" shot [verified: C1
  pi_creature_scene.py]:
  - three Randolph students in BLUE_D / BLUE_E / BLUE_C, bottom-left
  - a Mortimer teacher in GREY_BROWN, bottom-right
  - a black screen rectangle (height 4) in the upper-left for the figure under
    discussion
  - a GREY_E backdrop
- Modes (`says`, `thinks`, `change("hesitant")`, `Blink`) carry the viewer's
  objections and reactions [verified: C1 code, frames].
- They appear in all eight videos, densest in 2016–17: 11–12 of 36 samples in the
  first 9 min of V1/V2 vs 3–6 in V3–V7 [measured: manual count on contact sheets].
- V8 adds an illustrated robot-rover pi creature as PNG sprites [verified: C1
  robot.py] — illustration, not Manim geometry.

**Imagery beyond Manim geometry** [verified: frames + C1 code]
- Photos (Kahneman, Tversky, book covers) and line icons (Steve, books, wheat).
- Live footage: dice rolling in V5, the baby in V7.
- 3D `.obj` models (V7 plane) and textured surfaces (Earth texture maps).
- Third-party film clips with attribution (V7).
- Web and terminal screenshots, and AI-generated images (V6; he notes he
  couldn't get the model to draw a pi creature).
- Photoreal fur (V7): source not found.

**Composition and density** [inferred: contact sheets, full frames]
- One primary figure per frame, usually centred or right of centre. Text sits
  left or above as a short label next to its object.
- Multi-panel layouts are a deliberate "dashboard" for one anchor (V3: signal top,
  winding graph bottom-left, frequency plot bottom-right).
- Insets and comparisons: 2–3 small framed panels with one-word headers ("One
  point / Several points / All points").
- Dense frames exist (V5's 11-line cases list; V6's token tables) but stay
  single-topic, with every element sharing one colour code.

## 7. Motion & sync grammar

**Clip and shot lengths**

Measured from 10 fps, 160×90 frame differences [measured: motion_stats.py].
A hard cut is a one-frame jump ≥ 8 grey levels and ≥ 6× its ±1 s
neighbourhood; I checked 4 of V4's cuts by eye and all were real. "Still" means
the mean frame difference is under 0.25 grey levels, so a tiny moving dot can
still count as still.

| | V1 | V2 | V3 | V4 | V5 | V6 | V7 | V8 |
|---|---|---|---|---|---|---|---|---|
| Hard cuts / min | 1.2 | 2.9 | 1.7 | 2.2 | 2.8 | 3.3 | 3.2 | 2.8 |
| Median shot (s) | 26.4 | 11.2 | 15.9 | 7.9 | 10.7 | 13.3 | 10.6 | 11.7 |
| Mean shot (s) | 45.5 | 20.4 | 34.7 | 26.0 | 20.9 | 18.2 | 18.5 | 21.2 |
| Still frames | 85% | 73% | 49% | 74% | 65% | 61% | 27% | 44% |
| Holds ≥ 1 s per min | 10.3 | 12.1 | 7.8 | 12.1 | 10.1 | 9.8 | 5.0 | 7.0 |
| Median hold (≥ 1 s) | 3.0 s | 2.2 s | 2.4 s | 2.6 s | 2.2 s | 2.2 s | 1.9 s | 2.3 s |
| 90th-pct hold | 9.5 s | 5.8 s | 6.0 s | 6.7 s | 6.3 s | 5.6 s | 4.4 s | 5.6 s |
| Longest hold | 30.5 s | 25.8 s | 18.9 s | 14.9 s | 19.4 s | 18.0 s | 18.8 s | 16.8 s |
| Time in holds ≥ 3 s | 67% | 45% | 30% | 51% | 35% | 31% | 11% | 23% |

Apart from V1 and V3, there are 2–3 hard cuts a minute (one every ~20–25 s).
Shots are long by YouTube standards, because most change happens *inside* a shot
as morphs and camera moves.

- One video is cut from 24–55 Manim scene classes: V1 24, V2 55, V4 47, V7 55
  [measured: class counts in C1]. That is one class per 19–32 s of finished
  video [inferred: count ÷ duration; not every class is used].
- Animation `run_time` has a median of 2.0 s (p10 1 s, p90 5 s in 2015–19 and 8 s
  in 2024–26) [measured: code_stats.py].
- About 60 `play` calls and 38 `wait` calls per 1,000 lines of scene code
  [measured].

**How visuals track the words**

- *Process.* The animation is built first, sentence by sentence against the
  script ("putting visuals to each sentence"). The VO is recorded over the laid-out
  timeline, and then he cuts [verified: W6, W5]. Sync is hand-made per shot in
  Final Cut, not computed from word timestamps [inferred: no audio in scene code,
  bare 1-s waits, W1 "clips to be edited together later"].
- *Measured alignment* [measured: sync_stats.py].
  - Of the motion onsets (the picture starts changing after ≥ 1 s of stillness),
    36–54% fall within ±1 s of a phrase start (a word after ≥ 0.3 s of silence).
  - Chance would give roughly 33–50%, given 12–21 phrase starts per minute.
  - So onsets are only loosely locked to phrase starts: above chance in V4, V5,
    V7, V8 and at chance in the rest.
- *When they do line up, the picture follows the voice.* Among onsets within
  ±2 s of a phrase start:
  - the median lag is +0.0 to +0.3 s, i.e. the picture moves just *after* the
    phrase begins;
  - lags (46–53%) outnumber leads (27–51%) in 7 of 8 videos.
- *Within a shot*, alignment is by idea, not by word. A shot holds one figure
  through several sentences while the narration walks around it, then moves when
  the idea moves. Holds of 2–3 s are typical, 5–10 s are common (90th
  percentile), and 15–30 s happen in every video (table above).

**Transitions inside a scene** [measured: per-1k-line rates, 2015–19 → 2024–26]
- Morphing grew:
  - `TransformFromCopy` 1.1 → 6.0
  - `TransformMatchingTex/Strings` 0 → 2.0
  - `FadeTransform` 0 → 2.5
  - plain `Transform` fell 6.3 → 1.8
- Staggered entrances (`lag_ratio`) rose 2.5 → 16.2.
- `.animate` rose 0 → 35.
- Camera work (`frame.animate`, `reorient`) rose 0 → 8.5 + 1.4; 3D camera
  glides are now a staple.
- `Write` is reserved for text and equations; `ShowCreation` draws curves and
  graphs; `FadeIn/FadeOut` handle the rest.

**Emphasis.** Colour change plus an under- or around-flash (`FlashUnder`,
`FlashAround`, `VShowPassingFlash`), a `SurroundingRectangle` (≈4 per 1k), or
dimming everything else. `Indicate` is rare (0.06–0.36 per 1k) and
`Wiggle`/`Flash` are almost unused [measured: code_stats.py; verified:
hairy_ball/supplements.py uses `FlashUnder` + `set_fill(color)` on
"continuous"].

**What happens in pauses.**

- Pauses ≥ 0.6 s are not reserved for animation.

  | Share of frames moving | V1 | V2 | V3 | V4 | V5 | V6 | V7 | V8 |
  |---|---|---|---|---|---|---|---|---|
  | During speech | 15% | 28% | 49% | 27% | 36% | 40% | 74% | 57% |
  | During pauses | 17% | 24% | 71% | 19% | 30% | 35% | 67% | 56% |

  [measured: sync_stats.py]
- Pauses therefore behave like speech. Usually the picture is either holding or
  continuing a morph. Only V3 (the winding animation) moves clearly more in
  pauses.
- The long pauses that do exist sit right after a payoff or at a section turn.
  V4's longest gaps [measured: audio RMS] map onto its beat sheet:
  - 2.0 s at 4:19, right after the mantra "It should update prior beliefs"
  - 2.7 s at 4:50, between "Heart of Bayes' theorem" and "When to use"
  - 2.0 s at 7:38, after the formula is complete
  - 1.8 s at 8:30, before "don't memorize"
  - 1.6 s at 10:13, before the Linda detour
  - 3.6 s at 12:41, before "Bayes as proportions"

**Between scenes.** Scenes are separate renders joined in Final Cut [verified:
P1, W1].

- The common move is to fade the figure out and start the next clip on an empty
  black stage. `FadeOut` runs at ~16 per 1k lines and every scene class begins
  empty.
- Hard cuts come at ~3/min in recent videos (table above).
- Cuts go to and from the logo, the classroom (grey) scenes, footage and insets.
  The 4 detected cuts I inspected in V4 went logo→Steve, title→title, diagram→
  formula and classroom→sample grid.
- No wipes, slides or 2D transition effects appear in any sampled frame
  [verified: cut frames, contact sheets].

## 8. Polish

What keeps 3b1b frames clean, roughly in order of how much it matters.

1. **Each scene is a fresh stage.**
   - A scene class is a short clip that starts from nothing and is cut, not
     cleaned up. Leftovers from section A cannot reach section B, because B is a
     different render [inferred: C1 architecture of 24–55 classes per video plus
     editor assembly].
   - Inside a clip, the number of live objects stays small.
2. **Labels are attached, not parked.**
   - `next_to(obj, dir, buff)` is the most common placement call (~22 per 1k
     lines), ahead of `move_to` (14) and `to_edge` (6–9) [measured]. Default
     buffers are 0.25 between objects and 0.5 from the frame edge
     [verified: C2 default_config.yml].
   - A label moves with its object. Updaters (`add_updater`, `f_always`) keep
     labels glued to moving things [measured: 6.4 + 1.2 per 1k].
3. **Black backstroke instead of avoidance.**
   - `set_backstroke(BLACK, 3–8)` draws a black outline *behind* the glyphs
     [verified: C2 vectorized_mobject.py `set_backstroke` default width 3; C1
     uses widths 1–8, with 5–8 on titles and labels].
   - A label can then sit over grid lines, arrows or a busy 3D render and stay
     legible. Before 2020 the same job was `add_background_rectangle`
     [measured: 2.35 → 0.09 per 1k lines].
   - ManimCE has the same mechanism: `set_stroke(BLACK, w, background=True)` /
     `background_stroke_width` [verified: vendor/manim vectorized_mobject.py].
4. **Short text.** Median two words per label; prose only when the prose *is* the
   object (a quoted description, a model's output). Multi-line text is
   hand-broken at ~30 characters, left-aligned, never auto-shrunk to fit
   [measured: text_lines.py; verified: C1 statement code].
5. **Colour replaces arrows.** Because a word and its object share a colour, few
   leader lines are needed. When a term needs pointing, it gets quotation marks
   and one short arrow ("Prior" → P(H)) [verified: frames V4].
6. **Dim, don't delete.**
   - What is not in play drops to low opacity but stays put: dimmed formulas
     (V5), inactive list items (V7), inactive bars (V8) [verified: frames].
   - The eye goes to the bright thing; the layout never jumps.
7. **Zones within a frame.** Formula row above, diagram below, sometimes split
   by a dashed line (V4). Text column left, figure right (V7 statement). Titles
   top-left with an underline [verified: frames, code].
8. **Overlays for 3D.**
   - Text over 3D scenes is pinned to the camera with `fix_in_frame()`
     [verified: C1, P1 45:39; measured 1.75 per 1k lines 2024–26].
   - Some overlays are their own scenes. `FluxDecimals` contains only a
     corner readout, which is then laid over the fluid render
     [verified: C1 hairy_ball/supplements.py; compositing inferred].
9. **Insets instead of redraws.** A finished figure returns as a small framed
   inset on dark grey, so the viewer recognizes it without a second build
   [verified: frames V5 1:30, V7 9:00].
10. **Not perfect, and that's fine.**
    - V3 at 5:45: "3.00 cycles/second" sits on the top edge of its grid panel,
      and "Center of mass" crosses the panel's bottom edge.
    - Both stay readable because the text is bright on black with a dark
      backing [verified: full frame V3 5:45].
    - 3b1b tolerates text touching a figure. It does not tolerate text that is
      unreadable or that names the wrong thing.

## 9. Reproducing it with a code-driven pipeline

**What code (Manim CE) can reproduce directly**
- Black background; ManimGL hex palette defined explicitly (not CE's
  `YELLOW_C`); CMU Serif for `Text` so it matches LaTeX (the font has to be
  installed first).
- Underlined titles; left-aligned, hand-broken statement blocks.
- `MathTex` with `tex_to_color_map` shared with the diagram's colours.
- Build-up via `TransformMatchingTex` / `TransformFromCopy`.
- Quoted term labels with short arrows; braces with counts.
- Numbered claim lists with active/dim states.
- Live readouts (`DecimalNumber` + updaters, sign-coloured).
- Black background-stroke on all text.
- `LaggedStart` entrances; dashboards that persist and update.
- Screen-in-screen insets on `#222222`.
- 3D scenes with camera moves and fixed-in-frame overlays.
- Icons from SVG; photos via `ImageMobject`.

**What needs assets or another tool**
- A character. Pi creature art is Grant's: the repo's content is CC BY-NC-SA
  [verified: C1 README] and the SVGs are not in it. A comparable *own* mascot
  with poses, eyes and speech bubbles would be needed [inferred].
- Illustrations (V8's robot sprites), icon sets, photos of people and books.
- Live footage, third-party film clips, textured 3D models, photoreal renders.
- Music: a quiet bed under the setup, out of the way in technical stretches
  [verified: P3 12:26].
- Editing/compositing: clips assembled on a timeline, overlays composited, cuts
  timed to the VO. A code pipeline can stand in for this with per-beat clips
  joined by ffmpeg, but the "cut as thinking" step is human in 3b1b [verified:
  W5].

**Building blocks we would need**

| Block | Behaviour |
|---|---|
| `Palette3b1b` | ManimGL hexes plus a per-video map from concepts to colours, shared by `MathTex` and figures. |
| `Title` | Text at 72 in CMU Serif, `to_corner(UL)` plus `Underline`. Fades when the figure takes over. |
| `Label(obj, text, dir)` | `next_to` + backstroke, rides its object via updater, dies with it. |
| `TermTag("Prior", target)` | Quoted name with a short arrow to a symbol. |
| `ClaimList` | Numbered claims; `activate(i)` dims the others to ~0.3. |
| `Readout` | "Name: value unit" with live value and sign colour. |
| `Inset(fig)` | Shrinks a finished figure onto a GREY_E screen rectangle. |
| `Dashboard` | Fixed panels for one anchor whose state changes. |
| `Mascot` | Poses, blink, look_at, says/thinks bubbles; used for objections and reactions. |
| `ClassroomScene` | Grey backdrop, a black screen rectangle upper-left holding the current figure, three students bottom-left, a teacher bottom-right (the `TeacherStudentsScene` layout). |
| `ColorLinkedText` | Prose where keywords take their object's colour, plus a `FlashUnder`. |
| Scene-per-beat rendering | Each beat is its own clip with a clean stage, assembled with optional fades. |
| Pacing profile "3b1b" | ~185 WPM, median gap 0.4 s, ≥1 s gaps < 1/min, no forced pause after every question. |

## 10. Sources

**Sample videos** — V1–V8, table at top. Manual English captions (`en`), YouTube
auto captions (`en-orig`, word timing), audio (m4a) and 360p video, all pulled
2026-11-21 with yt-dlp.

**Grant's own process videos** (captions read in full or grepped)
- P1 — [How I animate 3Blue1Brown | A Manim demo with Ben Sparks](https://www.youtube.com/watch?v=rbu7Zu5X1zI), 2024-10-12
- P2 — [Make math videos! | Summer of Math Exposition announcement](https://www.youtube.com/watch?v=ojjzXyQCzso), 2021-07-16
- P3 — [What makes a great math explanation? | SoME2 results](https://www.youtube.com/watch?v=cDofhN-RJqg), 2022-10-01
- P4 — [Q&A with Grant Sanderson (3blue1brown)](https://www.youtube.com/watch?v=Qe6o9j4IjTo), 2018-08-24

**Code** (shallow clones, 2026-11-21)
- C1 — [github.com/3b1b/videos](https://github.com/3b1b/videos) @ `31f8ffe` (2026-11-10): `custom_config.yml`, `README.md`, `CLAUDE.md`, `stage_scenes.py`, `custom/characters/pi_creature.py`, `custom/end_screen.py`, `_2019/bayes/part1.py`, `_2026/hairy_ball/*.py`, `_2026/cross_entropy/robot.py`, plus all `_20xx` scene code for the counts.
- C2 — [github.com/3b1b/manim](https://github.com/3b1b/manim): `manimlib/default_config.yml`, `constants.py`, `mobject/types/vectorized_mobject.py`, `config.py`.
- vendor/manim (this repo's ManimCE fork) for CE colour constants and background stroke.

**Web** († = read by a research sub-agent, not re-read by me; others I read or
spot-checked the quoted passage myself)
- W1 — https://www.3blue1brown.com/about — FAQ, team, Manim and video-making advice (fetched 2026-11-21)
- W2 † — https://web.archive.org/web/20210105170409/https://www.3blue1brown.com/faq — 2021 FAQ
- W3 † — https://www.3blue1brown.com/blog/some1 — SoME1 rules and four criteria (2021)
- W4 † — https://some.3b1b.co/rules — current SoME criteria
- W5 — https://www.dwarkesh.com/p/grant-sanderson — Dwarkesh Podcast, 2023-10-12 (timeline → VO → edit quote checked)
- W6 — https://podscripts.co/podcasts/lex-fridman-podcast/grant-sanderson-3blue1brown-and-the-beauty-of-mathematics — Lex Fridman #64 auto-transcript, 2020-01-07 (script → visuals → narrate → edit quote checked)
- W7 — https://podscripts.co/podcasts/lex-fridman-podcast/118-grant-sanderson-math-manim-neural-networks-teaching-with-3blue1brown — Lex Fridman #118, 2020-08 (Blue Yeti quote checked; other quotes †)
- W8 — https://www.numberphile.com/s/The-Hope-Diamond-with-3blue1brown.pdf — Numberphile podcast transcript, 2018-12-12 (sample-lessons quote checked)
- W9 † — https://perell.com/podcast/grant-sanderson-math-for-the-masses — notes, hooks, ambient research (2020)
- W10 † — https://habr.com/ru/post/594373/ — written Q&A, script and animation durations (2021-12-09)
- W11 † — https://smartventure.substack.com/p/week-5-here-we-come — paraphrased Q&A (2023-02-01)
- W12 — https://3blue1brown.substack.com/p/recruiting-both-for-myself-and-for — one-man shop, contractors (2025-12-04; quote checked)
- W13 † — https://3blue1brown.substack.com/p/an-artists-take-on-ai-in-math — 2026 team (2026-10-23)
- W14 † — https://3blue1brown.substack.com/p/how-i-animate-3blue1brown — Manim demo post (2024-10-12)
- W15 † — https://3blue1brown.substack.com/p/some4-prizes — "feel like you invented it yourself" (2026-01-16)
- W16 † — https://3blue1brown.substack.com/p/reinventing-entropy — "rediscover the core idea" (2026-06-07)

**Method.** Scripts, transcripts, frames and outputs are kept out of git in
the gitignored repo folder
`research_cache/3b1b/`
(`scripts/`, `analysis/`, `txt/`, `frames/`, `sheets/`). Video and audio files
were deleted after measuring.

| Script | What it measures |
|---|---|
| `lang_metrics.py` | WPM, ASR gaps, sentence stats, questions, pronouns, signposts, Flesch–Kincaid (textstat) |
| `pauses_audio.py` | 20 ms RMS, threshold 18 dB under the 70th-percentile frame |
| `demo_pace.py` | The same audio method on the skill's 47 demo narrations |
| `motion_stats.py` | 10 fps frame differences: cuts, still share, holds |
| `sync_stats.py` | Motion vs. narration pauses and phrase starts |
| `bg_color.py`, `palette.py` | Frame colours |
| Logo detector | Correlation of every 5-s frame against logo frames |
| `ocr_text.py` + `ocr_summarize.py` | RapidOCR, 10–20 s frame spacing |
| `code_stats.py` | API usage per 1k lines by era |
| `text_lines.py` | On-screen string lengths |

Contact sheets at 15-s spacing were made for all eight videos; I read the first
sheet of each and additional sheets for V4 and V7, plus full frames for detail.

## 11. Gap analysis vs our skill

Read against `skills/manim-explain/SKILL.md`, `references/narrative-patterns.md`,
`references/craft-laws.md` and `assets/style.py`. For pacing I also measured the
skill's own narrations: 47 demos with `audio/narration.mp3` + `timing.json`,
same audio method as §4.

### Already captured

- **Concrete before abstract, meaning before names.** Craft laws 7 and 12
  (motivate → manipulate → name) and the "compress into terminology" step of the
  arc match Grant's advice almost word for word [P2 10:10, P2 16:47].
- **One anchor kept front and center.** Narrative law 4 and the "concrete
  anchors" section match the SoME2 clarity advice [P3 11:41].
- **Naive-but-flawed, then refine.** "Productive failure" (narrative §3) is the
  same as Grant's micro-motivation template [P3 09:44].
- **Formulas build up from visuals and morph.** Craft laws 11 and 16 and Motion 14
  match V4's piece-by-piece assembly and the rise of `TransformMatchingTex` /
  `TransformFromCopy` in his code.
- **Return to the opening anchor and leave one portable principle** (law 17) —
  exactly V4's ending.
- **Evidence as relationships, rounded toy numbers OK** (law 14) — matches how V4
  uses 1/21, 0.4 and 16.7% as the toy, not as results.
- **Dimming is not deletion** (Motion 4) and **labels die with their referent**
  (Layout 3) — consistent with 3b1b's dim-in-place habit.
- **Dark background + LaTeX + blue/teal/yellow/red palette** — the right family.

### Missing

1. **Typography.** `style.py` builds every `Text` without a font, so Pango picks
   the host's fallback.
   - On this machine that renders as a DejaVu-style serif, wider and heavier
     than Computer Modern [verified: keyframe
     `demos/mn-06-neuron/out/keyframes/002_play-end_4.20s.png`; `fc-list` shows
     no CMU fonts installed].
   - 3b1b's `Text` is CMU Serif, so labels match the LaTeX [C1 config].
   - The mismatch between prose and `MathTex` is visible in any frame that has
     both, and the result is host-dependent.
2. **Backstroke legibility.** No helper sets a black background stroke on text.
   The skill's only defence against text-over-figure is to keep them apart
   (bands, clearance 0.17–0.25). 3b1b lets labels touch figures and keeps them
   readable with `set_backstroke` [C2, C1].
3. **Colour as a shared key between words, formulas and figures.** `C` is a role
   palette (primary/accent/wrong/right) with no per-concept map that
   `MathTex(tex_to_color_map=…)`, labels and figures all read from.
4. **The 3b1b hexes.** `C["accent"] = YELLOW_C` is CE's `#F7D96F`, not 3b1b's
   `#FFFF00`. `BLUE_E` differs too. Defining the ManimGL values explicitly fixes
   it.
5. **A character for the viewer's voice.** No mascot, no speech or thought bubbles,
   no "student objects" beat. In 3b1b these carry objections, reactions and humour
   in every sampled video.
6. **The viewer's voice in the script.** The narrative refs never ask for
   anticipated objections ("you might ask…", "I hear some of you asking…"),
   "pause and ponder" invitations, an end-of-video puzzle, first-person asides,
   or credit to a person / history beat as motivation.
7. **Non-Manim imagery.** No path for photos, icons, footage, screenshots, 3D
   models or insets of earlier figures.
8. **Composition patterns.** Underlined UL titles, text-left/figure-right
   statements, persistent dashboards for the anchor, numbered claim lists with
   dim states, screen-in-screen insets. None are helpers today.
9. **Scene-per-beat architecture.** The skill renders each demo from one
   `ExplainerScene`; `ce-01` is a single class of 2,377 lines and `ce-10` has two
   classes over 3,751 lines [verified: demos/*/scenes]. Grant cuts a video from
   24–55 classes. The single long `construct` is why the skill needs leftover
   scanners, phantom-slot fixes and a section-boundary law (Layout 7). 3b1b
   sidesteps all of it with short scenes joined in the edit.
10. **Cold open, end card and music bed.** No logo/cold-open convention, no end
    screen, no quiet music under setup segments.
11. **External review before final.** Grant runs sample lessons before scripting
    and a Patreon early release before publishing [W8, W1]. The skill's "no
    approval gates" rule is about not blocking on Ben. It has no cold-viewer
    review of the *script* either (simulated or real).

### Gets wrong (relative to 3b1b)

1. **Pacing is ~25% slower and far more paused.** I ran the §4 audio method on
   all 47 demo narrations [measured: demo_pace.py on `demos/*/audio/narration.mp3`
   + `timing.json`]:

   | | Skill demos (median, range) | 3b1b V1–V8 |
   |---|---|---|
   | WPM over the voiced span | 139 (122–161) | 179–202 |
   | Pauses ≥ 1 s per min | 4.6 (1.4–8.4) | 0.45–1.78 |
   | Silence share (gaps ≥ 0.3 s) | 22% (18–25%) | 10–19% |
   | Median pause | 0.54 s | 0.40–0.50 s |
   | 90th-percentile pause | 1.14 s | 0.75–1.07 s |

   - The pause budget asks 0.9–1.3 s after every question and 0.7–1.0 s after
     every heavy morph. 3b1b's 90th-percentile pause is 0.75–1.07 s, and recent
     videos have ~0.5 pauses ≥ 1 s per *minute*.
   - Grant does warn against fire-hose speed, so the target is not "faster". It
     is his profile: long sentences at a steady clip, with the picture doing the
     work, and rare long pauses at section turns.
2. **Idle motion.** `soft_idle`, `breathe_until` and `breathe_scene` keep figures
   pulsing, and `check_sync` treats any still stretch over ~6 s as a defect
   (Motion 3).
   - 3b1b holds still while the voice explains: 27–85% of frames are still, the
     90th-percentile hold is 4.4–9.5 s, and every video has holds of 15–30 s
     (§7).
   - Grant's rules are "Every movement on the screen should be deliberate" and
     "Avoid pointless animations" [W1]. Breathing pulses are exactly the kind of
     motion he warns against.
3. **Emphasis via `Indicate`.** `pop_named` and `ask_about` scale-and-recolour with
   `Indicate` (×1.06–1.18). 3b1b almost never uses `Indicate` (0.06–0.36 per 1k
   lines). It emphasises by colouring the term, flashing under or around it, or
   dimming the rest.
4. **Key sentences and questions as on-screen text.**
   - `key_sentence` / `ask_about` write the narrated sentence or question in a
     band and then animate it to a parked side position.
   - 3b1b speaks its questions and key sentences. When text does go up it is a
     short title-like line ("Puzzle: …", "Why the layers?", "Hypothesis: …") or a
     label, and it doesn't fly to a parking slot.
   - The band system (TITLE / KEY / PANEL_LABEL / BOTTOM rows) is a slide grid;
     3b1b's text is attached to objects. 44–65% of OCR'd text boxes sit in the
     middle half of the frame, and the bottom quarter holds only 12–22% (§6).
5. **`safe_text` shrinks text to fit.** It produces uneven type sizes (the skill
   already patched one symptom with `safe_multiline`). 3b1b picks a size and
   hand-breaks lines at ~30 characters. Nothing shrinks silently.
6. **Tone split.** The skill makes definitions and formulas "documentary (clear,
   steady, fewer flourishes)". 3b1b keeps one conversational voice throughout:
   contractions at 17–25 per 1k words in every video, and the formula reveal is
   "this, my friends, is Bayes' theorem". Steady, yes; register change, no.
7. **"Every spoken change has a visible one", enforced mechanically.** The
   principle matches 3b1b, but it is enforced by a lint over verbs and adjectives
   plus a timeline audit. That pushes toward a motion for every word and toward
   token pulses. 3b1b's alignment is at the level of the idea per shot, cut in the
   editor, with stills allowed. Measured motion onsets sit only loosely on
   phrase starts (§7).
   - The skill's "see then hear" rule (start the visual 0.3–0.5 s *before* the
     label, Motion 6) is the opposite of the measured 3b1b tendency: when onsets
     are near a phrase start, the picture follows by 0.0–0.3 s.

**Highest-leverage changes, in order**
1. Install and pin CMU Serif for `Text`, and define the ManimGL hex palette
   explicitly.
2. A backstroke on every label, and `next_to`-attached labels in place of bands.
3. A per-video concept→colour map shared by text, `MathTex` and figures.
4. Drop idle breathing; allow holds.
5. A 3b1b pacing profile for TTS (rate and pause budget).
6. Scene-per-beat rendering.
7. A mascot plus objection beats in the script template.
