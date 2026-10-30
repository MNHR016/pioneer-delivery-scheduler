"""Required examples, adversarial inputs, and independent small-input oracles."""

import json
from pathlib import Path
import random
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from delivery_analysis import Location, closest_pair, count_inversions, select_time

ROOT = Path(__file__).resolve().parents[1]
CASES = json.loads((ROOT / "tests/cases.json").read_text())


def brute_closest(points):
    return min((a.x - b.x) ** 2 + (a.y - b.y) ** 2
               for i, a in enumerate(points) for b in points[i + 1:])


def brute_inversions(planned, actual):
    ranks = {item: i for i, item in enumerate(planned)}
    return sum(ranks[actual[i]] > ranks[actual[j]]
               for i in range(len(actual)) for j in range(i + 1, len(actual)))


class ClosestTests(unittest.TestCase):
    def check_pair(self, points, expected):
        original = points.copy()
        pair, distance = closest_pair(points)
        self.assertEqual(distance, expected)
        self.assertEqual(len(set(pair)), 2)
        by_id = {point.id: point for point in points}
        a, b = (by_id[item] for item in pair)
        self.assertEqual((a.x - b.x) ** 2 + (a.y - b.y) ** 2, distance)
        self.assertEqual(points, original)
        return pair

    def test_examples(self):
        for case in CASES["closest"]:
            with self.subTest(case=case["name"]):
                pair = self.check_pair([Location(*row) for row in case["points"]], case["expected"])
                if "pair" in case:
                    self.assertCountEqual(pair, case["pair"])

    def test_random_against_brute_force(self):
        rng = random.Random(413)
        for trial in range(200):
            # A narrow x range deliberately creates many tied x-coordinates.
            coords = rng.sample([(x, y) for x in range(-3, 4) for y in range(-25, 26)], rng.randrange(2, 65))
            points = [Location(i, x, y) for i, (x, y) in enumerate(coords)]
            with self.subTest(trial=trial):
                self.check_pair(points, brute_closest(points))

    def test_large_integer_coordinates(self):
        value = 10 ** 100
        points = [Location("a", -value, 0), Location("b", value, 0),
                  Location("c", value + 1, 0), Location("d", 0, value)]
        self.check_pair(points, 1)

    def test_invalid_inputs(self):
        for points in ([], [Location("a", 0, 0)],
                       [Location("a", 0, 0), Location("a", 1, 2)],
                       [Location("a", 0, 0), Location("b", 0, 0)], [1, 2]):
            with self.subTest(points=points), self.assertRaises(ValueError):
                closest_pair(points)
        for args in (("a", 1.5, 0), ("a", True, 0), ([], 0, 0), ("", 0, 0)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                Location(*args)


class InversionTests(unittest.TestCase):
    def test_examples(self):
        for case in CASES["inversions"]:
            with self.subTest(case=case["name"]):
                self.assertEqual(count_inversions(case["planned"], case["actual"]), case["expected"])

    def test_large_count(self):
        planned = list(range(1, 100001))
        self.assertEqual(count_inversions(planned, planned[::-1]), 4_999_950_000)

    def test_random_against_nested_loops(self):
        rng = random.Random(414)
        for trial in range(200):
            planned = list(range(rng.randrange(1, 65)))
            rng.shuffle(planned)
            actual = rng.sample(planned, len(planned))
            before = (planned.copy(), actual.copy())
            with self.subTest(trial=trial):
                self.assertEqual(count_inversions(planned, actual), brute_inversions(planned, actual))
                self.assertEqual((planned, actual), before)

    def test_invalid_inputs(self):
        for planned, actual in (([], []), ([1], [1, 2]), ([1, 1], [1, 2]),
                                ([1, 2], [1, 1]), ([1, 2], [1, 3]), ([True], [True]),
                                ([[]], [[]]), ([""], [""])):
            with self.subTest(planned=planned, actual=actual), self.assertRaises(ValueError):
                count_inversions(planned, actual)


class SelectionTests(unittest.TestCase):
    def test_examples(self):
        for case in CASES["select"]:
            with self.subTest(case=case["name"]):
                self.assertEqual(select_time(case["times"], case["k"]), case["expected"])

    def test_random_all_ranks_against_sorting(self):
        rng = random.Random(415)
        for size in range(1, 65):
            values = [rng.randrange(20) for _ in range(size)]
            original = values.copy()
            for k, expected in enumerate(sorted(values), 1):
                with self.subTest(size=size, k=k):
                    self.assertEqual(select_time(values, k), expected)
                    self.assertEqual(values, original)

    def test_many_duplicates(self):
        values = [9, 0, 4, 4, 4] * 2000
        for k, expected in ((1, 0), (2000, 0), (2001, 4), (8000, 4), (8001, 9), (10000, 9)):
            with self.subTest(k=k):
                self.assertEqual(select_time(values, k), expected)

    def test_invalid_inputs(self):
        for values, k in (([], 1), ([1], 0), ([1], 2), ([1], True), ([1], 1.0),
                          ([-1, 2], 1), ([1.5], 1), ([True], 1), (["2"], 1)):
            with self.subTest(values=values, k=k), self.assertRaises(ValueError):
                select_time(values, k)


class CommandLineTests(unittest.TestCase):
    def run_cli(self, task, path):
        return subprocess.run([sys.executable, "-m", "delivery_analysis", task, str(path)],
                              cwd=ROOT, capture_output=True, text=True)

    def test_sample_files(self):
        for task, file, key, expected in (("closest", "locations", "distance_squared", 1),
                                         ("inversions", "orders", "inversions", 2),
                                         ("select", "times", "value", 16)):
            with self.subTest(task=task):
                result = self.run_cli(task, ROOT / "data" / f"{file}.json")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)[key], expected)

    def test_bad_files_and_shapes(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            for task in ("closest", "inversions", "select"):
                with self.subTest(task=task, input="missing"):
                    self.assertEqual(self.run_cli(task, path).returncode, 2)
            for data in ("not json", "null", "{}", "[1, 2]", '{"times": [1], "k": 0}'):
                path.write_text(data)
                for task in ("closest", "inversions", "select"):
                    with self.subTest(task=task, input=data):
                        result = self.run_cli(task, path)
                        self.assertEqual(result.returncode, 2)
                        self.assertIn("error:", result.stderr)
                        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
