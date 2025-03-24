"""Discounting Curve."""

import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import scienceplots
from attrs import define, field
from typing import Union

plt.style.use('science')

@define(kw_only=True)
class DiscountingCurve:
    """ Class to represent a discounting curve object. """

    times : np.ndarray[Union[dt.date, float]] 
    discount_factors : np.ndarray[float]
