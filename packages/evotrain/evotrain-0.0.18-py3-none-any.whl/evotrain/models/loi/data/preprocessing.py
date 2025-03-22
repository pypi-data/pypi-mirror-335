import numpy as np
from evotrain import logistic, random_uniform_jitter


def scale_s2_l2a_bands(
    arr: np.ndarray,
    scaling_factor=10_000,
    apply_logistic=False,
    k_factor=5,
    apply_jitter=False,
    k_factor_jitter=2,
):
    """
    Scale the Sentinel-2 L2A bands and optionally apply logistic scaling.

    Parameters
    ----------
    arr : np.ndarray
        The array containing the Sentinel-2 L2A bands.
    scaling_factor : int, optional
        Scaling factor for the Sentinel-2 bands. Default is 10,000.
    apply_logistic : bool, optional
        Whether to apply logistic scaling. Default is False.
    k_factor : int, optional
        Factor for logistic scaling. Default is 5.
    apply_jitter : bool, optional
        Whether to apply random jitter to the k_factor. Default is False.
    k_factor_jitter : int, optional
        The amount of jitter to apply to the k_factor. Default is 2.

    Returns
    -------
    np.ndarray
        The scaled Sentinel-2 L2A bands.
    """
    assert arr.dtype == np.float32, "Array must be of type np.float32"

    arr = arr / scaling_factor

    if apply_logistic:
        k_noised_signal = k_factor + _random_jitter(k_factor_jitter, apply_jitter)
        arr = logistic(arr, k=k_noised_signal)

    return arr


def _random_jitter(x, apply_jitter=True):
    """
    Applies random jitter to a value if jitter is enabled.

    Parameters
    ----------
    x : float
        The value to which jitter is to be applied.
    apply_jitter : bool, optional
        Whether to apply jitter. Default is True.

    Returns
    -------
    float
        The jittered value if apply_jitter is True, otherwise 0.
    """
    return random_uniform_jitter(x) if apply_jitter else 0
