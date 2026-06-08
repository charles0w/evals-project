---
title: Who Validates the Validators?
type: paper
domain: llm-eval
summary: "Before trusting an LLM judge, align it to human preference: have a human\
  \ grade a subset, then select the judge prompt/criteria that best match those grades\
  \ \u2014 and expect the criteria themselves to drift as you look at data."
source: https://arxiv.org/abs/2404.12272
tags:
- eval-kb
- llm-as-judge
- paper
---
# Who Validates the Validators?

**TL;DR:** An LLM judge is itself a model that can be wrong. This paper makes the loop honest: grade a sample by hand, pick the judge implementation that best agrees with your grades, and accept that defining "good" is iterative — your criteria sharpen only once you start looking at real outputs.

## What it is

Shankar et al. (2024). The core move: you can't just write a judge prompt and trust its scores. Their EvalGen interface generates candidate judge implementations (LLM grader prompts *and* Python assertion functions), then asks the human to grade a subset of outputs; that feedback selects the implementations that best align with human judgment.

The deeper finding is about **criteria drift**: people think they know their eval criteria up front, but grading real outputs changes what they care about. Evaluation is a moving target you discover by doing, not a spec you write once.

## Why it matters / when to use

This is the discipline that turns "I have a judge" into "I have a *trustworthy* judge." For every repo using llm-as-judge, the validation step is non-optional: grade 30–50 real outputs myself, measure judge agreement, iterate the rubric. Skipping it means I'm stacking an unvalidated judge on top of an unvalidated agent — confidence with no ground truth.

## Gotchas

- **The validation set is the asset** — those hand-graded examples are reusable gold data; treat them as durable, version them.
- **Criteria drift is a feature, not a failure** — expect to rewrite your rubric after looking at outputs; budget for it instead of treating the first rubric as final.
- Alignment is subjective and per-task — a judge validated for one repo's notion of "good" doesn't transfer to another's.

## Source & related

- Primary: Shankar et al., "Who Validates the Validators? Aligning LLM-Assisted Evaluation with Human Preferences" — https://arxiv.org/abs/2404.12272
- Related: llm-as-judge · 01-sources
