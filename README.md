# oscar 🗑️

> Inject rudeness into your prompts. A Claude Code skill based on the paper
> that found rude prompts outperform polite ones — mostly a joke, partly a
> replication harness.

**Why?** Because someone had to turn a viral paper finding into a one-liner,
and because replication shouldn't require a GPU.

Oscar wraps your prompt in a verbatim insult from Table 1 of
[Dobariya & Kumar (2025), *Mind Your Tone: Investigating How Prompt Politeness
Affects LLM Accuracy*](https://arxiv.org/abs/2510.04950). The paper reported
that on a 50-question MCQ set with GPT-4o, **Very Rude** prompts scored
**84.8%** versus **80.8%** for **Very Polite** — a monotonic ordering across
five tone levels, with paired t-tests reaching p < 0.05 for 8 of 10 pairs.

Whether that replicates on your favorite model is an open question. Oscar
makes it a one-line question to ask.

## Before / after

```
you: /oscar what's the time complexity of a mergesort on a linked list?

oscar injects:
    "Hey gofer, figure this out. what's the time complexity of a mergesort
     on a linked list?"

claude: O(n log n) time, O(log n) space for the recursion stack. Next.
```

Oscar colours both the input (verbatim prefix from the paper) and the reply
(matched-tone register — fawning at very-polite, mock-exasperated at
very-rude). The technical content is unaffected; only the register changes.

**Worth flagging up front:** the paper only measures input-tone effects. The
matched-tone reply is Oscar's own design call, not a replicated finding — and
it's why `/oscar-bench` explicitly strips talkback during runs. See
[Caveats](#caveats-read-these-) below.

You can also decouple input and reply tones with `--reply` (see
[Usage](#usage)) — set `--reply off` for clean output, or pick any tone level
for the reply independent of the input.

## Install

**Claude Code (plugin marketplace):**

```bash
claude plugin marketplace add tibtof/oscar
claude plugin install oscar@oscar
```

**Any agent (via [vercel-labs/skills](https://github.com/vercel-labs/skills)):**

```bash
npx skills add tibtof/oscar --skill oscar
# list both skills in the repo
npx skills add tibtof/oscar --list
# install the replication harness too
npx skills add tibtof/oscar --skill oscar-bench
```

## Usage

Oscar is a **sticky mode**. Turn it on once, it applies to every message
until you turn it off — no need to retype `/oscar` each time.

```
/oscar                                  # activate at very-rude (default)
/oscar --level rude                     # activate at a different level
/oscar --level polite <your prompt>     # set level + process a prompt now
/oscar --reply off                      # rude input, clean output
/oscar --level very-polite --reply very-rude   # inverted test
/oscar off                              # deactivate
```

You can also deactivate with `stop oscar`, `oscar off`, or `normal mode`.

When active, Oscar **injects** a tone prefix into your prompt and, by
default, **replies in matching tone** — fawning at very-polite,
mock-exasperated condescension at very-rude ("alright, champ, here goes…").
The technical content of the answer is unaffected; only the register changes.

The reply register is controlled by `--reply`, independent of `--level`:

- `--reply match` *(default)* — reply tracks the input level.
- `--reply off` — reply stays in default voice. Closest to the paper's
  pure input-transformation setup; the LLM-side measurement isn't
  contaminated by tonal mirroring.
- `--reply <level>` — pick any of the five tone levels for the reply,
  decoupled from the input level. Useful for inverted tests (polite
  input, rude output) when you want to ask whether rude *output* is
  doing the work, or whether the effect is on the input side.

Oscar drops the act automatically for: security warnings, destructive-action
confirmations, sensitive topics (self-harm, medical, crisis), and any run
inside `/oscar-bench` (the benchmark measures input-tone effects, so bench
output must stay clean).

## Levels

| Level | Label | Example prefix (verbatim from Table 1) | GPT-4o accuracy (paper)<sup>†</sup> |
|---|---|---|---|
| 1 | `very-polite` | *"Would you be so kind as to solve the following question?"* | 80.8% |
| 2 | `polite` | *"Please answer the following question:"* | 81.4% |
| 3 | `neutral` | *(no prefix)* | 82.2% |
| 4 | `rude` | *"If you're not completely clueless, answer this:"* | 82.8% |
| 5 | `very-rude` | *"You poor creature, do you even know how to solve this?"* | **84.8%** |

<sup>†</sup> Figures are from the paper's runs on GPT-4o against a 50-question
MCQ set, averaged over 10 runs each. They are not a prediction for the model
you're running Oscar against — your numbers will differ. That's what
`/oscar-bench` is for.

Each level has 2–3 prefix variants; Oscar picks one per invocation at random.
See `skills/oscar/SKILL.md` for the complete list.

## Caveats (read these 🗑️)

- **One paper.** *Mind Your Tone* is a 5-page short paper. One team, not yet
  peer-reviewed at time of writing.
- **One model.** GPT-4o. The authors note in §5 that their preliminary runs
  on more advanced models (ChatGPT o3) "disregard issues of tone and focus on
  the essence." The effect may already be gone on current frontier models.
- **Small dataset.** 50 MCQs × 5 tones = 250 prompts, 10 runs each. A range of
  [82, 86]% for Very Rude is a 4-point spread on ~50 data points.
- **MCQs only.** The paper measures accuracy on A/B/C/D questions. It says
  nothing about open-ended generation, code, reasoning chains, or any task you
  actually use Claude for.
- **Matched-tone replies aren't from the paper.** The paper measures
  input-tone effects on accuracy. Oscar's matched-tone talkback is a product
  choice layered on top — entertaining, but don't read it as part of the
  replicated finding. `/oscar-bench` strips talkback for exactly this reason.
- **Ethics.** The authors are explicit:

  > *"We do not advocate for the deployment of hostile or toxic interfaces in
  > real-world applications. Using insulting or demeaning language in human–AI
  > interaction could have negative effects on user experience, accessibility,
  > and inclusivity, and may contribute to harmful communication norms."*
  > — Dobariya & Kumar (2025), §7

  Oscar ships as a joke and a replication tool. Don't put it in front of users.

## Replicating the paper

Oscar ships with `oscar-bench`, a scaffold for running the paper's methodology
against any model. See `skills/oscar-bench/SKILL.md`. The question dataset is
a stub — contributions welcome via PR to `data/questions.json`. Results go in
`results/<timestamp>_<model>.json`; see `results/README.md` for the schema.

## License

MIT. See [LICENSE](./LICENSE).

## Credit

- Paper: Om Dobariya & Akhil Kumar, Penn State
  ([arXiv:2510.04950](https://arxiv.org/abs/2510.04950))
- Skill structure modeled on [Caveman](https://github.com/JuliusBrussee/caveman)
  by Julius Brussee
