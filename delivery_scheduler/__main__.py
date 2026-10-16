"""Command-line interface for the delivery scheduler."""

import argparse
from .io import load_deliveries
from .scheduler import assign_drivers, max_deliveries, min_rejections


def main():
    parser = argparse.ArgumentParser(description="Plan deliveries and driver schedules")
    parser.add_argument("file", help="Path to a delivery data file")
    parser.add_argument(
        "--mode", choices=["all", "select", "drivers", "reject"], default="all",
        help="Which schedule to calculate (default: all)",
    )
    args = parser.parse_args()

    try:
        deliveries = load_deliveries(args.file)
    except (OSError, ValueError) as error:
        parser.error(str(error))

    if args.mode in ("all", "select"):
        selected = max_deliveries(deliveries)
        print("\nONE DRIVER — MAX DELIVERIES")
        for job in selected:
            print(f"  {job.id}: {job.start} -> {job.finish}")
        print(f"Total completed: {len(selected)}")

    if args.mode in ("all", "drivers"):
        schedules = assign_drivers(deliveries)
        print("\nDRIVER ASSIGNMENTS")
        for number, jobs in enumerate(schedules, start=1):
            details = "  ".join(f"{job.id} ({job.start}-{job.finish})" for job in jobs)
            print(f"  Driver {number}: {details}")
        print(f"Minimum drivers required: {len(schedules)}")

    if args.mode in ("all", "reject"):
        rejected, accepted = min_rejections(deliveries)
        accepted_ids = {job.id for job in accepted}
        rejected_ids = [job.id for job in deliveries if job.id not in accepted_ids]
        print("\nMINIMUM REJECTIONS")
        print(f"  Accepted: {', '.join(job.id for job in accepted) or '(none)'}")
        print(f"  Rejected: {', '.join(rejected_ids) or '(none)'}")
        print(f"Minimum rejected: {rejected}")


if __name__ == "__main__":
    main()
