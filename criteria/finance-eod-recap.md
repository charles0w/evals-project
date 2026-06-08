---
agent: finance
tags:
- ai-evals
- criteria
- finance
---
# Criteria — Finance EOD Recap

Canonical rubric for grading ai-trading-bot's end-of-day recap. Referenced by the reporting block; this note is the source of truth.

```text
Grade this end-of-day options/markets recap on:
1. Faithfulness — every number (prices, %, P/L, tickers) is supported by the
   day's actual market data. Penalize ANY invented or unverifiable figure hard.
2. Completeness — covers the day's key movers, the portfolio's positions and
   P/L, and any triggered watch-list levels. Missing a held position is a major gap.
3. Calibration — claims are appropriately hedged; no overconfident directional
   calls stated as fact. Reward reasoning, penalize hype.
4. Actionability — a reader could act on it: clear next-day levels or flags.
Score 1.0 only if all four hold. Drop fast for hallucinated numbers.
```

- **Threshold:** 0.7 (tune after validating).
- **Judge model:** use a different family than the recap generator (self-preference).
- **Why these axes:** finance is the highest-stakes fleet output — a hallucinated number is the costliest failure, so faithfulness is weighted hardest.

## Known issue — faithfulness needs source data

First live run (2026-06-04) scored a sample recap **0.15**: the judge correctly refused to trust any number because it had **no market data to verify against** ("cannot be evaluated against actual market data"). An LLM judge with no ground truth can only assess *internal consistency*, not factual faithfulness. Fix before relying on the faithfulness axis:

- **Preferred:** pass the day's actual prices/positions to `judge()` alongside the recap, so it can actually check the numbers.
- **Or:** reframe criterion 1 to "internally consistent and appropriately hedged" if source data isn't supplied.

This is who-validates-the-validators in practice — validate the judge before trusting its scores.

## Changelog

- 2026-06-04 — initial rubric; flagged faithfulness-needs-source-data after first live run.

## See also

- eval-reporting · llm-as-judge · README
