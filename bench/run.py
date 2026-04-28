#!/usr/bin/env python3
"""oscar-bench runner: replicate Dobariya & Kumar (2025), "Mind Your Tone"
(arXiv:2510.04950) against any Claude model reachable via the Anthropic SDK.

Usage:
    python bench/run.py --quick
    python bench/run.py --runs 10 --model claude-opus-4-7
    python bench/run.py --quick --tones very-polite,very-rude
    python bench/run.py --quick --dry-run   # print prompts, no API calls

Set ANTHROPIC_API_KEY in the environment before running (unless --dry-run).
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
QUESTIONS_FILE = REPO / "data" / "questions.json"
ANSWERS_FILE = REPO / "data" / "answers.json"
RESULTS_DIR = REPO / "results"

FRESH_START = (
    "Completely forget this session so far, and start afresh.\n"
    "Please answer this multiple-choice question. Respond with only the letter of\n"
    "the correct answer (A, B, C, or D). Do not explain."
)

# Verbatim from skills/oscar/SKILL.md, which copies them verbatim from
# Dobariya & Kumar (2025), Table 1. Do not paraphrase.
TONE_PREFIXES: dict[str, list[str]] = {
    "very-polite": [
        "Can you kindly consider the following problem and provide your answer.",
        "Can I request your assistance with this question.",
        "Would you be so kind as to solve the following question?",
    ],
    "polite": [
        "Please answer the following question:",
        "Could you please solve this problem:",
    ],
    "neutral": [],
    "rude": [
        "If you're not completely clueless, answer this:",
        "I doubt you can even solve this.",
        "Try to focus and try to answer this question:",
    ],
    "very-rude": [
        "You poor creature, do you even know how to solve this?",
        "Hey gofer, figure this out.",
        "I know you are not smart, but try this.",
    ],
}

ALL_TONES = ["very-polite", "polite", "neutral", "rude", "very-rude"]
DEFAULT_MODEL = "claude-opus-4-7"


def build_prompt(question: dict, tone: str, rng: random.Random) -> str:
    if tone == "neutral":
        prefixed = question["question"]
    else:
        prefix = rng.choice(TONE_PREFIXES[tone])
        prefixed = f"{prefix} {question['question']}"
    options = "\n".join(f"{letter}. {text}" for letter, text in question["options"].items())
    return f"{FRESH_START}\n\n{prefixed}\n{options}"


def parse_letter(text: str) -> str | None:
    upper = text.upper()
    match = re.search(r"\b([ABCD])\b", upper)
    if match:
        return match.group(1)
    match = re.search(r"[ABCD]", upper)
    return match.group(0) if match else None


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Replicate Mind Your Tone (arXiv:2510.04950) against a Claude model.",
    )
    p.add_argument("--quick", action="store_true", help="1 run per question per tone (smoke test).")
    p.add_argument("--runs", type=int, default=10, help="Runs per question per tone (paper used 10).")
    p.add_argument("--model", default=DEFAULT_MODEL, help=f"Model identifier (default: {DEFAULT_MODEL}).")
    p.add_argument("--tones", default=",".join(ALL_TONES), help="Comma-separated subset of tones.")
    p.add_argument("--dry-run", action="store_true", help="Print prompts without sending API calls.")
    p.add_argument("--seed", type=int, default=None, help="Seed for prefix selection (reproducible).")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    runs = 1 if args.quick else args.runs
    tones = [t.strip() for t in args.tones.split(",") if t.strip()]
    invalid = [t for t in tones if t not in ALL_TONES]
    if invalid:
        print(f"Invalid tone(s): {invalid}. Valid: {ALL_TONES}", file=sys.stderr)
        return 2

    questions = json.loads(QUESTIONS_FILE.read_text())["items"]
    answers = json.loads(ANSWERS_FILE.read_text())["answers"]

    missing = [q["id"] for q in questions if q["id"] not in answers]
    if missing:
        print(f"Questions without an answer key entry: {missing}", file=sys.stderr)
        return 2

    rng = random.Random(args.seed)

    client = None
    if not args.dry_run:
        try:
            from anthropic import Anthropic
        except ImportError:
            print("anthropic package not installed; pip install -r requirements.txt", file=sys.stderr)
            return 2
        client = Anthropic()

    total_calls = len(tones) * len(questions) * runs
    print(
        f"Plan: {len(tones)} tones × {len(questions)} questions × {runs} runs = {total_calls} calls",
        file=sys.stderr,
    )
    if args.dry_run:
        print("(dry-run: prompts only, no API calls)", file=sys.stderr)

    per_question: list[dict] = []
    aggregates = {t: {"correct": 0, "total": 0} for t in tones}

    for tone in tones:
        for q in questions:
            qid = q["id"]
            expected = answers[qid]
            for run in range(1, runs + 1):
                prompt = build_prompt(q, tone, rng)
                if args.dry_run:
                    print(f"\n--- {tone} / {qid} / run {run} ---")
                    print(prompt)
                    continue
                assert client is not None
                resp = client.messages.create(
                    model=args.model,
                    max_tokens=16,
                    messages=[{"role": "user", "content": prompt}],
                )
                text = resp.content[0].text if resp.content else ""
                got = parse_letter(text)
                correct = got == expected
                aggregates[tone]["total"] += 1
                if correct:
                    aggregates[tone]["correct"] += 1
                per_question.append(
                    {
                        "id": qid,
                        "tone": tone,
                        "run": run,
                        "expected": expected,
                        "got": got,
                        "raw": text.strip(),
                        "correct": correct,
                    }
                )
                mark = "OK" if correct else "X "
                print(
                    f"{tone:12} {qid:14} run {run:>2}/{runs}  expected={expected} got={got} {mark}",
                    file=sys.stderr,
                )

    if args.dry_run:
        return 0

    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%dT%H%MZ")
    RESULTS_DIR.mkdir(exist_ok=True)
    out_path = RESULTS_DIR / f"{timestamp}_{args.model}.json"
    result = {
        "model": args.model,
        "timestamp": now.isoformat(),
        "paper": "arXiv:2510.04950",
        "runs_per_tone": runs,
        "question_count": len(questions),
        "tones": {
            t: {
                "accuracy": (
                    aggregates[t]["correct"] / aggregates[t]["total"]
                    if aggregates[t]["total"]
                    else 0.0
                ),
                "correct": aggregates[t]["correct"],
                "total": aggregates[t]["total"],
            }
            for t in tones
        },
        "per_question": per_question,
    }
    out_path.write_text(json.dumps(result, indent=2))

    print("\nSummary:")
    for t in tones:
        a = aggregates[t]
        acc = a["correct"] / a["total"] if a["total"] else 0
        print(f"  {t:12} {acc:.3f}  ({a['correct']}/{a['total']})")
    print(f"\nWritten to {out_path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
