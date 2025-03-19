"""
This library contains routines to perform and analyze surveys,
most of the sampling methods here presented have been taken from
Tillé's textbook.
"""

from .sampling import *
from .load_data import load_data
from .df_sample import sample as sample_df
from .weights import get_weights
