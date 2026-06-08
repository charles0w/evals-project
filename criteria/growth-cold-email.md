---
agent: growth
tags:
- ai-evals
- criteria
- growth
---
# Criteria — Growth Cold Email

Rubric for grading berkeley-biz-websites cold outreach emails before they send. A bad cold email isn't just ignored — it burns the domain's deliverability, so quality gating here protects the whole channel.

```text
Grade this cold outreach email (to a local business with no/weak website) on:
1. Personalization — references the SPECIFIC business (name, type, actual gap
   like "no website / outdated site"). Penalize generic mail-merge that could go
   to anyone. Wrong business name is an automatic low score.
2. Accuracy — every claim about their current situation is true and verifiable.
   No invented facts about their business.
3. Value + CTA — states a clear, concrete value prop and ONE low-friction call to
   action (see the demo, quick reply). No vague "let's hop on a call" with no hook.
4. Tone — helpful peer, not salesy or desperate; concise (a busy owner skims it).
5. Deliverability — avoids spam-trigger patterns (ALL CAPS, "FREE!!!", excessive
   links, misleading subject). Plain, human, specific.
Score 1.0 only if personalized AND accurate AND non-spammy. Drop fast for wrong
business details or generic templates.
```

- **Threshold:** 0.75 (deliverability-protective).
- **Judge model:** different family than the email generator.
- **Why these axes:** personalization + accuracy drive reply rate; deliverability protects the sending domain across the whole batch — one spammy pattern hurts every future send.

## Changelog

- 2026-06-04 — initial rubric.

## See also

- llm-as-judge · judge-biases · README
