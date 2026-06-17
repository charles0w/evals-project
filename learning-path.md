---
tags:
- research
- ai-evals
- learning-path
---
# 02 — Learning path (6-week deep dive)

A sequenced run through 01-sources that ends with a real eval harness on **ai-trading-bot** and a publishable write-up. The rule: **every week ends by adding entries to the knowledge base** — reading without capture doesn't count. Mark each KB entry's `status` and `confidence` as you go; the Base's "Learning queue" view is your worklist.

> Target: ~4–6 focused hours/week. Stretch to 8 weeks if a project crunch hits — the sequence matters more than the calendar.

> [!note] The foundational entries are already seeded (14 in `kb/`). The weekly "capture" steps below are now mostly about *reading the source, then promoting the entry's `status` from to-learn → learning → mastered* and adding any gotcha you hit — not writing from scratch. Per-agent judge rubrics live in criteria/.

## Week 0 — Orientation

- Read the 3 anchors in 01-sources (Hamel's evals FAQ, the applied-LLMs piece, "Who Validates the Validators").
- Goal: absorb the vocabulary and the *why*. No building yet.
- **Capture:** confirm the 6 seed KB entries make sense; set each to `learning` once you've read its source. First skim of who-validates-the-validators.

## Week 1 — LLM-as-judge foundations

- Read: MT-Bench/Chatbot Arena paper + G-Eval. Deep-read who-validates-the-validators.
- Do: write a tiny pointwise *and* pairwise judge over 20 hand-picked outputs from any repo. Hand-grade the same 20 yourself.
- **Capture:** measure judge-vs-your agreement. Move llm-as-judge toward `mastered`; add a new entry on **position/verbosity bias** if you hit it.

## Week 2 — Datasets + the two-tool stack

- Read: two-tool-stack sources; skim DeepEval and Langfuse docs.
- Do: stand up **DeepEval as a CI gate** on a toy task; wire one metric to fail a test. Optionally connect **Langfuse** for tracing.
- **Capture:** entry on **golden datasets** (how to build/curate one); entry on **G-Eval** as a metric. Promote two-tool-stack.

## Week 3 — Agent & trajectory eval

- Read: τ-bench paper, agent-as-a-judge, the agent-eval survey. Internalize trajectory-eval and pass-k-reliability.
- Do: run (or read closely) the τ-bench retail tasks; see pass^k collapse first-hand.
- **Capture:** promote trajectory-eval, pass-k-reliability, agent-as-a-judge. Add entry on **T-Eval / AgentBoard Progress Rate** if you want the trajectory-metric detail.

## Week 4 — PROOF: eval harness on ai-trading-bot ✅ built

The depth → **proof** step. This is where the edge becomes real. **Implemented in [`harness/`](harness/)** — run `python harness/proof_harness.py validate` (or `--mock` for an offline demo).

- ✅ Define the success metric for one bot behavior — "signal rationale is sound and correctly cites the data" (rubric in `harness/proof_harness.py`, adapted from `criteria/finance-eod-recap.md`).
- ✅ Build a golden set from past signals — `harness/golden_signals.jsonl`, 30 hand-labeled cases *with ground-truth market data*. **Swap in real signals to make it live.**
- ✅ Implement an LLM judge for rationale quality; **validate it** against the labels (agreement, Cohen's κ, false-pass count — `who-validates-the-validators` in practice).
- ✅ Report **pass^k**, not just average — `passk` subcommand, with Wilson confidence intervals.
- ✅ **Capture:** project note in [`harness/notes.md`](harness/notes.md); gotchas logged there (faithfulness-needs-ground-truth, κ-over-raw-agreement, pass^k-needs-nondeterminism).
- **Remaining:** run `validate` against a real cross-family judge and record the κ; promote the related KB entries to `mastered`.

## Week 5 — Rigor + distribution

- Read: statistics of eval (sample size, confidence intervals on scores); benchmark-literacy pieces (contamination, gaming).
- Do: add confidence intervals to your Week-4 numbers. Write the war-story: "I built an eval harness for a trading bot — here's what broke."
- **Capture:** entry on **eval statistics / sample size**; entry on **benchmark contamination**. This write-up is the **distribution** step — the public artifact that makes the depth legible.

## After: keep it alive

- New paper/tool/trick → one atomic KB entry (use `kb/_template.md`).
- Use the Base's **"Needs review"** view (mastered + >30 days unreviewed) to refresh fading knowledge; bump `reviewed` when you do.
- Feed agents: point CEO (and any repo agent) at `research/ai-evals/kb/` as eval context — see 03-usage.

## See also

- 01-sources — the source list
- 03-usage — how to add entries + how agents query the DB
- README — the depth → proof → distribution thesis
