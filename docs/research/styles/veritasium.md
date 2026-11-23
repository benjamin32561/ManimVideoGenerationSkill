# Veritasium — style study (phase 1)

Research date: 2026-11-21. Scope: how Veritasium goes from idea to finished video, and what
the words, pictures and motion look like, with the problem → wall → revelation cycle made
explicit. Render engines are out of scope.

**How to read the tags.** `[verified: X]` means I read it in source X, listed in §10.
`[inferred: …]` is my reasoning from the evidence named. `[measured: …]` is a number from my
own scripts over the sample (method in §10). Anything not found says so.

**Sample (8 videos, 2012–2026).** All on youtube.com/@veritasium. Two of the three
recent videos are fronted by presenters other than Derek Muller (credits in each
description). Same list in `research_cache/veritasium/SAMPLE.md`.

| ID | Video | Date | Length | Presenter(s) | Format |
|---|---|---|---|---|---|
| V1 | [Where Do Trees Get Their Mass?](https://www.youtube.com/watch?v=2KZb2_vcNTg) | 2012-03-12 | 4:10 | Derek Muller | Street interviews, then the answer |
| V2 | [The Bayesian Trap](https://www.youtube.com/watch?v=R13BD8qKeTg) | 2017-04-05 | 10:36 | Derek | Derek to camera + animation |
| V3 | [This equation will change how you see the world (the logistic map)](https://www.youtube.com/watch?v=ovJcsL7vyrk) | 2020-01-29 | 18:39 | Derek | Math explainer, coded visuals |
| V4 | [Math's Fundamental Flaw](https://www.youtube.com/watch?v=HeQX2HjkcNo) | 2021-05-22 | 33:59 | Derek | History-of-math documentary |
| V5 | [The Most Misunderstood Concept in Physics](https://www.youtube.com/watch?v=DxL2HoqLbyA) | 2023-07-01 | 27:14 | Derek | Physics documentary (entropy) |
| V6 | [The Strange Math That Predicts (Almost) Anything](https://www.youtube.com/watch?v=KZeIEiBrT_w) | 2025-07-25 | 32:32 | Derek + Casper Mebius (alternating narration) | Math history (Markov chains) |
| V7 | [Randomness is a lie. Let me explain](https://www.youtube.com/watch?v=uXuQF_PPg5U) (also served as "The Simplest Math Problem No Computer Can Solve") | 2026-11-18 | 38:48 | Gregor Čavlović | Math/CS investigation |
| V8 | [Relativity is so much weirder than we thought...](https://www.youtube.com/watch?v=eyZEqSPeMwg) | 2026-10-23 | 34:27 | Gregor Čavlović + Emilia Gyles | Lab/field experiment documentary |

Process sources include two of the channel's own videos: *Khan Academy and the
Effectiveness of Science Videos* (2011, `eVtCO84MDj8`, Derek summarising his PhD) and
*The Future of Veritasium* (2025-12-24, `piHGnG4LsmQ`, how the team was built).

---

## 1. Snapshot

- **Who.** Derek Muller started Veritasium in 2011 after a physics-education PhD
  (Sydney, 2008). For most of its life he did "all the research, writing, filming,
  and editing myself. Even the crappy animations" [verified: P2 5:21]. In 2017 he put
  it at "about 98 percent of the work" [verified: W1]. Electrify Video Partners bought
  part of the business in April 2023 and took over hiring and production [verified:
  P2 9:17–10:41; W3]. There are now "over 30 people working on Veritasium, writer,
  directors, researchers, illustrators, animators, editors, and production staff"
  [verified: P2 12:07].
- **Other presenters now front videos (verified).**
  - Derek is stepping back: "in some upcoming videos, I will not appear at all, even
    if I'm guiding things in the background" [verified: P2 16:07].
  - V7 credits "Presenter - Gregor Čavlović"; V8 credits "Presenters: Gregor
    Čavlović and Emilia Gyles"; V6 (2025) is co-narrated by Derek and Casper Mebius,
    with the caption track labelling alternate lines [Derek] / [Casper] [verified:
    descriptions, caption tags].
  - Each video now has its own writer/director (e.g. Kaela Albert on V6, Emilia
    Gyles and Daniel Leonard on V7, Sarah Houlton on V8) [verified: descriptions].
- **Topics.** Physics, math, engineering, and more and more investigative history
  and exposés (PFAS, Monsanto, GPS jamming, Enigma) [verified: channel listing;
  P2 12:22]. A sister channel, InGenius, launched 2026-09-30 for social-science
  stories that "don't fully belong on Veritasium" [verified: P3].
- **Audience and mission.** "I want to increase the level of critical thinking in
  the world" [verified: P2 3:09]. Every video carries an undercurrent: "how do we know
  what's true, how would we know if we were wrong" [verified: P2 3:01; same idea in W2].
- **Length.** The sampled videos grow from 4 min (2012) to 33–39 min (2021–26). Derek
  says length "has continued to increase", a trend that "began before Electrify"
  [verified: P2 11:57]. Channel-wide, over the 454 uploads on the Videos tab
  (approximate upload dates from YouTube's "x ago" labels) [measured: yt-dlp flat
  listing]:

  | Era | Uploads | Median length | Middle half | Share > 20 min |
  |---|---|---|---|---|
  | 2011–13 | 140 | 3.5 min | 2.6–4.8 | 0% |
  | 2014–16 | 64 | 6.9 min | 4.8–8.2 | 0% |
  | 2017–19 | 73 | 9.0 min | 6.3–12.1 | 1% |
  | 2020–22 | 61 | 18.1 min | 13.5–20.7 | 28% |
  | 2023–24 | 54 | 24.3 min | 18.7–31.6 | 69% |
  | 2025–26 | 60 | 32.8 min | 25.1–39.7 | 95% |

  Uploads per year have stayed at 16–32 since 2014 [measured], consistent with
  Derek's "the number of main channel videos has remained basically constant"
  [verified: P2 11:45]. V7 has carried at least three titles since upload [verified:
  RSS, two listings].
- **Reach.** 21.5 M subscribers on 2026-11-21 [measured: yt-dlp metadata]. The
  sample's views run from 2.5 M (V1) to 31.7 M (V5) [measured].
- **Money.** A sponsor read in most long-form videos (Brilliant, NordVPN, Hostinger,
  Audible), plus Patreon, the Snatoms kit and an *Elements of Truth* board game
  [verified: descriptions; P2 14:21]. Sponsor reads take 1.3–2.2 min per sampled
  video [measured: SponsorBlock segments].

## 2. Production pipeline & tools

**Two eras.** Up to about 2020 Derek did nearly everything himself. From 2021 a small
team formed, and since 2023 the channel has run as a studio with one writer/director
per video [verified: P2 6:08–8:13, 12:07–12:58].

| Stage | What happens | Tools / people | Evidence |
|---|---|---|---|
| Idea | Early on, topics were misconceptions he knew from teaching, then books, conversations, viewer comments. Now pitched in team pitch meetings, with the test "will this make people change the way they view the world?" | Derek; now writer/directors pitch | [verified: W1; P3 0:07; W4] |
| Research | The writer/director goes "extremely deep in research to trace stories back to scientific papers and original sources". Dedicated researchers since ~2025; experts consulted on every video. | Researchers (2–3 credited per video in 2025–26), outside experts (10 thanked on V6) | [verified: W5; V6–V8 credits; P2 14:44] |
| Script | Written and rewritten by the writer/director, often with Derek as co-writer. V3 went through "many earlier iterations (including parts she filmed that were replaced)"; V4 had expert "reviews of earlier drafts" and "specific rewrites". V7 credits a separate "Script Consultant". | Writer/directors; Derek; script consultant | [verified: W5; V3, V4, V7 descriptions] |
| Storyboard | Storyboards and shot lists are part of the writer/director role. A team member in P2 (speaker not named in the captions): "The way our videos are storyboarded now, it's so professional. It's like a movie studio." | Writer/director; illustrators | [verified: W5; P2 13:24] |
| Fact check | "All our facts are checked internally, and we also use multiple experts with every video." V6 credits a named fact-checker. Legal review for exposés. | Fact-checker, experts, legal team | [verified: P2 13:32–13:45, 14:44; V6 description] |
| Filming | Presenter on location, lab visits, interviews with researchers, street interviews (early), demos. In 2017 a Panasonic GH5 with a 7 mm lens for "selfie-style" shots, a Zhiyun Crane gimbal, Sennheiser wireless lavs, GoPros for alternate angles. Now camera operators and outside crews are credited. | Presenter, camera operators | [verified: W1; V5–V8 credits] |
| Animation | Through ~2019, simple animations by Derek in Final Cut Pro; "if you see good animations they were made by someone else in a different piece of software probably after effects". V3's visuals were Python (PyQt5/pyqtgraph, vispy, numba) by Jonny Hyman. Since 2021, two to six animators per video, plus illustrators; the two main animators were hired through cold emails. "That was drawn by hand by a person and animated by a person too", "it's not AI". | Final Cut Pro X (Derek); After Effects (hedged by Derek); Python for V3; animators + illustrators | [verified: W6; C1 repo; P2 7:22, 13:15; credits] |
| Edit | Derek edited everything at first ("I am perhaps the slowest editor you will ever meet") and was "still editing about half of the videos" in 2021; V4 credits "Editors: Derek Muller". Now a lead editor plus additional editors per video. | Final Cut Pro X (Derek); a team now. The current editors' software is not documented. | [verified: P2 5:51, 8:30; W6; credits] |
| Music & SFX | Epidemic Sound library tracks, plus original music and SFX by Jonny Hyman. | Epidemic Sound, Artlist (V3), Jonny Hyman | [verified: descriptions V2–V6] |
| Review | Early versions go to Patreon supporters "who graciously help us catch mistakes". V3 had feedback from Henry Reich (minutephysics), Dianna Cowern and others on earlier cuts. | Patreon, peer creators | [verified: P2 14:53; V3 description] |
| Packaging | Thumbnails by dedicated designers (2–4 credited per video in 2025–26). V7 has carried at least three titles. | Thumbnail designers | [verified: credits; RSS vs. listing titles] |

**How long a video takes.** Not found in a primary source. What is documented: in
2011–13 Derek worked "40 to 50 hours per week" on the channel [verified: P2 0:24];
by 2021 he was pulling all-nighters to launch by 6 AM [verified: P2 8:42]; the number
of main-channel videos "has remained basically constant" while length grew [verified:
P2 11:45]. From the RSS feed, main-channel long-form uploads in Oct–Nov 2026 come
roughly weekly, with one writer/director per video, so each video has a parallel
team [inferred: RSS + credits]. A per-video duration of several months is likely but
not stated anywhere I could find [inferred].

**Team growth in the credits** [measured: names in each description's credit block,
approximate]: V4 (2021) 10 people, V5 (2023) 12, V6 (2025) 22, V7 (2026) 32. Writers
went from Derek alone, to Derek plus one or two co-writers (2021–25), to videos where
Derek is only an executive producer (V7, V8).

**The research behind the method (Muller's PhD).** The thesis tested physics videos
on 1,000+ students [verified: W7 abstract; W8]:

- A clear "Exposition" (lecture-style, correct information only, with "graphs, force
  diagrams, animations, and live action demonstrations, along with 'talking head'
  narration") was rated "clear", "simple" and "concise", and produced little learning:
  6.0 → 6.3 out of 26 in one study [verified: T p.170, p.199; P1].
- Students watching it "felt the material was review and therefore didn't pay full
  attention" [verified: T p.32]. Confidence rose anyway [verified: T p.30; P1].
- Versions that raised the common misconceptions and then refuted them produced
  much larger gains: effect sizes d = .83 (Dialogue) and d = .79 (Refutation) against
  the Exposition [verified: T p.174]. In P1 the post-test average "nearly doubled to
  11 out of 26" [verified]. Students rated their mental effort higher and called the
  video "confusing" [verified: T p.199; P1].
- **The dialogue format is not what made it work.** The Refutation had a single
  lecture-style speaker who stated each misconception and refuted it. "As both
  Refutation and Dialogue treatments produced similar effect sizes, it seems that both
  methods … are equally effective in non-interactive multimedia" [verified: T p.177].
  This matters for Ben: the misconception-first effect does not need a second
  character.
- Derek's summary: present correct information alone and "students think they know
  it", "don't pay their utmost attention", don't notice the difference from what they
  already think, "don't learn a thing" and "get more confident in the ideas they were
  thinking before" [verified: P1]. "With the veritasium films I always try to start
  with the misconceptions" [verified: P1].
- Two later framings by Derek: "You have to make the video in a way that engages with
  people's prior knowledge, which includes talking about misconceptions. Or you need
  to give people an interesting conundrum, or an interesting problem or question"
  [verified: W1, 2017]. And: "If you don't tap in to them, it's easy for people to watch
  a video and think they're understanding it but it's really just reinforcing what they
  thought beforehand" [verified: W2, 2024].

What is not found: number of script drafts per video, the animators' software in
2021–26, whether narration is recorded before or after the edit, and the time from
pitch to upload.

## 3. Script writing process & structure

### How scripts get made

- **Start from what the viewer already believes.** "With the veritasium films I always
  try to start with the misconceptions" [verified: P1, 2011]. Later he widened it to "an
  interesting conundrum, or an interesting problem or question" [verified: W1, 2017].
  The team's test for a story is whether it will make people "change the way they view
  the world" [verified: W4].
- **Research goes to primary sources.** The writer/director role is to go "extremely
  deep in research to trace stories back to scientific papers and original sources" and
  to "ensure that scripts align with the visual direction of the videos" [verified: W5].
  Description reference lists of 10–20 papers and books (V3, V4, V5) and named experts
  (V4 "consultation on set theory and specific rewrites"; V6 thanks ten) back this
  [verified: descriptions].
- **Drafts are iterated and reviewed outside the team.** V3 thanks four people for
  feedback on "earlier versions", including one who said "earlier versions weren't
  good"; V4 thanks a professor "for reviews of earlier drafts" [verified: V3, V4
  descriptions]. Patreon supporters see early versions [verified: P2 14:53]. V7 credits
  a "Script Consultant" [verified].
- **Derek's role now is the editor's eye.** Casper Mebius: in meetings Derek listens,
  "Then he just makes one comment, and it's like he's throwing a dart and hitting the
  bull's-eye" [verified: W4]. Derek says he is "guiding things in the background"
  [verified: P2 16:10].
- **Watch time shaped the form** (a journalist's reading, not Derek's): YouTube's 2012
  move to reward watch time "encouraged Muller to develop longer videos in which he
  layered demonstrations, expert cameos, and slow-burn narrative reveals" [verified: W4].
- Not found: the number of drafts per video, whether scripts are written to a template,
  and how the narration is timed against the edit.

### The narrative cycle, made explicit

Ben's description fits the channel well: a short hook, then dig into the problem, hit a
wall, get a revelation, and go again. Below is what that looks like when measured. I
coded every **wall** (the narration states an obstacle, a contradiction or a failed
expectation) and every **revelation** (the narration states the resolution) from the
cue-level transcripts, then measured the spacing [measured: `cycle_stats.py` over my
hand coding; sponsor time removed].

| | V1 2012 | V2 2017 | V3 2020 | V4 2021 | V5 2023 | V6 2025 | V7 2026 | V8 2026 |
|---|---|---|---|---|---|---|---|---|
| Walls | 3 | 3 | 6 | 8 | 9 | 9 | 13 | 14 |
| First wall | 0:32 | 0:31 | 4:07 | 2:34 | 1:39 | 3:37 | 1:27 | 0:37 |
| Median gap between walls | 1.1 min | 3.4 | 1.0 | 3.4 | 2.0 | 2.5 | 2.2 | 1.9 |
| Wall → next revelation (median) | 0.6 min | 1.1 | 0.5 | 3.8 | 0.5 | 0.6 | 1.3 | 1.7 |
| Cycle grammar | guess → refute | puzzle → formula → twist | surprise chain | ledger (Hilbert's 3 questions) | chained why | ledger (4 opening questions) | ledger (3 problems) | ledger (3 challenges) |

So in the long-form era a wall arrives every **2–3.4 minutes**, and most are resolved
within **about a minute** (V4 is slower because each answer needs a full proof). That
is about 9–14 cycles in a 30-minute video.

**Three cycle grammars** [inferred: from the coding above and the transcripts]

1. **Guess → refute** (classic, V1). Each interviewee's guess is a wall that the
   narration knocks down with evidence. In V1 that goes soil, refuted by van Helmont's
   pot at 1:05, then water, then sunlight ("the energy is not matter", 2:39), and lands
   on air ("95% of a tree is actually from carbon dioxide", 3:09). The real people
   carry the misconception; no actor plays a student.
2. **Chained why** (V5, V3). Each revelation produces the next question, usually in
   the form "So if [what we just learned], then how [fact about the world]?". In V5:
   energy in equals energy out (1:39) → "Then what are we really getting from the
   sun?" → Carnot → efficiency is capped (6:26) → why does energy spread out, if
   physics runs both ways (11:19) → a snapshot shows heat flowing cold to hot (12:36)
   → Boltzmann: "not impossible, it's just improbable" (12:57) → then how is there any
   structure, "How does life exist?" (16:01) → the sun gives low entropy (16:28),
   which answers the opening question → "but then where did the sun get its low
   entropy?" (19:15) → the early universe looks uniform, "So how is this low entropy?"
   (20:05) → gravity (20:09) → and so on to black holes and the arrow of time.
3. **The ledger** (V4, V6, V7, V8; every long video since 2021 except V5). Early on,
   the video announces a numbered list of questions or obstacles. Each section then
   takes one item, and inside each item small wall → fix cycles run. Closing an item
   is said out loud.
   - V4 13:36: Hilbert's "three big questions": complete, consistent, decidable. They
     are answered no (Gödel, 14:48–21:28), no (second theorem), no (Turing, 26:47).
   - V6 0:00: four questions open the video (shuffling, uranium, next word, Google).
     They are answered in a different order, and the first one asked is answered last
     ("seven", 30:11), so it doubles as the callback.
   - V7 9:50: "three major challenges. One, sequences could get stuck in these short
     loops." Closed one by one: "at least that was one problem dealt with" (14:00), "So
     that is problem two dealt with" (15:32), "it solves our third problem,
     predictability" (25:46). The problems are also physical brass plaques on the set
     (LOOPS, PATTERNS, PREDICTABILITY). A plaque is gone from the table once its
     problem is solved (15:30) and all three come back for the review (17:40)
     [verified: frames].
   - V8 2:19: "three massive challenges": a clock accurate to 18 decimal places, taking
     it out of the lab, and reading a signal faster than electronics can count. They
     are shown as chapter cards ("The Clock / The Climb / The Count", 2:30). Inside them
     the sub-walls are announced as "another challenge" (6:17), "a different problem"
     (8:55), "a whole new problem" (18:50) and "one final problem" (25:12).
   - After the ledger is cleared, the video goes past it: V7's "But where did that
     secret key actually come from?" (25:50) and "So does that mean the problem is
     solved? Not exactly." (26:21) start a new, deeper cycle (physical and quantum
     randomness).

**Anatomy of a wall** [verified: transcripts and frames; the pattern is inferred]

- *In words.* The wall is set up by first stating the expectation, then breaking it:
  - "Since it's fully reversible, you might expect the efficiency to be 100%, but
    that is not the case." (V5 6:26)
  - "Looking at these numbers, there's no obvious pattern, but watch what happens if
    I keep going." (V7 7:35)
  - "So far, so good. But now comes the weird part." (V3 4:07)
  - "But a long sequence doesn't necessarily mean a good one." (V7 14:03)
  - "But wait, they're using random numbers to choose the measurements in an
    experiment that is designed to generate random numbers. It doesn't make sense."
    (V7 30:37)
  - The consequence-question: "So if the natural tendency of energy is to spread out
    … then how is it possible to have something like air conditioning…?" (V5 14:30)
- *In pictures.* The model that was just built is run until it visibly fails:
  - the middle-square column turns yellow on the repeating values 4100, 8100, 6100,
    2100 (V7 7:40–8:00);
  - a 3-D point cloud is rotated until RANDU's 15 planes appear (V7 14:24);
  - the energy-packet counter flips to 9 | 1 (V5 12:40) [verified: frames].
  - Revelations get the mirror move: the chart or model is extended until the answer
    is visible, as when V5's entropy bar chart rescales until the black-hole bar
    dwarfs everything else (23:00).
- *Who holds the wrong idea.* Real people do: street interviewees (V1, V5),
  historical figures (Nekrasov in V6, Hilbert in V4, Bekenstein's critics in V5), or
  the narrator's own reasonable expectation ("you might expect"). None of the eight
  uses a scripted naive character.

**Anatomy of a revelation**

- Usually a named person "realized", "had a flash of insight" or a "sudden
  revelation": Ulam (V6 12:15, 12:44; V7 3:39), von Neumann (V6 13:25), Boltzmann (V5
  12:57), Brin and Page (V6 20:29), Hänsch (V8 28:32). History is the way an idea
  arrives [verified: transcripts].
- It is first said in one plain sentence, then shown on a toy, then scaled up:
  - "Heat flowing from cold to hot is not impossible, it's just improbable." Then
    exact counts for an 8-atom toy (91,520 vs 627,264 configurations), then 80 atoms
    (0.05%), then "100 trillion, trillion atoms" (V5 12:57–13:59).
  - PageRank on a "toy internet with just four webpages", Amy, Ben, Chris and Dan (V6
    20:40).
- A short plain analogy often follows: Rubik's cube (V5 13:59), library stamps (V6
  19:48), Robin Hood's arrows (V7 29:10), a marble in a bowl (V8 12:01), tuning forks
  (V8 26:28).
- The payoff goes back to whoever held the misconception. In V5 the street
  interviewees reappear to hear the answer ("Oh wow, I did not know that", 17:05),
  and V6 returns to the opening shuffle question with people guessing (29:41)
  [verified].

**How one revelation becomes the next question.** The hand-off sentence starts with
"But" or "So" and takes the new result as its premise:

- "But then where did the sun get its low entropy?" (V5 19:15)
- "But in this chain, the transition probabilities aren't fixed…" (V6 14:05)
- "But Bernoulli only proved that it worked for independent events" (V6 2:36)
- "But there's one question we still haven't answered." (V6 29:41)

Sentence-initial "But" makes up 4–11% of sentences in V2–V8, and "So" 11–19% (§4).

### Openings

- **Classic (2011–17):** a direct question to the viewer or to people on the street
  within the first 10 s ("where do they get that matter to grow?", V1; "Picture this:
  You wake up one morning…", V2) [verified].
- **Long-form (2020–26):** a concrete scene or claim, then the question, then a one-line
  scope statement, all within 0:30–1:45:
  - V7: casino winners → "So are those numbers actually random?" (1:27) → "This is a
    video about the near impossibility of creating true randomness." (1:42)
  - V5: "This is a video about one of the most important, yet least understood concepts
    in all of physics." (0:00)
  - V4: "There is a hole at the bottom of math" (0:00)
  - V6: four questions, then "a strange math feud in Russia" (0:19)
  - V8: the mountain clock experiment (0:00) → "So why are we still testing it?" (1:15)
- "This is a video about …" opens or frames the scope in V5 and V7 [verified]. Then
  the turn to history: "To answer that, we have to go back to a discovery made two
  centuries ago." (V5 2:09); "we have to go back 150 years to a full-blown revolt in
  mathematics" (V4 3:36).

### History, people and on-camera experts

- History is the engine of the middle in V4–V7. Each new idea arrives with a dated
  scene and a person, often dramatised through illustrated reenactment (Carnot in V5,
  Ulam in hospital in V6 and V7).
- Experts appear as evidence, not as foils. They are interviewed in their labs or over
  video call, and their lines carry the facts or the stakes ("The way we know there is
  some contradiction…", V8 1:22) [verified: transcripts, frames].
- **The dialogue question (Ben's dislike).** Veritasium has no scripted
  teacher–student dialogue in the sample. Three nearby devices exist:
  - V6 alternates two narrators line by line ([Derek] / [Casper]), and they share
    one voice of exposition;
  - presenters chat with experts on location (V7, V8);
  - early videos rely on street interviews.

  The PhD result above says the refutation itself does the work, not the second
  speaker (§2), so a single narrator who states and refutes the misconception is
  enough.

### Humour and tone

Light and situational: "I guess they felt there were too many rabbits out there" (V3
12:35), *The Office* Jim-is-my-enemy loop as an analogy for self-reference (V4 20:55),
a Minecraft creeper exploding mid-sentence ("Occupational hazard", V7 15:39).
Moments of personal wonder close sections: "how did I get to be 37 years old without
hearing of the Feigenbaum constant?" (V3 17:01) [verified].

### Endings

- **Return to the opening line or scene** with the meaning changed. V4 repeats "There is
  a hole at the bottom of math" (32:07), followed by "instead thinking about this
  problem transformed the concept of infinity, changed the course of a world war and led
  directly to the invention of the device you're watching this on right now". V7 returns
  to von Neumann's "state of sin" paper for the extraction trick (34:53).
- **A turn to the viewer's life**: V2's "experimentation is essential" (8:53); V5's "let's
  make use of the low entropy we've got while we can" (25:30).
- **Open result**: V8 ends with the data still being analysed ("Is Einstein still
  right? … yes … we're still analyzing the data", 32:07).
- **A last surprise**: V6's "It's actually over 2,000" shuffles (31:16); V1's "in a
  sense you're becoming the tree" (3:40).
- No recap lists. The sponsor read sits at the end (V4, V5, V6) or mid-video at a
  section break (V7 18:45, V8 14:26), and is bridged back in with "now back to the
  casino" / "now back to you, Gregor" [verified].

## 4. Language profile

Same definitions as `styles/3blue1brown.md` §4. Text and punctuation come from the
creator's manual `en` track. Word timing comes from YouTube's auto track (`en-orig`),
and pauses from the audio track. Sponsor segments are removed (SponsorBlock)
[measured: `lang_metrics.py`, `pauses_audio.py`, `lang_markers.py`].

**Caveat.** All speech is counted, including street interviewees (most of V1) and
on-camera experts (V5–V8), as in the 3b1b method. V4's manual track has almost no
sentence punctuation, so its sentence rows (†) use a punctuation-restoring model. On V5
that model gives 19.5-word sentences against 18.1 on the manual text, so it runs about
8% long.

| | V1 | V2 | V3 | V4 | V5 | V6 | V7 | V8 |
|---|---|---|---|---|---|---|---|---|
| Year | 2012 | 2017 | 2020 | 2021 | 2023 | 2025 | 2026 | 2026 |
| Presenter | Derek | Derek | Derek | Derek | Derek | Derek + Casper | Gregor | Gregor + Emilia |
| Words (ASR, excl. sponsor) | 741 | 1,632 | 2,571 | 4,876 | 3,876 | 5,161 | 6,189 | 5,916 |
| WPM, whole video | 180 | 177 | 149 | 149 | 151 | 166 | 169 | 183 |
| WPM, excl. pauses ≥ 0.5 s | 226 | 210 | 202 | 194 | 198 | 206 | 208 | 221 |
| ASR gaps ≥ 1 s / min | 2.98 | 0.33* | 3.67 | 3.31 | 3.89 | 3.05 | 3.20 | 2.81 |
| Audio pauses ≥ 1 s / min | 0.24 | 0.54 | 0.29 | 1.16 | 0.86 | 0.74 | 0.66 | 0.59 |
| Audio pauses ≥ 2 s (count) | 0 | 1 | 1 | 7 | 5 | 0 | 1 | 3 |
| Silence share (gaps ≥ 0.3 s) | 6% | 12% | 8% | 14% | 8% | 6% | 8% | 6% |
| Median pause (≥ 0.3 s) | 0.49 s | 0.42 | 0.44 | 0.50 | 0.50 | 0.44 | 0.42 | 0.44 |
| 90th-pct pause | 0.85 s | 0.75 | 0.75 | 0.94 | 1.05 | 1.02 | 0.88 | 0.92 |
| Mean sentence (words) | 9.7 | 30.1‡ | 17.1 | 17.9† | 14.7 | 16.9 | 15.0 | 16.4 |
| Median sentence | 6 | 22‡ | 14 | 16† | 13 | 16 | 14 | 15 |
| Sentences > 30 words | 3% | 35%‡ | 13% | 12%† | 6% | 8% | 5% | 10% |
| Sentences ≤ 8 words | 62% | 15% | 19% | 17%† | 30% | 18% | 26% | 30% |
| Questions / min | 4.63 | 0.32 | 0.70 | 0.64† | 0.97 | 1.00 | 0.46 | 0.83 |
| Questions, % of sentences | 26% | 6% | 8% | 8%† | 9% | 10% | 4% | 8% |
| Flesch–Kincaid grade | 4.7 | 12.8‡ | 8.6 | 8.8† | 7.6 | 7.6 | 7.9 | 7.9 |
| "I/me/my" per 1k words | 18.4 | 4.9 | 11.7 | 2.2 | 5.6 | 6.8 | 8.2 | 5.4 |
| "we/us/let's" per 1k | 4.3 | 19.7 | 13.2 | 11.2 | 11.3 | 7.4 | 12.6 | 18.8 |
| "you/your" per 1k | 17.0 | 31.3 | 21.0 | 11.0 | 5.9 | 16.1 | 13.0 | 14.1 |
| Contractions per 1k | 38.3 | 28.9 | 19.9 | 11.2 | 14.6 | 17.3 | 22.1 | 26.7 |
| Sentences opening with and/but/so/or/now/then | 8% | 39% | 45% | 27%† | 27% | 39% | 39% | 37% |
| "but" ÷ "and" (×100) | 35 | 20 | 21 | 30 | 31 | 38 | 32 | 23 |

\* V2's auto track has unusually even word timing, so its ASR gap figure is not
comparable. ‡ V2's manual punctuation joins clauses with commas ("…tested positive
for a very rare disease that affects about 0.1% of the population and it's a nasty
disease, horrible consequences, you don't want it."), which inflates sentence length
and grade. Audio pauses use the 3b1b threshold (18 dB under the 70th-percentile frame).
Veritasium keeps music under almost all narration, so pause counts are lower bounds.

**Markers** (per 1,000 words, except the sentence-initial rows, which are % of
sentences) [measured: `lang_markers.py`]

| Marker | V1 | V2 | V3 | V4 | V5 | V6 | V7 | V8 |
|---|---|---|---|---|---|---|---|---|
| "So …" (sentence-initial %) | 3 | 15 | 14 | 11 | 12 | 13 | 17 | 19 |
| "But …" (sentence-initial %) | 0 | 7 | 4 | 8 | 6 | 11 | 5 | 5 |
| "And …" (sentence-initial %) | 1 | 6 | 21 | 3 | 5 | 11 | 13 | 10 |
| this / these / here (pointing) | 7 | 9 | 26 | 16 | 12 | 16 | 19 | 19 |
| digit tokens | 6 | 15 | 15 | 10 | 11 | 15 | 12 | 8 |
| years (1500–2029) | 1.4 | 0 | 0.4 | 2.6 | 0.8 | 1.9 | 1.0 | 0.9 |
| "problem / challenge" | 0 | 0 | 0.4 | 3.4 | 0.5 | 1.5 | 1.5 | 1.9 |
| naming ("called / known as") | 0 | 0 | 1.2 | 0.8 | 0.5 | 1.0 | 1.1 | 0.7 |
| "actually" | 2.8 | 8.6 | 2.3 | 0.8 | 0.3 | 0.8 | 4.2 | 2.1 |
| hedges (kind of, sort of, I think, maybe, probably) | 1.4 | 9.2 | 0.8 | 0.4 | 0.5 | 1.5 | 3.1 | 3.7 |
| "in other words" | 0 | 0 | 0 | 0 | 0.3 | 0.6 | 0.2 | 0.2 |

**What the numbers say**

1. **Short spoken sentences.** Mean 15–17 words and median 13–16 in the long-form
   era, with only 5–13% over 30 words. That is much shorter than 3b1b (mean 23–31) or
   Welch Labs (22). The reading grade is about 8 against their 11–14. The script is
   written for the ear: one fact per sentence, and short runs are normal ("He played a few rounds. He won some,
   lost some, and then he got up and walked away.", V7 0:07).
2. **Brisk, steady pace.** 149–183 WPM over the whole video and 194–226 while
   talking. The 2023 documentary pace (≈150) has sped up with the 2026 presenters
   (169–183) [measured].
3. **Questions carry the structure.** 0.5–1.0 questions a minute in long-form,
   higher than 3b1b (0–0.75) or Welch (0.19). Most are the wall and hand-off
   questions of §3: "So how is this low entropy?", "But how do you measure the
   quality of a webpage?", "So does that mean the problem is solved?" Street
   interviews raise the count in V1 (4.6/min) and V5.
4. **"But" and "So" are the hinges.** Sentence-initial "But" makes up 4–11% and "So"
   11–19%. "But" turns to the wall, and "So" draws the consequence.
5. **Person mix depends on format.** Documentary narration (V4, V5) talks about the
   story: "you" is only 6–11 per 1k and "I" 2–6. Presenter-led videos with on-camera
   demos use more "I" and "we" ("So I'm going to take a wheel with seven positions",
   V7 12:00), and V2 talks straight to the viewer (31 "you" per 1k).
6. **Plain register, contractions throughout** (11–29 per 1k, the 2026 presenters
   highest). Hedges are rare in narration and come mostly from on-camera speech.
7. **Pauses go after payoffs and before section turns** (as in 3b1b). V5's longest
   audio gaps: 3.2 s at 9:45, right after "Energy is most usable when it is
   concentrated and less usable when it's spread out" and before Clausius names
   entropy; 1.8 s at 14:48 between the Rubik's cube and the air-conditioner wall;
   2.1 s at 21:34 before Bekenstein. V4's cluster of 1.5–2.2 s pauses at 19:43–21:20
   sits on the Gödel card climax, and 2.2 s at 26:56 follows "mathematics is
   undecidable" [measured: audio RMS; matched to transcript].

**Recurring phrases** [measured: 3–4-grams in ≥ 5 of the 8 videos]: "and if you"
(7), "you need to", "to figure out", "a way to" (6 each), "you can see", "the same way",
"the number of", "and so on", "I don't know" (5 each). Characteristic sentence starts:
"This is …" (top-3 opener in V4, V5, V7, V8), "I mean …" (6 of 8 videos), "But then …"
(V6), "So the …" (V7, V8).

**Patterns with short examples** [verified: transcripts]

- *Expectation, then break:* "Now you might expect the equation to be chaotic from
  here on out, but as R increases, order returns." (V3 5:39)
- *Scope statement:* "This is a video about the near impossibility of creating true
  randomness." (V7 1:42)
- *Plain-language law:* "Heat flowing from cold to hot is not impossible, it's just
  improbable." (V5 12:57)
- *Concrete scale:* "a deck of 52 cards can be shuffled in 52 factorial ways, and that's
  about 8 times 10 to the power of 67 different arrangements." (V7 3:21)
- *Saying the ledger out loud:* "So that is problem two dealt with." (V7 15:32)
- *Personal stake:* "how did I get to be 37 years old without hearing of the
  Feigenbaum constant?" (V3 17:01)

## 5. Flow

Two beat sheets: V5 (Derek, 2023, the "chained why" grammar) and V7 (Gregor
Čavlović, 2026, the "ledger" grammar). Timestamps come from the cue-level manual
captions; pictures from frames every 5 s, read as 10-s contact sheets (±5 s).
**W** = wall, **R** = revelation, **→** = the hand-off question that opens the next
cycle. On-screen text is quoted as it appears.

### V5 — The Most Misunderstood Concept in Physics (2023-07-01, 27:14)

| Time | Cycle | Said | Shown | On-screen text |
|---|---|---|---|---|
| 0:00 | Hook | Scope: "one of the most important, yet least understood concepts in all of physics". Teaser list: storms, the universe's end, the direction of time, life. | The sun (SDO footage), light streaks, a crowd from above, Earth from orbit. | "What does the …" typed out in a serif font over Earth (0:30) |
| 0:31 | Misconception | Street interviews: "What does the Earth get from the sun?" "Energy." How much is radiated back? "Less", "70%", "20%". | Derek with a mic on a beach path, one interviewee at a time. | none |
| 1:39 | **W1** | "it should be exactly the same amount of energy in from the sun as earth radiates into space". → "Then what are we really getting from the sun?" (1:54) | Earth with a red arrow, back to the interviewees ("That's a good question"). | none |
| 2:09 | History | "To answer that, we have to go back to a discovery made two centuries ago." Napoleon, Sadi Carnot, French steam engines at 3% efficiency. | Painterly illustrated reenactment with parallax: a portrait, a quill letter, a chateau under attack, a young Carnot. | Script-font name over the portrait: "Lazare Carnot" |
| 4:08 | Build | The ideal heat engine, step by step: hot bar, expansion, cold bar, compression. It is fully reversible. | 3D-rendered cylinder, piston and flywheel on dark grey. Gas particles turn orange when hot and blue when cold. The hot bar is orange. | "Energy in the Engine" with a vertical meter filling green |
| 6:26 | **W2** | "you might expect the efficiency to be 100%, but that is not the case." | Derek at his desk, pointing at the same animation on his monitor. Then the formula. | E = Q_H − Q_C, with Q_H orange and Q_C blue |
| 7:13 | Build | Kelvin: absolute zero would give 100%. | Archival portrait, a cylinder stretched tall. | "Lord Kelvin" (script), "Absolute Zero" |
| 8:15 | **R1** | Efficiency depends "fundamentally on the temperatures of the hot and cold sides". Real engines reach 3%, not 32%, because energy spreads out. | The formula rewritten in three steps; old engine footage and patent drawings. | "Efficiency = (Q_H − Q_C)/Q_H" → "(T_H − T_C)/T_H" → "1 − T_C/T_H"; "293 K / 433 K = 32%" |
| 9:31 | **R2** | "this process is irreversible … Energy is most usable when it is concentrated". A 3.2 s pause follows. Clausius names entropy (9:58). | The flywheel engine glowing red at the base; Clausius's portrait. | "Rudolf Clausius", then the title card "Entropy" |
| 10:19 | Consolidate | The two laws; "energy spreads out over time"; "disorder" is the usual phrase, but "the tendency of energy to spread out" is better. | A starfield behind the text; montage of a Newton's cradle, shuffled cards, a grass fire, a water balloon. | "Laws of Thermodynamics / 1. The energy of the universe is constant." "Energy spreads out over time." |
| 11:19 | **W3** | "So why does energy spread out over time? … most of the laws of physics work exactly the same way forwards or backwards". | Toy model: two bars of 8 atoms each, with energy packets hopping. | Large yellow counts "7" and "3" beside the bars |
| 12:36 | **W4** | "So stop, look at this. Now there are nine energy packets in the left bar, and only one in the right … Shouldn't that be impossible?" | The counts flip to 9 and 1. | "9" "1" |
| 12:57 | **R3** | Boltzmann: "not impossible, it's just improbable". 91,520 configurations put 9 packets on the left, against 627,264 that split them 5 and 5, and there is a 10.5% chance the left bar ends up with more than it started. Scaled up: 0.05% at 80 atoms, effectively never at 10²⁶. | Bar charts with axis labels and the tail bars in red, braced "10.5%". The histogram narrows as the grid grows (70/30). | "Unique Configurations", "Energy Packets Left Solid", "10.5%", ".05%" |
| 13:59 | Analogy | Rubik's cube: one solved state, quintillions of messy ones. | Derek outdoors, turning a cube with his eyes closed. | none |
| 14:57 | **W5 → R** | "how is it possible to have something like air conditioning …?" Because entropy rises more at the power plant (15:20). A 1.8 s pause before the turn. | Stock footage chain: AC unit, suburb, power lines, a highway. | none |
| 15:40 | **W6** | "then how is there any structure left on earth? … How does life exist?" | A closed system decaying: bones, ice, ruins. | none |
| 16:17 | **R4** (answers W1) | "luckily, earth is not a closed system … What the sun really gives us is a steady stream of low entropy". Each photon in leaves as 20. | Earth from orbit, the sun. **The interviewees return** to hear it ("Oh wow, I did not know that", 17:05). A sun→Earth diagram with wiggly photons. | none |
| 18:06 | Extend | Life as an entropy accelerator; Jeremy England. | Jellyfish, hummingbird, sea surface, microbes. | A quote typed out in serif: "You start with a random clump of atoms, …" |
| 19:15 | **→ W7** | "but then where did the sun get its low entropy?" Answer: the past hypothesis (19:41). | Sun, then the Milky Way. | none |
| 20:05 | **W8 → R5** | The early universe was uniform: "So how is this low entropy?" "the thing we've left out is gravity" (20:09). | CMB map, then a white glow clumping into structure, a dam spillway (useful energy), colliding planets. | none |
| 21:00 | Data | Entropy budget: early universe 10⁸⁸ k_B, stars, interstellar medium, neutrinos, CMB photons. | Purple bar chart; each new bar is added and the axis rescales. | "Entropy (k_B)", category labels, values |
| 21:36 | **W9 → R6** | Bekenstein: black holes have entropy, so they should have a temperature. Physicists called it nonsense, and Hawking set out to prove him wrong, "But to his surprise" found Hawking radiation (22:17). A 2.1 s pause before this section. | Bekenstein's portrait, black-hole renders, the paper with a highlighted passage. | "Jacob Bekenstein", "dS = δQ/T" |
| 23:14 | Payoff | "almost all the entropy of the universe is tied up in black holes". The early universe had "0.000000000000003%" of today's entropy. | The bar chart rescales again: the Sagittarius A* bar, then all black holes, dwarf every earlier bar. | "Sagittarius A*", "Black Holes", the long decimal typed out |
| 24:09 | Consequence | Arrow of time, then heat death (24:26). | Asteroids, a planet, a black hole evaporating to red. | none |
| 24:52 | **Twist** | "So it sounds like entropy is this awful thing … But just because maximum entropy has low complexity does not mean that low entropy has maximum complexity." | Milk poured into tea, swirling patterns. | none |
| 25:30 | Close | "let's make use of the low entropy we've got while we can." Brilliant read follows. | Tea; sponsor screens. | Sponsor UI |

Shape: **a 2-minute hook, nine walls in 23 minutes, and the first wall's question
answered at the two-thirds point (16:28)**. The rest of the video follows the
follow-up question outward, from the sun to the Big Bang and black holes. Each section
change happens on a "So …?" or "But then …?" sentence.

### V7 — Randomness is a lie. Let me explain (2026-11-18, 38:48; presenter Gregor Čavlović)

| Time | Cycle | Said | Shown | On-screen text |
|---|---|---|---|---|
| 0:00 | Hook | A man films a slot machine, leaves, returns and wins spin after spin; $10,000 in an hour; ten casinos. | Cinematic reenactment in low warm light; a US map with three states lit; slot-machine internals; a hand hovering over the button. | Location card, lower left: "LUMIERE PLACE CASINO / JUNE 2ND 2014" |
| 1:10 | Question | The outcomes are "decided by a computer inside the machine … So are those numbers actually random?" (1:27) | First look at the **set**: Gregor at a green card table in front of a red curtain. Animated slot reels. | none |
| 1:30 | Scope | It connects Minecraft, nuclear weapons and digital security. "This is a video about the near impossibility of creating true randomness." (1:42) | Number tiles on green felt; a hopper-style "INPUT → OUTPUT" machine emitting numbers. | "INPUT", "OUTPUT", "486 065 819" |
| 1:50 | History | 1940s chance in a nuclear chain reaction; Los Alamos odds; Ulam. | Nucleus and neutrons animation; "1945" over a canyon road; illustrated period scenes. | "1945" |
| 2:58 | **W** | Ulam's encephalitis, solitaire, 52! ≈ 8×10⁶⁷ shuffles; he tried analytically "and he got nowhere" (3:37). | Illustrated hospital bed, hands dealing cards, Gregor dealing on the felt. | none |
| 3:39 | **R** | "But then he had a much simpler idea": play 100 games and count. The same idea works for neutrons, with dice deciding each collision (4:05). | Ulam's quote over the illustration; a grid of games; dice on the felt; labelled outcome icons. | "I WONDERED WHETHER A MORE PRACTICAL METHOD…", "WIN 8 OUT OF 100 / CHANCES OF WINNING ≈ 8%", "BOUNCE OFF / ABSORBED / SPLIT", "1) Use the probabilities for its new situation" |
| 5:03 | **W** | ENIAC can follow 100 neutrons, "But the ENIAC couldn't roll a die" (5:43) and had no memory for random-digit books. | Archival ENIAC footage; the RAND book. | "A MILLION Random Digits"; a two-line constraints list with icons |
| 5:59 | **R** | von Neumann's middle-square method, worked on seed 2137. | Gregor lays physical number cards on the felt, squares the seed and strikes the edge digits. | The cards themselves |
| 7:35 | **W** | "there's no obvious pattern, but watch what happens if I keep going." After 43 steps it is stuck in a loop: 4100, 8100, 6100, 2100. Every seed falls into one of eight traps (8:25). | A motion-graphic column of number tiles; the loop values light up yellow; a bar chart of the eight traps. | Number tiles, trap bars |
| 8:30 | Patch | 8-digit numbers, 2,000 checked by hand, restart from the seed; it works ("a 100% success"); named the Monte Carlo method (9:08). | Archival photos with quote cards; the casino photo on a journal page. | "THE RESULTS ARE VERY PROMISING AND…" |
| 9:30 | Name | "So they're called pseudorandom numbers". von Neumann: "in a state of sin". | Gregor at the table. | "Pseudo-random numbers" (lower centre) |
| 9:50 | **Ledger** | "three major challenges. One, sequences could get stuck in these short loops." Two, hidden patterns; three, predictability. | Engraved brass plaques laid on the felt. | "LOOPS", "PATTERNS" (and later "PREDICTABILITY") |
| 10:06 | Case | Matthew Bolan shows the Minecraft diamond trick: find clay, count three blocks, dig. "I got eight." | Webcam interview with a name card; gameplay with picture-in-picture faces. | "Matthew Bolan", game UI |
| 11:52 | Build | The linear congruential generator, shown with a 7-position wheel (multiply by 3, wrap around), then the formula and graph. | A physical paper wheel whose sectors fill yellow; a graph on felt green with parallel diagonals. | "new = a · current mod m", "LINEAR" |
| 13:53 | **✓1** | RANDU (IBM, 1960s, Skylab): half a billion numbers before repeating, "so at least that was one problem dealt with" (14:00). | Archival IBM and Skylab footage. | none |
| 14:03 | **W** | "But a long sequence doesn't necessarily mean a good one." Rotating the cube "in just the right way" shows 15 planes (14:30). | Gregor opens a laptop; a Desmos 3D point cloud rotates until the planes line up. | The RANDU formula |
| 14:56 | **✓2** | Java's LCG: the planes are "so closely packed" the points look random. "So that is problem two dealt with." (15:32) | A checklist with ticks appearing one at a time; plaques with LOOPS removed. | "1990s – JAVA", "ADDS CONSTANT / BETTER MULTIPLIER / LARGER MODULUS", "PATTERNS / PREDICTABILITY" |
| 15:39 | Explain | Why the Minecraft trick works: the seeds for diamonds and clay differ by a constant, so the unknown cancels. | Colour-coded math on felt green; the cancelling terms highlighted. | "Diamonds S + 60,009 / River clay S + 60,012", "C − D ≡ aΔ (mod m)" |
| 16:41 | **W** | "But there is a more fundamental problem": the outputs reveal 32 of 48 bits, so there are only 65,536 candidates, "and only one matches" (17:22). | Bit strings as boxes of X's; a candidate-state panel comparing observed and predicted outputs; then the full predicted future. All three plaques are back for the review (17:40). | "48 Binary Digits", "2¹⁶ = 65,536", "CANDIDATE INTERNAL STATE", "COMPARE", "RECOVERED INTERNAL STATE (48 BITS)" |
| 18:01 | Coda | Matthew's trick was patched in 1.18; Gregor crafts the diamond armour. | Patch-notes screenshot; game footage. | Changelog text |
| 18:45 | Sponsor | Hostinger, bridged in through the diamonds. | Product screens. | "AD" badge, bottom right |
| 19:47 | Back to hook | "now back to the casino": arrests, a hacker named Alex in St Petersburg, ex-Russian machines reverse-engineered. | Casino surveillance expert on video call; machine internals; reenactment. | Name card "DARRIN HOKE / CASINO SURVEILLANCE EXPERT" |
| 21:02 | Build | The Mersenne Twister: seed → a table of 624 → twist → outputs. | A diagram on felt green: digit tables, arrows, a box. | "SEED", "DIGIT SCRAMBLER", "Output 0 … Output 624" |
| 22:05 | **W → R** | They could predict the outputs, but human reaction takes a quarter second (22:27), so the app vibrates the phone a quarter second early (22:35). $250,000 a week; prison terms. | Reenactment close-ups of a hand and a phone; an article screenshot with a yellow highlight. | "sentenced to two years in federal prison" (highlighted) |
| 23:06 | Stakes | "all of these generators fail at being unpredictable if you know enough". Security needs more. | Keyboard close-up; NIST corridor. | "NIST – BOULDER, COLORADO" |
| 24:30 | **✓3** | Cryptographic generators: a counter fed through encryption with a secret key, 128 bits; "it solves our third problem, predictability" (25:46). | **The cold-open INPUT → OUTPUT machine returns**, now with a key dial. | "INPUT", "OUTPUT", "key", "128 BITS" |
| 25:50 | **→ W** | "But where did that secret key actually come from?" Hardware noise, Cloudflare's lava lamps. | A chip in fingers; an Intel block diagram. | Diagram labels |
| 26:21 | **W** | "So does that mean the problem is solved? Not exactly." A coin toss is deterministic; Laplace's demon. | A paper excerpt with a highlight; Laplace's portrait. | "naturally tossed coins obey the laws of mechanics" (highlighted), "PIERRE-SIMON LAPLACE" |
| 27:09 | **R** | Krister Shalm (NIST): randomness is what "nobody could have predicted in advance"; quantum measurement. | Lab tour with handheld camera; annotated optics. | "PATH OF THE LASER" |
| 27:50 | Build | Laser → crystal → an entangled photon pair in superposition. | Flat cut-paper graphics on green: a laser, a crystal, orange and purple photons with polarisation arrows, a "?". | "LASER", "POLARIZATION" |
| 29:10 | Analogy | "quantum archery": Robin Hood splitting two arrows at once into 10-micron fibres. | Target graphics. | "FIBER OPTIC CABLES ("TARGETS")" |
| 30:00 | **W → R** | Stations 110 m apart choose angles at random, "But wait, they're using random numbers to choose the measurements … It doesn't make sense." (30:37) Answer: "it takes randomness to make randomness" (30:49). | Alice/Bob boxes split by a dashed yellow line; detectors with angle bars; 0/1 chips. | "ALICE", "BOB", "110 M", "DETECTOR", "0", "1" |
| 31:13 | **R** | Bell inequality: the correlations exceed the classical limit. | A meter bar with "MATHEMATICAL LIMIT"; a card linking the channel's earlier Bell video. | "MATHEMATICAL LIMIT", "OBSERVED LIMIT" (34:20) |
| 32:09 | **W → R** | The freedom-of-choice loophole; David Kaiser's quasar-chosen measurements (32:48). | Video call; night sky; a diagram of two telescopes and the photon source. | "DAVID I. KAISER", "WILLIAM HERSCHEL TELESCOPE", "TELESCOPIO NAZIONALE GALILEO", "ENTANGLED PHOTON SOURCE" |
| 33:31 | **W** | "If I was a hacker, how would I attack the system?" NIST has to rest on stated assumptions. | Lab interview; then a list building one line at a time. | "NIST's randomness certification assumes: 1) … 4)" |
| 34:15 | **W → R** | Raw bits are uneven → von Neumann's coin trick "in the same 1951 paper as his 'state of sin' joke" (34:53) → extraction: 820 certified bits concentrated into 512 (35:31). | Coin graphics; the meter bars; 0/1 chips. | Bit chips |
| 35:59 | Payoff | "So this is the closest you can get to random." Einstein's dice; "God's dice are not loaded" (36:40). | Lab; Krister to camera. | none |
| 36:49 | Close | random.colorado.edu; choosing a sweater colour by entangled photons; "randomize the internet". Then the board-game ad and a blooper. | Lab; game box. | URL |

Shape: **a 1.5-minute hook that is left hanging; a ledger of three problems announced
at 9:50 and closed one by one (14:00, 15:32, 25:46); the hook paid off in the middle
(19:47–23:06); then a second act past the ledger, with five more walls on the way to
certified quantum randomness.** The opening machine diagram comes back at 24:40 with
one new part, the key, which is how the video shows that the earlier model has been
extended rather than replaced.

### Flow patterns across both [inferred: both beat sheets plus the other six cycle maps]

- **A visible state carries the argument.** V5's energy meter and entropy bar chart,
  V7's plaques and input/output machine. Each wall or revelation changes that state
  (a bar dwarfed, a plaque removed, a part added), so the viewer can see where the
  argument stands.
- **Model, run, break.** Every wall in both videos is shown by running the model just
  built until it fails (the loop lights up, the planes appear, the counts flip). The
  narration says "watch what happens" or "stop, look at this" one beat before.
- **Revelations arrive through a person and a date**, then get a one-sentence plain
  statement, then a toy with real numbers, then a scale-up.
- **Callbacks close loops.** V5 returns to the street interviewees; V7 returns to the
  casino at the midpoint and to von Neumann's 1951 paper at the end. Both close the
  opening question well before the end and then go one level deeper.
- **Section changes are spoken, not titled.** Apart from a few title words ("Entropy",
  "Absolute Zero", "1990s – JAVA"), new sections are opened by a question in the
  narration.

## 6. Visual system

**No house palette. Each video gets its own art direction, drawn from its story
world.** This is the main visual difference from 3b1b (one black stage and one palette
for ten years) and from Welch (one paper-and-desk world) [verified: contact sheets of
all 8; measured: the hue mix of saturated pixels changes video to video, e.g. felt
green is 15% of V7's colour pixels and under 3% in the others, `palette.py`].

| Video | Stage for explanations | Look of the graphics | Text style |
|---|---|---|---|
| V1 2012 | Street, handheld | None (interviews only) | None |
| V2 2017 | Derek walking on a hilltop, wide-angle selfie | Black background, hand-lettered equations in a comic font, H and E colour-coded, dot grids ("999 PEOPLE", "11 PEOPLE") | Handwritten caps |
| V3 2020 | Whiteboard outdoors; Derek at his computer; Derek in front of a projected Mandelbrot set | Screen-captured Python plots (dark grey, cyan dots): time series beside a bifurcation diagram; a 3D Mandelbrot | Plot labels, handwritten formula |
| V4 2021 | Hilltop at dusk; a wooden table with cards | Dark navy blueprint grid (Game of Life), a serif number table for Cantor, silhouette-crowd illustrations, Wang tiles, a flip chart | Serif, small caps |
| V5 2023 | Derek at his desk pointing at the animation on his monitor; outdoors with props | 3D-rendered engine on charcoal grey; LaTeX-style equations with hot = orange and cold = blue; purple bar charts; painterly illustrated history | Computer-Modern-like serif; script-font name captions |
| V6 2025 | Casper in a library; Derek outdoors at dusk | White-background flat diagrams (vowel and consonant circles in yellow and indigo, arrows with probabilities); painterly caricatures; archival | Clean sans + serif math |
| V7 2026 | A built set: red curtain, green card table, chips and cards | Everything drawn on felt green: cream number tiles, yellow highlights, red/orange/purple flat shapes, brass plaques; cinematic reenactment; illustration | Condensed sans caps; serif math |
| V8 2026 | NIST labs, a mountaintop, a helicopter hangar | Mid-century "lab instrument" look: mustard, teal and cream paper cut-outs, a retro oscilloscope with a dial and a digital readout | Serif titles, sans labels; chapter cards |

**Recurring devices** [verified: frames; first instance cited]

1. **Physical props for abstract symbols.** Hands move cards, tiles and wheels on a
   table: Gödel numbering on cards (V4 16:00), the middle-square method on number cards
   (V7 6:30), modular arithmetic on a paper wheel whose sectors fill yellow (V7 12:10),
   problems as brass plaques (V7 10:00), a Rubik's cube (V5 14:10), tuning forks (V8
   26:28). Each prop gets a clean motion-graphic twin right after it (the cards become
   the tile column at V7 7:40).
2. **The presenter uses the graphic.** Derek explains the engine while pointing at it on
   his monitor (V5 6:20, 8:30), stands inside the projected Mandelbrot set (V3 7:05),
   types into a calculator (V3 2:30); Gregor opens a laptop to rotate the RANDU cube
   (V7 14:20).
3. **Illustrated reenactment of history**, painterly or comic, with parallax camera moves
   (V4, V5 2:20–4:10, V6, V7 2:50–3:40). Portraits come with the person's name in script
   or caps.
4. **Documents as evidence.** Paper and article excerpts with a yellow highlighter stroke (V7 23:00,
   26:40), paper pages (V5 22:40), patch notes, journal pages, the RAND book.
5. **Experts on camera** in their lab or on a webcam call, with a two-line lower third
   (NAME / role in caps: "DARRIN HOKE / CASINO SURVEILLANCE EXPERT", "Dr. Andrew Ludlow").
6. **A quantity gets a gauge.** "Energy in the Engine" meter (V5), "MATHEMATICAL LIMIT /
   OBSERVED LIMIT" bars (V7 34:20), a retro dial with a THz readout (V8 4:30).
7. **Data charts that rescale.** V5's entropy bar chart adds a category at a time, and
   the axis keeps rescaling until earlier bars vanish; histograms with a brace label
   ("10.5%"); a 3D point cloud rotated to reveal structure.
8. **Location and date cards** for reenactments and visits ("LUMIERE PLACE CASINO / JUNE
   2ND 2014", "NIST – BOULDER, COLORADO", "1945").
9. **Chapter structure made visible** when the video runs on a ledger: V8's stacked
   chapter cards "Chapter 1: The Clock / Chapter 2: The Climb / Chapter 3: The Count"
   (2:30); V7's plaques.
10. **Earlier videos as cards.** A YouTube-card screenshot of the channel's Bell-test
    video (V7 31:40).

**Equations.** LaTeX-style serif math (Computer Modern look), colour-mapped to the
picture in V5 (Q_H orange = hot bar, Q_C blue = cold) and V7 (the cancelling terms
highlighted). They are built in steps: V5 rewrites efficiency three times in place
(8:00–8:20) [verified: frames]. Formulas are few. Most quantitative content is
numbers in tiles, charts and counters.

**On-screen text** [measured: RapidOCR on frames every 20 s; it reads text in
screenshots, papers and game UI too, and misses tiny labels, so treat these as rough]

| | V1 | V2 | V3 | V4 | V5 | V6 | V7 | V8 |
|---|---|---|---|---|---|---|---|---|
| Frames with any text | 8% | 31% | 50% | 55% | 35% | 59% | 48% | 54% |
| Frames with ≥ 10 words | 0% | 3% | 23% | 15% | 9% | 13% | 13% | 6% |
| Text boxes in top ¼ / middle ½ / bottom ¼ | – | 30/66/4 | 24/44/32 | 21/60/19 | 19/52/30 | 24/49/27 | 27/56/17 | 14/67/19 |
| Median text-box height (% of frame) | – | 7.5 | 4.2 | 5.8 | 5.8 | 5.6 | 4.2 | 4.2 |
| Boxes of ≤ 3 words | – | 100% | 99% | 90% | 80% | 84% | 78% | 93% |

- About half the frames carry some text, but almost all of it is short labels, names,
  numbers and document excerpts. The narration is never captioned on screen.
- Key sentences go on screen only rarely, and then as a typed line on an empty
  background: "Energy spreads out over time." (V5 10:40); "What does the …" (V5 0:30);
  "Does gravity itself obey…" (V8 2:00).
- Text sits mostly in the middle half, attached to its object. The bottom quarter is
  used for lower-thirds and location cards (17–32% of boxes).

**Characters.** No mascot. The human presenter is the character, and from 2025 there
are several presenters. Historical figures are drawn as recurring illustrated
characters within a video, and **illustrations are reused across videos**: V7's shot
of Ulam in his hospital bed (3:05) is the same illustration as V6's (11:35) [verified:
frames side by side]. So the team keeps reusable illustration assets [inferred].

## 7. Motion & sync grammar

**Cuts, shots and holds** [measured: `motion_stats.py`, 10 fps, 160×90 frame
differences, same thresholds as the 3b1b doc; I checked 6 random detected cuts in V7 by
eye and all 6 were real]

| | V1 | V2 | V3 | V4 | V5 | V6 | V7 | V8 |
|---|---|---|---|---|---|---|---|---|
| Hard cuts / min | 9.6 | 2.3 | 5.9 | 5.8 | 10.0 | 10.8 | 10.4 | 13.1 |
| Median shot (s) | 4.5 | 15.0 | 6.7 | 6.3 | 3.3 | 3.5 | 3.6 | 3.0 |
| Mean shot (s) | 6.1 | 25.4 | 10.1 | 10.2 | 6.0 | 5.6 | 5.7 | 4.6 |
| Still frames | 6% | 16% | 25% | 13% | 19% | 24% | 20% | 16% |
| Holds ≥ 1 s per min | 1.0 | 2.6 | 4.9 | 2.4 | 2.5 | 3.3 | 3.2 | 2.9 |
| Median hold (≥ 1 s) | 1.4 s | 2.4 | 1.5 | 1.9 | 1.8 | 2.5 | 1.6 | 2.3 |
| 90th-pct hold | 3.6 s | 6.2 | 3.1 | 5.2 | 4.8 | 5.9 | 3.6 | 4.7 |
| Longest hold | 4.5 s | 11.3 | 11.6 | 9.7 | 14.5 | 19.3 | 13.5 | 6.6 |
| Time in holds ≥ 3 s | 2% | 10% | 6% | 5% | 6% | 13% | 5% | 6% |

- **Documentary cutting, getting faster.** Since 2023 there are 10–13 cuts a minute
  (a new shot every 3–4 s at the median), against 6 in 2020–21, 2.3 in V2 (one long
  selfie walk) and 2–3 in 3b1b. The picture changes mostly *between* shots, not inside
  one long morph.
- **Stillness is rare and short.** 13–25% of frames are still, against 27–85% for 3b1b;
  holds of 3 s or more take 5–13% of the runtime, against 11–67% for 3b1b. The longest
  holds are on diagrams the narration walks through: V6's vowel–consonant chain (19.3 s
  at 7:01) and toy web (11.5 s at 20:51), V5's absolute-zero cylinder (14.5 s at 7:35),
  V7's LCG graph (13.5 s at 13:19) [measured: `*.holds.json`, matched to frames].
- **Live footage is rarely still.** Handheld camera, parallax on illustrations and slow
  pushes on photos keep even "static" content moving [verified: frames; inferred from
  the low still share in footage-heavy V1 (6%)].

**How visuals track the words** [verified: transcripts and frames; patterns inferred]

- **Enumeration builds.** When the narration counts ("One, … Two, … three"), the
  picture adds one element per item: the constraints list (V7 6:00), the plaques (V7
  10:00), the Java checklist ticks (V7 15:10), NIST's four assumptions (V7 34:00–34:10),
  V8's three chapter cards (2:30).
- **"Watch what happens" leads the change by about a beat.** The phrase comes first, then
  the model runs to its failure while the narration describes it (V7 7:35 → the loop
  lights up at 7:52; V5 12:36 "So stop, look at this" → 9 | 1).
- **A new term appears on screen as it is said**, once, as a short label or lower third
  ("Pseudo-random numbers", V7 9:30; "Entropy", V5 9:58), and then leaves.
- **Equations change in place while the sentence describes the rewrite** (V5 8:00–8:20).
- Sync is cut in the edit. There are no code-driven timing tools in the process
  sources [inferred: Final Cut / editors in §2; no evidence of word-timestamp tooling].

**Measured alignment** [measured: `sync_stats.py`, `cuts_vs_pauses.py`; phrase start =
an ASR word onset after a ≥ 0.6 s inter-word gap; pause = audio ≥ 18 dB under the
70th-percentile level for ≥ 0.3 s; chance = share of non-sponsor time inside the same
windows]

| | V1 | V2 | V3 | V4 | V5 | V6 | V7 | V8 |
|---|---|---|---|---|---|---|---|---|
| Cuts within ±0.5 s of a phrase start | 53% | 33% | 56% | 53% | 67% | 49% | 53% | 50% |
| … chance | 38% | 41% | 52% | 44% | 45% | 34% | 44% | 39% |
| Cuts inside a narration pause (±0.15 s) | 12% | 14% | 17% | 30% | 25% | 19% | 24% | 16% |
| … chance | 9% | 20% | 13% | 21% | 12% | 9% | 13% | 10% |
| Frames moving during speech | 95% | 85% | 75% | 87% | 82% | 77% | 80% | 84% |
| Frames moving during pauses ≥ 0.6 s | 85% | 82% | 73% | 87% | 73% | 67% | 75% | 77% |

- **Cuts lean toward phrase boundaries.** In the long-form videos, 49–67% of cuts fall
  within half a second of a phrase start (1.2–1.5× chance), and 16–30% fall inside a
  pause (1.4–2.1× chance). V5 is the most tightly cut on the voice. The pattern is the
  Welch one (cuts in speech pauses), but weaker.
- **Motion does not stop for pauses.** The picture moves in 67–87% of pause frames, almost
  as often as during speech, because footage, parallax and camera pushes keep running.
  Motion onsets after a still are too rare (2–47 per video) to say whether they lead
  or follow the voice. Where they occur, the median lag is about 0 s (−0.14 to +0.05 s
  in V3–V8).

**Transitions**

- Hard cuts dominate, including between footage and graphics.
- **Match cuts from prop to graphic**: physical number cards → the same numbers as motion
  tiles (V7 7:30 → 7:40); the physical wheel → its graph (V7 13:00 → 13:10).
- **The shared background as glue**: consecutive graphic shots on the same felt green
  (V7), charcoal (V5) or white (V6) read as one surface across cuts.
- Camera moves on stills: slow push or parallax on illustrations and archival photos.
- No wipes or flashy 2D transitions in the sampled frames [verified: contact sheets].

**Emphasis vocabulary** [verified: frames]

- A yellow fill or glow on the current item: loop values, wheel sectors, tiles.
- Red for the anomaly: the red tail bars in the histogram, a red arrow at Earth (V5 1:40).
- A highlighter stroke on documents.
- Removing or ticking items in the ledger.
- Rescaling a chart so one bar dominates.
- Big numerals for the quantity under discussion.
- No pulsing or wiggle emphasis was seen.

**Pauses and music.** Music runs under nearly all narration, so true silence is rare
(silence share 6–14%, §4). The longer gaps (1.5–4 s) come after a payoff line or just
before a new section (V5 9:45, 14:48, 21:34; V4 26:56).

## 8. Polish

What keeps Veritasium frames clean, roughly in order of how much it matters.

1. **One idea per graphic shot, then cut.** Graphic shots last a few seconds (median
   shot 3–4 s in 2023–26, §7). A new idea usually arrives by cut rather than by piling
   more onto the same frame, so clutter has little time to build up [inferred: motion
   stats + contact sheets].
2. **A per-video design system, applied strictly.** One background (felt green,
   charcoal, white or mustard), two to four accent colours and one label typeface,
   used across dozens of graphic shots. Example: all of V7's diagrams sit on the same
   felt green as the presenter's table, so cuts between the set and the graphics feel
   like one world [verified: frames].
3. **Colour carries the variable.** Hot is orange and cold is blue in V5's particles, bars
   and equation (Q_H, Q_C). In V7 yellow marks "the one we're looking at": loop values,
   wheel sectors, the current tile [verified: frames].
4. **Physical prop first, graphic twin second.** The prop makes the object concrete (number
   cards, a paper wheel, plaques). The motion graphic then keeps the same layout and
   abstracts it, so the viewer recognises it at once (V7 6:30 → 7:40) [verified].
5. **Anchors gain parts instead of being redrawn.** V7's input/output machine from 1:40
   returns at 24:40 with a key dial; V5's entropy chart keeps its axes and adds bars
   [verified].
6. **Real magnitudes, shown honestly.** Big numerals for counts (7 | 3, 9 | 1), long
   decimals typed out, charts rescaled live so the viewer sees one bar dwarf the rest
   [verified].
7. **Minimal, attached text.** Names on two-line lower thirds, quotes with attribution,
   short labels next to their objects; the narration is never captioned on screen (§6).
8. **Evidence on screen.** Paper and article excerpts with a single highlighter stroke on
   the sentence being quoted; long reference lists in the description [verified].
9. **Expert review before publishing.** Multiple experts per video, a fact-checker,
   Patreon early access, legal review for exposés (§2). This is polish of the claims,
   not the pixels.

## 9. Reproducing it with a code-driven pipeline

**The basic gap.** In a random sample of 40 frames per video, designed graphics and
illustration fill about **46% of V7, 58% of V5 and 40% of V8**. The rest is the
team's own camera footage (presenter, experts, labs and locations: 36% of V7, 5% of V5,
53% of V8) and found material (archival, documents, stock footage and stock space
renders: 18%, 38%, 8%) [measured: manual coding of random 5-s frames outside sponsor
reads, n = 40 per video, so ±8 points; V5's sample missed its street interviews. I
also tried CLIP zero-shot labels, but they were right on only about 60% of a 32-frame
check, so they are not used]. A Manim + TTS pipeline can make the
graphic half. The other half has to be replaced by something code can make, or left out.

**What code (Manim CE) can reproduce directly**

- **The ledger.** An on-screen list of the 2–4 open problems announced early. Items are
  removed or ticked as each is solved, and the list comes back for a review (V7's plaques,
  V8's chapter cards).
- **Model → run → break.** Iterate the toy process on screen until it visibly fails:
  repeated values light up, a 3D point cloud is rotated to show its planes, a counter
  flips the wrong way.
- **Gauges and rescaling charts.** A meter for the key quantity; a bar chart that adds
  one category per sentence and rescales so earlier bars shrink.
- **Toy with real counts, then scale-up.** Small lattice + big numerals → histogram with
  a braced tail → a narrower histogram at a larger N.
- **Colour-mapped equation rewrites in place** (three forms of the same formula).
- **Anchor diagrams that gain parts** (the input/output machine plus a key).
- **Number tiles, flat cut-paper shapes and a single per-video background colour**,
  i.e. the per-video art direction as a theme object (background, 2–4 accents, label
  font).
- **Typed quote cards** with attribution, **location/date cards**, **two-line name cards**.
- **Document cards.** A public-domain paper excerpt typeset as a page, with a
  highlighter sweep over the quoted sentence.

**What needs assets or another tool**

- Presenter on camera, street interviews, expert interviews, lab and location footage.
- Painterly illustration of historical figures and scenes (V5–V7 use credited
  illustrators).
- Archival photos and film, stock b-roll (credited to Getty, Pond5, Storyblocks), NASA
  and visualization-lab renders, 3D-rendered apparatus (V5's engine).
- Music bed under nearly all narration (Epidemic Sound, original scores by Jonny Hyman).
- **Code substitutes, ranked by fidelity** [inferred]:
  1. a document card for any primary source;
  2. a quote card in place of an expert sound bite (with the expert's name and role);
  3. a portrait card (public-domain photo, or a flat silhouette) with a script-font name
     for historical figures;
  4. a date/location card in place of reenactment.

  None of these replace the presence of a person on screen. A code-only Veritasium
  style will feel more like an illustrated essay than a documentary.

**Script template for a "Veritasium" style** [inferred: §3, §4, §5]

1. Hook: a concrete scene or claim, 0:00–1:30. End on the central question and one
   scope sentence ("This is a video about …").
2. The viewer's likely belief, stated by the narrator ("you might expect …"), or by a
   historical figure who held it. **No second character.** The PhD result says a single
   narrator who states and refutes the misconception works as well as a dialogue (§2).
3. History entry: "To answer that, we have to go back to …"
4. Either a **ledger** of 2–4 numbered problems, or a **chained-why** sequence.
5. Per cycle: build the model → run it until it breaks (wall) → a named person's insight
   → one plain sentence → a toy with real numbers → scale-up → tick the ledger → a
   "But / So …?" hand-off.
6. Midpoint callback to the hook. Answer the opening question by about two-thirds
   through, then go one level deeper.
7. Ending: return to the opening line or the people from the opening, then one last
   twist or open result. No recap list.

**Measured targets for the style's speaker profile and lint** (from §3–§4, long-form
2021–26)

| Target | Value |
|---|---|
| Walls | one every 2–3.4 min; first within 0:37–3:37 |
| Wall → revelation | median 0.5–1.7 min (3.8 in V4, where each answer is a proof) |
| WPM (whole) / while talking | 150–185 / 195–225 |
| Mean / median sentence | 15–18 / 13–16 words; ≤ 13% over 30 words |
| Reading grade | ≈ 8 |
| Questions | 0.5–1.0 per min, placed at walls and hand-offs |
| Sentence-initial "So" / "But" | 11–19% / 4–11% |
| Contractions | 11–27 per 1k words |
| Audio pauses ≥ 1 s | 0.6–1.2 per min, mostly after payoffs and before sections |

**Building blocks we would need**

| Block | Behaviour |
|---|---|
| `Theme` (per video) | Background colour, 2–4 accents, label font, number-tile style; every scene reads from it. |
| `Ledger(items)` | Numbered problem list; `close(i)` removes/ticks an item; `review()` brings all back. |
| `RunUntilBreak(process)` | Iterates a toy process as a column/stream of tiles; `highlight_repeat()` lights the loop. |
| `Gauge(name)` | Vertical meter with a label; animates fill to a value. |
| `RescalingBars` | Adds one category at a time; axis rescales so earlier bars shrink. |
| `CountToHistogram` | Lattice with big-numeral counts → histogram with braced tail → larger-N histogram. |
| `MachineDiagram` | Input → box → output stream; `add_part()` for later extensions. |
| `DocCard(text, highlight)` | Typeset excerpt with a highlighter sweep over one sentence. |
| `QuoteCard`, `NameCard`, `PlaceDateCard` | Attributed quote; two-line name/role; place + date. |
| `PortraitCard(name)` | Image or silhouette with a script-font name. |
| Scene-per-beat | Short shots (3–6 s) joined by cuts; one idea per graphic shot. |
| Pacing profile "veritasium" | ~170 WPM, short sentences, 0.5–1 question/min, music bed, longer pauses only after payoffs. |

**Where this style clashes with the current skill rules** (see synthesis §7)

- *No exact numbers or tables (hard rule 10)*: Veritasium's revelations depend on exact
  counts (91,520 vs 627,264; 2¹⁶ = 65,536; 4.669). This should be a style setting.
- *Long holds vs fast cutting*: 3b1b-style holds and slow builds do not match a style
  with 6–13 cuts a minute. The style needs scene-per-beat cutting.
- *Key sentence on screen*: rare here, as in 3b1b. Use typed key lines only at section
  turns.
- *Misconception devices*: the skill must not satisfy "address the misconception" with a
  dialogue character (Ben's dislike). The refutation is the narrator's job.

## 10. Sources

**Sample videos** — V1–V8 (table at top). Manual English captions (`en`), YouTube auto
captions (`en-orig`, word timing), 360p video with audio, `info.json` (descriptions,
credits, chapters), all pulled 2026-11-21 with yt-dlp. SponsorBlock segments for sponsor
removal (`meta/sponsor.json`).

**Process videos (Veritasium's own uploads)**
- P1 — [Khan Academy and the Effectiveness of Science Videos](https://www.youtube.com/watch?v=eVtCO84MDj8), 2011 (Derek summarising his PhD; captions read in full)
- P2 — [The Future of Veritasium](https://www.youtube.com/watch?v=piHGnG4LsmQ), 2025-12-24 (team history, Electrify, 30+ staff, process claims; captions read in full)
- P3 — [We're trying something new...](https://www.youtube.com/watch?v=ONAuUyml0yI), 2026-09-30 (InGenius launch, pitch meetings)

**Thesis and papers**
- T — Derek A. Muller, *Designing Effective Multimedia for Physics Education*, PhD thesis, University of Sydney, 2008. Read via Wayback: https://web.archive.org/web/2015/https://www.sydney.edu.au/science/physics/pdfs/research/super/PhD(Muller).pdf (page numbers are the printed ones)
- W7 — Muller & Sharma, "Tackling misconceptions in introductory physics using multimedia presentations", UniServe Science symposium 2007, https://openjournals.library.sydney.edu.au/IISME/article/view/6345 (abstract fragments only; the PDF returned 403)
- W8 — Muller, Sharma & Reimann, *Science Education* 2008, abstract via https://perticles.blogspot.com/2008/01/muller-sharma-reimann-sci-ed-2008.html (272 students; dialogue viewers "judged themselves to be similar to the student")

**Web** (all fetched 2026-11-21; quotes re-checked against the saved text in `research_cache/veritasium/web/`)
- W1 — https://www.creatorhandbook.net/inside-veritasium-an-interview-with-dr-derek-muller-12ad2351a4b3/ — Creator Handbook interview, 2017-09-01 (98% solo, GH5 kit, topic sources, misconceptions quote)
- W2 — https://sydney.edu.au/news-opinion/news/2024/11/05/the-element-of-truth.html — University of Sydney alumni profile, 2024-11-05
- W3 — https://www.tubefilter.com/2026/01/06/veritasium-derek-muller-electrify-investment/ — Tubefilter, 2026-01-06 (Electrify deal, team, costs quadrupled)
- W4 — https://www.scientificamerican.com/article/how-youtube-star-derek-muller-of-veritasium-is-challenging-scientific/ — Scientific American profile, 2025 (Casper Mebius quotes, the "change the way they view the world" test, watch-time reading)
- W5 — https://www.productionbase.co.uk/film-tv-jobs/writer-director-youtube-channel-remote-working-10.24.0239739 — Veritasium Writer/Director job post (code suggests Oct 2024; the original Electrify Teamtailor posts return 410)
- W6 — https://rosetta.to/u/wired/veritasium-s-derek-muller-answers-the-web-s-most-searched-questions-wired — caption mirror of WIRED's Autocomplete interview with Derek, 2022-11-25 (Final Cut Pro X; "probably after effects")
- Wikipedia, Derek Muller (background only; no claim relies on it)
- Not read: Derek's TEDxSydney talk *The key to effective educational science videos* (https://www.youtube.com/watch?v=RQaW2bFieo8), which covers the same PhD findings as P1; the 2018 Physics Forums interview (only the question thread was reachable); MIT OCW 20.219 (2015) lecture transcript (404).

**Code**
- C1 — https://github.com/jonnyhyman/Chaos — Jonny Hyman's scripts for V3 (Python; PyQt5/pyqtgraph, vispy, numba), read via `gh api` 2026-11-21

**Method.** Scripts, transcripts, frames and outputs are in the gitignored
`research_cache/veritasium/` (`scripts/`, `analysis/`, `txt/`, `frames/`, `sheets/`,
`web/`). Video files were deleted after measuring.

| Script | What it measures |
|---|---|
| `lang_metrics.py` | WPM, ASR gaps, sentence stats, questions, pronouns, contractions, FK (textstat) |
| `punct.py`, `v4_sent.py` | Punctuation restoration for V4 (validated on V5) and its sentence stats |
| `lang_markers.py` | Marker rates per 1k words, sentence openers, shared n-grams |
| `pauses_audio.py` | 20 ms RMS pauses, threshold 18 dB under the 70th-percentile frame, sponsor removed |
| `turns.py`, `cycle_stats.py` | Regex candidates for walls/revelations; spacing of my hand-coded list |
| `motion_stats.py` | 10 fps frame differences: hard cuts (6 of 6 sampled cuts in V7 checked by eye), stills, holds |
| `sync_stats.py`, `cuts_vs_pauses.py` | Motion in speech vs pauses; cuts vs phrase starts and pauses, against chance |
| `ocr_text.py`, `ocr_summarize.py` | RapidOCR on frames every 20 s |
| `palette.py` | Hue mix of saturated pixels |
| `contact_sheet.py` | 10-s sheets for V5 and V7 (read in full), 15–30-s sheets for the rest, random 40-frame sheets for shot coding |

Contact sheets read: V5 and V7 at 10-s spacing (all), V2, V3, V4, V6, V8 at 15–45-s
spacing, plus random 40-frame samples of V4, V5, V7, V8 (V4's was not coded).
