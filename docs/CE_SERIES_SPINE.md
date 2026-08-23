# Computer Engineering series — the spine

Fifteen videos, one per volume of `StudyMaterial/Computer Engineering/`, in
folder order. **They are one argument, not fifteen summaries.**

## The question the series answers

Ben is an electrical engineer. He understands MOSFETs, semiconductor physics,
and how a binary number decodes into a selection of logic gates. His gap, in his
words: *how do you get from that to writing a kernel?* Everything here is built
to close that specific gap, in order, without ever asking him to accept a layer
on faith.

## Hard rules for every video in this series

1. **Inherit and hand off.** Each video opens on the exact question the previous
   one closed with, and closes on the question the next one opens with. The
   opening beat must restate the inherited question in one sentence — assume the
   viewer watched the previous video a week ago, not a minute ago.
2. **Never assume a layer that has not been built yet.** No mentioning the OS
   before video 8. No mentioning caches before video 4. If a later idea must be
   gestured at, name it as a debt: "we will need something to fill that table —
   that is three videos from now."
3. **RISC-V is the anchor.** All encodings, register names and instruction
   examples are RV32I unless the volume is inherently ISA-agnostic. Show real
   32-bit encodings with real field boundaries. Where Apple/ARM64 differs in a
   way that matters (exception levels, TTBR registers), name it in one sentence
   and move on.
4. **The audience is an EE.** Reach for the electrical explanation when one
   exists — a bistable pair of inverters, a DRAM cell as a capacitor bleeding
   charge, setup/hold as a race. Never explain a MOSFET. Never explain what a
   voltage is. Do explain every piece of software vocabulary from nothing.
5. **Vocabulary module.** `utils/cpu.py` is shared, identical in every demo.
   Grayscale is a value; semantic colour is a *role* (instruction gold, data
   blue, control teal, fault red). Reuse `bitfield`, `reg_file`, `mem_column`,
   `datapath_stage` rather than reinventing them, so a register file looks the
   same in video 2 and video 12.
6. **Cross-reference, do not transcribe.** The `.tex` volume is the rigorous
   track. The video carries the argument and the pictures; it may quote a result
   and point at the appendix. It must not become a spoken table of contents.

## The ladder

| # | slug | volume | opens on | closes on |
|---|------|--------|----------|-----------|
| 1 | `ce-01-sequential-machines` | 1_1 | Gates compute instantly and remember nothing. So what holds a result still long enough to use it? | We can now run **one** wired algorithm forever. What if we want a different one tomorrow? |
| 2 | `ce-02-programmable-computer` | 1_2 | Rewiring for each algorithm is absurd. What if the algorithm were *data*? | The program lives in memory — but we have been drawing memory as one flat uniform box, and it is not one thing. |
| 3 | `ce-03-memory-devices` | 1_3 | What is memory physically, and why can it not be both fast and large? | The fast memory is tiny and the large memory is slow. How do you get both at once? |
| 4 | `ce-04-memory-hierarchy` | 1_4 | Locality is an empirical fact about programs. Can it be exploited automatically? | The address a program names no longer determines where its data physically sits — and two programs both want address 0x1000. |
| 5 | `ce-05-virtual-memory` | 1_5 | Two programs, one address. Who arbitrates? | Translation is enforced in hardware, but *something* has to fill that table — and it cannot be the program being translated. |
| 6 | `ce-06-pipelines` | 2_1 | The datapath is idle most of every cycle. Why? | Overlapping instructions makes "which instruction are we on" ambiguous. |
| 7 | `ce-07-out-of-order` | 2_2 | In-order issue stalls on one slow load. Can we run past it? | If instructions finish out of order, "where was I?" has no answer — and that answer is exactly what is needed to interrupt a program and resume it. |
| 8 | `ce-08-interrupts-privilege` | 2_3 | A CPU that only completes instructions can never be reached from outside. How does anything stop it? | We now have a *mechanism* for taking control, with no *policy*. Who owns the vector table? |
| 9 | `ce-09-kernel-processes` | 2_4 | Privilege is a hardware constraint, not an operating system. What is the software that uses it? | Two processes, one CPU, both runnable. Who decides which runs, and when does it get asked? |
| 10 | `ce-10-scheduler` | 2_5 | The timer interrupt is the only reason preemption can exist. Given that hook, what policy? | Now they genuinely interleave, and they share memory. That breaks in ways a single sequential machine never could. |
| 11 | `ce-11-synchronization` | 2_6 | Two threads, one variable, no order. Why can software alone not fix this? | Every atom we built assumed one CPU with one cache. Add a second core and the assumption dies. |
| 12 | `ce-12-cache-coherence` | 3_1 | Two caches hold the same address. Which one is right? | Coherence orders accesses to *one* address. It says nothing about the order of accesses to *different* addresses. |
| 13 | `ce-13-memory-consistency` | 3_2 | Each address is coherent, and the program is still wrong. How? | The hardware is now correct and fast. The OS still has to decide which core runs what. |
| 14 | `ce-14-multiprocessor-scheduling` | 3_3 | One ready list or many? And what does a cache make "cheap" mean? | Threads turn out to be the wrong unit of work for this. |
| 15 | `ce-15-dispatch-qos` | 3_4 | A thread per task is the wrong grain. What replaces it? | (Series close — return to the ladder: every layer was forced by the one below it.) |

## Per-video notes

**1 · sequential machines.** The EE entry point: cross-coupled inverters, setup
and hold as a race, why edge-triggering exists. Land the FSM as *the* general
shape: state register + next-state logic + output logic. Datapath and control as
two FSMs talking. Do **not** mention instructions.

**2 · programmable computer.** The single reframe that matters: the control FSM's
next-state function becomes a *table in memory*, and the state register becomes
the PC. Build an RV32I encoding on screen field by field (opcode / rd / funct3 /
rs1 / rs2 / funct7) and show the same bits driving the same gates from video 1.
Fetch–decode–execute as the outer loop. Registers vs memory. Call and return as
the first thing that needs a stack.

**3 · memory devices.** Physical, EE-flavoured: SRAM as six transistors holding
each other up; DRAM as one capacitor leaking, hence refresh and destructive
reads; flash as trapped charge and why erase is a block operation. The point is
the *cost curve*, not a device tour.

**4 · memory hierarchy.** Locality as measurement, not assumption. Direct-mapped
→ set-associative → fully associative as a forced progression. Address split into
tag/index/offset — reuse the `bitfield` visual from video 2. Write-through vs
write-back. Close on the aliasing problem that virtual memory will inherit.

**5 · virtual memory.** The one indirection. Page table as a function from VPN to
PFN; multi-level tables because a flat one is absurd; the TLB because the walk is
too slow. Permission bits as hardware-enforced policy. Close hard on: *the table
is data in memory that the running program must not be able to write.*

**6 · pipelines.** Idle silicon forces it. Structural / data / control hazards as
three failures of the same overlap. Forwarding, stalling, prediction. Keep this
about throughput; do not drift into exceptions.

**7 · out-of-order.** Scoreboard → Tomasulo → reorder buffer. The ROB is the
punchline and it is the bridge to video 8: architectural state must be
recoverable at an instruction boundary, or the machine cannot be interrupted.

**8 · interrupts and privilege.** Three distinct transfers (interrupt /
exception / trap) that share one mechanism. Vector table, mode bit, what the
hardware saves. RISC-V `mstatus`/`mtvec`/`mepc`, named as such. Privilege as a
*hardware* constraint: a bit that changes which instructions decode legally —
tie this straight back to video 1's decoder.

**9 · kernel, processes, threads.** The PCB as frozen machine state — literally
the register file plus the page-table root plus the PC from video 2. Context
switch as save/restore. Thread vs process as "what is shared." Monolithic vs
microkernel. The syscall path end to end.

**10 · scheduler.** Policy on the timer hook. FIFO → SJF → round robin → MLFQ →
CFS/vruntime → EDF. Every policy answers "what does fair mean" differently.

**11 · synchronization.** Why load-modify-store is not atomic; what hardware
must provide (LR/SC in RISC-V, CAS elsewhere); spin vs block; futex as the fast
path. Close on: this all assumed one cache.

**12 · cache coherence.** Two caches one line. Snooping vs directory. MSI → MESI
→ MOESI as forced refinements. Invalidate vs update.

**13 · memory consistency.** The reordering that makes correct hardware run
wrong programs. SC as the ideal, TSO as what x86 gives, weak models as what ARM
gives, release/acquire as the portable contract. Fences.

**14 · multiprocessor scheduling.** Global vs per-core ready lists, work
stealing, affinity as a cache argument, heterogeneous cores (this is where Apple
P/E cores appear as an *instance*), gang scheduling.

**15 · dispatch and QoS.** Thread-per-task is the wrong grain; work queues;
naming submission; latency vs throughput; priority inversion and forcing a worker
to let go. Close the series by walking back down the ladder in fifteen seconds.
