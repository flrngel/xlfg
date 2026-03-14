# Research notes behind xlfg 2.0.5

This revision adds a more explicit harness model instead of just adding more prompts.

## 1) A harness is runtime structure, not a bigger prompt

The most useful lesson from recent harness writeups is that long-horizon agent quality improves when the environment, execution loop, and artifacts are made more explicit and enforceable.

That is why xlfg now adds:
- `why.md`
- `harness-profile.md`
- `workboard.md`
- `proof-map.md`

## 2) Memory should align to the actual unit of work

Large, episode-level memory blobs are too coarse for long software workflows. xlfg keeps shared knowledge, role-specific memory, and an append-only ledger, and retrieval can filter by stage, role, kind, scope, path, and time.

## 3) Verification must be linked to the requirement, not only to command success

The new `proof-map.md` makes verification answer a stricter question: *what exact evidence would prove this scenario really works?*

## 4) Capability loading should be progressive

Optional agents now load only when the diagnosis justifies them. This borrows the useful “progressive loading” idea from larger harnesses without importing the whole runtime stack.

## 5) Deterministic recall stays the default

This repo still intentionally avoids vector search, HyDE, and LLM query expansion in the core path. The priority is auditability, exact provenance, and high-signal retrieval for production engineering work.
