# Synthesis: how these styles are made, and what it means for the skill

Written 2026-11-21 from the five research docs. Every number here is copied from them; follow
the links for method and sources. Measured pause figures use different thresholds per doc
(noted where it matters), so compare pauses within a doc, not across docs.

- [styles/3blue1brown.md](styles/3blue1brown.md)
- [styles/welch-labs.md](styles/welch-labs.md)
- [styles/floatheads-physics.md](styles/floatheads-physics.md)
- [styles/landscape.md](styles/landscape.md) (8 more channels, tools, published script guidance)
- [agentic-systems.md](agentic-systems.md) (how automated systems do it)

## 1. From idea to finished video

| Stage | 3Blue1Brown | Welch Labs | FloatHeadPhysics |
|---|---|---|---|
| Idea | Starts only when there's an "aha" to build around | "The most compelling and clear question I can" | The "silly" fundamental questions teachers brush off |
| Research | Self; sample lessons before scripting | Self + paid research assistant; notebooks on real models | Feynman Lectures; Feynman technique on himself |
| Outcome design | Core visual chosen early ("the core visual around which the narrative will revolve") | Reframe found in the research ↔ writing loop becomes the spine | Backward design: outcome → misconceptions → storyline → visuals |
| Script | Full script; wording changes while animating | Numbered paragraphs (p1…p85), iterated with the RA | Outline-like; A-roll has natural self-corrections |
| Storyboard | Not documented | Notion + 1920×1080 Illustrator frames per paragraph range, with notes | Not documented |
| Voice | Records himself over the laid-out clips | Records himself; sometimes trims VO to fit an animation | On-camera take = narration |
| Animation | His manimgl, interactive, 24–55 short scenes per video | manimgl, interactive, one file per paragraph range; Illustrator SVGs; desk shoots | Unknown tool; screen-recorded canvas likely (inferred) |
| Sync | By hand in Final Cut | By hand in Premiere, cuts in speech pauses | Tight, in the edit |
| Review | Patreon early release | Not documented | Patreon early drafts |

The landscape adds the same picture from other channels: most write the script, record the
voice, then animate and time the visuals to it (Kurzgesagt, minutephysics, Branch, Core Dumped).
Kurzgesagt calls writing "the bottleneck" and goes through about a dozen drafts. Nobody
syncs in code; every human creator syncs in an editor.

**What this means for us.** Our pipeline already has the right order (script → voice → timed
visuals). What humans do that we don't:

- They **plan the frame before animating it**: Welch's storyboard frames, Grant's core visual.
- They work in **short shots joined in an edit**, not one long take.
- They **review the script** before production: Grant's sample lessons, and Patreon drafts
  for both Grant and Mahesh.

## 2. How the script is built

### Openings

| | 3Blue1Brown | Welch Labs | FloatHeadPhysics |
|---|---|---|---|
| First line | Concrete in 7 of 8 videos (a digit, a baby's head, two lists) | A real artifact, a historical moment, or a provocation | A common claim, then "Or are they?" |
| Then | Central question within 0:05–1:30; cold open of 1–3 min before the logo (since 2019) | The driving "how exactly / why" question by about 1:00 | Personal confession → source / mentor reveal → "rediscover" → "let's begin" |

### Middle

| | 3Blue1Brown | Welch Labs | FloatHeadPhysics |
|---|---|---|---|
| Spine | Several templates: phenomenon → challenge → build; puzzle → result → formula → return; practical question → history → reinvent | One running real-model example from start to end; scale-up to production numbers; a measured payoff | Socratic dialogue: the mentor poses, Mahesh answers wrongly, the mentor hints, the idea is rebuilt |
| Jargon | Operate first, name second; names are scarce (one explicit naming every 2–20 min) | Show first, then "called / known as"; every symbol tied to a real dimension | "Name after need": the term arrives after the idea is rebuilt |
| Viewer's voice | Voiced objections ("I hear some of you asking…"), pi creatures, "pause and ponder" | Rare; a staged rebuttal at most | Built into the dialogue: he plays the naive learner |
| History | Motivation, not chronology | The default frame; primary sources on screen | Frame of a whole video, or the hook; the scientist becomes the mentor |

### Endings

- **3Blue1Brown:** return to the opening with a portable principle, an open puzzle, or a
  next-chapter tease. Never a recap list.
- **Welch Labs:** open questions in a row, a hedged personal take, "it will be fascinating to
  see…", a callback to the opening, then the outro.
- **FloatHeadPhysics:** collapse everything to one root cause, a wonder line, tease the next
  video, then stop abruptly.

**Ben's preference (decision 15):** logical steps forward and a flow of data and information,
as in 3b1b and Welch. FloatHeadPhysics' narrated dialogue with a mentor is out. Its
misconception-first opening and frame hygiene stay as research input only.

**Shared across all three, and already in the skill:** concrete before abstract, one running
example, the naive answer that fails before the real one, and an ending that closes the opening.

**Not in the skill:** a cold open before any title, the viewer's voiced objections, history as
the frame, and endings other than "return to the anchor".

## 3. Language

| | 3Blue1Brown (V1–V8) | Welch Labs (A–G median) | FloatHeadPhysics (S1–S6) | Our 47 demos |
|---|---|---|---|---|
| Words per minute | 175–199 | 169 | 154–203 (slowing over time) | 139 (median, voiced span) |
| Mean sentence (words) | 22.6–31.3 | 22.3 | 11.9–17.5 | not measured |
| Questions per minute | 0–0.75 | 0.19 | 1.9–2.6 | 0.9–1.3 s pause after each |
| "you" per 1k words | 19–29 | 1.6 | 16–29 | not measured |
| "we" per 1k words | 7–17 | 34 | 17–30 | not measured |
| "I" per 1k words | 7–13 | 1.7 | 10–20 | not measured |
| Register | One conversational voice; 17–25 contractions per 1k | Measured, documentary, exact numbers | Chatty, personal, reacts big ("Whoa!") | Tone split: curious hooks, documentary explanations |

Pauses: 3b1b has 0.45–1.8 audio pauses of 1 s or more per minute (falling over time). Our
demos have 4.6 per minute, measured the same way by the 3b1b agent. Welch and FloatHeadPhysics
used different thresholds, so they are not in this table.

**What this means.** Each style is a different speaker. Words per minute, sentence length,
question rate, pronoun mix and register are all measurable, so a style can set targets and the
script lint can check them. Our current narration is slower and far more paused than any of
the three.

## 4. Timing against the voice

| | 3Blue1Brown | Welch Labs | FloatHeadPhysics | Our skill |
|---|---|---|---|---|
| Granularity | Idea per shot | Clause | Spoken noun | Cue word |
| Offset | Picture follows the voice by 0–0.3 s when starts line up | Change lands near its noun; cuts fall in pauses (44–64% vs 11–24% chance) | −0.8 s to +0.4 s around the noun | "See then hear": 0.3–0.5 s before |
| Animation length | Mostly 1 s waits between plays; plays of normal length | Modal 2–3 s, often 5–10 s | Not measured | Median 0.30–0.37 s in pf-08…13 |
| Still frames | 27–85% of frames; 15–30 s holds in every video | Few long silences, but the camera or a lagged reveal keeps moving | A finished board can hold for minutes | Breathing idles; `check_sync` flags any gap over 6 s |
| Emphasis | Colour the term, flash under it, dim the rest; `Indicate` almost never | Dim the rest, a small yellow arrow, an outline box; no `Indicate` | ✗ / ✓ stamps, boxed results, glow | `Indicate` pulses, scale-and-recolour |

**What this means.** No reference style snaps changes onto single words. All three let a frame
hold still while the voice explains it. Our freeze-then-burst problem (see the
[diagnosis](README.md#diagnosis-the-frame-freezes-then-everything-happens-at-once)) comes from a
sync model that none of them use. The research supports word-level *alignment* (Mayer: spoken
words at the same time as the matching graphic, d = 1.31). It does not support word-level
*snapping*.

## 5. How frames stay clean

Rules that two or more of the three styles share, with evidence:

| Rule | 3b1b | Welch | FHP | Agentic systems |
|---|---|---|---|---|
| Plan the layout before animating | core visual first | 1920×1080 storyboards; code redraws them from pixel coordinates | – | Strongest evidence of any fix (OmniManim, Code2Video grid) |
| Very little text per frame | median label 2 words; 74% ≤ 3 | 1–4 caps words per label; 5–22 items per graphic | median 1–5 words, max about 15–22 | Text budgets per slot (practitioner rules) |
| Text sits next to its object | 44–65% in the middle half of the frame | captions under or beside the object | labels on leader lines | – |
| A fixed place for each kind of text | no fixed bands | title, caption row, dimensions, footnote, legend: never shared | keep-out zone for the camera card | anchor grids |
| Never shrink text to fit | hand-broken at about 30 characters | narrow size band (mostly 20–32) | – | `fitText` floor, then rewrite the copy |
| Dim, don't delete or move | yes | yes (3,584 `set_opacity` calls) | yes | – |
| Readable over busy figures | black stroke behind text (`set_backstroke`) | text kept off busy plot areas | – | – |
| One colour per concept | across prose, formulas, figures | one colour per entity for the whole video | colour-coded LaTeX | – |
| Many short shots, not one long scene | 24–55 scene classes | one file per paragraph range | hard cuts between layouts | Code2Video renders scenes in parallel |

**What we do today instead:**

- free placement from a free-text `show:` field;
- horizontal text bands (title / key / panel label / bottom);
- `safe_text` shrinks text to fit;
- one scene class of up to 3,751 lines;
- no text backstroke.

## 6. What a style has to specify

From the comparison, a style pack needs these parts. The landscape doc proposes the same axes.

1. **Narrative mode and templates:** the opening sequence, the spine, how jargon is introduced,
   the viewer's voice device, the ending.
2. **Speaker profile:** targets for words per minute, pause budget, sentence length, question
   rate, pronoun mix and register, which the script lint checks.
3. **Sync grammar:** granularity, allowed offset from the anchor word, minimum animation
   length, and whether holds are allowed.
4. **Visual tokens:** background, palette with a role for each colour, fonts per text role,
   stroke widths, arrow tip.
5. **Text policy:** the named slots, word budget per slot and per frame, size band, how labels
   attach, backstroke.
6. **Emphasis vocabulary:** which highlight moves are allowed, and which are banned (e.g.
   `Indicate` for 3b1b and Welch).
7. **Composition patterns:** a style's recurring layouts (3b1b: text left / figure right,
   insets; Welch: anchor diagram plus camera stops, comparison tables).
8. **Rule overrides:** which core laws this style relaxes (see §7).
9. **Banned tells:** things that make it look generated or off-style.

## 7. Where the current skill's rules clash with the reference styles

| Current rule | 3b1b | Welch | FHP | Suggestion |
|---|---|---|---|---|
| Hard rule 5: never open with "let's start…"; tone split | Keeps one voice, no split | – | Opens "So Feynman, where do we start?" | Move the opening rule and tone into the style |
| Hard rule 8 + lint: every spoken change has a visible one, on that word | Idea-per-shot, loose | Clause | Noun, tight | Keep the principle; change the mechanism to phrase spans (§4) |
| Hard rule 9: never prose on a live graph | – | Notes and footnotes in their own slots | – | Allow prose in a declared slot, off the plot area |
| Hard rule 10: no exact numbers or tables | Toy numbers only | Exact numbers are central | – | Make it a style setting |
| Breathing idles; still stretch > 6 s is a defect | 15–30 s holds | Holds after key results | Minutes-long holds | Delete idles; allow holds |
| Bands for titles, keys and captions | No bands; labels on objects | Fixed slots per kind of text | Keep-out zone | Slots defined by the style, plus labels attached to objects |
| `Indicate` / pop emphasis | Almost never used | Unused | – | Use the style's emphasis vocabulary |
| Pause 0.9–1.3 s after every question | Above its 90th-percentile pause | – | – | Pause budget from the style's profile |

## 8. Lessons that apply to every style

These are style-independent and are the strongest candidates for the redesign's core. Ben
adopted 1–3 and the §7 rule split as decisions 18–21 (README, 2026-11-21).

1. **Plan the frame before code.** Each beat's objects get a place in a layout plan (style slots
   or a grid). Code places objects through the plan, and checks compare against it.
2. **Short shots, stitched.** One scene per beat or shot, each starting from a known stage,
   rendered in parallel and joined at mux time.
3. **Phrase-level sync with holds.** A visual change spans the phrase that describes it and
   lands near its anchor word. Still frames are fine while the voice explains them. No idle
   motion.
4. **Text discipline.** Short labels attached to their objects, a fixed size band, never
   shrink to fit, backstroke where text crosses a figure, dim instead of delete.
5. **Measured targets.** Pace, pauses, text per frame and emphasis are numbers a style sets and
   a check verifies, the way `check_sync` already checks motion.
6. **Use the agent's vision for meaning.** Geometry gets deterministic checks with computed
   fixes; the frame review asks whether the picture says what the voice says.
