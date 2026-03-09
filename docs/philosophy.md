# xlfg philosophy

## The wrong loop

A lot of agent workflows still do this:

1. vague requirement
2. code quickly
3. run big tests later
4. patch whatever fails

That loop rewards shortcuts.

## The xlfg loop

1. recall the smallest relevant prior truth
2. define **why** the work matters
3. diagnose the real problem
4. define the UX / behavior contract
5. define the test contract
6. define the environment contract
7. choose the minimum honest harness profile
8. implement in bounded task loops
9. verify with evidence
10. compound what was learned

## Bigger harness is not automatically better

The goal is not to imitate a giant multi-service runtime for its own sake.

The goal is to import the useful harness ideas:
- explicit state
- bounded loops
- progressive capability loading
- durable memory
- honest proof

and leave out the parts that add operational weight without improving local product work.

## Review is not the cleanup crew

Reviewers should catch blind spots, not rescue a sloppy implementation strategy.
Planning and implementation must do most of the quality work.

## Shortcut patches are debt

A change that only hides the symptom is not a good result, even if it makes a test pass.
If a workaround is the only safe move, it must be documented as a workaround and treated as a scoped exception — not silently passed off as the real solution.

## Green commands are not enough

Verification is not “did some commands return 0?”

Verification is:
- did the intended flow actually work?
- does the environment state prove the right build / server / endpoint is live?
- does the proof map have real evidence for required scenarios?

If the proof map still has a required gap, the run is not done.
