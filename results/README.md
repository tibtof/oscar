# results/

Per-run output from `/oscar-bench`. One file per run, named
`<ISO-timestamp>_<model>.json` (e.g. `2026-04-23T1234_claude-opus-4-7.json`).

Schema: see `skills/oscar-bench/SKILL.md`.

## Contributing results

Replications are welcome. PR a new file into this directory with:

- **Don't fake the runs.** This is a replication harness; fabricated numbers
  poison the point of the repo. If you partially ran and stopped, say so in
  the `notes` field.
- **Record the model identifier exactly** as returned by the provider
  (e.g. `claude-opus-4-7`, `gpt-4o-2024-08-06`, `gemini-2.0-pro-exp`).
- **Note any deviations** from the paper's methodology — e.g. you only ran
  3 runs per tone instead of 10, you used a subset of the questions, you
  added temperature or top-p parameters.
- **One file per run.** Don't overwrite previous runs.

The repo owner may ask for the raw per-question array if aggregated numbers
look surprising.
