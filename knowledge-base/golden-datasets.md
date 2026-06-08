---
title: Golden Datasets
type: technique
domain: general
summary: "A curated, human-labeled set of representative and edge-case inputs with\
  \ expected outputs (or pass/fail labels) that an eval runs against; the durable\
  \ asset of any eval program \u2014 most cheaply grown by harvesting real production\
  \ failures into regression cases."
source: https://hamel.dev/blog/posts/evals-faq/
tags:
- eval-kb
- datasets
- technique
---
# Golden Datasets

**TL;DR:** Evals are only as good as what you test against. A golden set is your curated bank of cases — typical inputs, known edge cases, and past failures — with expected results. It's the asset that compounds: every bug you turn into a case can never silently regress again.

## What it is

A versioned collection of `(input, expected)` examples — expected can be a gold answer, a rubric, or just a pass/fail label. Three sources feed it:

1. **Representative cases** — the normal distribution of real inputs.
2. **Edge cases** — the weird stuff that breaks things (empty data, adversarial phrasing, extreme values).
3. **Regression cases** — every production failure, captured the moment you find it, so it's tested forever after.

## Why it matters / when to use

This is the Week-4 deliverable in 02-learning-path: hand-label ~30–50 past ai-trading-bot recaps into a golden set, and it becomes reusable forever — for validating the judge (who-validates-the-validators), for CI gating (two-tool-stack), and for catching regressions when I change a prompt or model. Curating *sources* of cases up front is also how the ingestion noise problem gets solved: a good set encodes what "good" means.

## Gotchas

- **Start tiny.** 30 well-chosen cases beat 500 random ones. Per CEO's own eval-plan: "don't build a 200-task suite" — 90% of regressions live in ~10 behaviors.
- **Label drift** — as your notion of "good" sharpens (who-validates-the-validators), revisit old labels; a stale gold answer poisons every run.
- **Leakage** — keep the golden set out of any prompt/few-shot context, or you're testing memorization, not capability (see benchmark-contamination).

## Source & related

- Primary: Hamel Husain, "LLM Evals: Everything You Need to Know" — https://hamel.dev/blog/posts/evals-faq/
- Related: who-validates-the-validators · two-tool-stack · eval-statistics · 01-sources
