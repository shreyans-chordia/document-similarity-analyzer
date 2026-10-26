# Document Similarity & Plagiarism Detection Analyzer
**DAA Course Project (INT3101) · Backend**

A Python tool that compares two text documents and gives a plagiarism score.
It combines exact string matching (Naïve, Rabin-Karp, KMP) with dynamic-programming
approximate matching (Edit Distance, LCS), and it benchmarks every algorithm against its
theoretical Big-O.

Every algorithm is written from first principles. Only plain Python is used for the core logic.

---

## 1. Project structure

```
daa_project/
├── naive_match.py      Naïve string matching          O(n·m)
├── rabin_karp.py       Rabin-Karp (rolling hash)      O(n+m) average
├── kmp.py              Knuth-Morris-Pratt + LPS       O(n+m) always
├── edit_distance.py    Levenshtein distance (DP)      O(n·m)
├── lcs.py              Longest Common Subsequence     O(n·m)
├── similarity.py       MAIN: combines everything, gives score + verdict
├── benchmark.py        Times every algorithm, saves CSV + graphs
├── tests/              Unit tests (correctness)
├── data/               Sample documents to compare
└── report/             Benchmark output (CSV + PNG graphs)
```

---

## 2. How to run (Windows PowerShell)

**Step 1. Open PowerShell in the project folder**
```powershell
cd $HOME\Desktop\daa_project
```

**Step 2. (One time) Install matplotlib. It is only needed for the graphs.**
```powershell
pip install -r requirements.txt
```

**Step 3. Run each algorithm's small demo to see how it works**
```powershell
python naive_match.py
python rabin_karp.py
python kmp.py
python edit_distance.py
python lcs.py
```

**Step 4. Compare two documents**
```powershell
python similarity.py data\original.txt data\copied.txt
python similarity.py data\original.txt data\partial.txt
python similarity.py data\original.txt data\paraphrased.txt
python similarity.py data\original.txt data\unrelated.txt
```

Optional flags:
```powershell
python similarity.py data\original.txt data\copied.txt --algo naive        # naive | rabin_karp | kmp
python similarity.py data\original.txt data\copied.txt --w1 0.5 --w2 0.5   # change weights
python similarity.py data\original.txt data\copied.txt --json              # JSON output (for frontend)
```

**Step 5. Run the tests**
```powershell
python -m unittest discover tests -v
```

**Step 6. Run the benchmark**, which writes graphs to `report\`
```powershell
python benchmark.py
```

---

## 3. How the analyzer works (the pipeline)

```
 Doc 1 text ─┐
             ├─► 1. Preprocess ─► 2. Exact match (Naïve / RK / KMP) ─► exact_score ─┐
 Doc 2 text ─┘                    3. Edit distance (DP)            ─► edit_score  ─┼─► 5. final_score ─► 6. verdict
                                  4. LCS (DP)                      ─► lcs_score (extra info)
```

1. **Preprocess.** The text is lowercased, punctuation is removed and the text is split into words.
   `"Hello, World!"` becomes `["hello", "world"]`
2. **Exact match.** Doc 1 is cut into overlapping **5-word phrases**. Each phrase is searched
   for in Doc 2 using the chosen string-matching algorithm. Any word that falls inside a found
   phrase is marked as "copied".
   `exact_score = copied words / total words in Doc 1`
3. **Edit distance (word level).** This is the minimum number of word insertions, deletions and
   replacements needed to turn Doc 1 into Doc 2.
   `edit_score = 1 − distance / max(len1, len2)`
4. **LCS (word level).** This is the longest run of words that appears in both documents in the
   same order. It shows how much of the original word order was kept.
   `lcs_score = LCS length / max(len1, len2)`
5. **Final score**
   `final_score = w1 × exact_score + w2 × edit_score` (defaults: w1 = 0.6, w2 = 0.4)
6. **Verdict.** A score of 70% or more is **High** (likely plagiarised). A score from 40% up to
   70% is **Moderate** (check manually). A score under 40% is **Low** (likely original).

### Why combine two scores?
- **Exact matching** catches copy-paste. Even one changed word inside a phrase breaks that
  phrase's match.
- **Edit distance** catches documents that were lightly edited. A few word changes only lower
  the score a little.

### Results on the sample data
| Compared with `original.txt` | Exact | Edit | Final | Verdict |
|---|---|---|---|---|
| `copied.txt` (a few words changed) | 90.7% | 91.8% | **91.1%** | High |
| `partial.txt` (about half copied) | 42.3% | 44.3% | **43.1%** | Moderate |
| `paraphrased.txt` (same meaning, new words) | 0% | 13.3% | **5.3%** | Low |
| `unrelated.txt` | 0% | 6.2% | **2.5%** | Low |

**Limitation:** paraphrasing (same meaning, different words) is not detected. These are
string algorithms, so they compare words, not meaning. Detecting paraphrase would need NLP
(synonyms or embeddings), which is outside the scope of a DAA project.

---

## 4. The algorithms, explained briefly

| Algorithm | Main idea | Time | Space |
|---|---|---|---|
| **Naïve** | Try every position and compare characters one by one | O(n·m) worst | O(1) |
| **Rabin-Karp** | Compare hash *numbers*. The hash is rolled forward in O(1). Characters are checked only when the hashes are equal | O(n+m) avg, O(n·m) worst | O(1) |
| **KMP** | Precompute the LPS array. On a mismatch, jump the pattern forward and never move back in the text | O(n+m) always | O(m) |
| **Edit Distance** | `dp[i][j]` = cost to convert the first i items into the first j items. Take the min of insert, delete and replace | O(n·m) | O(n·m) |
| **LCS** | `dp[i][j]` = LCS of the prefixes. If the items match, add 1 to the diagonal. Otherwise take the max of the cell above and the cell to the left | O(n·m) | O(n·m) |

Each `.py` file has a detailed explanation and a worked example at the top.

---

## 5. Benchmark results: theory vs practice

`benchmark.py` runs 4 experiments. Each time is the average of 3 runs measured with
`time.perf_counter()`. The **ratio** column is time(this size) ÷ time(previous size). Because
each size is double the previous one, O(n) gives a ratio of about 2 and O(n²) gives about 4.

| # | Experiment | What theory says | What we observed |
|---|---|---|---|
| 1 | Random text, n doubles | All three are about linear | Ratios are about 2 for all three ✔ |
| 2 | Worst case `aaa…a` vs `aa…ab` (m = 50), n doubles | Naïve does m comparisons at each position | Naïve is about **18× slower** than KMP ✔ |
| 3 | Worst case, n fixed, **m doubles** | Naïve O(n·m) grows. KMP and RK O(n+m) stay flat | Naïve ratio is about **2.0**. KMP and RK ratios are about **1.0** ✔ |
| 4 | Edit distance & LCS, n doubles | O(n²) | Ratios are about **4** ✔ |

Graphs are saved in `report\`:
- `matching_random.png`
- `matching_worst_case.png`
- `matching_vary_pattern.png`, the clearest proof of O(n·m) vs O(n+m)
- `dp_algorithms.png`, which shows the quadratic curve

*Note: exact milliseconds depend on your laptop. The ratios and shapes are what matter.*

---

## 6. Using the backend from a frontend (next step)

`similarity.analyze(text1, text2, algorithm, w1, w2)` returns a Python dictionary
(JSON-ready), so a small Flask/FastAPI server or a Streamlit page can call it directly:

```python
from similarity import analyze
result = analyze(text1, text2, algorithm="kmp", w1=0.6, w2=0.4)
# result["final_score"], result["verdict"], result["copied_passages"], result["time_ms"], ...
```
