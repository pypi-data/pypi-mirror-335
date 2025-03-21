"""
Absufyu: Utilities
------------------
Some random utilities

Version: 5.2.0
Date updated: 12/03/2025 (dd/mm/yyyy)
"""

# Module Package
# ---------------------------------------------------------------------------
__all__ = [
    "get_installed_package",
    "set_min",
    "set_max",
    "set_min_max",
    "stop_after_day",
]

# Library
# ---------------------------------------------------------------------------
import pkgutil
from datetime import datetime

from absfuyu.core import deprecated, versionadded, versionchanged


# Function
# ---------------------------------------------------------------------------
@versionchanged("2.7.1", reason="Use ``pkgutil`` lib")
def get_installed_package():
    """
    Return a list of installed packages

    Returns
    -------
    list[str]
        List of installed packages
    """
    iter_modules = list(
        {module.name for module in pkgutil.iter_modules() if module.ispkg}
    )
    return sorted(iter_modules)


@deprecated("5.0.0")
def set_min(
    current_value: int | float,
    *,
    min_value: int | float = 0,
) -> int | float:
    """
    Return ``min_value`` when ``current_value`` < ``min_value``

    Parameters
    ----------
    current_value : int | float
        Current value

    min_value : int | float
        Minimum value
        (Default: ``0``)

    Returns
    -------
    int | float
        Analyzed value


    Example:
    --------
    >>> set_min(-1)
    0
    """
    # if current_value < min_value:
    #     current_value = min_value
    # return current_value
    return max(min_value, current_value)


@deprecated("5.0.0")
def set_max(
    current_value: int | float,
    *,
    max_value: int | float = 100,
) -> int | float:
    """
    Return ``max_value`` when ``current_value`` > ``max_value``

    Parameters
    ----------
    current_value : int | float
        Current value

    max_value : int | float
        Maximum value
        (Default: ``100``)

    Returns
    -------
    int | float
        Analyzed value


    Example:
    --------
    >>> set_max(101)
    100
    """
    # if current_value > max_value:
    #     current_value = max_value
    # return current_value
    return min(max_value, current_value)


def set_min_max(
    current_value: int | float,
    *,
    min_value: int | float = 0,
    max_value: int | float = 100,
) -> int | float:
    """
    Return ``min_value`` | ``max_value`` when ``current_value``
    is outside ``[min_value, max_value]``

    Parameters
    ----------
    current_value : int | float
        Current value

    min_value : int | float
        Minimum value
        (Default: ``0``)

    max_value : int | float
        Maximum value
        (Default: ``100``)

    Returns
    -------
    int | float
        Analyzed value


    Example:
    --------
    >>> set_min_max(808)
    100
    """
    # Set min
    # current_value = set_min(current_value, min_value=min_value)
    current_value = max(current_value, min_value)
    # Set max
    # current_value = set_max(current_value, max_value=max_value)
    current_value = min(current_value, max_value)
    return current_value


@versionadded("3.2.0")
def stop_after_day(
    year: int | None = None, month: int | None = None, day: int | None = None
) -> None:
    """
    Stop working after specified day.
    Put the function at the begining of the code is recommended.

    Parameters
    ----------
    year : int
        Desired year
        (Default: ``None``)

    month : int
        Desired month
        (Default: ``None``)

    day : int
        Desired day
        (Default: ``None`` - 1 day trial)
    """
    # None checking - By default: 1 day trial
    now = datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month
    if day is None:
        day = now.day + 1

    # Logic
    end_date = datetime(year, month, day)
    result = end_date - now
    if result.days < 0:
        raise SystemExit("End of time")
