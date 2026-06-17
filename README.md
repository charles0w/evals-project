# evals-project

A practical, opinionated knowledge base and toolkit for **evaluating LLMs and AI agents** — built depth-first, around one question that matters more than any benchmark leaderboard:

> *Is this output good enough to trust with a customer, or with capital?*

Most "AI evals" advice is hand-waving. This repo is the opposite: a curated set of atomic concept notes, a reusable Python toolkit for scoring agent output, and per-task judging rubrics — assembled while actually wiring evals into production agents.

## Why evals (and why depth)

Evals are the durable, under-practiced skill in AI engineering. Models change; the discipline of *measuring whether they're any good* doesn't. Almost everyone ships on vibes — a working eval harness is rare and immediately legible as expertise. This project is organized around going **deep on one thing** rather than wide on everything.

## What's here

| Folder | What it is |
|---|---|
| [`knowledge-base/`](knowledge-base/) | Atomic concept notes — one idea per file (LLM-as-judge, trajectory eval, pass^k reliability, judge biases, benchmark contamination, the canonical papers/benchmarks, and more). Start at [`knowledge-base/README.md`](knowledge-base/README.md). |
| [`toolkit/`](toolkit/) | Reusable code. `ceo_report.py` — a provider-aware **LLM-as-judge** (Anthropic or any OpenAI-compatible endpoint), a **pass^k-style reliability tracker**, and a status reporter. Plus runnable [`examples/`](toolkit/examples/). |
| [`harness/`](harness/) | The **Week-4 PROOF harness** — a runnable end-to-end eval on one real behavior (ai-trading-bot signal rationales): a hand-labeled golden set, a validated LLM judge, and pass^k reliability with confidence intervals. Start at [`harness/README.md`](harness/README.md). |
| [`criteria/`](criteria/) | Per-task judging **rubrics** — versioned definitions of "good," kept out of code so they have one home. |
| [`sources.md`](sources.md) | A curated, deliberately short source list — the few people, papers, tools, and benchmarks actually worth following. |
| [`learning-path.md`](learning-path.md) | A 6-week deep dive that ends in a real eval harness on a real system. |

## The toolkit in 30 seconds

```python
from ceo_report import judge, track_reliability

ev  = judge(output, criteria="Faithful to source data; complete; no hallucinated numbers")
rel = track_reliability("my-agent", passed=ev["score"] >= 0.7)
print(ev["score"], ev["summary"], rel)
```

- `judge()` auto-selects **Anthropic** (`ANTHROPIC_API_KEY`) or any **OpenAI-compatible** endpoint (`EVAL_JUDGE_URL`/`EVAL_JUDGE_KEY`). Returns `{score 0..1, summary}`.
- **Local cross-family judge with [Ollama](https://ollama.com) (free, offline).** Ollama speaks the OpenAI chat API, so a local open model is a zero-cost *different family* from a Claude/GPT/Gemini generator — the cheap fix for self-preference bias. `ollama pull qwen2.5:7b`, then point `EVAL_JUDGE_URL` at `http://localhost:11434/v1/chat/completions`. See [`.env.example`](.env.example) for the full config.
- `track_reliability()` records pass/fail and returns the recent pass-rate — a `pass^k`-style consistency proxy (capability ≠ reliability).
- No heavy deps: standard library + `PyYAML`-free. Bring your own model key (or run a local one).

## Tests / CI gate

The toolkit ships with an offline test suite (standard-library `unittest`, no network, no keys) — eating our own dog food on [`two-tool-stack.md`](knowledge-base/two-tool-stack.md)'s "a CI gate + a platform." Run it locally:

```bash
python -m unittest discover -s toolkit/tests -v
```

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs the same suite on every push/PR across Python 3.9–3.12, plus a byte-compile syntax gate over `toolkit/`.

## Core principles (baked into every note)

1. **Capability ≠ reliability.** A model that's right 80% of the time but inconsistent on identical inputs is untradeable. Measure both.
2. **Validate the judge before you trust it.** An LLM judge is itself a model that can be wrong — hand-grade a sample and confirm agreement first. Judge with a *different* model family than the one that produced the output (self-preference bias).
3. **Faithfulness needs ground truth.** A judge with no source data can only assess internal consistency, not factual correctness — give it the data.
4. **Statistical rigor.** A score off 20 examples has a huge confidence interval. Report sample size; don't trust single-number deltas.
5. **Distrust leaderboards.** Benchmark contamination inflates public scores over time — weight your own private evals.

## Status

Living repo. The knowledge base grows as new techniques and benchmarks land; the toolkit is in active use. Contributions/forks welcome under the MIT license.
