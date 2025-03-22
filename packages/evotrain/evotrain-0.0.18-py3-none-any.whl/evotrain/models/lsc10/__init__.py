# add missing imports
import datetime
from datetime import timedelta

import numpy as np
from scipy.integrate import quad
from scipy.stats import norm


# Functions to get the seasonality score
def compute_sigma(days):
    return days / 3


def day_of_year(day, month, year=2020):
    date = datetime.datetime(year, month, day)
    start_of_year = datetime.datetime(year, 1, 1)
    return (date - start_of_year).days + 1


def get_season_borders(year):
    seasons = {
        "fall_before": (
            day_of_year(21, 9, year - 1),
            day_of_year(20, 12, year - 1),
        ),
        "winter": (day_of_year(21, 12, year - 1), day_of_year(20, 3, year)),
        "spring": (day_of_year(21, 3, year), day_of_year(20, 6, year)),
        "summer": (day_of_year(21, 6, year), day_of_year(20, 9, year)),
        "fall": (day_of_year(21, 9, year), day_of_year(20, 12, year)),
        "winter_after": (
            day_of_year(21, 12, year),
            day_of_year(20, 3, year + 1),
        ),
    }
    return seasons


def seasonality_score(day, month, year, smoothing_days):
    day_of_year_val = day_of_year(day, month, year)
    sigma = compute_sigma(smoothing_days)

    seasons = get_season_borders(year)

    # Gaussian distribution centered on the day_of_year value
    x = np.arange(-730, 731)  # Span over two years for buffer zones
    gaussian = norm.pdf(x, loc=day_of_year_val, scale=sigma)
    gaussian /= gaussian.sum()  # Normalize the area to 1

    season_scores = []
    for season, (start, end) in seasons.items():
        if start < end:
            season_area, _ = quad(
                norm.pdf, start, end, args=(day_of_year_val, sigma)
            )
        else:  # Crossing the year boundary, handle integration in two parts
            part1, _ = quad(
                norm.pdf, start, 730, args=(day_of_year_val, sigma)
            )
            part2, _ = quad(norm.pdf, -730, end, args=(day_of_year_val, sigma))
            season_area = part1 + part2
        season_scores.append(season_area)

    # Return the scores for the 4 main seasons, excluding the buffer seasons
    scores = season_scores[1:-1]
    scores = list(map(lambda x: round(x, 4), scores))
    return scores


def to_datetime(date):
    """
    Converts a numpy datetime64 object to a python datetime object
    Input:
      date - a np.datetime64 object
    Output:
      DATE - a python datetime object
    """
    timestamp = (date - np.datetime64("1970-01-01T00:00:00")) / np.timedelta64(
        1, "s"
    )
    return datetime.datetime.utcfromtimestamp(timestamp)


def get_season(sample_id, season_jitter):
    ymd = sample_id.split("_")[-1]
    y, m, d = ymd[:4], ymd[4:6], ymd[6:]
    date = np.datetime64(f"{y}-{m}-{d}T00:00:00")

    if season_jitter:
        time_jitter = np.round(
            random_jitter(season_jitter)
        )  # add 15 days jitter to the date
    else:
        time_jitter = 0

    date_scaled = to_datetime(date) + np.sign(
        time_jitter
    ) * datetime.timedelta(days=abs(time_jitter))
    date_timetuple = date_scaled.timetuple()

    year = date_timetuple.tm_year
    month = date_timetuple.tm_mon
    day = date_timetuple.tm_mday

    smoothing_days = 60
    scores = seasonality_score(day, month, year, smoothing_days)

    feats = np.ones((4, 128, 128))  # scores for 4 seasons
    for ind, score in enumerate(scores):
        feats[ind, ...] = feats[ind, ...] * score

    return feats


def is_leap_year(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def day_of_year_cyclic(sample_id, doy_jitter=15):
    """
    Encodes a given date as sine and cosine components of the day of the year.

    Parameters:
        date_str (str): Date in the format YYYYMMDD.
        doy_jitter (int): Number of days to add or subtract from the day of the year (default is 0).

    Returns:
        tuple: Sine and cosine components of the day of the year.
    """

    date_str = sample_id.split("_")[-1]

    # Parse the date
    date_obj = datetime.datetime.strptime(date_str, "%Y%m%d")

    # Apply jitter to the date
    jittered_date = date_obj + timedelta(days=doy_jitter)

    # Calculate the day of the year (1-365 or 366 for leap years)
    day_of_year = jittered_date.timetuple().tm_yday

    # Total number of days in the year
    total_days = 366 if is_leap_year(jittered_date.year) else 365

    # Encode as sine and cosine using numpy
    day_of_year_sin = np.sin(2 * np.pi * day_of_year / total_days)
    day_of_year_cos = np.cos(2 * np.pi * day_of_year / total_days)

    return day_of_year_sin, day_of_year_cos


def day_of_year_cyclic_feats(sample_id, doy_jitter=15, height=128, width=128):
    date_str = sample_id.split("_")[-1]

    # Parse the date
    date_obj = datetime.datetime.strptime(date_str, "%Y%m%d")

    # Apply jitter to the date
    jittered_dates = [
        date_obj + timedelta(days=doy_jitter) for _ in range(height * width)
    ]

    # Calculate the day of the year (1-365 or 366 for leap years)
    day_of_year = (
        np.array(
            [
                jittered_date.timetuple().tm_yday
                for jittered_date in jittered_dates
            ]
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
