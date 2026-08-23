# Craft laws (accumulate from production feedback)

These are **non-negotiable defaults for every video** this skill produces.
When the user corrects a video, encode the lesson here as an **abstract rule**
(so the next topic inherits it) — then patch the demo. Do **not** leave craft
knowledge only in chat or only in one demo’s scene file.

**Abstraction test:** if the law still names a specific demo object (one metric,
one dataset, one toy chart) as the *rule* rather than as an *example*, rewrite it.

## Process

1. **Run the pipeline end to end.** A video request means script → TTS → align →
   Manim → render → pixel QA → delivered MP4, in one pass, **without asking for
   approval** of the arc, the script, or the visuals. Self-review against these laws
   instead; the user reviews the finished video. Only stop when a *tool* is blocked
   (missing key, exhausted quota with no fallback) — and say which fallback you took.
2. **Craft feedback is a skill edit, not a chat reply.** Encode it here first
   (see *Feedback → skill*), then patch the demo in the same pass.

## Narrative

1. **Lead with a question / situation**, never “let’s start… / today we will…”.
   Pattern: situation → stake → question → first tool.
   **Independent series open on their own question.** Never open video 01 of a
   new course with “you already know / you already own / as an engineer you
   have…” from another course or from the viewer’s résumé. Each topic is a
   self-contained argument. Inherit-and-hand-off applies *within* a series
   (video n opens on n−1’s close). Video 01 has no previous video in *this*
   series. Domain analogies (RC, filter, table) may appear *inside* a beat when
   they are the picture for a mechanism this course is teaching — never as the
   hook that assumes a previous series.
2. **Tone split:** hooks and story beats = **curious**; definitions and formulas =
   **documentary** (clear, steady, fewer flourishes).
3. **Concrete only for the intro.** After the hook, stay abstract unless a tiny toy
   is needed to read a number. Do not drag the concrete props through the whole video.
4. **Length follows teaching**, not a minute target. Cut fluff; keep clarity.
   **Depth sets length: a hard topic earns more beats.** Count the genuinely
   separate conceptual steps the viewer must take (why this object, why this form,
   why this constraint, each algebraic move) and give each one its own beat with
   its own visual. Never compress a derivation or a historical argument to keep a
   video near the length of the last one — a five-minute topic told in three
   minutes is not concise, it is a summary of an explanation.
5. **Name the object correctly.** Prefer precise domain nouns in VO and captions
   (e.g. “distribution” over a vague “profile”). Wrong names teach the wrong concept.
6. **One question per visual.** Each representation answers one question; morph to a
   new representation when the question changes.
7. **No empty explanations.** Every definition / formula beat must *say what each
   piece means* (numerator, centering matrix, normalization…) while the matching
   part lights or morphs on screen. Naming a symbol without developing it feels
   hollow — prefer one extra documentary sentence over a bare label flash.
8. **Motivate → compute → name.** Before introducing formal notation (Frobenius,
   HSIC, CKA, …), first explain *what is being measured* in plain language and
   *how the arithmetic does that* (even briefly: “multiply matching cells, add
   them up — that scores agreement”). Only then morph into the named formula.
   Do **not** lead with “we use the Frobenius product” and hope the name teaches.
9. **No unmotivated posits.** When the story introduces an assumption, definition
   or constant the viewer could not have predicted, the beat *before* it must
   answer "where did this come from?": what was already known, what was tried,
   what failed, and what pinned this particular form. A fix that simply appears
   — "his move was to assume X" — reads as authorial fiat and teaches nothing,
   however elegant the consequences.
   **When the honest answer is "it was a guess", say so.** Explain what the guess
   was fitted to and which independent constraint fixed its form; naming a
   hypothesis as a hypothesis is part of the explanation, not a gap in it. The
   viewer should leave able to say both *why anyone would try this* and *what was
   still unjustified at the time*.
10. **Spoken numerals are load-bearing.** Any count, delta or value the VO states
   ("five more cross", "about a quarter", "nine of twenty") is a contract with the
   picture. Derive it from the scene's data constants — compute the count in the
   scene module and let the script quote it — or tune the constant until the
   spoken number is literally true. A narrated number the viewer can recount on
   screen and find wrong destroys trust in everything else in the frame.
   **The same holds for on-screen readouts**: a chip reading "≈ 0" beside a
   picture showing a third of the maximum is a lie the viewer can measure. Compute
   readout values with the same function that draws the figure
   (`f"{mean_energy(ratio):.2f}"`), never by hand — then the number and the
   picture cannot drift apart.
11. **Mathematical progress is visible.** When the story advances A → A′ → B in
   math, the on-screen `MathTex` must **morph through those forms** (part-by-part
   `TransformMatchingTex` / staged `ReplacementTransform`), not jump to the final
   equation. Viewers should *see* the derivation, not only hear it.
   Prefer: concrete sum / picture → compact operator → named quantity.

## Voice / TTS

1. **Text rewrite > voice choice.** Ellipses, short beats, rhetorical questions in hooks;
   clean sentences in explanations.
2. **Pacing problems are usually script + chunking**, not the voice ID. Fix speed,
   pause density, and chunk seams before swapping voices.
3. **VO must breathe.** Continuous speech with no thinking gaps feels like the VO is
   *running*. After “take / look at / call this X”, **split the TTS** into a new
   `tts_chunk` and set `pause_after` so silence is baked into the audio. Manim
   soft-idles / pops X in that gap. Do **not** fake long pauses with naked `wait()`
   on continuous audio.
4. **Pause budgets (defaults):**
   | Moment | `pause_after` |
   |--------|----------------|
   | After naming an object | 0.55–0.75 |
   | After a **question** (thinking beat) | **0.9–1.3** |
   | After a heavy morph / formula land | **0.7–1.0** |
   Default `tts.inter_chunk_silence` ~0.4–0.5. Questions that share a chunk with
   the next idea feel rushed — **end the question beat**, pause, then continue.
5. **Chunk for meaning, pause for clarity.** Group related sentences in one chunk for
   prosody; start a **new chunk** whenever the viewer needs a beat to register a new
   object, question, or completed animation.
6. **Head silence** (`tts.head_silence` ≥ 1.0–1.5s) so the first word is not clipped.
7. **One TTS provider: OpenRouter** (`x-ai/grok-voice-tts-1.0`, male voice `leo`).
   No second provider, no fallback path, no per-demo provider switching. If the
   VO feels wrong, fix **text, chunking, pauses, speed** — in that order.
8. **Bookmarks must survive Whisper.** Prefer distinctive spoken words STT keeps.
   Fix any missing bookmark before render. Prefer **chunked STT** when VO has
   inter-chunk silence gaps (full-file Whisper often drops the middle).
9. **Never cue a number or a symbol word.** STT transcribes what it *hears* into
   the shortest written form: "ten percent" comes back as `10%`, "nine" may come
   back as `9`. `align_words.py` normalizes digit↔word and splits symbol tokens
   (`10%` → `10` + `percent`), but the reliable cue is still a distinctive
   **lexical** word next to the number ("fraction", "quota"), not the number.
10. **Cue words must be spelled the way STT writes them.** Transcripts come back
    in US spelling whatever locale the narration was written in, so a British cue
    ("memorises", "colour", "centre") never matches its transcript. `align_words.py`
    folds the known variants (-ise/-ize, -our/-or, -re/-er), but prefer the US form
    in `say` for any cue word that has one.
11. **Cue words must be transcript singletons, and compounds are not safe.**
    Two failure modes, both invisible until a render walks to a cue that already
    happened. (a) A cue word Whisper writes differently — it splits compound
    technical terms, so `wordline` comes back "word line", `lookaside` "look
    aside", `dataflow` "data flow". (b) A cue word the narration says more than
    once: forward-only matching binds it to whichever occurrence follows the
    cursor, which is usually the wrong one, and each late bind drags the cursor
    further so the *following* beats fail too. One mangled word has been
    observed taking thirty cues with it. Choose words that occur **exactly once
    in the whole narration**, and prefer a distinctive multi-syllable word over
    a short common one. `cue_doctor.py` reports what the transcript actually
    says; `cue_repair.py` re-cues automatically; `align_words.py` now joins
    adjacent tokens and rejects implausible forward jumps, but none of that
    beats picking a singleton in the first place.
12. **Repair cues without re-paying for STT.** When only the cue list changed
    (renamed / dropped bookmark, same audio), run
    `align_words.py demos/<slug> --remap` — it re-maps against the words already
    in `timing.json`. Re-run full alignment only when the narration audio changed.

## Motion / Manim

1. **Morph, don’t respawn.** Related A→B uses `Transform` / `ReplacementTransform` /
   height morphs. `FadeOut`+`FadeIn` only for long gaps or unrelated objects.
2. **First appearance must move.** New graphs/charts/structures grow, morph, or
   class-swap — never pop in frozen. Then soft-idle.
3. **Fill the gap, do not take one breath and freeze.** A single `soft_idle`
   covers about a second. When the next cue is six or eight seconds away — a long
   documentary sentence over one figure — the frame is then frozen for the rest of
   it while the narration keeps talking. Use `breathe_until(scene, tn, cue, *mobs)`,
   which repeats gentle idles until the cue is nearly due. `check_sync.py` reports
   these as *still stretches*; treat any over ~6s as a defect.
4. **Dimming is not deletion.** When a beat says an object is suppressed, frozen
   or ignored, that object must stay *legible* — the viewer has to see the thing
   being suppressed. Dim to ~0.5 opacity, never to near-zero, and keep the
   reference it is being compared against at full strength; the contrast carries
   the message. A beat that fades its own subject to nothing renders an empty
   frame while the narration talks about it.
   **Corollary:** when the picture cannot support the claim, fix the parameter or
   soften the claim — do not stack another animation on top. Extra motion added to
   rescue a weak beat usually removes what little was readable.
5. **Soft idle on holds.** During long VO on one figure: gentle pulse / shimmer —
   not a static freeze.
6. **See then hear.** Start the visual ~0.3–0.5s before the narrated label when possible.
7. **Beat suspense (baked pauses).** Between major scenes / after naming an object,
   leave a thinking gap via **TTS chunk boundaries** + `pause_after` / 
   `inter_chunk_silence` — then soft-idle on screen. Never insert naked `wait()` that
   desyncs from continuous speech.
8. **Animations must finish before the next idea.** Size `run_time` so the morph
   *lands* before the next bookmark (use `TimedNarration.play_before` — reserves a
   settle). Do not start the next narrated concept while the previous transform is
   still mid-tween. If the VO needs the finished picture, **bake** `pause_after` on
   that beat so the audio waits too.
9. **Question moves its referent.** If VO asks how / which / what about **X**, the
   mobjects that *are* X must move **while the question is spoken** (pulse, Indicate,
   height shimmer, class-swap) — not after, not frozen. Use `ask_about()` when helpful.
   Viewer must see what “X” is. Then hold through the **question pause** (0.9–1.3s).
10. **Named object pops, then settles.** When VO names a *specific* object (layer \(i\),
   unit \(j\), term \(T\), set \(S\)), that mobject must **pop** at the naming moment
   (scale / Flash / Indicate / brighten) so the eye locks onto it — then a short
   settle in the **audio pause** after the name. Nested names nest emphasis:
   first the container (layer), then the member (unit \(j\) inside it). A label alone
   is not enough if the geometric avatar does not move.
11. **Causal pairs move together.** When VO describes how A changes with B (e.g. input
   → neuron activation), animate **both** sides in lockstep — cycle the inputs *and*
   show the dependent object responding. Never narrate a dependence while only one
   side of it moves.
12. **Labels sit on the correct side of the story.** If VO says inputs have classes /
   groups (dogs vs cats), those labels attach to the **input** side — never park class
   chips on the output just because there is empty space there.
13. **Procedures are staged, not flashed.** When VO describes a multi-step process
   (choose quota → rank → keep/cut → lock; build a formula; compare cases), animate
   **each verb** as a readable step. A single recolor / one-shot Transform that jumps
   to the end state is not enough — the viewer must see *what is being selected /
   built / discarded* and why.
14. **Formula BUILD_UP.** For any equation that is *derived*, script `show:` must
    list the morph stages (term → next term → full line). Manim should
    `TransformMatchingTex` / Indicate parts in lockstep with spoken meaning.
    Dropping the finished `MathTex` in one `Write` is only OK for a one-symbol label.
15. **Picture matches the spoken noun.** The on-screen schematic must depict the
    structure the VO just named. If VO says a whole system (network, pipeline, graph),
    show the **whole** system first; when VO narrows to a part (“this layer”, “this
    node”, “this term”), focus / isolate that part, then morph it forward. Never leave
    a mismatched or underspecified schematic on screen for the whole beat.
16. **Do not Indicate whole heatmaps / dense grids.** `Indicate` / `ask_about` on a
    grid of cells can wash fills to the highlight color. Pulse the **border** /
    SurroundingRectangle, or rebuild the heatmap after. Same for any many-cell
    VGroup whose fill encodes data — bar rows and 1-D sequence strips included.
    **This covers `ask_about` referents**, whose motion is an `Indicate`: pass a
    `SurroundingRectangle` drawn *around* the subject, never the subject itself —
    and a labelled card's own frame is not a safe substitute, since recolouring it
    repaints the fill its label sits on. Ring it from outside and the colour
    coding, the fill and the label all survive.
17. **Parametric figures must be checked at the extremes you animate to.** When a
    visual encodes a physical parameter (rung spacing ∝ frequency, bar height ∝
    gain), the builder silently clips or drops elements at the far end of the
    range — and the beat that indexes those elements crashes, or worse, quietly
    shows nothing. Before rendering, evaluate the builder at every value the
    scene uses and assert the pieces the beat needs still exist and sit inside
    the frame. Pick the parameter so the *teaching* is visible: the whole point
    of "one lump costs more than kT" is seeing that rung above the line.
18. **Bind every `.copy()` you animate.** A copy passed inline to an animation
    (`ReplacementTransform(a, b.copy())`) becomes a new, unnamed mobject that no
    later `FadeOut(original)` can reach — it simply stays on screen for the rest
    of the video. Assign it to a name and dispose of that name. Ghost mobjects
    never fail a test; they only show up in pixels.
19. **Render ≥30fps** (`-qm`). `-ql` (15fps) looks stepped even with smooth rate funcs.
20. **Visual-only iteration is allowed** when wording/pauses are already correct.
    If pauses or spoken nouns are wrong, **regen TTS** (split chunks + `pause_after`)
    then align — do not only re-render Manim.


## Layout / text

1. Use **LayoutBoard** + reserved bands (title / key / panel-label / bottom).
2. Run layout tests (`pytest tests/test_layout.py` or demo snapshots) before calling
   a scene done.
   **A snapshot must contain every text-like mobject that is on screen at that
   beat — and only those.** A snapshot listing a subset certifies a frame that
   never occurs: two chips that each pass alone still collide when they are
   co-present. An *over*-inclusive snapshot is equally wrong — it invents a
   collision between things that never share the screen, and you "fix" a layout
   that was fine. When a beat passes through two states (a chip is replaced, a
   figure is cleared mid-beat), snapshot **each state separately**. Build every
   snapshot from "what is alive at this instant", not "what this beat mentions".
3. **Every label dies with its referent.** A panel label, tag or caption that
   names an object must be faded in the same `play` that removes the object. A
   label outliving its figure silently mislabels whatever occupies that space for
   the rest of the video, and no overlap test can catch it — only pixels can.
   **This includes emphasis decorations**, which are the ones actually forgotten:
   a `SurroundingRectangle` / ring / arrow drawn to highlight something is not
   part of that something, so the `FadeOut(figure)` at the section boundary does
   not reach it. It then sits on an empty stage for the rest of the video as a
   mysterious empty box, and later lands on top of whatever the next section
   draws there. Every ring goes into the same disposal `play` as its subject.
   Neither audit sees this: an empty rectangle overlaps no *text*, and the cue
   windows it sits through are full of other motion.
4. **Give each persistent chip its own reserved x slot.** Counters, quotas, gain
   badges and readouts accumulate as a video goes on; place them from named
   constants (one slot each) instead of eyeballing a free-looking gap, and the
   collision cannot happen when a later beat adds one more.
5. **Never crossfade two key sentences in one `play`.** `FadeOut(old)` and
   `FadeIn(new)` in the same call leaves both in KEY_BAND for the whole run
   time, which `watch_layout` reports as a live collision and `assert_clear`
   cannot see (it only samples where you call it). Sequence the handover: fade
   the old one out, `board.clear` it, then fade the new one in. Same rule for
   any two mobjects that share one reserved slot.
6. Key sentences park in **KEY_BAND**, never into the title strip.
6. Labels beside/above objects in reserved bands — never on growing bars.
7. **A section boundary must dispose of the previous figure, explicitly.** Before
   the first mobject of a new section lands, every mobject from the previous one
   is faded, shrunk to a thumbnail, or morphed forward — decided in the same
   `play`, never left to chance. Writing equations where a diagram still lives is
   the most common way a long video goes unreadable, and it is invisible in the
   code: each section looks correct in isolation. Prefer shrinking to a corner
   thumbnail over fading when the figure returns later — it keeps the identity
   link and shows the viewer it will be back.
8. **Never occlude the primary figure with prose.** Do not drop questions, captions,
   or glosses into the middle of the frame while a graph / net / diagram owns that
   space. Put text in a reserved band (KEY / BOTTOM / panel-label), or **clear /
   shrink / shift** the figure first, then use center stage. Center-stage text is
   only legal on an empty (or intentionally vacated) stage.
9. **Figures need air.** Dual panels / bar charts / nets must keep clear gutters
   between panels and between figure and text (≥ ~0.35–0.5 manim units). If a label
   or equation fights a growing bar, move the label to a reserved band or shrink /
   shift the chart — do not let them share the same pixel region.
10. **Spoken state-words drive the visual.** When VO uses a key adjective / state name
   that has an on-screen avatar (spread, piled, gold, cutoff, scale…), that label /
   morph must **appear or play on that word** — not earlier as a static prop, and not
   after the line has already passed.
11. **Never narrate a frozen motion.** If VO says “scale / grow / morph / cut”, the
   figure must be animating on that verb (bookmark the verb). Do not speak the action
   while the chart sits still and only move later on a different word.
   **Loudness must change pixel height:** if bar heights are peak-normalized, scaling
   every value by a constant is a no-op on screen — use a shared `ref_peak` or
   `multiply_heights` so quiet→loud is visible and more units can cross a fixed cutoff.
12. **Sibling cards must read at one type size.** Helpers that shrink text to
   fit a width (`safe_text(..., max_width=…)`) are silent: the short label keeps
   its font size and the long one is scaled down, so two cards presenting a
   parallel pair — the two branches of a fork, the two halves of a comparison —
   end up visibly different sizes and the longer idea reads as the lesser one.
   Wrap the long label onto two lines at the shared size (`safe_multiline`)
   instead of letting it shrink. Check any card whose text you did not choose
   the width for.
13. **Highlighting must keep the label readable.** Never raise a labelled chip /
   box / node to full fill opacity in the *same colour as its own text* — the word
   disappears. Emphasize with fill ~0.4–0.55 + brighter stroke + a contrasting
   (white) label, and dim the others rather than blanking them. Same for
   `set_opacity(1.0)` on any VGroup that mixes a filled shape with text on top:
   it silently drives the shape's fill to 1 as well. (Also: `set_opacity` on a
   group containing an `Arc`/outline turns it into a filled blob — set stroke
   opacity instead.)
   **A `(grid, SurroundingRectangle)` sheet is the same trap and the commonest
   one:** `set_opacity(f)` on that pair raises the *rectangle's fill* opacity too,
   so the border stops framing the data and becomes a coloured pane painted over
   it — at `set_opacity(1.0)` the grid disappears completely behind a solid
   block. Drive the grid's fill and the border's stroke separately (a
   `dim_sheet(group, frac)` helper), and never `set_opacity` a group that mixes a
   filled figure with an outline. No audit catches this: the frame is fully
   populated, nothing overlaps, every cue window has motion — only pixels show a
   flat rectangle where the data was.
   **Corollary — emphasize the frame, not the group.** `Indicate` / `pop_named`
   on a card, chip or labelled box recolors *every* submobject, so the label ends
   up the same color as the fill it sits on. Build such objects as
   `VGroup(frame, body)` and animate them separately: pulse the frame's stroke,
   tint its fill ≤ ~0.2, and drive the body's opacity on its own. Dim/undim
   helpers beat a bare `set_opacity` on the whole card.
14. **One conceptual lane.** Do not reopen a closed layer of the story (e.g. finish
   the class-mean *distribution*, then talk as if we are back to raw activations).
   Advance: activations → means → distribution → mass / shape → number. Each step
   names the *current* object.
15. **Visual QA loop (mandatory before calling a render done).** AABB occupancy
    catches overlaps and leftovers; **pixels catch the rest**. After the
    geometry pass:
    1. Run `scripts/qa_frames.py demos/<slug>` (tiles `out/keyframes/`).
    2. **Read the contact sheet**, then **Read full-resolution frames** for *every*
       beat that adds a caption near a figure (not only a sparse bookmark list).
    3. Check: text contrast, gutters, no text↔graph occlusion, labels on the correct
       side, spoken adjectives visibly matched, **formula stages readable**.
    4. Fix; re-run the geometry pass; re-read until clean.


## QA / tooling

1. **`qa_frames.py` defaults to every bookmark in `timing.json`.** Do not hard-code
   cue lists from a previous demo — sparse or wrong-topic cues miss caption-near-figure
   beats. Pass `--bookmarks` only to narrow intentionally.
2. **`lint_script.py` before TTS.** Warns on questions without a long `pause_after`,
   formula beats whose `show:` lacks BUILD_UP/MORPH, and missing `latex` on math beats.
   Prefer scripts that show sum/product stages before named operators (Frobenius, HSIC).
3. **`TimedNarration.play_before`.** Prefer over bare `play` when a morph must land
   before the next bookmark.
4. **Never read a colour off a `Text`.** `Text` is a `VGroup` of glyphs and its
   *group* colour is unset, so `mob.get_color()` returns black. A helper that
   re-creates a label "in the same colour as the old one" therefore paints it
   black on a black background: invisible, and invisible to every mechanical
   audit — the mobject is present, nothing overlaps, the cue window has motion.
   Read the colour from the thing that actually carries it (a frame's stroke, a
   role constant), never from the glyph group.
5. **A render that stops advancing has asserted, not hung.** Layout assertions
   abort the process, so the last `Animation N` line sits there looking like a
   stall under load. Always read the log tail before blaming contention:
   `sed 's/\x1b\[[0-9;]*m//g' <log> | grep -E "^  (overlap|oob):"`.
6. **Marginal overlaps are still overlaps.** `assert_clear()` pads by ~0.08, so
   two labels a tenth of a unit apart fail. When inserting something *between*
   two existing objects, move **both** neighbours — shifting only one just moves
   the collision to the other side.
7. **Scan for mobjects that are added and never removed.** Before rendering,
   list every name passed to `FadeIn` / `Create` / `Write` / `Grow*` and subtract
   every name passed to `FadeOut` / `ReplacementTransform` / `TransformMatchingTex`
   and every name folded into a `VGroup` that is disposed of. What remains should
   be exactly the mobjects meant to persist to the last frame (title, final
   equation, closing note). Anything else is a ghost that will ride the rest of
   the video. This is ten lines of static analysis and it catches in seconds what
   otherwise costs a full render plus a frame-by-frame read.

## The three audits (mandatory, mechanical)

Craft laws about motion and layout used to be checkable only by a human reading
1000 lines of scene code and a sparse strip of stills. They are now enforced:

1. **`check_sync.py` — every cue window must contain motion.** A cue marks a
   visual event by definition, so a silent window is proof that the narration
   described something and the frame sat still. Fix silent cues before shipping;
   treat *thin* windows (a token pulse standing in for a described change) as
   suspects. Requires nothing but `TimedNarration`, which records the timeline.
2. **`check_layout.py` — no text may overlap text for longer than a glance.**
   Add `watch_layout(self, DEMO_DIR)` beside `tn.attach(self)`. It samples the
   live frame several times a second, so it catches collisions that happen while
   something grows, slides, or sits at maximum size — exactly the ones static
   snapshots and bookmark stills both miss. Brief crossings during a morph are
   filtered out; anything that lingers is real.
3. **`qa_frames.py` tiles captured stills, not an MP4.** The geometry pass
   already rasterized cues, play ends, and overlap openings into
   `out/keyframes/`. Bookmark stills remain useful for reading the story; they
   are not a layout check.

A render is not done until all three are clean or every remaining item is
deliberate and stated.

## Feedback → skill (mandatory)

When the user says “X felt wrong”:

1. **Abstract** the lesson into a law in this file (applies to *any* future video).
2. Mirror it in the relevant `reference/*.md` (layout, narrative, sync, …).
3. Update `templates/` defaults / helpers if the pattern should be the starting point.
4. Only then patch the current demo.

Do not “just fix this video.” The skill exists so the same feedback is not repeated
for every new topic.

## Register every figure with the board, or the audits are blind

`LayoutBoard.assert_clear()` only compares what was handed to `board.add(...)`.
A table, strip or panel built and positioned without registering it is invisible
to the check, and so are all the collisions it causes. Two videos shipped defects
of exactly this shape:

- an instruction strip whose last chip's rectangle ran through the `counter`
  pointer label beside a memory table — neither was registered
- a memory table sitting in the same band as every caption and outcome chip in
  the scene, its border painted across three of them

Both looked fine to a green `assert_clear()`. When a figure is placed, register
it in the same breath. If a collision is reported against something you thought
was elsewhere, the fix is usually to register the *other* thing too and let the
board tell you the truth.

## A box either contains a text or does not touch it

The most common real collision is not text over text — the two glyph runs never
meet. It is a **box border cutting through text**: a chip rectangle running into
the label beside it, an emphasis rectangle starting mid-word, a table's edge
crossing a caption, a caption overflowing the panel it was meant to sit in.

`check_layout` now reports these as `box-cuts-text`, using the rule above: a
partial overlap between a drawn rectangle and a text is always a defect, while
full containment (a chip and its own label) is always fine. Text-over-text
still blocks the build; `box-cuts-text` is surfaced for the frame review to
judge, because a bar behind a label or deliberately stacked cards are legitimate.

## Clearance is 0.17, not 0.16 — leave 0.25

`LayoutBoard` pads **both** boxes by 0.08 (its `pad` default), and the overlap
test uses `<=`, so a gap of exactly 0.16 is still reported. Measured:

| gap | reported |
|-----|----------|
| 0.14 | overlap |
| 0.16 | overlap |
| 0.17 | clear |

So the true minimum is 0.17 and there is no margin at it. **Leave 0.25 or
more.** Most of the layout failures in one 15-video series were of exactly one
shape — two figures 0.10 to 0.14 apart — and several fix attempts moved
something to precisely the minimum and failed again.

## Fixing one assertion exposes the next

Layout assertions abort on the first failure, so a scene with four of them takes
four rounds. Expect a cascade and keep the `-n 0,1` loop tight rather than
reading the first failure as the only one.

## Every drawn encoding is computed from named fields and asserted

A hand-typed bit string is a factual claim no audit and no frame review can
check — 32 characters all look equally plausible, and the field brackets under
them look right wherever they are put. One video reached the review gate with a
`fence w,w` strip that was wrong twice over: the bits were not the instruction,
and the `pred` / `succ` brackets pointed at the `rd` and `opcode` fields.

Build the word from its fields and assert it against the known value:

```python
_FENCE_W = 0b0001                       # the W bit of a pred / succ field
FENCE_WW_WORD = ((0b0000 << 28) | (_FENCE_W << 24) | (_FENCE_W << 20)
                 | (0 << 15) | (0b000 << 12) | (0 << 7) | 0b0001111)
assert FENCE_WW_WORD == 0x0110000F, "fence w,w assembles to 0x0110000f"
FENCE_WW_BITS = format(FENCE_WW_WORD, "032b")
FENCE_PRED_SPAN, FENCE_SUCC_SPAN = (4, 7), (8, 11)     # string indices, from the left
assert FENCE_WW_BITS[4:8] == "0001" and FENCE_WW_BITS[8:12] == "0001"
```

Assert the field spans too, not just the word. `bitfield()` takes **string
indices from the left**, which are the complement of the bit numbers the ISA
manual quotes: for a 32-bit word, `bits[31:28]` is `s[0:4]`. Getting the word
right and the brackets wrong still draws a lie. The same discipline already
protected the `lw` strip in another video, where the word came from a computed
constant and the spans matched the spec exactly.

## A faded figure is still a box unless the slot is cleared

`FadeOut` changes opacity; it does not change coordinates, and it does not
unregister the slot. A board slot whose mobject has been faded therefore keeps
contributing a **phantom box** at the old position, and everything later placed
there is reported as colliding with something the viewer cannot see. Chasing
those as real defects wastes whole render cycles.

`assert_clear()` now skips figures whose fill and stroke opacity are both
effectively zero, which matches what `layout_watch` already did on the live
frame. Still call `board.clear(name)` when you dispose a figure — the opacity
check is a safety net, not a licence to leak slots. And check the *names*: a
`board.clear("c0head")` for a slot registered as `"head0"` silently does
nothing.

## The detectors are helpers; the frame review is the gate

A chip's rounded border ran through the "slot 0" label of the queue row it was
placed in, for fifteen seconds, and `check_layout` did not report it — the same
geometry flagged correctly in an isolated test, so the real scene fell just
outside a threshold. It was found by looking at the frame.

Take the reports as a list of places to look first, never as proof that the rest
is clean. Every tool here narrows the search; none of them closes it.

## A label that outlives its section can be wrong, not just misplaced

One panel label reading "snooping: every cache listens" was never disposed and
rode into the section that replaced snooping with a directory and a mesh. That is
not a layout blemish — for the length of that section the caption asserted the
opposite of the picture. When checking leftovers, ask what the stale figure is
*claiming*, not only what it overlaps.

## Anchor a caption to the thing it labels, never to an absolute y

Almost every `box-cuts-text` defect in one 15-video series had the same shape: a
caption pinned to a hand-chosen `y` that happened to land on the **bottom border
of the very box it was describing**. The author picks the number by eye against
one render; the box's height then comes from its content (`queue_card(4,
row_h=0.34)` is 1.36 tall, a `SurroundingRectangle` adds its buff), so the
caption ends up on the edge and the border strikes through the words.

Observed in one scene alone: "one ready list" on its card's frame for 6 s, "one
ready list per core — one lock per core" across four queue cards for **51 s**,
and "working set" on its ring's border for 16 s.

Write the relationship, not the coordinate:

```python
list_lab.next_to(list_card, DOWN, buff=0.24)
count_chip.next_to(list_lab, DOWN, buff=0.20)
ws_name.next_to(ws_ring, UP, buff=0.20)      # below it, the bottom band leaves 0.16
```

`next_to` survives a change in the box's contents; an absolute `y` does not. Use
absolute coordinates for the *figures*, relative placement for their *labels*.

## When a band cannot hold everything, retire a caption instead of shuffling

The same scene had a 0.79-high band that four things wanted: the queue cards'
caption, two load chips, a theta marker and an equation — 0.95 of content with
clearance. No arrangement fits, and three attempts at nudging one of them each
traded the collision for a different one.

The answer was not a better position. The partition caption had already been
read by the time the load-balance beat began, so it was **disposed at its own
beat boundary** and the band held the rest comfortably. Ask what still needs to
be on screen before asking where to put it.

## A box that swallows a text whole is occlusion, not containment

The containment rule — "a box either fully contains a text or must not touch
it" — has a hole. When a *wide* panel is laid over a *small* node, the node's
label ends up 100 % inside the panel, which the rule reads as legitimate. One
video shipped an entire MOESI state diagram buried under a later comparison
panel that way: "your copy is wrong" sat exactly on the `S` node, and `O` sat on
the core boxes, for the rest of the section.

The distinction is ownership. `check_layout` now records each leaf's top-level
ancestor and reports full containment as **box-buries-text** whenever the box and
the text belong to different top-level mobjects. A chip containing its own label
shares an ancestor and stays silent.

## Two things that made the layout audit quietly narrower than it looked

Both were found by testing the detector against a case it had missed, rather than
by trusting a green report:

1. **`family_members_with_points()` skips text.** A manim `Text` has
   `has_points() == False` — its outlines live in `VMobjectFromSVGPath` children —
   so walking the family that way never yields the `Text` itself. Walk
   `get_family()`, which includes point-less parents.
2. **A `MathTex` parent reports zero opacity.** The glyphs carry it, not the
   parent, so an "is it visible?" filter reading only the parent discarded every
   equation. Fall back to the maximum over children.

The lesson under both: a checker that reports "0 problems" is making two claims —
that it looked, and that it found nothing. Test it against a defect you have
already seen with your own eyes before believing the second one.

## Containment is only occlusion with draw order and fill

The first version of the buried-text check asked one question — do the box and
the text belong to different groups? — and reported 46 violations on a video that
had none. Every one was innocent, for two reasons worth knowing:

* `set_reg` / `set_readout` / `set_cell` swap a value with `Transform`, which
  re-adds the **new** text as its own top-level mobject. Its own cell box then
  looks like a stranger enclosing it.
* A `SurroundingRectangle` ring is *supposed* to enclose things it does not own,
  and hides nothing, because it has no fill.

A box conceals a text only when all three hold: it fully contains it, it is
painted **after** it (`scene.mobjects` is drawn in order, so a later index is on
top), and it has real fill (> 0.30). With those, the check finds the genuine case
— an opaque panel laid over a state node — and stays quiet on the rest.

The general lesson: a geometric test alone cannot decide occlusion. Occlusion is
geometry **plus paint order plus opacity**, and a checker that ignores two of the
three will bury you in noise and get ignored — which is worse than not having it.
