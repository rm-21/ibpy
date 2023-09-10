import datetime as dt
import math
from typing import Literal

from dateutil.relativedelta import relativedelta
from pydantic import validate_call


@validate_call
def calculate_intervals_with_period_and_start(
    period: str,
    interval: Literal[
        "1min",
        "2min",
        "3min",
        "5min",
        "10min",
        "15min",
        "30min",
        "1h",
        "2h",
        "3h",
        "4h",
        "8h",
        "1d",
        "1w",
        "1m",
    ],
    from_dt: dt.datetime,
) -> list[tuple[dt.datetime, str]]:
    def timedelta_to_period(td: dt.timedelta) -> str:
        if td.days > 0:
            return f"{td.days}d"
        hours = td.seconds // 3600
        if hours > 0:
            return f"{hours}h"
        minutes = (td.seconds % 3600) // 60
        if minutes > 0:
            return f"{minutes}min"
        return "1min"  # Default to 1 minute if less than a minute

    # Convert period to timedelta or date offset using relativedelta
    if period[-1] == "y":
        end_dt = from_dt + relativedelta(years=int(period[:-1]))
    elif period[-1] == "m":
        end_dt = from_dt + relativedelta(months=int(period[:-1]))
    elif period[-1] == "w":
        end_dt = from_dt + relativedelta(weeks=int(period[:-1]))
    elif period[-1] == "d":
        end_dt = from_dt + relativedelta(days=int(period[:-1]))
    elif period[-1] == "h":
        end_dt = from_dt + relativedelta(hours=int(period[:-1]))
    elif period[-3:] == "min":
        end_dt = from_dt + relativedelta(minutes=int(period[:-3]))
    else:
        raise ValueError("Invalid period format")

    # Convert interval to timedelta
    if interval[-3:] == "min":
        interval_td = dt.timedelta(minutes=int(interval[:-3]))
    elif interval[-1] == "h":
        interval_td = dt.timedelta(hours=int(interval[:-1]))
    elif interval[-1] == "d":
        interval_td = dt.timedelta(days=int(interval[:-1]))
    elif interval[-1] == "w":
        interval_td = dt.timedelta(weeks=int(interval[:-1]))
    elif interval[-1] == "m":
        # Calculate the exact number of days between the two dates
        start_of_next_month = from_dt + relativedelta(months=1)
        interval_td = start_of_next_month - from_dt
    else:
        raise ValueError("Invalid interval format")

    total_duration = end_dt - from_dt
    num_intervals = math.ceil(total_duration / interval_td)

    # If num_intervals exceeds 1000, break the time period into intervals of 1000
    period_list = []
    current_start_dt = from_dt
    while num_intervals > 1000:
        current_period = timedelta_to_period(1000 * interval_td)
        period_list.append((current_start_dt, current_period))
        current_start_dt = current_start_dt + 1000 * interval_td
        num_intervals -= 1000

    # Append the remaining period
    remaining_period = timedelta_to_period(num_intervals * interval_td)
    period_list.append((current_start_dt, remaining_period))
    return period_list
