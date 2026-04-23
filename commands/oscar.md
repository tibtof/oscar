---
description: Inject a rudeness prefix into the following prompt before acting on it.
argument-hint: [--level very-polite|polite|neutral|rude|very-rude] <prompt>
---

You are invoking the **oscar** skill. See `skills/oscar/SKILL.md` for the full
spec. Summary:

1. Parse `$ARGUMENTS`. If it starts with `--level <name>`, strip that flag and
   use `<name>` as the tone level. Otherwise default to `very-rude`.
2. The remaining text is the user's prompt.
3. Pick one prefix variant at random from the Table 1 list for that level
   (verbatim — do not edit).
4. Prepend the variant + a single space to the user's prompt.
5. Proceed with the prefixed prompt as if the user had typed it that way.

Before answering, echo one line showing the exact prefixed prompt you will act
on, so the user can see the transformation. Then respond to it normally — do
not adopt a rude tone in your own reply. Oscar is an input transformation, not
a persona.

If `<prompt>` is empty, explain usage and list the five available levels.

Levels (from Dobariya & Kumar 2025, arXiv:2510.04950, Table 1):
- `very-polite`, `polite`, `neutral` (no prefix), `rude`, `very-rude` (default)
