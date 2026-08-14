# The ten highest-ranked submissions

The ten highest-ranked entries on the IOL-AI 2026 board (`leaderboard.csv`, the board live at
[iolai.org](https://iolai.org)). **Every team name links to their code at the exact revision that was
scored**, so anything below can be checked, and anything not mentioned can be looked up there. The same links
for all 48 board rows are in `submissions/code_sources.csv`.

Everything stated here was read from that code or computed from the archived predictions. Where a team's
setting comes from an environment variable, the value is the script's default, since the platform never
recorded the environment a run was given. Models were identified by comparing SHA-256 of the weight shards
against the upstream repo rather than by reading config labels. Several entries share code, and where that is
the case the entry says so; reusing public repositories was permitted under the rules. `attractordynamics`
deleted their repo after the competition, so their entry comes from the copy preserved in the organizer backup
bucket.

Scores are on a 0 to 100 scale over the full 14-row test set. `Public` is the same run's score on the 8 public
rows, which for ranks 8, 9 and 10 is lower than the public figure on the site, because the site shows each
team's best public run rather than the run that was scored. `Record` is the directory under `submissions/`.

| Rank | Team | Score | Public | EM | chrF | Model | Record |
|---:|---|---:|---:|---:|---:|---|---|
| 1 | [arvindcr4](https://huggingface.co/arvindcr4/iolai-2026-qwen25-14b-awq/tree/f283a4a3847ca2661a62473ed002c4f3ee496558) | **19.79** | 22.45 | 12.41 | 31.57 | Qwen2.5-14B AWQ | `01_arvindcr4` |
| 2 | [BigRatz](https://huggingface.co/BigRatz/LOL-AI-2026/tree/3586ae7605602cf5f968781bbdf0f6e31b5392fd) | **18.85** | 20.92 | 11.55 | 30.75 | Qwen2.5-14B AWQ | `02_BigRatz` |
| 3 | [hhhar](https://huggingface.co/hhhar/Linguist_should_be_smart_2/tree/2217a1da3316183530654356507f8b8bdaee9b1e) | **18.19** | 20.39 | 11.35 | 29.14 | Qwen2.5-14B AWQ | `03_hhhar` |
| 4 | [friedspaghetti](https://huggingface.co/divaspoudel/iol-Qwen2.5-14B-Instruct-AWQ/tree/9a98d495b69df65e382b0be9db7bc246852c5396) | **17.91** | 20.08 | 11.07 | 28.98 | Qwen2.5-14B AWQ | `04_friedspaghetti` |
| 5 | [mastermind](https://huggingface.co/gneupane/iol-Qwen2.5-14B-Instruct-AWQ/tree/fd051c9fb74e0869cf1ba906801ab881fa0c3586) | **16.73** | 18.22 | 10.07 | 27.78 | Qwen2.5-14B AWQ | `05_mastermind` |
| 6 | [Hul](https://huggingface.co/Lipas007/iol-ai-2026-qwen14b-awq/tree/da494d112735ccb6d49ec093cf102325e2134b60) | **16.72** | 18.28 | 9.84 | 28.41 | Qwen2.5-14B AWQ | `06_Hul` |
| 7 | [jbuaba](https://huggingface.co/jbuaba/iolai-2026-qwen25-14b/tree/f770fa3d494eb5a5eb5f543b5e34e725561c6e3f) | **16.51** | 17.82 | 9.84 | 27.68 | Qwen2.5-14B AWQ | `07_jbuaba` |
| 8 | attractordynamics | **15.85** | 17.01 | 9.12 | 27.56 | Qwen2.5-14B AWQ | `08_attractordynamics` |
| 9 | [LOPE-NTU](https://huggingface.co/richardlian/iolai-2026-4b-mist-oldv2/tree/ba789db20d369f197cae6ac4383199cf0aac6c2f) | **15.12** | 14.51 | 9.62 | 23.78 | Qwen3.5-4B Q8 GGUF | `09_LOPE-NTU` |
| 10 | [srikarkashyap](https://huggingface.co/srikarkashyap/medqa-14b-v2-explanations/tree/cd4d6782cd59fa63704b9115a2755ab267082707) | **14.67** | 14.92 | 7.98 | 26.99 | Qwen3-14B AWQ | `10_srikarkashyap` |

**1. [arvindcr4](https://huggingface.co/arvindcr4/iolai-2026-qwen25-14b-awq/tree/f283a4a3847ca2661a62473ed002c4f3ee496558), 19.79.**

* **Model** Qwen2.5-14B-Instruct in 4-bit AWQ. All three weight shards match the organizers' repo on SHA-256.
* **Prompt** the one the organizers published with the task: "You solve International Linguistics Olympiad
  problems. Answer every numbered item. Put each answer on its own line, in order, with no numbering and no
  extra text." It appears verbatim in eight of these ten scripts, including teams that share no other code. A
  longer prompt of their own, which frames the model as a gold medallist and asks it to segment morphemes and
  check every example, sits behind `IOL_BASELINE`, which defaults to on, so the elaborate path did not run. A
  header comment gives their reason: the organizers' reference script reached exact match 0.0729 on the hidden
  set "with THESE EXACT WEIGHTS" against their own best of 0.0333.
* **Repetition penalty** set to 1.0, in place of the 1.05 that ships in the organizers' weights. Their
  submission comment attributes their whole margin over the baseline, 9.40 to 19.79 on the same weights, to
  that one change. The penalty discourages reusing tokens already emitted, which on this exam falls on
  legitimate repetition: stems and affixes recurring across items, and forms that repeat syllables internally
  such as *kpedekpede* in the answer key. Exact match gives no partial credit, so a small shift away from the
  right form costs the whole item.
* **Decoding** greedy, `do_sample=False`. Output budget is
  `max(192, min(IOL_MAXNEW, 40 percent of the remaining time at 30 tokens per second))`, and `IOL_MAXNEW`
  defaults to 900. Input is truncated at 6,144 tokens.
* **Voting** up to 8 sampled passes at temperature 0.5, top_p 0.95, started only while the time left exceeds
  1.25 times the cost of the greedy pass. The greedy answer anchors every item; a sampled form replaces it only
  when at least two samples agree on it and it has strictly more support than the anchor. The docstring records
  why: an earlier version treating all candidates equally replaced the greedy answer about half the time and
  measured exact match 0.011 on their mock set against 0.044 for the anchored version.
* **Parsing** in the mode that ran, every non-empty line of the generation, with no forcing to the expected
  item count. The archived record shows item counts matching the key on 12 of the 14 rows.
* **Failure handling** a complete answer file is written before the model loads, with blank slots pre-filled
  with the question text, and rewritten after each stage. A final pass repairs rows whose item count is wrong or
  which contain blanks. 150 s is held back from the 30-minute limit.
* **Explanations** a separate greedy pass of 200 tokens per row, truncated to 1,200 characters, with up to
  300 s reserved for it.
* **Note** the file's header describes the baseline replication as using 512 tokens and their submission
  comment reports 512, but no code path produces that number, so `IOL_MAXNEW=512` must have been set in an
  environment the platform did not record.

**2. [BigRatz](https://huggingface.co/BigRatz/LOL-AI-2026/tree/3586ae7605602cf5f968781bbdf0f6e31b5392fd), 18.85.**

* **Model** Qwen2.5-14B AWQ in float16, loaded with `trust_remote_code=True`.
* **Decoding** greedy first pass at `IOL_MAXNEW=512` with `repetition_penalty=1.0` passed on every
  `generate()` call, plus shorter sub-passes of 300 and 200 tokens for the numeric task types.
* **Voting** up to 24 sampled passes at temperature 0.5, top_p 0.95, started only while the time left exceeds
  1.25 times the first pass. Per-item majority vote anchored on the greedy answer, which is replaced only when
  a form has at least two votes and more support than the anchor.
* **Time** `IOL_TIME_LIMIT=1800` and `IOL_SAFETY=150`, with a `Deadline` stopping criterion inside
  `generate()` that stops 10 s before the limit, batches skipped when under 25 s remain, and inputs truncated
  at 6,144 tokens.
* **Code** 12 top-level functions, all with minified names (`lg`, `lf`, `d1` to `d8`, `d11`, `main`). Only one
  name is shared with `arvindcr4`'s script, but the voting function reproduces its rule step by step, down to
  returning the anchor below three candidates and requiring at least two votes plus strictly more support than
  the anchor, and several constants coincide: the 1.25 time factor, the `min(300, 0.25 x first-pass cost + 60)`
  explanation reserve, the 150 s margin, the 6,144-token input cap, temperature 0.5 and top_p 0.95. On timing,
  `BigRatz` had been submitting since 21 July while `arvindcr4`'s first run was 25 July, but every `BigRatz` run
  through 25 July scored 10.00 or below and their scores move to 16.82 and above on 26 July, after
  `arvindcr4`'s 19.79 was on the public board.

**3. [hhhar](https://huggingface.co/hhhar/Linguist_should_be_smart_2/tree/2217a1da3316183530654356507f8b8bdaee9b1e), 18.19.**

* **Structure** a trimmed derivative of `arvindcr4`'s script, rebuilt as an A/B harness with flags for
  reasoning (`IOL_COT`), sample count and temperature.
* **Decoding** `MAX_NEW=900`, up to 24 samples at temperature 0.5, batch size 4, 30 tokens per second assumed
  for budgeting, `IOL_TIME_LIMIT=1800` with `IOL_SAFETY=150` and a per-token deadline check.
* **Removed from the parent** the matching solver and the bijection repair step, both recorded in the header as
  refuted on the hidden set.
* **Experiment log** the header lists each variant with the score it produced: 0.1959 for the configuration
  they shipped, .1826 for their own answer cleaner against raw lines, .127 for a single greedy pass without
  voting, .116 for per-task hints, .082 for forced item counts, and a match-letters logprob solver marked
  refuted.
* **Note** 0.1959 equals the public score of their earlier run `hhhar_run03`, 19.59, so the log is feedback
  from the 8 public rows.

**4. [friedspaghetti](https://huggingface.co/divaspoudel/iol-Qwen2.5-14B-Instruct-AWQ/tree/9a98d495b69df65e382b0be9db7bc246852c5396), 17.91.**

* **Structure** a rewrite of the same design, 38 KB against the parent's 34 KB, sharing 5 of 21 function names
  and keeping the parent's opening docstring line. The docstring is replaced by a changelog of their own
  changes.
* **Voting** samples are clustered by chrF similarity rather than exact normalised match, so near-identical
  forms count as one vote. Sampling is convergence-aware: once every item in a problem block has a majority,
  that block is dropped from later rounds.
* **Decoding** `MAX_NEW=900`, up to 8 samples at temperature 0.5, top_p 0.95, `repetition_penalty=1.0` set
  explicitly with a comment noting that some AWQ chat models ship a penalty in their config.
* **Task handling** the matching assignment solver is kept, on the stated grounds that free-form generation on
  permutation tasks tends to emit the identity ordering, and is reused for "which digit" tasks. Item-count
  detection also reads lowercase sub-item letters and fill-in-the-blank underscores.
* **Engineering** batch size is chosen from a token-length probe run after the tokenizer loads rather than from
  a fixed guess, and the script computes its own exact match and chrF locally.
* **Volume** 62 archived runs, the most of any external team and level with the organizers' Tiny-Aya-R1 entry,
  against a median of 12 runs per team.

**5. [mastermind](https://huggingface.co/gneupane/iol-Qwen2.5-14B-Instruct-AWQ/tree/fd051c9fb74e0869cf1ba906801ab881fa0c3586), 16.73.** `arvindcr4`'s file verbatim apart from nine removed blank lines, with all 19
top-level functions identical, submitted about 28 hours later. It scored 3.06 lower, so gaps of one to three
points anywhere on this board are within run-to-run variation for identical code. A fourth copy sits outside
the ten: `macbook`, at rank 26, is the same file with the comments and docstring stripped out.

**6. [Hul](https://huggingface.co/Lipas007/iol-ai-2026-qwen14b-awq/tree/da494d112735ccb6d49ec093cf102325e2134b60), 16.72.**

* **Model** Qwen2.5-14B AWQ in float16 with `device_map="auto"`, loaded from the repo directory.
* **Decoding** one greedy pass at `IOL_MAX_NEW_TOKENS=512`, no sampling and no voting anywhere.
  `repetition_penalty` is never mentioned in the script, so the 1.05 in their model repo's
  `generation_config.json` applied.
* **Parsing** every non-empty line of the generation, followed by normalisation per task type. The file labels
  itself "v8".
* **Explanations** two phases. Phase 1 writes a per-row note assembled from the problem itself: task type,
  language, a 90-character preview of the query and the first three answers, so no two rows repeat a sentence.
  Phase 2 replaces those with model-generated sentences for as many rows as time allows, 48 tokens each,
  stopping with 20 s left and truncating at 320 characters. Their explanation rate of 100% therefore mixes the
  two sources.
* **Time** a soft deadline of 1,650 s, with a look-ahead that stops answering rows once the elapsed time plus
  8 s per remaining row would overrun it.
* **Note** the script is documented in Spanish.

**7. [jbuaba](https://huggingface.co/jbuaba/iolai-2026-qwen25-14b/tree/f770fa3d494eb5a5eb5f543b5e34e725561c6e3f), 16.51.**

* **Structure** a package rather than a single file: `solver/model.py` (202 lines), `solver/matching.py` (173),
  `solver/minimal.py` (139) and `solver/items.py` (96), behind a 5.7 KB `script.py`.
* **Model** Qwen2.5-14B loaded fully offline (`HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`) with an
  `assert_gpu_resident` check that the weights are on the GPU.
* **Decoding** `apply_greedy_decoding()` sets `do_sample=False` and `repetition_penalty=1.0` on the generation
  config and clears `temperature`, `top_p`, `top_k` and `typical_p`, and each generate call passes
  `repetition_penalty=1.0` again with a 512-token default. Their repo's own `generation_config.json` also sets
  1.0.
* **Instrumentation** the value of `generation_config.repetition_penalty` observed at run time is printed to
  the log, along with the soft deadline for each row.
* **Explanations** a separate pass asking for "2-4 short bullet points explaining the answer, human-readable,
  not a chain of thought", capped at 96 tokens and given up to 2,000 characters of the generation as context.
* **Time** the 30-minute limit with a 150 s safety margin, and 300 s reserved for the explanation pass.

**8. attractordynamics, 15.85.**

* **Models** two of 9.99 GB each, 19.98 GB together by their own manifest: Qwen2.5-14B-Instruct-AWQ for the
  solve stage and Qwen3-14B-AWQ for a letter-matching stage, each run in its own subprocess so one frees the
  GPU before the other loads. Their shipped `SUBMIT_MODEL_SAMPLE_SHA256.txt` gives a SHA-256 for the first
  shard of each and both match upstream, the solve model being the organizers' baseline.
* **Code** 20 Python files, 460 KB, of hand-written rule checkers containing no model: parse the example table,
  align characters to find what changed, keep a rule only on an unambiguous majority, then regenerate every
  example from the rule and abstain on a single mismatch.
* **Prompt** their own, not the organizers': "Solve the linguistic problem. Use only the given data. Answer
  the query with one answer per line, in the order requested."
* **Decoding** greedy, `do_sample=False`. `repetition_penalty` is not mentioned in any of the 20 files, so the
  1.05 in the baseline weights applied. The solver caps output at `IOL_MAX_NEW_TOKENS`, default 1,536, while
  the runner passes 768 unless told otherwise.
* **Disabled by default** the entry point turns off stream memory, both sidecars, translation refinement and
  the second model, the last with the comment "Default off: Qwen3 match load OOMs/crashes eval; Alabama-only is
  fail-soft". The letter-match model was uploaded, 9.99 GB of weights, and disabled in the same file.
* **What ran** their run log, recorded at the time, shows the rule modules did not override the model's answers
  and the matching module locked nothing. 14 of their 26 archived runs scored identically to the decimal, and
  the scored run is the earliest of them, from 19 July; the best of the later ones reached 15.90.
* **Self-reporting** the submission ships per-file checksums and a `MANIFEST.json` recording the local run it
  was built from: 22 of 122 answers exact, 4 of 20 rows complete, 218.7 seconds, marked "LOCAL only; not
  official leaderboard".

**9. [LOPE-NTU](https://huggingface.co/richardlian/iolai-2026-4b-mist-oldv2/tree/ba789db20d369f197cae6ac4383199cf0aac6c2f), 15.12.**

* **Model** a 4.48 GB 8-bit GGUF, `model/model-Q8_0.gguf`, run on a bundled build of `llama.cpp`. Its GGUF
  metadata gives `general.architecture=qwen35` and `general.size_label=4.2B`, 32 blocks at 2,560 hidden, and
  names the model "E36 Merged", so it is a merge of their own rather than a stock release. It is under a third
  the size of the models the other nine ran.
* **Structure** the scored `script.py` is a 684-byte wrapper that sets environment defaults and calls their own
  package. The repo holds 71 Python files: 11 in `v2/` and 59 vendored libraries, so the sandbox's own versions
  could not interfere.
* **Configuration** `PROMPT_MODE=direct`, `N_SAMPLES=5`, `MAX_NEW=700`, `LLAMA_CTX=6144`, `FEWSHOT=0`,
  `THINK=0`, `REFINE_ROUNDS=0`. Thinking, few-shot prompting and refinement rounds were all built and all
  switched off. The docstring still says `N=3` while the code sets 5.
* **Prompt** in direct mode, a short instruction to return bare JSON with no reasoning. A two-stage induction
  prompt that teaches a method and caps reasoning at 300 words is in the package but not on the path that ran.
* **Decoding** five samples combined by per-item majority vote. No penalty is passed to the llama-cpp
  bindings, so the vendored default of 1.0 applied. Their transformers backend sets 1.05, but it is not the
  path that ran.
* **Scores** their chrF of 23.78 is the lowest in the ten while their exact match of 9.62 is higher than the
  row above them.
* **Explanations** none. Their explanation rate is 0%, the only such case in the ten.

**10. [srikarkashyap](https://huggingface.co/srikarkashyap/medqa-14b-v2-explanations/tree/cd4d6782cd59fa63704b9115a2755ab267082707), 14.67.**

* **Model** Qwen3-14B in 4-bit AWQ. Both shards match `Qwen/Qwen3-14B-AWQ` on SHA-256.
* **Getting it to load** the model would not load in the sandbox, so the repo carries a wheelhouse with
  transformers 4.51.3, tokenizers 0.21.1, huggingface_hub 0.30.2 and autoawq 0.2.9, installed with
  `pip install --no-index --no-deps` so nothing touches the network. Their header credits the two public repos
  they took this and their prompt from, `workerplacemint/iol-ai-2026-qwen3-14b-awq` and
  `ajinkyamulay/iolai-qwen3-14b-awq-push`, the second belonging to `randomizer` at rank 12, and states that
  their prompt is a verbatim copy of the Pass-1 path those repos annotate as scoring 0.1470 in public. The
  archive agrees: `randomizer`'s scored run has a public score of 14.70.
* **Decoding** one greedy answer plus 2 sampled candidates at temperature 0.7, top_p 0.8, top_k 20, which
  their script identifies as Qwen3's own recommended non-thinking settings. Sampling seeds are derived from the
  row id and the sample index, so their sampling is reproducible.
* **Voting** item-level majority against the greedy baseline. A candidate enters the vote only if its item
  count matches the structurally inferred expected count, and ties keep the greedy answer.
* **Budget** scales with the question: 48 tokens per expected answer plus 128, floor 512, cap 1,536. Sampled
  candidates are given between 20 and 90 seconds each and are skipped when the per-row budget is too small.
* **Matching questions** generation is restricted to the legal option letters, whitespace and end-of-sequence
  by a `prefix_allowed_tokens_fn` built from decoded token text rather than fixed token ids, which makes an
  invalid answer impossible rather than unlikely.
* **Note** `repetition_penalty` is never set in the script, and `Qwen/Qwen3-14B-AWQ` leaves it at 1.0, so this
  entry got the setting the Qwen2.5 teams had to make themselves.
* **Volume** 53 archived runs.
