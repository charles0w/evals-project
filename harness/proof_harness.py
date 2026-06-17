#!/usr/bin/env python3
"""
proof_harness.py — the Week-4 PROOF harness (learning-path.md).

The depth -> proof step: take ONE bot behavior (ai-trading-bot's signal
rationale), build a hand-labeled golden set, run an LLM judge over it, and
then do the part almost everyone skips: VALIDATE THE JUDGE against the human
labels before trusting a single score (who-validates-the-validators), and
report pass^k reliability — not just an average — with confidence intervals.

Two subcommands:

    python proof_harness.py validate            # judge vs human labels
    python proof_harness.py passk --k 5          # reliability on identical inputs

Provider: reuses toolkit/ceo_report.judge() — set ANTHROPIC_API_KEY or
EVAL_JUDGE_URL/KEY (see .env.example). IMPORTANT: judge with a DIFFERENT model
family than the one that wrote the rationales (self-preference bias).

No keys handy? Add --mock to run a deterministic pseudo-judge so the pipeline
and the statistics are demonstrable offline. Mock numbers are illustrative
only — they are NOT a validation of any real judge.

Swap in real data: replace golden_signals.jsonl with your own hand-labeled
signals (same fields). That labeled set — not this code — is the durable asset.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

# Reuse the toolkit's provider-aware judge.
_TOOLKIT = Path(__file__).resolve().parent.parent / "toolkit"
sys.path.insert(0, str(_TOOLKIT))
from ceo_report import judge as real_judge  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import proof_stats as st  # noqa: E402

GOLDEN = Path(__file__).resolve().parent / "golden_signals.jsonl"
DEFAULT_THRESHOLD = 0.7  # from criteria/finance-eod-recap.md

# Rubric adapted from criteria/finance-eod-recap.md, with the explicit
# SOURCE DATA verification step that the criteria note flags as the fix for
# "faithfulness needs ground truth" — the judge can only check numbers it's given.
CRITERIA = """\
Grade this trading-signal RATIONALE against the SOURCE DATA provided with it.
1. Faithfulness — every number (prices, %, P/L, tickers, dates, levels) must be
   supported by the SOURCE DATA. Penalize ANY invented, contradicted, or
   unverifiable figure hard. This axis dominates.
2. Completeness — accounts for the relevant positions and movers in the data;
   omitting a held losing position is a major gap.
3. Calibration — claims are appropriately hedged; no overconfident directional
   calls stated as fact ("guaranteed", "can't lose"). Reward reasoning, penalize hype.
4. Actionability — a reader could act on it: a clear next-day level or flag.
Score 1.0 only if all four hold. Drop fast for hallucinated numbers or claims
that contradict the SOURCE DATA.
"""


def load_golden(path=GOLDEN):
    items = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            items.append(json.loads(line))
    return items


def _payload(item):
    """The text handed to the judge: the rationale plus its ground-truth data."""
    return (
        f"SIGNAL: {item['signal']}\n\n"
        f"SOURCE DATA (ground truth — verify every figure against this):\n"
        f"{item['market_data']}\n\n"
        f"RATIONALE TO GRADE:\n{item['rationale']}"
    )


def _mock_score(item, run_idx=0):
    """Deterministic stand-in judge: centers on the human score with seeded
    noise, so borderline items realistically flip across runs. Demo only."""
    h = int(hashlib.sha256(f"{item['id']}:{run_idx}".encode()).hexdigest(), 16)
    noise = ((h % 1000) / 1000.0 - 0.5) * 0.30  # +/- 0.15
    return max(0.0, min(1.0, item["human_score"] + noise))


def score_item(item, *, mock, run_idx=0):
    """Return a judge score in 0..1 for one item (real judge or mock)."""
    if mock:
        return _mock_score(item, run_idx)
    ev = real_judge(_payload(item), CRITERIA)
    return ev["score"]


def _bar(frac, width=24):
    fill = int(round(frac * width))
    return "#" * fill + "-" * (width - fill)


def cmd_validate(args):
    items = load_golden()
    if args.limit:
        items = items[: args.limit]
    thr = args.threshold

    human_pass, judge_pass = [], []
    human_raw, judge_raw = [], []
    misses = []  # disagreements, the rows worth re-reading by hand

    for it in items:
        s = score_item(it, mock=args.mock)
        if s is None:
            print("Judge not configured — set ANTHROPIC_API_KEY or "
                  "EVAL_JUDGE_URL/KEY, or pass --mock for an offline demo.")
            return 2
        hp = bool(it["human_pass"])
        jp = s >= thr
        human_pass.append(hp)
        judge_pass.append(jp)
        human_raw.append(float(it["human_score"]))
        judge_raw.append(float(s))
        if hp != jp:
            misses.append((it, s))

    n = len(items)
    agree = st.agreement_rate(human_pass, judge_pass)
    kappa = st.cohen_kappa(human_pass, judge_pass)
    conf = st.confusion(human_pass, judge_pass)
    lo, hi = st.wilson_interval(sum(1 for h, j in zip(human_pass, judge_pass) if h == j), n)
    corr = st.pearson(human_raw, judge_raw)

    print(f"\n=== JUDGE VALIDATION {'(MOCK — illustrative only)' if args.mock else ''} ===")
    print(f"golden set        : {n} hand-labeled signal rationales")
    print(f"pass threshold    : {thr}")
    print(f"human pass rate    : {sum(human_pass)}/{n}")
    print(f"judge pass rate    : {sum(judge_pass)}/{n}")
    print("-" * 52)
    print(f"agreement          : {agree:.1%}  [{_bar(agree)}]")
    print(f"  95% CI (Wilson)  : [{lo:.1%}, {hi:.1%}]")
    print(f"Cohen's kappa      : {kappa:.2f}  ({_kappa_label(kappa)})")
    print(f"score correlation  : {corr:.2f}  (Pearson, raw 0..1)")
    print(f"confusion (pass=+) : tp={conf['tp']} tn={conf['tn']} "
          f"fp={conf['fp']} fn={conf['fn']}")
    print(f"  precision/recall : {conf['precision']:.2f} / {conf['recall']:.2f}")
    print("-" * 52)
    # The dangerous error for a trading bot: judge waves through a bad signal.
    print(f"FALSE PASSES (judge OK'd a human-failed signal): {conf['fp']}")
    if misses:
        print("\nDisagreements to re-grade by hand (criteria drift lives here):")
        for it, s in misses:
            kind = "FALSE-PASS" if (s >= thr and not it["human_pass"]) else "false-fail"
            print(f"  [{kind}] {it['id']}  judge={s:.2f} human={it['human_score']:.2f}"
                  f"  ({it['failure_mode']})")

    print("\nVERDICT:", _verdict(kappa, conf, args.mock))
    return 0


def cmd_passk(args):
    items = load_golden()
    if args.limit:
        items = items[: args.limit]
    thr, k = args.threshold, args.k

    per_item, flaky = [], []
    for it in items:
        runs = []
        for r in range(k):
            s = score_item(it, mock=args.mock, run_idx=r)
            if s is None:
                print("Judge not configured — set a key or pass --mock.")
                return 2
            runs.append(s >= thr)
        per_item.append(runs)
        if any(runs) and not all(runs):  # inconsistent on an identical input
            flaky.append((it, runs))

    res = st.passk(per_item)
    n = res["n_items"]
    lo, hi = st.wilson_interval(sum(1 for r in per_item if all(r)), n)

    print(f"\n=== pass^k RELIABILITY {'(MOCK — illustrative only)' if args.mock else ''} ===")
    print(f"items x runs       : {n} x {k} = {n * k} judged inputs")
    print(f"pass@1 (capability): {res['pass_hat_1']:.1%}  [{_bar(res['pass_hat_1'])}]")
    print(f"pass^{k} (reliability): {res['pass_k']:.1%}  [{_bar(res['pass_k'])}]")
    print(f"  95% CI (Wilson)  : [{lo:.1%}, {hi:.1%}]")
    print(f"inconsistent items : {len(flaky)}/{n} flipped across identical runs")
    if flaky:
        print("\nFlaky (the reliability gap you can't see in an average):")
        for it, runs in flaky:
            seq = "".join("P" if x else "." for x in runs)
            print(f"  {it['id']}  [{seq}]  human={it['human_score']:.2f}")
    print("\nNOTE: capability != reliability. The gap between pass@1 and "
          f"pass^{k} is what makes a pipeline (un)trustable with capital.")
    return 0


def _kappa_label(k):
    if k >= 0.8:
        return "almost perfect"
    if k >= 0.6:
        return "substantial"
    if k >= 0.4:
        return "moderate"
    if k >= 0.2:
        return "fair"
    return "poor — do NOT trust this judge yet"


def _verdict(kappa, conf, mock):
    if mock:
        return ("MOCK run — this validates the harness math, not a real judge. "
                "Re-run with a real key (different model family) to trust scores.")
    if kappa >= 0.6 and conf["fp"] == 0:
        return "Judge is trustworthy for gating (kappa substantial, no false-passes)."
    if conf["fp"] > 0:
        return (f"NOT yet trustworthy — {conf['fp']} false-pass(es): the judge waved "
                "through signals you failed. Tighten the rubric and re-validate.")
    return ("Borderline — kappa below 0.6. Sharpen the criteria on the "
            "disagreements above, re-label if your notion of 'good' drifted, re-run.")


def main():
    p = argparse.ArgumentParser(description="Week-4 PROOF harness for ai-trading-bot signal rationales.")
    sub = p.add_subparsers(dest="cmd", required=True)

    pv = sub.add_parser("validate", help="judge the golden set, measure agreement vs human labels")
    pv.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    pv.add_argument("--mock", action="store_true", help="deterministic offline pseudo-judge")
    pv.add_argument("--limit", type=int, default=0, help="only the first N items")
    pv.set_defaults(func=cmd_validate)

    pk = sub.add_parser("passk", help="run the judge k times per item, report pass^k")
    pk.add_argument("--k", type=int, default=5)
    pk.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    pk.add_argument("--mock", action="store_true", help="deterministic offline pseudo-judge")
    pk.add_argument("--limit", type=int, default=0, help="only the first N items")
    pk.set_defaults(func=cmd_passk)

    args = p.parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
