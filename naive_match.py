"""
Naive (Brute-Force) String Matching
===================================

IDEA
    Slide the pattern over the text one position at a time.
    At every position, compare the characters one by one.
    If all m characters match, we found an occurrence.

EXAMPLE
    text    = "abcabd"
    pattern = "abd"
    i=0: "abc" vs "abd" -> mismatch at 3rd char
    i=1: "bca" vs "abd" -> mismatch at 1st char
    i=2: "cab" vs "abd" -> mismatch at 1st char
    i=3: "abd" vs "abd" -> MATCH at index 3

COMPLEXITY  (n = len(text), m = len(pattern))
    Time  : O((n - m + 1) * m)  ->  O(n * m) in the worst case
            (worst case: text = "aaaa...a", pattern = "aaa...ab")
    Space : O(1) extra (apart from the list of results)
"""


def naive_search(text, pattern):
    """Return a list of every index where `pattern` starts in `text`."""
    n = len(text)
    m = len(pattern)
    positions = []

    if m == 0 or m > n:
        return positions

    # Try every possible starting position i
    for i in range(n - m + 1):
        j = 0
        # Compare character by character until a mismatch
        while j < m and text[i + j] == pattern[j]:
            j += 1
        # If we compared all m characters without a mismatch -> match
        if j == m:
            positions.append(i)

    return positions


if __name__ == "__main__":
    # Small demo:  python naive_match.py
    text = "abcabdabd"
    pattern = "abd"
    print("Text   :", text)
    print("Pattern:", pattern)
    print("Matches at:", naive_search(text, pattern))   # [3, 6]
