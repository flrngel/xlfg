---
description: Internal xlfg specialist lens. Split the work into coherent decision slices — not atomic one-line edits. Load from plan when the change touches more than one surface.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash
---

# xlfg-task-divider

Load this specialist from the plan phase when the change spans multiple surfaces and you need an ordering that avoids broken intermediate states.

## Purpose

Divide the work into **decision slices** — coherent chunks where one person owns a single decision — not atomic edits that split decisions across boundaries.

## Lens

You are preventing merge conflicts that don't exist yet. Parallel divergent decisions create bad merges; one owner per decision stays clean.

## How to work it

- Start with the plan's objective groups (`O1`, `O2`, …). One owner per group by default.
- Within a group, only subdivide when the surfaces are genuinely independent (no shared types, no shared config, no sequenced dependency). If there's coupling, keep the slice whole.
- Order the slices so each intermediate state compiles and the test contract's `fast_check` can run. A slice that leaves the repo broken halfway through is a bad slice.
- Name each slice by what it *decides*, not what it *edits*. "Introduce the retry config schema" not "edit 4 files."

## Done signal

An ordered list of slices with owner-decision, surface, and predecessor dependency. No slice leaves the repo in a non-buildable state.

## Stop-traps

- Splitting an epic into many atomic packets because the scope "feels big." Big isn't split criterion; independence is.
- Creating a slice that spans two decisions. That's how parallel work conflicts.
- Ordering by file-count rather than by dependency. The graph matters; the diff size doesn't.
