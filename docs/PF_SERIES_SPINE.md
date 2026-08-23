# Philosophical Foundations series — the spine

Thirteen videos, one per week of HUJI 6110
(`StudyMaterial/HUJI/A/6110_Philosophical_Foundations/`). **They are one
argument, not thirteen summaries of names.**

Source of truth for content: `Philosophical Foundations.tex` (Hebrew weekly
spine compiled from Zamir 2021, Adelman 2022, and `raw/`). The video carries
the argument in English; the `.tex` is the exam track. Do not transcribe the
notes. Take the claim, the reason, and the price.

## The question the series answers

Ben is an electrical engineer entering a cognitive-science master's. He already
owns causation, closed physical systems, and machines. His gap is the one the
course is built to close: *what is a mind, such that psychology, computation,
and the brain can talk to each other without one swallowing the others?*

The semester is a story of failures. Every approach to the mind–body problem
gets stuck, and the next one pays a different price. Dualism dies on causation.
Behaviorism flees the mind and loses explanation. Identity theory is too tight.
Cognitivism and functionalism bring representations back; Searle says syntax is
not understanding. At the end the question flips: not only “what is a mind”
but “how do you join the sciences of it.”

## Hard rules for every video in this series

1. **Inherit and hand off.** Each video opens on the exact question the previous
   one closed with, and closes on the question the next one opens with. The
   opening beat restates the inherited question in one sentence — assume the
   viewer watched last week, not a minute ago.
2. **Never assume a position that has not been earned yet.** No Turing test
   before video 7. No modules before video 10. No Marr before video 12. If a
   later idea must be gestured at, name it as a debt.
3. **Exam distinctions are load-bearing.** Semantic vs metaphysical, type vs
   token, analytic vs synthetic, identity vs supervenience, Turing vs
   behaviorism, syntax vs semantics, local vs global integration. If the exam
   forces a choice of *relation*, the video must draw that relation and keep
   the impostor on screen long enough to refuse it.
4. **The picture is the argument.** This series is more textual than Computer
   Engineering. That does not license a slide of prose. Every spoken change
   still has a visible one: a relation arrow that appears, breaks, or morphs;
   a position that gains a price chip; a room that fills with a rule book.
   Wallpaper quotations are a defect. A two-box diagram with a labelled
   relation *is* the content.
5. **Name the price.** When a view fails, the failure stays on stage as a
   chip the next view is paying to avoid. The series memory is a stack of
   unpaid bills, not a list of philosophers.
6. **Audience is an EE.** Reach for a machine or a closed causal system when
   one exists — a lookup table, a feedback loop, a closed physics. Never
   explain what a cause is. Do explain every piece of philosophical vocabulary
   from nothing (qualia, disposition, type, token, module). Hebrew exam terms
   may sit as on-screen labels; the voice is English.
7. **Cross-reference, do not transcribe.** Quote a result and point at the
   notes. The video is not a spoken table of contents of `raw/`.
8. **Vocabulary module.** `utils/mind.py` (to be built with the first scene)
   is shared, identical in every demo. Positions are `cpu.block`-shaped cards.
   Semantic colour is a *role*: mind gold, body/teal-physical, behavior grey,
   computation blue, fault red for a broken relation, address-yellow for a
   price or a debt. Reuse `position`, `price`, `relation`, `room`, `level_stack`
   rather than reinventing them, so “pain” in video 5 looks like “pain” in
   video 8.

## The ladder

| # | slug | week | opens on | closes on |
|---|------|------|----------|-----------|
| 1 | `pf-01-mind-body` | א | Pain, a decision, and alcohol in the blood all seem real. In what *relation* do mental and physical states stand? | If they are two kinds of thing, how does a thought move a hand? |
| 2 | `pf-02-dualism` | ב | Two substances, one closed physics. How are they causally connected? | Maybe the mind is not a *thing* at all — maybe the question was the mistake. |
| 3 | `pf-03-logical-behaviorism` | ג | Ryle: looking for the mind next to the body is a category mistake. Then what are mental words *about*? | Lab psychology still trusted first-person reports. What happens if the science throws the inner out? |
| 4 | `pf-04-psychological-behaviorism` | ד | Only behavior is public. Can a science of mind be a science of stimulus and response? | Dispositions and histories still miss what is *inside* the pattern — and some learning has no reinforcement. |
| 5 | `pf-05-identity-theory` | ה | Super-Spartans still hurt. If the mind is not a disposition, is it the brain? | Type identity is too tight: kick a Martian. What stays the same across different hardware? |
| 6 | `pf-06-cognitivism` | ו | Latent maps, wugs, and *goed*. Behaviorism cannot chain this. What is inside? | If cognition is rules on representations, a machine can run those rules. Can it think? |
| 7 | `pf-07-turing-test` | ז | Church–Turing: every algorithm is a table. The imitation game: if you cannot tell, you ascribe thought. Is that enough? | Ascribing thought from behavior is not identifying thought with behavior. What *is* a mental state, such that many machines could share it? |
| 8 | `pf-08-functionalism` | ח | Armstrong: the behaviorist was right that mind tracks behavior, and wrong to *identify* them. Mind is the causal role. What is the role? | A table that is too loose gives China a headache; a table that is too tight withholds a mind for one missing wire. And the role never mentions how it *feels*. |
| 9 | `pf-09-chinese-room` | ט | Syntax in, syntax out, Turing passed, nobody home. Is running the algorithm understanding? | If the inner is processing, how is the processing *organized* — one soup, or parts? |
| 10 | `pf-10-mental-architecture` | י | Perception is neither a reflex nor a little scientist. What is a module, and what is left in the middle? | Cognitive science is many labs, many levels, many tools. What makes that one discipline? |
| 11 | `pf-11-integration` | יא | Bermúdez: phenomenon × level × method. Local links vs a reduction to physics. Which one can we actually have? | For one information-processing system, what would a local join even look like? |
| 12 | `pf-12-marr-levels` | יב | Marr: one thing, three levels — computation, algorithm, implementation. Why can you not read the program off a single neuron? | Entities plus activities, not a pure task-decomposition and not a pile of parts. What is a *mechanism*? |
| 13 | `pf-13-mechanism` | יג | Craver: a mechanism is organized entities and activities that produce a phenomenon. How do you test across levels? | (Series close — walk back down the unpaid bills: every layer was forced by a failure underneath.) |

## Per-video notes

**1 · mind–body.** Two inventories that both refuse to be fiction: pain, belief,
the redness of red; a hand moving, a C-fiber, alcohol in the blood. The
psychophysical problem is not “whether they connect” but *in what relation*:
identity, causation, supervenience, something else. Cartesian dualism as the
classical answer the course will throw away: *res cogitans* / *res extensa*.
First person vs third person; transparency, incorrigibility, authority.
Other minds as the direct tax on first-person access. Chalmers: easy problems
(NCC correlations) vs the hard problem (why any of this *feels*). Picture: two
columns, a blank relation, then “first person” as a lock on the mind column
that third-person arrows cannot enter. Do **not** spend the video on pineal
glands; that is video 2.

**2 · dualism, the causal question.** Interactionism (Descartes, pineal as
meeting point) vs the causal closure of physics. Parallelism
(Leibniz / Malebranche) as causation-shaped non-causation. Weak vs strong
epiphenomenalism. Three pressures: Alexander’s dictum, closure, no
overdetermination. Attack the *argument*, not only the conclusion: describing
lightning without “discharge” does not make two things. Picture: an arrow from
mind to hand that physics already occupies; the arrow either breaks physics,
does no work, or is a second cause of the same event. Close on Ryle’s suspicion
that we have been looking for an extra building.

**3 · logical behaviorism.** Category mistake: the university is not another
building; the mind is not another thing beside the body. Verification: meaning
= public conditions of correct use; Wittgenstein’s beetle. Disposition vs
episode (salt dissolves). Semantic thesis (mental talk *translates* into
behavior talk) vs metaphysical thesis (there is nothing behind). Epistemic
punch: no privileged first person; other minds close because everyone sees the
same patterns. Picture: a campus map with a tourist asking “where is the
university”; then “thirsty” as an if-then arrow, not a tank in the head. Keep
semantic vs metaphysical as two stacked cards the rest of the series will
reuse.

**4 · psychological behaviorism.** Wundt’s lab as dualism-as-method. Watson /
Skinner: psychology is the science of behavior because only behavior is
third-person. Classical vs operant conditioning as *stable change in response
probability*, not a change of inner representation. Skinner’s “little man in
the head”: thirst *is* the search pattern. Exam trap: Watson signs the
semantic thesis clearly and leaves the metaphysical one vague. Picture:
introspection as a private meter that will not agree across labs; then a
Pavlov pairing and a Skinner consequence, both as arrows that never enter a
mind box. Close on the inner that dispositions still miss.

**5 · identity theory.** Putnam’s super-Spartans and the stage faker: a
disposition is not the meaning of the state. Disease is the *cause* of
symptoms, not the symptom bundle. Materialism: reality is material; identity
theory does not deny mind, it *identifies* it. Pain = C-fiber firing: two
descriptions, one thing. Nomological identity, not logical (lightning /
discharge vs bachelor / unmarried). Supervenience vs identity; why identity
is cheaper (Ockham, closure, no overdetermination). Type vs token physicalism;
multiple realizability and the Martian. Smart’s “what it is like to have it”
and Armstrong’s causal role as a bridge to video 8 — name that as a debt, do
not teach functionalism yet. Picture: two labels slamming onto one event;
then a type-identity padlock that will not fit a Martian, falling open into
token identity.

**6 · cognitivism.** Behaviorism breaks from inside. Tolman & Honzik latent
learning: a jump in performance the day food appears. Poverty of stimulus and
the wug test. U-shaped overregularization (*went* → *goed* → *went*) with no
reinforcement of the error. Lashley: “the fat cat sat on the mat and howled”
is not an association chain. Cognitivism: representations plus rewrite rules.
Chomsky: deep structure, generative grammar, transformations. Complex behavior
as mechanical application of rules — hence, in principle, a machine. Picture:
a maze that fills in *without* a reward chip, then a wug that takes a plural
the child never heard; then a phrase structure that is a tree, not a bead
string. Close on the machine that can run the tree.

**7 · Turing test.** Turing machine: tape, head, table. Church–Turing: every
finite procedure is a table. Multiple realizability twice — infinitely many
tables for one function, infinitely many hardwares for one table — *before*
the brain. Imitation game (1950): judge, human, machine, text only (fairness:
do not score the hardware). Turing does **not** identify thought with
behavior; behavior is an *indicator*, the same one we use on other people.
Objections: Jefferson (consciousness) → other minds; Lovelace (no novelty) →
surprise, human determinism, learning machines. Picture: a TM table that
survives a hardware swap; then a wall that hides bodies, with the judge
ascribing “thinks” to whichever stream of text. Keep the two-card distinction
from video 3: ascription vs identity.

**8 · functionalism.** Armstrong: mind is tied to behavior and is not
behavior. Solubility is not “would dissolve”; it is the inner property that
*causes* dissolving. Pain is the occupier of the role between injury and
withdrawal. Role-identity is analytic; occupant-identity is synthetic
(scientific discovery). The role is holistic: belief-that-it-rains yields an
umbrella only given wanting-to-stay-dry. Machine functionalism: same mental
kind = same role in a TM table. Consequences: psychology autonomous from
physics; realization need not be biological; physical realization must be
*isomorphic* to the table. Challenges: Block’s China brain (liberalism);
chauvinism (one missing wire); inverted spectrum (role vs qualia). Picture:
a causal profile as a node with three ports (in, other-states, out); then the
same graph drawn once in neurons and once in a city of telephones.

**9 · Chinese room.** Searle: weak AI (the computer as a tool; a hurricane
simulation is not a hurricane) vs strong AI (the right program *is* a mind).
He attacks the strong claim. The room: a person who knows no Chinese, a rule
book, symbols in, symbols out, Turing passed in Chinese, no understanding
inside. Syntax ≠ semantics. Exam skeleton: (1) the person does not understand;
(2) the system passes Turing; (3) functionalism attributes understanding to
anyone who implements the algorithm; contradiction between (1) and (3). Formal
manipulation is not sufficient (he understands English in the same room) and
not necessary (answering “hamburger” is about meaning, not glyph shape).
“Wrong order”: being a belief *explains* taking the umbrella, not the reverse
— the same pressure video 5 put on behaviorism. Replies: the system
understands; or the argument kills strong AI without killing functionalism as
a research stance. Picture: the room, the book, the wall; first-person dark,
third-person fluent. Do not let the “system reply” erase the person — keep
both boxes.

**10 · mental architecture.** If mind is information processing, how is it
*arranged*? Gall’s question without Gall’s method; neuropsychology as
selective deficit. Fodor: perception is not a reflex and not a little
scientist. Müller–Lyer stays after you know the lines are equal —
cognitively impenetrable, yet “smart” in the poverty-of-stimulus sense.
Peripheral module: domain specific, fast, innate, neural, mandatory,
informationally encapsulated. Central systems: slow, isotropic, for planning.
Sandwich: input modules → center → output modules. The center’s problem: any
input can affect any output, so there is no finite transformation table.
Massive modularity deletes the center; Fodor did not go there. Picture: a
Müller–Lyer that will not yield to a “you know better” chip; then a sandwich
with a sealed left column and an open middle.

**11 · integration.** The course turns from philosophy *in* cognitive science
to philosophy *of* these sciences. Subfields, levels, tools (EEG, behavior,
single cell). Integration problem: what makes this one discipline rather than
a pile of labs? Bermúdez: a 3-D space, phenomenon × organization level ×
method, to be filled with *points and links*. Local integration joins two
points (hippocampus and episodic memory). Global integration wants
theory-reduction down to physics. The course is skeptical of the global: even
in the exact sciences reductions are rare, and token physicalism already
refused a type-reduction of psychology to brain. Picture: a sparse 3-D lattice
with one local edge lit; a reduction arrow down to physics that will not
carry the type.

**12 · Marr’s levels.** A model of *local* integration for one information
processor. Three levels of the *same* thing: (1) computational / the
phenomenon — what is the problem, what are the constraints (vision: what is
where from light on the retina); (2) algorithmic / software — intermediate
representations and the transforms, infinitely many algorithms for one
computation (“37” vs binary); (3) implementational / hardware — brain or chip,
multiple realizability again. Each level constrains the one above. Methodology
is top-down: you cannot read the editor from a voltage on a pin, so you cannot
read the computation from one neuron. Psychology and linguistics are not
waiting for neuroscience — they say what is worth looking for below. This
continues Turing (behavior as indicator of a process) and the autonomy of
psychology from functionalism. Picture: three stacked panes of one object,
not three objects; a pin that will not yield a program.

**13 · mechanism, and the walk back.** Craver: a cognitive capacity as a
mechanism — entities and activities organized in time and space that are
responsible for a phenomenon. A clock is gears *turning*, not a heap of brass
and not a pure task list. Recursive: each activity is itself a mechanism one
level down. Between-level experiments: top-down (perturb the phenomenon, watch
below) and bottom-up (perturb a part, watch above). Relevance: activity φ of
component x is relevant to phenomenon ψ of system S when x is part of S and
you can change ψ through φ and conversely, other things equal. Every such
explanation *is* a local integration. Series close: start from mind–body and
first person; pass through a computational model of mind; end with a tool that
joins computation to brain without swallowing psychology. That is the bridge
to 6164, 6166, and 6115 — there they measure the representation; here we asked
what would count as one. Picture: a clock that is neither a pile nor a
flowchart; then a fifteen-second descent of the unpaid-bill stack from video
1.

## Visual vocabulary (to be built into `utils/mind.py`)

Reuse `demos/_ce_shared`-style roles so an EE who watched the other series is
not taught a second palette:

| Role | Colour | Used for |
|------|--------|----------|
| mind | instruction gold | mental states, first-person, qualia |
| body | control teal | physical states, brain, C-fibers |
| behavior | idle grey | dispositions, public criteria, imitation-game text |
| compute | data blue | representations, TM tables, algorithms |
| fault | fault red | broken causation, category mistakes, unpaid prices |
| debt | address yellow | named debts (“three videos from now”) and price chips |

Primitives: `position(name)` a labelled card; `price(text)` a chip that
survives a section fade; `relation(a, b, label)` an arrow whose label is the
exam word (identity / cause / supervenes / plays-the-role); `room()` the
Chinese-room enclosure; `level_stack(n)` Marr’s three panes; `module_sandwich()`
Fodor’s left-sealed / middle-open layout.

## What this series is not

- A history of philosophy with dates as the plot.
- A spoken glossary. Terms appear when a failure forces them.
- A recap of the Computer Engineering series. Machine analogies are allowed
  because the viewer is an EE; they are not prerequisites, and they must not
  smuggle in caches, kernels, or QoS.
- Hebrew narration. The notes are Hebrew; the voice is English; exam terms
  may be labelled on screen in both.
