"""Print reproducible example inputs and checked outputs as JSON."""

import json
from pathlib import Path

from delivery_analysis import Location, closest_pair, count_inversions, select_time


def main():
    cases = json.loads((Path(__file__).parent / "tests/cases.json").read_text())
    results = []
    for task, examples in cases.items():
        for case in examples:
            row = {"task": task, **case}
            if task == "closest":
                pair, value = closest_pair([Location(*point) for point in case["points"]])
                row["returned_pair"] = pair
                assert "pair" not in case or set(pair) == set(case["pair"])
            elif task == "inversions":
                value = count_inversions(case["planned"], case["actual"])
            else:
                value = select_time(case["times"], case["k"])
            assert value == case["expected"], case["name"]
            row["output"] = value
            results.append(row)
    planned = list(range(1, 100001))
    large_count = count_inversions(planned, planned[::-1])
    assert large_count == 4_999_950_000
    results.append({"task": "inversions", "name": "B6_large_count", "input": "planned=list(range(1, 100001)); actual=planned[::-1]", "expected": 4_999_950_000, "output": large_count})
    for k, expected in ((1, 0), (2000, 0), (2001, 4), (8000, 4), (8001, 9), (10000, 9)):
        value = select_time([9, 0, 4, 4, 4] * 2000, k)
        assert value == expected
        results.append({"task": "select", "name": "C9_many_duplicates", "input": "[9, 0, 4, 4, 4] * 2000", "k": k, "expected": expected, "output": value})
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
