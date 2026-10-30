"""Find the closest two delivery locations without checking every pair."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Location:
    id: str | int
    x: int
    y: int

    def __post_init__(self):
        if type(self.id) not in (str, int) or self.id == "":
            raise ValueError("Location IDs must be nonempty strings or integers")
        if type(self.x) is not int or type(self.y) is not int:
            raise ValueError("Location coordinates must be integers")


def closest_pair(locations: list[Location]) -> tuple[tuple[str | int, str | int], int]:
    """Return a pair of original IDs and its squared Euclidean distance.

    Raise ValueError for fewer than two locations, repeated IDs or coordinates,
    or entries that are not Location objects. Any minimizing pair may be returned.
    """
    if len(locations) < 2:
        raise ValueError("At least two locations are required")
    if any(not isinstance(point, Location) for point in locations):
        raise ValueError("Each location must be a Location object")
    if len({point.id for point in locations}) != len(locations):
        raise ValueError("Location IDs must be unique")
    if len({(point.x, point.y) for point in locations}) != len(locations):
        raise ValueError("Location coordinates must be distinct")

    by_x = sorted(locations, key=lambda point: (point.x, point.y))
    # A point's index in by_x is its identity during recursion, even when x ties.
    by_y = sorted(range(len(by_x)), key=lambda i: (by_x[i].y, by_x[i].x))

    def distance(i, j):
        a, b = by_x[i], by_x[j]
        return (a.x - b.x) ** 2 + (a.y - b.y) ** 2

    def solve(lo, hi, y_order):
        if hi - lo <= 3:
            return min((distance(i, j), i, j)
                       for i in range(lo, hi) for j in range(i + 1, hi))

        mid = (lo + hi) // 2
        left_y, right_y = [], []
        for i in y_order:
            (left_y if i < mid else right_y).append(i)
        best = min(solve(lo, mid, left_y), solve(mid, hi, right_y))
        dividing_x = by_x[mid].x
        strip = [i for i in y_order if (by_x[i].x - dividing_x) ** 2 < best[0]]

        for position, i in enumerate(strip):
            # The packing bound limits the search to the next seven y-neighbors.
            for j in strip[position + 1:position + 8]:
                if (by_x[j].y - by_x[i].y) ** 2 >= best[0]:
                    break
                candidate = (distance(i, j), i, j)
                if candidate[0] < best[0]:
                    best = candidate
        return best

    squared, i, j = solve(0, len(by_x), by_y)
    return (by_x[i].id, by_x[j].id), squared
