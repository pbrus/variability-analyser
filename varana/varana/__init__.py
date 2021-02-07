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

__all__ = ["detrend", "fit", "freq_comb", "phase", "plt_pdgrm", "trim"]
__version__ = "1.1.0"

from varana import detrend
from varana import fit
from varana import freq_comb
from varana import phase
from varana import plt_pdgrm
from varana import trim
