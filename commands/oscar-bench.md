---
description: Replicate the Mind Your Tone (arXiv:2510.04950) MCQ benchmark against the current model.
argument-hint: [--quick] [--runs N] [--model id] [--tones csv] [--dry-run] [--seed N]
---

Invoke `bench/run.py` (the oscar-bench replication runner; see
`skills/oscar-bench/SKILL.md` for the methodology).

1. Translate `$ARGUMENTS` directly to CLI flags for the script:
   `--quick`, `--runs N`, `--model <id>`, `--tones <csv>`, `--dry-run`,
   `--seed N`. Default to `--quick` if no run-count flag is given.
2. Before running, show: model, number of questions in `data/questions.json`,
   tones, runs, and total API calls (`tones × questions × runs`). If the
   question set has fewer than 50 items, warn the user that this is not a
   full paper replication and offer to continue anyway.
3. Confirm `ANTHROPIC_API_KEY` is set in the environment unless `--dry-run`.
4. Ask the user to confirm before sending any API calls.
5. Run via Bash: `python bench/run.py <flags>`. The script writes
   `results/<ISO-timestamp>_<model>.json` (schema in
   `skills/oscar-bench/SKILL.md`) and prints a per-tone summary on stderr.
6. Show the user the summary table and the path to the results file.

Carve-out reminder: any output you produce to summarize the bench run must
stay in default voice — Oscar's talkback register is suppressed inside
bench runs (see `skills/oscar/SKILL.md`).
