# The narrative pattern of great explainers

Written 2026-11-21. It tests one hypothesis against 10 hand-labelled videos (3 by 3Blue1Brown,
3 by Welch Labs, 4 by Veritasium) and 6 of our own scripts, and turns what it finds into a
grammar that a script stage can follow and a lint can check.

**Tags.**
- [measured] comes from my scripts over the labelled timelines (method in §8).
- [verified: source] means I read it in the source named.
- [inferred] is my reading of the evidence.

Timestamps are video time. "%" is a share of **content time**, which leaves out sponsor
reads, inserted interview clips and end cards.

## 1. Verdict

**Ben's hypothesis is right about the repeating unit but misses two things. Several units
chain together under one question that stays open, and each revelation is cashed out before
the next unit starts.**

Ben's words: "a short intro, then digging deeper to understand the problem, then hitting a
wall, and then revelation, going over and over".

| Part of the hypothesis | Holds? | Evidence |
|---|---|---|
| Short intro | Yes | The central question (Q0) arrives at a median of 60 s [measured]. It comes within 90 s in 8 of 10 videos and within 10% of content time in 9 of 10. The two late ones still open on a complete mini-cycle. Welch F's 6.6-min history prologue is itself a full attempt → twist cycle that produces Q0. Veritasium's Gödel video states its thesis in the first sentence. |
| Dig → wall → revelation | Mostly | Every video has 2–9 turns. [measured] Of 64 units: 59% are wall → revelation, 19% overturn a stated intuition with no separate wall sentence ("you might expect X, but"), and 22% are plain builds (question → work → answer). [measured] Walls are short pivots: median segment 16 s, about 8% of runtime. [measured] |
| "Over and over" | Yes, but as a chain, not a loop | 81% of revelations and answers directly cause the next question. [measured] Often the revelation's own cost or consequence becomes the next wall. Welch C: KV caching fixes compute, "but this compute shortcut does come at a cost". Veritasium entropy: "not impossible, just improbable", then "so why don't we observe this?" |
| (missing) One question held open | – | Each video keeps one central question open across the whole runtime. Sub-cycles nest inside it, up to depth 3. The biggest revelation lands at a median of 67% of runtime, with a range of 22–94%. [measured] |
| (missing) Cash-out | – | After a revelation the video names it, formalises it, tests it on a new case, or scales it to real numbers. This consolidation takes 16–26% of content time [measured]. It is the largest role in 3b1b and Veritasium and second to dig in Welch. In Veritasium it is bigger than walls and revelations combined. |
| (missing) The work | – | Setup, dig and attempts take 35–46% of runtime. [measured] The wall only lands because the viewer has watched the attempt run. |

The unit to template is therefore: **question → work → turn → cash-out → causal link to the
next question**. The turn takes one of three forms: a wall broken by a revelation, an
intuition overturned, or an answer built step by step. Units are nested under one macro
question that resolves late, and the video ends with a payoff that returns to the opening.

## 2. Codebook

Defined before labelling. Version 1.1 added one clause after the first two videos (see the R
row). Each segment of narration gets exactly one role, by the job it does in the argument.

| Code | Role | Operational definition | Markers |
|---|---|---|---|
| H | hook | Before the central question. Buys attention with a concrete artifact, a provocation, stakes, or a preview of the payoff. | "This is a 3", a date or name, "shocked the world", payoff number up front |
| Q | question | Poses a problem that the following segments set out to answer. Q0 is the central question. | "how exactly", "why", "can you", "the question is", "Puzzle:" |
| S | setup | Builds the objects, vocabulary or running example needed to engage an open question. No tension. | "imagine", "let's say", "suppose", "first" |
| D | dig | Works step by step through the mechanism or data on the anchor while a question is open. | "if you take", "then", "we can see", "notice", numbers |
| A | attempt | Puts forward a candidate answer, method, hypothesis or reasonable intuition to be tested. | "you might think", "most people would say", "one popular solution", "assume" |
| W | wall | Progress is blocked by a named obstruction. Subtypes: **fail** (an attempt breaks), **contra** (fact vs expectation, or fact vs fact), **cost** (works but too costly or limited), **mystery** (unexplained observation), **gap** (a missing piece). | "but", "the problem", "doesn't", "weird", "impossible", "?" |
| R | revelation | A reframe, trick, hidden fact or answer that removes a preceding W, **or overturns a stated A** (added in v1.1). Must point back to it. | "it turns out", "actually", "the key", "remarkably", "not X, just Y" |
| N | answer | Closes a question by building, with no obstruction or overturned attempt in between. | "so this is how", "and that is" |
| C | consolidate | After R or N. Subtypes: **name**, **formal**, **gen**, **test** (new case), **scale** (real numbers), **recap**. | "called", a formula, "more generally", "in the real model" |
| B | bridge | A short pivot of 5 s or more between units. | "Now back to…", "step back" |
| X | aside | Off the causal spine: anecdote, humour, credits, tangent. | "by the way" |
| P | payoff | The ending: a return to the opening, a principle, open questions, or a tease. | "back to Steve", "it will be fascinating to see" |
| O | off-spine | Sponsor, interview clip, career fair, end card. Excluded from the content clock. | – |

**Units.**
- A **wall unit** is Q? → work → W → R → C*.
- A **refute unit** is Q? → A → R → C*, with no separate W.
- A **build unit** is Q → work → N → C*.

Each unit records its parent unit (nesting), and each R or N records its **link** to what
follows:
- `causal`: the resolution itself raises the next question;
- `return`: it pops back to a parent question;
- `jump`: the next question is not caused by it, usually a planned topic.

The **climax** (★) is the R or N that resolves Q0. If Q0 resolves by accumulation, it is the
R with the strongest turn.

## 3. Per-video timelines

Only the turn rows are listed: H, Q, A, W, R, N, P. The **Flow** line gives every segment
in order, grouped by unit. Depth 0 is the macro arc, and "→" marks the link out of an R or N.

Sample:

| Channel | Videos |
|---|---|
| 3Blue1Brown | V4 Bayes (2019), V2 Neural network (2017), V7 Hairy ball (2026) |
| Welch Labs | C DeepSeek MLA (2025), F Bitter Lesson (2026), E Grokking (2025) |
| Veritasium | Logistic map (2020), Entropy (2023), Math's Fundamental Flaw (2021), The Bayesian Trap (2017) |

#### V4 Bayes theorem (2019) — HZGCoVF3YvM, 14.83 content min

Flow: `c0: H S S Q | c1: S A W D R* C | c2: Q D N C | c3: W R C | c4: S D N C C | c0: B | c5: S Q W R C | c6: W R | c7: A R C | c0: B | c8: W R | c0: P`

| t | % | role | cycle (depth) | what happens |
|---|---|---|---|---|
| 0:00 | 0 | H | c0 (0) | stakes: central to science, ML, a treasure hunt worth $700M |
| 1:25 | 10 | Q | c0 (0) | Q0 librarian or farmer? |
| 2:16 | 15 | A | c1 (1) | the intuitive answer |
| 2:24 | 16 | W:fail | c1 (1) | intuition ignores the 20:1 farmer/librarian ratio |
| 3:51 | 26 | R ★ → causal | c1 (1) | 4/24 = 16.7%: likelihood ratio can't beat the base rate |
| 4:42 | 32 | Q | c2 (1) | generalise: write it as a formula |
| 7:17 | 49 | N → causal | c2 (1) | formula assembled from the 4 and 24 |
| 7:50 | 53 | W:cost | c3 (1) | objection: the formula is more complicated than the sample |
| 7:59 | 54 | R → jump | c3 (1) | value: quantify and systematise belief change |
| 9:25 | 63 | N → jump | c4 (1) | restriction is uneven; new probability = proportion of the wonky shape |
| 11:01 | 74 | Q | c5 (1) | bank teller vs feminist bank teller |
| 11:11 | 75 | W:contra | c5 (1) | conjunction judged likelier than its superset |
| 11:27 | 77 | R → causal | c5 (1) | rephrasing as "100 people" drops the error to 0 |
| 12:09 | 82 | W:cost | c6 (1) | samples miss continuity |
| 12:14 | 83 | R → causal | c6 (1) | areas handle continuity and are sketchable |
| 12:25 | 84 | A | c7 (1) | common view of probability |
| 12:32 | 85 | R → jump | c7 (1) | reframe: probability is the math of proportions |
| 13:27 | 91 | W:contra | c8 (1) | context ambiguous: who is Steve? the prior is open |
| 14:04 | 95 | R → return | c8 (1) | every point of debate is a move of prior or likelihood in the diagram |
| 14:21 | 97 | P | c0 (0) | principle: evidence should update beliefs, not determine them; reprogram intuition |

#### V2 But what is a neural network? (2017) — aircAruvnKk, 16.42 content min

Flow: `c0: H Q S | c1: Q D N C | c2: Q A W R C | c3: Q D | c3a: W R | c3b: W R | c3: N C C X | c4: W R X C | c5: A R* C | c0: P`

| t | % | role | cycle (depth) | what happens |
|---|---|---|---|---|
| 0:00 | 0 | H | c0 (0) | "This is a 3": appreciate how effortlessly brains read sloppy digits |
| 0:49 | 5 | Q | c0 (0) | Q0 challenge: write the program; "trivial to dauntingly difficult" |
| 2:44 | 17 | Q | c1 (1) | what are the neurons, how are they linked? |
| 4:33 | 28 | N → jump | c1 (1) | activations in one layer determine the next |
| 5:37 | 34 | Q | c2 (1) | why expect layers to behave intelligently? |
| 5:49 | 35 | A | c2 (1) | hope: penultimate layer = loops and lines |
| 6:41 | 41 | W:gap | c2 (1) | how would you recognise the subcomponents? |
| 6:52 | 42 | R → jump | c2 (1) | recursive decomposition: pixels → edges → patterns → digits |
| 8:21 | 51 | Q | c3 (1) | design the layer-to-layer mechanism: which knobs? |
| 10:15 | 62 | W:gap | c3a (2) | sum can be any number; activations must be in 0..1 |
| 10:24 | 63 | R → causal | c3a (2) | squish with sigmoid |
| 10:58 | 67 | W:gap | c3b (2) | want a threshold other than 0 |
| 11:11 | 68 | R → causal | c3b (2) | bias |
| 11:22 | 69 | N → causal | c3 (1) | weights = pattern, bias = threshold |
| 13:27 | 82 | W:cost | c4 (1) | the per-neuron formula is cumbersome |
| 13:33 | 82 | R → jump | c4 (1) | matrix-vector form |
| 15:18 | 93 | A | c5 (1) | recall the simplification "neuron holds a number" |
| 15:28 | 94 | R ★ → causal | c5 (1) | neuron = function; the whole network is just a function with 13,000 parameters |
| 16:13 | 99 | P | c0 (0) | tease: how does it learn? next video |

#### V7 Why you can't comb a hairy ball (2026) — BHdbsHFs2P0, 27.75 content min

Flow: `c0: H | c1: Q | c0: Q | c2: S Q A D C W R C | c0: B | c1: Q W A R D | c1a: W R | c1: C | c3: Q A S D | c3a: W R | c3b: W R | c3: N | c4: Q A W R C | c5: Q D N C | c3: X | c6: Q S D N C N | c3: D R* | c0: C P P`

| t | % | role | cycle (depth) | what happens |
|---|---|---|---|---|
| 0:00 | 0 | H | c0 (0) | baby's hair swirl → "hairy ball theorem"; comb around an axis leaves two tufts |
| 0:50 | 3 | Q | c1 (1) | puzzle posed and deferred: can you leave only one tuft? |
| 1:05 | 4 | Q | c0 (0) | Q0 why would anyone care, and why is it true (promise: an elegant proof) |
| 2:35 | 9 | Q | c2 (1) | choose the wing direction continuously for every heading |
| 3:00 | 11 | A | c2 (1) | some simple rule from heading to wing; "how hard could it be?" |
| 5:33 | 20 | W:fail | c2 (1) | the function used in the animation glitches at the poles |
| 6:24 | 23 | R → jump | c2 (1) | no cleverness avoids it: you must use more of the trajectory |
| 9:02 | 33 | Q | c1 (1) | return to the one-tuft puzzle |
| 9:14 | 33 | W:fail | c1 (1) | every field tried has two null points |
| 9:24 | 34 | A | c1 (1) | hypothesis: null points come in pairs, like magnet poles |
| 9:38 | 35 | R → causal | c1 (1) | one null point is possible: stereographic projection |
| 10:41 | 39 | W:cost | c1a (2) | the picture is unreadable near the pole |
| 10:57 | 39 | R → causal | c1a (2) | fluid-flow view: flow lines are circles tangent at the pole |
| 11:55 | 43 | Q | c3 (1) | how do you prove zero is impossible? |
| 12:11 | 44 | A | c3 (1) | assume a nowhere-zero field exists; pause and ponder; credit |
| 14:56 | 54 | W:gap | c3a (2) | can't animate a field that doesn't exist |
| 15:14 | 55 | R → causal | c3a (2) | borrow the one-null field and cut out the pole |
| 15:51 | 57 | W:cost | c3b (2) | the sphere crosses itself; hard to read |
| 15:59 | 58 | R → causal | c3b (2) | vary the radius, widen the hole |
| 16:14 | 59 | N → causal | c3 (1) | two facts: turns inside out; never crosses the origin |
| 16:36 | 60 | Q | c4 (2) | why inside out? what does inside out even mean? |
| 17:02 | 61 | A | c4 (2) | "just look away from the origin" |
| 17:10 | 62 | W:gap | c4 (2) | inside/outside must survive arbitrary deformation |
| 17:30 | 63 | R → causal | c4 (2) | coordinates + right-hand rule define orientation |
| 19:18 | 70 | Q | c5 (2) | why must the deformation reverse orientation? |
| 20:13 | 73 | N → causal | c5 (2) | p → −p reverses orientation |
| 21:44 | 78 | Q | c6 (2) | why can't a sphere turn inside out without crossing the origin? |
| 23:07 | 83 | N → causal | c6 (2) | net flux = 1 L/s, invariant under deformation |
| 24:12 | 87 | N → causal | c6 (2) | only crossing the origin changes net flux |
| 25:09 | 91 | R ★ → return | c3 (1) | flux must end at both −1 and +1: contradiction; you can't comb a hairy ball |
| 27:45 | 93 | P | c0 (0) | rigour exercises; homology |
| 28:09 | 95 | P | c0 (0) | open puzzle: comb even-dimensional spheres, e.g. a 4-D hypersphere |

#### C How DeepSeek Rewrote the Transformer (2025) — 0VLAoVGf_74, 15.56 content min

Flow: `c0: H Q S D | c1: Q D D D N | c2: W R D C | c3: W C B A W A W R* D | c3a: W R | c3: C | c0: P`

| t | % | role | cycle (depth) | what happens |
|---|---|---|---|---|
| 0:04 | 0 | H | c0 (0) | R1 shocked the world; open papers; MLA cuts the KV cache 57×, 6× faster (payoff previewed) |
| 1:08 | 7 | Q | c0 (0) | Q0 how did they squeeze so much out of a standard architecture? |
| 3:11 | 20 | Q | c1 (1) | how does standard attention work? build the equations |
| 6:39 | 42 | N → causal | c1 (1) | attention block output assembled |
| 6:49 | 43 | W:cost | c2 (1) | pattern grows as tokens²; 100k tokens = a Harry Potter book |
| 7:36 | 48 | R → causal | c2 (1) | attention patterns barely change token to token |
| 9:58 | 64 | W:cost | c3 (1) | memory: 2·n·d_h·n_h·l numbers |
| 12:29 | 70 | A | c3 (1) | multi-query attention: share one K/V |
| 12:55 | 72 | W:fail | c3 (1) | less specialisation hurts performance |
| 13:01 | 73 | A | c3 (1) | grouped-query attention, groups of 8 (Llama 3) |
| 13:28 | 76 | W:fail | c3 (1) | still a performance hit |
| 13:37 | 77 | R ★ → causal | c3 (1) | key insight: a learned latent space, shared and cached, projected back up per head |
| 14:44 | 84 | W:cost | c3a (2) | looks like memory traded for compute |
| 14:58 | 86 | R → causal | c3a (2) | absorb W_UK and W_UV into the query and output weights |
| 16:15 | 94 | P | c0 (0) | improvement without performance loss; "it will be fascinating to see…" |

#### F Can humans make AI any better? [Bitter Lesson] (2026) — 2hcsmtkSzIw, 17.6 content min

Flow: `c0: H | c1: D D W R C | c2: A W R* | c0: Q | c3: Q D W | c4: Q D W R | c5: W R D | c4: C | c3: C | c6: A C | c0: P`

| t | % | role | cycle (depth) | what happens |
|---|---|---|---|---|
| 0:00 | 0 | H | c0 (0) | 1971 ARPA goal; Harpy beats it; "would be replaced by something completely different" |
| 3:43 | 21 | W:cost | c1 (1) | scaling Harpy proved difficult |
| 3:53 | 22 | R → causal | c1 (1) | HMMs: same graph, edges learned from data; no expert rules; scales to 20k words |
| 5:18 | 30 | A | c2 (1) | GPT-2: "it seemed like we had learned the bitter lesson" |
| 5:59 | 34 | W:contra | c2 (1) | Sutton on a podcast (clip) |
| 8:24 | 35 | R ★ → causal | c2 (1) | twist: the field read the essay backwards; LLMs are a negative example, like Harpy |
| 8:45 | 37 | Q | c0 (0) | Q0 will LLMs hit a barrier from relying on human knowledge? |
| 8:56 | 38 | Q | c3 (1) | what would an AI that discovers like we can look like? |
| 9:55 | 44 | W:contra | c3 (1) | imitation = human knowledge |
| 10:04 | 45 | Q | c4 (2) | how else to train? AlphaGo as the parallel |
| 13:07 | 55 | W:cost | c4 (2) | Elo 1517: mid-amateur ceiling |
| 13:21 | 56 | R → causal | c4 (2) | self-play: the signal is a real game's outcome, not a human's opinion; policy gradient named |
| 14:25 | 62 | W:fail | c5 (3) | policy network alone not superhuman |
| 14:33 | 63 | R → causal | c5 (3) | value function estimation: predict P(win) |
| 17:49 | 81 | A | c6 (1) | RLHF and RLVR already add RL to LLMs; "remains to be seen" |
| 20:04 | 94 | P | c0 (0) | four open questions; "my take"; "it will be fascinating to see" |

#### E The most complex model we actually understand [grokking] (2025) — D8GOeCFFby4, 33.33 content min

Flow: `c0: H Q S | c1: S D Q C W W Q X S C | c2: D Q N | c3: D W R N | c4: Q N W A W D N | c5: W D R C | c6: Q D R* C | c4: C | c7: Q D R C R | c1: C | c8: W C | c0: P`

| t | % | role | cycle (depth) | what happens |
|---|---|---|---|---|
| 0:00 | 0 | H | c0 (0) | "No one understands modern AI."; a burst of open questions |
| 0:56 | 3 | Q | c0 (0) | Q0 how much must we strip away to truly understand a model? claim: grokking is the most complex model we fully understand |
| 5:52 | 18 | Q | c1 (1) | could you find the structure from patterns alone? |
| 6:52 | 21 | W:fail | c1 (1) | fits training data, fails test: memorised |
| 7:17 | 22 | W:mystery | c1 (1) | the vacation run: sudden generalisation after thousands of steps |
| 7:39 | 23 | Q | c1 (1) | what mechanism memorises, lies dormant, then learns? |
| 12:46 | 38 | Q | c2 (2) | is this structure related to grokking? |
| 12:52 | 39 | N → causal | c2 (2) | the memorising model has no waves or loops |
| 15:01 | 43 | W:cost | c3 (2) | embedding signal is noisy, mixed frequencies |
| 15:31 | 44 | R → causal | c3 (2) | a weighted sum of 8 positions gives a clean cosine; signal spread across locations |
| 16:47 | 48 | N → causal | c3 (2) | the model computes sin and cos of its inputs |
| 16:53 | 49 | Q | c4 (2) | why trigonometry for modular addition? |
| 16:57 | 49 | N → causal | c4 (2) | it's a clock: circles in the activations = clock hands |
| 18:08 | 52 | W:gap | c4 (2) | it still has to add x and y, which it never receives as numbers |
| 18:50 | 54 | A | c4 (2) | attention can compute cos x + cos y |
| 19:03 | 55 | W:fail | c4 (2) | we need the sum of the angles, not of their cosines |
| 20:44 | 60 | N → causal | c4 (2) | strongest component: cos x · cos y |
| 21:02 | 61 | W:contra | c5 (3) | sums are natural, so why a product? does it help? |
| 22:20 | 65 | R → causal | c5 (3) | this neuron fires when x + y = 65: it has learned to add |
| 23:19 | 68 | Q | c6 (3) | how do products become a sum? |
| 24:40 | 72 | R ★ → return | c6 (3) | cos x cos y − sin x sin y = cos(x + y): the network learned the sum-of-angles identity |
| 26:39 | 78 | Q | c7 (2) | does this explain why it groks? |
| 27:11 | 79 | R → causal | c7 (2) | the flat plateau hides the circuit being built |
| 28:49 | 84 | R → causal | c7 (2) | grokking happens at clean-up, when memorised examples are removed |
| 29:56 | 88 | W:cost | c8 (1) | full LLMs remain far from this clarity |
| 32:24 | 95 | P | c0 (0) | the name; ghosts; alien vs human; "it will be fascinating to see" |

#### This equation will change how you see the world (logistic map, 2020) — ovJcsL7vyrk, 17.16 content min

Flow: `c0: H Q | c1: S A W R | c2: D D Q D | c3: W R D | c5: W A R | c6: D W Q S R* C | c7: Q N C C | c8: W C | c0: P`

| t | % | role | cycle (depth) | what happens |
|---|---|---|---|---|
| 0:00 | 0 | H | c0 (0) | "What's the connection between a dripping faucet, the Mandelbrot set, rabbits…? It's this one simple equation." |
| 0:02 | 0 | Q | c0 (0) | Q0 (same sentence) what connects them? |
| 0:38 | 2 | A | c1 (1) | multiply by a growth rate r |
| 0:48 | 3 | W:fail | c1 (1) | grows exponentially forever |
| 0:53 | 4 | R → jump | c1 (1) | add (1 − x); logistic map named; inverted parabola, negative feedback |
| 3:12 | 17 | Q | c2 (1) | how does equilibrium depend on r? |
| 4:10 | 23 | W:mystery | c3 (1) | past r = 3 the graph splits in two. Why? |
| 4:20 | 24 | R → causal | c3 (1) | it oscillates between two values; cycles seen in nature |
| 5:13 | 29 | W:mystery | c5 (1) | chaos: never settles; pseudo-random numbers |
| 5:44 | 32 | A | c5 (1) | "you might expect chaos from here on" |
| 5:47 | 32 | R → causal | c5 (1) | windows of order: period 3 at 3.83; every period exists |
| 6:40 | 37 | W:contra | c6 (1) | plot twist announced: the bifurcation diagram is part of the Mandelbrot set (claim before mechanism) |
| 6:48 | 38 | Q | c6 (1) | how? |
| 8:07 | 46 | R ★ → causal | c6 (1) | plot the iterates on a z-axis: from the side it is the bifurcation diagram |
| 10:18 | 58 | Q | c7 (1) | objection: does it really model populations? |
| 10:29 | 59 | N → jump | c7 (1) | yes, in lab populations; and it spans unrelated sciences |
| 14:20 | 82 | W:mystery | c8 (1) | "even spookier": Feigenbaum's 4.669; "no one knows where this constant comes from" |
| 16:05 | 92 | P | c0 (0) | May's plea to teach it; personal: why we don't teach chaos |

#### The Most Misunderstood Concept in Physics (entropy, 2023) — DxL2HoqLbyA, 25.92 content min

Flow: `c0: H Q | c1: A Q A R W | c2: X S D Q A W D R C | c3: D N C | c4: A R | c5: Q S W R | c6: Q C C | c7: W R | c8: W R* C C C | c9: Q N | c10: W R D C | c11: W R C N C | c12: A R | c0: P`

| t | % | role | cycle (depth) | what happens |
|---|---|---|---|---|
| 0:00 | 0 | H | c0 (0) | "one of the most important, yet least understood concepts"; time's direction; why life exists |
| 0:32 | 2 | Q | c0 (0) | Q0 asked on the street: what does the Earth get from the sun? |
| 0:35 | 2 | A | c1 (1) | vox pops: light, heat, energy |
| 0:57 | 4 | Q | c1 (1) | how much energy is radiated back? |
| 1:08 | 4 | A | c1 (1) | vox pops: less, we use some |
| 1:38 | 6 | R → causal | c1 (1) | exactly the same amount goes back out |
| 1:51 | 7 | W:mystery | c1 (1) | then what are we really getting? "nobody talks about it" |
| 6:18 | 24 | Q | c2 (1) | efficiency? |
| 6:25 | 25 | A | c2 (1) | "you might expect 100%" |
| 6:30 | 25 | W:fail | c2 (1) | heat must be dumped at the cold side |
| 8:15 | 32 | R → causal | c2 (1) | efficiency depends only on temperatures; 100% is impossible |
| 9:34 | 37 | N → causal | c3 (2) | same energy, less usable: concentrated vs spread |
| 11:04 | 43 | A | c4 (1) | entropy as disorder |
| 11:14 | 43 | R → causal | c4 (1) | entropy = the tendency of energy to spread out |
| 11:20 | 44 | Q | c5 (1) | why, if physics is time-symmetric? |
| 12:40 | 49 | W:contra | c5 (1) | snapshot: heat flowed cold → hot; "shouldn't that be impossible?" |
| 12:54 | 50 | R → causal | c5 (1) | not impossible, improbable: count the configurations |
| 13:33 | 52 | Q | c6 (2) | then why don't we see it? |
| 14:50 | 57 | W:contra | c7 (1) | then how does air conditioning cool a house? |
| 15:12 | 59 | R → causal | c7 (1) | by increasing entropy more elsewhere (the power plant) |
| 15:48 | 61 | W:mystery | c8 (1) | then how is there structure? how does life exist? |
| 16:05 | 62 | R ★ → causal | c8 (1) | Earth isn't closed: the Sun gives a stream of low entropy (answers Q0) |
| 19:11 | 74 | Q | c9 (1) | where did the Sun get its low entropy? |
| 19:17 | 74 | N → causal | c9 (1) | back to the Big Bang: the past hypothesis |
| 19:52 | 77 | W:contra | c10 (2) | uniform and mixed: how is that low entropy? |
| 20:09 | 78 | R → causal | c10 (2) | with gravity, spread-out matter is the unlikely state |
| 21:37 | 83 | W:contra | c11 (1) | black-hole entropy implies temperature implies radiation: "nonsense" |
| 22:13 | 86 | R → causal | c11 (1) | Hawking: they do radiate; Bekenstein was right |
| 23:50 | 92 | N → causal | c11 (1) | entropy is the arrow of time |
| 24:53 | 96 | A | c12 (1) | entropy = the dull end |
| 25:00 | 96 | R → end | c12 (1) | tea and milk: complexity lives in the middle |
| 25:34 | 99 | P | c0 (0) | use the low entropy while we can |

#### Math's Fundamental Flaw (2021) — HeQX2HjkcNo, 32.79 content min

Flow: `c0: H | c1: S A R | c0: Q | c2: S Q A D R | c3: S W C R C | c4: S Q A W D R D N X C | c5: A R | c6: Q S D A R | c7: C N* C | c0: P P`

| t | % | role | cycle (depth) | what happens |
|---|---|---|---|---|
| 0:00 | 0 | H | c0 (0) | "There is a hole at the bottom of math": true statements that cannot be proven; twin primes; "we may never know" |
| 2:25 | 7 | A | c1 (1) | you'd think you could predict any pattern's fate |
| 2:38 | 8 | R → causal | c1 (1) | undecidable: no algorithm, running it doesn't settle it |
| 3:14 | 10 | Q | c0 (0) | Q0 why does undecidability show up everywhere (tiles, quantum physics, Magic)? |
| 4:30 | 14 | Q | c2 (1) | more naturals or more reals in [0, 1]? |
| 4:38 | 14 | A | c2 (1) | both infinite, so the same size; assume a complete list |
| 5:59 | 18 | R → causal | c2 (1) | the diagonal number is missing: uncountable > countable |
| 8:42 | 27 | W:contra | c3 (1) | the set of all sets that don't contain themselves |
| 10:11 | 31 | R → causal | c3 (1) | Zermelo restricts "set"; "self-reference refused to die" |
| 13:36 | 41 | Q | c4 (1) | complete? consistent? decidable? |
| 14:16 | 44 | A | c4 (1) | "we must know, we will know" |
| 14:45 | 45 | W:contra | c4 (1) | Gödel: completeness is impossible (announced, not yet shown) |
| 19:33 | 60 | R → causal | c4 (1) | the card that says "this card is unprovable" |
| 20:33 | 63 | N → causal | c4 (1) | true statements without proof |
| 21:36 | 66 | A | c5 (1) | at least prove consistency |
| 21:43 | 66 | R → causal | c5 (1) | a consistent system cannot prove its own consistency |
| 22:13 | 68 | Q | c6 (1) | is maths decidable? |
| 25:05 | 77 | A | c6 (1) | assume a halting oracle H; build H+ |
| 25:53 | 79 | R → causal | c6 (1) | H on H+ is always wrong: H can't exist; maths is undecidable |
| 28:24 | 87 | N ★ → return | c7 (1) | every Turing-complete system has its own halting problem: tiles, quantum systems, Game of Life (answers Q0) |
| 30:01 | 92 | P | c0 (0) | Gödel's and Hilbert's ends; "we must know" vs "sometimes we can't know"; Turing's life |
| 32:08 | 98 | P | c0 (0) | callback to the first line; infinity, a war, the device you watch on |

#### The Bayesian Trap (2017) — R13BD8qKeTg, 9.35 content min

Flow: `c0: H S Q | c1: A W D R* C | c2: X S N C C C | c3: W C | c4: A R D R | c0: P`

| t | % | role | cycle (depth) | what happens |
|---|---|---|---|---|
| 0:00 | 0 | H | c0 (0) | "Picture this": you feel sick, a battery of tests, positive for a rare (0.1%) nasty disease |
| 0:43 | 8 | Q | c0 (0) | Q0 how likely is it that you have it? |
| 0:47 | 8 | A | c1 (1) | "most people would say 99%" |
| 0:54 | 10 | W:fail | c1 (1) | the intuitive answer is wrong |
| 2:05 | 22 | R ★ → causal | c1 (1) | 9%: "incredibly low" |
| 3:57 | 42 | N → causal | c2 (1) | keep updating; never certain, ever more accurate |
| 6:30 | 70 | W:cost | c3 (1) | it can't set priors; 100% vs 0% priors can never be moved |
| 7:11 | 77 | A | c4 (1) | usual lesson: Bayes is counterintuitive |
| 7:20 | 78 | R → causal | c4 (1) | the trap: we internalise too well; repeated failure updates us toward "impossible" |
| 8:23 | 90 | R → end | c4 (1) | our actions change outcomes; certainty becomes self-fulfilling; experiment |
| 8:55 | 95 | P | c0 (0) | "maybe it's time to change"; asks viewers |

## 4. Measurements and cross-channel comparison

### 4.1 Per video [measured]

Turn units are wall plus refute units. A unit whose wall is resolved only inside a child unit
counts in neither column. Welch E's grokking mystery is the one case.

| Video | Content min | Intro to Q0 | Units: wall / refute / build | Turns per 10 min | Median turn-unit length | Median W→R tension | Max depth | Climax at | Links causal / return / jump |
|---|---|---|---|---|---|---|---|---|---|
| 3b1b V2 Neural net | 16.4 | 49 s (5%) | 4 / 1 / 2 | 3.0 | 43 s | 11 s | 2 | 94% | 4 / 0 / 3 |
| 3b1b V4 Bayes | 14.8 | 85 s (10%) | 5 / 1 / 2 | 4.0 | 37 s | 17 s | 1 | 26% | 4 / 1 / 3 |
| 3b1b V7 Hairy ball | 27.8 | 65 s (4%) | 6 / 1 / 2 | 2.5 | 121 s | 19 s | 2 | 91% | 9 / 1 / 1 |
| Welch C DeepSeek | 15.6 | 65 s (7%) | 3 / 0 / 1 | 1.9 | 77 s | 47 s | 2 | 77% | 4 / 0 / 0 |
| Welch E Grokking | 33.3 | 56 s (3%) | 2 / 2 / 2 | 1.2 | 133 s | 54 s | 3 | 72% | 8 / 1 / 0 |
| Welch F Bitter Lesson | 17.6 | 395 s (37%) | 4 / 0 / 0 | 2.3 | 130 s | 12 s | 3 | 35% | 4 / 0 / 0 |
| Ver. Logistic map | 17.2 | 2 s (0%) | 4 / 0 / 1 | 2.3 | 69 s | 22 s | 1 | 46% | 3 / 0 / 2 |
| Ver. Entropy | 25.9 | 32 s (2%) | 7 / 2 / 2 | 3.5 | 57 s | 17 s | 2 | 62% | 11 / 0 / 0 |
| Ver. Gödel | 32.8 | 194 s (10%) | 2 / 4 / 1 | 1.8 | 211 s | 189 s | 1 | 87% | 7 / 1 / 0 |
| Ver. Bayesian Trap | 9.4 | 43 s (8%) | 1 / 1 / 1 | 2.1 | 96 s | 71 s | 1 | 22% | 3 / 0 / 0 |

**Macro holds.** Inside a unit, tension is short: the median W→R gap is 18 s over 38 walls
[measured]. The macro question is held far longer [measured]:
- Q0 → climax: 24 min in V7 and 23 min in Welch E.
- Welch E's grokking mystery (7:17) is not explained until 27:11, about 19 content minutes,
  with five nested sub-units in between.
- Welch C's memory wall (9:58) waits about 2 content minutes, across a sponsor break, for MLA.

### 4.2 Role shares, mean % of content time [measured]

| Channel | H | Q | S | D | A | W | R | N | C | B | X | P |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3b1b | 3.8 | 6.9 | 11.2 | 19.2 | 5.1 | 8.3 | 13.5 | 4.2 | 19.7 | 1.5 | 2.9 | 3.8 |
| Welch | 4.2 | 4.3 | 7.3 | **33.3** | 5.1 | 8.2 | 12.6 | 2.4 | 16.0 | 0.3 | 0.8 | 5.6 |
| Veritasium | 1.7 | 2.9 | 12.8 | 17.8 | 4.0 | 7.8 | 14.6 | 4.2 | **26.2** | 0.0 | 2.4 | 5.6 |

Totals by group [measured]:
- **Work** (S + D + A): 3b1b 35.5%, Welch 45.7%, Veritasium 34.6%.
- **Turn** (W + R + N): 23–27%.
- **Cash-out** (C): 16–26%.

### 4.3 Nesting and chaining

- **One macro arc in all 10** [measured]. The pattern is not a flat loop. Q0 opens at the
  start and every unit is a child or grandchild of it.
- **Depth varies by channel** [measured].
  - Veritasium is mostly flat at depth 1: a "staircase of whys" where each answer raises the
    next question.
  - Welch goes deepest, to depth 3 in E and F: a mechanism is broken down into sub-mechanisms.
  - 3b1b goes to depth 2 with short micro-fixes, e.g. V2's sigmoid and bias fixes inside
    "which knobs?".
- **Chaining** [measured]. Links are 81% causal, 6% return and 13% jump.
  - 6 of the 9 jumps are in 3b1b V2 and V4, mostly after a declared roadmap ("three
    levels… in reverse order"). The others are V7 (1) and the logistic map (2).
  - Welch and Veritasium almost never jump: 16/17 and 24/27 of their links are causal.
- **How a revelation produces the next question** [inferred from the timelines]. Four moves
  recur:
  1. **Cost of the fix**: Welch C, KV caching → memory; MLA → extra compute.
  2. **Scale-up**: "then why don't we observe this?", Veritasium entropy.
  3. **Stops-there**: "so how do you know it stops there?", 3b1b V7.
  4. **Where did that come from?**: "where did the sun get its low entropy?", Veritasium.

### 4.4 Where the climax sits

The climax is at 22–94%, median 67% [measured]. It falls in two clusters [inferred]:
- **Puzzle-first** videos answer Q0 early, then deepen: V4 26% and the Bayesian Trap 22%.
  Both are Bayes videos; the base-rate answer arrives within 4 minutes and the rest
  generalises it, makes it geometric, or turns it on the viewer.
- **Build-to-climax** videos assemble the pieces and click late: V2 94%, V7 91%, Gödel 87%,
  Welch C 77%, Welch E 72%.

Welch F is a third shape. Its biggest turn is the twist that *creates* Q0, at 35%.

### 4.5 Shared vs per-style

**Shared by all three** [measured unless marked]:
- a short hook to Q0;
- one macro question;
- units of work → turn → cash-out;
- a causal chain between units;
- walls as short pivots of about 15 s;
- a cash-out of about 16–26%;
- a payoff that closes the opening;
- a viewer's intuition voiced by the narrator, never by a character in narrated dialogue
  [verified: transcripts]. 3b1b's pi creatures appear on screen, but the narration stays
  one voice.

**Per-style parameters** [measured; framings inferred from the subtypes]:

| Parameter | 3Blue1Brown | Welch Labs | Veritasium |
|---|---|---|---|
| Intro to Q0 | 50–85 s; concrete object, then a challenge | ~60 s on an artifact or history; payoff number previewed (C: "57×" at 0:50); or a whole prologue cycle (F) | 0–45 s; question to the viewer, vox pops, or thesis first |
| Turns per 10 min | 2.5–4.0 | 1.2–2.3 | 1.8–3.5 |
| Median turn-unit length | ~45 s (V7 longer) | ~2 min | ~1–1.5 min (Gödel ~3.5 min) |
| Wall framing (subtype counts) | gap 5, cost 5, fail 3, contra 2: objections and "kicks the problem down the road" | cost 7, fail 5, contra 3, gap 1, mystery 1: engineering attempts on a scoreboard | contra 7, mystery 5, fail 3, cost 1: surprising observations and announced paradoxes |
| Unit mix (wall / refute / build) | 15 / 3 / 6 | 9 / 2 / 3 | 14 / 7 / 5 (refutes overturn "most people would say") |
| Biggest share after work | C 20% | D 33% (long builds of one diagram) | C 26% (tests, experiments, applications) |
| Where data sits | toy numbers inside D (4/24, 13,000 knobs) | exact numbers inside W:cost and C:scale (4 MB/token, 57×) | numbers in C:scale and experiments (91,520 vs 627,264; 1 photon in, 20 out) |
| Who voices the attempt | "you might think", "I imagine", a pi-creature objection on screen | prior methods and the field's belief (MQA, "we had learned the lesson") | street interviews, "most people would say", "you might expect" |
| Device before the mechanism | deferred puzzle (V7 asks at 0:50, returns at 9:02) | payoff number in the hook | claim before mechanism ("The plot twist here is…", then "How does that work?") |
| Max depth | 2 | 3 | 1–2 |
| Jumps allowed | yes, after a declared roadmap | no | rarely |
| Ending | portable principle, open puzzle, next-chapter tease | open questions, a hedged take, "it will be fascinating to see" | callback to the first line, wonder, personal note |

## 5. How walls and revelations are built

### 5.1 In words [measured unless marked]

The language below is pooled per channel over every segment of the role. Veritasium's sentence
columns leave out the Gödel video, whose captions have no punctuation. Veritasium's attempt
segments include vox-pop speech.

| | 3b1b D | 3b1b W | 3b1b R | Welch D | Welch W | Welch R | Ver. D | Ver. W | Ver. R |
|---|---|---|---|---|---|---|---|---|---|
| "but" per 1k words | 4.0 | **9.9** | 3.5 | 3.6 | **9.3** | 5.6 | 3.9 | **13.6** | 9.6 |
| Wall-marker lexicon per 1k | 5.0 | **16.4** | 9.7 | 6.5 | **19.6** | 12.0 | 6.6 | **24.2** | 16.0 |
| Revelation-marker lexicon per 1k | 9.9 | 12.0 | **14.6** | 7.6 | 15.0 | **22.5** | 11.2 | 7.6 | **16.8** |
| Questions, % of sentences | 3.6 | **11.3** | 0.0 | 0.6 | **10.5** | 3.5 | 2.5 | **17.3** | 8.1 |
| Sentences of 8 words or fewer, % | 9.7 | **15.9** | 8.2 | 6.7 | 10.5 | 10.5 | 16.0 | **34.6** | 21.0 |
| Mean sentence length (words) | 23.9 | 22.0 | 23.7 | 20.6 | 20.1 | 21.4 | 17.9 | 12.7 | 17.3 |
| Words per minute | 182 | 193 | 180 | 163 | 162 | 158 | 157 | 144 | 157 |

**Openers** (the first 25 words of each segment, all channels pooled: 48 W, 52 R, 44 D, 27 A):

| Phrase | W | R | D | A |
|---|---|---|---|---|
| "but" | 40% | 40% | 11% | 30% |
| a question (?) within 15 s | **21%** | 2% | 2% | 15% |
| "not enough / still / doesn't" | 12% | 6% | 0% | 7% |
| "actually" | 10% | **17%** | 5% | 7% |
| "well" (answering) | 4% | **13%** | 7% | 15% |
| "remarkable / beautiful / elegant / clever / lovely" | 0% | **10%** | 2% | 4% |
| "you might think / expect", "most people" | 0% | 0% | 0% | **19%** |

What the tables show:

- **A wall is a turn plus a question.** In all three channels it carries 2.5–3.5× the "but"
  rate of dig and 3–17× the question share. Sentences get shorter in 3b1b and much shorter in
  Veritasium; Welch barely changes sentence length. Example: "So far, so good. But now comes
  the weird part." (Veritasium, logistic map 4:07)
- **A revelation answers and evaluates; it doesn't ask.** 3b1b asks no questions in R
  segments. Evaluative words appear almost only at revelations. Revelations reuse "but" to
  overturn ("not impossible, it's just improbable") and lean on "actually" and "well".
  Example: "Heat flowing from cold to hot is not impossible, it's just improbable."
  (Veritasium entropy 12:57)
- **The attempt carries the viewer's voice.** "You might think" and "most people would say"
  occur only in A segments. That is how all three channels voice the viewer without a third
  person [verified: transcripts].
- **Pauses.** I took caption-word onset gaps at each segment start.
  - No pause signature marks walls.
  - Question onsets have long lead-in gaps in every channel: median 1.4–1.7 s, against
    1.1–1.3 s for dig. In 3b1b, walls match them (1.4 s).
  - Welch leaves a gap of at least 1 s before every revelation (12/12, median 1.5 s), against
    83% before dig.
  - 3b1b does not (56%). It speeds up at walls (193 wpm, against 180 at revelations).
  - In 3b1b's audio, silences of 0.6 s or more before a segment are as common at walls (47%)
    as before consolidation (45%).

  So a pause before a revelation is a Welch trait, not a law. [measured; 8–22 onsets per
  role per channel, small n]

### 5.2 In pictures

A background pass measured the 5-s frames in 3b1b V2/V4/V7 and Welch C/E/F. Each window runs
from the segment start for up to 30 s. Same layout means a correlation above 0.6 with the
frame 30 s earlier. [measured]

| Channel | Role | Windows | Cuts per min | Pixel change per 5 s | On-screen words | Frames with ?, !, Puzzle, Why… | Same layout as 30 s earlier |
|---|---|---|---|---|---|---|---|
| 3b1b | W | 15 | **4.5** | **16.3** | 7.4 | **25%** | 13% |
| 3b1b | R | 18 | 2.6 | 13.4 | **8.9** | 12% | 11% |
| 3b1b | D | 11 | 1.3 | 11.3 | 4.6 | 3% | 27% |
| Welch | W | 17 | 1.9 | **20.0** | 19.4 | 0% | 18% |
| Welch | R | 12 | 1.8 | 16.5 | **25.8** | 0% | **50%** |
| Welch | D | 18 | 2.8 | 10.8 | 17.0 | 2% | 11% |

Holds don't separate the roles. 3b1b holds 32% of the time at walls, 43% at revelations and
40% in dig.

**What the screen does at a wall** [verified: frames, 8 walls]:
- It cuts to a new layout or a physical object. Welch C 6:49: a Harry Potter book stands for
  100k tokens.
- It flags the wrong answer. 3b1b V4 11:11: a red box and "85% chose this!".
- It writes the obstruction on screen. V7 9:14: "Hypothesis: Null points come in pairs". V7
  14:56: "Proof by Contradiction (Doesn't actually exist)".
- A character bubble voices the objection. V2 6:38: "Okay, but recognizing loops is just as
  hard!"
- It stretches a chart to expose an anomaly. Welch E 7:17: the x-axis grows from 175 to
  10,000 steps.

**What the screen does at a revelation** [verified: frames, 8 revelations]:
- The anchor diagram stays, or re-runs with one element changed. This is strongest in Welch
  (50% same layout). Welch C 7:36: the Q/K chain re-runs with one new row, "blue".
- A boxed formula or number fills in step by step. V4 3:51: the 210-icon grid stays while
  4/(4+20) ≈ 16.7% fills in.
- A new titled section names the new construction ("Stereographic Projection", "MULTI-HEAD
  LATENT ATTENTION").
- Opposed results appear side by side in opposite colours (V7 25:09: −1.0 red, +1.0 green),
  or a scoreboard gains a row (Welch C's table).
- At the climax, the opening image comes back: the furry ball in V7, the Harpy graph in Welch F.

**The rule of thumb** [inferred]. A wall changes the *frame*: a new layout, a red flag, a
question written up. A revelation changes the *anchor*: the same picture with one thing
added, boxed or recoloured. The voice-side lesson carries over to the picture: the wall
breaks continuity, and the revelation restores it with a difference.

## 6. Comparison with our scripts

Inputs: the 52 `demos/*/script.yaml` on disk (not 47). **None has a `narrative_role` field.**
Only `assets/script_template.yaml` has one. Every beat does have `emotional_beat`
[verified: grep].

**All 52 scripts** [measured from `emotional_beat` and the `say:` text]:
- Length: median 3.8 estimated minutes at 139 wpm, range 2–17.
- Beats: 1,020 in total. 382 are `aha` and 145 are `productive_confusion`, so there are
  2.6 aha beats per confusion beat.
- Only 75 confusion beats are directly followed by an aha.
- Five scripts have no confusion beat at all, and one has 17 aha beats in a row.
- The mn series is median 75% aha, which is 4.8 per minute. The reference videos have
  about 0.12–0.4 turns per minute.
- 23 of 52 scripts open with a series recap.

**Six scripts hand-labelled with the same codebook** (pf-08, pf-09, mn-09, ce-06, ce-12, rsa)
[measured; "real" vs "asserted" is a judgement, so inferred]:

| | pf-08 | pf-09 | mn-09 | ce-06 | ce-12 | rsa | Reference videos |
|---|---|---|---|---|---|---|---|
| Est. length | 2.7 min | 2.4 min | 2.2 min | 10.3 min | 10.8 min | 4.1 min | 9–33 min |
| Intro to Q0 | 0 s | 0 s | 0 s | 36 s | 63 s | 9 s | 2–85 s, after a hook |
| Walls (real) | 4 (2) | 2 (1) | 2 (1) | 6 (4) | 4 (4) | 1 (1) | – |
| Revelations (real) | 2 (0) | 2 (2) | 5 (1) | 5 (4) | 4 (2) | 0 | – |
| `aha` beats that are real revelations | 0/6 | 2/4 | 1/15 | 4/6 | 2/12 | 0/4 | – |
| Work share (S + D + A) | 4% | 24% | 23% | 27% | 11% | 28% | 35–46% |
| Turn share (W + R + N) | 39% | 25% | 39% | 60% | 61% | 21% | 23–27% |
| Climax position | 18% | 24% | 18% | 19% | 14% | 50% | median 67% |
| Links | 3 jump | 1 causal, 1 jump | 4 jump, 1 causal | 5 causal | 5 causal, 2 jump | 2 causal, 1 return | 81% causal |
| Max depth | 1 | 1 | 1 | 3 | 2 | 1 | 1–3 |

How our scripts differ:

1. **All turn, little work.** The reference videos spend 35–46% of their time setting up, digging
   and running attempts before a turn. pf-08 spends 4%, and ce-12 spends 11% while giving 61%
   to turns. A wall the viewer hasn't watched form is only asserted. [measured]
2. **Asserted walls.** The refuted view and its refutation often share one beat (pf-08
   `solubility`, `holistic`; mn-09 `peak`, `pumps`; pf-09 `system_reply`). In mn-09 the
   wall-to-resolution gaps are 5–9 s, against an 18 s reference median and longer macro holds.
   Weak example (pf-09 `system_reply`): "A reply: the system understands, not the person. Do
   not let that erase the person." Strong example (ce-06 `pred_one_bit`): "That exit is a
   mistake, and it flips the bit, so the next entry into the same loop is a mistake too. Two
   mistakes for every trip through the loop, forever." [verified: scripts]
3. **Aha inflation.** `emotional_beat: aha` means "a fact is stated". Of the 47 aha beats in
   the six labelled scripts, 9 (19%) are real revelations. [measured]
4. **Answer before question, and lecture order.**
   - The pf and mn scripts put Q0 in beat 0 with no hook. pf-08 announces the answer while
     asking ("The answer this week is a causal role. What is the role?").
   - The climax sits at 14–24% in 5 of 6 scripts. What follows is mostly a list of related
     points, with 8 of 10 pf/mn links being jumps.
   - pf-08 puts all four of its walls in beats 13–16 of 19 and resolves none. That is
     thesis → elaboration → objections, which is lecture order. [measured]
5. **The ce series already has the pattern.** ce-06 runs attempts with costs (`org_single`,
   `org_multi`) into a revelation (`org_pipe`). That revelation causes the next wall
   (`hazard_define`), with sub-units three levels deep. This is the Welch C shape.
   [measured]
6. **The current skill model is one cycle.** `references/narrative-patterns.md` gives a single
   8-step arc: orient → intuitive approach → productive failure → isolate → compress → test →
   boundary → return. `script_template.yaml` instantiates one wall. The reference videos chain
   2–9 turns under a held Q0. The skill's because/but/therefore `bridge:` test is the right
   seed for the link field. [verified: files]

**Length matters** [inferred from turns per 10 min]. A 3–4 minute video supports about 1–2
real turns plus one build. That is far below the 5–15 aha beats our short scripts carry.

## 7. The pattern as a template

### 7.1 Grammar

```text
Video    := Hook Q0 Arc Payoff
Hook     := H                     # concrete artifact | provocation | stakes | payoff preview;
                                  # may itself be a full Unit whose turn produces Q0 (prologue mode)
Arc      := Unit+                 # every Unit descends from Q0; Q0 stays open until the climax
Unit     := Q? Work Turn Cashout? Link
Work     := (S | D | A | Unit)+   # must contain D or A on the anchor; child Units nest here
Turn     := W R                   # wall unit: R resolves W        (target ~55-65% of units)
          | A R                   # refute unit: R overturns A     (~15-25%)
          | N                     # build unit: plain answer       (~20-25%)
Cashout  := C+                    # name | formal | gen | test | scale | recap
Link     := causal | return | jump  # jump only after a roadmap Bridge
Payoff   := P+                    # callback to Hook/Q0 + principle | open questions | tease
Climax   := exactly one R or N marked climax, resolving Q0 (or the macro wall)
```

### 7.2 Script fields (per beat)

These extend the current `script_template.yaml`. They replace `emotional_beat`, which becomes
derivable.

```yaml
- id: memory_wall
  narrative_role: wall          # hook|question|setup|dig|attempt|wall|revelation|answer|consolidate|bridge|aside|payoff
  role_sub: cost                # wall: fail|contra|cost|mystery|gap ; consolidate: name|formal|gen|test|scale|recap
  unit: u3                      # unit id; u0 = macro arc
  parent: u0
  obstruction: "caching every key and value costs 4 MB per token"   # walls only, ≤ 15 words
  against: kv_cache_fix         # walls: the attempt/revelation beat it blocks
- id: latent_space
  narrative_role: revelation
  unit: u3
  resolves: memory_wall         # revelations: the wall or attempt they remove; answers: the question
  link: causal                  # causal|return|jump (revelations and answers)
  climax: true                  # exactly one in the script
```

### 7.3 Style parameters

The values below are the measured ranges from §4, used as defaults.

```yaml
narrative:
  3b1b:      {intro_max_s: 90, turns_per_10min: [2.5, 4.0], unit_mix: {wall: .60, refute: .15, build: .25},
              tension_s: [6, 40],  work_min: .30, cashout_min: .15, causal_min: .60, max_depth: 2,
              climax_range: [.20, .95], wall_subtypes: [gap, cost, fail, contra], jumps: roadmap_only,
              revelation_questions_max: 0, ending: [principle, open_puzzle, tease]}
  welch:     {intro_max_s: 75, prologue_unit_ok: true, turns_per_10min: [1.2, 2.5], unit_mix: {wall: .65, refute: .15, build: .20},
              tension_s: [10, 120], work_min: .40, cashout_min: .15, causal_min: .85, max_depth: 3,
              climax_range: [.35, .80], wall_subtypes: [cost, fail, contra], jumps: none,
              payoff_number_in_hook: true, ending: [open_questions, take, callback]}
  veritasium: {intro_max_s: 45, turns_per_10min: [1.8, 3.5], unit_mix: {wall: .55, refute: .25, build: .20},
              tension_s: [10, 90], work_min: .30, cashout_min: .20, causal_min: .85, max_depth: 2,
              climax_range: [.20, .90], wall_subtypes: [contra, mystery, fail], claim_before_mechanism_ok: true,
              ending: [callback_first_line, wonder]}
```

### 7.4 Lint rules

Each rule is checkable from the fields above plus the `say:` text and estimated time.

| ID | Check | Level | Grounding |
|---|---|---|---|
| N1 | Narration before the first `question` beat in u0 ≤ `intro_max_s`. That beat contains a question or challenge ("?", or opens with how/why/can/what). | error | §4.1 |
| N2 | A `hook` precedes Q0, unless the style allows a question-first opening (Veritasium). A series recap is not a hook. | warn | §6.4 |
| N3 | Every unit has a Turn (W→R, A→R or N), and at least one setup, dig or attempt beat before it in the same unit. | error | §2, §6.1 |
| N4 | A wall and the revelation that resolves it are in different beats, and the gap is within `tension_s`. A gap longer than `tension_s` is allowed only if the revelation resolves through a child unit. | error / warn | §4.1, §6.2 |
| N5 | A wall has a `role_sub`, an `obstruction`, and an `against` beat that exists earlier. Its `say:` contains a turn marker (but, however, problem, doesn't, can't, not enough) or a question. | error / warn | §5.1 |
| N6 | A revelation's `resolves:` points to an earlier wall or attempt in its unit or an ancestor. An answer resolves a question. An "aha" with nothing to resolve is an answer or a consolidation. | error | §2 |
| N7 | Each revelation or answer is followed by at least one consolidation beat before the next wall. Total consolidation share ≥ `cashout_min`. | warn | §4.2 |
| N8 | Turns per 10 min fall within `turns_per_10min`. Revelation beats make up ≤ 20% of beats and ≤ 20% of time. | error | §4.1, §6.3 |
| N9 | Work share (setup + dig + attempt) ≥ `work_min`. | warn | §4.2, §6.1 |
| N10 | The share of `causal` links ≥ `causal_min`. Each `jump` is preceded by a `bridge` that declared the roadmap. | warn | §4.3 |
| N11 | Exactly one `climax`. It is a revelation or answer that resolves Q0 or the macro wall, sits within `climax_range`, and is followed by consolidation and payoff. | error | §4.4 |
| N12 | The last content beat is a `payoff`. It shares a key noun with the hook or Q0 (callback), or asks open questions where the style allows. | warn | §4.5 |
| N13 | Depth ≤ `max_depth`. | warn | §4.3 |
| N14 | Revelation beats ask ≤ `revelation_questions_max` questions. Wall beats have a mean sentence length ≤ that of revelation beats. Evaluative words (remarkable, beautiful, elegant, clever) appear only in revelation or payoff beats. | warn | §5.1 |
| N15 | The viewer's intuition is voiced in attempt beats by the narrator ("you might think…", "most people would say…"). No narrated dialogue with a character or persona (Ben's no-gimmick rule). | error | §4.5, §5.1 |

### 7.5 How a script stage uses it [inferred]

1. Write the viewer contract as now. Add the **macro question**, the **climax** that resolves
   it, and the **turn budget** for the target length: turns_per_10min × minutes.
2. Plan the units top-down as a chain. For each unit, state its question, the work on the
   anchor, the turn (which wall or attempt, and why it fails), the cash-out, and the link
   that makes the next question unavoidable.
   - Prefer the **cost of the fix** and **stops-there** links (§4.3).
   - Nest a child unit when a step needs its own fix.
3. Write `say:` text last. Walls carry the turn word and usually a question. Revelations carry
   the answer and no question. The attempt carries the viewer's voice.
4. Plan the picture per role (§5.2). At a wall, change the frame or flag the failure. At a
   revelation, keep the anchor and add, box or recolour one thing. At the climax, call back
   the hook image.

## 8. Method and limits

- **Corpus.**
  - 3b1b: creator `en` tracks for text, auto-caption words for timing; V7 has auto captions
    only.
  - Welch: auto captions with model or ASR punctuation (from the Welch study).
  - Veritasium: `en` tracks for text and `en-orig` auto tracks for timing. These were fetched
    by a parallel agent; I used the five that had arrived and labelled four.
  - Not done: the optional Primer and Reducible check, and 3b1b V8 (entropy), which is
    unlabelled.
- **Labelling.**
  - One labeller (me), using codebook v1.1 written before labelling.
  - Segments are anchored to exact word onsets by phrase matching, with a fallback to caption
    lines where auto captions drop words. Anchors were checked by printing every resolved
    timeline.
  - Ambiguities, and how I resolved them:
    - V4: is "the heart of Bayes" (4:10) the revelation, or the 16.7% result (3:51)?
    - The Bayesian Trap: its title twist (7:20) is a bigger turn than the Q0 answer (2:05).
      The climax rule picks the Q0 answer.
    - Veritasium's announced twists are coded as walls, with the mechanism as the revelation.
    - Welch F's twist is coded as a revelation that creates Q0.
- **Tools** (scratch, not in the repo):
  - `research_cache/pattern/scripts/`:
    - `tl.py`: resolve timelines and compute metrics;
    - `analyse.py`, `markers.py`, `onsets.py`, `tables.py`.
  - Timelines are in `pattern/timelines/*.tsv`.
  - Frame stats are in `pattern/frames/`, and the six labelled scripts in `pattern/ben/`.
- **Limits.**
  - n = 10 videos and one labeller, with no inter-rater check.
  - The marker lexicons are coarse regexes.
  - Pause numbers come from caption onsets, not audio, except where noted for 3b1b.
  - Frames are 5 s apart, so fast changes are missed.
  - Veritasium's live-action footage was not frame-checked.
  - The "real vs asserted" judgements on our scripts are inferred.

## 9. Sources

Videos (all youtube.com):

| Channel | Video | Link |
|---|---|---|
| 3Blue1Brown | V2 But what is a neural network? (2017) | https://www.youtube.com/watch?v=aircAruvnKk |
| 3Blue1Brown | V4 Bayes theorem, the geometry of changing beliefs (2019) | https://www.youtube.com/watch?v=HZGCoVF3YvM |
| 3Blue1Brown | V7 Why you can't comb a hairy ball (2026) | https://www.youtube.com/watch?v=BHdbsHFs2P0 |
| Welch Labs | C How DeepSeek Rewrote the Transformer [MLA] (2025) | https://www.youtube.com/watch?v=0VLAoVGf_74 |
| Welch Labs | E The most complex model we actually understand (2025) | https://www.youtube.com/watch?v=D8GOeCFFby4 |
| Welch Labs | F Can humans make AI any better? (2026) | https://www.youtube.com/watch?v=2hcsmtkSzIw |
| Veritasium | This equation will change how you see the world (2020) | https://www.youtube.com/watch?v=ovJcsL7vyrk |
| Veritasium | The Most Misunderstood Concept in Physics (2023) | https://www.youtube.com/watch?v=DxL2HoqLbyA |
| Veritasium | Math's Fundamental Flaw (2021) | https://www.youtube.com/watch?v=HeQX2HjkcNo |
| Veritasium | The Bayesian Trap (2017) | https://www.youtube.com/watch?v=R13BD8qKeTg |

Repo documents:
- [styles/3blue1brown.md](styles/3blue1brown.md) §3 and §5: templates, hooks, and beat sheets for V4 and V7.
- [styles/welch-labs.md](styles/welch-labs.md) §3 and §5: the structural template, and beat sheets for C and F.
- [synthesis.md](synthesis.md).
- Skill files: `skills/manim-explain/references/narrative-patterns.md`, `skills/manim-explain/assets/script_template.yaml`.
- Our scripts: `demos/*/script.yaml` (52 on disk).
