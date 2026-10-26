"""
Longest Common Subsequence (LCS) - Dynamic Programming
======================================================

IDEA
    The longest sequence of items that appears in BOTH A and B
    in the same order, but not necessarily next to each other.

    A = "the quick brown fox".split()
    B = "the brown lazy fox".split()
    LCS = ["the", "brown", "fox"]   (length 3)

    In plagiarism detection this shows how much of the word ORDER
    was kept, even if some words were added or removed.

DP TABLE
    dp[i][j] = length of the LCS of the first i items of A
               and the first j items of B.

    Base case:  dp[0][j] = dp[i][0] = 0

    Recurrence:
        if A[i-1] == B[j-1]:  dp[i][j] = dp[i-1][j-1] + 1
        else:                 dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    To get the actual words we walk back from dp[n][m] (backtracking).

COMPLEXITY  (n = len(A), m = len(B))
    Time  : O(n * m) to fill the table + O(n + m) to backtrack
    Space : O(n * m)
"""


def lcs(a, b):
    """Return (length, common_subsequence_as_list) for sequences a and b."""
    n = len(a)
    m = len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    # Fill the table
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # Backtrack from the bottom-right corner to recover the subsequence
    sequence = []
    i, j = n, m
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            sequence.append(a[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    sequence.reverse()

    return dp[n][m], sequence


if __name__ == "__main__":
    # Small demo:  python lcs.py
    print(lcs("ABCBDAB", "BDCABA"))   # length 4
    a = "the quick brown fox".split()
    b = "the brown lazy fox".split()
    print(lcs(a, b))                  # (3, ['the', 'brown', 'fox'])
