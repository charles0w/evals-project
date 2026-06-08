---
title: Trajectory Evaluation
type: concept
domain: agent-eval
summary: Grade an agent's step-by-step path (tool calls, recovery, progress toward
  goal) rather than only its final answer; this is what separates agent eval from
  plain LLM eval.
source: https://arxiv.org/abs/2503.16416
tags:
- eval-kb
- agent-eval
- trajectory
---
# Trajectory Evaluation

**TL;DR:** An agent can reach the right answer by luck through a terrible path, or fail a good run on the last step. Trajectory eval scores the *process* — were the tool calls correct, did it recover from errors, did each step advance the goal — not just the outcome.

## What it is

Final-answer eval treats the agent as a black box: right or wrong. But agents are multi-step, and outcome-only scoring hides where and why they fail. Trajectory eval opens the box. Key named approaches:

- **T-Eval** — at each step, measure how closely the agent's predicted next tool call matches the expected one, isolating decision quality from downstream noise.
- **AgentBoard "Progress Rate"** — compares the actual trajectory against an expected one for a fine-grained measure of how far the agent advanced, even on tasks it ultimately failed.
- **Agent-as-a-Judge** — an agent grades the whole trajectory with granular per-step feedback (see agent-as-a-judge).

## Why it matters / when to use

This is my core domain — almost every repo is agentic. For ai-trading-bot, "did it make money" is outcome eval; "did it correctly pull the data, apply the thesis, and size the position" is trajectory eval — and the second one tells me whether a win was skill or luck. For game-factory and CEO, trajectory eval is the only way to debug *why* a multi-step run went wrong.

## Gotchas

- **You need expected trajectories** — defining the "gold path" is labor; sometimes multiple paths are valid, so rigid path-matching over-penalizes creativity.
- **Outcome and progress can diverge** — high progress rate with task failure (or vice versa) is the interesting signal, not noise; report both.
- Don't conflate trajectory eval with logging. Tracing shows you the path; trajectory eval *scores* it against an expectation.

## Source & related

- Primary: Survey — "Evaluation of LLM-based Agents" — https://arxiv.org/abs/2503.16416
- Related: agent-as-a-judge · pass-k-reliability · 01-sources
