from datetime import datetime, timedelta


def compute_target_date(advance_days: int) -> str:
    now = datetime.now()
    target_date = now.date() + timedelta(days=advance_days)
    return target_date.strftime("%Y-%m-%d")



def build_start_end_datetime(date_str: str, hour1: str):
    """
    date_str: "2026-02-12"
    hour1: "2:00pm"

    returns:
        start_str: "2026-02-12 14:00:00"
        end_str:   "2026-02-12 14:30:00"
    """

    # Combine date + hour
    combined = f"{date_str} {hour1}"

    # Parse into datetime
    start_dt = datetime.strptime(combined, "%Y-%m-%d %I:%M%p")

    # Add 30 minutes
    end_dt = start_dt + timedelta(minutes=30)

    # Format back to required string
    start_str = start_dt.strftime("%Y-%m-%d %H:%M:%S")
    end_str = end_dt.strftime("%Y-%m-%d %H:%M:%S")

    return str(start_str), str(end_str)

def to_hhmm(dt_str: str) -> str:
    # "2026-02-26 14:00:00" -> "2026-02-26 14:00"
    return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M")