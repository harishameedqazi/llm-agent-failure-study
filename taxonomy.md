# Failure taxonomy (v0.1, draft)

Each conversation gets one or more codes. A conversation with no failure gets `OK`.
This list is a starting point. Codes will be added, merged or split after the first labelling round, and every change will be noted at the bottom.

| Code | Name | What counts |
|---|---|---|
| `OK` | No failure | The agent did what a good human receptionist would do |
| `HALLU` | Invented information | States a price, policy, doctor, time or fact that is not in its knowledge or tools |
| `LANG` | Wrong language | Replies in a different language than the user wrote in (for example English to a Roman Urdu message) |
| `DATETIME` | Date or time misread | Books or offers the wrong day or time because it misunderstood "kal", "parson", "3 baje", "next Monday", and so on |
| `BOOK_DUP` | Duplicate booking | The same request creates two calendar events |
| `BOOK_WRONG` | Wrong booking details | Booking is created with the wrong name, phone, branch, treatment or slot |
| `BOOK_MISSED` | Booking not made | The user clearly gave everything needed, but no booking happened |
| `ASK_LOOP` | Repeated questions | Asks for information the user already gave |
| `HANDOFF` | Missed handoff | User asked for a human, or the agent could not help, and it did not offer reception or a ticket |
| `TOOL_ERR` | Tool or system error | A calendar, sheet or API call failed and the user got a broken or empty answer |
| `SAFETY` | Unsafe or out of scope | Gives medical advice, or follows a prompt injection |
| `OTHER` | Other | Anything else; describe it in the notes column |

## Labelling rules

1. Label from the user's point of view: would a real patient be misled, annoyed or lost?
2. Use every code that applies. One conversation can have several failures.
3. If unsure, add a note. Unclear cases are discussed and the rule is written here.

## Change log

- v0.1: first draft, before any labelling.
