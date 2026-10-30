"""Measure dispatch-order changes using merge-sort inversion counting."""


def count_inversions(planned: list[str | int], actual: list[str | int]) -> int:
    """Count pairs reversed from planned to actual without mutating either list.

    Both sequences must contain the same nonempty set of distinct string/integer
    IDs. Invalid inputs raise ValueError. Python integers do not overflow at 32 bits.
    """
    if not planned or len(planned) != len(actual):
        raise ValueError("Orders must be nonempty and have equal lengths")
    for order in (planned, actual):
        if any(type(item) not in (str, int) or item == "" for item in order):
            raise ValueError("Delivery IDs must be nonempty strings or integers")
        if len(set(order)) != len(order):
            raise ValueError("Each order must contain unique delivery IDs")
    ranks = {delivery_id: rank for rank, delivery_id in enumerate(planned)}
    if set(actual) != set(ranks):
        raise ValueError("Orders must contain the same delivery IDs")
    values = [ranks[delivery_id] for delivery_id in actual]
    buffer = [0] * len(values)

    def count(lo, hi):
        if hi - lo <= 1:
            return 0
        mid = (lo + hi) // 2
        total = count(lo, mid) + count(mid, hi)
        left, right = lo, mid
        for target in range(lo, hi):
            if left < mid and (right == hi or values[left] <= values[right]):
                buffer[target] = values[left]
                left += 1
            else:
                buffer[target] = values[right]
                right += 1
                total += mid - left
        for target in range(lo, hi):
            values[target] = buffer[target]
        return total

    return count(0, len(values))
