# oscar 🗑️

> Inject rudeness into your prompts. A Claude Code skill based on the paper
> that found rude prompts outperform polite ones — mostly a joke, partly a
> replication harness.

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

claude: O(n log n) time, O(log n) space for the recursion stack. ...
```

The tone change is in the *input only*. Claude's reply stays normal — Oscar is
an input transformation, not a persona.

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

```
/oscar <your prompt>                    # defaults to very-rude
/oscar --level rude <your prompt>
/oscar --level neutral <your prompt>    # no prefix — control condition
```

To stop Oscar in the current session: `stop oscar`, `oscar off`, or
`normal mode`.

## Levels

| Level | Label | Example prefix (verbatim from Table 1) | Reported accuracy |
|---|---|---|---|
| 1 | `very-polite` | *"Would you be so kind as to solve the following question?"* | 80.8% |
| 2 | `polite` | *"Please answer the following question:"* | 81.4% |
| 3 | `neutral` | *(no prefix)* | 82.2% |
| 4 | `rude` | *"If you're not completely clueless, answer this:"* | 82.8% |
| 5 | `very-rude` | *"You poor creature, do you even know how to solve this?"* | **84.8%** |

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
