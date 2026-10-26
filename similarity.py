"""
Document Similarity & Plagiarism Analyzer  (main backend module)
================================================================

PIPELINE  (what happens when you compare two documents)

  1. PREPROCESS   lowercase, remove punctuation, split into words
                     "Hello, World!" -> ["hello", "world"]

  2. EXACT MATCH  (Naive / Rabin-Karp / KMP)
       - Cut Document 1 into overlapping 5-word phrases ("chunks").
       - Search each chunk inside Document 2 with the chosen algorithm.
       - Every word of Doc 1 that is inside a found chunk is "copied".
       exact_score = copied words / total words in Doc 1

  3. EDIT DISTANCE  (word-level DP)
       - How many word insert/delete/replace edits turn Doc 1 into Doc 2?
       edit_score = 1 - distance / max(len1, len2)

  4. LCS  (word-level DP)  - extra information, shows kept word order
       lcs_score = LCS length / max(len1, len2)

  5. FINAL SCORE
       final_score = w1 * exact_score + w2 * edit_score
       (default w1 = 0.6, w2 = 0.4)

  6. VERDICT
       >= 0.70  -> High similarity (likely plagiarised)
       >= 0.40  -> Moderate similarity (check manually)
       <  0.40  -> Low similarity (likely original)

HOW TO RUN  (PowerShell, from the project folder)
    python similarity.py data\\original.txt data\\copied.txt
    python similarity.py data\\original.txt data\\copied.txt --algo naive
    python similarity.py data\\original.txt data\\copied.txt --w1 0.5 --w2 0.5
"""

import argparse
import json
import re
import time

from naive_match import naive_search
from rabin_karp import rabin_karp_search
from kmp import kmp_search
from edit_distance import edit_distance
from lcs import lcs

# Map of algorithm names -> search functions (all have the same signature)
SEARCH_ALGORITHMS = {
    "naive": naive_search,
    "rabin_karp": rabin_karp_search,
    "kmp": kmp_search,
}

DEFAULT_CHUNK_SIZE = 5   # words per phrase used for exact matching


# ----------------------------------------------------------------------
# Step 1: Preprocessing
# ----------------------------------------------------------------------
def preprocess(text):
    """Lowercase, replace punctuation with spaces, return list of words."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)   # keep only letters, digits, spaces
    return text.split()


# ----------------------------------------------------------------------
# Step 2: Exact matching with a string-matching algorithm
# ----------------------------------------------------------------------
def exact_match_score(words1, words2, algorithm="kmp", chunk_size=DEFAULT_CHUNK_SIZE):
    """
    Returns (score, copied_passages).
    score           = fraction of Doc 1 words that appear in copied chunks
    copied_passages = list of copied phrases (strings) found in Doc 2
    """
    if not words1 or not words2:
        return 0.0, []

    search = SEARCH_ALGORITHMS[algorithm]
    k = min(chunk_size, len(words1))   # short documents use a smaller chunk

    # Join Doc 2 into one string. Spaces on both ends make sure we only
    # match WHOLE words (" cat " will not match inside " catalog ").
    text2 = " " + " ".join(words2) + " "

    copied = [False] * len(words1)     # copied[i] = True if word i was found

    # Slide a window of k words over Doc 1
    for start in range(len(words1) - k + 1):
        chunk = " " + " ".join(words1[start:start + k]) + " "
        if search(text2, chunk):                       # found at least once
            for i in range(start, start + k):
                copied[i] = True

    score = sum(copied) / len(words1)
    return score, _collect_passages(words1, copied)


def _collect_passages(words, copied):
    """Join runs of consecutive copied words into readable passages."""
    passages = []
    current = []
    for word, is_copied in zip(words, copied):
        if is_copied:
            current.append(word)
        elif current:
            passages.append(" ".join(current))
            current = []
    if current:
        passages.append(" ".join(current))
    return passages


# ----------------------------------------------------------------------
# Step 3 & 4: DP based scores
# ----------------------------------------------------------------------
def edit_distance_score(words1, words2):
    """Returns (score, distance). score = 1 - distance / longer length."""
    longest = max(len(words1), len(words2))
    if longest == 0:
        return 1.0, 0
    distance = edit_distance(words1, words2)
    return 1 - distance / longest, distance


def lcs_score(words1, words2):
    """Returns (score, lcs_length). score = LCS length / longer length."""
    longest = max(len(words1), len(words2))
    if longest == 0:
        return 1.0, 0
    length, _ = lcs(words1, words2)
    return length / longest, length


# ----------------------------------------------------------------------
# Step 5 & 6: Combine everything
# ----------------------------------------------------------------------
def get_verdict(score):
    if score >= 0.70:
        return "High similarity - likely plagiarised"
    if score >= 0.40:
        return "Moderate similarity - check manually"
    return "Low similarity - likely original"


def analyze(text1, text2, algorithm="kmp", w1=0.6, w2=0.4,
            chunk_size=DEFAULT_CHUNK_SIZE):
    """
    Compare two raw texts and return all results as a dictionary.
    (A dictionary converts directly to JSON, so the frontend can use it later.)
    """
    if algorithm not in SEARCH_ALGORITHMS:
        raise ValueError(f"Unknown algorithm '{algorithm}'. "
                         f"Choose from {list(SEARCH_ALGORITHMS)}")
    if w1 < 0 or w2 < 0 or (w1 + w2) == 0:
        raise ValueError("Weights must be non-negative and not both zero")

    # Normalise weights so they always add up to 1
    total = w1 + w2
    w1, w2 = w1 / total, w2 / total

    words1 = preprocess(text1)
    words2 = preprocess(text2)

    t0 = time.perf_counter()
    exact, passages = exact_match_score(words1, words2, algorithm, chunk_size)
    t1 = time.perf_counter()
    edit, distance = edit_distance_score(words1, words2)
    t2 = time.perf_counter()
    lcs_val, lcs_len = lcs_score(words1, words2)
    t3 = time.perf_counter()

    final = w1 * exact + w2 * edit

    return {
        "algorithm": algorithm,
        "weights": {"w1": round(w1, 3), "w2": round(w2, 3)},
        "word_counts": {"doc1": len(words1), "doc2": len(words2)},
        "exact_match_score": round(exact, 4),
        "edit_distance": distance,
        "edit_distance_score": round(edit, 4),
        "lcs_length": lcs_len,
        "lcs_score": round(lcs_val, 4),
        "final_score": round(final, 4),
        "verdict": get_verdict(final),
        "copied_passages": passages,
        "time_ms": {
            "exact_match": round((t1 - t0) * 1000, 3),
            "edit_distance": round((t2 - t1) * 1000, 3),
            "lcs": round((t3 - t2) * 1000, 3),
        },
    }


# ----------------------------------------------------------------------
# Command-line interface
# ----------------------------------------------------------------------
def print_report(result, name1, name2):
    line = "=" * 60
    print(line)
    print(" PLAGIARISM / SIMILARITY REPORT")
    print(line)
    print(f" Document 1 : {name1}  ({result['word_counts']['doc1']} words)")
    print(f" Document 2 : {name2}  ({result['word_counts']['doc2']} words)")
    print(f" Algorithm  : {result['algorithm']}")
    print(line)
    print(f" Exact match score   : {result['exact_match_score'] * 100:6.2f} %")
    print(f" Edit distance       : {result['edit_distance']} word edits")
    print(f" Edit distance score : {result['edit_distance_score'] * 100:6.2f} %")
    print(f" LCS length          : {result['lcs_length']} words")
    print(f" LCS score           : {result['lcs_score'] * 100:6.2f} %")
    print(line)
    w = result["weights"]
    print(f" FINAL SCORE = {w['w1']} x exact + {w['w2']} x edit"
          f" = {result['final_score'] * 100:.2f} %")
    print(f" VERDICT     : {result['verdict']}")
    print(line)
    if result["copied_passages"]:
        print(" Copied passages found in Document 2:")
        for p in result["copied_passages"]:
            print(f"   - \"{p}\"")
    else:
        print(" No copied passages found.")
    t = result["time_ms"]
    print(line)
    print(f" Time: exact {t['exact_match']} ms | edit {t['edit_distance']} ms"
          f" | lcs {t['lcs']} ms")
    print(line)


def main():
    parser = argparse.ArgumentParser(description="Compare two text documents.")
    parser.add_argument("doc1", help="path to the first (original) document")
    parser.add_argument("doc2", help="path to the second (suspected) document")
    parser.add_argument("--algo", default="kmp", choices=SEARCH_ALGORITHMS.keys(),
                        help="exact matching algorithm (default: kmp)")
    parser.add_argument("--w1", type=float, default=0.6, help="weight of exact match score")
    parser.add_argument("--w2", type=float, default=0.4, help="weight of edit distance score")
    parser.add_argument("--chunk", type=int, default=DEFAULT_CHUNK_SIZE,
                        help="words per phrase for exact matching (default: 5)")
    parser.add_argument("--json", action="store_true", help="print raw JSON output")
    args = parser.parse_args()

    with open(args.doc1, encoding="utf-8") as f:
        text1 = f.read()
    with open(args.doc2, encoding="utf-8") as f:
        text2 = f.read()

    result = analyze(text1, text2, args.algo, args.w1, args.w2, args.chunk)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result, args.doc1, args.doc2)


if __name__ == "__main__":
    main()
