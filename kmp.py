"""
Knuth-Morris-Pratt (KMP) String Matching
========================================

IDEA
    The naive method throws away what it already learned after a mismatch
    and moves the pattern only one step. KMP never moves backwards in the
    text. It pre-computes an LPS array that tells it how far it can safely
    jump the pattern after a mismatch.

LPS ARRAY  (Longest Proper Prefix which is also a Suffix)
    lps[i] = length of the longest proper prefix of pattern[0..i]
             that is also a suffix of pattern[0..i].

    Example: pattern = "ababc"
        index : 0 1 2 3 4
        char  : a b a b c
        lps   : 0 0 1 2 0
    lps[3] = 2 because "ab" is both a prefix and a suffix of "abab".

SEARCH
    Keep two pointers: i (text) and j (pattern).
      - characters match     -> move both forward
      - j reaches m          -> match found; set j = lps[j-1]
      - mismatch and j > 0   -> j = lps[j-1]   (i stays where it is!)
      - mismatch and j == 0  -> i += 1

COMPLEXITY  (n = len(text), m = len(pattern))
    Time  : O(m) to build LPS + O(n) to search  =  O(n + m)  ALWAYS
    Space : O(m) for the LPS array
"""


def build_lps(pattern):
    """Build the LPS (failure function) array for the pattern."""
    m = len(pattern)
    lps = [0] * m
    length = 0      # length of the current longest prefix-suffix
    i = 1

    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        elif length > 0:
            # Fall back to the previous shorter prefix-suffix (don't move i)
            length = lps[length - 1]
        else:
            lps[i] = 0
            i += 1

    return lps


def kmp_search(text, pattern):
    """Return a list of every index where `pattern` starts in `text`."""
    n = len(text)
    m = len(pattern)
    positions = []

    if m == 0 or m > n:
        return positions

    lps = build_lps(pattern)
    i = 0   # pointer in text
    j = 0   # pointer in pattern

    while i < n:
        if text[i] == pattern[j]:
            i += 1
            j += 1
            if j == m:                       # full match
                positions.append(i - m)
                j = lps[j - 1]               # keep looking for overlapping matches
        elif j > 0:
            j = lps[j - 1]                   # jump the pattern, text pointer stays
        else:
            i += 1

    return positions


if __name__ == "__main__":
    # Small demo:  python kmp.py
    print("LPS of 'ababc' :", build_lps("ababc"))      # [0, 0, 1, 2, 0]
    text = "abcabdabd"
    pattern = "abd"
    print("Text   :", text)
    print("Pattern:", pattern)
    print("Matches at:", kmp_search(text, pattern))   # [3, 6]
