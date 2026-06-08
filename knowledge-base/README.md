# Knowledge base

Atomic notes — one concept per file. Each has a dense one-line summary, what it is, why it matters, and the gotchas (where people get it wrong). Read top-down by theme.

## LLM-as-judge & scoring
- [llm-as-judge.md](llm-as-judge.md) — the workhorse technique: score output against a rubric with a strong model
- [g-eval.md](g-eval.md) — chain-of-thought + form-filling scoring; basis of most metric tooling
- [judge-biases.md](judge-biases.md) — position / verbosity / self-preference bias, and the fixes
- [who-validates-the-validators.md](who-validates-the-validators.md) — align the judge to human preference before trusting it
- [longjudgebench.md](longjudgebench.md) — judges are unreliable on long-form output, not just short

## Agent & trajectory evaluation
- [trajectory-eval.md](trajectory-eval.md) — grade the path (tool calls, recovery), not just the final answer
- [pass-k-reliability.md](pass-k-reliability.md) — consistency over k trials; capability ≠ reliability
- [agent-as-a-judge.md](agent-as-a-judge.md) — an agent grades another agent's whole trajectory
- [agent-planning-benchmark.md](agent-planning-benchmark.md) — isolate planning quality from execution

## Datasets, rigor & tooling
- [golden-datasets.md](golden-datasets.md) — the curated, reusable test set; the asset that compounds
- [eval-statistics.md](eval-statistics.md) — sample size & confidence intervals; stop trusting single numbers
- [benchmark-contamination.md](benchmark-contamination.md) — why leaderboard scores inflate; keep your sets private
- [two-tool-stack.md](two-tool-stack.md) — a CI gate + a platform; don't make one tool do both
- [ragas-rag-eval.md](ragas-rag-eval.md) — splitting RAG failures into retrieval vs generation

> Some notes include project-specific "why it matters" examples from the author's own agents — read those as illustrations of the concept, not requirements.
