---
description: Replicate the Mind Your Tone (arXiv:2510.04950) MCQ benchmark against the current model.
argument-hint: [--quick] [--runs N] [--model id] [--tones csv]
---

Invoke the `oscar-bench` skill (see `skills/oscar-bench/SKILL.md` for the full
spec).

Default mode is `--quick` (1 run per question per tone) until the full
50-question dataset has been populated in `data/questions.json`. Warn the user
if the dataset has fewer than 50 items and offer to continue anyway.

Before running:
1. Confirm the current model identifier and show it back to the user.
2. Show how many questions, tones, and runs this invocation will cover, and
   the rough token budget.
3. Ask the user to confirm before sending any API calls.

After running, write results to `results/<ISO-timestamp>_<model>.json` using
the schema in `skills/oscar-bench/SKILL.md`, and print a summary table of
per-tone accuracy.
