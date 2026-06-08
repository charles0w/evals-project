---
title: Ragas (RAG Evaluation)
type: tool
domain: rag-eval
summary: "An open-source, reference-free framework for evaluating retrieval-augmented\
  \ generation on four core metrics \u2014 faithfulness, answer relevancy, context\
  \ precision, context recall \u2014 that separately diagnose the retrieval half from\
  \ the generation half of a RAG pipeline."
source: https://github.com/explodinggradients/ragas
tags:
- eval-kb
- rag-eval
- tooling
---
# Ragas (RAG Evaluation)

**TL;DR:** RAG fails in two distinct places — bad retrieval or bad generation — and a single "is the answer good" score can't tell them apart. Ragas splits the diagnosis into four LLM-graded metrics, mostly without needing ground-truth labels.

## What it is

A framework (github explodinggradients/ragas; paper arXiv 2309.15217) for reference-free RAG evaluation. The four core metrics:

- **Faithfulness** — is the answer factually grounded in the retrieved context? (catches hallucination)
- **Answer relevancy** — does the answer actually address the question? (catches off-topic / padded answers)
- **Context precision** — is the retrieved context free of irrelevant noise? (retrieval quality)
- **Context recall** — did retrieval pull *all* the needed context? (retrieval completeness)

Faithfulness + answer relevancy grade the **generation** half; context precision + recall grade the **retrieval** half.

## Why it matters / when to use

Relevant the moment any agent does retrieval over the vault or a corpus — e.g. a CEO `query_journal`-style tool, or any RAG step in the trading/research bots. When answers are wrong, Ragas tells me *which half* to fix: low faithfulness → tighten generation/prompt; low context recall → fix the retriever. It slots into the CI-gate role of the two-tool-stack for RAG-specific checks.

## Gotchas

- The metrics are themselves LLM-judged — inherits judge-biases and needs validation (who-validates-the-validators).
- "Reference-free" is convenient but context recall still benefits from some ground-truth; don't assume zero labeling.
- RAG-specific — it grades retrieval+generation, not multi-step agent trajectories (use trajectory-eval for those).

## Source & related

- Primary: Ragas — https://github.com/explodinggradients/ragas · paper https://arxiv.org/abs/2309.15217
- Related: two-tool-stack · llm-as-judge · judge-biases · 01-sources
