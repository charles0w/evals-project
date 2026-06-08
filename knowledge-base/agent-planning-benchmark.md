---
title: Agent Planning Benchmark (APB)
type: benchmark
domain: agent-eval
summary: "A planning-specific diagnostic benchmark (4,209 cases, 22 domains) that\
  \ isolates an agent's planning quality \u2014 goal decomposition, tool selection,\
  \ calibrated refusal \u2014 separately from execution, so end-to-end failure no\
  \ longer hides whether the plan or the action was at fault."
source: https://arxiv.org/abs/2606.04874
tags:
- eval-kb
- agent-eval
- benchmark
---
# Agent Planning Benchmark (APB)

**TL;DR:** Most agent benchmarks only report end-to-end success, which blurs *why* a run failed. APB grades the **plan itself** — decomposition, tool choice, knowing when to refuse — as an upstream signal, separate from execution.

## What it is

A diagnostic framework (arXiv 2606.04874, June 2026): 4,209 cases across 22 domains and five settings, covering holistic planning, feedback-conditioned step-wise planning, and robustness under extraneous tools, broken tools, and unsolvable tasks. Across 12 models it exposes systematic weakness in long-horizon planning, tool-noise robustness, and calibrated refusal. The authors validate it as an *upstream complement* to execution benchmarks — APB-guided refinement improved plan correctness and downstream execution on ToolSandbox and τ²-bench tasks.

## Why it matters / when to use

Directly relevant to my reliability work. When an agent (CEO, game-factory, the trading bots) fails a multi-step task, APB-style thinking lets me ask "was the plan bad or the execution bad?" — the diagnostic split that makes debugging tractable. Pairs with trajectory-eval (grading the path) and pass-k-reliability (consistency of the path).

## Gotchas

- Scores plan *quality*, not task completion — a high plan grade is an upstream signal, **not** a guarantee of execution success. Complements, doesn't replace, τ-bench-style end-to-end runs.
- Cases are multimodal (MLLM-oriented), so scores may not transfer cleanly to text-only agents.

## Source & related

- Primary: "Agent Planning Benchmark: A Diagnostic Framework for Planning Capabilities in LLM Agents" — https://arxiv.org/abs/2606.04874
- Related: trajectory-eval · pass-k-reliability · 01-sources
