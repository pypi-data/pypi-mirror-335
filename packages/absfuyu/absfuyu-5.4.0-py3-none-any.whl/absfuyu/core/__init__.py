"""
Absfuyu: Core
-------------
Bases for other features

Version: 5.4.0
Date updated: 21/03/2025 (dd/mm/yyyy)
"""

# Module Package
# ---------------------------------------------------------------------------
__all__ = [
    # color
    "CLITextColor",
    # path
    # "CORE_PATH",
    # class
    "ShowAllMethodsMixin",
    "BaseClass",
    # wrapper
    "tqdm",
    "unidecode",
    # decorator
    "deprecated",
    "versionadded",
    "versionchanged",
]

__package_feature__ = [
    "beautiful",  # BeautifulOutput
    "docs",  # For (package) hatch's env use only
    "extra",  # DataFrame
    "full",  # All package
    "dev",
]


# Library
# ---------------------------------------------------------------------------
# from importlib.resources import files

# Most used features are imported to core
from absfuyu.core.baseclass import BaseClass, CLITextColor, ShowAllMethodsMixin
from absfuyu.core.docstring import deprecated, versionadded, versionchanged
from absfuyu.core.dummy_func import tqdm, unidecode

# Path
# ---------------------------------------------------------------------------
# CORE_PATH = files("absfuyu")
