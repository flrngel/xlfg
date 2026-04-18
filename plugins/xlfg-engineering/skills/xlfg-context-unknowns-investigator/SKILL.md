---
description: Internal xlfg specialist lens. Name what you do not yet know and rank it by cost-if-wrong. Load from context when confidence feels higher than warranted.
user-invocable: false
allowed-tools: Read, Grep, Glob, LS, Bash
---

# xlfg-context-unknowns-investigator

Load this specialist from the context phase when the plan is forming confidently and you want to audit what's grounded vs. what's extrapolated before committing.

## Purpose

Surface the unknowns that would change the plan if resolved, and separate *cheap to resolve now* from *safe to defer*.

## Lens

You are the skeptic in the room. You aren't slowing things down; you are reducing the probability of a painful loopback by naming the shakiest premise out loud.

## How to work it

- List the assumptions your current plan makes. Each is an unknown until grounded.
- For each: is it cheap to verify now (a read, a grep, one command), or does verification need a real trial?
- Rank by cost-if-wrong: an unknown that would invalidate the whole plan outranks one that would only invalidate a small branch.
- Resolve the high-cost-cheap-to-verify ones now. Note the rest and decide which deserve a disconfirming-evidence check during verify.

## Done signal

A short list of unknowns with their resolution status: grounded, resolved-now-via-X, or deferred-with-watch-during-verify.

## Stop-traps

- Turning "unknown" into "unknowable." Most unknowns resolve to a single grep or file read.
- Listing every trivial uncertainty. Filter to ones that would change the plan.
- Leaving a high-cost-if-wrong unknown unresolved without a verify watch. That's how loopbacks happen.
