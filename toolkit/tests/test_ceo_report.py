"""
Offline unit tests for ceo_report.py — standard library only (`unittest`),
matching the toolkit's no-heavy-deps philosophy. No network, no API keys.

Run from the repo root:
    python -m unittest discover -s toolkit/tests -v
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Make `import ceo_report` work no matter where the test is launched from.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import ceo_report  # noqa: E402


class ClampTests(unittest.TestCase):
    def test_within_range_unchanged(self):
        self.assertEqual(ceo_report._clamp01(0.42), 0.42)

    def test_clamps_above_and_below(self):
        self.assertEqual(ceo_report._clamp01(1.7), 1.0)
        self.assertEqual(ceo_report._clamp01(-0.3), 0.0)

    def test_accepts_int_and_str(self):
        self.assertEqual(ceo_report._clamp01(1), 1.0)
        self.assertEqual(ceo_report._clamp01("0.5"), 0.5)


class ParseJudgeTests(unittest.TestCase):
    def test_plain_json(self):
        out = ceo_report._parse_judge('{"score": 0.8, "summary": "solid"}')
        self.assertEqual(out, {"score": 0.8, "summary": "solid"})

    def test_extracts_json_from_surrounding_prose(self):
        content = 'Here is my verdict:\n{"score": 0.6, "summary": "ok"}\nThanks!'
        out = ceo_report._parse_judge(content)
        self.assertEqual(out["score"], 0.6)
        self.assertEqual(out["summary"], "ok")

    def test_out_of_range_score_is_clamped(self):
        out = ceo_report._parse_judge('{"score": 1.5, "summary": "over"}')
        self.assertEqual(out["score"], 1.0)

    def test_missing_summary_defaults_empty(self):
        out = ceo_report._parse_judge('{"score": 0.3}')
        self.assertEqual(out["summary"], "")

    def test_garbage_raises(self):
        with self.assertRaises(Exception):
            ceo_report._parse_judge("not json at all")


class TrackReliabilityTests(unittest.TestCase):
    def setUp(self):
        # Point the reliability store at an isolated temp file per test.
        self._tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self._tmp.close()
        os.unlink(self._tmp.name)  # start from "no file yet"
        self._orig_store = ceo_report._REL_STORE
        ceo_report._REL_STORE = Path(self._tmp.name)

    def tearDown(self):
        ceo_report._REL_STORE = self._orig_store
        try:
            os.unlink(self._tmp.name)
        except OSError:
            pass

    def test_first_pass_is_full_rate(self):
        self.assertEqual(ceo_report.track_reliability("a", passed=True), 1.0)

    def test_rolling_fraction(self):
        ceo_report.track_reliability("a", passed=True)
        ceo_report.track_reliability("a", passed=False)
        rate = ceo_report.track_reliability("a", passed=True)
        self.assertAlmostEqual(rate, 2 / 3)

    def test_window_truncates_old_runs(self):
        # 8 fails then 1 pass, window=8 -> oldest fail drops out, 1/8 pass.
        for _ in range(8):
            ceo_report.track_reliability("a", passed=False)
        rate = ceo_report.track_reliability("a", passed=True)
        self.assertAlmostEqual(rate, 1 / 8)

    def test_agents_are_isolated(self):
        ceo_report.track_reliability("a", passed=True)
        self.assertEqual(ceo_report.track_reliability("b", passed=False), 0.0)

    def test_persists_to_disk(self):
        ceo_report.track_reliability("a", passed=True)
        on_disk = json.loads(Path(self._tmp.name).read_text())
        self.assertEqual(on_disk["a"], [True])


class JudgeUnconfiguredTests(unittest.TestCase):
    """With no provider env set, judge() must degrade gracefully, not raise."""

    def setUp(self):
        self._saved = (
            ceo_report.JUDGE_PROVIDER, ceo_report.JUDGE_URL,
            ceo_report.JUDGE_KEY, ceo_report.ANTHROPIC_KEY,
        )
        ceo_report.JUDGE_PROVIDER = ""
        ceo_report.JUDGE_URL = ""
        ceo_report.JUDGE_KEY = ""
        ceo_report.ANTHROPIC_KEY = ""

    def tearDown(self):
        (ceo_report.JUDGE_PROVIDER, ceo_report.JUDGE_URL,
         ceo_report.JUDGE_KEY, ceo_report.ANTHROPIC_KEY) = self._saved

    def test_returns_none_score_with_hint(self):
        out = ceo_report.judge("some output", criteria="be good")
        self.assertIsNone(out["score"])
        self.assertIn("judge not configured", out["summary"])


class ReportUnconfiguredTests(unittest.TestCase):
    """With no REPORT_URL/SECRET, report() must no-op to False, not raise."""

    def setUp(self):
        self._saved = (ceo_report.REPORT_URL, ceo_report.REPORT_SECRET)
        ceo_report.REPORT_URL = ""
        ceo_report.REPORT_SECRET = ""

    def tearDown(self):
        ceo_report.REPORT_URL, ceo_report.REPORT_SECRET = self._saved

    def test_noops_to_false(self):
        self.assertFalse(
            ceo_report.report("finance", ok=True, summary="hi", eval_score=0.9)
        )


if __name__ == "__main__":
    unittest.main()
