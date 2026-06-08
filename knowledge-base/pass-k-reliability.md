---
title: pass^k (Reliability Metric)
type: metric
domain: agent-eval
summary: "pass^k measures the probability an agent succeeds on ALL k independent attempts\
  \ at a task \u2014 a consistency/reliability metric, distinct from pass@k which\
  \ rewards succeeding at least once."
source: https://arxiv.org/abs/2406.12045
tags:
- eval-kb
- agent-eval
- reliability
- metrics
---
# pass^k (Reliability Metric)

**TL;DR:** Capability ≠ reliability. pass^k asks "if I run this task k times, does it succeed *every* time?" — the question that actually matters before you trust an agent with a customer or with capital.

## What it is

From the τ-bench paper. Two easily-confused metrics:

- **pass@k** (capability) — succeeds on *at least one* of k tries. Optimistic; rewards a lucky run.
- **pass^k** (reliability) — succeeds on *all* k tries. Punishing; measures consistency.

The τ-bench result is the memorable one: even strong function-calling agents (gpt-4o-class) solved <50% of tasks, and pass^8 dropped below 25% in the retail domain. Translation: run the same task eight times and three-quarters of the time at least one run breaks. That gap between "works in the demo" and "works every time" is the whole reliability problem in one number.

## Why it matters / when to use

This is the single most important metric framing for any repo where a failure costs money. ai-trading-bot: a signal pipeline that's right 70% of the time but *inconsistent* on identical inputs is untradeable. shopify-arbitrage and CEO: same — one bad run in eight that auto-fulfills a wrong order or sends a wrong message is a real liability. Report pass^k, not just average success, the moment money or customers are involved.

## Gotchas

- **Single-number reporting off tiny samples** — pass^k on 20 examples has huge variance; you need enough trials to trust the estimate, and ideally confidence intervals.
- pass^k collapses fast as k grows — don't panic at low pass^8; understand it's geometrically harsher than pass@1 by design.
- Reliability and capability are different axes. A more capable model can be *less* reliable. Track both.

## Source & related

- Primary: Yao et al., "τ-bench: Tool-Agent-User Interaction in Real-World Domains" — https://arxiv.org/abs/2406.12045
- Related: trajectory-eval · two-tool-stack · 01-sources
