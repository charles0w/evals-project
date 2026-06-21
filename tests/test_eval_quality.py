"""Liveness gate: judge() returns a valid score on a known-good input.

Requires ANTHROPIC_API_KEY. Skips cleanly if not configured so CI
on forks (no secrets) stays green without masking real failures.

Run from repo root:
    PYTHONPATH=toolkit python -m unittest discover -s tests -v
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "toolkit"))

from ceo_report import judge

CRITERIA = """\
Grade this end-of-day options/markets recap on:
1. Faithfulness — every number (prices, %, P/L, tickers) is supported by the
   day's actual market data. Penalize ANY invented or unverifiable figure hard.
2. Completeness — covers the day's key movers, the portfolio's positions and
   P/L, and any triggered watch-list levels.
3. Calibration — claims are appropriately hedged; no overconfident directional
   calls stated as fact.
4. Actionability — a reader could act on it: clear next-day levels or flags.
Score 1.0 only if all four hold. Drop fast for hallucinated numbers.
"""

SAMPLE = (
    "EOD recap — 2026-06-04. SPX closed +0.6% at 6,012; NVDA +2.3% into the "
    "close on heavy call flow. Portfolio day P/L +1.8%; held NVDA 6/20 1100C "
    "(+14%) and SPY puts (-5%). Watch level: NVDA 1180 resistance tomorrow; "
    "trim if it gaps above on weak breadth. No earnings in the book this week."
)


class LiveJudgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ev = judge(SAMPLE, CRITERIA)
        if ev["score"] is None:
            raise unittest.SkipTest("judge not configured — set ANTHROPIC_API_KEY")
        cls.ev = ev

    def test_score_in_range(self):
        self.assertGreaterEqual(self.ev["score"], 0.0)
        self.assertLessEqual(self.ev["score"], 1.0)
        self.assertIsInstance(self.ev["summary"], str)
        self.assertGreater(len(self.ev["summary"]), 0)

    def test_score_reasonable(self):
        self.assertGreaterEqual(
            self.ev["score"], 0.5,
            f"score {self.ev['score']} unexpectedly low for a clean sample: {self.ev['summary']}"
        )


if __name__ == "__main__":
    unittest.main()
