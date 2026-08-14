# IOL-AI 2026 competition results

These are the collected results of the IOL-AI 2026 competition: the 14 problems, the answer key, the scorer,
and one record per row of the leaderboard at [iolai.org](https://iolai.org).

The problems are the International Linguistics Olympiad's, taken from the Individual Contest at IOL 2026
([ioling.org](https://ioling.org)). This competition put them to language models instead of students.

Copyright for the problems remains at IOL. Authors for the [2026 problems and solutions](https://ioling.org/problems/by_year/#23) are Lai Otsuka, Dan-Mircea Mirea, Eimear McKnight, Vesko Milev.

## Repository structure

```
task/
    test.csv           the 14 problems
    solution.csv       the official answer key
    metric.py          the competition scorer
submissions/
    01_arvindcr4/      one directory per board row, named for its position
        metadata.json      team, rank, submission repo, submission comment
        metrics.json       every score, over the full test set and over the private split
        predictions.json   14 rows: prediction, per-item scores, explanation
    ...
    48_abhiandprusehf/
    code_sources.csv   a link to each team's code
leaderboard.csv        the board, all 48 rows, ranks and scores as on iolai.org
index.json             flat index of all 46 records. Start here.
TOP10.md               what the ten highest-ranked submissions did
```

Records are named for their board position, so `01_arvindcr4` is the winner and `48_abhiandprusehf` is last.
Ranks and scores follow [iolai.org](https://iolai.org) exactly.

### Board composition

The leaderboard has 48 rows, of which 42 are external teams with a scored submission. The remaining six are
organizer entries: `Tiny-Aya-R1`, which competed, four `Baseline-*` reference runs, and `iolai-test`. All rows
are ranked together, so the organizer entries occupy positions of their own, from 31 downward.

Two team counts should not be confused: 46 external teams submitted during the competition, and 42 of those
reached the board. Any figure reported per team should state which of the two it uses.

46 of the 48 rows have a record here. Positions 38 and 41 are baseline entries whose submission CSV was not
archived.

Each record includes an `archive_run_id`, for example `arvindcr4_run08`. This is the submission's identifier
in the competition archive, numbered over that team's successful runs, and is not a path.

## The problems and the answer key

`task/test.csv` and `task/solution.csv` are the competition's own files, copied in unmodified.

| File | Columns |
|---|---|
| `test.csv` | `id`, `context`, `query`, `work_lang`, `task_lang`, `task_type`, `eval_type`. No answers |
| `solution.csv` | `id`, `answer`, `split`, `points`, `task_type`, `eval_type` |

`context` holds the worked examples a solver reasons from and `query` is the instruction. `points` is the
row's weight in the score.

Each record embeds its own copy in `predictions.json`, where `query` is called `source` and `answer` is
called `target_text`. One trap: both are JSON-encoded **strings**. Run `json.loads` on them before comparing
with `predicted_items`, which is already a list. Some items accept alternatives, so a parsed item can itself
be a list.

## Scores

The metric is `score = sqrt(weighted_exact_match * weighted_chrF)`. Exact match is all or nothing per item
after normalisation, chrF is character n-gram overlap and gives partial credit, and the geometric mean of the
two rewards answers that are right rather than merely close. Items are averaged within a row, and rows are
weighted by their `points`.

The 14 problems come in two splits, marked in `solution.csv`. 8 rows were public, scored live on the board
during the competition. 6 rows were private and held back until the end. The final score covers all 14 rows,
public and private together, and that is the `score` field everywhere here. Each record also reports each split
on its own, with the same three numbers: `public_score`, `public_exact_match` and `public_chrf` over the 8
public rows, and `private_split_score`, `private_split_exact_match` and `private_split_chrf` over the 6
private ones.

The scorer itself is included, at `task/metric.py`, so any record can be rescored from its own
`predictions.json`. Every score here was produced with it from the archived submissions.

## Participants' code

The code is not copied here, it is linked. `submissions/code_sources.csv` has a link per record, and each
`metadata.json` repeats it as `code_url`. Every submission was a Hugging Face model repo, and the link points
at the exact revision that was scored, so it shows the repo as it stood at submission rather than whatever it
holds now. Where a repo has since been deleted, `code_backup` gives the archived copy instead.

## Reading the data

Plain JSON, no dependencies.

```python
import json, pathlib

index = json.loads(pathlib.Path("index.json").read_text())

for r in index["records"][:10]:                     # already in board order
    print(f"{r['rank']:>2}  {r['team']:20} {r['score'] * 100:5.2f}  {r['path']}")

run = pathlib.Path("submissions/01_arvindcr4")      # the winner
metadata = json.loads((run / "metadata.json").read_text())
metrics = json.loads((run / "metrics.json").read_text())
predictions = json.loads((run / "predictions.json").read_text())
```

Record scores are on a 0 to 1 scale. Multiply by 100 for the leaderboard scale used in `leaderboard.csv`.

Records match the shape of `iol-2026-explain`, the companion repo of frontier-model runs on the same 14
problems, and `score` means the same thing in both. Two differences when loading them together: a frontier
run keeps its files in `<model>/default/` and names the third `raw_outputs.json`, and its rows come in
varying order, so join on `id`.

**Records hold predictions, not traces.** The platform stored only the finished `submission.csv`, so the
prompts and reasoning behind each answer no longer exist, and nothing was reconstructed to fill the gap. That
is also why `generation_params` is `null`: decode settings lived in each team's script and were never
recorded. [`TOP10.md`](TOP10.md) covers the ten highest-ranked submissions, read from their code at the scored
revision.
