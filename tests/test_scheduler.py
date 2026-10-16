"""Core scheduling checks, including all of the standard edge cases."""

import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from delivery_scheduler import Delivery, max_deliveries, assign_drivers, min_rejections
from delivery_scheduler.io import load_deliveries


def jobs(intervals):
    return [Delivery(f"D{i}", start, finish) for i, (start, finish) in enumerate(intervals, 1)]


class SelectionTests(unittest.TestCase):
    def test_required_cases(self):
        cases = [
            ([], 0),
            ([(1, 3)], 1),
            ([(1, 3), (3, 5), (5, 7)], 3),
            ([(1, 5), (2, 6), (3, 7)], 1),
            ([(5, 7), (1, 3), (3, 5), (2, 4)], 3),
            ([(1, 4), (2, 4), (4, 6)], 2),
        ]
        for intervals, expected in cases:
            with self.subTest(intervals=intervals):
                chosen = max_deliveries(jobs(intervals))
                self.assertEqual(len(chosen), expected)
                self.assertTrue(all(a.finish <= b.start for a, b in zip(chosen, chosen[1:])))


class DriverTests(unittest.TestCase):
    def test_required_cases(self):
        cases = [
            ([], 0),
            ([(1, 3)], 1),
            ([(1, 3), (3, 5), (5, 7)], 1),
            ([(1, 5), (2, 6), (3, 7)], 3),
            ([(1, 4), (2, 5), (4, 7), (5, 8)], 2),
            ([(5, 8), (1, 4), (2, 5), (4, 6), (6, 9)], 2),
        ]
        for intervals, expected in cases:
            with self.subTest(intervals=intervals):
                original = jobs(intervals)
                schedules = assign_drivers(original)
                self.assertEqual(len(schedules), expected)
                self.assertCountEqual([j.id for group in schedules for j in group],
                                      [j.id for j in original])
                for group in schedules:
                    self.assertTrue(all(a.finish <= b.start for a, b in zip(group, group[1:])))


class RejectionTests(unittest.TestCase):
    def test_required_cases(self):
        cases = [
            ([], 0),
            ([(1, 3)], 0),
            ([(1, 3), (3, 5), (5, 7)], 0),
            ([(1, 5), (2, 6), (3, 7)], 2),
            ([(5, 7), (1, 3), (3, 5), (2, 4)], 1),
            ([(1, 2), (2, 3), (3, 4), (1, 3)], 1),
        ]
        for intervals, expected in cases:
            with self.subTest(intervals=intervals):
                self.assertEqual(min_rejections(jobs(intervals))[0], expected)

    def test_invalid_input_and_file(self):
        with self.assertRaises(ValueError):
            Delivery("bad", 3, 3)
        with TemporaryDirectory() as temp:
            path = Path(temp) / "data.csv"
            path.write_text("id,start,finish\nA,1,3\nB,3,5\n")
            self.assertEqual(len(load_deliveries(path)), 2)
            path.write_text("A,1,3\nA,3,5\n")
            with self.assertRaises(ValueError):
                load_deliveries(path)


if __name__ == "__main__":
    unittest.main()
