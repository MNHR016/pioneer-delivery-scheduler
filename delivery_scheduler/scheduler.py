"""Greedy delivery scheduling algorithms."""

from dataclasses import dataclass
import heapq


@dataclass(frozen=True)
class Delivery:
    id: str
    start: int
    finish: int

    def __post_init__(self):
        if self.start >= self.finish:
            raise ValueError(f"Delivery {self.id}: start must be before finish")


def max_deliveries(deliveries: list[Delivery]) -> list[Delivery]:
    """Keep as many deliveries as possible using a single driver."""
    # Finishing early leaves more time for the next job.
    ordered = sorted(deliveries, key=lambda job: (job.finish, job.start, job.id))
    selected = []
    last_finish = float("-inf")

    for job in ordered:
        if job.start >= last_finish:
            selected.append(job)
            last_finish = job.finish

    return selected


def assign_drivers(deliveries: list[Delivery]) -> list[list[Delivery]]:
    """Schedule every delivery while using the fewest drivers possible."""
    ordered = sorted(deliveries, key=lambda job: (job.start, job.finish, job.id))
    schedules: list[list[Delivery]] = []
    # Each entry is (when the driver is free, driver index).
    available: list[tuple[int, int]] = []

    for job in ordered:
        if available and available[0][0] <= job.start:
            _, driver = heapq.heappop(available)
        else:
            driver = len(schedules)
            schedules.append([])

        schedules[driver].append(job)
        heapq.heappush(available, (job.finish, driver))

    return schedules


def min_rejections(deliveries: list[Delivery]) -> tuple[int, list[Delivery]]:
    """Return the minimum rejected count and a possible accepted schedule."""
    accepted = max_deliveries(deliveries)
    return len(deliveries) - len(accepted), accepted
