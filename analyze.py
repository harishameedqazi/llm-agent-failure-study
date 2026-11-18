"""Summarise the labels: how often each failure happens, and how much two annotators agree.

Usage:
    python analyze.py --labels labels/labels_haris.csv
    python analyze.py --labels labels/labels_haris.csv --second labels/labels_kamran.csv

Failure rates come with 95% Wilson confidence intervals, because with a few
hundred conversations the uncertainty is large and should be reported.
Agreement is Cohen's kappa per failure code (present vs absent).
"""
import argparse
import csv
import math
from collections import Counter, defaultdict

from label import CODES


def load(path):
    with open(path, encoding="utf-8") as f:
        return {row["run_id"]: row for row in csv.DictReader(f)}


def codes_of(row):
    return set(row["codes"].split("|")) if row["codes"] else set()


def wilson(k, n, z=1.96):
    """95% confidence interval for a proportion k/n."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def kappa(a, b):
    """Cohen's kappa for two lists of booleans."""
    n = len(a)
    if n == 0:
        return float("nan")
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def rates(labels):
    n = len(labels)
    print(f"\nConversations labelled: {n}")
    any_fail = sum(1 for r in labels.values() if codes_of(r) - {"OK"})
    lo, hi = wilson(any_fail, n)
    print(f"With at least one failure: {any_fail} ({any_fail / n:.0%}, 95% CI {lo:.0%} to {hi:.0%})\n")

    counts = Counter(c for r in labels.values() for c in codes_of(r))
    print(f"{'code':<12}{'count':>6}{'rate':>8}   95% CI")
    for code in CODES:
        if code == "OK":
            continue
        k = counts.get(code, 0)
        lo, hi = wilson(k, n)
        print(f"{code:<12}{k:>6}{k / n:>8.0%}   {lo:.0%} to {hi:.0%}")

    for field in ("language", "group"):
        print(f"\nFailure rate by {field}:")
        by = defaultdict(lambda: [0, 0])
        for r in labels.values():
            by[r[field]][1] += 1
            by[r[field]][0] += bool(codes_of(r) - {"OK"})
        for key, (k, total) in sorted(by.items()):
            print(f"  {key:<14}{k}/{total} ({k / total:.0%})")


def agreement(first, second):
    shared = sorted(set(first) & set(second))
    print(f"\nAgreement on {len(shared)} runs labelled by both annotators (Cohen's kappa):")
    for code in CODES:
        a = [code in codes_of(first[i]) for i in shared]
        b = [code in codes_of(second[i]) for i in shared]
        if any(a) or any(b):
            print(f"  {code:<12}{kappa(a, b):.2f}")
    disagree = [i for i in shared if codes_of(first[i]) != codes_of(second[i])]
    print(f"\nRuns to discuss ({len(disagree)}): {', '.join(disagree[:30])}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", required=True)
    ap.add_argument("--second")
    args = ap.parse_args()
    first = load(args.labels)
    rates(first)
    if args.second:
        agreement(first, load(args.second))


if __name__ == "__main__":
    main()
