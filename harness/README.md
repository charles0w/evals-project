# PROOF harness — eval on ai-trading-bot signal rationales

The **Week-4 "proof" step** from [`../learning-path.md`](../learning-path.md): the point where the eval *discipline* becomes a working artifact on one real behavior. It takes a single ai-trading-bot output — the **signal rationale** — and runs the full loop almost everyone skips:

1. **Golden set** — [`golden_signals.jsonl`](golden_signals.jsonl): 30 hand-labeled rationales, each with the **ground-truth `market_data`** the rationale must be faithful to. This labeled set is the durable, reusable asset (see [`golden-datasets`](../knowledge-base/golden-datasets.md)).
2. **Judge** — reuses the toolkit's provider-aware [`judge()`](../toolkit/ceo_report.py) with a rubric adapted from [`criteria/finance-eod-recap.md`](../criteria/finance-eod-recap.md). The rationale is handed to the judge **together with its source data**, which is the documented fix for "faithfulness needs ground truth."
3. **Validate the judge** — measure agreement against the human labels *before* trusting any score ([`who-validates-the-validators`](../knowledge-base/who-validates-the-validators.md)): agreement %, Cohen's κ, confusion matrix (with **false-passes** called out — the dangerous error for a trading bot), Pearson on the raw 0..1 scores, and a Wilson confidence interval ([`eval-statistics`](../knowledge-base/eval-statistics.md)).
4. **Report reliability, not just average** — pass^k over identical inputs ([`pass-k-reliability`](../knowledge-base/pass-k-reliability.md)): does the pipeline pass on **all** k runs, or only on average?

## Run it

```bash
# Validate the judge against the human labels (needs a model key — see below)
python harness/proof_harness.py validate

# Reliability: run the judge k times per item on identical inputs
python harness/proof_harness.py passk --k 5
```

**Judge provider** (set one — see [`../.env.example`](../.env.example)):
- `ANTHROPIC_API_KEY`, or
- `EVAL_JUDGE_URL` + `EVAL_JUDGE_KEY` (any OpenAI-compatible endpoint, incl. a local Ollama for a free cross-family judge).

> Judge with a **different model family** than the one that wrote the rationales — self-preference bias is real ([`judge-biases`](../knowledge-base/judge-biases.md)).

**No key handy?** Add `--mock` for a deterministic offline pseudo-judge so the pipeline and the statistics run end to end (this is what CI does). Mock numbers are illustrative only — they validate the *harness math*, not a real judge.

```bash
python harness/proof_harness.py validate --mock
python harness/proof_harness.py passk --mock --k 5
```

## Reading the output

- **Cohen's κ ≥ 0.6** (substantial) and **zero false-passes** → the judge is trustworthy enough to gate on. Below that, the harness tells you to sharpen the rubric on the printed disagreements and re-validate.
- **False-pass** = the judge approved a signal you failed by hand. For a pipeline trusted with capital this is the costly direction; the verdict weights it.
- **pass@1 vs pass^k gap** = the inconsistency an average hides. Flaky items (passed some runs, failed others on the *same* input) are listed by id.

## Swap in real data

Replace [`golden_signals.jsonl`](golden_signals.jsonl) with your own hand-labeled signals — same fields per line:

| field | meaning |
|---|---|
| `id` | stable identifier |
| `signal` | the signal/direction the bot emitted |
| `market_data` | **ground truth** — the numbers the rationale must match |
| `rationale` | the agent output being graded |
| `human_score` | your hand label, 0..1 |
| `human_pass` | your hand label at the 0.7 threshold |
| `failure_mode` | tag for the disagreement analysis (`none`, `hallucinated_number`, …) |
| `note` | why you labeled it that way |

The code is fixed; **the labeled set is the asset.** Expect to revise labels as your notion of "good" sharpens — criteria drift is a feature, not a failure.

## Files

| file | what |
|---|---|
| `golden_signals.jsonl` | the 30-case hand-labeled golden set |
| `proof_stats.py` | pure, tested stats (κ, Wilson CI, pass^k, Pearson) |
| `proof_harness.py` | the runner: `validate` and `passk` subcommands |
| `notes.md` | project log — what this proves and the gotchas hit building it |

Stats are unit-tested in [`../toolkit/tests/test_proof_stats.py`](../toolkit/tests/test_proof_stats.py).
