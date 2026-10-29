# Narrative architecture for explanatory videos

Use this before writing `script.yaml`. Reproduce the sequence of questions that
lets a viewer build the idea for themselves. Let the drama come from that genuine
investigation.

## Start with the viewer contract

Write these fields before outlining beats:

```yaml
viewer_contract:
  starting_point: "What this audience already understands in ordinary language"
  central_question: "The single causal question the video will resolve"
  initial_intuition: "The reasonable idea the viewer will test"
  anchor_example: "One concrete situation that can carry the whole explanation"
  ending_insight: "What the viewer will be able to explain in their own words"
```

Audience labels such as `graduate` only set the prerequisite ceiling. They do not
make project-specific experiment names, metrics, notation, or acronyms common
knowledge.

## The explanatory arc

This is a reasoning order, not a fixed number of beats.

### 1. Orient

Show the concrete situation before stating the thesis. Establish:

- what the viewer is looking at;
- what outcome someone wants;
- what ordinary intuition predicts;
- what surprising observation creates the problem.

The central question should make sense without technical vocabulary. Give it the
context it needs: “Why does beta collapse?” is opaque until the viewer understands
what is being preserved and sees it disappear.

### 2. Let the intuitive approach work

Demonstrate the simple method in the easiest case. This gives the viewer a model
worth believing and a stable visual anchor. Do not rush to the exception or tell
the viewer that the intuition is naive before they have seen why it is useful.

### 3. Create a productive failure

Change one condition and let the prediction fail visibly. Ask the viewer to notice
the inconsistency. Hold the question long enough to think. The failure creates the
need for the next idea.

### 4. Isolate the missing mechanism

Compare the working and failing cases. Change one feature at a time until the
missing relationship is visible. Describe that relationship in ordinary language
before naming it. Keep returning to the opening anchor so each abstraction has a
picture attached to it.

### 5. Compress into terminology or math

Only after the viewer can describe the mechanism visually:

1. perform the operation on the anchor;
2. name the parts;
3. morph those parts into notation;
4. give the formal name last.

The equation is a compact record of reasoning the viewer has already followed.

### 6. Test the new model

Use the model to predict a second case or repair the original failure. This is the
payoff: the viewer sees that the explanation does work, rather than merely hearing
that it is accepted.

### 7. Mark the boundary

Show one important case the explanation does not solve. A limitation is easiest
to understand when it breaks a specific assumption already seen on screen.

### 8. Return and resolve

Revisit the opening image or question. State what changed in the viewer's model
and leave one portable principle, not a catalog of facts or measurements.

## Causal-spine test

For every neighboring pair of beats, complete one sentence:

- “Because we just learned ___, we can now ask ___.”
- “But ___ contradicts that picture, so we need ___.”
- “Therefore ___ should happen in the next case.”

Put the result in each beat's `bridge:` field while planning. The bridge is not
necessarily narrated verbatim. If no sentence fits, the next beat is probably a
side fact. Move it to source notes or cut it. If several beats can be reordered
without harm, the script is organized by topic rather than by reasoning.

Each beat also records `viewer_knows_after:`. Read those lines in sequence. They
should form a knowledge ladder with no step depending on a term or mechanism that
has not yet been built.

## Concrete anchors

A useful anchor is small enough to hold in working memory and rich enough to show
the whole mechanism. Keep it on screen, or return to it, across multiple beats.

Prefer:

- one waveform that gets mixed, transformed, and recovered;
- one moving edge followed across several frames;
- one number walked through a repeated rule;
- one physical situation whose prediction can be tested.

Avoid changing datasets, model names, diagrams, or metaphors every beat. A second
example belongs near the payoff, where it tests generalization.

## Misconceptions and productive confusion

Do not fabricate a foolish straw man. Use the strongest reasonable intuition a
viewer at the stated starting point would have. Show where it works, then expose
the exact condition under which it fails. The correction should reuse the old
model and add the missing distinction.

Useful sequence:

```text
reasonable intuition → successful easy case → prediction → contradiction
→ missing mechanism → revised model → successful new prediction
```

## Evidence without a results dump

Evidence has one narrative job: decide between the old and revised models.

Prefer a visual relationship:

- rises steadily vs. plateaus;
- sharp vs. smeared;
- stable ordering vs. reversal;
- agreement where the assumption holds vs. failure where it breaks.

Do not narrate exact scores, run codes, sample counts, or rows of a benchmark
table in an ordinary explainer. Put those in `SOURCE_NOTES.txt`. If magnitude is
conceptually necessary, use one rounded comparison and interpret it immediately.
Exact values are reserved for a user-requested audit, benchmark, or report
walkthrough.

## Common failure patterns

| Failure | Why it loses the viewer | Repair |
|---|---|---|
| Technical paradox in the first sentence | The viewer cannot feel surprised by undefined objects | Show the ordinary situation and desired outcome first |
| Hook → definition → results | Gives the answer before creating a need for it | Let an intuitive attempt succeed, then fail |
| New diagram every beat | Forces the viewer to rebuild context repeatedly | Keep one anchor and transform it |
| Named concept before visible behavior | Asks the name to carry the understanding | Show behavior, describe it, then name it |
| Several evidence beats in a row | Becomes a spoken lab report | Keep the one relationship that changes the argument |
| “And next...” transitions | Lists adjacent topics without causality | Use because / but / therefore bridges |
| Caveat pile at the end | Replaces the takeaway with memory load | Demonstrate one boundary that breaks a known assumption |

## Reusable patterns

| Pattern | Reasoning spine |
|---|---|
| Mystery → Investigation → Resolution | observable paradox → reproduce it → isolate cause → explain → predict |
| Wrong → Less Wrong → Right | useful intuition → boundary failure → add missing distinction → retest |
| Build Up → Payoff | simple components → combine → behavior emerges → formalize → use |
| Two Perspectives → Unity | build view A → build view B → map the same object between them |
| Specific → General → Specific | anchor → extract rule → predict a new concrete case |

Most strong explainers combine patterns. Choose one main spine; do not use the
table as a checklist of sections.

## Formula and metric explainers

Preferred sequence:

1. Show the decision or distinction the viewer wants to make.
2. Let the obvious measurement fail on the anchor.
3. Manipulate a tiny visual example to isolate the missing property.
4. Build the arithmetic from those visible operations.
5. Name the metric and morph into its notation.
6. Contrast one nearby quantity that answers a different question.
7. Apply both to the opening case and show the boundary of each.

Never open with the metric's benchmark value or formal definition.

## Source-informed principles

These references illustrate the architecture. Use the reasoning principles while
keeping the video's own voice and surface style.

- [3Blue1Brown: Fourier transform](https://www.3blue1brown.com/lessons/fourier-transforms/)
  builds a frequency-unmixing machine from one sound example, tests it, and only
  then translates the visual machine into the formal transform.
- [3Blue1Brown: Bayes' theorem](https://www.3blue1brown.com/lessons/bayes-theorem/)
  starts with a concrete judgment, exposes the missing base-rate intuition, and
  derives notation after the reasoning is already visible.
- [3Blue1Brown: Essence of calculus](https://www.3blue1brown.com/lessons/essence-of-calculus/)
  frames understanding as something the viewer could plausibly rediscover from a
  carefully chosen special case.
- [Muller et al., “Saying the wrong thing”](https://doi.org/10.1111/j.1365-2729.2007.00248.x)
  found stronger learning gains when multimedia explicitly engaged and corrected
  misconceptions than when it gave a concise exposition.
- [Kurzgesagt's production process](https://kurzgesagt.org/what-we-do?visit=videos)
  treats the script as the video's backbone and iterates repeatedly to turn
  research into a coherent story rather than a sequence of facts.

## Final script read

Before TTS, read only the `say:` fields aloud, without titles, sources, show notes,
or access to the research report. Confirm:

1. The first minute is understandable from the declared starting point.
2. The viewer sees the problem before hearing the answer.
3. Every technical term is preceded by its visible meaning.
4. Each beat follows causally from the previous one.
5. The anchor returns throughout the explanation.
6. Evidence appears as an interpretable relationship, not a number list.
7. The ending resolves the opening question in ordinary language.

If any check fails, revise the script before generating audio.
