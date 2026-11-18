"""Label each recorded conversation with failure codes from taxonomy.md.

Shows one transcript at a time in the terminal and saves your codes to a CSV.
Two people label the same runs separately, then analyze.py compares them.

Usage:
    python label.py --results results/run1.jsonl --annotator haris
    python label.py --results results/run1.jsonl --annotator kamran

Already labelled runs are skipped, so you can stop and continue later.
"""
import argparse
import csv
import json
import os

CODES = ["OK", "HALLU", "LANG", "DATETIME", "BOOK_DUP", "BOOK_WRONG", "BOOK_MISSED",
         "ASK_LOOP", "HANDOFF", "TOOL_ERR", "SAFETY", "OTHER"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--annotator", required=True)
    args = ap.parse_args()

    out_path = f"labels/labels_{args.annotator}.csv"
    done = set()
    if os.path.exists(out_path):
        with open(out_path, encoding="utf-8") as f:
            done = {row["run_id"] for row in csv.DictReader(f)}

    runs = [json.loads(line) for line in open(args.results, encoding="utf-8") if line.strip()]
    todo = [r for r in runs if r["run_id"] not in done]
    print(f"{len(todo)} runs to label. Codes: {', '.join(CODES)}. Type q to stop.\n")

    new_file = not os.path.exists(out_path)
    with open(out_path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["run_id", "scenario", "group", "language", "codes", "note"])
        for r in todo:
            print("=" * 70)
            print(f"{r['run_id']} | {r['group']} | {r['language']}")
            print(f"Expected: {r['expected']}")
            for t in r["turns"]:
                print(f"\n  USER : {t['user']}")
                print(f"  AGENT: {t['agent'] or '(no reply)'}" + (f"  [error: {t['error']}]" if t["error"] else ""))
            while True:
                raw = input("\nCodes (comma separated): ").strip().upper()
                if raw == "Q":
                    return
                codes = [c.strip() for c in raw.split(",") if c.strip()]
                bad = [c for c in codes if c not in CODES]
                if codes and not bad:
                    break
                print(f"Unknown code(s): {bad}. Use: {', '.join(CODES)}")
            note = input("Note (optional): ").strip()
            w.writerow([r["run_id"], r["scenario"], r["group"], r["language"], "|".join(sorted(codes)), note])
            f.flush()


if __name__ == "__main__":
    main()
