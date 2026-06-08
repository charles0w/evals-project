"""
backtest.py — honest walk-forward backtester that reuses the live grading rule.

It replays a SIGNAL strategy over historical prices and grades each call exactly
the way sync_dashboard.py grades live predictions (same direction/NOISE/return
rule, same record shape), so a backtest result is directly comparable to the
forward loop. The whole point is to find out if a signal has edge *before*
trusting it — and to do so without fooling yourself.

ANTI-SELF-DECEPTION (the rigor that makes a backtest worth anything):
  • No lookahead — the strategy only ever sees prices up to the decision day;
    the exit price (decision day + horizon) is used ONLY for grading.
  • Baseline — every result is reported against the base rate of up-moves over
    the same windows, plus a significance test vs that baseline. An edge that
    isn't bigger than the baseline + noise is not an edge.
  • Out-of-sample — metrics are split into in-sample (tune here) and
    out-of-sample (the only number that counts). Don't tune on OOS.
  • Costs — a per-trade cost (bps) is subtracted from every trade; a backtest
    with zero costs lies.
  • Caveats it CANNOT fix: survivorship bias (yfinance only has tickers that
    still exist) and multiple-comparisons (run 50 strategies, one looks great by
    chance — see knowledge-base/benchmark-contamination.md).

Requires: pip install yfinance pandas
Run:      python backtest.py
"""
from __future__ import annotations
import math
import statistics
import datetime as dt

# ── config ──────────────────────────────────────────────────────────────
UNIVERSE = ["SPY", "QQQ", "NVDA", "AAPL", "MSFT", "AMD", "AVGO", "TSLA", "AMZN", "META", "NFLX"]
START, END = "2021-01-01", "2026-06-01"
HORIZON = 5            # trading days held (mirror predictions.jsonl)
NOISE = 0.01           # 1% band: smaller moves count as flat, not a hit (mirror grading)
COST_BPS = 5           # round-trip cost per trade, basis points (0.05%)
TRAIN_END = "2024-06-01"   # everything after this is OUT-OF-SAMPLE (the real test)


# ── data ────────────────────────────────────────────────────────────────
def download_close(tickers, start, end):
    import yfinance as yf
    df = yf.download(tickers, start=start, end=end, progress=False, auto_adjust=True)
    close = df["Close"] if "Close" in df else df
    return close.dropna(how="all")


# ── strategies ──────────────────────────────────────────────────────────
# A strategy sees ONLY history up to `date` and returns calls:
#   [(ticker, "up"|"down", conviction "low"|"medium"|"high"), ...]

def strat_dip_reversion(date, hist):
    """Hypothesis: a big 1-day drop mean-reverts. Buy names down >=4% on the day."""
    if len(hist) < 2:
        return []
    last, prev = hist.iloc[-1], hist.iloc[-2]
    calls = []
    for t in hist.columns:
        if math.isnan(last[t]) or math.isnan(prev[t]) or prev[t] == 0:
            continue
        r = last[t] / prev[t] - 1
        if r <= -0.04:
            calls.append((t, "up", "high" if r <= -0.07 else "medium"))
    return calls

def strat_momentum(date, hist):
    """Hypothesis: 1-day strength continues. Predict up on names up >=4% on the day."""
    if len(hist) < 2:
        return []
    last, prev = hist.iloc[-1], hist.iloc[-2]
    return [(t, "up", "medium") for t in hist.columns
            if not math.isnan(last[t]) and not math.isnan(prev[t]) and prev[t] and last[t]/prev[t]-1 >= 0.04]

def strat_baseline_spy(date, hist):
    """Naive benchmark: always 'SPY up'. The bar any real signal must clear."""
    return [("SPY", "up", "low")] if "SPY" in hist.columns else []

STRATEGY = strat_dip_reversion   # <- swap to test a different hypothesis


# ── grading (mirrors sync_dashboard.py) ─────────────────────────────────
def grade_call(direction, entry, exit_):
    if entry is None or exit_ is None or entry == 0:
        return None
    ret = exit_ / entry - 1
    realized = ret if direction == "up" else -ret          # directional PnL
    realized -= COST_BPS / 10000.0                          # subtract trade cost
    correct = ret > NOISE if direction == "up" else ret < -NOISE
    return {"ret": ret, "realized": realized, "correct": bool(correct)}


# ── walk-forward engine ─────────────────────────────────────────────────
def run(close, strategy, horizon=HORIZON):
    dates = list(close.index)
    records = []
    for i in range(1, len(dates) - horizon):       # need a prior day + a future exit
        d = dates[i]
        hist = close.iloc[: i + 1]                  # data through day d ONLY (no lookahead)
        for ticker, direction, conviction in strategy(d, hist):
            entry = close[ticker].iloc[i]
            exit_ = close[ticker].iloc[i + horizon]
            g = grade_call(direction, float(entry), float(exit_))
            if g is None:
                continue
            records.append({"date": d.date().isoformat(), "ticker": ticker,
                            "direction": direction, "conviction": conviction, **g})
    return records


def base_rate(close, horizon=HORIZON):
    """Base rate of an up-move (> NOISE) over the same horizon across the universe — the naive benchmark."""
    dates = list(close.index)
    ups = tot = 0
    for i in range(1, len(dates) - horizon):
        for t in close.columns:
            e, x = close[t].iloc[i], close[t].iloc[i + horizon]
            if math.isnan(e) or math.isnan(x) or e == 0:
                continue
            tot += 1
            if x / e - 1 > NOISE:
                ups += 1
    return ups / tot if tot else 0.0


# ── metrics + significance ──────────────────────────────────────────────
def _p_two_sided(z):
    return math.erfc(abs(z) / math.sqrt(2))    # normal-approx two-sided p-value

def summarize(records, baseline_p, label):
    n = len(records)
    if n == 0:
        print(f"\n[{label}] no trades.")
        return
    hits = sum(r["correct"] for r in records)
    hit = hits / n
    avg_real = statistics.mean(r["realized"] for r in records)
    cum = sum(r["realized"] for r in records)            # equal-size, sequential
    # significance of hit-rate vs the base rate (binomial normal approx)
    se = math.sqrt(baseline_p * (1 - baseline_p) / n) if 0 < baseline_p < 1 else float("nan")
    z = (hit - baseline_p) / se if se and not math.isnan(se) else float("nan")
    p = _p_two_sided(z) if not math.isnan(z) else float("nan")
    print(f"\n[{label}]  trades={n}")
    print(f"  hit rate            {hit:.1%}   (baseline up-rate {baseline_p:.1%})")
    print(f"  edge vs baseline    {hit - baseline_p:+.1%}   z={z:.2f}  p={p:.3f}"
          + ("  *** significant" if not math.isnan(p) and p < 0.05 else "  (not significant)"))
    print(f"  avg realized/trade  {avg_real:+.2%}  (after {COST_BPS}bps cost)")
    print(f"  cumulative (equal-size)  {cum:+.1%}")
    # by conviction — does the 2-signal 'high' tier actually beat 'low'?
    for c in ("high", "medium", "low"):
        sub = [r for r in records if r["conviction"] == c]
        if sub:
            print(f"    {c:6} n={len(sub):4}  hit={sum(s['correct'] for s in sub)/len(sub):.1%}"
                  f"  avg={statistics.mean(s['realized'] for s in sub):+.2%}")


def main():
    print(f"Downloading {len(UNIVERSE)} tickers {START}..{END} ...")
    close = download_close(UNIVERSE, START, END)
    bp = base_rate(close)
    recs = run(close, STRATEGY)
    train_end = dt.date.fromisoformat(TRAIN_END)
    in_s = [r for r in recs if dt.date.fromisoformat(r["date"]) <= train_end]
    oos  = [r for r in recs if dt.date.fromisoformat(r["date"]) >  train_end]
    print(f"\nStrategy: {STRATEGY.__name__}  |  horizon={HORIZON}d  cost={COST_BPS}bps")
    summarize(in_s, bp, "IN-SAMPLE (tune here — do NOT trust as edge)")
    summarize(oos, bp, "OUT-OF-SAMPLE (the number that counts)")
    print("\nReminder: OOS edge must clear the baseline AND be significant AND survive costs."
          "\nRunning many strategies and picking the best = overfitting (kb/benchmark-contamination).")


if __name__ == "__main__":
    main()
