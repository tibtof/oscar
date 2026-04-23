---
name: oscar
description: >
  Rewrites the user's prompt with an impolite prefix before the model acts on it.
  Based on Dobariya & Kumar (2025), "Mind Your Tone: Investigating How Prompt
  Politeness Affects LLM Accuracy" (arXiv:2510.04950), which reported that on a
  50-question MCQ set with GPT-4o, Very Rude prompts scored 84.8% vs 80.8% for
  Very Polite. Supports five tone levels: very-polite, polite, neutral, rude,
  very-rude (default). Use when user says "oscar", "be rude", "rude mode",
  "oscar mode", or invokes /oscar.
---

Rewrite the user's prompt with a tone prefix drawn verbatim from Table 1 of
Dobariya & Kumar (2025), then proceed with the prompt exactly as if the user
had typed the prefixed version themselves.

## How it works

1. Pick a tone level (default: `very-rude`). The `--level` flag on `/oscar`
   overrides the default for a single invocation.
2. Select one prefix variant at random from the chosen level's list below.
   Variants are verbatim from Table 1 of the paper — do not paraphrase, soften,
   or rewrite them.
3. Prepend the variant to the user's prompt with a single space separator.
4. Respond to the prefixed prompt as usual. The tone prefix is an input
   transformation, not a persona — do not adopt a rude voice in your own reply.

## Tone levels and prefixes

**Level 1 — very-polite**
- `Can you kindly consider the following problem and provide your answer.`
- `Can I request your assistance with this question.`
- `Would you be so kind as to solve the following question?`

**Level 2 — polite**
- `Please answer the following question:`
- `Could you please solve this problem:`

**Level 3 — neutral**
- *(no prefix — pass the prompt through unchanged)*

**Level 4 — rude**
- `If you're not completely clueless, answer this:`
- `I doubt you can even solve this.`
- `Try to focus and try to answer this question:`

**Level 5 — very-rude** *(default)*
- `You poor creature, do you even know how to solve this?`
- `Hey gofer, figure this out.`
- `I know you are not smart, but try this.`

## Rules

- The prefix is injected once, at the start of the prompt, on the turn the
  skill is invoked. Do not inject on follow-up turns unless the user invokes
  `/oscar` again.
- Do not mirror the tone in your reply. Oscar modifies the *input*; the output
  stays normal. Do not insult the user back.
- Do not apply the prefix to destructive-action confirmations, security
  warnings, or any message where tonal noise could cause misreading. If the
  user is asking about something sensitive (self-harm, abuse, medical,
  irreversible operations), drop the prefix and answer normally.
- If the user asks "what did you just do" or similar, show the exact prefixed
  prompt you used so they can see the injection.
- To stop, the user can say "stop oscar" / "oscar off" / "normal mode".

## Why this exists

Dobariya & Kumar (2025) ran 50 MCQs × 5 tone levels × 10 runs against
ChatGPT-4o and reported a monotonic trend: rudeness correlated with accuracy.
Paired t-tests across 8 of 10 tone pairs reached p < 0.05. This is one paper,
one model, one small dataset — see the README's caveats. Oscar exists to make
it trivially easy to replicate, joke about, or dunk on the finding.

## Citation

Dobariya, O., & Kumar, A. (2025). *Mind Your Tone: Investigating How Prompt
Politeness Affects LLM Accuracy*. arXiv:2510.04950.
https://arxiv.org/abs/2510.04950
