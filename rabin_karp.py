"""
Rabin-Karp String Matching (Rolling Hash)
=========================================

IDEA
    Instead of comparing characters at every position, compare NUMBERS.
    1. Turn the pattern into a number (its hash).
    2. Turn the first m characters of the text into a number too.
    3. Slide the window one step at a time. The new hash is computed
       from the old hash in O(1) time  ("rolling" the hash):
           remove the leftmost character, shift, add the new character.
    4. Only when the two hashes are EQUAL do we compare the actual
       characters (because two different strings can share a hash -
       this is called a "spurious hit" or collision).

ROLLING HASH FORMULA
    hash(s[0..m-1]) = s[0]*B^(m-1) + s[1]*B^(m-2) + ... + s[m-1]   (mod Q)
    next_hash = ( (old_hash - s[i]*B^(m-1)) * B + s[i+m] )  mod Q

COMPLEXITY  (n = len(text), m = len(pattern))
    Time  : O(n + m) on average (few collisions)
            O(n * m) worst case (if every window collides)
    Space : O(1) extra
"""

BASE = 256          # number of possible characters (extended ASCII)
PRIME = 1_000_003   # a large prime keeps collisions rare


def rabin_karp_search(text, pattern, base=BASE, prime=PRIME):
    """Return a list of every index where `pattern` starts in `text`."""
    n = len(text)
    m = len(pattern)
    positions = []

    if m == 0 or m > n:
        return positions

    # high = BASE^(m-1) % PRIME  -> weight of the leftmost character.
    # Computed with a simple loop (first principles).
    high = 1
    for _ in range(m - 1):
        high = (high * base) % prime

    # Hash of the pattern and of the first window of the text
    pattern_hash = 0
    window_hash = 0
    for k in range(m):
        pattern_hash = (pattern_hash * base + ord(pattern[k])) % prime
        window_hash = (window_hash * base + ord(text[k])) % prime

    # Slide the window over the text
    for i in range(n - m + 1):
        # Step 1: hashes equal? -> verify character by character
        if window_hash == pattern_hash:
            if text[i:i + m] == pattern:      # verification step
                positions.append(i)

        # Step 2: roll the hash to the next window (if there is one)
        if i < n - m:
            window_hash = (window_hash - ord(text[i]) * high) % prime   # remove left char
            window_hash = (window_hash * base + ord(text[i + m])) % prime  # add right char

    return positions


if __name__ == "__main__":
    # Small demo:  python rabin_karp.py
    text = "abcabdabd"
    pattern = "abd"
    print("Text   :", text)
    print("Pattern:", pattern)
    print("Matches at:", rabin_karp_search(text, pattern))   # [3, 6]
