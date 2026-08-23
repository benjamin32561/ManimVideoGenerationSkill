# Introduction to Language series — the spine

Thirteen videos, one per week of HUJI 6112
(`StudyMaterial/HUJI/A/6112_Introduction_to_Language/`). **They are one
argument, not thirteen level-summaries.**

Source of truth for content: `Introduction to Language.tex` (Hebrew weekly
spine compiled from Shahar, Zamir 2021, and `raw/`). The video carries the
argument in English; the `.tex` is the exam track. Do not transcribe the
notes. Take the claim, the reason, and the price.

## The question the series answers

Ben is an electrical engineer entering a cognitive-science master's. He already
owns signals, filters, finite-state machines, and statistical learning. His gap
is the one the course is built to close: *how does a child build an infinite
system from finite, noisy input — and what does each level of language
(sound, form, sentence, meaning) actually buy toward that?*

The semester is not a tour of IPA tables. Every level is a partial answer to
the same inference problem. Chomsky buys creativity with rich innateness;
usage-based linguistics buys rich input with a model that is still not closed.
At the end the question flips: not only “what is in the head” but “what can
you model from input alone.”

## Hard rules for every video in this series

1. **Inherit and hand off.** Each video opens on the exact question the previous
   one closed with, and closes on the question the next one opens with.
2. **Never assume a position that has not been earned yet.** No phonemes before
   video 6. No wug before video 8. No trees before video 10. No Grice before
   video 12. Forward glances are named debts.
3. **Exam distinctions are load-bearing pictures.** Descriptive vs prescriptive,
   competence vs performance, phoneme vs allophone, inflection vs derivation,
   dual-route vs one system, grammatical vs sensible vs prescriptive,
   constituent vs linear order, implicature vs entailment vs presupposition,
   critical vs sensitive. Draw both candidates and refuse the impostor.
4. **The picture is the argument.** A beat that only puts a sentence on a black
   frame is a defect. Prefer two cards and a labelled relation; a continuous
   wave that gets cut; a tree that is not a string; a novel item that takes a
   plural nobody reinforced.
5. **Name the price.** When a view fails, the failure stays as a chip the next
   view is paying to avoid. Series memory is a stack of unpaid bills, not a
   list of linguists.
6. **Audience is an EE.** Reach for a filter, a codebook, a finite table, a
   statistical estimator when one exists. Never explain what a spectrum is.
   Do explain every piece of linguistic vocabulary from nothing (phoneme,
   allophone, morpheme, constituent, implicature). Hebrew exam terms may sit
   as on-screen labels; the voice is English. US spelling (`behavior`).
7. **Cross-reference, do not transcribe.** Quote a result and point at the
   notes. The video is not a spoken table of contents of `raw/`.
8. **Vocabulary module.** `utils/lang.py` (built with video 01) is shared,
   identical in every demo. Semantic colour is a *role*: meaning gold, sound
   teal, performance grey, grammar blue, fault red, debt yellow. Reuse
   `position`, `price`, `relation`, `wave`, `min_pair`, `bracket`, `wug`,
   `level_stack` rather than reinventing them.

## The ladder

| # | slug | week | opens on | closes on |
|---|------|------|----------|-----------|
| 1 | `il-01-descriptive` | א | A child builds an infinite system from finite noisy input. Before innateness: what is even the object of study? | A finite kit that generates infinite output. Two packages share the facts. What must we assume before any child hears a word? |
| 2 | `il-02-competence` | ב | Two packages, same facts. How much grammar must be innate? | The sign is mostly arbitrary, so mapping must be learned. How do you infer an infinite grammar from finite noisy samples? |
| 3 | `il-03-learnability` | ג | Input is finite, noisy, sometimes wrong. Grammar must generate infinities and block infinities. How? | Before asking what is innate: what physical sound does the child actually hear? |
| 4 | `il-04-phonetics-ipa` | ד | Speech is a continuous pressure wave. Phonetics is the physics, not the contrast. How is it produced and written? | The wave is continuous. What is the acoustic signature of a vowel, and how is a consonant a constriction? |
| 5 | `il-05-phonetics-acoustic` | ה | Source plus filter. Formants. Place, manner, voicing. VOT is a continuum. | When does a language treat that continuum as two buttons? |
| 6 | `il-06-phonemes` | ו | Phonology asks which sound differences *matter* in this language. Phone, phoneme, minimal pair. | If phonemes are decisions, what laws decide which allophone appears? |
| 7 | `il-07-categorical` | ז | Rules on natural classes. Categorical perception of VOT. Infants cut a continuum without a lexicon. | What are the smallest pieces that carry meaning, not just contrast? |
| 8 | `il-08-morphology` | ח | A morpheme is the smallest meaningful piece. Inflection vs derivation. The wug takes a plural nobody reinforced. | If a novel item takes a rule, is the mental lexicon one system or two? |
| 9 | `il-09-lexicon` | ט | Dual-route vs one network. U-shaped overregularization. Frequency is the test. | Words combine. What does a speaker know when they know how to build a sentence? |
| 10 | `il-10-syntax` | י | Grammaticality is not sense and not a schoolbook standard. Constituents, not adjacent words. | The string lies. What does hierarchy buy that linear order cannot? |
| 11 | `il-11-hierarchy` | יא | Recursion, head vs adjunct, structural ambiguity. Binding depends on the tree. | Once the tree is built, what is left for word-meaning — and what is left for context? |
| 12 | `il-12-semantics-pragmatics` | יב | Sense vs reference. Speech acts. Grice. Implicature vs entailment vs presupposition. | Back to the infant: what can input actually teach, and what breaks if you wait? |
| 13 | `il-13-acquisition` | יג | Segmentation, gavagai, critical vs sensitive, distributional semantics. | (Series close — walk the unpaid bills: every level was a partial answer to learnability.) |

## Per-video notes

**1 · descriptive.** Linguistics is an empirical science of natural language,
not of logic, not of “correct Hebrew,” not of how one ought to speak. Three
questions: what, why, how. Descriptive vs prescriptive: the same first-person
future *y-* is, for the scolder, a blight, and for the describer a system with
constraints (Ziv 2006: “ken ani yavo” not “ken yavo”). Synchronic vs
diachronic; langue/competence vs parole/performance; language vs dialect (no
linguistic test for high vs low). A generative system: a finite kit that
makes infinite output. Do **not** teach Chomsky vs usage-based yet.

**2 · competence.** Two packages, not two lecturers. Chomsky (from 1957):
formal laws, grammaticality judgments; *Colorless green ideas…* is grammatical
without being sensible. Usage-based: rich input, general learning, communicative
drive; no rich innate syntax. Price of each. Arbitrariness of the sign (kiki /
bouba as a statistical pressure, not a cancellation of the rule). Diversity,
endangerment, Nicaraguan Sign Language as language *creating* in view of
researchers. Close on learnability.

**3 · learnability.** Inference problem, not “smart children.” Production
stages as layers, not dates to memorize. What imitation cannot buy:
segmentation, gavagai, rules including exceptions, pragmatics. Four historical
packages: original-language isolation (empty), behaviorism (dies on creativity),
UG (must say *what* is innate), usage-based (must say *how much* input). No
negative evidence vs Chouinard & Clark reformulations. Absolute vs statistical
universals. Close on: what does the child actually hear?

**4 · phonetics IPA.** Phonetics is physics of sound *before* contrast.
Articulatory / acoustic / auditory. Vocal tract map (place next week sits on
it). IPA: one glyph per segment, an approximation of a continuum. Vowels:
height, backness, rounding; monophthong vs diphthong; syllable = onset + rhyme.
Do not teach formants or VOT yet.

**5 · acoustic phonetics.** Source + filter; formants. Consonants: place,
manner, voicing as independent axes. VOT as milliseconds, not two buttons.
English voiced tends short; voiceless longer — the boundary is language-specific.
Tools: spectrogram vs stroboscopy vs palatography measure *different planes*.
Labov: *r* in New York is still phonetics, not a scolding. Close on: when does
the continuum become two categories?

**6 · phonemes.** Phonology = which differences matter *in this language*.
Phone vs phoneme vs minimal pair. Slash vs bracket. Allophone: free variation
vs complementary distribution. Hindi aspiration *is* contrastive — same
physics, different status. Neutralization is not allophony. Close on rules.

**7 · categorical.** Rules hit natural classes, not arbitrary lists.
Categorical perception: equal physical steps, unequal identification. Eye-tracking
bomb/palm: categories are sharp in labeling, graded in RT. Perceptual narrowing;
Maye, Werker & Gerken bimodal VOT. Chinchillas cut too: auditory vs motor
theories. Close on meaning-bearing pieces.

**8 · morphology.** Morpheme ≠ letter and ≠ phoneme. Free vs bound; stem vs
affix. Inflection (same word, no category change, syntactic) vs derivation
(new word, sometimes category change, lexical). Allomorph vs dummy allomorphy
that is just a phonological rule. Wug test: productivity without reinforcement.
Close on one lexicon or two.

**9 · lexicon.** Dual system: store stems and irregulars; compute regulars.
One system: one network, frequency-sensitive. U-shape (*went* → *goed* →
*went*). Both tell a U; frequency and context decide. Zamir: data lean one
system. Close on building sentences.

**10 · syntax.** Grammatical ≠ sensible ≠ prescriptive. T-model; autonomy of
syntax. Judgments give negative data a corpus never will; cost is subjectivity.
Constituent tests (replace, move, question, coordinate) as converging evidence,
not one sufficient test. Asymmetry: verb+object is a unit; subject+verb is not.
Close on hierarchy.

**11 · hierarchy.** Recursion as the infinity mechanism. Head vs adjunct.
NP/VP/PP rules that contain each other. Structural vs lexical ambiguity.
Pronoun binding depends on c-command, not linear “who came first.” Subject vs
object relative clauses: processing load vs missing rule. Close on meaning
and context.

**12 · semantics and pragmatics.** Sense vs reference (morning star / evening
star). Definition-lists fail (circularity, polysemy). Austin: speech acts
change the world; truth-conditions have no value there. Grice: cooperation
plus four maxims (quantity, quality, relation, manner) — rationality, not
politeness. Implicature (cancellable) vs entailment vs presupposition
(survives negation). Close on the infant again.

**13 · acquisition and computation.** Prenatal rhythm, not a born lexicon.
Segmentation at 7.5 months; statistical learning (Saffran). Gavagai;
under- and over-extension. Critical vs sensitive; Genie is confounded; deaf
of deaf vs deaf of hearing is cleaner; Nicaraguan generations; L2 is sensitive
more than critical. Distributional semantics as a cognitive hypothesis, not
just NLP. Series close: walk the unpaid bills from video 1. Bridge to 6110
(representation) and 6115 (processing in time).

## Visual vocabulary (built into `utils/lang.py`)

Same role palette as the other series so an EE is not taught a second map:

| Role | Colour | Used for |
|------|--------|----------|
| mind | instruction gold | meaning, competence, sense, concepts |
| body | control teal | sound, articulation, input, brain |
| behavior | idle grey | performance, parole, utterances, dialect |
| compute | data blue | grammar, phonemes, rules, trees |
| fault | fault red | wrong analyses, scolding, impostor tests |
| debt | address yellow | named debts and price chips |

Primitives: `position(name)`, `price(text)`, `relation(a, b, label)`,
`wave()` a continuous pressure bar, `min_pair(a, b)` two tokens differing in
one segment, `bracket(label)` a constituent, `wug()` a novel-item card,
`level_stack(n)` the semester’s levels — never stack later levels early.

## What this series is not

- A spoken IPA table or a tour of linguists’ names.
- A recap of Philosophical Foundations. Syntax≠semantics was video 9 of that
  series as Searle; here it is grammaticality without sense, earned from
  *Colorless green ideas*, not from the Chinese room.
- Hebrew narration. The notes are Hebrew; the voice is English.
