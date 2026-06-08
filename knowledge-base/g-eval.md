---
title: G-Eval
type: technique
domain: llm-eval
summary: An LLM-as-judge scoring method that uses a strong model plus chain-of-thought
  'evaluation steps' and a form-filling paradigm to grade open-ended output against
  a rubric, with token-probability weighting for finer-grained scores; the basis for
  most modern metric tooling.
source: https://arxiv.org/abs/2303.16634
tags:
- eval-kb
- llm-as-judge
- technique
---
# G-Eval

**TL;DR:** A more rigorous flavor of llm-as-judge: instead of asking "rate this 1–5," G-Eval first has the model generate explicit evaluation steps (chain-of-thought), then fills a scoring form, and can weight by token probabilities for smoother scores. It's what powers the built-in metrics in tools like DeepEval.

## What it is

Liu et al. (2023). The recipe: (1) give the judge a task definition + criteria, (2) let it auto-generate the chain of *evaluation steps* for that criteria, (3) have it score via a structured form, (4) optionally weight the score by the probabilities of the rating tokens to avoid the "always says 3" clustering of naive 1–5 prompts. Result: noticeably higher correlation with human judgment than plain pointwise scoring on summarization/dialogue tasks.

## Why it matters / when to use

When a bare llm-as-judge score feels noisy, G-Eval is the upgrade. It's already implemented as a metric type in DeepEval, so in practice I'd reach for it there rather than hand-rolling. Good default for grading the *quality* dimension of any open-ended agent output (recaps, listings, summaries).

## Gotchas

- Still an LLM judge — inherits judge-biases (verbosity, position) and must be validated against humans (who-validates-the-validators).
- The probability-weighting trick needs logprob access; not all API endpoints expose it, in which case you fall back to plain form-filling.
- Auto-generated eval steps drift with the model — pin the judge model/version so scores stay comparable over time.

## Source & related

- Primary: Liu et al., "G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment" — https://arxiv.org/abs/2303.16634
- Related: llm-as-judge · judge-biases · two-tool-stack · 01-sources
