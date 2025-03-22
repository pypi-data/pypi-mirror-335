import datetime
import importlib.metadata
import random
from datetime import timedelta
import numpy as np

__version__ = importlib.metadata.version("evotrain")

BANDS_L2A = {
    10: ["B02", "B03", "B04", "B08"],
    20: ["B05", "B06", "B07", "B8A", "B11", "B12"],
    60: ["B01", "B09"],
}

BANDS_L2A_ALL = BANDS_L2A[10] + BANDS_L2A[20] + BANDS_L2A[60]


def logistic(x, L=1, k=3.60, x0=0, y0=-0.5, s=2):
    """
    Logistic function used to scale the Sentinel-2 bands and DEM.

    Parameters
    ----------
    x : np.ndarray or float
        The input value or array to be scaled.
    L : float, optional
        The curve's maximum value. Default is 1.
    k : float, optional
        The logistic growth rate or steepness of the curve. Default is 3.60.
    x0 : float, optional
        The x-value of the sigmoid's midpoint. Default is 0.
    y0 : float, optional
        The y-offset of the sigmoid. Default is -0.5.
    s : float, optional
        The scaling factor for the output. Default is 2.

    Returns
    -------
    np.ndarray or float
        The scaled value or array.
    """
    return (L / (1 + np.exp(-k * (x - x0))) + y0) * s


def random_uniform_jitter(n):
    """
    Applies random jitter to a value if jitter is enabled.
    Uses a uniform distribution.

    Parameters
    ----------
    x : float
        The value to which jitter is to be applied.

    Returns
    -------
    float
        The jittered value.
    """
    return random.uniform(-n, n)


def random_normal_jitter(std, mean=0):
    """
    Applies random jitter to a value if jitter is enabled.
    Uses a normal distribution.

    Parameters
    ----------
    std : float
        The standard deviation of the normal distribution.
    mean : float, optional
        The mean of the normal distribution. Default is 0.

    Returns
    -------
    float
        The jittered value.
    """
    return random.normalvariate(mean, std)


def load_latlon(bounds, epsg, resolution=10, steps=5):
    """
    Returns a lat, lon feature from the given bounds/epsg.

    This provide a coarse (but relatively fast) approximation to generate
    lat lon layers for each pixel.

    'steps' specifies how many points per axis should be use to perform
    the mesh approximation of the canvas
    """
    import geopandas as gpd
    from rasterio.crs import CRS
    from shapely.geometry import Point
    from skimage.transform import resize

    xmin, ymin, xmax, ymax = bounds
    out_shape = (
        int(np.floor((ymax - ymin) / resolution)),
        int(np.floor((xmax - xmin) / resolution)),
    )

    xx = np.linspace(xmin + resolution / 2, xmax - resolution / 2, steps)
    yy = np.linspace(ymax - resolution / 2, ymin + resolution / 2, steps)

    xx = np.broadcast_to(xx, [steps, steps]).reshape(-1)
    yy = np.broadcast_to(yy, [steps, steps]).T.reshape(-1)

    points = [Point(x0, y0) for x0, y0 in zip(xx, yy)]

    gs = gpd.GeoSeries(points, crs=CRS.from_epsg(epsg))
    gs = gs.to_crs(epsg=4326)

    lon_mesh = gs.apply(lambda p: p.x).values.reshape((steps, steps))
    lat_mesh = gs.apply(lambda p: p.y).values.reshape((steps, steps))

    lon = resize(lon_mesh, out_shape, order=1, mode="edge")
    lat = resize(lat_mesh, out_shape, order=1, mode="edge")

    return np.stack([lat, lon], axis=0).astype(np.float32)


def lat_lon_to_unit_sphere(lat, lon):
    """
    Convert latitude and longitude arrays (in degrees) to 3D unit sphere coordinates (x, y, z).

    Parameters:
    lat (array-like): Array of latitudes in degrees.
    lon (array-like): Array of longitudes in degrees.

    Returns:
    tuple: Three NumPy arrays (x, y, z) with the same shape as the input lat and lon arrays.
    """
    # Convert latitude and longitude from degrees to radians
    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)

    # Calculate x, y, z on the unit sphere
    x = np.cos(lat_rad) * np.cos(lon_rad)
    y = np.cos(lat_rad) * np.sin(lon_rad)
    z = np.sin(lat_rad)

    return x, y, z


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
        date_obj + timedelta(days=random_uniform_jitter(doy_jitter))
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
