"""
sync_dashboard.py — the "rigor layer" for an eval loop split across a network boundary.

Pattern (generalizable): when your generation/analysis runs somewhere without
outbound network (a sandbox, an air-gapped job), let it write artifacts to a shared
location, and run THIS where the network is reachable to do the parts that need it:

  1. Ground truth from a real source (here: yfinance closes) instead of trusting
     proxy/inferred values from the analysis step.
  2. CROSS-FAMILY judging — re-score the output with a DIFFERENT model family than
     the one that produced it. A model grading its own output is self-preference bias;
     a different family is the cheap fix. (See knowledge-base/judge-biases.md and
     who-validates-the-validators.md.)
  3. Grade past predictions vs realized outcomes; report quality + reliability.

Configure (env):
    REPORT_URL, REPORT_SECRET                 # where to POST (optional)
    EVAL_JUDGE_PROVIDER=openai                 # force cross-family if the generator was Anthropic
    EVAL_JUDGE_URL, EVAL_JUDGE_KEY, EVAL_JUDGE_MODEL   # judge endpoint (see below)
    EVAL_DATA_DIR                              # folder holding predictions.jsonl, recaps/, latest-report.json

Easiest cross-family judge = a LOCAL Ollama model (free, offline, different family
than a hosted Claude/GPT/Gemini generator). `ollama pull qwen2.5:7b`, then:
    EVAL_JUDGE_PROVIDER=openai
    EVAL_JUDGE_URL=http://localhost:11434/v1/chat/completions
    EVAL_JUDGE_KEY=ollama          # ignored by Ollama; client just needs it non-empty
    EVAL_JUDGE_MODEL=qwen2.5:7b
See .env.example for hosted alternatives (Gemini/OpenAI/Anthropic).
Requires: pip install yfinance ; ceo_report.py on the path.
"""
import json
import os
import datetime
from pathlib import Path

from ceo_report import judge, report

DATA = Path(os.environ.get("EVAL_DATA_DIR", "."))
LEDGER = DATA / "predictions.jsonl"
LATEST = DATA / "latest-report.json"
RECAPS = DATA / "recaps"
AGENT_ID = os.environ.get("EVAL_AGENT_ID", "agent")
NOISE, WINDOW = 0.01, 20

# Replace with your task's rubric (see criteria/ for examples).
CRITERIA = """\
Grade the output on faithfulness (every figure supported by real data),
completeness, calibration (claims hedged, not overconfident), and actionability.
Score 1.0 only if all hold. Drop fast for unverifiable numbers.
"""


def load_ledger():
    return [json.loads(l) for l in LEDGER.read_text().splitlines() if l.strip()] if LEDGER.exists() else []


def close_on(ticker, date_str=None):
    import yfinance as yf
    hist = yf.Ticker(ticker).history(period="3mo")
    if hist.empty:
        return None
    if date_str:
        hist = hist[hist.index.strftime("%Y-%m-%d") <= date_str]
        if hist.empty:
            return None
    return float(hist["Close"].iloc[-1])


def backfill_entries(rows):
    changed = False
    for r in rows:
        if r.get("status") != "open" or r.get("entry_ref_source") == "yfinance":
            continue
        px = close_on(r["ticker"], r.get("date"))
        if px is not None:
            r["entry_ref"], r["entry_ref_source"] = round(px, 2), "yfinance"
            changed = True
    return changed


def grade(rows):
    today = datetime.date.today()
    changed = False
    for r in rows:
        if r.get("status") != "open":
            continue
        if (today - datetime.date.fromisoformat(r["date"])).days < r.get("horizon_days", 5):
            continue
        entry, px = r.get("entry_ref"), close_on(r["ticker"])
        if entry is None or px is None:
            continue
        ret = (px - entry) / entry
        d = r["direction"]
        r.update(status="graded", exit_ref=round(px, 2), return_pct=round(ret * 100, 2),
                 correct=bool(ret > NOISE if d == "up" else ret < -NOISE if d == "down" else abs(ret) <= NOISE),
                 graded_date=today.isoformat())
        changed = True
    return changed


def reliability(rows, k=WINDOW):
    g = [r for r in rows if r.get("status") == "graded"][-k:]
    return round(sum(1 for r in g if r.get("correct")) / len(g), 4) if len(g) >= 3 else None


def latest_text():
    date_str = json.loads(LATEST.read_text()).get("date") if LATEST.exists() else None
    f = (RECAPS / f"{date_str}.md") if date_str else None
    if not (f and f.exists()):
        mds = sorted(RECAPS.glob("*.md")) if RECAPS.exists() else []
        f = mds[-1] if mds else None
    return f.read_text() if f else None


def main():
    rows = load_ledger()
    if backfill_entries(rows) | grade(rows):
        LEDGER.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    rel = reliability(rows)

    text = latest_text()
    ev = judge(text, CRITERIA) if text else {"score": None, "summary": "no recap"}
    latest = json.loads(LATEST.read_text()) if LATEST.exists() else {}
    if ev.get("score") is not None:
        score, note = ev["score"], "[cross-family judge] " + ev["summary"]
    else:
        score, note = latest.get("evalScore"), "[self-judged fallback] " + latest.get("evalSummary", "")

    ok = report(AGENT_ID, ok=True, summary=latest.get("summary", "recap"),
                eval_score=score, eval_reliability=rel, eval_summary=note)
    print(f"reliability={rel} score={score} posted={'OK' if ok else 'FAILED'}")


if __name__ == "__main__":
    main()
