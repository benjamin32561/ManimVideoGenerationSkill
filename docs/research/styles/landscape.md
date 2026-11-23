# Explainer styles landscape — phase 1 (channels, tools, script practice)

Research date: 2026-11-21. Scope: STEM explainer channels other than 3Blue1Brown, Welch Labs and
Floatheads Physics (covered elsewhere). Phase 1 describes styles and the tools creators use; it does
not benchmark our render engine.

**Evidence tags.** `[verified: source]` = stated by the creator/tool docs or visible in the cited
artifact. `[measured: method]` = computed by me from captions/frames (method in §2).
`[inferred: from what]` = my reading of evidence; treat as a lead, not a fact.

## 0. Findings at a glance

1. **Narration comes first almost everywhere, and the edit is where sync happens.** Kurzgesagt
   records narration after illustration and before animation: "His voiceover provides the timing for
   the animation team" [verified: kurzgesagt.org/youtube]. minutephysics writes, records and
   edits audio before storyboarding a single drawing [verified: Sixty Symbols, 2011]. Core Dumped
   generates the voice in ElevenLabs and syncs PowerPoint renders to it in DaVinci Resolve [verified:
   Core Dumped Q&A, 2025]. Artem Kirsanov renders long code animations and time-remaps them to his
   voice in After Effects [verified: "How I make science animations"]. The clear exception is
   Sebastian Lague, who builds the project first and scripts from its version history [verified: Q&A].
   Primer's simulation-driven videos probably work the same way [inferred: narration comments on
   simulation runs].
2. **One channel already ships a TTS-narrated, slide-animated CS series at scale.** Core Dumped
   (ElevenLabs voice, PowerPoint visuals) calls the voice "part of the channel's identity" [verified:
   Q&A]. Its measured articulation rate is fast (182–201 wpm) but it inserts many ≥1 s pauses
   (8–10 per minute) [measured]. That is the closest existing match to our pipeline.
3. **Pace varies by ~2x across good channels.** Words per narrated minute range from ~126
   (Branch Education, Core Dumped) to ~212–234 (minutephysics, which cuts nearly every breath:
   ≤0.7 pauses ≥1 s per minute) [measured]. A style preset needs its own WPM *and* pause budget, not
   just a TTS speed.
4. **Words per frame separates the styles; background colour does not** [measured: OCR + palette].
   Six of eight channels sit on a dark ground. The text load spans almost two orders of magnitude.

   | Channel | Words/frame (mean) | Frames with text | Dark-ground frames |
   |---|---|---|---|
   | Kurzgesagt | 0.8 | 22.2% | 71.8% |
   | minutephysics (handwriting undercounted) | 5.5 | 85.7% | 70.9% |
   | Artem Kirsanov | 14.6 | 92.6% | 93.8% |
   | Reducible | 18.0 | 96.5% | 98.3% |
   | Branch (incl. watermark) | 19.5 | 100.0% | 12.9% |
   | Sebastian Lague (UI text) | 25.4 | 97.9% | 7.0% |
   | Primer | 41.1 | 98.4% | 100.0% |
   | Core Dumped | 46.3 | 97.5% | 94.9% |

   Mayer's redundancy principle supports Kurzgesagt-style sparse labels, but its effect size is the
   weakest of his principles (d = 0.10) [verified: Mayer 2023]. Text-heavy CS styles are therefore a
   defensible preset, not an error.

5. **The code-driven channels each rely on one bespoke layer.** Reducible pairs Manim CE with a house
   palette and fonts file [verified: repo]. Primer uses its own Godot toolkit with LaTeX→mesh
   [verified: repo]. Sebastian Lague uses Unity with his own timing helpers [verified: Q&A]. Artem
   Kirsanov adds a Blender add-on that runs NEURON simulations [verified]. A multi-style generator
   needs a per-style "house kit" (palette, type, primitives, timing helpers), not just a prompt.
6. **Narrative mode is the biggest style axis after visuals.** The modes differ in measured pronoun
   and question use. Kurzgesagt is second-person essay ("you" 34–74 per 1k words). Lague is a
   first-person build log ("I" up to 23 per 1k, "we" 42–52). Primer is simulation-as-experiment
   (prediction prompts; questions are 10% of sentences in the RPS video). Branch is a guided teardown
   tour with long, low-tension sentences (but÷and 6.5–13.5). Reducible is guided problem-solving
   ("How would you approach this problem?").
7. **Polish comes from fixed layout zones, not from per-frame care.** Examples: Reducible's
   top-centre title plus mono labels inside cells, Primer's persistent procedure list with a moving
   pointer, Branch's translucent label panels in negative space, and Core Dumped's vertical split
   panels [verified: frames]. Each can be encoded as a layout grammar.

## 1. Channel picks

| # | Channel | Why it shapes a multi-style generator (one line) | Code-driven? |
|---|---|---|---|
| 1 | **Reducible** | Manim CE in a CS/algorithms register distinct from 3b1b (black + neon palette, mono data cells), with all scene code public [verified: repo]. | Yes (Manim CE) |
| 2 | **Artem Kirsanov** | Computational/cellular neuroscience (Ben's topic), a hybrid of Manim/matplotlib/Blender composited in After Effects, with a published how-I-animate breakdown [verified]. | Hybrid |
| 3 | **Primer** | Simulation-as-story with 3D characters, built in a public game-engine toolkit (Blender→Unity→Godot) [verified: repos/descriptions]. | Yes (Godot C#) |
| 4 | **Sebastian Lague** | First-person "build log" mode (computer engineering: logic gates→RAM), visuals are the real Unity project [verified: Q&A]. | Yes (Unity C#) |
| 5 | **Kurzgesagt** | The illustrated / After Effects contrast case; it covers neuroscience and philosophy-of-mind topics (memories, minds) and publishes its process [verified]. | No (AE) |
| 6 | **minutephysics** | Hand-drawn, ultra-compressed physics (thermal/colour-temperature topics); the fastest, near-breathless VO [measured]. | No (paper + camera) |
| 7 | **Branch Education** | Photoreal 3D Blender teardowns of computer hardware (CPU, DRAM), a team-made computer-engineering reference [verified]. | Partly (Blender) |
| 8 | **Core Dumped** | Low-level CS/OS explainers made with PowerPoint + ElevenLabs TTS, the nearest existing match to our TTS pipeline [verified: Q&A]. | No (slides), but trivially code-able |

Code-animated picks: Reducible, Primer, Sebastian Lague (plus Artem's Python/Blender layer).
Illustrated / After Effects contrast: Kurzgesagt. Hand-drawn contrast: minutephysics.

**Candidates considered and not picked** (none was sampled; all reasons are [inferred: channel
lists and general knowledge]):

- **Veritasium:** presenter-led live action and documentary interviews, which a narration+animation generator
  cannot reproduce. Its research angle is used in §5 instead.
- **Steve Brunton:** lightboard lectures that depend on an on-camera lecturer.
- **ByteByteGo:** an animated-infographic system-design style. Its toolchain is unverified: the only
  claim found is a blog comment saying "After Effects".
- **Up and Atom** and **Zach Star:** presenter-plus-graphics; no verified tooling found.
- **Mutual Information:** Manim ML/statistics, which overlaps Reducible. Its channel handle did not
  resolve.

Philosophy of mind and linguistics have no dedicated pick. Kurzgesagt's mind videos are the
closest sampled proxy for conceptual, equation-free topics.

## 2. Method (how the numbers were made)

- **Transcripts.** Two videos per channel (three for minutephysics), from YouTube caption tracks
  via yt-dlp. Word timings come from the auto track (`en-orig`). Sentences come from the manual
  track where one exists, otherwise from ASR punctuation. Reducible and one minutephysics video
  had unpunctuated ASR, which I punctuated with an LLM (Gemini 2.5 Flash via OpenRouter). The
  token sequence was checked against the ASR with difflib: matches were ≥0.98, except the A* video
  at 0.92–0.99, where the model corrected ASR misspellings such as "ukian"→"euclidean"; the word
  count moved by 0.3%. These rows are labelled `asr+llm_punct`.
- **Sponsor exclusion.** SponsorBlock sponsor/selfpromo/interaction/outro segments are removed from
  all language and visual metrics.
- **Rates.** WPM (span) = words ÷ time from first to last narrated word. WPM (articulation) = words ÷
  the sum of inter-word gaps shorter than 1.5 s, which approximates speaking rate without long
  pauses. "Breath group" = words between word-onset gaps ≥0.75 s. ASR gives approximate word
  onsets only (no offsets), so treat pause figures as relative between channels.
- **Text features.** Questions = sentences ending in "?". Pronouns per 1,000 words. "but÷and×100"
  is Randy Olson's but-to-and ratio (more "but" = more tension/turns; see §5G). FK grade =
  Flesch–Kincaid via `textstat`.
- **Frames.** One 360p video per channel, one frame every 4 s (sponsor frames removed), and a
  4×6 contact sheet that I inspected visually. Palette = k-means (k=8) over downsampled frames.
  On-screen text = RapidOCR on every 4th sampled frame (every 16 s), confidence ≥0.6. Hard cuts =
  ffmpeg `scene>0.3`. "Large change" = mean absolute pixel difference >25/255 between frames 4 s
  apart; "near-static" = <2/255.
- **Limits.** The sample is 2 videos per channel, so these are style fingerprints, not population
  statistics. OCR undercounts handwriting and tiny text and overcounts watermarks (Branch's logo
  is on every frame). The cut detector reads minutephysics' 1-photo-per-second stop-motion as cuts.

---

## 3. Channel profiles

### 3.1 Reducible — Manim CE algorithms explainer (black + neon, mono data)

Sampled: *How PNG Works* (2022, frames + transcript), *A\* Search* (2024, transcript).

**1. Snapshot.** Long-form (16–35 min) CS/algorithms videos. Their pitch is to re-derive an
algorithm as if you had to invent it. The visuals are boxed arrays, grids of numbers, trees and
charts on pure black. The creator is Nipun Ramakrishnan; recent videos are "Animations created
jointly by Nipun Ramakrishnan and Jesús Rascón" [verified: video descriptions].

**2. Production pipeline & tools.**
- Manim throughout. Early videos used a modified 3b1b `manimlib` (Cairo). The switch to Manim
  Community came with the Marching Squares video (Oct 2021) [verified: repo README].
  Descriptions cite Manim CE v0.11.0 (PNG, 2022) and v0.18.1 (A\*, 2024) [verified: descriptions].
- All animation code is public at `nipunramk/Reducible`, one folder per video [verified: repo].
- House style is a module of constants. `reducible_colors.py` defines a palette (`REDUCIBLE_PURPLE
  #8c4dfb`, `REDUCIBLE_YELLOW #ffff5c`, `REDUCIBLE_GREEN_LIGHTER #00cc70`, `REDUCIBLE_WARM_BLUE
  #08B6CE`, `REDUCIBLE_ORANGE #FFB413`, `REDUCIBLE_CHARM #FF5752`, …) and fonts
  `REDUCIBLE_FONT = "CMU Serif"` and `REDUCIBLE_MONO = "SF Mono"` [verified: `2022/common/reducible_colors.py`].
  Shared mobject classes (e.g. a bar chart "to add font personalization") live in `common/classes.py`
  [verified: repo].
- Music comes from a collaborator (Jesús Rascón) and stock artists [verified: descriptions]. Editor
  and VO chain: no source found.

**3. Script writing process & structure.** I found no published account of the scripting process
(searched interviews and the repo).
- *Structure* [inferred: transcripts]:
  1. A real-world motivation (JPEG artefacts; map apps).
  2. A naive approach, then its failure ("what went wrong here?").
  3. Incremental refinement with worked examples.
  4. An assembled pipeline.
  5. Contrast with an alternative (PNG vs QOI; greedy vs Dijkstra vs A\*).
  6. A moral ("simple and understandable solutions").
- Reader-participation questions: "How would you approach this problem?"; "How do you think LZSS
  will encode it?" [verified: transcript].

**4. Language profile (measured).**

| Video | Sentences from | Narrated min | Words | WPM (span / articulation) | Pauses >=1 s per min | Words per breath group | Sentence len mean / median / p90 | % sentences >25 w | Questions % of sentences (per min) | you / we / I per 1k words | but÷and x100 | FK grade |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| How PNG Works (2022) `EFUYNoFRHQI` | asr+llm_punct | 30.57 | 4968 | 162.5 / 188.3 | 7.88 | 14.3 | 18.5 / 17.0 / 30 | 19.4 | 3.4 (0.29) | 5.4 / 28.4 / 4.4 | 31.1 | 9.6 |
| A* Search (2024) `88I6IidylGc` | asr+llm_punct | 16.18 | 2412 | 149.1 / 180.7 | 11.07 | 10.6 | 16.9 / 16.0 / 26 | 12.7 | 7.0 (0.62) | 4.6 / 42.7 / 1.2 | 25.0 | 8.2 |

Reading [inferred: from the table]: steady (149–163 wpm) "we"-voice exposition (28–43 per 1k).
Many ≥1 s pauses (7.9–11.1 per minute); the A\* video has the most of any human narrator in the
sample, which matches step-wise reveals. Sentences are short-to-medium (median 16–17 words) at a moderate grade level (8–10).

**5. Flow — PNG (31 min).**
- 0:00 Hook/agenda: PNG keeps quality where JPEG artefacts; the theme is speed vs quality.
- ~1:00 Bytes and pixels; Huffman refresher (tree at ~3:00).
- ~6:00 LZSS from text examples (sliding window, lookahead, offset/length).
- ~12:00 Why raw pixels compress badly, so filters (Sub/Up/Avg/Paeth), choosing by minimum sum of
  absolute differences.
- ~21:00 Assemble the pipeline: filter → LZSS → Huffman.
- ~24:00 Contrast: QOI's run-length/index tricks and benchmark bars.
- ~30:00 Moral: simplicity wins. Sponsor at the end.

**6. Visual system.**
- *Measured* (How PNG Works (2022); 459 frames at 1 per 4 s; OCR on 115):
  - Ground: dark 98.3% / light 0.2% of frames; mean luma 18.1/255; mean saturation 0.122.
  - Text: on 96.5% of frames; 18.0 words/frame (median 11 on frames with text, p90 36); 7.87% of frame area; vertical top/mid/bottom 0.28/0.46/0.26.
  - Change: large 10.5% / near-static 45.0% of 4-s windows; hard cuts 0.22/min.
  - Dominant colours: `#000000` 78%, `#182322` 8%, `#443f3f` 6%, `#766661` 4%, `#492bc8` 2%, `#e8e2e6` 1%.
- Type: CMU Serif for titles and chart captions; SF Mono for data, labels and cell values
  [verified: repo + frames].
- Imagery: arrays as rows of rounded squares, numeric grids, binary trees, bar charts, a single test
  photo [verified: frames].
- Density: high data density but generous black margins. Titles sit top-centre and active objects
  in the middle band [verified: frames; OCR position shares].

**7. Motion & sync grammar.** The screen is mostly still while the narration works through a
state: 45.0% of 4-s windows are near-static and only
10.5% change a lot [measured]. Hard cuts are rare
(0.22/min) [measured]. Changes are local: a box lights up, a pointer slides along
the window, cells fill in, an encoded output grows one token at a time [verified: frames].
Colour carries meaning: green cells are literals; purple/yellow mark back-references and
offset/length [verified: frames].

**8. Polish.**
- Every label sits inside or directly under its object; no free-floating prose on graphs.
- One title per scene; dimmed (low-opacity) copies show context that is out of focus.
- Footnotes are tiny but present ("*Tests run on Intel i7 quad core, 16 GB RAM").

[verified: frames]

**9. Reproducibility (code-driven).** **High.** Same library as ours (Manim CE). Their palette and
font constants are public, so a "Reducible-like" preset is a constants module + an array/grid/tree
component kit + a no-prose-on-graphs rule. The one gap is SF Mono, which is an Apple font
[inferred]. Swap in a licensed mono such as JetBrains Mono for redistribution.

---

### 3.2 Artem Kirsanov — computational neuroscience, hybrid code + AE compositing

Sampled: *The Core Equation Of Neuroscience* (2024, frames + transcript), *Your Brain Is 150,000
Mini-Brains* (2025, transcript), *How I make science animations* (2023, process source).

**1. Snapshot.** 13–40 min videos on neural computation (Hodgkin–Huxley, cortical columns,
hippocampus, learning rules). Artem states a research role at Harvard [verified: descriptions].
The tone is that of a careful lecture, with face-camera inserts at a desk with a mic and
blackboard [verified: frames].

**2. Production pipeline & tools** [verified: "How I make science animations", 2023].
- **After Effects** is the "main workhorse", for simple animation and for "composing the results of
  other programs". He chose it for "an optimal balance between capabilities and usability".
- **Python** covers what AE scripting cannot ("Yes, technically there is a JavaScript API, but
  honestly I found it to be quite unusable"):
  - **Manim**, used heavily early on and still for network/graph animation ("Manim just has got
    such an amazing, out-of-the-box solution for graph theory").
  - **matplotlib** `FuncAnimation` for most plot animation. He finds it more intuitive and
    controllable frame by frame than Manim, which could not do things like "drawing gradient lines
    colored by coordinate".
- **Blender** (free, Python API) for anything 3D: neurons, mice in mazes, surface plots. His own
  add-ons are **BlenderSpike**, which brings NEURON-simulator voltage data onto real morphologies,
  and **BlenderBrain**, which imports brain-atlas meshes (Allen Institute atlases via the BrainGlobe
  API).
- **Illustrator** for assets and diagrams (live-linked into AE), **Photoshop** for thumbnails and
  raster work, **Premiere Pro** for editing (especially face-cam), and **Audition** for voice
  cleanup ("removing plosives and other nasty things like breaths and mouth sounds").
- **Sync technique:** render each code animation as a very long clip (e.g. 5,000 frames), then speed
  it up and ease it with AE time-remapping "to match the voice". Black-background clips are layered
  with the Screen blend mode so black becomes transparent. "Time remapping is your best friend."
- **Research:** papers plus recorded lectures, with notes kept in an Obsidian Zettelkasten [verified:
  "My Strategy To Consume Information Effectively"].

**3. Script writing process & structure.** The scripting process itself is not published (searched).
The animation process works by decomposition: identify a scene's "core components", then assign
each to the tool that does it best [verified: process video].
- *Structure* [inferred: transcripts]:
  1. An open mystery ("The human brain remains one of science's greatest mysteries") or a striking
     anatomical fact ("This is neocortex, a sheet of cells just a few millimeters thick").
  2. The biophysical ingredients one at a time.
  3. The model assembled term by term.
  4. A historical payoff (the n⁴ gate exponent found before channel structure was known).
  5. An extension to space or network.
  6. What the model explains.
- Questions often open a sub-mechanism ("How fast does the number of permissive gates change?")
  [verified: transcript].

**4. Language profile (measured).**

| Video | Sentences from | Narrated min | Words | WPM (span / articulation) | Pauses >=1 s per min | Words per breath group | Sentence len mean / median / p90 | % sentences >25 w | Questions % of sentences (per min) | you / we / I per 1k words | but÷and x100 | FK grade |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| The Core Equation Of Neuroscience (2024) `zOmhHE2xctw` | manual:en-US | 23.1 | 3104 | 134.4 / 146.9 | 6.75 | 8.2 | 18.8 / 18.0 / 30 | 22.0 | 3.0 (0.22) | 1.9 / 22.6 / 1.0 | 17.2 | 11.9 |
| Your Brain Is 150,000 Mini-Brains (2025) `Dykkubb-Qus` | asr | 20.09 | 2979 | 148.2 / 158.6 | 6.57 | 11.6 | 16.1 / 14 / 30 | 14.6 | 2.7 (0.25) | 17.5 / 10.4 / 0.7 | 26.8 | 9.8 |

Reading [inferred]: among the slowest narrators in the sample (134–148 wpm span; 147–159
articulation; only Branch is slower), with short breath groups (8–12 words). It is also the most lexically varied: type/token
over the first 1,000 words reaches 0.479, the highest
measured. The derivation video reads at FK grade 11.9, the newer one at 9.8. Equations are spoken
as meaning, not symbols.

**5. Flow — Hodgkin–Huxley (23 min).**
- 0:00 Mystery hook: computers vs neurons; models as simplified descriptions; promise of HH.
- ~2:00 Ions and the membrane as a capacitor (dQ/dt = C dV/dt).
- ~4:00 Diffusion vs electric force; equilibrium potential (K⁺ ratio ~30).
- ~9:00 Conductance, driving force, gating variable n, rate equations; the n⁴ payoff.
- ~15:00 Na⁺ (m³h) and the leak; the full current equation; the simulated spike.
- ~19:00 Spatial extension (cable/compartments).
- ~21:00 Close; sponsor.

**6. Visual system.**
- *Measured* (The Core Equation Of Neuroscience (2024); 324 frames at 1 per 4 s; OCR on 81):
  - Ground: dark 93.8% / light 0.0% of frames; mean luma 29.7/255; mean saturation 0.62.
  - Text: on 92.6% of frames; 14.6 words/frame (median 13 on frames with text, p90 25); 14.75% of frame area; vertical top/mid/bottom 0.39/0.31/0.3.
  - Change: large 11.8% / near-static 30.7% of 4-s windows; hard cuts 0.73/min.
  - Dominant colours: `#010006` 63%, `#16161b` 11%, `#323135` 10%, `#574e53` 6%, `#867b7a` 4%, `#b9adab` 4%.
  - Caveat: the text area is inflated because the OCR also reads the chalk-covered blackboard behind
    the face-cam and the large LaTeX equations [inferred: frames].
- Very dark navy-black backgrounds with neon cyan/magenta/green glows. LaTeX equations in Computer
  Modern; sentence-case serif headings at top-centre [verified: frames].
- 3D glowing ion-channel and neuron renders (his stated 3D tool is Blender [verified: process
  video]), a scanned figure from the 1952 paper, and face-cam shots [verified: frames].
- Text is used as **definitions on screen** ("Let n be the probability of finding a single gate in
  the permissive state") next to the equation it defines [verified: frames].

**7. Motion & sync grammar.**
- Curves draw on as narrated; the equation builds term by term with colour-coded terms; 3D
  channels open and close.
- Cuts are rare in the graphics (0.73/min) [measured]. Many of the cuts that do
  occur look like face-cam switches [inferred: contact sheet].
- Pacing is set in post by time-remapping [verified: process video].

**8. Polish.**
- The glow look comes from Screen-blended layers [verified: process video].
- Labels attach to their object with thin leader lines.
- Dense derivation frames (the full cable equation) are split across a top equation and
  bottom annotations, with term braces ("Driving force") pointing into the formula.

[verified: frames]

**9. Reproducibility (code-driven).** **Medium-high.** Manim CE covers LaTeX build-ups and graph
animation. Neon glow can be approximated with stacked strokes [inferred]. Two gaps: per-segment
gradient-coloured curves (his reason for leaving Manim [verified]) and 3D biophysical renders, which
need Blender/bpy [inferred]. Face-cam inserts are out of scope. His long-render-then-retime trick is
the inverse of our audio-first sync; we already time to words, so we do not need it [inferred].

---

### 3.3 Primer — simulation-as-story (blobs), custom game-engine toolkit

Sampled: *Simulating a single brain cell* (2025, frames + transcript), *Simulating the Evolution of
Rock, Paper, Scissors* (2024, transcript).

**1. Snapshot.** By Justin Helps. Agent-based simulations of evolution, game theory, statistics and
(recently) artificial neurons. Cute 3D "blob" creatures on a grassy platform. Recent videos add
presenter cut-outs in the corner [verified: frames; descriptions "Made with Godot"].

**2. Production pipeline & tools.**
- **Blender era:** `Helpsypoo/primerpython`, "a library of tools that lets you write high-level
  functions to build and animate objects in Blender". It ran via the Script Runner add-on on
  Blender 2.79, and "Much of the structure comes from manim" [verified: README; repo archived].
- **Unity era:** `Helpsypoo/PrimerUnity` and `primereconomy` ("Building a simulated economy in Unity
  for Primer videos") [verified: GitHub].
- **Godot era (current):** both sampled videos say "Made with Godot" and link
  `Primer-Learning/PrimerTools` (C#) [verified: descriptions + repo]. The toolkit includes a LaTeX→SVG→mesh
  pipeline (`LaTeX/LatexToMesh.cs`, `SvgToMesh.cs`) and `Animation/AnimationSequence.cs`
  [verified: repo tree]. The author has "given up on the idea of designing this to be usable by
  others", and the blob models are private [verified: README].
- Music: Mathieu Keith [verified: description]. Edit/VO chain: not found.

**3. Script writing process & structure.** No published scripting process was found.
- *Structure* [inferred: transcripts]:
  1. Set up the agents and the rule ("These blobs compete for food by playing rock, paper,
     scissors").
  2. **Ask the viewer to predict** ("Before we hit go, what do you think will happen…?" — 14
     questions in 14.6 min [measured]).
  3. Run the simulation, then explain the surprise.
  4. Change one rule and repeat.
  5. Name the formal concept late ("evolutionarily stable strategy"), explicitly *after* the
     intuition: "The fancy terminology isn't really necessary here, but I wanted to at least
     mention it" [verified: transcript].
- The neuron video follows a curriculum spine instead. A persistent "Training Loop Steps" list is
  revised as the model grows [verified: frames].

**4. Language profile (measured).**

| Video | Sentences from | Narrated min | Words | WPM (span / articulation) | Pauses >=1 s per min | Words per breath group | Sentence len mean / median / p90 | % sentences >25 w | Questions % of sentences (per min) | you / we / I per 1k words | but÷and x100 | FK grade |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Simulating a single brain cell (2025) `GkiITbgu0V0` | asr | 33.75 | 5766 | 170.9 / 179.8 | 3.29 | 17.9 | 15.3 / 14 / 26 | 10.6 | 2.7 (0.3) | 9.0 / 39.2 / 4.2 | 37.7 | 7.0 |
| Simulating the Evolution of Rock, Paper, Scissors (2024) `tCoEYFbDVoI` | manual:en | 14.57 | 2365 | 162.3 / 189.8 | 4.53 | 17.8 | 17.4 / 16 / 31 | 19.0 | 10.2 (0.96) | 7.2 / 20.3 / 5.1 | 37.1 | 8.2 |

Reading [inferred]:
- Fast, conversational and plain: FK 7–8, the lowest in the sample. Short sentences (median 14–16).
- Many causal connectives ("so/therefore" 13–15 per 1k; only Lague uses more) and the highest
  but÷and (37–38), i.e. the most turns and consequences.
- Few long pauses (3.3–4.5 per minute).

**5. Flow — single neuron (34 min).**
- 0:00 What ANNs power; a promise of what you will understand by the end.
- ~2:00 Natural vs artificial neuron.
- ~3:30 A neuron as a function; parameters; learning = adjusting them.
- ~6:45 Task 1, distance from energy: hand-written update rule, error.
- ~10:40 The loss surface; gradient descent; learning rate.
- ~17:00 Task 2, classify mangoes: sigmoid, 100,000 epochs.
- ~27:00 Two inputs; XOR fails, setting up multi-neuron networks.
- End: next video teaser.

**6. Visual system.**
- *Measured* (Simulating a single brain cell (2025); 507 frames at 1 per 4 s; OCR on 127):
  - Ground: dark 100.0% / light 0.0% of frames; mean luma 42.9/255; mean saturation 0.129.
  - Text: on 98.4% of frames; 41.1 words/frame (median 37 on frames with text, p90 76); 9.25% of frame area; vertical top/mid/bottom 0.31/0.47/0.22.
  - Change: large 3.6% / near-static 63.6% of 4-s windows; hard cuts 0.18/min.
  - Dominant colours: `#1b1c1d` 79%, `#333633` 7%, `#4d5748` 5%, `#6a7272` 3%, `#8a6345` 2%, `#b59773` 2%.
- Charcoal background, off-white Computer-Modern-style serif (LaTeX rendered to meshes
  [verified: repo]), red/blue accents, a 3D grass platform, blob characters, real photos (mangoes),
  and one meme insert [verified: frames].
- Density: very high and structured, second only to Core Dumped in words per frame [measured].
  Graph (left) + neuron diagram (centre) + step list (right) + data table + 3D loss plots on one
  frame [verified: frames]. The screen is calm while this happens:
  63.6% near-static 4-s windows [measured].

**7. Motion & sync grammar.**
- Simulations play out in real time while the narrator comments.
- An arrow pointer walks down the step list as each step runs.
- 3D camera orbits reveal loss surfaces.
- The presenter cut-out appears beside the graphics, not as a full-screen cut (0.18
  hard cuts/min).

[verified: frames; measured]

**8. Polish.**
- Columns are kept strictly: plot | model | procedure.
- The step list is persistent, so the viewer always knows where they are.
- Weak point: secondary text is very small (procedure sub-bullets are tiny at 360p).

[verified: frames]

**9. Reproducibility (code-driven).** **Medium.** The 2D layer is straightforward in Manim: plots,
step list with pointer, LaTeX, tables. Primer's identity is the 3D simulated agents, which need a
3D engine (Blender bpy or Godot) plus character assets [inferred]. The reusable grammar is
**predict → run → explain → perturb**, which works with 2D agents too [inferred].

---

### 3.4 Sebastian Lague — first-person coding/hardware adventure (Unity)

Sampled: *Simulating 256 Bytes of RAM* (2025, frames + transcript), *Coding Adventure: Simulating
Fluids* (2023, transcript), *Answering Your Questions* (2023, process source).

**1. Snapshot.** 25–80 min "Coding Adventure" episodes. He builds a working thing (fluid sim,
renderer, logic-gate computer) and narrates the journey, including failures [verified: transcripts].
The RAM video belongs to a computer-architecture series built in his own logic simulator
(`SebLague/Digital-Logic-Sim` linked) [verified: description].

**2. Production pipeline & tools** [verified: "Answering Your Questions"].
- Each project is kept under version control. Afterwards he walks its history and takes screen
  recordings of "everything that I think would be nice to show".
- "I make all the visualizations in Unity". For drawing he uses Freya Holmér's **Shapes** asset and
  his own rough `VidTools`; his `ImmediateAnimation` helper computes clip progress with easing and
  sequential start times so "everything adjust[s] automatically".
- Keyboard triggers advance animations live; scenes can be scrubbed.
- "I spend a bit of time experimenting with these different easing function[s]".
- Edit and voice-over: "arranging all the clips in Davinci Resolve", then final VO.
- He suggests Manim or Motion Canvas for people outside Unity.
- Fluids is "Written in C# and HLSL, and running inside the Unity engine" [verified: description].

**3. Script writing process & structure** [verified: Q&A].
1. Build first, film later from version history.
2. "start piecing together a rough script of what I want to say, and in what order".
3. Decide which parts get extra explanatory visualizations.
4. "do a rough read through of the script, and start arranging all the clips" to judge pacing.
5. Refine the script or "cut out whole sections if they feel too boring or confusing".
6. Final VO and final edit.

- *Structure* [inferred: transcripts]: greeting + goal ("let's draw a circle"), then repeated
  try → observe failure → understand → fix loops, with honest asides ("I probably should have started
  with that"), and a sign-off.

**4. Language profile (measured).**

| Video | Sentences from | Narrated min | Words | WPM (span / articulation) | Pauses >=1 s per min | Words per breath group | Sentence len mean / median / p90 | % sentences >25 w | Questions % of sentences (per min) | you / we / I per 1k words | but÷and x100 | FK grade |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Simulating 256 Bytes of RAM (2025) `HGkuRp5HfH8` | manual:en-GB | 25.58 | 4385 | 171.4 / 192.9 | 6.92 | 15.6 | 23.9 / 22.0 / 43 | 39.7 | 0.5 (0.04) | 2.3 / 51.5 / 7.5 | 18.8 | 10.1 |
| Coding Adventure: Simulating Fluids (2023) `rSKMYc1CQHE` | manual:en-GB | 47.56 | 8346 | 175.5 / 192.0 | 8.26 | 12.8 | 26.0 / 24.0 / 45 | 46.6 | 0.3 (0.02) | 0.5 / 42.1 / 22.9 | 26.0 | 11.5 |

Reading [inferred]:
- Long sentences (mean 24–26 words; ~40–47% over 25 words, on a par with Branch) delivered fast
  (171–176 wpm).
- Almost no questions (≤0.5% of sentences).
- "We" dominates (42–52 per 1k); "I" spikes in build logs (23 per 1k in Fluids).
- "let's" is the most frequent signpost (up to 11.6 per 1k).

**5. Flow — 256 bytes of RAM (26 min).**
- 0:00 Series recap: demo of the registers + ALU (15 − 10).
- ~1:30 Why memory: a grid of latches, a 4-bit address.
- ~2:40 Row/column select with decoders; a real-world aside (DRAM refresh; SEM photos of SRAM
  cells).
- ~11:00 Live test: store/read.
- ~14:00 Hierarchy up to MEM-256.
- ~17:30 Asynchronous vs clocked; wire to registers; demo.
- ~22:45 A small XNOR equality circuit; sign-off.

**6. Visual system.**
- *Measured* (Simulating 256 Bytes of RAM (2025); 385 frames at 1 per 4 s; OCR on 97):
  - Ground: dark 7.0% / light 1.0% of frames; mean luma 75.0/255; mean saturation 0.172.
  - Text: on 97.9% of frames; 25.4 words/frame (median 28 on frames with text, p90 43); 4.99% of frame area; vertical top/mid/bottom 0.17/0.35/0.48.
  - Change: large 12.5% / near-static 54.4% of 4-s windows; hard cuts 0.66/min.
  - Dominant colours: `#404041` 60%, `#2d2929` 9%, `#0c0a0b` 8%, `#636a74` 6%, `#ad9a8b` 5%, `#7d503f` 5%.
- Mid-grey canvas with orange chips, colour-coded wires (red/green/blue/purple buses), red
  7-segment displays and a persistent bottom menu bar listing built components (UI text inflates
  the OCR count) [verified: frames].
- Inserts: credited SEM photos and stock video. Separate dark diagram scenes show abstractions
  (CPU/cache/RAM) [verified: frames].

**7. Motion & sync grammar.**
- Screen recordings of the live tool: wires light up when high, values change in place, and the
  camera pans and zooms.
- Explanatory scenes are triggered animations with tuned easing [verified: Q&A].
- Few hard cuts (0.66/min); visuals mostly change inside one canvas [measured;
  verified: frames].

**8. Polish.**
- Colour is functional: wire colour = bus identity, lit = logic high.
- Labels are chip names inside the chips, so nothing floats.
- Hierarchy is shown by collapsing a sub-circuit into a labelled chip ("MEM-256" title card over a
  dimmed circuit).

[verified: frames]

**9. Reproducibility (code-driven).** **Low-medium.** The "logic-sim canvas" look (chips, buses,
lit wires, 7-seg readouts) is very reproducible as a Manim/Motion Canvas component kit [inferred].
The *narrative* (real discoveries, real bugs) needs a real project log; a generator that fakes it
would mislead [inferred]. Usable as a preset only for build-it-up topics: logic → ALU → RAM.

---

### 3.5 Kurzgesagt — illustrated flat-vector essay (After Effects)

Sampled: *How Are Memories Stored Inside Your Brain?* (2026, frames + transcript), *Our Minds Are
Weirder than You Think* (2026, transcript), *How to Make a Kurzgesagt Video in 1200 Hours* (2020,
process source).

**1. Snapshot.** 10–15 min science essays by a studio team, with a single recurring narrator (Steve
Taylor) and original music (Epic Mountain) [verified: descriptions]. Topics in the sample:
memory engrams, animal and human minds (consciousness, aphantasia).

**2. Production pipeline & tools** [verified: 1200-hours video; kurzgesagt.org/youtube].
- Research: books, papers, expert conversations, and a public "sourcesheet" per video.
- Script.
- Sketching (visual metaphors, transitions).
- Illustration: ~200 panels "in Adobe Illustrator"; 2–3 illustrators for 8–12 weeks.
- Narration: recorded "on a Neumann TLM 103 microphone and Pro Tools".
- Animation "in Adobe After Effects" (Cinema 4D being trialled in 2020). Characters are rigged;
  "every single thing that's moving on-screen has been moved manually"; 2–3 animators for 8–10
  weeks.
- Original music and sound design. Reviews "every few days". "At least 1,200 hours" per video, with
  2–4 videos in flight.

**3. Script writing process & structure.**
- Rewritten "over and over"; "about a dozen drafts"; expert fact-checks. "Writing is the bottleneck
  for our videos, and very hard to speed up", taking "between a few weeks and literally years"
  [verified: 1200-hours video; site].
- *Structure* [inferred: transcripts]:
  1. Poetic metaphor hook ("Memories are biological magic").
  2. Stakes for *you* ("they are a huge part of what makes you you").
  3. A cluster of questions.
  4. The mechanism told through a recurring character and visual metaphor.
  5. A twist (memories change when recalled).
  6. A reflective callback ending ("you may be able to rewrite your lore").

**4. Language profile (measured).**

| Video | Sentences from | Narrated min | Words | WPM (span / articulation) | Pauses >=1 s per min | Words per breath group | Sentence len mean / median / p90 | % sentences >25 w | Questions % of sentences (per min) | you / we / I per 1k words | but÷and x100 | FK grade |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| How Are Memories Stored Inside Your Brain? (2026) `PqtggjVAi8M` | manual:en | 12.96 | 1963 | 151.5 / 170.4 | 5.4 | 11.6 | 15.9 / 14.5 / 27 | 11.1 | 3.2 (0.31) | 73.9 / 3.1 / 2.0 | 25.0 | 8.8 |
| Our Minds Are Weirder than You Think (2026) `dl0-TveDDGA` | manual:en | 10.67 | 1527 | 143.1 / 168.1 | 5.34 | 11.1 | 17.8 / 16.0 / 31 | 19.3 | 19.3 (1.59) | 34.7 / 23.6 / 0.0 | 32.7 | 9.0 |

Reading [inferred]:
- Second person dominates: 74 "you" per 1k words in the memory video, the highest in the sample;
  "we" is rare there (3 per 1k).
- Short sentences (median 14.5–16). Moderate pace (143–152 wpm) over music.
- The philosophy-of-mind video is the most question-dense in the sample (19% of sentences;
  1.6 per minute) and uses "imagine" prompts (2.6 per 1k).

**5. Flow — memories (13 min).**
- 0:00 Metaphor + stakes + "What IS a memory?".
- ~1:20 Neurons and connections (≈10,000 each).
- ~2:40 Perception is assembled from parts → neuron assemblies.
- ~4:00 What becomes permanent.
- ~5:20 The engram: a partial cue completes the pattern.
- (Sponsor ~6:00–7:13.)
- ~7:45 Strengthening by retelling; sleep replay in the hippocampus.
- ~10:20 Reconsolidation: recall makes it malleable.
- ~11:40 Implications.
- Callback close.

**6. Visual system.**
- *Measured* (How Are Memories Stored Inside Your Brain? (2026); 177 frames at 1 per 4 s; OCR on 45):
  - Ground: dark 71.8% / light 2.8% of frames; mean luma 67.4/255; mean saturation 0.758.
  - Text: on 22.2% of frames; 0.8 words/frame (median 2 on frames with text, p90 2); 0.81% of frame area; vertical top/mid/bottom 0.41/0.36/0.23.
  - Change: large 88.6% / near-static 0.0% of 4-s windows; hard cuts 5.67/min.
  - Dominant colours: `#0a0321` 36%, `#2d0b5a` 23%, `#403898` 12%, `#43c7d4` 8%, `#984a35` 6%, `#984acb` 6%.
- Deep indigo/violet backgrounds with radial glow; highly saturated foreground (yellow engrams,
  cyan/magenta neurons); round-faced characters; dioramas inside spheres [verified: frames].
- Text is nearly absent: single labels ("HIPPOCAMPUS"), speech bubbles, newspaper props
  [verified: frames; OCR].
- Density: rich illustration but one focal subject per frame [verified: frames].

**7. Motion & sync grammar.**
- Constant motion: 0.0% near-static windows, the lowest in the sample;
  88.6% large-change windows [measured].
- Cut-like transitions are frequent (5.67/min) [measured].
- Hand-keyed character animation, glow pulses, zoom-through transitions between metaphors
  [verified: process video; frames].
- Timing follows the recorded VO [verified: site].

**8. Polish.**
- The subject is centred with darkened edges (vignette).
- One brightness/saturation peak per frame guides attention.
- No text competes with the art.

[verified: frames]

**9. Reproducibility (code-driven).** **Low** for the full look. It is hundreds of bespoke
illustrations plus character rigs [verified: process video]. A *Kurzgesagt-lite* preset is
plausible: flat vector shapes, a radial-glow background, saturated accents, no text, second-person
script. The art budget is the blocker: it needs an SVG asset library or generated vector art
[inferred].

---

### 3.6 minutephysics — hand-drawn time-lapse, compressed physics

Sampled: *The Color Temperature Paradox* (2024, frames + transcript), *You're Technically HOTTER
Than The Sun* (2022, transcript), *We Used To Have No Idea How Sight Worked* (2026 upload of a 2018
pilot, transcript; its narration says so, so it is atypical). Process sources: Sixty Symbols *Making
Minute Physics* (2011) and *minutephysics Behind the Scenes – Teleportation*.

**1. Snapshot.** Henry Reich; 2–6 min (sometimes longer) physics explainers built on stick figures,
hand-lettered labels, a paradox hook and a single resolution. The 2024 sample shows white/coloured
marker lines on a dark warm-black ground with the drawing hand visible. The hand looks
colour-inverted (pink skin) [verified: frames]. That points to black-on-white paper footage inverted
in post [inferred: from frames]. There are also live-action photo inserts (camera, lights)
[verified: frames].

**2. Production pipeline & tools.**
- 2011 account [verified: Sixty Symbols]:
  - Markers "from a hardware store".
  - "I have a camera that I've put up here facing down it's just a still camera"; "one picture
    every second while I'm drawing"; on paper ("people think I do this on whiteboards").
  - The script is recorded at a microphone behind a cubicle wall so "the sound is really dead".
  - He edits the audio "like crazy".
- BTS Teleportation [verified: transcript via rosetta.to]: storyboard first; drawings are "actually
  image sequences"; colour-correct and assemble; simple layer animation for effects.
- Editing software: not named in either source.

**3. Script writing process & structure** [verified: Sixty Symbols].
- "the big long part is writing the script". He reads it aloud while writing, then records and edits
  the sound. "only then do I even start to storyboard out the drawings".
- Storyboard, drawing and editing each take about an hour per finished minute.
- He sometimes asks Perimeter Institute physicists to check for mistakes.
- *Structure* [inferred: transcripts]:
  1. A concrete everyday observation ("take a piece of white paper into different lighting
     conditions").
  2. A paradox ("Kelvin is a unit for measuring temperature, not color").
  3. The physics (hotter = bluer).
  4. A second twist (camera settings are compensation, so reversed).
  5. A crisp re-naming punchline ("call it what color are your lights").

**4. Language profile (measured).**

| Video | Sentences from | Narrated min | Words | WPM (span / articulation) | Pauses >=1 s per min | Words per breath group | Sentence len mean / median / p90 | % sentences >25 w | Questions % of sentences (per min) | you / we / I per 1k words | but÷and x100 | FK grade |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| The Color Temperature Paradox (2024) `mqZm6u12RJA` | asr+llm_punct | 3.64 | 852 | 234.2 / 234.2 | 0.0 | 142.0 | 21.1 / 20.0 / 39 | 40.0 | 2.5 (0.27) | 14.1 / 7.0 / 1.2 | 13.0 | 10.8 |
| You're Technically HOTTER Than The Sun (2022) `6tu0mIpX8nU` | manual:en | 2.87 | 607 | 211.8 / 211.8 | 0.7 | 67.4 | 22.3 / 21 / 34 | 29.6 | 3.7 (0.35) | 9.9 / 3.3 / 0.0 | 18.5 | 10.9 |
| We Used To Have No Idea How Sight Worked (2026) `5qYRfCnIITk` | manual:en | 13.67 | 2336 | 170.9 / 179.9 | 3.29 | 15.0 | 26.1 / 24 / 45 | 46.1 | 6.7 (0.44) | 9.4 / 13.3 / 3.4 | 25.3 | 11.4 |

Reading [inferred]:
- The short-form videos are the fastest narration measured: 212–234 wpm with ≤0.7 pauses of ≥1 s
  per minute, so breaths are edited out.
- Sentences are long for the speed (median 20–21). The 2018 pilot is slower (171 wpm) and closer to
  a documentary.

**5. Flow — colour temperature (3.6 min).**
- 0:00 White paper under different lights; cameras white-balance; Kelvin paradox.
- 0:22 Blackbody: hotter is bluer (Wien).
- 0:46 Misconception: "warm" light is the cooler one.
- 1:15 Non-blackbody sources; the 2,000–10,000 K range; green/magenta tint.
- 2:06 Camera setting reversed.
- 2:50 Consequences.
- 3:15 Rename punchline.
- 3:39 Sponsor.

**6. Visual system.**
- *Measured* (The Color Temperature Paradox (2024); 55 frames at 1 per 4 s; OCR on 14):
  - Ground: dark 70.9% / light 0.0% of frames; mean luma 75.7/255; mean saturation 0.394.
  - Text: on 85.7% of frames; 5.5 words/frame (median 3 on frames with text, p90 7); 5.89% of frame area; vertical top/mid/bottom 0.21/0.36/0.44.
  - Change: large 75.9% / near-static 7.4% of 4-s windows; hard cuts 55.25/min.
  - Dominant colours: `#1a120c` 32%, `#30231b` 29%, `#a09ca2` 10%, `#624230` 8%, `#796f6c` 6%, `#bb7449` 5%.
- Hand-lettered words ("Wien's Law", "2000K … 10000K", "Then:") and stick figures, with colour used
  only for physical colour (glowing bulbs, a spectrum band) [verified: frames].
- Text is short labels and numbers, often on a number line [verified: frames; OCR].

**7. Motion & sync grammar.**
- Drawings appear stroke by stroke in time-lapse, hand included [verified: frames]. In 2011 the
  capture was one photo per second [verified: Sixty Symbols]. The cut detector registers
  55.25 "cuts"/min (~0.9 per second), which fits that stop-motion cadence rather than
  editing [inferred].
- Big changes in 75.9% of 4-s windows [measured].
- The drawing races to keep up with the VO [inferred: frames vs transcript timing].

**8. Polish.**
- Each frame holds one idea; labels are written where they apply.
- High-contrast light-on-dark lines.
- The hand is part of the aesthetic. "I try to draw things from left to right", which keeps the hand
  off finished work [verified: BTS transcript; the purpose is the transcript summary's reading].

**9. Reproducibility (code-driven).** **Medium.** The look can be approximated with stroke-order
SVG reveal (Manim `Create`/`DrawBorderThenFill`), a handwriting font, a warm-black ground and an
optional hand sprite [inferred]. The pace is the harder part. 210–235 wpm with no breaths needs TTS
at a fast rate *and* pause trimming, and our current beat-pause conventions run the other way
[inferred].

---

### 3.7 Branch Education — photoreal 3D hardware teardown (Blender)

Sampled: *How do CPUs Work?* (2025, frames + transcript), *How does Computer Memory Work?* (2022,
transcript).

**1. Snapshot.** 20–40 min computer-hardware explainers. A 3D "camera" tours real devices:
laptop → board → chip → transistor. Physical metaphors (a library for memory, a calculator for the
ALU, a notebook for registers) carry the abstraction [verified: frames]. Founder Teddy Tablante
(electrical/mechanical engineer) [verified: brancheducation.pages.dev].

**2. Production pipeline & tools** [verified: brancheducation.pages.dev; descriptions].
- Six steps:
  1. Research and scripting.
  2. Storyboarding.
  3. 3D modelling and voice-over.
  4. Animation in Blender.
  5. Visual accuracy review.
  6. Sound design.
- "Animation built using Blender 3.1.2" and "Post with Adobe Premiere Pro" (2022 credits). The
  2025 credits list an Animation Director, primary and secondary animators, "Research, Script and
  Editing: Teddy Tablante", and "Voice Over: Phil Lee" (human).
- "over 1,100 hours" per video. An AI policy: every 3D model and animation is "built by human hands";
  AI is used for source finding and grammar checks.

**3. Script writing process & structure** [verified: site].
- Research draws on raw technical documentation, academic papers and patents.
- Teddy writes every script; editors and reviewers check each draft.
- *Structure* [inferred: transcripts]:
  1. Ubiquity hook ("Inside every desktop computer, smartphone…").
  2. A history comparison.
  3. A physical teardown.
  4. Install the governing metaphor.
  5. Step a real program (a C++ for-loop compiled to assembly) through fetch-decode-execute.
  6. Map the metaphor back onto a die shot.
  7. Variants (RISC/CISC, GPU SIMT).
- Questions are rare, but rhetorical "Have you ever wondered…" openers appear [verified:
  transcript].

**4. Language profile (measured).**

| Video | Sentences from | Narrated min | Words | WPM (span / articulation) | Pauses >=1 s per min | Words per breath group | Sentence len mean / median / p90 | % sentences >25 w | Questions % of sentences (per min) | you / we / I per 1k words | but÷and x100 | FK grade |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| How do CPUs Work? (2025) `16zrEPOsIcI` | manual:en | 35.85 | 4518 | 126.0 / 142.7 | 6.89 | 8.2 | 26.5 / 24.0 / 41 | 46.5 | 1.8 (0.08) | 6.9 / 20.4 / 1.1 | 13.5 | 12.9 |
| How does Computer Memory Work? (2022) `7J7X7aZvMXQ` | manual:en | 34.38 | 4747 | 138.1 / 151.3 | 5.96 | 8.6 | 25.0 / 24.0 / 41 | 44.1 | 2.1 (0.12) | 4.0 / 11.0 / 0.0 | 6.5 | 11.7 |

Reading [inferred]:
- The slowest human delivery (126–138 wpm), with long noun-heavy sentences (median 24; ~45% over
  25 words) and the highest grade level (FK 11.7–12.9).
- The lowest but÷and in the sample (6.5–13.5): an additive guided tour rather than a tension-driven
  story.

**5. Flow — CPU (36 min).**
- 0:00 Ubiquity + promise; 1980s machines vs a modern laptop.
- ~3:50 Teardown to DRAM/CPU.
- ~7:20 Library/table/book/calculator metaphor.
- ~10:50 Recipe/ingredients = instructions/data; C++ → assembly.
- ~14:10 Walk the loop through fetch-decode-execute.
- ~17:50 Decoder, control signals, buses.
- ~21:30 Variants (sponsor ~25:30–27:55).
- ~28:00 Map to a real die.
- ~32:00 Multicore/GPU.
- Wrap.

**6. Visual system.**
- *Measured* (How do CPUs Work? (2025); 488 frames at 1 per 4 s; OCR on 122):
  - Ground: dark 12.9% / light 8.8% of frames; mean luma 119.8/255; mean saturation 0.193.
  - Text: on 100.0% of frames; 19.5 words/frame (median 10 on frames with text, p90 51); 6.7% of frame area; vertical top/mid/bottom 0.26/0.4/0.34.
  - Change: large 57.5% / near-static 1.0% of 4-s windows; hard cuts 0.03/min.
  - Dominant colours: `#c0bfbd` 19%, `#4b5350` 16%, `#656d5f` 15%, `#2f3035` 13%, `#85837a` 11%, `#a4a09b` 10%.
- Photoreal props on a green cutting mat or a vast library hall; label panels in a light sans with a
  soft glow on translucent dark cards; a persistent "Branch Education" watermark bottom-right
  (counted by OCR on every frame); instruction lists as on-screen tables [verified: frames].

**7. Motion & sync grammar.**
- Continuous camera moves and exploded views instead of cuts: 0.03 hard cuts/min,
  the lowest measured. Yet 57.5% of 4-s windows change a lot and only
  1.0% are near-static, because the camera is always moving.
- Objects animate in place: a calculator display changes, wires light, paper fills.

[measured; verified: frames]

**8. Polish.**
- Labels sit in negative space beside the prop, never over the geometry.
- One metaphor object per concept stays in fixed positions on the desk, so spatial memory does
  the work.

[verified: frames]

**9. Reproducibility (code-driven).** **Low** at full fidelity (team modelling, 1,100+ h
[verified]). A *schematic-Branch* preset is feasible in 2D or simple 3D. Keep the metaphor-on-a-desk
staging, fixed object positions, label cards, and slow, dense, low-tension narration [inferred].

---

### 3.8 Core Dumped — slide-animated low-level CS with a TTS voice

Sampled: *What Happens When a CPU Receives an Unknown Instruction?* (2026, frames + transcript),
*How CPUs Run Functions* (2026, transcript), *You Wouldn't Stop Asking Me The Same Questions*
(2025, process source).

**1. Snapshot.** By George. 10–25 min OS/CPU explainers (processes, signals, ISA extensions,
calling conventions) with a dry humour stinger, serialized ("A couple of episodes back…")
[verified: transcripts].

**2. Production pipeline & tools** [verified: Q&A 2025].
- "every video on this channel is made entirely with PowerPoint slides".
- "The only stage of my workflow where AI is involved is the voice over. For that, I use 11 Labs".
- He then syncs "the audio with the animations in Da Vinci Resolve". "That's my entire workflow."
- He keeps the AI voice because it "has become part of the channel's identity".
- He uses AI for finding sources, not for explanations.

**3. Script writing process & structure.** Concepts are "based on knowledge I've gathered over the
years"; no drafting process is published [verified: Q&A].
- *Structure* [inferred: transcripts]:
  1. A question barrage ("What happens when we give a CPU an instruction it doesn't know? Does the
     program crash? Does the operating system show an error?").
  2. A recap of the previous episode.
  3. The mechanism built up from a "what if we…" engineering problem.
  4. Real code (assembly, C, CPUID bit fields).
  5. A live demo (run an AVX-512 binary on an old CPU → crash).
  6. Explain via the OS (SIGILL → core dump; analogy to segfaults).
  7. Mitigation.
  8. Next-episode hook.

**4. Language profile (measured).**

| Video | Sentences from | Narrated min | Words | WPM (span / articulation) | Pauses >=1 s per min | Words per breath group | Sentence len mean / median / p90 | % sentences >25 w | Questions % of sentences (per min) | you / we / I per 1k words | but÷and x100 | FK grade |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| What Happens When a CPU Receives an Unknown Instruction? (2026) `WtlGB-YVLOg` | asr | 11.91 | 1509 | 126.7 / 181.9 | 9.91 | 7.7 | 17.8 / 15 / 33 | 22.4 | 9.4 (0.67) | 4.6 / 19.9 / 5.3 | 32.4 | 11.0 |
| How CPUs Run Functions (2026) `7YyALikxAlU` | asr | 19.36 | 2966 | 153.2 / 201.3 | 8.21 | 10.9 | 21.7 / 18 / 41 | 27.0 | 1.5 (0.1) | 3.4 / 13.5 / 2.4 | 30.0 | 11.4 |

Reading [inferred]:
- The TTS voice speaks fast (articulation 182–201 wpm), but the edit adds many ≥1 s pauses (8–10
  per minute) and short breath groups (8–11 words). The net span rate (127–153 wpm) is close to
  Branch's.
- The question-barrage opener lifts question share to 9% in the ISA video.

**5. Flow — unknown instruction (12.5 min).**
- 0:00 Question barrage; ISA recap.
- ~1:15 ISA extensions (SSE/AVX…).
- ~2:25 Naming/compatibility.
- ~4:45 Key line on screen: "Problems emerge only if the processor reaches an instruction it
  doesn't support."
- ~6:00 CPUID leaves/subleaves.
- ~8:25 Inline-asm feature checks.
- ~9:35 Crash demo.
- ~10:45 SIGILL and core dump.
- Fallback strategies; comic stinger.

**6. Visual system.**
- *Measured* (What Happens When a CPU Receives an Unknown Instruction? (2026); 157 frames at 1 per 4 s; OCR on 40):
  - Ground: dark 94.9% / light 0.0% of frames; mean luma 22.2/255; mean saturation 0.118.
  - Text: on 97.5% of frames; 46.3 words/frame (median 22 on frames with text, p90 127); 7.62% of frame area; vertical top/mid/bottom 0.3/0.46/0.24.
  - Change: large 12.8% / near-static 50.0% of 4-s windows; hard cuts 0.8/min.
  - Dominant colours: `#000000` 59%, `#0e0e0f` 21%, `#232628` 10%, `#474948` 4%, `#fafafa` 2%, `#7260c8` 2%.
- Pure black ground; monospace everywhere (keyword highlights in yellow/green); CPU product photos;
  register and bit-field diagrams; side-by-side assembly listings; tree diagrams of CPUID leaves
  [verified: frames].
- Key sentences appear as standalone typed text, with the emphasised words in bold colour
  [verified: frames].

**7. Motion & sync grammar.**
- Slide builds and (likely) Morph transitions: objects slide between slides and panels split with
  vertical rules [inferred: frames + PowerPoint workflow].
- Frequent ≥1 s pauses in the VO [measured] appear to give each slide build time to land [inferred].
- 0.8 hard cuts/min [measured].

**8. Polish.**
- Strong left/right panel discipline and generous black space.
- Colour highlights point into dense code.
- Weak point: very small code in multi-column listings [verified: frames].

**9. Reproducibility (code-driven).** **Very high.** Black + mono + boxes + code listings + photo
inserts, narrated by TTS with inserted pauses, is essentially our current pipeline with a different
theme [inferred]. It is evidence that viewers accept a TTS voice for this register. The sampled
videos have 0.17 M and 0.32 M views, and the channel's most-viewed recent upload has 1.5 M
[verified: channel listing, 2026-11-21].

---

## 4. Tools landscape

| Tool | What it is | Sampled channels using it (verified) | Good at (for narrated explainers) | Bad at / costs |
|---|---|---|---|---|
| **Manim Community** (Python) | Community-maintained Manim, "more stable, better tested and documented" [verified: Manim FAQ] | Reducible (v0.11 → v0.18.1); Artem (graphs) | LaTeX, morphs, graph/network objects, deterministic code; `manim-voiceover` adds TTS, bookmarks, and Whisper word timing [verified: plugin docs] | Weak 3D; per-segment gradient strokes awkward [verified: Artem]; not a compositor [inferred] |
| **ManimGL** (Python, OpenGL) | Grant Sanderson's version; "more experimental", breaking changes undocumented [verified: Manim FAQ] | Reducible's pre-2021 videos used older 3b1b `manimlib` (Cairo) [verified: README] | Interactive OpenGL preview [inferred: general knowledge, not verified here] | Reducible: "not quite stable … much trickier to learn" (opinion) [verified: README] |
| **Motion Canvas** (TypeScript) | Generator-based animation library + real-time editor, "designed to create informative vector animations and synchronize them with voice-overs" [verified: README] | None in sample; recommended by Lague as an alternative [verified] | Time events (`waitUntil`) draggable in a timeline to match the VO without editing code [verified: docs] | LaTeX/3D support not checked in this phase; TypeScript/web stack [inferred] |
| **Remotion** (React/TS) | Video as React components | None in sample | Web typography/CSS/SVG, data-driven templates; captions import/transcribe/display/export [verified: docs index] | Company licence required for for-profit orgs above 3 employees [verified: LICENSE]; no math layout built in [inferred] |
| **Blender** (+ `bpy`) | Free 3D suite with Python API | Branch (Blender 3.1.2); Artem (3D neurons via BlenderSpike/BlenderBrain); Primer's early `primerpython` (Blender 2.79) [all verified] | Photoreal or stylised 3D, exploded views, camera fly-throughs, scripted scenes | Modelling/animation labour (Branch: 1,100+ h/video, team) [verified]; no native "plot a surface" [verified: Artem]; render cost [inferred] |
| **Godot** (C#) | Open-source game engine | Primer ("Made with Godot", PrimerTools) [verified] | Real-time simulation + rendering in one place; LaTeX→mesh in PrimerTools [verified: repo] | Toolkit "not designed to be usable by others" [verified]; you build the video tooling yourself |
| **Unity** (C#) | Game engine | Sebastian Lague (all visualizations; Shapes asset; VidTools) [verified]; Primer's earlier PrimerUnity [verified] | Visualizing a real running project; interactive scrubbing; easing | Drawing primitives "a bit cumbersome" without plugins; manual object lifetime management [verified: Lague] |
| **After Effects** | Motion graphics/compositor | Kurzgesagt (main animation tool); Artem ("main workhorse"); Veritasium's animators [verified: WIRED] | Compositing, text animation, time-remapping to VO, rigs, blend modes | Scripting API "quite unusable" (Artem) [verified]; hand-keyed labour (Kurzgesagt: 2–3 animators × 8–10 weeks) [verified] |
| **Cinema 4D** | 3D for motion design | Kurzgesagt (trialling, 2020) [verified] | AE-adjacent 3D | Paid; no sampled code workflow |
| **Illustrator** | Vector drawing | Kurzgesagt (~200 panels/video); Artem (assets, live-linked to AE) [verified] | Bespoke vector art; AE round-trip | Manual; art skill is the bottleneck |
| **Photoshop** | Raster editing | Artem (thumbnails, raster fixes) [verified] | Cut-outs, colour fixes | — |
| **Procreate** | iPad drawing app | None verified in sample (searched) | Hand-drawn assets/frames [inferred] | — |
| **Keynote** | Slides with Magic Move | None verified in sample; Magic Move is used for classroom animations in Apple Education resources [verified: resource titles] | Fast morph-between-slides animation [verified: Apple Education] | Manual, no code, limited easing control [inferred] |
| **PowerPoint** | Slides (Morph transition) | Core Dumped (entire visuals) [verified] | Very fast authoring of text/code/diagram builds; rendered as video | Manual per slide; sync done later in an NLE [verified: Core Dumped uses Resolve] |
| **matplotlib** (`FuncAnimation`) | Python plotting | Artem (most plot animation) [verified] | Fine control of per-element properties per frame | Low level; needs compositing for text/layout [verified: Artem] |
| **DaVinci Resolve** | Edit/colour/audio NLE | Sebastian Lague (assembly + pacing + final); Core Dumped (VO sync) [verified] | Free tier; rough-cut-for-pacing workflow | Manual sync |
| **Premiere Pro** | NLE | Branch (post, 2022); Artem (editing, face-cam) [verified] | Standard edit + Adobe round-trip | Manual sync |
| **Final Cut Pro X** | NLE | Veritasium ("I only use Final Cut Pro X", including thumbnail text) [verified: WIRED] | Fast editing on Mac | Mac only |
| **Pro Tools + Neumann TLM-103** | VO recording chain | Kurzgesagt narration [verified] | Studio VO | Human narrator time |
| **Adobe Audition** | Audio cleanup | Artem (noise, plosives, breaths, mouth sounds) [verified] | VO cleanup | — |
| **ElevenLabs** | TTS | Core Dumped (all VO) [verified] | Consistent "channel voice"; no recording | Per-character cost [inferred]; viewers ask about it [verified] |
| **Paper + markers + still camera** | Physical time-lapse | minutephysics (1 photo/s, 2011) [verified] | Authentic hand-drawn look; quick (≈1 h per finished minute for drawings) [verified] | Not editable after the fact [inferred] |
| **NEURON simulator, Allen atlas meshes** | Science data sources | Artem (via BlenderSpike/BlenderBrain) [verified] | Real biophysics behind the visuals | Specialist setup |

**Notes.**
- **Hybrid stacks are normal.** Artem's rule is "No single mathematical animation … was created with
  matplotlib or Manim alone. There is always some After Effects involved" [verified]. For a code-only
  generator, the compositor jobs (glow, blend modes, time-remap, text animation) have to live inside
  the renderer [inferred].
- **Sync tooling is where the code tools differ most.**
  - Manim CE + `manim-voiceover`: speech-bounded `with` blocks + bookmarks + Whisper word timing
    [verified: plugin docs].
  - Motion Canvas: named time events dragged in an editor timeline [verified].
  - Remotion: captions as data [verified].
  - Unity/Godot: the author's own sequencing classes (`ImmediateAnimation`, `AnimationSequence`)
    [verified].
  - Our word-timestamp approach sits closest to `manim-voiceover` [inferred].
- **Every code-driven creator ended up with a house kit:** colour/font constants (Reducible), drawing
  and timing helpers (Lague), LaTeX→mesh plus private character assets (Primer), and Blender add-ons
  (Artem) [verified: repos/Q&A].

## 5. Published script-writing guidance (synthesised)

**A. Research and accuracy come before words.**
- Kurzgesagt:
  - Starts from books, papers and experts.
  - Expects to change its own view while researching.
  - Has experts fact-check the script.
  - Publishes sources [verified: 1200-hours video; site].
- Branch: reads documentation, papers and patents, and runs a separate *visual* accuracy review
  [verified: site].
- TED-Ed: checks the writer's sources and fact-checks before assigning a narrator and animator
  [verified: EdSurge 2018].

**B. The script is the bottleneck, and it is rewritten many times.**
- "Writing is the bottleneck for our videos" (Kurzgesagt; "about a dozen drafts") [verified].
- "it takes forever to write a script" (Reich) [verified].
- TED-Ed asked one educator for an "800-900 word script" that is "simple and direct" [verified:
  EdSurge 2018]. At our measured 126–234 wpm that is roughly 3.5–7 minutes [inferred: arithmetic].

**C. Read it aloud while writing, and judge pacing against picture before the final VO.**
- Reich reads the script aloud as he writes [verified].
- Lague does "a rough read through" while arranging clips to "get a sense of the pacing", then cuts
  boring or confusing sections before the final VO [verified].
- A university script guide: "There's no substitute for practicing a video script aloud." It also
  assumes "Most people read at a 120-words-per-minute pace" [verified: UW Continuum guide]. That
  is below every professional rate measured here (126–234), so 120 wpm is a floor, not a target
  [inferred].

**D. Script → storyboard order.**
- In most sampled workflows, visuals are planned from a finished script:
  - Kurzgesagt sketches "visual metaphors, transitions between ideas" after the script is ready.
  - minutephysics storyboards only after recording.
  - Branch storyboards after scripting.
  - MinuteEarth goes pitch → script → rough sketches → final illustration [verified: respective
    sources; MinuteEarth via rosetta.to summary].
- Inverse workflows exist where the artifact is the subject. Lague builds first and scripts from
  version history; Artem renders long clips and retimes them to the VO [verified].

**E. VO recording practice.**
- Kurzgesagt's narrator records one full flowing take, then retakes "paragraphs and sentences until
  they feel right" [verified].
- Reich records in a deadened booth and edits heavily [verified].
- Artem cleans plosives, breaths and mouth sounds in Audition [verified].
- Core Dumped uses a fixed TTS voice as brand identity [verified].
- Mayer's voice principle (human > machine voice, 6 of 7 tests, d = 0.74) is qualified in the same
  chapter: "advances in modern text-to-speech engines can allow them to be more human-like" (Craig &
  Schroeder 2017, 2018) [verified: Mayer 2023].

**F. Hooks and openings.**
- YouTube's Creator Playbook (2011) on the first 15 seconds [verified: blog.youtube]:
  - "Start off with something that will immediately grab attention".
  - "Make it clear what your video is about early on".
  - "Tease the rest of the video so the audience is intrigued to see where you take them".
  - "A flashy intro may look cool, but it's not the star of the video."
- The sampled openings fall into five types [verified: transcripts]:
  - **question barrage** (Core Dumped)
  - **everyday paradox** (minutephysics)
  - **metaphor + personal stakes** (Kurzgesagt)
  - **ubiquity + promise** (Branch, Primer)
  - **open mystery** (Artem)
- Derek Muller's research is relevant to the paradox and question hooks [verified: Muller & Sharma
  2012 abstract]:
  - Misconceptions "give students a false sense of knowing, limiting the mental effort they invest".
  - "exposing students to common misconceptions, even in non-interactive settings, can help them
    overcome these difficulties".
  - Scientific American's 2025 profile opens: "Clarity numbs the mind, but confusion can crack it
    open." [verified: SciAm]
  - Practical reading: name the wrong intuition on screen, then break it [inferred]. minutephysics'
    "warm light is actually cooler" beat and Primer's prediction prompts both do this
    [verified: transcripts].

**G. Structure: tension and turns.**
- Randy Olson's **And–But–Therefore** template: every "story can be reduced to this single
  structure". It follows Trey Parker's "rule of replacing and's with either but's or therefore"
  [verified: NCSE].
- Olson also treats "the ratio of 'buts' to 'ands' in a speech" as "a useful diagnostic of good
  narrative". Clinton's speeches score near 1/5 and Trump's around 1/3 [verified: SciAm blog,
  Kuchner 2018]. A rhetoric historian in the same piece distrusts the ratio, so treat it as a rough
  lint, not a quality score.
- Measured here, but÷and×100 ranges from 6.5 (Branch memory video) to 38 (Primer); 20 ≈ 1/5 and
  33 ≈ 1/3 [measured].
  - Higher-turn channels (Primer, Kurzgesagt, Core Dumped, Reducible) use predict/contrast/twist
    beats.
  - Branch is a cumulative tour.
- Primer's **predict → run → explain → perturb** loop is the clearest repeatable "but" generator
  [inferred: transcripts].

**H. On-screen text and visual signalling (research)** [verified: Mayer 2023, Table 2–4].

| Principle | Effect size (d) | Tests | Implication for us |
|---|---|---|---|
| Temporal contiguity (words at the same time as the graphic) | 1.31 | 8/8 | Strongest; this is what word-timestamp sync buys |
| Modality (spoken rather than printed words) | 1.00 | 18/19 | Narrate rather than print |
| Personalization (conversational over formal) | 1.00 | 13/15 | Conversational register |
| Coherence (cut extraneous material) | 0.86 | 18/19 | Cut seductive details |
| Spatial contiguity (labels near their parts) | 0.82 | 9/9 | Labels next to the parts |
| Pre-training (introduce key concepts first) | 0.78 | 10/10 | Introduce names first |
| Signaling (highlight the essentials) | 0.70 | 26/28 | Highlights, arrows, emphasis |
| Segmenting (learner-paced parts) | 0.67 | 7/7 | Bounded chunks |
| Image (presenter's face on screen) | 0.19 | 4/7 | Face-cam adds little |
| Redundancy (don't caption the narration) | 0.10 | 8/12 | Weakest effect |

- The chapter allows "a minimal number of words on the screen—mainly, to help highlight the main
  points and to concretize technical or unfamiliar terms".
- That matches Artem's on-screen definitions, Reducible's labels and Core Dumped's single key
  sentence; Kurzgesagt sits at the extreme low end [inferred].

**I. Pacing numbers you can use** [measured; this sample].

| Channel | Narrated pace (span wpm) |
|---|---|
| Branch | 126–138 |
| Core Dumped (net; articulation 182–201) | 127–153 |
| Artem | 134–148 |
| Kurzgesagt | 143–152 |
| Reducible | 149–163 |
| Primer | 162–171 |
| Lague | 171–176 |
| minutephysics (short videos) | 212–234 |

- Pauses of ≥1 s run from ~0 per minute (minutephysics) to ~10–11 per minute (Core Dumped,
  Reducible A\*).
- Median sentence length runs from 14 (Primer, Kurzgesagt) to 24 words (Branch, Lague).

## 6. Cross-channel comparison

| Channel | Pace (span wpm; pauses ≥1 s/min) | Text density (OCR: % frames with text; words/frame) | Palette / ground | Toolchain (verified) | Narrative mode | Reproducibility with our code pipeline |
|---|---|---|---|---|---|---|
| Reducible | 149–163; 8–11 | 96.5%; 18.0 | Pure black; neon purple/yellow/green; CMU Serif + SF Mono | Manim (3b1b → CE) | Guided problem-solving; reinvent the algorithm | High |
| Artem Kirsanov | 134–148; 7 | 92.6%; 14.6 | Navy-black; neon glow; LaTeX serif | AE + Manim + matplotlib + Blender (+ Illustrator/Premiere/Audition) | Lecture-derivation with mystery hook + historical payoff | Medium-high |
| Primer | 162–171; 3–5 | 98.4%; 41.1 | Charcoal; off-white serif; 3D blobs on grass | Blender → Unity → Godot (own toolkit) | Simulation-as-experiment; predict → run → explain | Medium (2D layer high; 3D agents need an engine) |
| Sebastian Lague | 171–176; 7–8 | 97.9%; 25.4 (UI text) | Mid-grey canvas; orange chips; colour-coded wires | Unity (+ Shapes, VidTools) + Resolve | First-person build log | Low-medium (look yes, narrative needs a real project) |
| Kurzgesagt | 143–152; 5 | 22.2%; 0.8 | Indigo/violet + saturated glow; flat vector | Illustrator + After Effects (+ C4D trial), Pro Tools VO | Second-person essay; metaphor + stakes + twist | Low (art-bound); "lite" preset possible |
| minutephysics | 212–234 (short form); ≤0.7 | 85.7%; 5.5 (handwriting undercounted) | Warm black, light marker lines, colour only for physical colour | Paper, markers, still camera (2011) | Everyday paradox → physics → twist → punchline | Medium |
| Branch Education | 126–138; 6–7 | 100.0%; 19.5 (incl. watermark) | Photoreal; green mat / library; glow label cards | Blender + Premiere; team of animators | Guided physical tour + governing metaphor | Low (full); medium for a schematic variant |
| Core Dumped | 127–153 (articulation 182–201); 8–10 | 97.5%; 46.3 | Pure black; mono; yellow/green highlights; CPU photos | PowerPoint + ElevenLabs + Resolve | Question barrage → mechanism → code → demo | Very high |

## 7. What this implies for the style presets (short)

[inferred: from §3–6]

1. Parameterise each style on these axes:
   - **narrative mode** (guided problem-solving / lecture-derivation / simulation-experiment / build
     log / second-person essay / paradox-punchline / guided tour / question barrage)
   - **pace** (WPM + pause budget)
   - **text density** (labels-only ↔ code-heavy)
   - **layout grammar** (fixed zones)
   - **house kit** (palette, fonts, primitives)
2. Use the measured numbers in §3–6 as preset defaults and lint targets: questions per minute,
   "you"/"we" ratio, median sentence length, but÷and, and words per frame.
3. The cheapest new presets on our engine are Core Dumped-like, Reducible-like, and a schematic
   Branch-like style, then minutephysics-like. Kurzgesagt-like and Primer-like presets need an
   asset/3D strategy first.

## Sources

**Videos sampled** (YouTube; transcript = caption track, frames = 360p):
- Reducible: [How PNG Works](https://www.youtube.com/watch?v=EFUYNoFRHQI) (2022-03-29); [A* Search](https://www.youtube.com/watch?v=88I6IidylGc) (2024-07-27).
- Artem Kirsanov: [The Core Equation Of Neuroscience](https://www.youtube.com/watch?v=zOmhHE2xctw) (2024-11-02); [Your Brain Is 150,000 Mini-Brains](https://www.youtube.com/watch?v=Dykkubb-Qus) (2025-07-10); [How I make science animations](https://www.youtube.com/watch?v=yaa13eehgzo) (2023-08-07); [My Strategy To Consume Information Effectively](https://www.youtube.com/watch?v=OZ7LEB44B3E).
- Primer: [Simulating a single brain cell](https://www.youtube.com/watch?v=GkiITbgu0V0) (2025-09-27); [Simulating the Evolution of Rock, Paper, Scissors](https://www.youtube.com/watch?v=tCoEYFbDVoI) (2024-07-13).
- Sebastian Lague: [Simulating 256 Bytes of RAM](https://www.youtube.com/watch?v=HGkuRp5HfH8) (2025-04-12); [Coding Adventure: Simulating Fluids](https://www.youtube.com/watch?v=rSKMYc1CQHE) (2023-10-08); [Answering Your Questions](https://www.youtube.com/watch?v=kIMHRQWorkE) (2023-05-26).
- Kurzgesagt: [How Are Memories Stored Inside Your Brain?](https://www.youtube.com/watch?v=PqtggjVAi8M) (2026-06-16); [Our Minds Are Weirder than You Think](https://www.youtube.com/watch?v=dl0-TveDDGA) (2026-04-21); [How to Make a Kurzgesagt Video in 1200 Hours](https://www.youtube.com/watch?v=uFk0mgljtns) (2020).
- minutephysics: [The Color Temperature Paradox](https://www.youtube.com/watch?v=mqZm6u12RJA) (2024-07-24); [You're Technically HOTTER Than The Sun](https://www.youtube.com/watch?v=6tu0mIpX8nU) (2022-09-08); [We Used To Have No Idea How Sight Worked](https://www.youtube.com/watch?v=5qYRfCnIITk) (2026-11-12); Sixty Symbols, [Making Minute Physics](https://www.youtube.com/watch?v=YoQcg39Krvk) (2011); [minutephysics Behind the Scenes – Teleportation (transcript)](https://rosetta.to/u/minutephysics/minutephysics-behind-the-scenes-teleportation).
- Branch Education: [How do CPUs Work?](https://www.youtube.com/watch?v=16zrEPOsIcI) (2025-11-15); [How does Computer Memory Work?](https://www.youtube.com/watch?v=7J7X7aZvMXQ) (2022-11-04).
- Core Dumped: [What Happens When a CPU Receives an Unknown Instruction?](https://www.youtube.com/watch?v=WtlGB-YVLOg) (2026-08-27); [How CPUs Run Functions](https://www.youtube.com/watch?v=7YyALikxAlU) (2026-02-07); [You Wouldn't Stop Asking Me The Same Questions](https://www.youtube.com/watch?v=9MVk1DHJn2o) (2025-12-20).

**Creator sites and repos:**
- [nipunramk/Reducible](https://github.com/nipunramk/Reducible) (README; `2022/common/reducible_colors.py`, `classes.py`)
- [Helpsypoo/primerpython](https://github.com/Helpsypoo/primerpython)
- [Helpsypoo/PrimerUnity](https://github.com/Helpsypoo/PrimerUnity)
- [Primer-Learning/PrimerTools](https://github.com/Primer-Learning/PrimerTools)
- [SebLague/VidTools](https://github.com/SebLague/VidTools)
- [Kurzgesagt — Our video process](https://kurzgesagt.org/youtube/)
- [Kurzgesagt 1200 hours transcript (rosetta.to)](https://rosetta.to/u/kurzgesagt/how-to-make-a-kurzgesagt-video-in-1200-hours)
- [Branch Education site](https://brancheducation.pages.dev/)
- Artem Kirsanov GitHub (BlenderSpike, BlenderBrain), linked from the process video description.

**Tools:**
- [Manim CE installation FAQ (versions)](https://docs.manim.community/en/stable/faq/installation.html)
- [manim-voiceover docs](https://voiceover.manim.community/en/stable/)
- [Motion Canvas README](https://github.com/motion-canvas/motion-canvas)
- [Motion Canvas time events](https://motioncanvas.io/docs/time-events)
- [Remotion LICENSE](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md)
- [Remotion captions docs](https://www.remotion.dev/docs/captions/)
- [Apple Education — Keynote Magic Move resources](https://education.apple.com/resource/250013992)
- [WIRED: Derek Muller answers the web's most searched questions (transcript)](https://rosetta.to/u/wired/veritasium-s-derek-muller-answers-the-web-s-most-searched-questions-wired)

**Guidance and research:**
- R. E. Mayer, [Research-Based Principles for Designing Multimedia Instruction](https://www.unh.edu/teaching-learning-resource-hub/sites/default/files/media/2023-06/itow-research-based-principles-for-designing-multimedia-instruction-mayer.pdf) (APA Div. 2, 2023)
- Craig & Schroeder (2017), *Reconsidering the voice effect when learning from a virtual human*, Computers & Education 114 (cited via Mayer 2023 and [ReadSpeaker summary](https://www.readspeaker.com/blog/elearning-voice))
- Muller & Sharma, [Tackling misconceptions in introductory physics using multimedia presentations](https://openjournals.library.sydney.edu.au/IISME/article/view/6345)
- [Scientific American profile of Derek Muller](https://www.scientificamerican.com/article/how-youtube-star-derek-muller-of-veritasium-is-challenging-scientific/)
- [NCSE: And, But, Therefore — Randy Olson](https://ncse.ngo/and-therefore-randy-olson-and-art-science-storytelling-part-1)
- M. Kuchner, [How the word "but" could save the world](https://www.scientificamerican.com/blog/observations/how-the-word-but-could-save-the-world/) (Scientific American blog, 2018)
- [EdSurge: Behind the scenes of TED-Ed](https://edsurge.com/news/2018-08-16-behind-the-scenes-of-ted-ed-s-wildly-popular-youtube-channel-for-students) (2018)
- [UW Continuum script writing guide](https://instructorresource.continuum.uw.edu/technology/instructional-video/script-writing-guide/)
- [YouTube Creator Playbook tips: the first 15 seconds](https://blog.youtube/creator-and-artist-stories/youtube-creator-playbook-tips-first-15)
- [MinuteEarth — How we make MinuteEarth videos (transcript)](https://rosetta.to/u/minuteearth/how-we-make-minuteearth-videos-behind-the-scenes)

**Data services:** [SponsorBlock API](https://sponsor.ajay.app/) (segment exclusion); yt-dlp 2026.10.26; RapidOCR; textstat.
