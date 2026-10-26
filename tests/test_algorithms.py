"""
Correctness tests for every algorithm.

Run from the project folder (PowerShell):
    python -m unittest discover tests -v
"""

import os
import random
import sys
import unittest

# Let the tests import modules from the parent (project) folder
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from naive_match import naive_search
from rabin_karp import rabin_karp_search
from kmp import kmp_search, build_lps
from edit_distance import edit_distance
from lcs import lcs
from similarity import analyze, preprocess


def python_find_all(text, pattern):
    """Reference answer using Python's built-in str.find (only used for TESTING)."""
    positions = []
    start = text.find(pattern)
    while start != -1:
        positions.append(start)
        start = text.find(pattern, start + 1)
    return positions


class TestStringMatching(unittest.TestCase):
    ALGORITHMS = [naive_search, rabin_karp_search, kmp_search]

    def test_simple_cases(self):
        cases = [
            ("abcabdabd", "abd", [3, 6]),
            ("aaaaa", "aa", [0, 1, 2, 3]),     # overlapping matches
            ("hello world", "world", [6]),
            ("hello", "xyz", []),              # no match
            ("abc", "abcd", []),               # pattern longer than text
            ("abc", "", []),                   # empty pattern
        ]
        for algo in self.ALGORITHMS:
            for text, pattern, expected in cases:
                with self.subTest(algo=algo.__name__, text=text, pattern=pattern):
                    self.assertEqual(algo(text, pattern), expected)

    def test_cross_validation_random(self):
        """All three algorithms must agree with each other on random inputs."""
        random.seed(1)
        for _ in range(300):
            text = "".join(random.choice("ab") for _ in range(random.randint(0, 60)))
            pattern = "".join(random.choice("ab") for _ in range(random.randint(1, 5)))
            expected = python_find_all(text, pattern)
            for algo in self.ALGORITHMS:
                self.assertEqual(algo(text, pattern), expected,
                                 f"{algo.__name__} failed on {text!r}, {pattern!r}")

    def test_lps_array(self):
        self.assertEqual(build_lps("ababc"), [0, 0, 1, 2, 0])
        self.assertEqual(build_lps("aaaa"), [0, 1, 2, 3])
        self.assertEqual(build_lps("abcd"), [0, 0, 0, 0])
        self.assertEqual(build_lps("aabaaab"), [0, 1, 0, 1, 2, 2, 3])


class TestEditDistance(unittest.TestCase):
    def test_known_values(self):
        self.assertEqual(edit_distance("kitten", "sitting"), 3)
        self.assertEqual(edit_distance("flaw", "lawn"), 2)
        self.assertEqual(edit_distance("", "abc"), 3)
        self.assertEqual(edit_distance("abc", ""), 3)
        self.assertEqual(edit_distance("same", "same"), 0)

    def test_word_level(self):
        a = "the cat sat on the mat".split()
        b = "the cat sat on a mat".split()
        self.assertEqual(edit_distance(a, b), 1)


class TestLCS(unittest.TestCase):
    def test_known_values(self):
        self.assertEqual(lcs("ABCBDAB", "BDCABA")[0], 4)
        self.assertEqual(lcs("abc", "abc"), (3, ["a", "b", "c"]))
        self.assertEqual(lcs("abc", "xyz"), (0, []))
        self.assertEqual(lcs("", "abc"), (0, []))

    def test_word_level(self):
        a = "the quick brown fox".split()
        b = "the brown lazy fox".split()
        self.assertEqual(lcs(a, b), (3, ["the", "brown", "fox"]))


class TestSimilarity(unittest.TestCase):
    TEXT = ("Cloud computing lets companies rent servers and storage over "
            "the internet and pay only for what they use.")

    def test_preprocess(self):
        self.assertEqual(preprocess("Hello, World! It's 2026."),
                         ["hello", "world", "it", "s", "2026"])

    def test_identical_documents(self):
        result = analyze(self.TEXT, self.TEXT)
        self.assertEqual(result["final_score"], 1.0)

    def test_unrelated_documents(self):
        other = "The monsoon brings heavy rain to farmers across India every summer."
        result = analyze(self.TEXT, other)
        self.assertLess(result["final_score"], 0.4)

    def test_all_algorithms_give_same_score(self):
        modified = self.TEXT.replace("companies", "businesses")
        scores = {analyze(self.TEXT, modified, algorithm=a)["final_score"]
                  for a in ["naive", "rabin_karp", "kmp"]}
        self.assertEqual(len(scores), 1)

    def test_weights_are_normalised(self):
        result = analyze(self.TEXT, self.TEXT, w1=3, w2=1)
        self.assertEqual(result["weights"], {"w1": 0.75, "w2": 0.25})

    def test_empty_document(self):
        result = analyze("", self.TEXT)
        self.assertEqual(result["exact_match_score"], 0.0)


if __name__ == "__main__":
    unittest.main()
