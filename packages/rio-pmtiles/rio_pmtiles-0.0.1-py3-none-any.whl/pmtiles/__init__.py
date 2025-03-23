"""rio-pmtiles package"""

import sys
import warnings

__version__ = "0.0.1"

if sys.version_info < (3, 7):
    warnings.warn(
        "Support for Python versions < 3.7 will be dropped in rio-pmtiles version 2.0",
        FutureWarning,
        stacklevel=2,
    )
