"""
Offline unit tests for harness/proof_stats.py — stdlib unittest, no deps.

These cover the math the PROOF harness reports (agreement, kappa, Wilson CI,
pass^k, correlation), so the harness's claims are themselves under test.

Run from the repo root:
    python -m unittest discover -s toolkit/tests -v
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "harness"))
import proof_stats as st  # noqa: E402


class AgreementTests(unittest.TestCase):
    def test_perfect(self):
        self.assertEqual(st.agreement_rate([True, False, True], [True, False, True]), 1.0)

    def test_half(self):
        self.assertEqual(st.agreement_rate([True, True], [True, False]), 0.5)

    def test_empty(self):
        self.assertEqual(st.agreement_rate([], []), 0.0)


class ConfusionTests(unittest.TestCase):
    def test_counts_and_rates(self):
        human = [True, True, False, False]
        judge = [True, False, True, False]  # tp, fn, fp, tn
        c = st.confusion(human, judge)
        self.assertEqual((c["tp"], c["fn"], c["fp"], c["tn"]), (1, 1, 1, 1))
        self.assertAlmostEqual(c["precision"], 0.5)
        self.assertAlmostEqual(c["recall"], 0.5)
        self.assertAlmostEqual(c["f1"], 0.5)

    def test_false_pass_is_fp(self):
        # judge passed (True) what human failed (False) -> fp, the dangerous case
        c = st.confusion([False], [True])
        self.assertEqual(c["fp"], 1)


class KappaTests(unittest.TestCase):
    def test_perfect_agreement(self):
        self.assertAlmostEqual(st.cohen_kappa([True, False, True, False],
                                              [True, False, True, False]), 1.0)

    def test_unanimous_identical_is_one(self):
        # both raters say pass for everything -> treat as perfect, not 0/0
        self.assertEqual(st.cohen_kappa([True, True, True], [True, True, True]), 1.0)

    def test_chance_level_near_zero(self):
        # 50/50 raters that agree only at chance -> kappa ~ 0
        human = [True, True, False, False]
        judge = [True, False, True, False]
        self.assertAlmostEqual(st.cohen_kappa(human, judge), 0.0, places=6)

    def test_better_than_chance_positive(self):
        human = [True, True, True, False, False, False]
        judge = [True, True, False, False, False, True]  # 4/6 agree
        self.assertGreater(st.cohen_kappa(human, judge), 0.0)

    def test_empty(self):
        self.assertEqual(st.cohen_kappa([], []), 0.0)


class WilsonTests(unittest.TestCase):
    def test_half_is_symmetric_around_half(self):
        lo, hi = st.wilson_interval(50, 100)
        self.assertAlmostEqual((lo + hi) / 2, 0.5, places=2)
        self.assertLess(lo, 0.5)
        self.assertGreater(hi, 0.5)

    def test_bounds_clamped(self):
        lo, hi = st.wilson_interval(30, 30)  # 100% observed
        self.assertGreaterEqual(lo, 0.0)
        self.assertLessEqual(hi, 1.0)
        self.assertLess(lo, 1.0)  # CI is not degenerate at 1.0

    def test_smaller_n_wider_interval(self):
        lo_small, hi_small = st.wilson_interval(5, 10)
        lo_big, hi_big = st.wilson_interval(50, 100)
        self.assertGreater(hi_small - lo_small, hi_big - lo_big)

    def test_zero_n(self):
        self.assertEqual(st.wilson_interval(0, 0), (0.0, 0.0))


class PassKTests(unittest.TestCase):
    def test_all_consistent_pass(self):
        r = st.passk([[True, True, True], [True, True, True]])
        self.assertEqual(r["k"], 3)
        self.assertAlmostEqual(r["pass_hat_1"], 1.0)
        self.assertAlmostEqual(r["pass_k"], 1.0)

    def test_flaky_item_drops_passk_not_pass1(self):
        # item A always passes; item B passes 2 of 3 -> pass@1 high, pass^3 = 0.5
        r = st.passk([[True, True, True], [True, False, True]])
        self.assertAlmostEqual(r["pass_hat_1"], 5 / 6)
        self.assertAlmostEqual(r["pass_k"], 0.5)

    def test_nonuniform_raises(self):
        with self.assertRaises(ValueError):
            st.passk([[True, True], [True]])

    def test_empty(self):
        r = st.passk([])
        self.assertEqual(r["pass_k"], 0.0)
        self.assertEqual(r["n_items"], 0)


class PearsonTests(unittest.TestCase):
    def test_perfect_positive(self):
        self.assertAlmostEqual(st.pearson([1, 2, 3], [2, 4, 6]), 1.0)

    def test_perfect_negative(self):
        self.assertAlmostEqual(st.pearson([1, 2, 3], [6, 4, 2]), -1.0)

    def test_no_variance_returns_zero(self):
        self.assertEqual(st.pearson([1, 1, 1], [1, 2, 3]), 0.0)

    def test_length_mismatch_returns_zero(self):
        self.assertEqual(st.pearson([1, 2], [1]), 0.0)


if __name__ == "__main__":
    unittest.main()
