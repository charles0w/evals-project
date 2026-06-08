---
title: LongJudgeBench
type: benchmark
domain: llm-eval
summary: "A meta-evaluation benchmark measuring how reliable LLM-as-a-judge is on\
  \ long-form outputs (deep research, surveys, creative writing, long-chain analysis)\
  \ \u2014 the gap left by judge benchmarks that mostly test short answers; finds\
  \ judges remain unstable across scenarios."
source: https://arxiv.org/abs/2606.01629
tags:
- eval-kb
- llm-as-judge
- benchmark
---
# LongJudgeBench

**TL;DR:** Judges have been validated almost entirely on short answers, but we increasingly grade long-form output. LongJudgeBench shows long-form judging is *not* short-form judging with more tokens — and that current judges are unstable across scenarios, even with rubrics and references.

## What it is

A meta-evaluation benchmark (arXiv 2606.01629, June 2026) covering five practical long-form scenarios: deep research, scientific survey, creative writing, long-chain analysis, and systematic review. It systematically tests a range of LLM judges and finds a substantial reliability gap on long outputs: rubrics and references help but are not always sufficient.

## Why it matters / when to use

A direct, sharpening complement to who-validates-the-validators. Several of my outputs are long-form — an ai-trading-bot EOD recap, a CEO daily summary, a research synthesis. A judge I validated on short outputs may silently fail on those. Before trusting an llm-as-judge on any long document, account for the document-level demands this benchmark stresses.

## Gotchas

- The headline trap: reusing a short-form-validated judge prompt on long output is unsafe — long-form imposes document-level demands (consistency, coverage, structure) that short-form meta-eval never tests.
- Judges are *unstable across scenarios* — a judge that works for one long-form genre may not transfer to another; validate per use case.

## Source & related

- Primary: "Benchmarking LLM-as-a-Judge for Long-Form Output Evaluation" — https://arxiv.org/abs/2606.01629
- Related: who-validates-the-validators · llm-as-judge · 01-sources
