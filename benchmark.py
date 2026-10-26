"""
Benchmarking Harness
====================

Measures how the running time of each algorithm grows with input size,
so we can check the theoretical Big-O against real numbers.

EXPERIMENTS
  1. String matching on RANDOM text     (naive, rabin_karp, kmp)
       Expectation: all three grow roughly linearly with n, because on
       random text the naive method usually mismatches on the 1st char.

  2. String matching on WORST-CASE text (naive, rabin_karp, kmp)
       text = "aaaa...a", pattern = "aaa...ab"  (m = 50)
       Expectation: naive does ~m comparisons at every position -> O(n*m),
       so it becomes much slower; KMP stays O(n + m).

  3. WORST CASE with growing PATTERN length m  (n fixed = 20,000)
       Expectation: naive time grows with m (it is O(n*m)),
       KMP and Rabin-Karp stay almost flat (O(n + m)).

  4. DP algorithms                      (edit distance, LCS)
       Two random word lists of size n each.
       Expectation: O(n^2)  ->  doubling n should make time ~4x.

HOW TO READ THE "RATIO" COLUMN
  ratio = time(current n) / time(previous n)
  When n doubles:  O(n) -> ratio ~2,   O(n^2) -> ratio ~4
  (Experiment 3 doubles m instead: naive ratio ~2, KMP ratio ~1)

HOW TO RUN  (PowerShell)
    python benchmark.py
  Results are saved in the report\\ folder (CSV table + PNG graphs).
"""

import csv
import os
import random
import string
import time

from naive_match import naive_search
from rabin_karp import rabin_karp_search
from kmp import kmp_search
from edit_distance import edit_distance
from lcs import lcs

REPORT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "report")
REPEATS = 3          # each measurement is the average of this many runs
random.seed(42)      # same random data every run -> reproducible results

MATCHERS = {
    "naive": naive_search,
    "rabin_karp": rabin_karp_search,
    "kmp": kmp_search,
}


def time_it(func, *args):
    """Average running time of func(*args) in milliseconds."""
    total = 0.0
    for _ in range(REPEATS):
        start = time.perf_counter()
        func(*args)
        total += time.perf_counter() - start
    return (total / REPEATS) * 1000


def random_text(n):
    return "".join(random.choice(string.ascii_lowercase) for _ in range(n))


def random_words(n):
    vocab = ["data", "cloud", "server", "user", "network", "code", "file",
             "system", "model", "query", "store", "cache", "node", "api"]
    return [random.choice(vocab) for _ in range(n)]


# ----------------------------------------------------------------------
# Experiments
# ----------------------------------------------------------------------
def experiment_random(sizes, m=10):
    rows = []
    for n in sizes:
        text = random_text(n)
        start = random.randint(0, n - m)
        pattern = text[start:start + m]          # guaranteed to occur
        for name, func in MATCHERS.items():
            rows.append(("random_text", name, n, time_it(func, text, pattern)))
    return rows


def experiment_worst(sizes, m=50):
    rows = []
    pattern = "a" * (m - 1) + "b"
    for n in sizes:
        text = "a" * n
        for name, func in MATCHERS.items():
            rows.append(("worst_case", name, n, time_it(func, text, pattern)))
    return rows


def experiment_pattern_length(pattern_sizes, n=20_000):
    rows = []
    text = "a" * n
    for m in pattern_sizes:
        pattern = "a" * (m - 1) + "b"
        for name, func in MATCHERS.items():
            rows.append(("worst_case_vary_m", name, m, time_it(func, text, pattern)))
    return rows


def experiment_dp(sizes):
    rows = []
    for n in sizes:
        a = random_words(n)
        b = random_words(n)
        rows.append(("dp", "edit_distance", n, time_it(edit_distance, a, b)))
        rows.append(("dp", "lcs", n, time_it(lcs, a, b)))
    return rows


# ----------------------------------------------------------------------
# Output: console table, CSV, plots
# ----------------------------------------------------------------------
def print_table(title, rows):
    print("\n" + title)
    print(f"  {'algorithm':<15}{'size':>8}{'time (ms)':>14}{'ratio':>9}")
    print("  " + "-" * 44)
    previous = {}
    for _, algo, n, ms in rows:
        ratio = f"{ms / previous[algo]:.2f}" if algo in previous and previous[algo] > 0 else "-"
        previous[algo] = ms
        print(f"  {algo:<15}{n:>8}{ms:>14.3f}{ratio:>9}")


def save_csv(rows, path):
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["experiment", "algorithm", "size", "time_ms"])
        for exp, algo, n, ms in rows:
            writer.writerow([exp, algo, n, round(ms, 4)])


def plot(rows, title, xlabel, path):
    try:
        import matplotlib
        matplotlib.use("Agg")          # save to file, no window needed
        import matplotlib.pyplot as plt
    except ImportError:
        print("  (matplotlib not installed - skipping plot. Run: pip install matplotlib)")
        return

    plt.figure(figsize=(7, 4.5))
    algorithms = []
    for _, algo, _, _ in rows:
        if algo not in algorithms:
            algorithms.append(algo)
    for algo in algorithms:
        xs = [n for _, a, n, _ in rows if a == algo]
        ys = [ms for _, a, _, ms in rows if a == algo]
        plt.plot(xs, ys, marker="o", label=algo)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("time (ms)")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()
    print(f"  saved plot -> {path}")


def main():
    os.makedirs(REPORT_DIR, exist_ok=True)

    match_sizes = [5_000, 10_000, 20_000, 40_000, 80_000]
    dp_sizes = [100, 200, 400, 800]

    print("Running benchmarks (average of", REPEATS, "runs each)...")

    r1 = experiment_random(match_sizes)
    print_table("1) String matching - random text (m = 10)", r1)

    r2 = experiment_worst(match_sizes)
    print_table("2) String matching - worst case 'aaa..a' vs 'aa..ab' (m = 50)", r2)

    r3 = experiment_pattern_length([10, 20, 40, 80, 160])
    print_table("3) Worst case, n = 20,000 fixed, size = pattern length m", r3)

    r4 = experiment_dp(dp_sizes)
    print_table("4) DP algorithms - two word lists of n words each", r4)

    print()
    save_csv(r1 + r2 + r3 + r4, os.path.join(REPORT_DIR, "benchmark_results.csv"))
    print(f"  saved table -> {os.path.join(REPORT_DIR, 'benchmark_results.csv')}")

    plot(r1, "String matching on random text (m = 10)", "text length n (characters)",
         os.path.join(REPORT_DIR, "matching_random.png"))
    plot(r2, "String matching worst case (m = 50)", "text length n (characters)",
         os.path.join(REPORT_DIR, "matching_worst_case.png"))
    plot(r3, "Worst case: growing pattern length (n = 20,000)", "pattern length m",
         os.path.join(REPORT_DIR, "matching_vary_pattern.png"))
    plot(r4, "Edit Distance vs LCS  (O(n^2))", "words per document n",
         os.path.join(REPORT_DIR, "dp_algorithms.png"))


if __name__ == "__main__":
    main()
