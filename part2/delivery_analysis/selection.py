"""Select a delivery-time threshold with deterministic median-of-medians."""


def select_time(times: list[int], k: int) -> int:
    """Return the kth smallest time, using a 1-based rank and counting duplicates.

    The input is not changed. Empty input, noninteger/negative times, and invalid
    ranks raise ValueError. Sorting is limited to groups of at most five values.
    """
    if not times:
        raise ValueError("At least one delivery time is required")
    if any(type(value) is not int or value < 0 for value in times):
        raise ValueError("Delivery times must be nonnegative integers")
    if type(k) is not int or not 1 <= k <= len(times):
        raise ValueError("k must be an integer between 1 and the number of times")

    def select(values, rank):
        if len(values) <= 5:
            return sorted(values)[rank - 1]
        medians = []
        for start in range(0, len(values), 5):
            group = sorted(values[start:start + 5])
            medians.append(group[len(group) // 2])
        pivot = select(medians, (len(medians) + 1) // 2)
        lower, equal, higher = [], [], []
        for value in values:
            if value < pivot:
                lower.append(value)
            elif value > pivot:
                higher.append(value)
            else:
                equal.append(value)
        if rank <= len(lower):
            return select(lower, rank)
        if rank <= len(lower) + len(equal):
            return pivot
        # All smaller and equal values come before this partition in rank order.
        return select(higher, rank - len(lower) - len(equal))

    return select(times, k)
