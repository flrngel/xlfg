# Research notes behind xlfg 2.0.3

This revision adds a deterministic memory and recall layer.

## 1) Recall should load the right context, not the most "semantic" context
We borrowed the useful shape of `/recall` and QMD: temporal recall, typed query documents, and exact lexical syntax. We intentionally did **not** adopt vector search, HyDE, or LLM query expansion in xlfg because the goal here is auditable recall for production engineering workflows.

## 2) Memory should be aligned to the current stage and role
Large, episode-level memory blobs are too coarse for long software workflows. xlfg now keeps shared knowledge, role-specific memory, and an append-only ledger, and retrieval can filter by stage, role, kind, scope, path, and time.

## 3) Durable memory should be append-only and replayable
Instead of rewriting one giant summary, xlfg now keeps `ledger.jsonl` as a structured event log. The run stays local and episodic; durable lessons are promoted into shared knowledge and logged as immutable events.

## 4) Keep the retrieval contract simple enough to trust
The recall system is intentionally lexical-first. That makes it weaker than the best hybrid retrieval systems on broad QA benchmarks, but much easier to audit in engineering workflows where exactness and provenance matter more than fuzzy semantic reach.
