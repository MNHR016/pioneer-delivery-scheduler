# Pioneer Delivery Scheduler

Python project for scheduling deliveries and checking delivery data.
Needs Python 3.10 or newer. No packages to install.

## Part 1

Finds how many deliveries one driver can do, how many drivers are needed for all
of them, and how many requests would have to be rejected with one driver.

Run from this folder:

```bash
python3 -m delivery_scheduler data/deliveries.txt
```

You can add `--mode select`, `--mode drivers`, or `--mode reject` to run one option.

The input is `id,start,finish`, one delivery per line. Spaces work too.
IDs must be unique and start must be less than finish. Back-to-back deliveries
are allowed. The sample file gives 3 completed deliveries, 3 drivers, and 4 rejections.

## Part 2

Finds the closest two locations, counts changes in dispatch order, and finds
the kth smallest delivery time. The code and sample files are in `part2`.

```bash
cd part2
python3 -m delivery_analysis closest data/locations.json
python3 -m delivery_analysis inversions data/orders.json
python3 -m delivery_analysis select data/times.json
```

The sample results are a squared distance of 1, 2 inversions, and a time of 16.
See [part2/README.md](part2/README.md) for the input formats.

## Tests

Run this from the main folder for Part 1, or from `part2` for Part 2:

```bash
python3 -m unittest discover -s tests -v
```

Part 1 has 4 test methods and Part 2 has 14, with multiple cases in each.
