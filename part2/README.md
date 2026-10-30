# Part 2

Three more delivery algorithms. Uses Python 3.10 or newer, no extra packages.
Run these commands from the `part2` folder.

## Running it

```bash
python3 -m delivery_analysis closest data/locations.json
python3 -m delivery_analysis inversions data/orders.json
python3 -m delivery_analysis select data/times.json
```

Each command reads a JSON file and prints the result as JSON.

## Input

Closest locations takes a list of `[id, x, y]` rows:

```json
[["A", 0, 0], ["B", 3, 4]]
```

It returns the two IDs and their squared distance, which is 25 here.
Use at least two points, integer coordinates, unique IDs, and no repeated
coordinates. If pairs tie, any closest pair can be returned.

Dispatch order takes the planned and actual lists:

```json
{"planned": ["A", "B", "C"], "actual": ["C", "A", "B"]}
```

This returns 2 inversions. Both lists need the same unique IDs and cannot be empty.
IDs can be strings or integers for both this and the location input.

Delivery times takes a list and a rank:

```json
{"times": [8, 3, 3], "k": 2}
```

This returns 3. Times must be nonnegative integers. `k` starts at 1 and cannot
be bigger than the list. Repeated times count separately. Bad input prints an error.

## How it works

- Closest pair splits the points in half and checks nearby points across the split. O(n log n).
- Inversions uses merge sort and counts pairs that are out of order. O(n log n).
- Selection uses median-of-medians with groups of five. O(n) worst case.

All three use O(n) extra space and leave the input unchanged.

## Testing

```bash
python3 -m unittest discover -s tests -v
python3 run_cases.py
python3 benchmark.py
```

There are 14 test methods. They cover the examples, invalid input, ties,
duplicates, and a reversed order of 100,000 IDs. Small random inputs are checked
against brute force or sorting too.

Test cases are in `tests/cases.json`. Saved outputs and timings are in `results`.
The benchmark tries 100, 1,000, and 5,000 items. Times depend on the computer.
