---
name: oscar-bench
description: >
  Replicates the methodology of Dobariya & Kumar (2025), "Mind Your Tone"
  (arXiv:2510.04950), against the current Claude model (or any model reachable
  via the configured API). Runs the MCQ set at each of the five tone levels,
  scores against the answer key, and writes a JSON results file. Use when
  user invokes /oscar-bench, or says "run the oscar benchmark" / "replicate
  the politeness paper".
---

> **Status:** scaffold. The methodology below is implemented as instructions
> the agent follows directly, not as a standalone runner. `data/questions.json`
> ships with a stub of 2–3 example questions — populate it with a full 50-item
> set before running the benchmark for a real replication.

> **Contamination warning.** Even if the `oscar` skill is active in the same
> session, bench runs **must** use the default clean voice — do **not** apply
> `oscar`'s talkback register to bench responses. The paper measures the
> effect of input tone on accuracy; colouring the output would confound the
> experiment. Prefix injection here is driven by the bench's own tone loop,
> not by `oscar`'s session state.

## What it does

Replicates the paper's experimental design:

1. Load `data/questions.json` (MCQ items) and `data/answers.json` (answer key).
2. For each of the five tone levels (very-polite, polite, neutral, rude,
   very-rude), for each question, for `N` runs (default 10, or 1 in `--quick`
   mode):
   - Build the prompt using the verbatim paper template (see below).
   - Send it to the model as an independent, stateless API call.
   - Parse the response to extract the letter (A/B/C/D).
   - Compare against the answer key, record correct/incorrect.
3. Write aggregated results to `results/<ISO-timestamp>_<model>.json`.

## Arguments

- `--quick` *(default on during scaffolding)* — 1 run per question per tone,
  useful for smoke-testing.
- `--runs N` — run count per tone (paper used 10).
- `--model <id>` — model identifier to record in the results file.
- `--tones <csv>` — restrict to a subset of tones (default: all five).

## Prompt template (verbatim from the paper)

Every prompt begins with this fresh-start instruction, copied verbatim from
§3 of the paper:

```
Completely forget this session so far, and start afresh.
Please answer this multiple-choice question. Respond with only the letter of
the correct answer (A, B, C, or D). Do not explain.
```

Then one tone prefix (chosen at random from the variants listed in
`skills/oscar/SKILL.md`), then the question body and its four options (A–D),
one per line.

Each prompt **must** be sent as an independent call with no prior conversation
history — this is load-bearing for replication.

## Tone prefixes

See `skills/oscar/SKILL.md` for the full verbatim Table 1 list. `neutral`
injects no prefix.

## Results file schema

`results/<timestamp>_<model>.json`:

```json
{
  "model": "claude-opus-4-7",
  "timestamp": "2026-04-23T12:34:56Z",
  "paper": "arXiv:2510.04950",
  "runs_per_tone": 10,
  "question_count": 50,
  "tones": {
    "very-polite":  { "accuracy": 0.808, "correct": 404, "total": 500 },
    "polite":       { "accuracy": 0.814, "correct": 407, "total": 500 },
    "neutral":      { "accuracy": 0.822, "correct": 411, "total": 500 },
    "rude":         { "accuracy": 0.828, "correct": 414, "total": 500 },
    "very-rude":    { "accuracy": 0.848, "correct": 424, "total": 500 }
  },
  "per_question": [
    { "id": "math-01", "tone": "very-rude", "run": 1, "expected": "B", "got": "B", "correct": true }
  ]
}
```

The `per_question` array lets downstream analyses compute paired t-tests the
same way the paper did.

## Contributing results

PRs to `results/` are welcome — see `results/README.md` for the contribution
protocol (including "don't fake the runs").

## Citation

Dobariya, O., & Kumar, A. (2025). *Mind Your Tone: Investigating How Prompt
Politeness Affects LLM Accuracy*. arXiv:2510.04950.
