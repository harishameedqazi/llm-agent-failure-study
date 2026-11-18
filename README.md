# How LLM Customer Service Agents Fail: An Empirical Study (in progress)

I build and test AI agents that talk to real customers: a clinic receptionist that books appointments over web chat and phone, and a customer support agent for a crowdfunding platform. While testing them I kept finding failures that normal functional tests miss: misread Urdu dates, duplicate bookings, invented answers, missed handoffs to a human.

This repo is the toolkit for studying those failures properly instead of anecdotally:

1. **Run** a fixed set of scripted conversations against a deployed agent, several times each, because LLM answers vary from run to run.
2. **Label** every conversation with failure codes from a written taxonomy.
3. **Have a second person label the same conversations** and measure agreement, so the categories mean the same thing to two people.
4. **Report** how often each failure happens, with confidence intervals, broken down by language and task type.

## Research questions

- **RQ1.** What kinds of failures do LLM customer service agents show in real deployments?
- **RQ2.** How often does each kind happen, and does it differ between English, Urdu and Roman Urdu users?
- **RQ3.** Which failures are caught by ordinary functional tests, and which only show up in realistic conversations?

## Status

| Step | Status |
|---|---|
| Failure taxonomy draft ([taxonomy.md](taxonomy.md)) | Done, v0.1 |
| Scripted scenarios ([scenarios/clinic_chat.jsonl](scenarios/clinic_chat.jsonl)) | 24 written, target 100+ |
| Runner, labelling and analysis scripts | Done and tested |
| Permission to use anonymized production logs | Pending |
| First labelling round and agreement check | Not started |
| Write up | Not started |

## How to run

```bash
pip install -r requirements.txt

# 1. run every scenario 3 times against the agent's chat webhook
python run_scenarios.py --webhook https://YOUR-N8N-HOST/webhook/web-chat \
    --scenarios scenarios/clinic_chat.jsonl --out results/run1.jsonl --repeats 3

# 2. label the transcripts (each annotator separately)
python label.py --results results/run1.jsonl --annotator haris

# 3. failure rates, plus agreement once a second annotator has labelled
python analyze.py --labels labels/labels_haris.csv --second labels/labels_kamran.csv
```

For production logs: export the chat or call log to CSV, then run `anonymize.py` to remove emails, phone numbers and names before anything else. Raw logs are never committed (see `.gitignore`).

## Files

```
taxonomy.md            failure codes and labelling rules
scenarios/             scripted test conversations (JSON lines)
run_scenarios.py       sends scenarios to the agent webhook and saves transcripts
label.py               terminal tool for labelling transcripts with failure codes
analyze.py             failure rates with 95% Wilson intervals, Cohen's kappa
anonymize.py           removes personal data from exported logs
```

## Related projects

- [ai-clinic-receptionist](https://github.com/harishameedqazi/ai-clinic-receptionist): the clinic agent under study
- [apnacrowdfunding-support-agent](https://github.com/harishameedqazi/apnacrowdfunding-support-agent): the support agent under study
