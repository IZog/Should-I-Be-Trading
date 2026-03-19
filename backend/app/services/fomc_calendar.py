from datetime import date, datetime


FOMC_DATES = [
    "2025-01-28", "2025-01-29", "2025-03-18", "2025-03-19",
    "2025-05-06", "2025-05-07", "2025-06-17", "2025-06-18",
    "2025-07-29", "2025-07-30", "2025-09-16", "2025-09-17",
    "2025-10-28", "2025-10-29", "2025-12-09", "2025-12-10",
    "2026-01-27", "2026-01-28", "2026-03-17", "2026-03-18",
    "2026-04-28", "2026-04-29", "2026-06-16", "2026-06-17",
    "2026-07-28", "2026-07-29", "2026-09-15", "2026-09-16",
    "2026-10-27", "2026-10-28", "2026-12-15", "2026-12-16",
]


def get_next_fomc() -> dict:
    today = date.today()
    parsed_dates = sorted(set(datetime.strptime(d, "%Y-%m-%d").date() for d in FOMC_DATES))

    for fomc_date in parsed_dates:
        if fomc_date >= today:
            days_until = (fomc_date - today).days
            return {
                "next_date": fomc_date.isoformat(),
                "days_until": days_until,
                "is_within_warning": days_until <= 5,
            }

    # If all dates are in the past, return the last one
    last = parsed_dates[-1]
    days_until = (last - today).days
    return {
        "next_date": last.isoformat(),
        "days_until": days_until,
        "is_within_warning": False,
    }
