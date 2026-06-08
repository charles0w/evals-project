---
agent: social
tags:
- ai-evals
- criteria
- social
---
# Criteria — Social Post

Rubric for grading AI-generated social content / trend posts before scheduling.

```text
Grade this AI-generated social post on:
1. Factual safety — any claim (trend stat, product fact, "X is going viral") is
   true or clearly framed as opinion. Penalize hallucinated trends or invented
   numbers hard — a false viral claim is a credibility hit.
2. Hook — the first line earns the scroll-stop; not generic.
3. Platform fit — length, format, and tone match the target platform's norms.
4. Brand safety — no policy-violating, offensive, or off-brand content; no
   unlicensed/again-stereotyped material.
5. Clarity + CTA — the post has a point and (where relevant) a clear next action.
Score 1.0 only if factually safe AND brand-safe AND has a real hook. Drop fast for
hallucinated trend claims or policy risk.
```

- **Threshold:** 0.7.
- **Judge model:** different family than the post generator.
- **Why these axes:** factual safety + brand safety are gates — a false or off-brand post at scale is a reputation cost that outweighs any single engagement win.

## Changelog

- 2026-06-04 — initial rubric.

## See also

- llm-as-judge · judge-biases · README
