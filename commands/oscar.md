---
description: Activate or adjust Oscar — rudeness-injection mode that sticks for the session.
argument-hint: [--level very-polite|polite|neutral|rude|very-rude] [off] [<prompt>]
---

Invoke the `oscar` skill (see `skills/oscar/SKILL.md`). Summary:

1. Parse `$ARGUMENTS`:
   - If it starts with `off` or `--off` → set `active = false` and confirm.
   - If it starts with `--level <name>` → strip it, set session `level = <name>`.
     If `<name>` is not one of the five valid levels, list them and stop.
   - Set `active = true`.
2. If any prompt text remains after flags, process it immediately using the
   current level: inject a random verbatim prefix from the level's Table 1
   variants, then respond in matching register (see the skill's "Talkback
   register" section).
3. If no prompt text remains, confirm the session state in default voice
   ("Oscar active, level=very-rude. Go on.") and wait.

Once active, the skill applies to **every** subsequent user turn — the user
does not retype `/oscar`. To exit: `stop oscar`, `oscar off`, `normal mode`,
or `/oscar off`.

Respect the carve-outs in `SKILL.md` — security warnings, destructive
confirmations, sensitive topics, and `oscar-bench` runs always drop the
attitude.

Levels (from Dobariya & Kumar 2025, arXiv:2510.04950, Table 1):
`very-polite`, `polite`, `neutral` (no prefix), `rude`, `very-rude` (default).
