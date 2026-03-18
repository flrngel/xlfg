# xlfg 2.0.8: query understanding and root-solution upgrade

This note explains **why** xlfg 2.0.8 adds a query contract and anti-monkey-fix gates.

## The problem being fixed

Two linked failure modes kept showing up in xlfg runs:

1. The harness gradually **forgot what the original query actually meant**.
   - direct asks got partially implemented
   - implied asks disappeared after several steps
   - quality requirements faded while implementation details grew

2. The harness often shipped a **monkey fix / temp fix**.
   - one obvious entrypoint was patched
   - alternate paths still failed
   - tests were green for the narrow patch but not for the real user intent
   - implementation drifted from developer / product intention

The old artifacts (`why.md`, `diagnosis.md`, `flow-spec.md`, `test-contract.md`) helped, but they did not create one explicit request contract that later phases had to keep re-reading.

## Research ideas adopted

### 1) Query refinement before execution

A March 2026 paper, **CodeScout**, shows that coding agents improve when an underspecified request is converted into a more actionable problem statement *before* normal execution. The useful parts are:
- lightweight pre-exploration
- targeted scoping
- explicit reproduction / expected behavior
- reduced non-converging trajectories

xlfg adopts this as `query-contract.md` written by `xlfg-query-refiner` before broad repo fan-out.

### 2) Requirements and solutions must be separated

A March 2026 requirements-engineering paper argues that prompts blend:
- **Functionality + Quality**
- **General Solution**
- **Specific Solution**

That framing is valuable because coding agents often skip straight to a guessed solution without preserving the requirement itself.

xlfg adopts this decomposition inside `query-contract.md`.

### 3) Long runs suffer attention decay

Recent terminal-agent work reports that instructions near the start of a long trajectory lose influence as tool calls accumulate.

xlfg adopts a simple version of the remedy:
- keep a short **carry-forward anchor** inside `query-contract.md`
- force implementation / verification / review to re-read it
- copy it into `workboard.md` so the lead agent sees it repeatedly

This is the smallest practical version of an event-driven reminder system.

### 4) Many failures are path-drift, not raw capability gaps

Recent long-horizon work argues that agents often fail because they drift away from the task’s canonical solution path.

For xlfg, the practical lesson is:
- do not let implementation skip the request contract
- do not let tasks lose traceability to direct asks / implied asks
- do not treat a green symptom patch as proof of the root solution

### 5) Patch validation needs more than passing tests

Recent patch-validation work highlights three missing ingredients in false-correct patches:
- root cause analysis
- adherence to program specifications
- capturing developer intention

xlfg therefore adds all three to the run contract:
- `diagnosis.md`
- `query-contract.md`
- proof / scorecard traceability back to query / intent IDs

### 6) Skills only help when they are specific and context-compatible

Recent skill-evaluation work shows that most generic skills do not improve real SWE outcomes, and some hurt when they conflict with project context.

xlfg responds by keeping this upgrade narrow:
- one new planning agent (`xlfg-query-refiner`)
- one new run artifact (`query-contract.md`)
- stronger traceability in existing files
- no new heavy runtime layer

## What changed in xlfg 2.0.8

### New artifact

`query-contract.md`

It records:
- raw request
- direct asks (`Q*`)
- implied asks (`I*`)
- functionality and quality requirements (`R*`)
- general solution constraints
- specific solution constraints
- expected behavior / acceptance criteria (`A*`)
- reproduction / baseline notes
- non-goals
- developer / product intention
- prohibited shallow fixes
- carry-forward anchor

### New agent

`xlfg-query-refiner`

Its job is to make the request durable and explicit *before* the repo gets noisy.

### Existing artifacts now carry query traceability

- `flow-spec.md`
- `spec.md`
- `plan.md`
- `test-contract.md`
- `proof-map.md`
- `scorecard.md`
- task briefs / reports

These files now trace back to query / intent IDs so dropped requirements are easier to spot.

### Stronger anti-monkey-fix behavior

`test-contract.md` now includes **counterexample / anti-monkey probes**.

The idea is simple:
- if a patch only fixes the most obvious path,
- an alternate path / adjacent state / variant input should still fail,
- and the harness should plan for that explicitly.

### Stronger gates

A run is not honestly green if:
- commands passed but a direct ask still has no proof
- a non-negotiable implied ask disappeared
- the patch solved a local symptom while violating developer / product intention

## Practical rule of thumb for future evolution

When xlfg gets confused, ask in this order:

1. Did `query-contract.md` preserve what the user actually asked for?
2. Did the plan map tasks and proofs back to those query IDs?
3. Did implementation re-read the carry-forward anchor?
4. Did verification prove the root solution or only the absence of one visible symptom?
5. Did review catch uncovered asks or a monkey fix?

If the answer to any of those is “no”, fix the contract / traceability first.
