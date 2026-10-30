"""Run each delivery analysis independently using JSON input and output."""

import argparse
import json
from pathlib import Path

from . import Location, closest_pair, count_inversions, select_time


def main():
    parser = argparse.ArgumentParser(description="Analyze delivery locations, order, and times")
    parser.add_argument("task", choices=["closest", "inversions", "select"])
    parser.add_argument("file", type=Path, help="JSON input file (see README for each format)")
    args = parser.parse_args()
    try:
        data = json.loads(args.file.read_text(encoding="utf-8"))
        if args.task == "closest":
            if not isinstance(data, list):
                raise ValueError("Closest input must be a list of [id, x, y] locations")
            if any(not isinstance(row, list) or len(row) != 3 for row in data):
                raise ValueError("Each location must be [id, x, y]")
            pair, squared = closest_pair([Location(*row) for row in data])
            result = {"pair": pair, "distance_squared": squared}
        elif args.task == "inversions":
            if (not isinstance(data, dict) or not isinstance(data.get("planned"), list)
                    or not isinstance(data.get("actual"), list)):
                raise ValueError("Inversions input must contain planned and actual lists")
            result = {"inversions": count_inversions(data["planned"], data["actual"])}
        else:
            if (not isinstance(data, dict) or not isinstance(data.get("times"), list)
                    or "k" not in data):
                raise ValueError("Selection input must contain a times list and k")
            result = {"k": data["k"], "value": select_time(data["times"], data["k"])}
    except (OSError, UnicodeError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(result))


if __name__ == "__main__":
    main()
