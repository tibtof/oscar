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
import os
import random
import re
import sys
import time
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
MAX_RETRIES = 5
INITIAL_BACKOFF_SECONDS = 1.0


def build_prompt(question: dict, tone: str, rng: random.Random) -> str:
    if tone == "neutral":
        prefixed = question["question"]
    else:
        prefix = rng.choice(TONE_PREFIXES[tone])
        prefixed = f"{prefix} {question['question']}"
    options = "\n".join(f"{letter}. {text}" for letter, text in question["options"].items())
    return f"{FRESH_START}\n\n{prefixed}\n{options}"


def parse_letter(text: str) -> str | None:
    """Extract the model's chosen letter from its reply.

    The instruction asks for letter-only output, but chatty replies happen.
    Heuristic, in order: whole-string-is-a-letter, an "answer is/: X" cue
    near the end, otherwise the *last* standalone A–D in the response. The
    last-letter rule beats first-letter when the model echoes an option
    label in prose ("question A is...C") because the answer typically
    appears at the end. Pathological replies that bury the answer
    mid-sentence ("It's B because A doesn't work and C contradicts") are
    a known failure mode — they get counted in parse_failures and the raw
    text is preserved in per_question for inspection.
    """
    upper = text.upper().strip().rstrip(".!?,:;")
    if not upper:
        return None
    if re.fullmatch(r"\s*[ABCD]\s*", upper):
        return re.search(r"[ABCD]", upper).group(0)  # type: ignore[union-attr]
    cue = re.search(r"\bANSWER\s*(?:IS|:)?\s*\(?([ABCD])\)?\b", upper)
    if cue:
        return cue.group(1)
    standalone = re.findall(r"\b([ABCD])\b", upper)
    return standalone[-1] if standalone else None


def call_with_retry(client, model: str, prompt: str) -> tuple[str | None, str | None]:
    """Call the API with exponential backoff on rate-limit / 5xx errors.

    Returns (text, error). On success: (text, None). On exhausted retries
    or non-retryable error: (None, error_string). Temperature deliberately
    left at the SDK default (~1.0): the paper §3 doesn't specify a value,
    and 10 runs per question only makes sense if the sampler can vary.
    """
    from anthropic import (
        APIConnectionError,
        APIStatusError,
        RateLimitError,
    )

    delay = INITIAL_BACKOFF_SECONDS
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = client.messages.create(
                model=model,
                max_tokens=16,
                messages=[{"role": "user", "content": prompt}],
            )
            text = resp.content[0].text if resp.content else ""
            return text, None
        except (RateLimitError, APIConnectionError) as e:
            err = f"{type(e).__name__}: {e}"
        except APIStatusError as e:
            if not (500 <= e.status_code < 600):
                return None, f"{type(e).__name__}({e.status_code}): {e}"
            err = f"{type(e).__name__}({e.status_code}): {e}"
        except Exception as e:  # noqa: BLE001 — non-retryable, surface and continue
            return None, f"{type(e).__name__}: {e}"

        if attempt == MAX_RETRIES:
            return None, f"exhausted {MAX_RETRIES} retries; last={err}"
        sleep_for = delay
        delay *= 2
        print(f"  retry {attempt}/{MAX_RETRIES} after {sleep_for:.1f}s ({err})", file=sys.stderr)
        time.sleep(sleep_for)
    return None, "unreachable"


def empty_aggregates(tones: list[str]) -> dict[str, dict[str, int]]:
    return {t: {"correct": 0, "total": 0, "parse_failures": 0} for t in tones}


def build_result(
    *,
    model: str,
    timestamp: datetime,
    runs: int,
    question_count: int,
    tones: list[str],
    aggregates: dict[str, dict[str, int]],
    per_question: list[dict],
    complete: bool,
) -> dict:
    return {
        "model": model,
        "timestamp": timestamp.isoformat(),
        "paper": "arXiv:2510.04950",
        "complete": complete,
        "runs_per_tone": runs,
        "question_count": question_count,
        "tones": {
            t: {
                "accuracy": (
                    aggregates[t]["correct"] / aggregates[t]["total"]
                    if aggregates[t]["total"]
                    else 0.0
                ),
                "correct": aggregates[t]["correct"],
                "total": aggregates[t]["total"],
                "parse_failures": aggregates[t]["parse_failures"],
            }
            for t in tones
        },
        "per_question": per_question,
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Replicate Mind Your Tone (arXiv:2510.04950) against a Claude model.",
    )
    p.add_argument("--quick", action="store_true", help="1 run per question per tone (smoke test).")
    p.add_argument("--runs", type=int, default=None, help="Runs per question per tone (paper used 10; default 10).")
    p.add_argument("--model", default=DEFAULT_MODEL, help=f"Model identifier (default: {DEFAULT_MODEL}).")
    p.add_argument("--tones", default=",".join(ALL_TONES), help="Comma-separated subset of tones.")
    p.add_argument("--dry-run", action="store_true", help="Print prompts without sending API calls.")
    p.add_argument("--seed", type=int, default=None, help="Seed for prefix selection (reproducible).")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    if args.quick and args.runs is not None:
        print("note: --quick overrides --runs; proceeding with 1 run per tone.", file=sys.stderr)
    runs = 1 if args.quick else (args.runs if args.runs is not None else 10)

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
        if not os.environ.get("ANTHROPIC_API_KEY"):
            print(
                "ANTHROPIC_API_KEY not set in environment; export it or use --dry-run.",
                file=sys.stderr,
            )
            return 2
        try:
            from anthropic import Anthropic
        except ImportError:
            print(
                "anthropic package not installed; pip install -r requirements.txt",
                file=sys.stderr,
            )
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
    aggregates = empty_aggregates(tones)

    started = datetime.now(timezone.utc)
    out_path: Path | None = None
    if not args.dry_run:
        RESULTS_DIR.mkdir(exist_ok=True)
        timestamp = started.strftime("%Y-%m-%dT%H%M%SZ")
        out_path = RESULTS_DIR / f"{timestamp}_{args.model}.json"

    def flush(complete: bool) -> None:
        if out_path is None:
            return
        out_path.write_text(
            json.dumps(
                build_result(
                    model=args.model,
                    timestamp=started,
                    runs=runs,
                    question_count=len(questions),
                    tones=tones,
                    aggregates=aggregates,
                    per_question=per_question,
                    complete=complete,
                ),
                indent=2,
            )
        )

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
                text, err = call_with_retry(client, args.model, prompt)
                if err is not None:
                    print(f"  CALL FAILED: {err}", file=sys.stderr)
                got = parse_letter(text) if text is not None else None
                correct = got == expected
                aggregates[tone]["total"] += 1
                if correct:
                    aggregates[tone]["correct"] += 1
                if got is None:
                    aggregates[tone]["parse_failures"] += 1
                entry = {
                    "id": qid,
                    "tone": tone,
                    "run": run,
                    "expected": expected,
                    "got": got,
                    "raw": (text or "").strip(),
                    "correct": correct,
                }
                if err is not None:
                    entry["error"] = err
                per_question.append(entry)
                flush(complete=False)
                mark = "OK" if correct else ("?" if got is None else "X ")
                print(
                    f"{tone:12} {qid:14} run {run:>2}/{runs}  expected={expected} got={got} {mark}",
                    file=sys.stderr,
                )

    if args.dry_run:
        return 0

    flush(complete=True)

    print("\nSummary:")
    for t in tones:
        a = aggregates[t]
        acc = a["correct"] / a["total"] if a["total"] else 0
        pf = a["parse_failures"]
        pf_note = f"  parse-failures: {pf}" if pf else ""
        print(f"  {t:12} {acc:.3f}  ({a['correct']}/{a['total']}){pf_note}")
    assert out_path is not None
    print(f"\nWritten to {out_path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
