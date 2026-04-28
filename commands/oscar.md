---
description: Activate or adjust Oscar — rudeness-injection mode that sticks for the session.
argument-hint: [--level very-polite|polite|neutral|rude|very-rude] [--reply match|off|<level>] [off] [<prompt>]
---

Invoke the `oscar` skill (see `skills/oscar/SKILL.md`). Summary:

1. Parse `$ARGUMENTS` (flags may appear in any order, both may appear together):
   - If it starts with `off` or `--off` → set `active = false` and confirm.
   - If `--level <name>` is present → strip it, set session `level = <name>`.
     Valid: the five tone levels. Missing or invalid value: list the valid
     options and stop without changing state.
   - If `--reply <name>` is present → strip it, set session `reply = <name>`.
     Valid: `match`, `off`, or any of the five tone levels. Missing or
     invalid value: list the valid options and stop without changing state.
     Setting `reply` to the same level as `level` is accepted silently —
     for the current turn it produces the same output as `match`, but the
     two diverge if `level` is later changed.
   - Set `active = true`.
2. If any prompt text remains after flags, process it immediately:
   - Inject a random verbatim prefix from the current `level`'s Table 1
     variants.
   - Resolve the effective reply register from `reply` (see the skill's
     "Talkback register" section): `match` tracks `level`, `off` is default
     voice, a named level uses that level's register.
3. If no prompt text remains, confirm the session state in default voice
   and wait. On first activation that means
   "Oscar active, level=very-rude, reply=match. Go on."; otherwise echo
   the current values.

Once active, the skill applies to **every** subsequent user turn — the user
does not retype `/oscar`. To exit: `stop oscar`, `oscar off`, `normal mode`,
or `/oscar off`.

Respect the carve-outs in `SKILL.md` — security warnings, destructive
confirmations, sensitive topics, and `oscar-bench` runs always drop the
attitude.

Levels (from Dobariya & Kumar 2025, arXiv:2510.04950, Table 1):
`very-polite`, `polite`, `neutral` (no prefix), `rude`, `very-rude` (default).
