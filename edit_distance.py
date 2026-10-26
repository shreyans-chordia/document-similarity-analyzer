"""
Edit Distance (Levenshtein Distance) - Dynamic Programming
==========================================================

IDEA
    The minimum number of single-item edits needed to turn sequence A
    into sequence B. Allowed edits: INSERT, DELETE, REPLACE (each costs 1).

    It works on any sequence:
      - strings  -> edits are characters   ("kitten" -> "sitting" = 3)
      - lists    -> edits are whole words  (this is what the analyzer uses)

DP TABLE
    dp[i][j] = edit distance between the first i items of A
               and the first j items of B.

    Base cases:
        dp[i][0] = i   (delete all i items)
        dp[0][j] = j   (insert all j items)

    Recurrence:
        if A[i-1] == B[j-1]:
            dp[i][j] = dp[i-1][j-1]                 (no edit needed)
        else:
            dp[i][j] = 1 + min( dp[i-1][j],         (delete)
                                dp[i][j-1],         (insert)
                                dp[i-1][j-1] )      (replace)

    Answer: dp[n][m]

COMPLEXITY  (n = len(A), m = len(B))
    Time  : O(n * m)  - every cell is filled once
    Space : O(n * m)  - the full table
"""


def edit_distance(a, b):
    """Return the Levenshtein distance between sequences a and b."""
    n = len(a)
    m = len(b)

    # Create an (n+1) x (m+1) table filled with 0
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    # Base cases
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j

    # Fill the table row by row
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j],       # delete
                                   dp[i][j - 1],       # insert
                                   dp[i - 1][j - 1])   # replace

    return dp[n][m]


if __name__ == "__main__":
    # Small demo:  python edit_distance.py
    print("kitten -> sitting :", edit_distance("kitten", "sitting"))   # 3
    s1 = "the cat sat on the mat".split()
    s2 = "the cat sat on a mat".split()
    print("word level        :", edit_distance(s1, s2))                 # 1
