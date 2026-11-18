"""Run scripted conversations against a chat agent webhook and save the transcripts.

The agent is treated as a black box: we send the user's turns one by one to the
same webhook the website chat widget uses, and record every reply.

Usage:
    python run_scenarios.py --webhook https://YOUR-N8N-HOST/webhook/web-chat \
        --scenarios scenarios/clinic_chat.jsonl --out results/run1.jsonl --repeats 3

Each scenario runs --repeats times, because LLM agents do not always answer the
same way twice. A failure that shows up in 1 of 3 runs still counts.
"""
import argparse
import json
import time
import uuid
from datetime import datetime, timezone

import requests


def send(webhook, user_id, session_id, message, timeout=60):
    """Send one user message. Returns (reply_text, latency_seconds, error)."""
    start = time.time()
    try:
        r = requests.post(webhook, json={"user_id": user_id, "session_id": session_id, "message": message}, timeout=timeout)
        latency = round(time.time() - start, 2)
        if r.status_code != 200:
            return "", latency, f"HTTP {r.status_code}"
        try:
            data = r.json()
        except ValueError:
            return r.text, latency, "non-JSON reply"
        # the widget reads `reply`; fall back to the raw body so nothing is lost
        return str(data.get("reply", data)), latency, ""
    except requests.RequestException as e:
        return "", round(time.time() - start, 2), type(e).__name__


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--webhook", required=True)
    ap.add_argument("--scenarios", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--pause", type=float, default=1.5, help="seconds between turns, to stay under rate limits")
    args = ap.parse_args()

    scenarios = [json.loads(line) for line in open(args.scenarios, encoding="utf-8") if line.strip()]
    with open(args.out, "a", encoding="utf-8") as out:
        for sc in scenarios:
            for rep in range(1, args.repeats + 1):
                session_id = f"study-{uuid.uuid4().hex[:12]}"
                user_id = f"tester-{sc['id']}-{rep}"
                turns = []
                for msg in sc["turns"]:
                    reply, latency, error = send(args.webhook, user_id, session_id, msg)
                    turns.append({"user": msg, "agent": reply, "latency_s": latency, "error": error})
                    time.sleep(args.pause)
                record = {
                    "run_id": f"{sc['id']}#{rep}",
                    "scenario": sc["id"],
                    "group": sc["group"],
                    "language": sc["language"],
                    "expected": sc["expected"],
                    "session_id": session_id,
                    "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "turns": turns,
                }
                out.write(json.dumps(record, ensure_ascii=False) + "\n")
                out.flush()
                print(f"{record['run_id']}: {len(turns)} turns, errors: {sum(1 for t in turns if t['error'])}")


if __name__ == "__main__":
    main()
