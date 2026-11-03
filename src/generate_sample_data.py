"""Generate deterministic CSV input for the demo pipeline."""

from __future__ import annotations

import csv
from datetime import datetime, timedelta

from config import configured_path


EVENT_TYPES = ("purchase", "refund", "login", "view")
PRODUCTS = ("Alpha", "Bravo", "Charlie", "Delta", "Echo")
ROW_COUNT = 1000


def main() -> None:
    output = configured_path("raw", "events.csv")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["event_id", "event_time", "user_id", "product", "event_type", "amount"]
        )
        start = datetime(2026, 1, 1, 0, 0)
        for index in range(ROW_COUNT):
            event_type = EVENT_TYPES[index % len(EVENT_TYPES)]
            event_time = start + timedelta(minutes=index * 41)
            amount = 0.0 if event_type in {"login", "view"} else round(
                5.0 + ((index * 17) % 9500) / 100, 2
            )
            if event_type == "refund":
                amount = -amount
            writer.writerow(
                [
                    f"evt-{index + 1:04d}",
                    event_time.isoformat(),
                    f"user-{index % 100 + 1:03d}",
                    PRODUCTS[index % len(PRODUCTS)],
                    event_type,
                    f"{amount:.2f}",
                ]
            )
    print(f"Wrote {ROW_COUNT} sample rows to {output}")


if __name__ == "__main__":
    main()
