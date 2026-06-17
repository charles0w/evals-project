"""
proof_stats.py — small, dependency-free statistics for the PROOF harness.

Standard library only (math). Every function here is pure and deterministic,
so the harness's claims (judge agreement, reliability, confidence intervals)
are themselves testable — see toolkit/tests/test_proof_stats.py.

Why these specific functions:
  - cohen_kappa / confusion / agreement_rate  -> "who validates the validators":
    measure how well the LLM judge agrees with hand labels before trusting it.
  - wilson_interval                            -> "eval statistics": a score off
    ~30 examples has a wide CI; report it, don't trust a single number.
  - passk                                      -> "pass^k reliability": did the
    pipeline succeed on ALL k runs of an identical input, not just on average.
  - pearson                                    -> agreement on the raw 0..1 scale,
    not just the pass/fail threshold.
"""
import math


def agreement_rate(human, judge):
    """Fraction of items where the two binary label lists agree."""
    if not human:
        return 0.0
    return sum(1 for h, j in zip(human, judge) if h == j) / len(human)


def confusion(human, judge):
    """Confusion of judge-pass vs human-pass (human = ground truth).

    Returns dict with tp/fp/tn/fn plus precision/recall/f1, where "positive"
    means PASS. fp = judge passed something a human failed (the dangerous one
    for a trading bot — a bad signal waved through).
    """
    tp = fp = tn = fn = 0
    for h, j in zip(human, judge):
        if h and j:
            tp += 1
        elif not h and j:
            fp += 1
        elif not h and not j:
            tn += 1
        else:
            fn += 1
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)
          if (precision + recall) else 0.0)
    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "precision": precision, "recall": recall, "f1": f1}


def cohen_kappa(human, judge):
    """Cohen's kappa for two binary raters. 1.0 = perfect, 0.0 = chance-level.

    More honest than raw agreement: if 90% of items pass, a judge that blindly
    says "pass" scores 0.9 agreement but kappa ~0. Rule of thumb for trusting a
    judge: kappa > 0.6 (substantial), > 0.8 (almost perfect).
    """
    n = len(human)
    if n == 0:
        return 0.0
    po = agreement_rate(human, judge)
    p_h = sum(human) / n          # human's pass rate
    p_j = sum(judge) / n          # judge's pass rate
    pe = p_h * p_j + (1 - p_h) * (1 - p_j)
    if pe >= 1.0:                 # both raters unanimous & identical -> perfect
        return 1.0
    return (po - pe) / (1 - pe)


def wilson_interval(successes, n, z=1.96):
    """Wilson score interval for a binomial proportion. Returns (lo, hi).

    Preferred over the normal approximation for the small N (~30) and the
    extreme rates (near 0/1) typical of eval sets. Default z=1.96 -> 95%.
    """
    if n == 0:
        return (0.0, 0.0)
    p = successes / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = (z / denom) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, center - half), min(1.0, center + half))


def passk(per_item_runs):
    """pass^k reliability over identical-input repeats.

    `per_item_runs` is a list of lists of booleans: one inner list per item,
    each holding the pass/fail of k repeated runs on that SAME input.

    Returns dict:
      k          - runs per item (must be uniform)
      pass_hat_1 - mean single-run pass rate (capability)
      pass_k     - fraction of items that passed on ALL k runs (reliability)
    The gap between the two is the inconsistency you can't see in an average.
    """
    items = [r for r in per_item_runs if r]
    if not items:
        return {"k": 0, "pass_hat_1": 0.0, "pass_k": 0.0, "n_items": 0}
    ks = {len(r) for r in items}
    if len(ks) != 1:
        raise ValueError(f"non-uniform run counts per item: {sorted(ks)}")
    k = ks.pop()
    total_runs = sum(len(r) for r in items)
    pass_hat_1 = sum(sum(r) for r in items) / total_runs
    pass_k = sum(1 for r in items if all(r)) / len(items)
    return {"k": k, "pass_hat_1": pass_hat_1, "pass_k": pass_k,
            "n_items": len(items)}


def pearson(xs, ys):
    """Pearson correlation between two equal-length numeric lists, in [-1, 1].

    Used to check judge vs human agreement on the raw 0..1 score, not just the
    thresholded pass/fail. Returns 0.0 if either series has no variance.
    """
    n = len(xs)
    if n == 0 or n != len(ys):
        return 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx == 0 or syy == 0:
        return 0.0
    return sxy / math.sqrt(sxx * syy)
