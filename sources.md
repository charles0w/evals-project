---
tags:
- research
- ai-evals
- sources
---
# 01 — Curated eval sources

The ingestion list for the evals depth track. Deliberately short. Curation is the value — these are the sources with genuine signal, not an exhaustive dump. Read top-down: a few people, the paper canon, the tool stack, the benchmarks to know.

## Start here (the 3 anchors)

If I only read three things before anything else:

1. **Hamel Husain — "LLM Evals: Everything You Need to Know"** (the evals FAQ). The single best practitioner's-eye overview of the whole discipline. → https://hamel.dev/blog/posts/evals-faq/
2. **"What We Learned From a Year of Building with LLMs"** — the applied-LLMs collective (Yan, Bischof, Frye, Husain, Liu, Shankar). The eval sections are the field's common-sense baseline. → https://applied-llms.org/
3. **Shankar et al. — "Who Validates the Validators?"** The paper that makes you rigorous about LLM-as-judge instead of naive. → https://arxiv.org/abs/2404.12272

## People worth following (the few)

The whole point of depth is to follow a small, high-signal set — not 30 newsletters.

| Person | Where | Why they matter |
|---|---|---|
| **Hamel Husain** | [hamel.dev](https://hamel.dev/) | The #1 evals voice for practitioners. Ex-GitHub/Airbnb ML. Writes the canonical how-to material; co-teaches the top evals course. |
| **Shreya Shankar** | [sh-reya.com](https://www.sh-reya.com/) | The research rigor side. UC Berkeley PhD; LLM-as-judge alignment, DocETL. Pairs with Hamel — theory to his practice. |
| **Eugene Yan** | [eugeneyan.com](https://eugeneyan.com/) | Applied, pragmatic eval + LLM-system patterns from someone shipping at scale. Excellent writing, high frequency. |
| **Lenny + Hamel/Shreya podcast** | [Lenny's Newsletter](https://www.lennysnewsletter.com/p/why-ai-evals-are-the-hottest-new-skill) | "Why AI evals are the hottest new skill." Good for the strategic/positioning framing — confirms the edge thesis. |

> Deliberately *not* on this list: the 1–2M-subscriber daily news briefs. No edge in what everyone reads.

## Foundational papers (the canon)

The papers that define how the field thinks about measuring quality. Skim abstracts first; deep-read the ones that hit your current build.

| Paper | What it gives you |
|---|---|
| **Zheng et al. — Judging LLM-as-a-Judge with MT-Bench & Chatbot Arena** ([2306.05685](https://arxiv.org/abs/2306.05685)) | The canonical LLM-as-judge paper. Where the whole technique starts. |
| **Liu et al. — G-Eval** ([2303.16634](https://arxiv.org/abs/2303.16634)) | Chain-of-thought + GPT-4 scoring for NLG; the basis for most modern metric tooling. |
| **Shankar et al. — Who Validates the Validators?** ([2404.12272](https://arxiv.org/abs/2404.12272)) | Aligning LLM-assisted eval with human preference. Stops you from trusting a judge you never validated. |
| **Yao et al. — τ-bench (tool-agent-user)** ([2406.12045](https://arxiv.org/abs/2406.12045)) | The canonical *agent reliability* benchmark. Measures consistency across multi-turn tool use — your core domain. |
| **Zhuge et al. — Agent-as-a-Judge** ([2410.10934](https://arxiv.org/abs/2410.10934)) | Using an agent to grade an agent's *whole trajectory*, not just the final answer. The frontier of agent eval. |
| **Survey — Evaluation of LLM-based Agents** ([2503.16416](https://arxiv.org/abs/2503.16416)) | Map of the entire agent-eval landscape. Best single orientation document. |

**Trajectory-eval concepts to know by name:** T-Eval (next-tool-call alignment), AgentBoard "Progress Rate" (actual vs. expected trajectory), Agent-as-a-Judge (granular step feedback). These are what separate agent evals from plain LLM evals.

## The tool stack (canonical)

The practical lesson from the field: **you need two tools** — a lightweight CI/CD gate *and* a platform for human annotation + regression tracking + dashboards. Don't try to make one tool do both.

| Layer | Tools | Notes |
|---|---|---|
| **CI / code-native gating** | [promptfoo](https://www.promptfoo.dev/), [DeepEval](https://github.com/confident-ai/deepeval), [Ragas](https://github.com/explodinggradients/ragas) (RAG-specific) | promptfoo = YAML assertions + red-teaming (acquired by OpenAI, March 2026; core stays MIT/open). DeepEval = pytest-native, 50+ metrics incl. G-Eval. |
| **Platform / observability + regression** | [Braintrust](https://www.braintrust.dev/), [Langfuse](https://langfuse.com/) (OSS), [Arize Phoenix](https://phoenix.arize.com/), LangSmith | Braintrust = full lifecycle incl. prod monitoring. Langfuse = OSS, framework-agnostic, observability-first. |
| **Public-sector / rigorous** | [Inspect AI](https://inspect.aisi.org.uk/) (UK AISI), [OpenAI Evals](https://github.com/openai/evals) | Inspect is the serious open framework for structured, reproducible evals. |

Starter pairing for my repos: **DeepEval (CI gate) + Braintrust or Langfuse (platform).**

## Benchmarks to know (literacy, not leaderboard-chasing)

Knowing *why a benchmark is flawed* is high-status signal — being able to say "that leaderboard is contaminated" beats memorizing scores.

- **τ-bench / τ²-bench** — tool-agent-user reliability (my domain).
- **GAIA** ([2311.12983](https://arxiv.org/abs/2311.12983)) — general assistant, short-answer matching.
- **SWE-bench** ([2310.06770](https://arxiv.org/abs/2310.06770)) — coding agents on real GitHub issues.
- **WebArena / WebVoyager / OSWorld** — computer-use & web agents.
- Watch for: contamination, gaming, and single-number reporting off tiny samples (the rigor gap most people fall into).

## Course / long-form (when ready to go all-in)

- **AI Evals for Engineers & PMs** — Hamel Husain & Shreya Shankar, [Maven](https://maven.com/parlance-labs/evals). The field's most popular course (trained teams at OpenAI/Anthropic).
- **Evals for AI Engineers** — the O'Reilly book version of the above.

## How this feeds the database

Ingest People + Foundational + Tools changelogs → dedupe (same paper covered five ways) → extract the *delta* into structured notes here. This list is the seed; README has the depth → proof → distribution path.
