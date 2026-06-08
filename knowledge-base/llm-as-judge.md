---
title: LLM-as-a-Judge
type: technique
domain: llm-eval
summary: Use a strong LLM to grade model outputs against a rubric instead of relying
  on exact-match or human review; cheap and scalable, but biased and must be validated
  against human labels first.
source: https://arxiv.org/abs/2306.05685
tags:
- eval-kb
- llm-as-judge
---
# LLM-as-a-Judge

**TL;DR:** Have a capable model score outputs against a rubric. It's the workhorse of modern evals — scalable and cheap where exact-match fails — but it carries systematic biases and is worthless until you've checked it agrees with human judgment.

## What it is

Instead of grading a generated answer with string matching (impossible for open-ended output) or humans (too slow/expensive at scale), you prompt a strong LLM with the output + a rubric and ask for a score or a verdict. Two main forms:

- **Pointwise** — score one output on a scale (e.g. 1–5 on faithfulness). Easy, but scales are noisy and poorly calibrated.
- **Pairwise** — given two outputs, pick the better one. More reliable; underpins Chatbot Arena-style ranking.

Introduced rigorously in Zheng et al.'s MT-Bench / Chatbot Arena paper, which showed a strong judge model can approximate human preference at ~80%+ agreement — comparable to human-human agreement.

## Why it matters / when to use

This is the technique you'll lean on for almost every subjective quality check across my repos: "is this product listing good?" (shopify-arbitrage), "is this trade rationale sound?" (ai-trading-bot), "did the agent answer the user's actual question?" (CEO). Anywhere there's no gold string to match, an LLM judge is the default.

## Gotchas

The biases are real and named — knowing them is the depth signal:

- **Position bias** — pairwise judges favor whichever answer is shown first. Mitigate by running both orderings and averaging.
- **Verbosity bias** — judges reward longer answers regardless of quality.
- **Self-preference bias** — a model judges its own outputs more favorably.
- **Calibration** — never trust raw scores until you've measured judge-vs-human agreement on a labeled subset. An unvalidated judge is just a confident guess (see who-validates-the-validators).

## Source & related

- Primary: Zheng et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" — https://arxiv.org/abs/2306.05685
- Related: who-validates-the-validators · agent-as-a-judge · 01-sources
