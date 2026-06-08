---
title: Eval Statistics (Sample Size & Confidence)
type: concept
domain: general
summary: 'Eval scores are estimates with uncertainty: a number off 20 examples has
  a wide confidence interval, so apparent improvements are often noise. Report sample
  size and confidence intervals, and use enough examples before claiming a model/prompt
  change actually helped.'
source: https://hamel.dev/blog/posts/evals-faq/
tags:
- eval-kb
- statistics
- concept
---
# Eval Statistics (Sample Size & Confidence)

**TL;DR:** "82% vs 79%, the new prompt wins" off 30 examples is usually noise. An eval score is a sample statistic with a confidence interval; if the intervals overlap, you've proven nothing. This is the quiet differentiator — almost everyone reports a single number and stops.

## What it is

A pass-rate over N examples is a binomial estimate. Its uncertainty is roughly ±1/√N at the worst case — so 20 examples gives a confidence interval of ~±22 points, 100 gives ~±10, 400 gives ~±5. Practical consequences:

- **Confidence intervals** — report them, not just the point estimate. Wilson or bootstrap intervals on the pass-rate.
- **Significance** — to claim B beats A, the difference must exceed the noise (paired test on the same golden set, since the items are shared).
- **Power** — to detect a 3-point improvement reliably you need hundreds of examples, not dozens.

## Why it matters / when to use

The moment I'm comparing prompts/models on ai-trading-bot or CEO, this decides whether a change is real. Pair it with the reliability metric: pass^k off a tiny sample is *especially* noisy because it's a product of probabilities. Run comparisons on the same golden set so the test is paired and tighter.

## Gotchas

- **Single-number reporting off tiny samples** is the trap nearly everyone falls into.
- More data isn't free — judge calls cost money; balance N against budget (CEO's eval-plan budgets ~$0.13/run for exactly this reason).
- Beware multiple comparisons — test 10 prompt variants and one will look "best" by chance.

## Source & related

- Primary: Hamel Husain, "LLM Evals: Everything You Need to Know" — https://hamel.dev/blog/posts/evals-faq/
- Related: golden-datasets · pass-k-reliability · benchmark-contamination · 01-sources
