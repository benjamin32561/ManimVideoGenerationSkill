# From Molecule to Neuron series — the spine

Thirteen videos, one per week of HUJI 6164
(`StudyMaterial/HUJI/A/6164_From_Molecule_to_Neuron/`). **They are one
causal chain, not thirteen organelle tours.**

Source of truth for content: `From Molecule to Neuron.tex` (Hebrew weekly
spine compiled from Habib + Adam, Shavit, Regev, and `raw/`). The video
carries the argument in English; the `.tex` is the exam track. Do not
transcribe the notes. Take the claim, the reason, and the price.

## The question the series answers

Not two glued subjects. One chain: stable information in a molecule must
become a machine that works now, and that machine — a protein in a membrane
— is what turns a cell into an electrical computer.

First half (Naomi Habib): DNA → RNA → protein, and **control is as important
as sequence**. Second half (Yoav Adam): those proteins turn a membrane into a
charged capacitor, a capacitor into a pulse, a pulse into chemical release
that can be strengthened or weakened.

Exam: **mechanism** (why the membrane blocks, why Nernst, why all-or-none
AP, why NMDA is a coincidence detector) — not a name list.

Price of the course: does **not** reach behavior (6166) or “what counts as a
representation” (6110). Name those as *outside this course* at the series
close. Never as “you already know.”

## Hard rules for every video in this series

1. **Independent intro.** Video 01 opens on *this* course’s problem
   (chemistry in water; what barrier can hold an inside). It never opens
   with “you already know / you already own …” from another HUJI course or
   from an EE résumé. Videos 2–13 inherit last week’s close. EE pictures
   (RC, capacitor, filter) appear *inside* a beat when they *are* the
   mechanism this week is teaching (week 8: the membrane *is* an RC
   circuit). They are explained from this course’s objects, not assumed.
2. **Inherit and hand off.** Each video after 01 opens on the exact question
   the previous one closed with, and closes on the question the next one
   opens with.
3. **Never assume a mechanism that has not been earned yet.** No Nernst
   before video 7. No Hodgkin–Huxley before video 9. No NMDA coincidence
   before video 13. Forward glances are named debts.
4. **Exam distinctions are load-bearing pictures.** Bilayer vs watery
   boundary; DNA archive vs RNA working copy; primary vs tertiary when a
   channel opens; Nernst vs Goldman; channel vs pump; analog dendrite vs
   digital axon; uniporter vs ionotropic; AMPA vs NMDA coincidence. Draw
   both candidates and refuse the impostor.
5. **The picture is the argument.** A beat that only puts a sentence on a
   black frame is a defect. Prefer two cards and a labelled relation; a
   bilayer that blocks charge; a voltage trace that escapes toward sodium
   and comes back; a coincidence detector that needs two keys.
6. **Name the price.** When a view fails, the failure stays as a chip the
   next view is paying to avoid. Series memory is a stack of unpaid bills,
   not a list of organelle names.
7. **Audience is an EE in a cognitive-science master’s, starting this
   topic from zero.** Explain every piece of cell/neuron vocabulary from
   nothing (bilayer, Nernst, shunting, coincidence). Never explain what a
   capacitor *is* when week 8 uses one — do explain why *this membrane*
   is one. Hebrew exam terms may sit as on-screen labels; the voice is
   English. US spelling (`behavior`, `fiber`, `analog`).
8. **Cross-reference, do not transcribe.** Quote a result and point at the
   notes. The video is not a spoken table of contents of `raw/`.
9. **Vocabulary module.** `utils/cell.py` (built with video 01) is shared,
   identical in every demo. Semantic colour is a *role*: information gold,
   membrane/ions teal, leak/mixing grey, devices blue, fault red, debt
   yellow. Reuse `position`, `price`, `relation`, `bilayer`, `organelle`,
   `ion`, `channel`, `pump`, `helix`, `spike`, `synapse_cleft`,
   `voltage_trace`, `chain_stack` rather than reinventing them.

## The ladder

| # | slug | week | opens on | closes on |
|---|------|------|----------|-----------|
| 1 | `mn-01-membrane` | א | Life is chemistry in water. Mix inside with outside and the cell is gone in seconds. What barrier can hold an inside? | Fat blocks charge. How do you store copyable instructions if the archive cannot leave to wear out? |
| 2 | `mn-02-dna` | ב | Archive that copies without guessing. Why a double helix, and why most of the genome is not a gene? | You cannot send DNA to the cytosol to be worn down. What working copy can you throw away? |
| 3 | `mn-03-transcription` | ג | Unstable RNA is a feature. Why edit before leaving the nucleus? | Four letters must build machines with many chemistries. How does a triplet become a protein? |
| 4 | `mn-04-protein` | ד | Codons, tRNA adapter, structure is function. | Same DNA in liver and neuron. What turns one archive into many tissues? |
| 5 | `mn-05-regulation` | ה | Control is what turns one archive into many tissues. | Information processing in brain is a property of cells. What is a neuron, such that it can compute? |
| 6 | `mn-06-neuron` | ו | Polarity: dendrite in, axon out. Glia are not glue. Cajal vs Golgi. | Without a barrier to charge, no voltage. How do ion gradients become rest potential? |
| 7 | `mn-07-nernst` | ז | Nernst is one ion’s equilibrium, not the cell’s V_m. Goldman is the weighted leak. Steady state ≠ equilibrium. | Barrier without doors cannot live or signal. What is a channel vs a pump, and why is the membrane an RC circuit? |
| 8 | `mn-08-channels` | ח | Passive channel vs ATP pump. τ=RC, λ. Myelin as capacitor engineering. | Summed EPSPs at the AIS. What happens when they cross threshold? |
| 9 | `mn-09-action-potential` | ט | Positive feedback Na. All-or-none so amplitude is not the message. Peak above zero. Clamp exists because V-dependent g otherwise loops. | Dendrite is analog and decays; axon is digital and renews. How does the pulse travel, and how do two inputs add? |
| 10 | `mn-10-conduction` | י | Saltatory conduction. Temporal vs spatial summation. Kinesin/dynein. | The AP reached the terminal. Cells are not cytoplasmically continuous. How does a pulse become a molecule? |
| 11 | `mn-11-synapse` | יא | Ca²⁺ is the local fusion trigger. SNARE. Delay is the chemical signature. | Release without clearance is a stuck switch. How do you end the signal, and what is inhibition besides “minus voltage”? |
| 12 | `mn-12-inhibition` | יב | AChE / reuptake. Shunting via Cl⁻. Uniporter ≠ ionotropic receptor. | Neurons do not divide. How does a connection get stronger without a new cell? |
| 13 | `mn-13-plasticity` | יג | Hebb needs a coincidence detector: NMDA = ligand + depolarization (Mg block). LTP vs LTD. | Series close: walk the unpaid bills from the bilayer to NMDA. Bridge: 6166 behavior, 6110 representation — named as **outside** this course. |

## Per-video notes

**1 · membrane.** A cell is a unit of life: boundary + organized interior.
If the boundary were watery, diffusion equalizes in seconds. Phospholipids
are amphiphilic; they self-assemble a bilayer (not a pump that builds a
skin). The hydrophobic core rejects charge — that is *why* the membrane is
selective, and *why* voltage can exist later. Price: proteins as doors.
Organelles separate chemistries; vesicle is not an organelle; nucleus is
more permeable than the plasma membrane **on purpose**. Adult neuron does
not divide (named debt). Close on the archive that cannot leave.

**2 · dna.** Central dogma is a direction of flow, not a slogan. Double
helix copies without guessing (complement). Gene vs the rest (control, not
junk). Chromatin is the first control layer. Mitosis vs meiosis. Adult
neuron sits in G0. Germline vs somatic mutation. Close on: you cannot send
the archive to the cytosol.

**3 · transcription.** RNA is unstable on purpose (U, ribose, single
strand). Promoter, not “somewhere on the gene.” Three edits before export:
cap, poly-A, splicing. Alternative splicing is why ~20k genes are not 20k
recipes. ncRNA is post-transcriptional control. Close on four letters →
many chemistries.

**4 · protein.** Triplets, redundancy, silent mutation. tRNA is the
dictionary. A/P/E sites. Structure *is* function; a channel opening is
tertiary, not primary. Native well; denaturation vs degradation. ER:
translation **and** folding (exam). Close on same genome, many tissues.

**5 · regulation.** Promoter vs enhancer. Methyl closes, acetyl opens.
Fast (existing protein) vs slow (new gene). Kinase cascade, second
messenger. This is the condition for a neuron to make the right channels.
Close on: what is a neuron as a cell?

**6 · neuron.** Information processing is a property of cells, not a
continuous net. Soma / dendrite / axon polarity. Glia: astrocyte,
oligo vs Schwann (exam), microglia. Cajal vs Golgi; EM showed a cleft.
Methods by what they *actually* measure (EEG time, fMRI blood, clamp
current). Close on: how do gradients become rest?

**7 · nernst.** Orders of magnitude, not memorized millimolars. Two
forces. Nernst is one ion’s equilibrium, **not** V_m. Goldman is the
weighted leak. Driving force. Steady state ≠ equilibrium (pumps next
week). Close on doors and batteries.

**8 · channels.** Channel = passive, selective hole. Pump = against the
gradient, ATP. Secondary active. Uniporter ≠ ionotropic (named trap for
week 12). Membrane as RC: τ = RC is how long the membrane remembers;
λ is how far a passive voltage survives. Myelin lowers C, lengthens λ.
Close on threshold at the AIS.

**9 · action potential.** Positive feedback Na. All-or-none because
amplitude is not the analog of stimulus intensity. Peak above zero
refuses capacitor-collapse. TTX/TEA. Clamp exists because V-dependent
g otherwise loops. Refractory = one-way. Pumps refuel; they do not make
the spike. Close on analog dendrite / digital axon.

**10 · conduction.** Saltatory: passive under myelin, active at nodes.
Temporal summation (τ) vs spatial (λ, distance to AIS). Location is
computation. Kinesin anterograde, dynein retrograde — without roads,
no cargo at the terminal. Close on: pulse → molecule.

**11 · synapse.** Chemical translation. Ca²⁺ is the *local* fusion
trigger, not the postsynaptic message. SNARE. Order: AP → Ca channel →
synaptotagmin → SNARE → transmitter in the cleft. Delay is the chemical
signature. Ionotropic vs metabotropic. Close on clearance and inhibition.

**12 · inhibition.** Clearance is part of the code (AChE, reuptake).
Shunting: Cl⁻ conductance pins voltage away from threshold; location
near soma/AIS is why it works. Knee-jerk: inhibition is the action, not
decoration. Uniporter ≠ ionotropic. Close on: stronger without a new cell.

**13 · plasticity.** Hebb is macroscopic; NMDA is the molecule that can
*know* both sides fired. Two conditions: ligand + depolarization (Mg
block). Without Mg, coincidence dies. LTP vs LTD is calcium pattern, then
AMPA count in the membrane. Do not write “learning” without saying what
changed. Series close: walk the chain from bilayer to coincidence.
6166 and 6110 are named as unpaid *outside* bills, not as prior knowledge.

## Visual vocabulary

Same `ROLE` keys as PF/IL:

| role | colour | this series |
|------|--------|-------------|
| mind | gold | information, archive, coincidence “vote”, genotype |
| body | teal | membrane, fat, ions, current, voltage trace |
| behavior | grey | leak, mixing, methods averages, rest as compromise |
| compute | blue | channels, pumps, SNARE, digital AP, rules |
| fault | red | watery boundary, Nernst-as-V_m, amplitude-as-intensity, Golgi reticulum |
| debt | yellow | named debts and price chips |

Primitives in `utils/cell.py`: `position`, `price`, `relation`, `bilayer`,
`organelle`, `ion`, `channel`, `pump`, `helix`, `spike`, `synapse_cleft`,
`voltage_trace`, `chain_stack`, `nernst_line`, `rc_membrane`, `dim_group`,
`ring_around`.

`chain_stack` panes, never filled early:
archive → protein → voltage → pulse → release → change.

## Whisper-dangerous words

Do not cue: Nernst, Goldman, Hodgkin, Huxley, SNARE, NMDA, Cajal, Golgi,
Hebb, phospholipid, cytoskeleton, eukaryote. Prefer mechanism words:
`bilayer`, `equilibrium`, `clamp`, `threshold`, `myelin`, `shunting`,
`coincidence`, `clearance`. Cue `NMDA` only in video 13 if STT keeps it;
else cue `coincidence`.
