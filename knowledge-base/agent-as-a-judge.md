---
title: Agent-as-a-Judge
type: paper
domain: agent-eval
summary: Use an agentic system (not a single LLM call) to evaluate another agent's
  full task-solving trajectory, giving granular per-step feedback; outperforms LLM-as-a-Judge
  on agent tasks where intermediate steps matter.
source: https://arxiv.org/abs/2410.10934
tags:
- eval-kb
- agent-eval
- paper
---
# Agent-as-a-Judge

**TL;DR:** llm-as-judge grades a final answer in one shot. Agent-as-a-Judge gives the *judge* its own tools and agency so it can inspect the whole trajectory — reading intermediate artifacts, checking each requirement — and return step-level feedback instead of a single number.

## What it is

Zhuge et al. (2024), an organic extension of LLM-as-a-Judge. Contemporary eval either looks only at final outcomes (ignoring the step-by-step nature of agents) or needs heavy manual labor. Agent-as-a-Judge closes that gap: an autonomous judge-agent with abilities similar to the agents it evaluates, able to give intermediate feedback across the whole solve.

Proof-of-concept was code generation, with a new benchmark **DevAI** (55 realistic automated AI-dev tasks). Benchmarking three popular agentic systems, Agent-as-a-Judge dramatically outperformed LLM-as-a-Judge — and approached human-evaluator reliability at a fraction of the cost.

## Why it matters / when to use

This is the natural judge for my multi-step repos once they're mature. A single-call judge can't meaningfully grade a CEO run that touched five tools or a game-factory build pipeline — there's too much intermediate state. A judge-agent that can open those artifacts and check them step-by-step is the scalable alternative to me reviewing every run by hand. Pairs directly with trajectory-eval as the *how* behind grading trajectories.

## Gotchas

- **Cost and complexity** — the judge is now itself an agent that can fail, loop, or hallucinate; it needs its own validation (recursion of who-validates-the-validators).
- **Overkill for simple tasks** — if final-answer matching works, don't build an agent to judge it; reserve this for genuinely multi-step, artifact-heavy tasks.
- Still young — treat as a frontier technique to pilot, not a default.

## Source & related

- Primary: Zhuge et al., "Agent-as-a-Judge: Evaluate Agents with Agents" — https://arxiv.org/abs/2410.10934
- Related: trajectory-eval · llm-as-judge · who-validates-the-validators · 01-sources
