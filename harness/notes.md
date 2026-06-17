---
tags:
- ai-evals
- project
- ai-trading-bot
---
# Project note — PROOF harness (Week 4)

Stands in for the `repos/ai-trading-bot/notes.md` capture step in
[`../learning-path.md`](../learning-path.md): the harness lives here, in the
evals repo, because it's a reusable methodology — point it at real
ai-trading-bot signals by swapping `golden_signals.jsonl`.

## What this proves

The depth → **proof** step is done: one bot behavior (signal rationale) now has
an end-to-end eval that (1) judges against a hand-labeled golden set with the
**source data supplied** for faithfulness, (2) **validates the judge** against
the human labels before trusting it, and (3) reports **pass^k** reliability with
a confidence interval — not a single average. That's the whole thesis in a
runnable artifact.

## Gotchas hit (the capture the learning-path asks for)

- **Faithfulness is unmeasurable without ground truth.** This is exactly what
  `criteria/finance-eod-recap.md` flagged after its first live run (a recap
  scored 0.15 because the judge had no data to verify against). The fix is
  structural, not prompt-tuning: hand the judge the `market_data` alongside the
  rationale. The golden set bakes the ground truth into every row so the
  faithfulness axis actually bites.
- **Raw agreement lies; use kappa.** The golden set is ~47% pass, so a judge
  that blindly failed everything would still post ~53% agreement. Cohen's κ
  corrects for that chance baseline — it's the number to gate on, not agreement.
- **The dangerous error is asymmetric.** A false-fail wastes a good signal; a
  **false-pass** wages capital on a bad one. The harness surfaces false-passes
  separately and the verdict refuses to bless a judge that produced any.
- **Borderline cases are where criteria drift lives.** The deliberate
  borderline rows (`sig-011`, `sig-023`, `sig-030`) are the ones that flip
  across runs and drive most disagreements — re-grading exactly those is how the
  rubric sharpens. Keep a handful of borderline items in any golden set on
  purpose.
- **pass^k needs real nondeterminism.** An OpenAI-compatible judge at
  `temperature=0` is near-deterministic, so pass^k ≈ pass@1 and the metric looks
  trivially green. To actually probe reliability, run the judge at a non-zero
  temperature (or accept that you're measuring the *generator's* variance, not
  the judge's). The `--mock` mode injects seeded per-run noise so the pass^k
  machinery is observable offline.

## Next

- Run `validate` with a **real** cross-family judge and record the κ here;
  promote `who-validates-the-validators` and `pass-k-reliability` toward
  `mastered` in the KB.
- Week 5: add the paired-significance comparison (two rubrics / two judge models
  on the same golden set) and write the public war-story — the distribution step.
