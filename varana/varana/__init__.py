"""
Varana
======

This package allows to analyze inhomogeneous time series.
It was designed to analyze variability of stars.

This package provides tools to:
  1. detrend time series
  2. remove outliers
  3. fit a sum of sines to a light curve (time series)
  4. phase a light curve with a specific frequency
  5. display results on charts

"""

__all__ = ["detrend", "trim", "freq_comb", "fit", "phase", "plt_pdgrm"]
__version__ = "0.1.0"


from . import detrend
from . import trim
from . import freq_comb
from . import fit
from . import phase
from . import plt_pdgrm
