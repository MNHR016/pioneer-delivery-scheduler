"""Measure median wall-clock time; input generation is outside the timed region."""

import json
import platform
import random
from statistics import median
from time import perf_counter

from delivery_analysis import Location, closest_pair, count_inversions, select_time


def main():
    rng = random.Random(416)
    rows = []
    for size in (100, 1000, 5000):
        # Unique sampled grid positions allow both x and y ties.
        grid = rng.sample(range(size * size), size)
        points = [Location(i, value // size, value % size) for i, value in enumerate(grid)]
        planned = list(range(size))
        actual = rng.sample(planned, size)
        times = [rng.randrange(size) for _ in range(size)]
        row = {"n": size}
        for task, function, args in (("closest", closest_pair, (points,)),
                                      ("inversions", count_inversions, (planned, actual)),
                                      ("select", select_time, (times, (size + 1) // 2))):
            function(*args)  # One warm-up per size and algorithm.
            samples = []
            for _ in range(7):
                start = perf_counter()
                function(*args)
                samples.append((perf_counter() - start) * 1000)
            row[f"{task}_ms"] = median(samples)
        rows.append(row)
    print(json.dumps({"python": platform.python_version(), "platform": platform.system(),
                      "machine": platform.machine(), "seed": 416, "repeats": 7,
                      "statistic": "median milliseconds", "sizes": rows}, indent=2))


if __name__ == "__main__":
    main()
