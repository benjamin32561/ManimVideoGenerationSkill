# Welch Labs (Stephen Welch): style research

Phase 1 of adding a second style to `manim-explain`. This is a description of the style, not a render-engine evaluation.
3D camera flights exist in almost every recent Welch Labs video. They are noted here but not studied.

Tags: **[verified: source]** means a primary source states it: Welch's own words, a job post, repo code or comments, or the video itself.
**[inferred: from what]** is my reading of the evidence. **[measured]** comes from the scripts listed in §10.
Timestamps are `mm:ss` in the video named.

**Sample (8 videos).** Seven are from the AI era; the 2015 one is for contrast.

| # | Video | Date | Length | URL |
|---|---|---|---|---|
| A | The moment we stopped understanding AI [AlexNet] | 2024-07-01 | 17:38 | https://www.youtube.com/watch?v=UZDiGooFs54 |
| B | The Dark Matter of AI [Mechanistic Interpretability] | 2024-12-23 | 24:09 | https://www.youtube.com/watch?v=UGO_Ehywuxc |
| C | How DeepSeek Rewrote the Transformer [MLA] | 2025-03-05 | 18:09 | https://www.youtube.com/watch?v=0VLAoVGf_74 |
| D | The F=ma of Artificial Intelligence [Backpropagation, How Models Learn Part 2] | 2025-06-11 | 30:31 | https://www.youtube.com/watch?v=VkHfRKewkWw |
| E | The most complex model we actually understand [grokking] | 2025-12-20 | 35:28 | https://www.youtube.com/watch?v=D8GOeCFFby4 |
| F | Can humans make AI any better? [the Bitter Lesson] | 2026-01-31 | 23:39 | https://www.youtube.com/watch?v=2hcsmtkSzIw |
| G | Yann LeCun's $1B Bet Against LLMs [Part 1] [JEPA] | 2026-05-02 | 37:24 | https://www.youtube.com/watch?v=kYkIdXwW2AE |
| H | Imaginary Numbers Are Real [Part 1: Introduction] | 2015-08-28 | 5:47 | https://www.youtube.com/watch?v=T647CGsuOVU |

Also used as a process source: *Channel Update [April 2017]*, https://youtu.be/gZPy7OxAjRM, in which Welch walks through his own process.

---

## 1. Snapshot

- **Who.** Stephen Welch runs Welch Labs. He started the channel in 2014 and went full time in 2024 [verified: Aperiodical 2025-06-30]. He quit in 2019 because the channel didn't pay enough, worked as an ML engineer, came back through TikTok from 2022, and in 2024 earned "about half of what I made as a machine learning engineer" [verified: video D 28:00–29:30]. He describes the team as "me and a couple freelancers right now" [verified: Aperiodical]. The roles listed on welchlabs.com/jobs (fetched 2026-11-21; posting dates not shown) are freelance designer, video editor, Manim animator and technical research assistant [verified]. In video F (21:00) he says "the Welch Labs team and I have written a whole new book" [verified].
- **Topics.** Before 2024 the channel made math and ML *series* of 3–14-minute parts: *Imaginary Numbers Are Real* (13 parts), *Learning to See* (15), *How to Science*, self-driving cars, and Manhattan Project shorts. Since 2024 it has made long single videos on modern AI: AlexNet, perceptron, backprop, DeepSeek MLA, mechanistic interpretability, grokking, double descent, subliminal learning, VLA, JEPA, ResNets and world models. A few math and physics videos sit in between (Euler's formula, the i in Schrödinger's equation, Kepler). There is also a guest video on 3Blue1Brown's channel, "But how do AI images and videos actually work?" (2025-07-25, https://www.youtube.com/watch?v=iv-5mZ_9CPY) [verified: 3blue1brown.com/lessons/diffusion-models]. The repo's `_2025/sora` folder (diffusion, CLIP and flow-matching notebooks and scenes) matches that video [inferred]. I did not analyse it.
- **Audience.** "Enthusiastic high schoolers, college students, and really anyone interested in this stuff with some level of technical background" [verified: Aperiodical]. Welch's aim is that viewers "walk away understanding a really compelling set of deeper 'why's'" [verified: Aperiodical].
- **Length.** Welch says videos run "typically around 20 minutes" [verified: Aperiodical, mid-2025]. Measured over the 22 uploads from May 2024 to Nov 2026, the medians are 23.4 min for 2024 (n=8), **31.8 min for 2025** (n=8) and **36.3 min for 2026** (n=6); the longest is 42.9 min [measured]. The 2015 series parts ran 3–14 min.
- **Cadence.** His target is one video a month [verified: Aperiodical]. Measured over the same 22 uploads, the median gap is **39 days** (mean 44, range 22–94) [measured].
- **Business shape (it shapes the script).** Most videos have a sponsor read (KiwiCo, Incogni, Tufa Labs, Hudson River Trading) and end on a pitch for posters, the book or Patreon [verified: descriptions and transcripts]. Patreon members get "a real paper cutout used in a Welch Labs video… going all the way back to 2017" [verified: video D 29:50]. Physical props are part of the product.
- **Reach.** Imaginary Numbers Part 1 has 8.6M views; AlexNet 2.6M; DeepSeek 1.0M; LeCun Part 1 1.3M [verified: yt-dlp metadata, 2026-11-21].

## 2. Production pipeline & tools

### Stages, with evidence

| Stage | What happens | Evidence |
|---|---|---|
| Idea | He tries "to ask the most compelling and clear question I can, and answer it as effectively as possible." The topic converges during research; the imaginary-numbers series began as a Fourier-transform series. | [verified: Aperiodical; 2017 update 2:40] |
| Research | "I spend a ton of time on research," with a focus on history and context. A paid research assistant does literature reviews, "organize[s] sources to support script writing", builds "technical demonstrations/code… in Python & Pytorch" and "develop[s] and iterate[s] on scripts with Stephen". Notebooks run real models (GPT-2, Llama 3.2-1B, Gemma, DeepSeek V3 weights) and export the data that becomes visuals. | [verified: Aperiodical; jobs/technical-research-assistant; repo README ("hacking scripts… notebooks"); video C 17:30 "the matrix images… are actually from the real DeepSeek model"] |
| Script | 2017: a research ↔ writing "death spiral" in "a mostly empty Microsoft Word document" until "a half-decent script" exists, then editing. He now co-iterates with the research assistant. Where today's script lives is not stated. | [verified: 2017 update 1:39–3:06; jobs]. Location unknown. |
| Script units ("p-numbers") | Scene files are named by numbered script units (`p14_18.py`, `p78_85.py`, `P84_85.py`), and sub-beats get letters (`p32c`, `p75a/p75bb/p75d`, `p48b`). Comments treat them as script paragraphs: "# Paragraph 83" inside `p78_85.py`, "Ok now 3d Paragraph 48" inside `p45_51_book_graphics.py`, "run_time=20 … this covers a couple paragraphs", "after i rewrite these paragraphs I'll come figure out the animatino". One comment ("the first paragraph of p80") suggests a unit can hold more than one paragraph. | [inferred from repo comments: **p = numbered script paragraph / storyboard unit**. A scene file covers one unit or a contiguous range of them: `p21`, `p14_18`, `p41_58`, `p27_48`. Videos run to about p65–p85.] |
| Storyboard | 2017: "Video production starts with storyboarding and recording narration… The real issue is thinking of visuals that I actually have the skills to create." Now: full-fidelity **Illustrator artboards at 1920×1080**, named after the paragraph range plus an artboard number (`p43_59-11.svg/.png`), with direction notes typed into the frame ("Ok yeah so I think we show one column coming in at a time here… I'm 50/50 on this, we'll see."). A Notion database holds storyboard and notes, and a notebook (`notion-client` + `reportlab`) exports it to PDF. Animators receive "storyboards and technical direction". | [verified: 2017 update 3:08–3:23; repo `_2026/world_models/p50_59_storyboard/`, `p63_64_sketches/`; `_2025/tooling/notion_storyboard_to_pdf_1.ipynb`; comments "See notes in notion!"; jobs/freelance-manim-animator] |
| Voiceover | Welch narrates himself. In 2017 narration was recorded at the start of production, together with the storyboard. Scene code is written knowing the VO length ("I think I'll have time with the VO"), and sometimes the VO is changed to suit the animation ("tweak the VO to give a little more space for it?"). A freelance editor does "Edit narration audio". | [verified: 2017 update; repo `jepa_2/P67_75.py`, `generalization/p46_56.py` comments; jobs/freelance-video-editor] |
| Animation (code) | **manimgl** (3Blue1Brown's Manim, not Community), driven interactively: `self.embed()` appears 553 times, a Sublime Text "checkpoint paste" plugin is used, and a SHIFT+D helper copies the current camera pose as a `reorient(...)` call. It renders 4K at 30 fps. Since 2025 there are also LLM helpers: "Ok claude, now … I want to shade the area…", "Let's ask my buddy Claude", plus `p21_cursor_*.py` files. Freelancers "Submit animations as pull requests" (e.g. `network_pranav_pr_1.py`, `*_pranav.py`). | [verified: repo README, `custom_config.yml`, `sublime_custom_commands/`, `custom/welch_tools.py`, comments in `generalization/p65_68.py` and `sora/p40_51_book.py`; jobs] |
| Animation (non-code) | **Illustrator** for labels, overlays, network diagrams, equations and shaded regions, often imported back into Manim as SVG (`graphics/to_manim/*.svg`). **After Effects** for some graphics ("either in pure manim or AE exports"). **Overhead practical shoots** of paper cutouts, printed papers, hand drawings and props on a wooden desk. The 2017 rig was "a light box with a few clamp lights and a simple overhead camera", plus "a five axis motion rig I built from camera sliders… controlled from an IPython notebook". In 2025 he describes "a blend of overhead 'hand drawing' graphics and digital animations, many using manim". | [verified: repo comments in `backprop_2/book_animation_6.py` ("Illustrator is the way to go! 3d sucks for this!"), `backprop_3/p35_41.py` ("Bring in illustrator overlay of full newtwork!"), `p44_46_old.py` ("AE exports"); job posts (designer: Illustrator, After Effects, Premiere, InDesign); 2017 update 3:23–4:03; Aperiodical] |
| Edit / composite | **Adobe Premiere**: stitching scene renders, hiding glitches, blends, pans, late labels. Examples: "there is a little jump here -> I'm going to try to fix/hide it in premiere", "try blending in premiere!", "pan to the left in premiere, bring in the text, and replay the animation", "we pretty much hold this view and highlight stuff in editing". The editor role asks for "3+ years experience in Adobe Premiere". Colour correction appears in 2017. | [verified: repo `backprop_2/p44_46.py`, `backprop_3/p64_parallel.py`, `backprop_1/p39_48.py`, `deepseek/p34_42.py`; jobs; 2017 update 4:09] |
| Book / merch | *The Welch Labs Illustrated Guide to AI*. Vol. I has 9 chapters (perceptron, gradient descent, backprop, deep learning, AlexNet, neural scaling laws, mechanistic interpretability, attention, video & image generation), and "each chapter goes along with a Welch Labs video". Vol. II covers ResNets, RL, grokking, VLA and JEPA. Chapters carry exercises, Python code and a GitHub repo. In the repo, `book_*`, `*_merch.py`, `poster_*.py` and `thumbnail_hacking*.py` are re-renders of video scenes for print, posters and thumbnails, and the designer lays out book chapters in Illustrator/InDesign. | [verified: welchlabs.com/ai-book; video F 21:00–23:39 + chapter-listing frame at 22:50; repo filenames; jobs/editor] |

**Blender, DaVinci Resolve, Figma, Keynote.** I found no evidence that any of them is used [searched repo, job posts and interviews].
**How a talking-head or overhead shoot is planned today.** Not documented anywhere I could find.

### The pipeline as a chain

```
question → research (+ RA lit review, PyTorch notebooks on real models)
  → script in numbered paragraphs (p1…p85), iterated with RA
  → storyboard: Notion DB + Illustrator 1920×1080 artboards per paragraph range, with direction notes
  → VO recorded by Stephen (edited by freelancer)
  → per-paragraph-range manimgl scenes (Stephen + freelance animators via PRs, LLM coding help),
     data from notebooks (.npy/.png), labels/diagrams from Illustrator SVGs
  → overhead practical shoots (paper cutouts, printouts, props, hands), talking head, clips
  → Premiere: cut to VO, overlays, dissolves, sponsor + outro
  → re-render scenes as book figures / posters / thumbnails
```
The ordering of VO relative to animation is [inferred]. 2017 places it at the start. The 2025–26 comments show the VO existing while scenes are coded and being trimmed to fit.

### Code-level facts that matter for a pipeline [verified: repo]

- Scene timing is not driven by audio. Nothing in the repo syncs to audio; the only `.wav` reads in `the_bitter_lesson/p5.py` feed waveform *visuals*. Scenes are paced with `self.wait()`: 4,850 bare 1-second waits and 385 `self.wait(20)` tails. Run times are long: modal 3 s and 2 s, with 5–10 s common.
  - [inferred] Renders are generous takes with handles, and the cut to the VO happens in Premiere.
- `move_to([x,y,z])` with literal coordinates appears 3,267 times, against 820 `next_to(...)` calls. Layout is hand-placed and tuned live in `embed` mode.
- Emphasis is done with `set_opacity` (3,584 calls; most common values 0.5, 1.0, 0.0, 0.8, 0.3) and `set_color` (4,247). Stock emphasis animations are almost unused: `Indicate` 8, `Flash` 6, `Circumscribe` 0.
- Text: `Tex(` 1,502 against `Text(` 458. Fonts are Myriad Pro (~240 uses across spellings), Georgia 20, Helvetica 14, **American Typewriter 12** (the Harpy-era labels in F) and Minion Pro 4. The most common `font_size` is 24 (207 uses), then 32, 20, 28 and 22.
- Assets: `ImageMobject` 666 times (heatmaps and photos exported from notebooks) and `SVGMobject` 394 times (Illustrator exports).

## 3. Script writing process & structure

### Process

- **Research and writing alternate until the explanation becomes clear** [verified: 2017 update]. "After a few days of this I realize that I have no idea how the very simplest and most fundamental part of what I'm trying to explain actually works." The reframe that comes out of that becomes the script's spine: the Fourier series turned into the imaginary-numbers series.
- **Visual feasibility is a script constraint** [verified: 2017 "thinking of visuals that I actually have the skills to create"]. Code comments show the script being adjusted during animation: "Can already tell that I probably want a more detailed play by play in the narration", "Might work better with some script tweaks", "It's a quick line in the script… but I think it's pretty important pedagogically" [verified: repo `backprop_3/p35_41.py`, `backprop_2/p44_46_old.py`].
- **A fact check runs alongside the script.** One example is the technical-notes blog post for F, covering phoneme graph sizes, LPC order and distance metric [verified: welchlabs.com blog 2026-01-31]. He also shares notebooks, e.g. the Gemma walkthrough Colab linked from B [verified: B description].

### Structural template (observed in A–G) [inferred from transcripts + frames]

1. **Cold open on a concrete artifact or moment, 0:00–1:00.** No "welcome back", no agenda slide. Openers seen:
   - historical anecdote: D opens on Werbos and Minsky in the early 1970s; F on ARPA in 1971;
   - real artifact: A opens on an activation atlas; C on DeepSeek's papers on the desk;
   - provocation: E opens "No one understands modern AI.";
   - question: B opens "how would you know if a large language model was lying to you";
   - interview clip: G opens on LeCun.
2. **Early sponsor tag.** "This video is sponsored by KiwiCo, more on them later" appears within the first ~40 s in A and C [verified].
3. **The driving question, stated as a "how exactly" or "why" sentence.** C (1:00): "how exactly was the DeepSeek team able to squeeze such a significant improvement out of such a broadly used architecture". E (1:00) makes a thesis claim instead: "I'm going to claim that one specific example… is the most complex AI model we actually understand."
4. **Build from the ground up on one running example that persists for the whole video.** A real model on a real input, never an abstract x:
   - "The American flag is red, white, and" → *blue* (C);
   - "The capital of France is" → *Paris* through Llama (D, E, G);
   - longitude → Madrid/Paris/Berlin toy model (D);
   - "tell me about China" (F); "Mr. and Mrs. Dursley of number four" (F);
   - (x + y) mod 113 (E).
5. **Sponsor mid-roll at 24–59 % of runtime.** Chapter start / runtime: B 29 %, G 24 %, F 45 %, A 54 %, C 59 %; D puts it at 7 % [measured from chapter markers]. It is always bridged back in with "Now back to …" [verified: C 12:20, F 11:45].
6. **Scale-up to the real system with real numbers.** The toy mechanism is re-run on production dimensions: "61 layers… 7,808 patterns", "4 megabytes per token… 400 gigabytes" (C); "Llama 3.2… 1.2 billion parameters" (D).
7. **Resolution with a measured result.** "only 70 kilobytes per token, a 57x reduction" (C 16:05), shown as a table row.
8. **Zoom-out and personal take.** "My take here is that…" (F 20:27). A near-formula closing line: "it will be fascinating to see …", which appears in B, C, E and F [verified in transcripts].
9. **Callback.** The opening visual or clip returns: Werbos/Minsky quotes plus the Llama animation at D 27:50, the Harpy poster at F 20:00, the LeCun clip at G 35:00. Series episodes end on a hook: "Next time, we'll see what Minsky missed." (D 28:00).
10. **Commercial and personal outro.** Book, poster or Patreon pitch, often 1–3 minutes long (F's book pitch runs 2.5 min), and a black "Special Thanks to Patreon Supporters" card.

### Introducing jargon and math [inferred from transcripts and frames, counts in §4]

- **Show first, then name it with "called / known as".** "Attention works by computing matrices called attention patterns. These are the 144 attention patterns computed by the GPT-2 small model…" (C 1:35). "In the jargon of reinforcement learning, an agent's policy determines…" (F 12:00). The on-screen caps label arrives with the term.
- **Every symbol is grounded in a real dimension.** "GPT-2 small's embedding dimension is 768 and DeepSeek R1's… is 7168" (C 3:40), with `d=768` drawn on a bracket and `9×768` printed under the matrix.
- **Equations are built from plugged-in numbers.** In D the loss is computed as −ln(0.086) = 2.45 on paper cards and then in Manim, before the symbolic ∂L/∂h = ŷ − y is derived and boxed (D 7:00–14:30).
- **Analogy as a single picture, not an extended metaphor.** A full Harry Potter book stands for a 100k-token context (C 7:10–7:40). LeCun's cake is shown as a real cake photo (G 4:15). A clock face stands for modular arithmetic (E 17:00).

### History and story [verified frames/transcripts]

- History is the default frame, not a garnish:
  - D is framed by Werbos vs Minsky (1970s→2010s);
  - F by ARPA 1971 → Harpy 1976 → HMMs → Sutton 2019 → Dwarkesh podcast 2025;
  - A by McCulloch-Pitts 1943 → perceptron 1957 → backprop 1986 → LeNet 1989/98 → AlexNet 2012, drawn as a timeline.
- Primary sources appear on screen:
  - printed papers clipped with binder clips on the desk;
  - book pages with italic pull quotes and attribution;
  - archival photos on cards (Widrow and Hoff at D 11:00);
  - podcast and interview clips with a source caption.
- He interviews the protagonist himself: LeCun in G, credited "Special thanks to: Yann LeCun…" [verified: G description].

### Humour [inferred: rare, dry, mostly visual]

- 2015: stick figures with speech bubbles ("Bro, how many water buffalo are over there?", H 3:00).
- 2017: self-deprecating process jokes ("Narrating is super easy and I basically always get everything right on the first…").
- 2024–26 humour is a short visual gag inside a serious beat:
  - ChatGPT answering "Why is metal shiny?" as if trained in 3000 BCE ("Animal spirits inside the metal") or 1000 CE ("God made it that way") (F 19:00–19:25);
  - a printed "phone call from toddler jail?" in the Incogni read (D 2:20);
  - a staged rebuttal at the end of A ("are you mad that I called the blocks of compute dumb?").
- No running jokes and no character.

### Endings [verified transcripts]

- Open questions are stated as questions, about four in a row: "So, have we learned the bitter lesson or are we just repeating it? … And if so, is reinforcement learning the answer?" (F 20:00).
- Then a hedged personal view ("I'm more skeptical about…"), a forward-looking "it will be fascinating to see…", and the outro.

## 4. Language profile

### Method

[measured]
- **Corpus.** Welch's narration only. Sponsor, book, Patreon and update chapters are removed using the videos' own chapter markers. Interview and podcast speech in F and G is removed at the `>>` speaker-change markers (1,377 words in G, 326 in F).
- **Rates.** WPM and pauses come from the onset times of auto-caption words. "Pause" means an inter-onset gap of ≥ 1.0 s, which is about ≥ 0.6 s of silence after an average word.
- **Sentences.** Only H has a manual caption track. For A–D, punctuation was restored with a punctuation model; E–G come with YouTube's newer punctuated ASR.
  - Validation on H: the model found 59 sentences against 52 in the manual track (mean 16.0 vs 18.2 words) and 4 questions against 6. So model-punctuated sentence lengths run about 10 % short, and model question counts run low.
  - Validation on F: re-punctuating YouTube's ASR text with the model gives the same 119 sentences and the same mean of 22.3 words (median 21 vs 19), with 8 questions vs 9. The two machine sources are comparable.
  - Questions = sentences ending in "?" plus sentences opening with a question word or inverted auxiliary (a "when…" opener doesn't count).
- **Pronouns.** Counts per 1,000 words. "we" includes us, our and let's.
- **Readability.** FK = Flesch-Kincaid grade.

### Rate, rhythm, sentences, person

| Video | Narration min | Words | WPM (gross) | Articulation WPM | Pauses /min | Time in pauses % | Punctuation source | Sentences | Mean words/sent | Median | p90 | % > 30 words | Questions /100 sent | Questions /min | I /1k | we /1k | you /1k | FK grade |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A AlexNet | 15.6 | 2752 | 176 | 178 | 7.7 | 8 | model | 126 | 21.8 | 20 | 37 | 21 | 2.4 | 0.19 | 1.5 | 17.4 | 3.6 | 11.0 |
| B Dark matter | 22.2 | 3799 | 171 | 173 | 10.2 | 11 | model | 162 | 23.5 | 22 | 36 | 18 | 6.8 | 0.50 | 0.0 | 49.5 | 1.6 | 12.1 |
| C DeepSeek | 16.6 | 2806 | 169 | 172 | 10.1 | 12 | model | 119 | 23.6 | 22 | 40 | 25 | 1.7 | 0.12 | 2.5 | 34.2 | 2.9 | 12.3 |
| D Backprop 2 | 28.2 | 4858 | 172 | 181 | 8.4 | 14 | model | 250 | 19.5 | 18 | 30 | 9 | 0.0 | 0.00 | 8.0 | 74.5 | 1.2 | 10.3 |
| E Grokking | 33.4 | 5246 | 157 | 173 | 9.6 | 17 | YouTube ASR | 263 | 19.9 | 17 | 36 | 16 | 8.0 | 0.63 | 1.7 | 57.6 | 2.3 | 10.2 |
| F Bitter lesson | 17.5 | 2653 | 152 | 166 | 9.5 | 17 | YouTube ASR | 119 | 22.3 | 19 | 43 | 20 | 7.6 | 0.51 | 4.5 | 18.5 | 0.0 | 11.8 |
| G JEPA pt1 | 26.2 | 3940 | 150 | 172 | 12.6 | 23 | YouTube ASR | 139 | 28.3 | 24 | 53 | 36 | 3.6 | 0.19 | 1.3 | 25.4 | 0.3 | 14.9 |
| **Median A–G** | 22.2 | 3799 | **169** | **173** | **9.6** | **14** | – | 139 | **22.3** | **20** | **37** | **20** | **3.6** | **0.19** | 1.7 | **34.2** | **1.6** | 11.8 |
| H 2015 (contrast) | 5.8 | 944 | 163 | 182 | 6.2 | 12 | manual | 52 | 18.2 | 18 | 27 | 2 | 11.5 | 1.04 | 4.2 | 43.2 | 2.1 | 9.8 |

### Signposting and stance markers

Values are per 1,000 words, except the four "sentence-initial" rows, which are % of sentences.

| Marker | A | B | C | D | E | F | G | H | Median A–G |
|---|---|---|---|---|---|---|---|---|---|
| "So …" (sentence-initial, %) | 0.0 | 5.6 | 3.4 | 4.8 | 6.8 | 5.0 | 4.3 | 9.6 | 4.8 |
| "Now …" (sentence-initial, %) | 1.6 | 3.1 | 3.4 | 4.0 | 4.6 | 1.7 | 1.4 | 3.8 | 3.1 |
| "And …" (sentence-initial, %) | 0.8 | 0.0 | 0.8 | 5.6 | 5.7 | 10.9 | 2.9 | 9.6 | 2.9 |
| "But …" (sentence-initial, %) | 0.0 | 1.2 | 1.7 | 1.2 | 4.6 | 3.4 | 2.2 | 3.8 | 1.7 |
| this / these / here (pointing at the visual) | 19.6 | 22.9 | 13.9 | 22.0 | 28.8 | 15.5 | 17.8 | 27.4 | 19.6 |
| digit tokens (dims, counts, results) | 12.4 | 18.2 | 13.9 | 15.4 | 26.1 | 7.9 | 11.7 | 21.1 | 13.9 |
| naming: "called / known as / referred to as" | 3.3 | 2.4 | 3.6 | 1.6 | 1.5 | 4.1 | 3.3 | 1.1 | 3.3 |
| really / actually | 2.2 | 0.8 | 3.2 | 2.9 | 4.2 | 3.8 | 2.3 | 6.3 | 2.9 |
| hedges (kind of, roughly, maybe, might, seems…) | 4.0 | 2.6 | 2.1 | 1.4 | 2.1 | 4.9 | 1.0 | 4.2 | 2.1 |
| years (1500–2029) | 2.5 | 1.1 | 1.8 | 0.8 | 0.8 | 2.3 | 4.3 | 0.0 | 1.8 |
| intensifiers (incredible, remarkable, clever, elegant…) | 4.0 | 1.1 | 1.8 | 1.2 | 3.4 | 1.1 | 0.5 | 1.1 | 1.2 |
| "we saw / we'll see" (back/forward references) | 0.0 | 0.5 | 0.0 | 2.1 | 2.5 | 0.8 | 1.0 | 0.0 | 0.8 |
| "fascinating / remarkable" | 1.5 | 0.8 | 0.7 | 0.4 | 1.5 | 1.1 | 0.3 | 0.0 | 0.8 |
| "let's" | 0.0 | 3.2 | 0.7 | 1.9 | 3.6 | 0.0 | 0.0 | 4.2 | 0.7 |
| "note that" | 0.0 | 0.8 | 0.7 | 0.8 | 0.4 | 1.1 | 0.3 | 0.0 | 0.7 |
| for example / for instance | 0.4 | 0.0 | 0.7 | 0.4 | 0.8 | 0.8 | 0.5 | 0.0 | 0.5 |
| exactly | 0.0 | 0.5 | 0.7 | 0.4 | 0.6 | 0.4 | 1.0 | 2.1 | 0.5 |
| "I think / my take / I like" | 0.0 | 0.0 | 0.4 | 0.4 | 0.6 | 0.4 | 0.0 | 0.0 | 0.4 |
| "it turns out" | 0.0 | 0.0 | 0.0 | 0.6 | 0.6 | 0.8 | 0.3 | 1.1 | 0.3 |
| "in other words" | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

**Phrases shared across videos** [measured: 3- and 4-grams present in ≥ 5 of the 8 videos]:

- "(the idea / key insight) here is that" (7 videos)
- "we can see" (6)
- "we need to" (6)
- "and so on" (6)
- "it turns out" (5)
- "is known as" (5)
- "to figure out" (5)
- "the output(s) of" (5)
- "the number of" (5)

### Patterns

[inferred from the numbers above and close reading]

- **Fast and dense, steady rhythm.**
  - About 170 wpm when speaking, with short and frequent pauses: about 10 per minute, mostly well under a second.
  - Long silences are rare; the longest is 2–6 s.
  - Sentences are long (median 20 words, about one in five over 30) and often carry an appositive definition. Example (C 1:30): *"The interactions between tokens in large language models are handled by a mechanism called attention."*
- **"We", almost never "you".**
  - The narrator and viewer *do* the computation together: "we take the input matrix X", "our model", "our example input". The median is 34 "we" per 1k words against 1.6 "you" per 1k.
  - "I" is rare in explanation and concentrated in asides and outros: tinkering with the code (C 10:45), "My take here is…" (F 20:27), and D's "The time I quit YouTube" chapter (28:13). That chapter is not a promo, so it stays in the corpus, which is why D has the highest I-rate (8.0).
- **Pointing language** (~20 this/these/here per 1k words). The narration constantly points at what's on screen. Example (C 2:35): *"This first attention pattern in the third layer of GPT-2 has a high value mapping from the input token of American to the output token of flag."*
- **Exact numbers are part of the voice** (median 14 digit tokens per 1k words): "7,808 patterns", "a dimension of 768", "an Elo rating of 1517", "57x". Numbers are spoken as results, not hedged.
- **Questions are rare and placed at pivots** (median 0.19/min). Examples: *"But how exactly was the DeepSeek team able to squeeze such a significant improvement out of such a broadly used architecture?"* (C 1:00) and *"So, is Sutton right?"* (F 8:45).
  - Clusters of questions open an investigation: B asks five "why" questions in 20 s at 1:54–2:13, right after the cold open; E asks four at 0:30–1:00.
  - Clusters also close the video: F asks four in a row at 20:00.
  - D has none detected; it is driven by derivation rather than inquiry.
- **Naming formula.** About one "called / known as" per 300 words, the term arriving *after* its role has been described. There are no glossary dumps.
- **Plain register, low hedging, low hype.**
  - Hedges and intensifiers are each about 1–2 per 1k words.
  - Evaluation is reserved for a few beats: "really clever", "really elegant solution", "remarkable".
  - The stock closer: *"it will be fascinating to see…"* (B, C, E, F).
- **Grade level about 12** (FK median 11.8). That is consistent with the stated audience of "some level of technical background".
- **2015 contrast (H).** Shorter sentences (median 18, almost none over 30), five times more questions (1.04/min), more "So…/And…" openers, and more "really". The 2024+ voice is more declarative and documentary, with the investigation carried by the visuals rather than by rhetorical questions.
- **Caveat on the drift.** E–G (Dec 2025 onward) show slower gross WPM (150–157) and more pause time (17–23 %) than A–D (169–176 wpm, 8–14 %). That may be a real pacing change. It may also come from the different caption generation: E–G use the newer punctuated ASR, whose word timings could differ. I can't separate the two causes.

## 5. Flow

Two beat sheets: one data/equation-heavy video (C) and one history/argument video (F). "Shown" describes the frame; "On-screen text" is what is written on screen, with backticks marking literal text. All of it is [verified: frames every 5 s + transcript], timestamps ±5 s.

### C. How DeepSeek Rewrote the Transformer [MLA] (2025-03-05, 18:09)

| Time | Said (paraphrase / short quote) | Shown | On-screen text |
|---|---|---|---|
| 0:00–0:05 | "This video is sponsored by KiwiCo, more on them later." | KiwiCo logo on the wooden desk | logo only |
| 0:05–0:35 | Jan 2025, R1 "shocked the world"; DeepSeek published its weights, inference code and "one report per month in 2024". | Overhead: R1 paper printout pulled toward camera; pull-back to a desk tiled with clipped DeepSeek papers; a hand slides them | the printed papers themselves |
| 0:35–1:00 | MLA "strikes at the core of the transformer"; KV cache shrinks "by a factor of 57", text generation is ">6× faster". | The MLA paper is placed down, then cut to the finished MLA Manim diagram on black, which tilts into 3D (preview of the payoff) | matrix captions, `L_KV = XW_DKV`, `A = Softmax(QKᵀ/√d)` |
| 1:00–1:15 | "But how exactly was the DeepSeek team able to squeeze…" | DeepSeek chat screen recording, then Welch at his desk (talking head) | UI text |
| 1:15–1:35 | Autoregression: each token is a function of all previous tokens. | Paper cutout tokens "Deep Seek is a large" → DeepSeek card → "language"; then `f( … ) = model` with a yellow arrow | paper tokens; `f`, `=` |
| 1:35–2:10 | Attention patterns: GPT-2 has 12×12 = 144; R1 has 128×61 = 7,808. | Hands arrange printed attention-pattern cards in a wooden tray. Manim grid over dark wood, then a GPT-2 vs R1 grid with a yellow inset box | `GPT-2 ATTENTION PATTERNS`, `Input text: The American flag is red, white, and`, `12 Layers`, `12 Attention heads per layer`, `GPT-2` (yellow), `DeepSeek R1` (cyan), `61 Layers`, `128 Attention heads per layer` |
| 2:10–3:10 | Reading one pattern: American→flag (a modifier); the last head pulls flag, red, white → predicts *blue*. | One 9×9 pattern with token labels on both axes; magenta arrows; 🏳️→🇺🇸 icon; "blue" appears in blue. Dip to black, then a fast montage of the physical card tray, then a dissolve back | `Outputs`, `Inputs`, `9 Tokens`, token words, `blue` |
| 3:10–4:10 | Build X, then multiply by W_Q and W_K. | Heatmap matrix X with a `d=768` bracket; rounded boxes W_Q, W_K; Q and K heatmaps grow out to the right; the camera pans as the chain extends | `X`, `9×768`, `W_Q 768×64`, `QUERIES Q = XW_Q 9×64`, `KEYS K = XW_K` |
| 4:10–4:55 | Queries search for keys: "a token like flag could query for words that modify its meaning". | Speech bubbles on rows; all rows except *flag* and *American* dim; the two rows are pulled out; dot product | `"Do any tokens modify my meaning?"`, `"I'm a modifier!"`, `= 524.2` |
| 4:55–6:15 | QKᵀ → mask → softmax → values → weighted sum. | Diagram grows left to right; small rounded op boxes; final dashed box around the whole head | `Kᵀ`, `QKᵀ`, `Mask & Softmax`, `ATTENTION PATTERN 9×9`, `VALUES V = XW_V`, `ATTENTION HEAD OUT O = AV`, `ATTENTION HEAD` |
| 6:15–6:55 | Multiple heads, then stack outputs × W_O. | (3D) head stack fans out, then collapses to a stacked vector × W_O | `Stacked Attention Head Outputs`, `Output Weight Matrix`, `Layer Out` |
| 6:55–7:40 | Cost scales as tokens²; 100k tokens ≈ the first Harry Potter book. | 9×9 pattern with a yellow curved arrow; overhead: hands cut a Harry Potter page into word strips laid along the table edge; huge pattern overlay | `9² entries` |
| 7:40–9:40 | KV caching: on a new token only the bottom row is new, so keys and values are cached. | Paper tokens + "model" card; Manim chain re-run with a 10th row "blue"; magenta outlines on reused rows, cyan on new ones; the camera pushes in to each stage | `10×768`, `STORE IN MEMORY` (magenta), legend `KV Cache` / `New Computations` |
| 9:40–10:05 | Compute goes from quadratic to linear. | Line chart on black: quadratic curve, then a yellow linear one | `ATTENTION BLOCK COMPUTE SCALING`, `Compute`, `Input Tokens`, `No caching`, `with KV Caching` |
| 10:05–10:45 | Cost: 2·n·d_h·n_h·l numbers → ~4 MB/token → 400 GB at 100k tokens. | 3D slab stack with braces, then an equation with leader-line callouts to each variable; final value boxed | `NUMBER OF ENTRIES IN CACHE = 2·n·d_h·n_h·l`, `Input tokens`, `Dimension of key and value matrices`, `Number of attention heads per layer`, `Number of layers`, `CACHE SIZE = … ≈ 4 MB/token`, `400 GB` (boxed), `*2 Bytes/number (fp16)` |
| 10:45–12:20 | Personal tinkering with the inference code, then the KiwiCo read with his kids. | Welch at his monitors; kitchen footage; product grid; logo lower third | `kiwico.com/welchlabs`, code |
| 12:20–13:35 | "Now back to DeepSeek…" MQA shares one K/V (performance hit); GQA uses groups of 8. | (3D) tilted head stacks with white routing lines; a comparison table builds row by row on the right | `MULTI-QUERY ATTENTION (MQA)`, `GROUPED-QUERY ATTENTION (GQA)`, table headers `ATTENTION MECHANISM / KV CACHE ENTRIES PER TOKEN / KV CACHE SIZE PER TOKEN* / PERFORMANCE`, `8x Reduction`, footnotes |
| 13:35–15:35 | MLA: compress into a shared latent and project back up per head; the W_UK and W_UV weights can be absorbed. | 2D diagram rebuilt with `W_DKV`, `L_KV`; yellow arrows point at each new piece; magenta outline boxes; absorbed `W_Q W_UKᵀ` | `MULTI-HEAD LATENT ATTENTION (MLA)`, `KEYS & VALUE LATENTS L_KV = XW_DKV`, `Shared across all heads & cached`, `QUERIES PROJECTED TO LATENT SPACE` |
| 15:35–16:20 | Cache no longer depends on head count; 576 per token → 70 KB, a 57× reduction. | (3D) MLA stack; table gains a cyan MLA row; yellow arrow | `Multi-Head Latent Attention (MLA)` (cyan), `70 KB`, `Higher`, `57x Reduction` |
| 16:20–17:10 | "DeepSeek appears to have just made it work significantly better… it will be fascinating to see…" | Clean MLA 2D poster frame; talking head; papers on the desk; R1 paper picked up | title only |
| 17:10–18:09 | Patreon thanks; poster pitch ("the matrix images… are actually from the real DeepSeek model"); store. | Black thanks card; hands hold the printed poster | `Special Thanks to Patreon Supporters:`, names |

Shape: **about 1 min of hook, then about 9 min building one diagram, a mid-roll, 4 min of three variants of the same diagram, a 1-min payoff table and the outro.** The diagram built from 3:10 to 6:15 is reused, re-lit and extended until the end.

### F. Can humans make AI any better? [Bitter Lesson] (2026-01-31, 23:39)

| Time | Said | Shown | On-screen text |
|---|---|---|---|
| 0:00–0:28 | 1971 ARPA goal: 1,000 words at 90 %; five years later CMU's Harpy does 1,011 words at 95 %. | Hand slides a printed ARPA spec sheet onto drafting-grid paper held by brass weights. Push-in; a second column appears beside each spec with arrows | typewriter text: `SPEECH UNDERSTANDING SYSTEM PERFORMANCE GOALS`, `1000 word vocabulary`, `THE HARPY SPEECH RECOGNITION SYSTEM`, `1011 word vocabulary`, `95% accuracy` |
| 0:28–0:50 | Harpy's core was "an enormous knowledge graph" of 14,000+ phone nodes. | (3D) flight over a Manim graph of thousands of cream tiles | node labels |
| 0:50–2:05 | The path for "tell me about China"; the waveform is cut into blocks, each matched to a phone; beam search. | 2D phone graph (rounded tiles, typewriter labels); the path lights cyan, then magenta step by step; cyan waveform above; small spectrum curve inside each tile | `start`, `end`, phone codes (`T`, `EL`, `AH`…) |
| 2:05–3:45 | How the graph was built by hand: grammar → word graph → pronunciation graphs → juncture rules. | Back on paper: a hand lays word cards and arrows; phone cards; red-ink edits drawn by hand (Y glide, dropped T); green box overlay on the "TELL" sub-graph | `TELL`, `ME`, `ABOUT`, `CHINA`…, `"TELL"` (green) |
| 3:45–4:30 | Replaced by hidden Markov models whose probabilities are learned from data, and the field moved over. | Printed HMM lattice poster; IBM paper excerpt | `HIDDEN MARKOV MODEL` (red serif) |
| 4:30–5:35 | Sutton's 2019 essay: "general methods that leverage computation are ultimately the most effective". GPT-2 lands weeks later. | Essay printout on the desk, key sentence highlighted yellow; GPT-2 paper; Llama network animation | the essay text with highlight |
| 5:35–6:15 | "But then in 2025, something really surprising happened. Richard Sutton went on a podcast." | Talking head | none |
| 6:15–8:25 | Sutton argues LLMs are *not* bitter-lesson-pilled. | Podcast clip in an inset frame on black | `"Richard Sutton – Father of RL thinks LLMs are a dead end" · Dwarkesh Podcast · Sep 26, 2025` |
| 8:25–9:15 | "This is such a remarkable moment… So, is Sutton right?" Ends on the essay's closing lines. | Talking head; quick callbacks to the Harpy poster and Llama net; essay excerpt with highlight | highlighted sentences |
| 9:15–10:05 | Supervised next-token training "relies too much on human knowledge". | A hand cuts the first line of Harry Potter into word slips; paper tokens → LLM card → "number" | `Mr and Mrs Dursley of` → `number` |
| 10:05–11:45 | Sutton = father of RL; AlphaGo. Sponsor: Tufa Labs. | `REINFORCEMENT LEARNING` card, AlphaGo badge, physical Go set; talking head; papers; GPU rack photos | sponsor text |
| 11:45–13:15 | Policy network = state → action, trained on human games, which is "strikingly similar to LLM training"; Elo 1517. | Board → cyan CNN planes → move heatmap; parallel LLM row below (12:20); Elo bar chart | `AlphaGo`, `STATE`, `ACTION` (yellow caps), `SUPERVISED POLICY NETWORK (CNN)`, `POLICY`, `LARGE LANGUAGE MODEL` (written on letter by letter at 12:20) |
| 13:15–14:25 | Self-play: the winner's moves become positive examples. | Two policy nets V1/V2 around a board; moves tinted green/red; green `WINNER` badge | `POLICY GRADIENT METHOD`, `REINFORCE, Williams 1992` |
| 14:25–16:40 | Value functions, "arguably the most important thing… learned about reinforcement learning", then MCTS. | Sutton & Barto book on the desk with an italic pull quote; value net → `P(win)`; search tree | `P(win)`, `Quality of board position`, `VALUE NETWORK`, `BEST MOVES`, `HIGHEST PROBABILITY OF WINNING`, `MONTE CARLO TREE SEARCH (MCTS)` |
| 16:40–17:50 | AlphaGo Zero, no human games; "playing against an alien". | Nature paper printout; (3D) grid of game boards; Sutton clip again | paper title |
| 17:50–18:40 | RLHF vs RLVR. | Split screen with a vertical divider; colour-coded keywords | `REINFORCEMENT LEARNING FROM HUMAN FEEDBACK (RLHF)`, `…WITH VERIFIABLE REWARDS (RLVR)`, `Supervised pretraining on human text`, `Reinforcement learning to match human preferences`, `on correct answers` |
| 18:40–20:00 | Silver & Sutton, "Era of Experience": an LLM trained on old human knowledge would reason in old paradigms. | Paper on the desk; gag cards: ChatGPT as of 3000 BCE / 1000 CE / 1700 CE / 1970 CE answering "Why is metal shiny?" | `Animal spirits inside the metal`, `God made it that way`… (period fonts) |
| 20:00–21:05 | Four open questions, then "My take…": "I'm more skeptical…", "it will be fascinating to see what happens next." | Callbacks: Harpy poster, 3D graph, RLHF/RLVR split; talking head | none |
| 21:05–23:39 | Book pitch: each chapter maps to a video; exercises; code. | Book on the desk, page spreads, chapter listing | `CHAPTER LISTING` + chapter titles (= video titles) |

Shape: **a 5.5-minute historical prologue that *is* the argument**, a pivot to the present through one dramatic clip, then a mechanism section (AlphaGo) chosen to answer the prologue, an essay-style ending with questions, and a long promo.

## 6. Visual system

### Backgrounds

Share of 5-second frames by background class [measured, whole-frame pixel classifier; see §10 for caveats]:

| Video | Black (Manim, incl. graphics over darkened desk) | Desk (wood) | Slate grey boards | Light / paper | Other (footage, talking head, screen capture, full-bleed images) |
|---|---|---|---|---|---|
| A AlexNet 2024 | 12.7 | 22.6 | 15.6 | 13.7 | 35.4 |
| B Dark matter 2024 | 65.5 | 5.2 | 0.0 | 16.9 | 12.4 |
| C DeepSeek 2025 | 68.8 | 2.8 | 1.4 | 1.8 | 25.2 |
| D Backprop 2 2025 | 67.2 | 15.0 | 0.0 | 3.3 | 14.5 |
| E Grokking 2025 | 65.0 | 13.6 | 0.0 | 6.6 | 14.8 |
| F Bitter lesson 2026 | 49.6 | 5.6 | 0.0 | 18.0 | 26.8 |
| G JEPA pt1 2026 | 53.5 | 12.5 | 15.1 | 2.9 | 16.0 |
| H 2015 | 0.0 | 1.4 | 0.0 | 98.6 | 0.0 |

The figures cover the whole runtime, sponsor and outro included.
- In C, the sponsor and talking head make up most of "other".
- In F, "light" is mostly cream drafting paper and printed documents.
- In G, inset interview clips on black can count as "black".

A (2024) is the outlier: it leans on desk practicals and slate infographics. From late 2024 on, **about two thirds of runtime is Manim on black**.

- **Black #000000** for nearly all Manim work 2024–25 [verified: `custom_gx/welch_style.py` BACKGROUND, frames].
  - There is no gradient or texture behind diagrams.
  - Graphics are sometimes composited over a darkened, vignetted walnut desk (C 1:40 attention grid).
  - Late 2026 config and storyboards use **dark teal #031e1e** [verified: `custom_config.yml`, `world_models` storyboards; not in sample videos].
- **Dark walnut desk, shot from overhead, with a warm vignette.** This is the stage for paper cutouts, printouts, props and hands. Earlier work used light plywood or a white light box (H).
- **Slate grey (~#2b2b2b) "infographic" boards** for timelines and family trees (A 14:00–16:00, G 1:45–4:00, G 24:45).
- **Cream drafting-grid paper** for historical artifacts (F).
- **Talking head** in his book-lined office with a practical lamp, usually at pivots, the personal take and sponsor reads. It is a small share of runtime: my estimate from the contact sheets is about 5–10 % [inferred].

### Palette

[verified: `custom_gx/welch_style.py`, `custom/welch_axes.py`, scene constants]

| Token | Hex | Role observed in frames |
|---|---|---|
| CHILL_BROWN | #948979 | axes, ticks, tick labels, arrows, connectors, captions and dims, de-emphasised text, the custom arrow tip |
| FRESH_TAN | #dfd0b9 | primary line art (network nodes, boxes), body labels |
| YELLOW | #ffd35a | the *one* thing to look at: pointer arrows, boxed results, "Paris", the loss, key curve labels |
| BLUE | #65c8d0 | second series, "new computations", cyan-ish highlights |
| CYAN / MAGENTA | #00ffff / #ff00ff | signed or paired quantities (cos/sin, +/− updates), outline highlights, "store in memory" |
| CHILL_GREEN / GREEN | #6c946f / #00a14b | third series (Berlin), WINNER |
| CHILL_BLUE, YELLOW_FADE | #3d5c6f / #7f6a2d | shaded group panels behind parts of a network (D 12:40) |

- **Data colour maps** [verified frames + filenames]:
  - viridis-like for weight and activation heatmaps;
  - purple→yellow for attention patterns;
  - `magma_linear` for depth maps (world_models);
  - magenta single-hue for correlation matrices (G 23:45).
- **One colour per entity, held across every representation.** In D, Madrid = cyan, Paris = yellow and Berlin = green. That mapping holds for the neurons, the equations h₁/h₂/h₃, the map regions and the UMAP points. In E, cos is yellow and sin is magenta.
- **2026 world-models storyboard variant** [verified `p63_64.py`]: FRESH_TAN #f4ebd9, CHILL_BROWN #948678 for titles and dividers, YELLOW_HL #fcc947.

### Typography

[verified: code + frames]

| Use | Face | Style |
|---|---|---|
| Section titles | Myriad Pro (2026 storyboards: Open Sans) | **UPPERCASE, bold, wide letter-spacing**, top centre, often with the acronym in parentheses: `MULTI-HEAD LATENT ATTENTION (MLA)`, `JOINT EMBEDDING PREDICTIVE ARCHITECTURE (JEPA)` with the acronym in yellow |
| Component labels | Myriad Pro | UPPERCASE, semibold, small, tan or brown: `QUERIES`, `ENCODER`, `POLICY NETWORK`, `STATE`/`ACTION` (yellow for the two key terms) |
| Explanatory phrases | Myriad Pro | Sentence case, small, 1–3 lines: `Minimize Prediction Error`, `Shared across all heads & cached`, curve-end labels such as `with KV Caching` |
| Math, numbers, dims | LaTeX Computer Modern via `Tex` | Colour-coded by entity; dims tiny and brown (`9×64`, `768×64`) |
| Example sentences, tokens, quotes | Italic serif (storyboards: STIX Two Text italic; video: LaTeX/serif italic) | `The capital of France is` → `Paris`; pull quotes in italic serif with an em-dash attribution and keywords tinted yellow (D 0:10) |
| Period documents | American Typewriter / typewriter | Harpy-era graphs and labels (F) |
| Hand lettering | marker on paper | cards and annotations (D, E, G, 2015) |

- [inferred, from Illustrator-exported `Layer_1-2` SVGs and job posts] Labels in SVG overlays are typeset in Illustrator, not in Manim.
- Myriad Pro is an Adobe commercial font. The repo's `font_installed` check warns and falls back when it is missing [verified: `welch_style.py`].

### On-screen text: how much, where, and what kind

OCR of graphic (black-class) frames [measured: RapidOCR on 640×360 frames; about 40 frames per video, one per ~15 s of graphics].

| Video | Frames with no legible text | Text items / frame (median, p90) | Text tokens / frame (median, p90) | Longest text item in frame, chars (median) | Item height, % of frame height (median) | Items in top 15 % band | Items in bottom 15 % band | UPPERCASE share of letters |
|---|---|---|---|---|---|---|---|---|
| C DeepSeek | 8 % | 13, 26 | 14, 34 | 9 | 3.6 | 4 % | 6 % | 44 % |
| D Backprop 2 | 5 % | 22, 38 | 28, 39 | 15 | 4.2 | 4 % | 5 % | 15 % |
| F Bitter lesson | 2 % | 5, 16 | 8, 22 | 22 | 3.6 | 4 % | 19 % | 28 % |
| G JEPA pt1 | 38 % | 1, 10 | 2, 30 | 14 | 3.9 | 6 % | 6 % | 40 % |

What the numbers mean:
- The items are mostly **single labels, numbers and math fragments**: `QUERIES`, `9×64`, `0.905`, `h2=m2x+b2`. A frame can hold 10–40 of them, but **the longest item in a frame is typically 9–22 characters**: a short label or one equation, not a sentence.
- D's high counts come from the live numbers on its network diagram.
- F's bottom-band share comes from clip source lines and footnotes.
- G's empty frames are pure-image beats (photos, interview insets, the cake).
- **Text size is uniform.** The median OCR box height is 3.6–4.2 % of frame height, roughly 40–45 px of box at 1080p including ascender/descender padding. Titles are only slightly larger, and set apart by caps and tracking. 360p misses the tiniest dims and footnotes, so true counts are slightly higher.
- **The top band is reserved.** Only 4–6 % of items sit in the top 15 % of the frame, and that is where section titles live.

- **No narration captions and no sentence subtitles** [verified: all sampled frames]. The text on screen is:
  1. **section titles** (top centre, persist through a section);
  2. **object labels** (caps, under or left of the object);
  3. **math**;
  4. **source text that is itself a visual**: papers, book pages, essay excerpts with a yellow or orange highlighter on the key sentence (F 5:00, B 15:00);
  5. **footnotes**: tiny brown text at the bottom right, marked with asterisks (`*DeepSeek R1/V3 Architecture – 61 layers, 128 heads…`, `**Grouping factor of 8`, `*2 Bytes/number (fp16)`), plus academic citations bottom right (D 11:20, B 1:00).
- **Occasional explanatory paragraph** (2–3 lines, small, centred or left-aligned, brown/tan) next to a derivation. Example (D 14:20): "Since our Cross-Entropy loss depends on the correct output/label, we get different derivatives…". It sits in its own zone, never across the diagram.
- **Callouts with leader lines** for points in a scatter: rounded boxes holding a short excerpt with the keyword in yellow (D 27:20 UMAP).
- **Tables** are typeset like print:
  - caps headers in small bold brown;
  - row labels on two lines;
  - math cells in CM;
  - the winning row coloured;
  - a curved yellow arrow carrying the delta label ("57x Reduction").
- **Lower-third sponsor bars** with the URL and a left arrow pointing at the offer (C 12:05, D 3:30).

### Equations

- Each equation sits under or next to the object it computes, in a three-slot caption row: **CAPS name left, equation centre, dims right**, e.g. `QUERIES   Q = XW_Q   9×64` [verified C frames].
- Derivations stack vertically and dim as they get old; the result is boxed in a **yellow rounded rectangle** (D 14:30 `∂L/∂h = ŷ − y`).
- Cancelled terms are struck through (D 16:40).
- Numbers are substituted live into the same layout (D 17:30: `∂L/∂m₂ = x(ŷ₂ − y₂) = 2.3514°(0.09 − 1) = −2.140`).

### Characters

- **None.** No mascot and no pi-creature. In 2015 there were hand-drawn stick figures with speech bubbles (H).
- Anthropomorphism is limited to speech bubbles on data (C 4:25 "Do any tokens modify my meaning?").
- Welch appears himself as a talking head, and his hands appear in the overhead shots.

### Imagery

[verified frames]

- **Real model data rendered as images:**
  - weight and activation heatmaps (C, B);
  - attention patterns (C);
  - Llama 3.2 connection flows with the strongest edges only (D);
  - UMAP scatters (D);
  - loss landscapes (D);
  - activation atlases (A).
- **Physical props on the desk:**
  - paper cutout tokens and cards with drawn arrows;
  - printed attention-pattern tiles in a wooden tray;
  - a Harry Potter book cut up with scissors;
  - a wall clock with a digital overlay (E 17:00);
  - a Go set; a cake (G 4:15);
  - a tennis or ball-bounce scene shot live (G 2:00).
- **Documents:** arXiv papers (binder-clipped), book pages, Nature articles, essays.
- **Footage:** podcast and interview clips with a source line, archival video (Navlab), screen recordings (ChatGPT, DeepSeek chat, Neuronpedia), a live webcam fed into AlexNet (A 5:10).
- **Infographic boards:** a timeline with icons (A); an "AI family tree" of model icons with year labels (G); bar charts with caps titles and a subtitle in parentheses ("(ILSVRC, lower is better)", A 13:20).

### Composition and density

[inferred from frames]

- **One diagram per frame, with lots of black.** Pipelines read left → right; when a pipeline outgrows the frame the camera pans or pulls back rather than shrinking the type.
- **A recurring "anchor" diagram.** C's attention head, D's 3-neuron city model and E's embed → probe → attention → MLP → unembed strip each return 5–10 times and get lit, extended or annotated. Plots attach *to* the anchor: E puts sine waves above and below the probe with dotted leader arrows.
- **Comparisons as left/right splits with a thin vertical divider** (F RLHF | RLVR; world-models storyboards).
- **Dense frames are allowed only as texture.** Examples are the 144-pattern grid, the 14,000-node graph and the full Llama network. A short caps title and two bracket labels make them readable, and the camera then pushes into one cell.
- Margins are generous. Labels sit 0.05–0.15 units from their object (code `buff=0.1` 193×, `0.05` 101×, `0.15` 67×) [verified counts].

## 7. Motion & sync grammar

### Measured pacing

| Video | Hard cuts /min | Median gap between hard cuts (s) | p25–p75 (s) | % runtime in takes > 30 s | Longest takes (s @ start) | Backdrop switches /min | % of hard cuts inside a speech pause | Chance (% of time in pauses) |
|---|---|---|---|---|---|---|---|---|
| A AlexNet | 5.5 | 6.8 | 3.9–11.4 | 25 | 180 @ 4:51; 51 @ 15:20; 32 @ 11:38 | 3.5 | 44 | 11 |
| B Dark matter | 2.8 | 10.1 | 6.2–20.9 | 53 | 220 @ 2:13; 171 @ 16:21; 138 @ 9:28 | 2.0 | 60 | 13 |
| C DeepSeek | 2.6 | 7.5 | 3.8–15.4 | 69 | 282 @ 2:08; 183 @ 13:36; 118 @ 7:49 | 1.7 | 62 | 14 |
| D Backprop 2 | 2.4 | 9.3 | 4.6–17.0 | 69 | 348 @ 13:46; 198 @ 20:35; 141 @ 11:25 | 1.4 | 48 | 16 |
| E Grokking | 2.4 | 9.2 | 5.5–18.2 | 70 | 322 @ 19:17; 251 @ 9:06; 182 @ 13:57 | 1.5 | 57 | 20 |
| F Bitter lesson | 3.1 | 10.7 | 6.6–19.8 | 51 | 130 @ 13:05; 99 @ 0:27; 96 @ 6:46 | 2.4 | 60 | 20 |
| G JEPA pt1 | 2.7 | 11.5 | 5.2–20.8 | 60 | 223 @ 20:55; 124 @ 11:16; 119 @ 5:15 | 2.0 | 64 | 24 |
| H 2015 | 7.1 | 4.3 | 2.4–11.3 | 20 | 70 @ 1:01; 21 @ 2:11; 20 @ 0:27 | 0.4 | 9 | 14 |

[measured]
- **Backdrop switches** are changes of background class between consecutive 5-second frames; they catch the dissolves the cut detector misses.
- **"% of hard cuts inside a speech pause"** is the share of hard cuts (outside sponsor/promo) that fall in a gap of ≥ 0.6 s of silence between narration words. The "chance" column is the share of narration time occupied by such gaps.

**Read the cut-placement result this way.** In 2024–26 videos, **44–64 % of hard cuts land in a pause, about 3–5× chance.** Cuts are placed at clause and sentence boundaries in the edit. The 2015 video sits below chance (9 %): it is cut to a music bed, mid-sentence.

- Hard-cut detection (ffmpeg scene score > 0.25, detections within 1 s merged) undercounts dark-to-dark changes. Welch's frequent **dip-to-black** and **cross-dissolve** between Manim and desk footage fall below the threshold; one example is C 2:50–2:56: fade to black, a montage of several 0.5–1 s shots of the card tray, then a dissolve back [verified: 2 fps frame strip].
- Read the cut counts as lower bounds. The longest stretches without a hard cut are mostly unbroken Manim, checked in the contact sheets:
  - D 13:46–19:34 (the backprop derivation on the persistent network);
  - E 19:17–24:38 (the anchor pipeline on the left for 5 minutes while plots evolve on the right).
  - C 2:08–6:50 contains the one dip-to-black montage.

  **Long continuous camera-driven Manim takes of 3–6 minutes are the norm** in 2025–26.

### How visuals track words

[inferred from transcripts vs frames, plus code facts in §2]

- **Beat-level sync, not word-level.** Each spoken clause gets one visual change: a label writes on, a matrix fades in, the camera moves to the next stage. The change lands near the noun that names it ("we multiply our input matrix X by two separate sets of learned weights, W_Q and W_K" → boxes appear, C 3:45).
- Because renders are long takes with 1-second waits between animations and 20-second tails, the editor can slip whole animations against the VO in Premiere. That makes the clause-level alignment *possible*; exact syllable hits are neither attempted nor visible.
- **The camera is the main motion.** Most transitions inside a section are `frame.animate.reorient(...)` pans and push-ins over one big canvas: 2,668 `reorient` calls in the repo [verified count]. New content appears off-centre where the camera is about to go.
- **Morph and extend, rarely replace.** A new token row is appended to existing matrices; the 2D head becomes a 3D stack and back. `ReplacementTransform` appears 1,282 times against `FadeIn` 1,551 and `FadeOut` 1,245 [verified counts].
- **Lists and rows reveal with lags** (`LaggedStart` 254, `lag_ratio` 538). Labels **write on letter by letter** (F 12:20, "LARGE LANGUAGE MO…").
- **Numbers update in place** inside fixed-width slots (`format_number(..., total_chars=6).rjust`), with a `Step=042` counter in the corner during training loops (D 21:00–23:20) [verified code + frames].

### Emphasis vocabulary

In rough order of frequency [inferred from frames; counts verified in code]:

1. **Dim everything else** to about 0.2–0.5 opacity. The focus stays at 1.0 and positions do not change (C 4:40, C 8:20–8:45, D 11:50–12:30).
2. **Small yellow arrow** that appears, points for one clause, and goes (C 10:15, D 14:30, F 12:40). Its tip is notched like the axis tip.
3. **Outline rectangle** in magenta, cyan or yellow around an existing object (C 8:20 magenta = cached, cyan = new; D 9:40 yellow box on m₂).
4. **Colour change** to the entity colour (gray dots → yellow "cat" dots, `sora/p78_85.py`).
5. **Yellow boxed result**, used once per derivation.
6. **Curved yellow arrow with a delta label** in tables.

No shakes, no `Indicate` pulses, no zoom-bounce.

### Transitions

[verified frames]

- Inside Manim: camera moves and fades.
- Manim ↔ desk footage: cross-dissolve, or dip-to-black.
- To and from the talking head: hard cut.
- Section change: the title card swaps at top centre while the diagram persists or re-lights.
- Sponsor: hard cut in; "Now back to…" over a re-entry to the anchor diagram.

### Pauses

- **Frequency** [measured, §4]: about 10 pauses per narration minute (gap ≥ ~0.6 s), totalling 8–23 % of narration time. Pauses over ~1.1 s are rare: 0.1–4.8 per minute, longest 2–6 s.
  - There is no long "let it sink in" silence. The VO keeps moving, and **the visual keeps moving with it**: a camera drift, a lagged reveal finishing, numbers ticking.
- **What fills a pause** [inferred from frames + cut placement]:
  1. **a cut** (most hard cuts land in pauses);
  2. **an animation completing**, such as a matrix sliding into place or a row lighting up;
  3. **a held frame** right after a key result (the boxed equation, a table's final row) before the next sentence starts.
- **Music** is a sparse bed under some sections [verified: `[music]` markers in E–G's captions]. The markers fall at:
  - E: 0:18–0:23 and 33:43–34:25 (opening and close);
  - F: 5:24 (the GPT-2 turn) and 20:47–22:53 (take + promo);
  - G: 0:49, 10:16–10:37 (sponsor), 28:24 and 29:14.

  I did not analyse the music further.

## 8. Polish

What keeps Welch's frames clean. Each item says what he does and how, and is concrete enough to turn into a rule or a check.

1. **Layout is designed at final size before animation** [verified]. Storyboards are 1920×1080 Illustrator artboards. In the 2026 world-models scene the code **redraws each storyboard from its pixel coordinates**:
   - `PX = FRAME_HEIGHT/1080`;
   - `P(x, y)` maps storyboard pixels (y down) to Manim points;
   - stroke widths are calibrated (`STROKE_PER_PX = 1/2.03`);
   - text is placed by *left edge and baseline*.

   `px_text` sets a throwaway "H" in front of each string so that the cap height fixes the scale and the H's bottom fixes the baseline, so "strings with descenders sit correctly without per-string fudge factors". `CAP = {"Open Sans": 0.714, "STIX Two Text": 0.656}` matches Illustrator point sizes (`_2026/world_models/p63_64.py`).

   *Text never collides because its box was decided by a designer, not computed on the fly.*
2. **Labels that are hard to typeset in Manim are imported as SVG** [verified]. Examples: the DeepSeek head (`mha_2d_segments-*.svg`) and the backprop network background (`p44_background_1.svg`). Manim adds only the data images and live numbers, at hand-tuned absolute coordinates (`move_to([-0.2,0.38,0])`).
3. **No labels in 3D** [verified]. "ok i was thinking do labels in manim, but I think Illustrator is the way to go! 3d sucks for this!" and "Drop labels & legend, for illustrator overlay" (`backprop_2/book_animation_6.py`). Labels are composited flat over 3D renders in post, or added only once the camera has settled.
4. **Fixed slots for every kind of text** [inferred from frames]:
   - titles at top centre;
   - object captions under or left of the object;
   - dims small at the lower right of the object;
   - equations centred under the object;
   - footnotes bottom right;
   - legend bottom left;
   - sponsor lower third.

   A slot is never shared, so overlaps don't happen by construction.
5. **Labels are short** [measured in the OCR table above]. Caps nouns of 1–4 words. Anything longer becomes a footnote, a side note in its own column, or a document on the desk.
6. **Dim, don't delete, and don't move.** Context drops to low opacity in place, which preserves spatial memory and removes visual competition without re-layout (`set_opacity`: 3,584 calls) [verified].
7. **The camera frames; text is never rescaled to fit** [inferred from frames + code]. Zooming the frame scales text and diagram together, so relative sizes stay consistent. At high zoom, peripheral labels *are* allowed to slide out of frame. At C 8:05 the `VALUES` caption is cut by the bottom edge and the `9×64` dims by the right edge, while the focus (X with its new 10th row "blue", `10×768`) is fully inside, with margin. The focus element's labels are always fully inside.
8. **Fixed-width numerals** [verified `backprop_2/p22_24.py`]. `format_number` picks precision by magnitude and right-justifies to six characters, so updating values don't jitter or collide with neighbours.
9. **Leader lines and brackets instead of crowding** [verified frames]. Variables in a long equation are annotated through angled leader lines to labels placed above or below (C 10:25). Groups get braces with a centred label (`CONTEXT`, `REAL VIDEO`, `12 Layers`). Callouts sit outside the scatter, connected by thin lines (D 27:20).
10. **A strict colour budget per frame** [inferred]. Base tan/brown plus at most two accents, and the accents mean something (entity, or "look here").
11. **Contrast hierarchy through colour, not size** [inferred]. Primary labels are FRESH_TAN or white, secondary text CHILL_BROWN, the focus yellow. Text sizes stay within a narrow band (code `font_size` mostly 20–32).
12. **Glitches are fixed in the edit** [verified]: "there is a little jump here -> I'm going to try to fix/hide it in premiere". Imperfect renders are fine as long as the cut hides them. *This is not available to a fully automated pipeline*, so automated checks must do the job the editor does here.

What I did **not** see in any sampled frame: overlapping text, text over a busy part of a heatmap, labels crossing connector lines, or mixed sizes for sibling labels.

## 9. Reproducing it with a code-driven pipeline

### What code can reproduce well (Manim CE)

- **Black-background diagram language.**
  - Caps labels, CM math, tan line art, notched brown arrows.
  - Rounded op boxes (`RoundedRectangle`, about 0.1 corner radius), dashed group boxes, braces with labels.
- **Real-data visuals.**
  - Heatmaps from tensors: PNG via matplotlib/numpy into `ImageMobject`, or a `VGroup` of squares for small ones.
  - Attention patterns, UMAP scatters, loss curves, training counters, bar charts, comparison tables.
- **Persistent anchor diagram.**
  - Focus by opacity; outline highlights; yellow pointer arrows.
  - Live number updates in fixed-width slots.
- **Camera grammar.** `MovingCameraScene` push-ins and pans over a large canvas (3D flights aside).
- **Section title cards, split screens with a divider, legends, footnotes, citation lines.**
- **Quote cards.** Italic serif, attribution, one keyword in yellow.
- **Infographic boards.** Timelines and family trees on slate grey with icons and year labels.

### What needs illustration, compositing or footage

- **Overhead desk practicals** (paper cutouts, hands, scissors, props).
  - *Approximation*: render "paper card" mobjects (cream fill, slight rounded corners, soft drop shadow) over a photographed walnut texture with a vignette.
  - The cards can carry hand-drawn-style text (a marker font) and slide in on eased paths.
  - Hands and real props need footage or stock, so treat them as optional B-roll.
- **Printed papers and book pages.** Render the PDF page (pdf2image) and composite it on the desk texture with a shadow and a binder-clip PNG. A highlighter is a semi-transparent yellow rectangle behind a line. This is feasible in code.
- **Talking head, interview and podcast clips, screen recordings.** Footage only. A code pipeline should replace them with a narration-only beat over an anchor diagram, or with a quote card.
- **Illustrator-grade typesetting.** Achievable in code *if* layout is solved before animation (see below). A commercial font needs a license: Myriad Pro is Adobe's.
  - [inferred] Source Sans 3 (Adobe, OFL) is the closest freely licensable humanist sans. That is a judgement of similarity, not a Welch choice.

### Building blocks we would need

1. **`welch_style` tokens for Manim CE.** The palette from §6, plus the font roles (the tracking values are eyeballed from frames [inferred]):
   - `LABEL` caps Myriad/Source Sans semibold, tracking about +80;
   - `TITLE` caps bold, tracking about +150;
   - `MATH` CM;
   - `EXAMPLE` italic serif;
   - `PERIOD` typewriter.

   Plus `BACKGROUND` (#000), and stroke 3 / thin 2.
2. **Slot-based label layout per object.** `caption(obj, name, eq=None, dims=None)` produces the CAPS-left / eq-centre / dims-right row under the object; `title_card(text, acronym=None)`; `footnote(text, n_stars)` at bottom right; `legend(items)` at bottom left. The point is that collisions are prevented *by construction*, which fits the existing `LayoutBoard` / reserved-bands idea in `references/layout-craft.md`.
3. **A storyboard-pixel layer (port of `p63_64.py` `P`/`V`/`px_text`/`arrow`).** It lets the planner write layouts in 1920×1080 pixel space with baseline-anchored text, which is easy for an LLM and checkable, then map them to Manim. This is the most transferable idea in the repo.
4. **`MatrixHeatmap(tensor, cmap, row_labels, col_labels, dims)`.** Image-backed, with row-band highlight, row extraction and append-row animations.
5. **`AnchorDiagram`** with `focus(*parts)` (dim the rest), `outline(part, color)`, `point(part)` (yellow notched arrow in and out), `update_value(slot, x)`.
6. **`CameraTour`.** Named camera stops over one canvas (`frame.animate.move_to(...).set(height=...)`), the CE equivalent of Welch's `reorient` pasting.
7. **`CompareTable`.** Rows add one at a time, winning row coloured, curved delta arrow.
8. **`DeskCard` / `DeskDocument`.** Paper-on-wood compositing primitives for the practical look.
9. **Transitions.** Dip-to-black and cross-dissolve between "desk" and "black" beats, done at mux time with ffmpeg `xfade`, not in Manim.
10. **Text-collision QA.** Welch relies on a human editor; we can't. The existing `layout_check.py` / `check_layout.py` should treat the slot taxonomy as ground truth. Each text mobject is tagged with its slot; overlaps between slots fail, and so does any focus-label clipping at frame edges. Peripheral clipping during camera moves is allowed, as Welch does.

### Repo helpers worth porting (MIT)

| Helper | Why | Notes |
|---|---|---|
| `custom/welch_axes.py`: `generate_nice_ticks`, `WelchXAxis`/`WelchYAxis` | 1-2-5 tick picking with one tick of headroom each side, ignoring 0; brown axes, 3 px stroke, ticks outward (down/left), labels `buff=0.1`, notched SVG tip | manimgl → CE: replace `Tex` scale-by-`font_size/48` with `MathTex(font_size=…)` |
| `custom/welch_tip_manimce.py` (`WelchTip`) and `welch_arrow_tip_1.svg` | The notched arrowhead: tip (32.33, 13.21), back corners (0, 0)/(0, 26.42), notch at 7.67, about a 0.24 notch-to-length ratio | Already Manim CE |
| `custom/welch_numberline_manimce.py` | CE number line with Welch tips | Bug: pops `include_tip` and then reads it, so tips are always on. Fix when porting |
| `custom_gx/welch_style.py` | Canonical palette + font-presence check | Targets `manimgx`; copy the constants |
| `_2026/world_models/p63_64.py` `P`, `V`, `px_line`, `arrow`, `px_text`, `CAP` | Storyboard-pixel → scene mapping with baseline-true text | The core of building block 3 |
| `_2025/backprop_2/p22_24.py` `format_number` | Fixed-width numeral formatting | Trivial, high value |

### Where the Welch style diverges from the current `manim-explain` rules

These are for Ben to decide in phase 2; nothing has been changed.

- **Exact numbers and tables are central to Welch** (57×, 4 MB → 70 KB, Elo 1517, 61 layers). The current hard rule 10 says ordinary explainers avoid narrating exact scores and tables. A Welch style would need that rule relaxed: real numbers serve the story there.
- **Small explanatory prose on graphic frames** (side notes, footnotes) is a Welch device. Hard rule 9 says "Never put prose on a live graph". Welch keeps the prose *off the plot area*, in its own slot, so the two can coexist with a slot rule.
- **Word-level sync** is stricter than what Welch does (beat-level, edited). Audio-first word timestamps can stay, but the style would only need clause-level anchoring plus generous holds.
- **Historical framing, primary documents and a running real-model example** would need new `narrative_role` patterns (prologue-as-argument, callback ending, scale-up-to-real-numbers).

## 10. Sources

**Primary: Welch's own words**

- K. Steckles, "−e^{iπ} to Watch: Welch Labs", *The Aperiodical*, 2025-06-30. https://aperiodical.com/2025/06/eipi-to-watch-welch-labs/
- Welch Labs, *Channel Update [April 2017]*, 2017. https://youtu.be/gZPy7OxAjRM (manual captions)
- welchlabs.com: home, AI book (https://www.welchlabs.com/ai-book), jobs (https://www.welchlabs.com/jobs), freelance video editor (/freelance-video-editor), freelance Manim animator (/freelance-manim-animator), designer (/editor), technical research assistant (/technical-reserach-assistant), blog "Coming up for Air" (2021-02-14), "The Bitter Lesson Video – Technical Notes" (2026-01-31). All fetched 2026-11-21.
- Patreon creator page https://www.patreon.com/welchlabs (tiers did not render). The cutout reward is described in video D at 29:50.
- Video transcripts and descriptions of A–H (YouTube auto captions with word timing; manual `en` only for H).
- 3Blue1Brown lesson page for the Welch Labs guest video: https://www.3blue1brown.com/lessons/diffusion-models/ (seen via search listing only).

**Code**

- github.com/stephencwelch/manim_videos (MIT), shallow clone at commit `7b8075f` (2026-11-19). Files cited: `README.md`, `custom_config.yml`, `pyproject.toml`, `custom/welch_axes.py`, `custom/welch_tools.py`, `custom/welch_tip_manimce.py`, `custom/welch_numberline_manimce.py`, `custom/welch_arrow_tip_1.svg`, `custom_gx/welch_style.py`, `sublime_custom_commands/manim_plugins.py`, `_2025/tooling/notion_storyboard_to_pdf_1.ipynb`, `_2026/world_models/p63_64.py`, `_2026/world_models/p50_59_storyboard/*`, `_2025/deepseek/p12_p20.py`, `_2025/backprop_2/p22_24.py`, and comment lines in the backprop_1/2/3, deepseek, sora, generalization, jepa_2 and mech_interp_partial scene files quoted above.

**Not reachable**

- 3Blue1Brown members post "Manim session with Welch Labs" (members only).
- Welch Labs Patreon post "How AI Models Learn, Explained Visually" (HTTP 403).

**Measurement scripts and data**

All in scratch, not in the repo: `research_cache/welch/`.

- `scripts/vtt.py`: VTT parsing, word timing.
- `scripts/punctuate.py`: restores punctuation on auto captions with `oliverguhr/fullstop-punctuation-multilang-large` and drops sponsor/promo chapters.
- `scripts/metrics.py`: WPM, pauses, sentences, questions, pronouns, signposts, n-grams.
- `scripts/validate_punct.py`: model vs YouTube-ASR punctuation check.
- `scripts/shots.py`: merged hard-cut shot lengths.
- `scripts/cut_sync.py`: cut placement vs speech pauses, backdrop switches.
- `scripts/visual_stats.py`: background classes per 5-second frame.
- `scripts/ocr_stats.py` + `scripts/ocr_summary.py`: RapidOCR on graphic frames.
- `scripts/sheet.py`: contact sheets.
- Outputs are in `analysis/`; frames and contact sheets in `frames/`. Video files were deleted after frame extraction.

**Measurement caveats**

- **Background classifier.** It works on whole-frame pixel fractions: ≥ 45 % near-black → black; ≥ 45 % flat slate → grey; ≥ 45 % orange-brown → wood; ≥ 45 % bright → light; anything else → other.
  - It was spot-checked against C's contact sheets and matches the visible sections.
  - Known errors: graphics over a darkened desk count as "black"; zoomed diagrams that fill the frame can fall into "other".
- **Hard-cut detection** misses dissolves and dips to black between dark frames.
- **OCR** at 360p misses the smallest dims and footnotes, and splits or merges some math.
- **Word timings** are from YouTube ASR. E–G come from a newer ASR generation than A–D.
