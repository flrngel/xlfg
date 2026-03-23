---
name: xlfg
description: Legacy shim for the autonomous xlfg skill. Run the whole SDLC in one invocation.
argument-hint: "[feature, bugfix, investigation, or delivery request]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, LS, Bash, Edit, MultiEdit, Write, TodoWrite, Task
effort: high
hooks:
  PermissionRequest:
    - matcher: "ExitPlanMode"
      hooks:
        - type: command
          command: >
            echo '{"hookSpecificOutput": {"hookEventName": "PermissionRequest", "decision": {"behavior": "allow"}}}'
---

This legacy command is a compatibility shim for `skills/xlfg/SKILL.md`.

Follow that skill's workflow in this session.

Non-negotiable rules:

- run recall → plan → implement → verify → review → compound in this one invocation
- do **not** ask the user to run phase subcommands
- keep `spec.md` as the single source of truth
- seed only the lean core docs, then create optional docs only if they reduce risk
- ask the user only for true human-only blockers

Read `plugins/xlfg-engineering/skills/xlfg/SKILL.md` now if you need the full playbook, then execute it.
