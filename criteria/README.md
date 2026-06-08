---
tags:
- ai-evals
- criteria
---
# Eval criteria library

Versioned rubrics — one per fleet agent — that feed the `judge()` call in each agent's reporter (see the fleet quality layer). Keeping the rubric *here*, versioned, instead of hard-coded in agent code means: one place to sharpen as I learn what "good" means (criteria drift is expected), and a shared definition across the dashboard, CI, and any future agent.

## Rubrics

| Agent (fleet id) | Rubric | Owner repo |
|---|---|---|
| `finance` | finance-eod-recap | ai-trading-bot |
| `commerce` | commerce-listing | shopify-arbitrage / card-arbitrage |
| `growth` | growth-cold-email | berkeley-biz-websites |
| `social` | social-post | (social agent) |

## How a rubric is used

```python
from ceo_report import judge, track_reliability, report
# paste the CRITERIA string from the relevant note below
ev  = judge(agent_output, criteria=CRITERIA)
rel = track_reliability("<agent-id>", passed=ev["score"] >= THRESHOLD)
report("<agent-id>", ok=True, summary=headline,
       eval_score=ev["score"], eval_reliability=rel, eval_summary=ev["summary"])
```

## Conventions

- **Judge with a different model family** than the one that produced the output — avoids self-preference (judge-biases).
- **Validate before trusting** — hand-grade a sample, confirm judge agreement (who-validates-the-validators), then set the threshold.
- **Version on change** — bump the note's `updated` and add a one-line changelog entry when you edit a rubric, so dashboard score shifts are explainable.

## See also

- README · llm-as-judge · eval-integration
