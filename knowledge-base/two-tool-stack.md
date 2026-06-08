---
title: The Two-Tool Eval Stack
type: pattern
domain: general
summary: 'A sustainable eval setup needs two tools: a lightweight code-native gate
  for CI/CD (DeepEval, promptfoo, Ragas) plus a platform for human annotation, regression
  tracking, and dashboards (Braintrust, Langfuse, Arize Phoenix).'
source: https://www.braintrust.dev/articles/deepeval-alternatives-2026
tags:
- eval-kb
- tooling
- pattern
---
# The Two-Tool Eval Stack

**TL;DR:** Don't make one tool do everything. Pair a fast CI gate (blocks bad changes on every commit) with a platform (stores runs, tracks regressions, hosts human review). Trying to force either role onto the other tool is where eval setups rot.

## What it is

The field's settled division of labor:

- **CI / code-native gate** — runs in the test suite, fails the build when a metric drops. *DeepEval* (pytest-native, 50+ metrics incl. G-Eval), *promptfoo* (YAML assertions + red-teaming; acquired by OpenAI March 2026, core stays MIT/open), *Ragas* (RAG-specific).
- **Platform / observability** — persistent home for eval runs, regression history, human annotation queues, stakeholder dashboards, production tracing. *Braintrust* (full lifecycle incl. prod monitoring), *Langfuse* (OSS, framework-agnostic, observability-first), *Arize Phoenix*, *LangSmith*.

## Why it matters / when to use

Starter pairing for my repos: **DeepEval as the CI gate + Langfuse (OSS, self-hostable) or Braintrust as the platform.** The gate keeps regressions out automatically; the platform gives me a place to actually *look* at failures and build golden sets over time. For ai-trading-bot specifically, the platform's regression tracking is what lets me prove a model/prompt change didn't quietly degrade signal quality.

## Gotchas

- **One-tool trap** — using only a CI gate means no history or human review; using only a platform means nothing blocks a bad deploy. You feel the missing half within weeks.
- **Vendor lock-in** — prefer OSS/self-hostable (Langfuse, Inspect) where the data is sensitive; the trading and fulfillment repos shouldn't ship eval data to a third party casually.
- Don't over-buy early. v0 can be DeepEval + a flat results file; add the platform when the eval set and team justify it.

## Source & related

- Primary: Braintrust, "DeepEval alternatives (2026)" — https://www.braintrust.dev/articles/deepeval-alternatives-2026
- Related: pass-k-reliability · 01-sources
