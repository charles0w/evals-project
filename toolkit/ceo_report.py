"""
ceo_report.py — a tiny, dependency-free eval toolkit.

Three things, usable independently:
  judge(output, criteria)        -> LLM-as-a-judge score (0..1) + one-line rationale
  track_reliability(id, passed)  -> rolling pass-rate + Wilson CI (pass^k-style consistency proxy)
  report(agent_id, ...)          -> POST a status (+ optional eval fields) to a dashboard

Standard library only. Bring your own model key.

JUDGE PROVIDER — pick ONE (auto-selected; override with EVAL_JUDGE_PROVIDER):
  Anthropic (native):
    ANTHROPIC_API_KEY=<key>
    EVAL_JUDGE_MODEL=<optional, default claude-haiku-4-5-20251001>
  OpenAI-compatible (OpenAI, Gemini OpenAI endpoint, Groq, ...):
    EVAL_JUDGE_URL=https://api.openai.com/v1/chat/completions
    EVAL_JUDGE_KEY=<key>
    EVAL_JUDGE_MODEL=gpt-4o-mini

REPORTING (optional — only if you POST to a dashboard):
    REPORT_URL=<your endpoint>     # e.g. https://your-app/api/report
    REPORT_SECRET=<shared secret>  # sent as the x-report-secret header

RIGOR NOTE: an unvalidated judge is a confident guess. Hand-grade a sample and confirm
agreement before trusting these scores, and judge with a DIFFERENT model family than the
one that produced the output (self-preference bias).
"""
import math
import os
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

REPORT_URL = os.environ.get("REPORT_URL", "")
REPORT_SECRET = os.environ.get("REPORT_SECRET", "")

JUDGE_PROVIDER = os.environ.get("EVAL_JUDGE_PROVIDER", "").lower()
JUDGE_URL = os.environ.get("EVAL_JUDGE_URL", "")
JUDGE_KEY = os.environ.get("EVAL_JUDGE_KEY", "")
JUDGE_MODEL = os.environ.get("EVAL_JUDGE_MODEL", "")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

_REL_STORE = Path(os.environ.get("EVAL_STORE", str(Path.home() / ".eval_reliability.json")))

_STRICT_SUFFIX = (
    "\n\nCRITICAL: output ONLY the JSON object "
    '{"score": <0.0 to 1.0>, "summary": "<one sentence>"}. '
    "No explanation, no markdown, no extra keys."
)


def _clamp01(x):
    return max(0.0, min(1.0, float(x)))


def wilson_ci(k, n, z=1.96):
    """Wilson score confidence interval for a proportion k/n.

    Returns (low, high) — a 95% CI by default.
    Example: lo, hi = wilson_ci(hits, n); print(f"{hits/n:.0%} [{lo:.0%}, {hi:.0%}] n={n}")
    """
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = (z / denom) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, centre - half), min(1.0, centre + half))


def _extract_json_object(text):
    """Return the first balanced JSON object in text, or None."""
    start = text.find("{")
    if start == -1:
        return None
    depth, in_str, esc = 0, False, False
    for i, ch in enumerate(text[start:], start):
        if esc:
            esc = False
            continue
        if ch == "\\" and in_str:
            esc = True
            continue
        if ch == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def _judge_prompt(output, criteria, suffix=""):
    return (
        "You are a strict evaluation judge. Score the AGENT OUTPUT from 0.0 to 1.0 "
        "against the CRITERIA. Penalize unsupported claims and missing requirements. "
        "Do not reward length. Respond ONLY with compact JSON: "
        '{"score": <float 0..1>, "summary": "<one sentence>"}.\n\n'
        f"CRITERIA:\n{criteria}\n\nAGENT OUTPUT:\n{output}\n{suffix}"
    )


def _parse_judge(content):
    """Parse judge JSON. Raises ValueError if no valid schema-conforming object is found."""
    for candidate in (content.strip(), _extract_json_object(content)):
        if candidate is None:
            continue
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if "score" not in parsed:
            continue
        try:
            score = float(parsed["score"])
        except (TypeError, ValueError):
            continue
        if not (0.0 <= score <= 1.0):
            raise ValueError(f"score {score!r} out of range [0, 1]")
        return {"score": _clamp01(score), "summary": str(parsed.get("summary", "")).strip()}
    raise ValueError(f"no valid judge JSON in: {content[:200]!r}")


def judge(output, criteria, *, model=None, both=False):
    """Score `output` (0..1) against `criteria`.

    Returns {"score": float|None, "summary": str}.
    With both=True (requires ANTHROPIC_API_KEY + EVAL_JUDGE_URL/KEY):
    Returns the above plus {"anthropic": {...}, "openai": {...},
    "agreement": bool|None, "delta": float|None} — agreement is whether both
    providers agree when thresholded at 0.7. Use this to detect self-preference
    bias; accumulate across N calls for dataset-level kappa.
    """
    provider = JUDGE_PROVIDER or ("anthropic" if ANTHROPIC_KEY else ("openai" if (JUDGE_URL and JUDGE_KEY) else ""))
    if not both:
        if provider == "anthropic":
            return _judge_anthropic(output, criteria, model)
        if provider == "openai":
            return _judge_openai(output, criteria, model)
        return {"score": None, "summary": "judge not configured (set ANTHROPIC_API_KEY or EVAL_JUDGE_URL/KEY)"}

    a = _judge_anthropic(output, criteria, model) if ANTHROPIC_KEY else {"score": None, "summary": "ANTHROPIC_API_KEY not set"}
    o = _judge_openai(output, criteria, model) if (JUDGE_URL and JUDGE_KEY) else {"score": None, "summary": "EVAL_JUDGE_URL/KEY not set"}
    sa, so = a.get("score"), o.get("score")
    if sa is not None and so is not None:
        score = (sa + so) / 2
        agreement = (sa >= 0.7) == (so >= 0.7)
        delta = abs(sa - so)
    else:
        score = sa if sa is not None else so
        agreement, delta = None, None
    return {
        "score": score,
        "summary": a["summary"] if sa is not None else o["summary"],
        "anthropic": a,
        "openai": o,
        "agreement": agreement,
        "delta": delta,
    }


def _judge_anthropic(output, criteria, model):
    if not ANTHROPIC_KEY:
        return {"score": None, "summary": "ANTHROPIC_API_KEY not set"}
    for attempt, suffix in enumerate(("", _STRICT_SUFFIX)):
        body = json.dumps({
            "model": model or JUDGE_MODEL or "claude-haiku-4-5-20251001",
            "max_tokens": 256,
            "messages": [{"role": "user", "content": _judge_prompt(output, criteria, suffix)}],
        }).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages", data=body,
            headers={"content-type": "application/json", "x-api-key": ANTHROPIC_KEY,
                     "anthropic-version": "2023-06-01"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
            return _parse_judge(data["content"][0]["text"])
        except ValueError as e:
            if attempt == 0:
                print(f"[ceo_report] parse failed, retrying with strict prompt: {e}")
                continue
            print(f"[ceo_report] parse failed after retry: {e}")
            return {"score": None, "summary": f"judge parse error: {e}"}
        except Exception as e:
            print(f"[ceo_report] anthropic judge failed: {e}")
            return {"score": None, "summary": f"judge error: {e}"}
    return {"score": None, "summary": "judge parse error after retry"}


def _judge_openai(output, criteria, model):
    if not (JUDGE_URL and JUDGE_KEY):
        return {"score": None, "summary": "EVAL_JUDGE_URL/KEY not set"}
    for attempt, suffix in enumerate(("", _STRICT_SUFFIX)):
        body = json.dumps({
            "model": model or JUDGE_MODEL or "gpt-4o-mini",
            "messages": [{"role": "user", "content": _judge_prompt(output, criteria, suffix)}],
            "temperature": 0,
        }).encode()
        req = urllib.request.Request(
            JUDGE_URL, data=body,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {JUDGE_KEY}"},
            method="POST")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                content = json.loads(resp.read().decode())["choices"][0]["message"]["content"]
            return _parse_judge(content)
        except ValueError as e:
            if attempt == 0:
                print(f"[ceo_report] parse failed, retrying with strict prompt: {e}")
                continue
            print(f"[ceo_report] parse failed after retry: {e}")
            return {"score": None, "summary": f"judge parse error: {e}"}
        except Exception as e:
            print(f"[ceo_report] openai judge failed: {e}")
            return {"score": None, "summary": f"judge error: {e}"}
    return {"score": None, "summary": "judge parse error after retry"}


def track_reliability(agent_id, *, passed, window=8):
    """Record this run's pass/fail; return {rate, ci_low, ci_high, n} over the last `window` runs.

    pass^k in its strict form asks 'did ALL k runs pass' (0/1). This returns the smoother
    fraction-passed plus a 95% Wilson CI, which reads better on a dashboard while still
    surfacing inconsistency: 80% [55%, 94%] n=8 is very different from 80% [74%, 85%] n=100.
    """
    try:
        history = json.loads(_REL_STORE.read_text()) if _REL_STORE.exists() else {}
    except Exception:
        history = {}
    runs = (history.get(agent_id, []) + [bool(passed)])[-window:]
    history[agent_id] = runs
    try:
        _REL_STORE.write_text(json.dumps(history))
    except Exception as e:
        print(f"[ceo_report] could not persist reliability: {e}")
    n = len(runs)
    k = sum(runs)
    rate = k / n if n else 0.0
    lo, hi = wilson_ci(k, n)
    return {"rate": rate, "ci_low": lo, "ci_high": hi, "n": n}


def report(agent_id, *, ok, summary, state=None,
           eval_score=None, eval_reliability=None, eval_summary=None):
    """POST a status (+ optional eval fields) to REPORT_URL. Returns True on success.

    eval_reliability: float in [0, 1]. If you use track_reliability(), pass rel["rate"].
    """
    if not (REPORT_URL and REPORT_SECRET):
        print("[ceo_report] REPORT_URL/REPORT_SECRET not set — skipping report")
        return False
    status = {"state": state or ("ok" if ok else "error"),
              "lastRun": datetime.now(timezone.utc).isoformat(), "summary": summary, "ok": ok}
    if eval_score is not None:
        status["evalScore"] = round(_clamp01(eval_score), 4)
    if eval_reliability is not None:
        status["evalReliability"] = round(_clamp01(eval_reliability), 4)
    if eval_summary is not None:
        status["evalSummary"] = eval_summary
    req = urllib.request.Request(
        REPORT_URL, data=json.dumps({"agentId": agent_id, "status": status}).encode(),
        headers={"Content-Type": "application/json", "x-report-secret": REPORT_SECRET},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[ceo_report] report failed: {e}")
        return False
