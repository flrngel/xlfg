# xlfg philosophy

## The wrong loop

A lot of agent workflows still do this:

1. vague requirement
2. code quickly
3. run big tests later
4. patch whatever fails

That loop rewards shortcuts.

## The xlfg loop

1. understand the real problem
2. define the UX / behavior contract
3. define the test contract
4. define the environment contract
5. choose the root solution
6. implement in bounded task loops
7. verify with evidence
8. compound what was learned

## Review is not the cleanup crew

Reviewers should catch blind spots, not rescue a sloppy implementation strategy.
Planning and implementation must do most of the quality work.

## Shortcut patches are debt

A change that only hides the symptom is not a good result, even if it makes a test pass.
If a workaround is the only safe move, it must be documented as a workaround and treated as a scoped exception — not silently passed off as the real solution.
