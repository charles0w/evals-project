---
title: LLM Judge Biases
type: concept
domain: llm-eval
summary: "Systematic, named failure modes of LLM-as-judge \u2014 position bias (favoring\
  \ the first answer), verbosity bias (rewarding length), and self-preference bias\
  \ (favoring its own outputs) \u2014 each with a standard mitigation; knowing them\
  \ by name is the rigor signal."
source: https://arxiv.org/abs/2306.05685
tags:
- eval-kb
- llm-as-judge
- concept
---
# LLM Judge Biases

**TL;DR:** An LLM judge isn't neutral. It has predictable thumbs-on-the-scale, and each has a known fix. Citing these by name — and mitigating them — is what separates a real eval practitioner from someone who just prompts "rate this 1–10."

## The biases (and fixes)

- **Position bias** — in pairwise judging, the answer shown *first* (or second) wins more often regardless of quality. **Fix:** run both orderings and average, or count a win only if it holds in both.
- **Verbosity / length bias** — longer answers score higher even when no better. **Fix:** rubric line that explicitly says "do not reward length"; control for length in analysis.
- **Self-preference bias** — a model rates its *own* outputs more favorably than a third party would. **Fix:** judge with a *different* model family than the one that produced the output.
- **(Related) sycophancy / leniency** — judges drift toward agreeable, high scores. **Fix:** force a rubric and ask for the failing criterion explicitly.

## Why it matters / when to use

Every repo using llm-as-judge or g-eval is exposed. Concretely: if ai-trading-bot's recap is graded by the same model that wrote it, self-preference inflates the score — so the finance rubric should be judged by a different model. The "penalize hype / don't reward length" line in that rubric is the verbosity-bias guard.

## Gotchas

- Biases compound — a verbose answer shown first is doubly favored.
- Mitigations cost calls (dual-ordering doubles judge cost); budget for it.
- You only *know* a bias is controlled by measuring against human labels (who-validates-the-validators) — mitigations are hypotheses until validated.

## Source & related

- Primary: Zheng et al., MT-Bench / Chatbot Arena (§ on judge biases) — https://arxiv.org/abs/2306.05685
- Related: llm-as-judge · g-eval · who-validates-the-validators · longjudgebench · 01-sources
