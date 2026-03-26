# Intent-eval fixtures

These fixtures define messy or underspecified prompts for `xlfg eval-intent`.

Each JSON file should contain:

- `id`
- `query`
- `expected.work_kind`
- `expected.direct_asks`
- `expected.implied_asks`
- `expected.acceptance_criteria`
- `expected.objectives`
- `expected.blocking_ambiguities`
- `expected.forbidden_claims`
- `expected.max_blocking_questions`

To grade a real run:

```bash
xlfg eval-intent --fixture evals/intent/<case>.json --run <RUN_ID>
```


To score the bundled reference artifacts for all fixtures:

```bash
xlfg eval-intent --suite-dir evals/intent
```

To score your own captured run artifacts instead:

```bash
xlfg eval-intent --suite-dir evals/intent --artifacts-root path/to/captured-intent-artifacts
```
