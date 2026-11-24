# Intuitive derivation and logic-first explanation: FloatHeadPhysics study

Written 2026-11-24. A follow-up to [styles/floatheads-physics.md](styles/floatheads-physics.md)
and [narrative-pattern.md](narrative-pattern.md).

**Problem.** Videos generated with `manim-explain` lean too hard on math, exact equations and
numbers, and not hard enough on the ideas, thought process and logical steps that make those
equations feel inevitable. The first FloatHeadPhysics study focused on surface format (camera
card, palette, WPM, and his reported-speech dialogue with a dead scientist). When decision 15
ruled out the dialogue device, the **reasoning craft** running inside it was left behind.

This doc isolates how FloatHeadPhysics (Mahesh Shenoy) builds intuitive derivations — and how
he, 3Blue1Brown and Welch Labs actually ration numbers and equations — so those mechanics can
be built into the skill's core laws, research workflow, scripting guide and lint without
adopting his dialogue gimmick.

**Tags.** `[measured]` comes from scripts run over the cached transcripts in `research_cache/`
and the three current demos under `demos/`. `[verified: source]` means a primary transcript or
doc states it directly. `[inferred: from what]` is my reading of the evidence. Timestamps are
`mm:ss`.

---

## 1. Diagnosis: why our videos sound like spec sheets

### 1.1 Measured comparison across 24 reference videos and 3 demos `[measured]`

Every corpus was measured with the same tokenisers on spoken narration only (timestamps
stripped; Welch uses clean `punct_text` excluding sponsors/interviews).

- **NumMnt/1k:** contiguous spoken numeric mentions per 1,000 words — both digits (`150,528`,
  `77.2%`, `16`) and spelled-out number phrases (`minus seventy`, `one hundred and forty`,
  `two hundred and sixty`), excluding calendar years (`1800–2099`) and standalone pronoun `"one"`
  while counting compound `"one hundred"`, `"one million"`, etc.
- **Spec/1k:** exact decimals (`77.2`, `0.996`), percentages (`54.2%`, `75 percent`) and
  3+-digit non-year values (`384`, `1,600`, `150,528`) per 1,000 words.
- **Why/1k:** `"why"` per 1,000 words.
- **Hyp/1k:** thought-experiment prompts (`"what if"`, `"suppose"`, `"imagine"`) per 1,000 words.
- **Ded/1k:** explicit logical deductions (`"because"`, `"therefore"`, `"which means"`,
  `"this means"`, `"that means"`) per 1,000 words.
- **Trn/1k:** logical pivots and checks (`"but"`, `"wait"`, `"hold on"`, `"however"`) per 1,000 words.

| Corpus (n) | NumMnt/1k median (range) | Spec/1k median (range) | Why/1k median | Hyp/1k median | Ded/1k median | Trn/1k median |
|---|---:|---:|---:|---:|---:|---:|
| **FloatHeadPhysics** (8) | **10.6** (3.0–24.9) | **0.2** (0.0–5.6) | **3.2** | **1.1** | **6.6** | **10.5** |
| **3Blue1Brown** (8) | **15.5** (7.9–30.3) | **1.6** (0.2–4.1) | **0.8** | **0.8** | **1.0** | **6.2** |
| **Welch Labs** (8) | **18.5** (9.0–32.8) | **4.3** (2.1–11.3) | **0.4** | **0.1** | **0.6** | **4.2** |
| *Welch G: JEPA (37.4 min)* | *11.0* | *2.5* | *0.5* | *0.2* | *0.0* | *5.2* |
| **Demo: `resting-potential`** (`3b1b`) | **33.4** | **0.0** (spelled) | 1.1 | 0.5 | 4.8 | 4.2 |
| **Demo: `memory-hierarchy`** (`welch`) | **54.2** | **9.7** | **0.0** | **0.0** | 1.1 | 7.4 |
| **Demo: `jepa`** (`welch`) | **50.6** | **25.0** | **0.0** | 0.5 | 2.7 | **1.6** |

Per-video detail for FloatHeadPhysics (`research_cache/floatheads/subs/`):

| Video | Words | NumMnt/1k | Spec/1k | Why/1k | Hyp/1k | Ded/1k | Trn/1k |
|---|---:|---:|---:|---:|---:|---:|---:|
| S1 Magnetism (`sDlZ-aY9GN4`) | 3,305 | 3.0 | 0.0 | 3.6 | 1.2 | 8.5 | 8.8 |
| S2 Speed of light (`Vitf8YaVXhc`) | 3,189 | 13.2 | 5.6 | 5.3 | 1.6 | 9.7 | 11.2 |
| S3 Schrödinger's cat (`zkHFXZvRNns`) | 4,231 | 8.0 | 0.2 | 2.1 | 0.9 | 5.4 | 10.6 |
| S4 Heavy elements (`07YCJ6g4fBM`) | 3,905 | 3.8 | 0.3 | 2.0 | 0.3 | 7.4 | 9.5 |
| S5 Tensors (`k2FP-T6S1x0`) | 3,868 | 18.4 | 0.0 | 3.9 | 0.5 | 4.7 | 12.7 |
| S6 Fourier (`Nmp6ffuQSdI`) | 5,717 | 6.8 | 0.0 | 2.8 | 2.1 | 4.9 | 11.9 |
| Orbitals (`M--6_0F62pQ`) | 6,517 | 20.3 | 0.6 | 5.4 | 0.6 | 5.7 | 7.7 |
| Exclusion / walls (`S5TCzvfJntA`) | 6,828 | 24.9 | 5.0 | 2.5 | 1.6 | 9.6 | 10.4 |

### 1.2 Three headline findings `[measured]`

1. **Every single one of our three demos uses more numbers than the channel it imitates.**
   - Across all 24 reference videos, not one exceeds 32.8 numeric mentions per 1,000 words.
   - `resting-potential` (`3b1b`, 33.4/1k) exceeds all 8 3Blue1Brown videos (median 15.5, max 30.3).
   - `memory-hierarchy` (`welch`, 54.2/1k) is 2.9× the Welch median.
   - `jepa` (`welch`, 50.6/1k, 25.0 exact specs/1k) uses **4.6× more numbers** and **10.0× more
     exact specs** than Stephen Welch's own 37-minute JEPA video (11.0/1k, 2.5 specs/1k — only
     8 exact-spec sentences in the whole 37 minutes!). Single beats in our `jepa` demo pack
     13 numbers in 93 words (`scale_ijepa`) and 18 numbers in 132 words (`scale_vjepa`).
2. **FloatHeadPhysics is an outlier on explicit logical reasoning.**
   - Compared with 3b1b and Welch, his narration carries **4–8× more `"why"`s** (3.2 vs 0.8 and
     0.4/1k), **6–11× more explicit deductions** (`because / therefore / which means`: 6.6 vs
     1.0 and 0.6/1k), and **1.7–2.5× more logical turns** (10.5 vs 6.2 and 4.2/1k), while
     using the **lowest** numeric density (median 10.6/1k, exact specs 0.2/1k).
3. **Our current skill docs actively caused the spec-dump bias `[verified: repo files]`.**
   - `SKILL.md` step 1 opened with `"extract exact notation, values"` and `"exact numbers"`.
   - `references/research.md` framed `SOURCE_NOTES.md` around `"exact equations, architectures,
     dimensions, and published numbers"` with no distinction between fact-check ledger and
     spoken script, and no thinking-process or intuitive-derivation spine.
   - `styles/welch/STYLE.md` said `"with real numbers"`, `"Every symbol is tied to a real
     dimension"` and `"Exact numbers are part of the voice"`, without noting that Welch himself
     uses them sparingly (~18/1k, ~2.5–5 exact specs/1k).
   - `styles/*/style.yaml` set `questions_per_min` ceilings of `0.9` (3b1b) and `0.7` (Welch),
     which warned against active guiding questions during derivations, while `explain/narrative.py`
     had zero checks for numeric density or per-beat number dumps (so `memory-hierarchy` at
     54.2/1k and `resting-potential` at 33.4/1k both passed lint with 0 warnings).
   - Even in `resting-potential` (`3b1b`), Nernst (`c1_nernst`) and GHK (`c2_ghk`) were handed
     down by authority (`"The equation for it is named after Walther Nernst, and it tells you..."`)
     rather than derived intuitively or explicitly scoped as qualitative.

---

## 2. How FloatHeadPhysics derives ideas intuitively (8 transferable mechanisms)

Every mechanism below is independent of his dead-scientist dialogue device and works directly
in single-narrator voice (consistent with decision 15).

### 1. Reject formula-as-explanation and label-as-explanation up front
He explicitly calls out why reciting an equation or naming a rule does not answer `"why"`:
- **S2 (00:10–00:31):** Shows `KE = ½mv²/√(1−v²/c²) → ∞` and `"mass goes to infinity"`, then
  dismisses both: *"But my problem is that that's not an explanation. I don't have an intuition
  behind why that is true… What's physically happening?"* `[verified: Vitf8YaVXhc]`
- **Exclusion (01:17–01:27):** *"Electrons are fermions and two fermions cannot occupy the same
  quantum state — Pauli's exclusion principle. But that's not an explanation. We just gave it a
  name."* `[verified: S5TCzvfJntA]`
- **S5 (00:25–00:42):** Shows textbook definitions of tensors (`"multilinear relationship"`,
  `"multidimensional arrays"`), rejects them as opaque, and promises to rebuild the idea from
  scratch before defining it. `[verified: k2FP-T6S1x0]`
- **S3 (03:33):** Sets aside buzzwords (`"probability wave collapses"`) as *"superficial
  half-knowledge"* so the logic can start from raw observation. `[verified: zkHFXZvRNns]`

### 2. Backward design from the thinking process, not the spec sheet
In his Khan Academy process video (`kZeLl-tj55E` 00:32–08:26), he designs outcomes in four
buckets before touching storyline or visuals `[verified: kZeLl-tj55E]`:
1. **Thinking-process summary:** *"I try to summarize the thinking process, not just the facts…
   help beginners understand the thinking process that experts have."*
2. **Misconceptions:** written down first so the story *starts* from the wrong mental model and
   dismantles it rather than merely announcing the right answer.
3. **Prerequisites:** explicitly bounded, with a brief recap when needed so the video doesn't
   bloat.
4. **Minimal new-jargon list:** kept as short as possible; every new term is treated as heavy
   cognitive load, introduced slowly and only after the idea exists.

### 3. Start from one bedrock premise and force every step from it
Each video picks the smallest undeniable truth and makes the rest feel logically unavoidable:
- **S2 (Speed of light):** *The speed of light is constant in all frames* → diagonal photon path
  → photon clock slows → EM force carriers between atoms take diagonal paths → real clocks &
  muons slow → Pythagoras gives `γ` → accelerating ship slows by `γ` → infinite time or infinite
  fuel. `[verified: Vitf8YaVXhc]`
- **S6 (Fourier, 00:53):** *Heat flows from hot to cold* → hot block between colder/hotter blocks
  → temperature change tracks change in slope (curvature = second derivative = heat equation!) →
  what curve has curvature ∝ height? Sine! → linear sum of sines → periodic frequencies →
  integrate to isolate `h₀` → multiply by `sin` to isolate `h₁` → add `cos` for phase → `T → ∞`
  yields the Fourier transform. `[verified: Nmp6ffuQSdI]`
- **S5 (Tensors, 01:24):** *Ohm's law (`J ∝ E`)* → how many numbers describe conductivity? →
  1 fails in anisotropic crystal → 2 works only on lucky axes → rotate axes → 4 in 2D, 9 in 3D,
  `n²` in `n`D → scalars `n⁰`, vectors `n¹`, rank-2 tensors `n²`. `[verified: k2FP-T6S1x0]`
- **Exclusion (02:20):** *Identical particles cannot be told apart even in principle* → swap once
  rotates total amplitude by `δ` → swap twice returns to start → `δ ∈ {0°, 180°}` → symmetric
  particles bunch (bosons, lasers) vs antisymmetric particles cancel to 0 in the same state
  (fermions, Pauli exclusion, chemistry, solid walls). `[verified: S5TCzvfJntA]`

### 4. Simplify to an easier version first, then lift restrictions one by one
He names this problem-solving heuristic aloud whenever a derivation gets hard:
- **S6 (06:36, 15:03):** *"If you can't solve a hard problem, see if you can tackle an easier
  version."* Solves a single sine wave → sum of two sines → periodic signal of period `T` →
  non-periodic signal as `T → ∞`. `[verified: Nmp6ffuQSdI]`
- **Orbitals (02:58, 16:30):** 1D standing wave on a string (point nodes) → 2D line nodes → 3D
  spherical radial nodes and symmetric planar cuts (`s` and `p` orbitals). `[verified: M--6_0F62pQ]`
- **Exclusion (02:20, 24:20):** Starts with two separated detectors (distinct paths) to derive
  `δ ∈ {0°, 180°}`, *then* slides the two detectors onto the exact same spot so both paths share
  identical amplitudes (`0.4 ± 0.4`). `[verified: S5TCzvfJntA]`

### 5. Staged failure ladders and stating the constraint *before* the mathematical move
Rather than knocking down one weak strawman and handing down the textbook answer, he tests a
**plausible repair**, exposes the hidden assumption where it breaks, and then **states in plain
words the exact logical job the missing move must do** before revealing the move:
- **S5 (Tensors, 02:28–10:48):**
  - Attempt 1: 1 number → fails on graphite crystal.
  - Attempt 2 (plausible repair): 2 numbers `σ_x, σ_y` → tested on an angled field `E` and *seems
    to work!*
  - Deeper wall: *"You just got lucky"* — our axes happened to align with the crystal's special
    directions. Rotate the axes → `E_x` alone produces *both* `J_x` and `J_y`, forcing 4 numbers.
    `[verified: k2FP-T6S1x0]`
- **S6 (Fourier, 16:20–20:19) — textbook example of constraint-before-move:**
  - Attempt 1: differentiate infinitely for infinite equations → absurd.
  - Pivot: integrate instead → isolates `h₀` cleanly, but `h₁`'s sine cancels to 0.
  - Attempt 2 (plausible repair): square the whole equation so `h₁`'s area becomes positive →
    fails because squaring makes *every* term positive and breaks linearity.
  - **Stated constraint (19:45):** *"So what we need is some operation that only squares this
    one, doesn't square the rest, and is linear."*
  - Inevitable move (20:07): *"Multiply the whole equation by `sin(ω₁t)`!"* Because the
    constraint was stated first, the mathematical trick feels deduced, not pulled from a hat.
    `[verified: Nmp6ffuQSdI]`
- **S3 (Schrödinger's cat, 04:36–08:50):** Exhausts all 6 classical options by concrete test
  (close slit 2, close slit 1, add both, move screen next to slits, close both, insert barrier)
  before naming `"quantum superposition"`. `[verified: zkHFXZvRNns]`

### 6. Active `"why / why not / what if"` stress-tests against his own explanation
In his Q&A (`2VvG2p2nFLQ` 04:42–05:55), he calls chasing `"why / why not / what if"` tangents
the core of building intuition (e.g., *"if E = mc² uses the Doppler effect, why doesn't sound
produce E = mc²?"*). In his videos, these objections drive the logical chain:
- **S2:** *"Photon clocks slow down, but what about real physical clocks?"* (02:16); *"Clocks
  slow down, but does time itself slow down?"* (04:43, 07:13); *"Wait — what if I double my fuel
  output to cancel time dilation?"* (14:16 — this single `"what if"` derives infinite energy!).
  `[verified: Vitf8YaVXhc]`
- **S1:** *"Length contraction at crawling electron speeds is tiny — how can it create a real
  force?"* (08:31); *"What about a single moving charge?"* (09:45); *"Wait — what about charge
  conservation?"* (16:46). `[verified: sDlZ-aY9GN4]`
- **Orbitals:** *"Why slice the sphere at the center, not off-center?"* (17:12); *"Why not slice
  diagonally?"* (19:00). `[verified: M--6_0F62pQ]`

### 7. Qualitative mechanism first; equations as packaged sentences — or honest hand-waving
- **Long qualitative runway before symbols:** In S2, **8 full minutes** of physical geometry
  precede the first derived equation (`t' = t / √(1 − v²/c²)`); in S6, **26 minutes** of
  geometric reasoning precede the formal Fourier series; in S5, **11 minutes** precede the
  matrix form and **20 minutes** precede the formal definition of a tensor. `[verified: transcripts]`
- **Equations as packaged sentences (`2VvG2p2nFLQ` 06:05):** *"Equations at the end of the day
  are basically trying to communicate in a more packaged way."* Every step of `ct`, `ct'`, `vt'`
  → Pythagoras (S2 08:15–09:20) and `h₀·T = Area` → `h₁·(T/2) = Area` → `∫` (S6 18:20–26:56)
  packages geometry already on screen.
- **Play with the equation after deriving it (`2VvG2p2nFLQ` 06:47–07:45):** Don't leave symbols
  inert. Plug in 2–4 revealing values — low (`50% c → γ = 1.2`, *"that's why Newtonian physics
  works"*), midpoint (`87% c → γ = 2`, clean doubling), extreme (`99.9% c → γ = 22`) — or double
  a variable (`a = v²/R`) and ask *physically* why the output scales that way. `[verified:
  Vitf8YaVXhc 10:42; 2VvG2p2nFLQ 07:07]`
- **Hand-wave honesty:** When exact math lies outside the video's scope, he says so openly
  (*"the exact shape requires mathematical rigor, qualitatively the pattern remains"*, Orbitals
  07:00, 14:55; *"I don't have the mental capacity to work out all components, but the logic is
  identical"*, S5 16:23, 20:03; *"I may have glossed over some details, but the central idea is
  the same"*, S6 30:10). He never disguises an asserted textbook equation as a derivation.

### 8. Every number earns its seat (logic levers, never spec dumps)
- **Effortless derivation numbers:** In Exclusion, he picks `90% × 40% = 36%` and `10% × 10% =
  1%` specifically because `√0.36 = 0.6` and `√0.01 = 0.1`, and later `16%` each so `√0.16 = 0.4`
  → `(0.4 + 0.4)² = 64%` vs `(0.4 − 0.4)² = 0%` `[verified: S5TCzvfJntA 06:11, 14:59, 26:12]`.
  In S2, acceleration is `1,000 (km/s)/s` so halving it at `γ = 2` is instant mental math
  `[verified: Vitf8YaVXhc 11:45]`.
- **Exact physical numbers only when they prove a logical contradiction or payoff:** In S4
  (03:31–04:13), he introduces `k_B T ≈ 10–20 MeV` at hundreds of billions of Kelvin for one
  sharp logical job — `10–20 MeV` is the nuclear binding energy, proving supernova photons rip
  heavy nuclei apart instead of fusing them `[verified: 07YCJ6g4fBM]`. Likewise, Stephen Welch's
  own 37-minute JEPA video uses only 8 exact-spec sentences (e.g., `1920 × 1080 × 3 × 256` to
  prove why pixel distributions explode, and 3 historical ImageNet anchors), leaving ablation
  tables out of the voiceover `[measured: kYkIdXwW2AE]`.

---

## 3. What this changes in `manim-explain`

These changes go into the **core skill** (applying to every style) plus style-specific tuning
for both `3b1b` and `welch`, preserving decisions 8 and 15 (no narrated dialogue with characters;
two shipped visual styles).

1. **Core craft laws (`references/craft-laws.md`) and `SKILL.md`:**
   - Elevate logic-first intuitive derivation and number discipline to explicit hard/core laws:
     reject formula/label-as-explanation; test plausible repairs and `"why / why not / what if"`
     objections; simplify before generalizing; state the constraint before the move; derive
     equations as packaged logic and play with 2–3 revealing cases (or admit the qualitative
     boundary); make every spoken number earn its seat; ration new jargon.
2. **Research stage (`references/research.md`):**
   - Reframe `SOURCE_NOTES.md` around backward outcome design (thinking-process summary, bedrock
     premise, intuitive derivation steps + honesty boundaries, plausible repairs / objections)
     *before* equations and measurements.
   - Explicitly split **spoken numbers** (few, purposeful) from **reference-only specs** (fact-check
     ledger — `"know 10× more than you say"`).
3. **Scripting & spoken math (`references/narrative.md`, `references/spoken-math.md`, `assets/script_template.yaml`):**
   - Document the 7 intuitive-derivation moves and the 4-beat equation cycle (qualitative →
     derive why the operation is forced → build & speak by meaning → play with revealing cases).
   - Add optional `bedrock_premise` and `reasoning_spine` fields to `viewer_contract` in the
     template and guide (backward-compatible with existing scripts).
4. **Style packs (`styles/3b1b/`, `styles/welch/`):**
   - Clarify in `welch/STYLE.md` that real numbers are precision instruments for contradictions
     and payoffs (~11–20/1k in Welch's own videos), never spec-sheet dumps, and that architectural
     choices are derived from the failure constraints before quoting losses or benchmarks.
   - Widen `speaker.questions_per_min` ceilings (`3b1b`: `1.8`, `welch`: `1.5`) so guiding
     `"why / what if"` derivation questions aren't flagged as speaker violations.
5. **Mechanical lint guardrails (`explain/narrative.py` + `style.yaml` rules):**
   - Add measured warnings calibrated to all 24 reference videos (0 false positives across all
     8 FHP, 8 3b1b, and 8 Welch videos; catches all 3 overloaded demos):
     - `number_density`: spoken numeric mentions per 1,000 words (`3b1b` ≤ 31, `welch` ≤ 35),
       counting digits, number words and fractions while ignoring calendar years, bare `"one"`,
       model identifiers (`GPT-2`) and log bases (`base-two`).
     - `spec_overload`: exact decimals / percentages / 3+-digit specs per 1,000 words (`welch` ≤ 12).
     - `number_dump`: single beat cramming ≥ 7 (`3b1b`) or ≥ 8 (`welch`) numeric mentions at
       ≥ 8 per 100 words.
   - Report `numbers_per_1k` and `exact_specs_per_1k` in every lint run's profile output.

---

## 4. Subagent evaluation and iteration (`grok-4.7-xhigh`)

To verify that the updated skill actually changes generated scripts (not just docs), we ran
blind end-to-end research → script → lint tests using fresh `grok-4.7-xhigh` subagents across
both styles on math- and spec-heavy topics, without hinting at internal rules in the prompts:

| Round | Topic (`style`) | Nums/1k | Specs/1k | Q/min | Lint | What we observed and tightened |
|---|---|---:|---:|---:|---|---|
| Baseline | `jepa` (`welch`) | 50.6 | 25.0 | 0.40 | — | Spec dump (10× Welch's own JEPA); 0 `why`/1k |
| Baseline | `memory-hierarchy` (`welch`) | 55.4 | 9.7 | 0.52 | — | Chained byte arithmetic; 0 `why`/1k |
| Baseline | `resting-potential` (`3b1b`) | 33.4 | 0.0 | 0.21 | — | Nernst/GHK handed down by authority; 2 number dumps |
| Round 1 | `flash-attention` (`welch`) | 23.5 | 0.0 | 0.34 | 0 err / 0 warn | Big jump in logic & `SOURCE_NOTES` split; still read one update equation aloud in prose (`u2_formal`), chained byte arithmetic in `u2_wall`, and had declarative test cases (`0.34` q/min). Also exposed `GPT-2` counted as a number and `"you might expect"` clashing with Welch's `you <= 4/1k`. |
| Round 1 | `shannon-entropy` (`3b1b`) | 31.7\* | 0.0 | 0.35 | 0 err / 0 warn | Strong failure ladder (`N`, `1/p`, `1-p` → `-log₂ p`), but `u3_sum` double-verified fraction arithmetic aloud — slipped past Round 1 lint because `"a half"` / `"a quarter"` weren't counted yet. Also flagged `"When I say..."` falsely hitting `narrated_dialogue` and missing contractions (`you've`, `i'll`). |
| Round 2 | `lora` (`welch`) | **11.9** | **0.0** | **0.75** | 0 err / 0 warn | Zero spoken-algebra prose; `4×4` corner + 5 explicit constraints before `BA`; staged failure ladder (full copy → holes → sequential bottleneck → merged `W + BA`); live `"What if?"` checks; 35 MB vs 350 GB (10,000×) as one clean payoff. |
| Round 2 | `snells-law` (`3b1b`) | **4.0** | **0.0** | **0.83** | 0 err / 0 warn | Equal-speeds easier case → slow-glass extreme → plain-English zero-slide constraint before `sin θ / v` → vertical-leg repair refuted → live `"What if?"` cases + honest boundary on total internal reflection → Unit 3 derives wavefront pivot & stationary-phase bundle without knowing the target. |

\* Re-measured with the Round 2 fraction-aware `NUMBER_MENTION` counter (Round 1 had reported `28.0` before standalone fractions were added; with the fix, `shannon-entropy` flags both `number_density` at `31.7` and `number_dump` on `u3_sum` at `7/69w`, while all 24 reference videos remain at 0 false positives).

Round 1's friction directly produced five concrete Round 2 fixes:
1. **No spoken algebra / no double-verified arithmetic:** added explicit law ("voice carries the
   concept, screen carries the algebraic bookkeeping") to `SKILL.md`, `craft-laws.md`,
   `narrative.md` and `spoken-math.md`.
2. **Live `"what if?"` case-checks:** pushed test consolidations from flat lists into active
   reasoning (doubling `questions_per_min` from ~0.35 to ~0.75–0.83 in Round 2).
3. **One sharp contrast over chained intermediate arithmetic** (`craft-laws.md`, `welch/STYLE.md`).
4. **Lint fixes in `explain/narrative.py`:** added fraction words (`a half`, `one and three
   quarters`), excluded `GPT-2` / `base-two`, allowed clarifying `"When I say..."`, and added
   missing pronoun contractions (`you've`, `you'll`, `you'd`, `we'll`, `we'd`, `i'll`, `i'd`).
5. **Style-budget harmony:** clarified `"we might expect..."` for Welch, widened `3b1b`
   `turns_per_10min` floor from `2.5` to `2.0` and `welch` `climax_range` ceiling from `0.80`
   to `0.85` so deep multi-unit derivations have room to breathe.
