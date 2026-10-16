# Pioneer Delivery Scheduler

A small Python tool for planning deliveries when drivers and time slots are limited. It can pick the most jobs one driver can handle, split all jobs across the fewest drivers, and show which requests would need to be turned down.

The project uses greedy scheduling algorithms, so even a large list of delivery requests can be processed without trying every possible combination.

## Features

- **Single-driver planning:** keep the maximum number of non-overlapping requests.
- **Driver allocation:** assign every request using the minimum number of drivers.
- **Rejection planning:** find the smallest number of requests to reject with only one driver.
- **Simple data files:** read a whitespace-separated or comma-separated list of deliveries.
- **No dependencies:** runs with the Python standard library.

## Getting started

Requires **Python 3.10 or newer**. No installation or compilation needed.

```bash
python -m delivery_scheduler data/deliveries.txt
```

To run one feature at a time:

```bash
python -m delivery_scheduler data/deliveries.txt --mode select
python -m delivery_scheduler data/deliveries.txt --mode drivers
python -m delivery_scheduler data/deliveries.txt --mode reject
```

Run the tests:

```bash
python -m unittest discover -s tests -v
```

## Input file

Each line represents a delivery in the format `id,start,finish` (spaces also work). The header is optional, and lines starting with `#` are ignored.

```text
id,start,finish
D01,10,13
D02,2,5
D03,4,7
D04,1,8
D05,8,11
D06,11,14
D07,13,16
```

Times are integers; they could represent hours, minutes since midnight, or another consistent unit. Each start must be before its finish, and delivery IDs must be unique. A delivery starting exactly when another finishes **does not overlap**.

### Example result

With `data/deliveries.txt`, the single-driver schedule is:

```text
D02: 2 -> 5
D05: 8 -> 11
D06: 11 -> 14
Total completed: 3
```

Accepting all seven deliveries takes **3 drivers**. If only one driver is available, the minimum rejected count is **4**.

## How scheduling works

### 1. Max deliveries for one driver

The main greedy choice is to take the delivery that **finishes earliest** among the ones that are still compatible. First sort jobs by finish time, then work through them and keep a job whenever its start is at least the previous selected job's finish.

Why this works: consider any optimal schedule. If its first job finishes later than the earliest-finishing available job, we can swap that first job for the earlier-finishing one without losing room for anything afterward. Keep making the same choice for the remaining jobs. So choosing the earliest finish never reduces the best possible total.

Sorting is `O(n log n)`, and checking each delivery afterward is `O(n)`. Overall: **`O(n log n)`**.

### 2. Minimum drivers to accept all deliveries

Sort deliveries by start time. A **min-heap** stores `(finish_time, driver_number)` for each driver's most recent assignment. This makes it quick to find whichever driver becomes free first.

For each delivery:

1. If the earliest-free driver is available by the start time, give them the job.
2. Otherwise, add a new driver.
3. Push that driver's updated finish time into the heap.

Why it's minimal: we only add a driver when **every existing driver is still busy** at the next delivery's start. At that moment, all of those overlapping deliveries plus the new one need different drivers. No schedule could use fewer, so creating one more is necessary.

Sorting takes `O(n log n)` and each heap update is `O(log n)` over `n` jobs. Overall: **`O(n log n)`**.

### 3. Minimum rejected deliveries

This is the flip side of single-driver selection: if there are `n` requests and we can keep at most `k` compatible requests, we must reject exactly **`n - k`**. We reuse the earliest-finish algorithm rather than writing a separate scheduler. Overall: **`O(n log n)`**.

### 4. Why profit-first doesn't always work

Suppose flexible requests take one time slot each. A job has a ready time `R` and profit `P`. If it runs at time `T`, its value is `P / (1 + T - R)`. The proposed strategy takes requests in decreasing profit order and puts each into its earliest free slot after its ready time.

| Job | Ready time | Profit |
| --- | ---: | ---: |
| A | 0 | 10 |
| B | 0 | 9 |
| C | 1 | 8 |

**Profit-first greedy schedule:** A at slot 0, B at slot 1, C at slot 2.

- A: `10 / (1 + 0) = 10`
- B: `9 / (1 + 1) = 4.5`
- C: `8 / (1 + 1) = 4`
- **Total `V(G) = 18.5`**

**Better schedule:** A at slot 0, C at slot 1, B at slot 2.

- A: `10 / (1 + 0) = 10`
- C: `8 / (1 + 0) = 8`
- B: `9 / (1 + 2) = 3`
- **Total `V(S) = 21`**

Both schedules follow the ready-time and one-job-per-slot rules. Since `21 > 18.5`, the greedy strategy is **not always optimal**. The interesting part is that delaying B frees C to run right when it's ready, and the gain is bigger than B's lost value.

## Test results

These cases check empty data, single deliveries, back-to-back slots, overlapping requests, unsorted input, and equal finish times.

| Case | Single-driver maximum | Minimum drivers | Minimum rejected |
| --- | ---: | ---: | ---: |
| Empty input | 0 | 0 | 0 |
| One request `(1,3)` | 1 | 1 | 0 |
| Back-to-back `(1,3),(3,5),(5,7)` | 3 | 1 | 0 |
| All overlap `(1,5),(2,6),(3,7)` | 1 | 3 | 2 |

Additional required cases have different input sets for each feature:

| Feature | Test 5 | Test 6 |
| --- | --- | --- |
| Max selection | `(5,7),(1,3),(3,5),(2,4)` → **3** | `(1,4),(2,4),(4,6)` → **2** |
| Drivers | `(1,4),(2,5),(4,7),(5,8)` → **2** | `(5,8),(1,4),(2,5),(4,6),(6,9)` → **2** |
| Rejections | `(5,7),(1,3),(3,5),(2,4)` → **1** | `(1,2),(2,3),(3,4),(1,3)` → **1** |

All **18 required feature scenarios** are covered by `tests/test_scheduler.py`, along with input-validation tests.

## Project layout

```text
delivery-scheduler/
├── delivery_scheduler/
│   ├── __init__.py       # Public functions and data model
│   ├── __main__.py       # Command-line entry point
│   ├── io.py             # Reads delivery files
│   └── scheduler.py      # Scheduling algorithms
├── data/
│   └── deliveries.txt    # Sample requests
├── tests/
│   └── test_scheduler.py # Unit tests
├── .gitignore
└── README.md
```

## Possible improvements

Real delivery services also need to account for drive time, geographic location, driver shifts, and changing priorities. This first version treats each request as a fixed time interval and assumes any driver can take any delivery.
