"""
Custom metric for the IOL-AI 2026 competition.

Final score (per public/private split) is the GEOMETRIC MEAN of two
points-weighted aggregates, reported on a 0-1 scale:

    chrf_mean = sum_i (points_i * mean_j chrF(pred_ij, gold_ij)) / sum_i points_i
    em_mean   = sum_i (points_i * mean_j EM(pred_ij, gold_ij))   / sum_i points_i
    score     = sqrt(chrf_mean * em_mean)

Each row in the test set is a complete subproblem (all items together).
The solution stores answers as a JSON list; for eval_type="multi" each
element is itself a list of acceptable alternatives (any match counts).

Predictions should be newline-separated, one answer per line, in order.
Leading "N. " or "N) " numbering is stripped before comparison.

Submissions may also include an optional "explanation" column. It is never
scored — it only feeds "explanation_rate", the percent of outputs that
included a non-empty explanation (powers the Human Evaluation Challenge).
"""

import json
import math
import re
import unicodedata
from collections import Counter


# --------------------------------------------------------------------------- #
# Text normalization
# --------------------------------------------------------------------------- #
def normalize_text(s):
    if s is None:
        return ""
    s = unicodedata.normalize("NFC", str(s))
    s = s.replace("’", "'").replace("‘", "'")
    s = s.strip()
    if len(s) >= 2 and s[0] in "\"'" and s[-1] == s[0]:
        s = s[1:-1].strip()
    s = s.lower()
    s = " ".join(s.split())
    s = s.rstrip(".")
    s = s.strip()
    return s


# --------------------------------------------------------------------------- #
# chrF (character n-gram F-score), self-contained
# --------------------------------------------------------------------------- #
def _char_ngrams(s, n):
    s = s.replace(" ", "")
    if len(s) < n:
        return Counter()
    return Counter(s[i:i + n] for i in range(len(s) - n + 1))


def chrf_score(hyp, ref, max_n=6, beta=2.0):
    if not hyp and not ref:
        return 1.0
    if not hyp or not ref:
        return 0.0
    p_orders, r_orders = [], []
    for n in range(1, max_n + 1):
        h = _char_ngrams(hyp, n)
        r = _char_ngrams(ref, n)
        h_total = sum(h.values())
        r_total = sum(r.values())
        matches = sum((h & r).values())
        if h_total > 0:
            p_orders.append(matches / h_total)
        if r_total > 0:
            r_orders.append(matches / r_total)
    if not p_orders or not r_orders:
        return 0.0
    chr_p = sum(p_orders) / len(p_orders)
    chr_r = sum(r_orders) / len(r_orders)
    if chr_p == 0 and chr_r == 0:
        return 0.0
    b2 = beta * beta
    denom = b2 * chr_p + chr_r
    if denom == 0:
        return 0.0
    return (1 + b2) * chr_p * chr_r / denom


# --------------------------------------------------------------------------- #
# Per-item scoring
# --------------------------------------------------------------------------- #
def item_scores(pred, gold_alts):
    """Score pred against a list of acceptable gold strings.
    Returns (exact_match, chrf) taking the best over alternatives."""
    p = normalize_text(pred)
    best_em, best_cf = 0.0, 0.0
    for gold in gold_alts:
        g = normalize_text(gold)
        em = 1.0 if p == g and g != "" else 0.0
        cf = chrf_score(p, g)
        if em > best_em:
            best_em = em
        if cf > best_cf:
            best_cf = cf
    return best_em, best_cf


def parse_pred_items(pred_str, n_items):
    """Split a prediction into a list of n_items individual answers.

    Accepts EITHER of the two formats participants actually use:
      * a JSON list, e.g. ["answer 1", "answer 2"]   (the documented format), or
      * newline-separated answers, one per line (with optional 'N.'/'N)' numbering).
    Pads with empty strings if short, truncates if long."""
    def _pad(items):
        items = list(items)
        if len(items) < n_items:
            items += [""] * (n_items - len(items))
        return items[:n_items]

    if not pred_str or not pred_str.strip():
        return [""] * n_items
    s = pred_str.strip()

    # Preferred: a JSON list of answers.
    try:
        parsed = json.loads(s)
        if isinstance(parsed, list):
            return _pad([("" if x is None else str(x)).strip() for x in parsed])
    except Exception:
        pass

    # Fallback: newline-separated answers, stripping leading 'N. ' / 'N) '.
    lines = [re.sub(r"^\d+[\.\)]\s*", "", ln).strip() for ln in s.split("\n")]
    lines = [ln for ln in lines if ln]
    return _pad(lines)


# --------------------------------------------------------------------------- #
# Aggregate over all rows in a split
# --------------------------------------------------------------------------- #
def aggregate(rows):
    """rows: list of dicts with keys em, cf, points.
    Returns dict with score / chrf / exact_match on a 0-1 scale (matching the
    competition docs: score = sqrt(weighted_exact_match * weighted_chrF))."""
    wsum = 0.0
    em_acc = 0.0
    chrf_acc = 0.0
    for row in rows:
        w = float(row.get("points", 1.0) or 0.0)
        wsum += w
        em_acc += w * row["em"]
        chrf_acc += w * row["cf"]
    if wsum == 0:
        return {"score": 0.0, "chrf": 0.0, "exact_match": 0.0}
    em_mean = em_acc / wsum
    chrf_mean = chrf_acc / wsum
    score = math.sqrt(max(em_mean, 0.0) * max(chrf_mean, 0.0))
    return {
        "score": round(score, 4),
        "chrf": round(chrf_mean, 4),
        "exact_match": round(em_mean, 4),
    }


# --------------------------------------------------------------------------- #
# Entry point called by the competitions library: metric.compute(params)
# --------------------------------------------------------------------------- #
def _download_with_retry(repo_id, filename, token, attempts=5):
    """hf_hub_download with retries on transient network failures.

    Scoring runs only AFTER the participant's script finishes, which can be 10+
    minutes into the eval Space's life. By then the keep-alive connection that
    huggingface_hub pooled during start-up has usually been dropped by the
    server, so the first request here fails with:

        ConnectionError(ProtocolError('Connection aborted.',
            RemoteDisconnected('Remote end closed connection without response')))

    That killed otherwise-successful submissions (their script had already
    exited 0) - it hit the slowest, heaviest runs hardest, because they leave
    the longest idle gap. Retrying with a fresh session fixes it: a dead pooled
    socket is discarded and the next attempt dials a new connection.

    EntryNotFoundError means the file genuinely is not there, so it is re-raised
    immediately rather than retried.
    """
    import time
    from huggingface_hub import hf_hub_download
    from huggingface_hub.utils import EntryNotFoundError

    last_err = None
    for attempt in range(attempts):
        try:
            return hf_hub_download(
                repo_id=repo_id, filename=filename, token=token,
                repo_type="dataset",
            )
        except EntryNotFoundError:
            raise
        except Exception as err:  # network / protocol / transient Hub errors
            last_err = err
            # Drop any stale pooled connections before retrying.
            try:
                from huggingface_hub.utils._http import reset_sessions
                reset_sessions()
            except Exception:
                pass
            if attempt < attempts - 1:
                time.sleep(2 ** attempt)  # 1s, 2s, 4s, 8s
    raise last_err


def compute(params):
    import pandas as pd

    idc = params.submission_id_col  # "id"

    from huggingface_hub.utils import EntryNotFoundError

    ANSWERS_REPO = "iol-ai-challenge/iol-ai-2026-answers"

    # The answer key is stored ZIPPED at rest so it is never a readable CSV
    # sitting in the dataset. Prefer solution.zip; fall back to a plaintext
    # solution.csv during the transition.
    try:
        solution_file = _download_with_retry(ANSWERS_REPO, "solution.zip", params.token)
        sol = pd.read_csv(solution_file, dtype=str, compression="zip").fillna("")
    except EntryNotFoundError:
        solution_file = _download_with_retry(ANSWERS_REPO, "solution.csv", params.token)
        sol = pd.read_csv(solution_file, dtype=str).fillna("")

    submission_file = _download_with_retry(
        params.competition_id,
        f"submissions/{params.team_id}-{params.submission_id}.csv",
        params.token,
    )
    sub = pd.read_csv(submission_file, dtype=str).fillna("")

    def canon(series):
        return series.astype(str).str.strip().str.lstrip("0").replace("", "0")

    sol["_k"] = canon(sol[idc])
    sub["_k"] = canon(sub[idc])
    pred_by_key = dict(zip(sub["_k"], sub["pred"]))
    explanation_by_key = (
        dict(zip(sub["_k"], sub["explanation"])) if "explanation" in sub.columns else {}
    )

    def score_row(r):
        gold_list = json.loads(r["answer"])
        is_multi = r.get("eval_type", "single") == "multi"
        pred_str = pred_by_key.get(r["_k"], "")
        pred_items = parse_pred_items(pred_str, len(gold_list))

        em_scores, cf_scores = [], []
        for pred_item, gold_item in zip(pred_items, gold_list):
            alts = gold_item if is_multi else [gold_item]
            em, cf = item_scores(pred_item, alts)
            em_scores.append(em)
            cf_scores.append(cf)

        n = len(em_scores)
        return {
            "em": sum(em_scores) / n,
            "cf": sum(cf_scores) / n,
            "points": float(r["points"]) if str(r["points"]).strip() else 1.0,
        }

    def split_rows(split):
        return [
            score_row(r)
            for _, r in sol[sol["split"].str.lower() == split].iterrows()
        ]

    pub_rows = split_rows("public")
    priv_rows = split_rows("private")
    public = aggregate(pub_rows)
    # Final (private) score spans BOTH the public and the private questions,
    # not just the held-out private split.
    private = aggregate(pub_rows + priv_rows)

    total = len(sol)
    valid_explanations = sum(
        1 for k in sol["_k"] if explanation_by_key.get(k, "").strip()
    )
    explanation_rate = round(100.0 * valid_explanations / total, 4) if total else 0.0
    public["explanation_rate"] = explanation_rate
    private["explanation_rate"] = explanation_rate

    return {"public_score": public, "private_score": private}
