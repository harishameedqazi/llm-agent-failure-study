"""Remove personal data from exported production chat or call logs before analysis.

Input: a CSV exported from the Google Sheets chat log (one row per conversation).
Output: the same CSV with emails, phone numbers and known names replaced.

Usage:
    python anonymize.py --input raw/chat_log.csv --output data/chat_log_anon.csv \
        --text-columns "Transcript,Summary" --names names_to_remove.txt

This is a first pass. Always read a sample of the output by hand before using it:
regexes miss things, especially names written in Urdu script.
"""
import argparse
import csv
import re

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
# Pakistani mobiles (03xx..., +92 3xx...) and long digit runs in general
PHONE = re.compile(r"(\+?92[\s-]?3\d{2}|0?3\d{2})[\s-]?\d{3}[\s-]?\d{4}|\b\d{10,15}\b")


def scrub(text, names):
    text = EMAIL.sub("[EMAIL]", text)
    text = PHONE.sub("[PHONE]", text)
    for name in names:
        text = re.sub(rf"\b{re.escape(name)}\b", "[NAME]", text, flags=re.IGNORECASE)
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--text-columns", required=True, help="comma separated column names to scrub")
    ap.add_argument("--drop-columns", default="", help="comma separated columns to remove entirely, e.g. 'Caller Number,Email'")
    ap.add_argument("--names", help="text file with one name per line to replace")
    args = ap.parse_args()

    names = [n.strip() for n in open(args.names, encoding="utf-8")] if args.names else []
    names = [n for n in names if len(n) > 1]
    text_cols = [c.strip() for c in args.text_columns.split(",")]
    drop = {c.strip() for c in args.drop_columns.split(",") if c.strip()}

    with open(args.input, encoding="utf-8") as f_in, open(args.output, "w", newline="", encoding="utf-8") as f_out:
        reader = csv.DictReader(f_in)
        fields = [c for c in reader.fieldnames if c not in drop]
        writer = csv.DictWriter(f_out, fieldnames=fields)
        writer.writeheader()
        n = 0
        for row in reader:
            for c in text_cols:
                if c in row and row[c]:
                    row[c] = scrub(row[c], names)
            writer.writerow({k: row[k] for k in fields})
            n += 1
    print(f"wrote {n} rows to {args.output}")


if __name__ == "__main__":
    main()
