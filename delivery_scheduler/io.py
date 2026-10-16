"""Load delivery requests from a simple text or CSV-style file."""

from pathlib import Path
from .scheduler import Delivery


def load_deliveries(path: str | Path) -> list[Delivery]:
    deliveries = []
    seen_ids = set()

    with Path(path).open(encoding="utf-8") as file:
        for line_number, raw_line in enumerate(file, start=1):
            line = raw_line.split("#", 1)[0].strip()
            if not line:
                continue

            parts = line.replace(",", " ").split()
            if [part.lower() for part in parts] == ["id", "start", "finish"]:
                continue
            if len(parts) != 3:
                raise ValueError(f"Line {line_number}: expected ID, start, finish")

            delivery_id, start, finish = parts
            if delivery_id in seen_ids:
                raise ValueError(f"Line {line_number}: repeated ID {delivery_id}")
            try:
                job = Delivery(delivery_id, int(start), int(finish))
            except ValueError as error:
                raise ValueError(f"Line {line_number}: {error}") from error

            deliveries.append(job)
            seen_ids.add(delivery_id)

    return deliveries
