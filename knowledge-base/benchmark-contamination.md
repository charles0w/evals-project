---
title: Benchmark Contamination
type: concept
domain: general
summary: "When benchmark test data leaks into a model's training set, its reported\
  \ score reflects memorization, not capability \u2014 why public-leaderboard numbers\
  \ inflate over time. Detected via n-gram overlap, test-slot guessing, and logit/generation\
  \ probes; the reason to keep your own golden sets private."
source: https://github.com/lyy1994/awesome-data-contamination
tags:
- eval-kb
- benchmarks
- concept
---
# Benchmark Contamination

**TL;DR:** If a model saw the test set during training, its score is memorization, not skill. Being able to say "that leaderboard number is contaminated" — and explain how you'd detect it — is high-status eval literacy.

## What it is

Public benchmarks leak into training corpora through benchmark websites, papers quoting examples, and Q&A forums. Two flavors:

- **Verbatim** — the model effectively memorized the test items.
- **Paraphrased** — same content with synonym swaps / reordering; harder to catch, still inflates scores.

Detection methods worth knowing by name: **n-gram / MinHash overlap** between train and test; **Testset Slot Guessing (TS-Guessing)** — mask part of a benchmark item and see if the model completes it; **logit-based** probes (compare log-probs across answer-option orderings); **generation-based** completion checks.

## Why it matters / when to use

Two practical takeaways for me: (1) **distrust leaderboard deltas** — a new model "beating" τ-bench or SWE-bench may just have fresher contamination; weight your own evals over public numbers. (2) **keep golden sets private** — never publish them or paste them into prompts, or you contaminate your *own* future evals. This is also why "contamination-resistant" / dynamically-refreshed benchmarks are emerging.

## Gotchas

- Contamination is rarely all-or-nothing — paraphrased leakage is common and quietly inflates.
- A model can be contaminated on benchmark *format* (not just answers), gaming the eval without knowing content.
- Even private sets erode: once you log results publicly or train on production data that includes eval items, leakage creeps in.

## Source & related

- Primary: Awesome Data Contamination (paper list) — https://github.com/lyy1994/awesome-data-contamination
- Related: golden-datasets · eval-statistics · pass-k-reliability · 01-sources
