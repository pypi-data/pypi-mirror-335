import datetime
from datetime import timedelta
from .preprocessing import _random_jitter
import numpy as np

def day_of_year(date):
    start_of_year = datetime.datetime(date.year, 1, 1)
    return (date - start_of_year).days + 1


def is_leap_year(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def day_of_year_cyclic_feats(date_str, doy_jitter=0, height=96, width=96):
    import datetime

    # Parse the date
    date_obj = datetime.datetime.strptime(date_str[:10], "%Y-%m-%d")

    # Apply jitter to the date
    jittered_dates = [
        date_obj + timedelta(days=_random_jitter(doy_jitter))
        for _ in range(height * width)
    ]

    # Calculate the day of the year (1-365 or 366 for leap years)
    day_of_year = (
        np.array(
            [jittered_date.timetuple().tm_yday for jittered_date in jittered_dates]
        )
        .reshape(height, width)
        .astype(np.float32)
    )

    # Total number of days in the year
    total_days = 366 if is_leap_year(date_obj.year) else 365

    # Encode as sine and cosine using numpy
    day_of_year_sin = np.sin(2 * np.pi * day_of_year / total_days)
    day_of_year_cos = np.cos(2 * np.pi * day_of_year / total_days)

    return np.array([day_of_year_sin, day_of_year_cos])