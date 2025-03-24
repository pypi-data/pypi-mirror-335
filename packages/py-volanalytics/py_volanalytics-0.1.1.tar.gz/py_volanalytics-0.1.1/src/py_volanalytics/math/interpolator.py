""" 
A collection of Interpolators.

Interpolator objects are initiated with:

    x_values : sorted list of numerical values 
    y_values : list of numerical values
    extrapolate : boolean if object should return value if the call is outside the range

Example usage:
    x_values = [1, 2, 4, ]
    y_values = [2, 8, 4.5, ]
    interpolator = LinearInterpolator(
        x_values,
        y_values,
        extrapolate=True
    )
    print([interpolator(x) for x in range(8)])
        >>[2.0, 2.0, 8.0, 6.25, 4.5, 4.5, 4.5, 4.5]

Base abstract class:
    Interpolator
Concrete implementations:
    LinearInterpolator

References: 
[Building curves using Area Preserving Quadratic Splines](https://www.researchgate.net/publication/325132236_Building_Curves_Using_Area_Preserving_Quadratic_Splines), Hagan, 2018
[Interpolation Methods for Curve Construction](https://www.deriscope.com/docs/Hagan_West_curves_AMF.pdf), Hagan, 2006

"""

import numpy as np
import datetime as dt
from abc import ABC, abstractmethod
from enum import IntEnum, StrEnum
from typing import List, cast, Optional
from attrs import define, field
import matplotlib.pyplot as plt
import scienceplots

plt.style.use('science')

from py_volanalytics.types.var_types import NumericType

class ExtrapolateIndex(IntEnum):
    """
    Helper extrapolations enum.

    Indicates if we are in front of or in the back of the interpolation range.

    """

    FRONT = -1
    BACK = -2

class BoundaryCondition(StrEnum):
    """
    Helper boundary conditions enum.

    Indicates if this is a natural cubic spline, or Hermite(Bessel)
    """

    NATURAL_CUBIC_SPLINE = "Natural Cubic Spline"

@define(kw_only=True)
class Interpolator(ABC):
    """ Abstract base class for interpolator objects."""

    _xs: List[NumericType] | List[dt.datetime] | np.ndarray = field(alias="x_values")
    _ys: List[NumericType] | np.ndarray = field(alias="y_values")
    _extrapolate: bool = field(
        alias="extrapolate",
        default=False,
    )

    @_xs.validator
    def check_x_values(self, attribute, values):  # pylint: disable=W0613
        """Validates that x_values are sorted."""
        if not values:
            raise ValueError("list of x values is empty.")
        if len(values) == 1:
            return
        zero_point = dt.timedelta(0) if isinstance(values[0], dt.date) else 0
        for i in range(len(values) - 1):
            if values[i + 1] - values[i] < zero_point:
                raise ValueError("List of x values is not sorted")

    @_ys.validator
    def check_y_values(self, attribute, values):  # pylint: disable=W0613
        """Validates that y_values equal length to x_values."""
        if len(values) != len(self._xs):
            raise ValueError("List of y values is different len from x values.")

    @property
    def x_values(self) -> List[float]:
        """Get x values."""
        return self._xs

    @property
    def y_values(self) -> List[float]:
        """Get y values."""
        return [float(x) for x in self._ys]

    @property
    def is_extrapolator(self) -> bool:
        """Check if object extrapolates."""
        return self._extrapolate

    @abstractmethod
    def __call__(self, x: float | dt.date) -> float:
        """Call to get interpolated y value."""

    def __len__(self):
        """Get length of interpolator."""
        # unambiguous since we validated equal len
        return len(self._xs)
    
    def _find_index(self, x: float) -> int:
        """Helper function to get the adjacent index."""
        if x < self._xs[0]:
            return ExtrapolateIndex.FRONT
        for i in range(len(self) - 1):
            if self._xs[i] <= x < self._xs[i + 1]:
                return i
        return ExtrapolateIndex.BACK
    
    def _convert_to_float(self, delta: float | dt.timedelta) -> float:
        """Convert the potential time delta to year fraction float."""
        if isinstance(delta, dt.timedelta):
            # convert to year fraction, assume daily granularity
            delta = delta.days / 365
        return cast(float, delta)   

    def plot(
        self,
        title : Optional[str] = None,
        x_label : Optional[str] = None,
        y_label : Optional[str] = None
    ):
        """ Helper function to plot an interpolated curve """
        x_values = np.linspace(start=self._xs[0], stop=self._xs[-1], num=len(self) * 100)
        y_values = [self(x) for x in x_values]
        xlabel = x_label if x_label is not None else r'$x$'
        ylabel = y_label if y_label is not None else r'$y$'
        title = title if title is not None else r'Interpolated curve $y(x)$'
        plt.figure(figsize=(8,6))
        plt.title(title)
        plt.xlabel(xlabel = xlabel)
        plt.ylabel(ylabel = ylabel)
        
        plt.plot(x_values, y_values)
        plt.show() 
    
class LinearInterpolator(Interpolator):
    """Interpolator using linear interpolation, constant extrapolation."""

    def __call__(self, x: float | dt.date) -> float:
        """Call to get interpolated y value."""
        index = self._find_index(x)

        # negative index mean outside range
        if index < 0 and not self.is_extrapolator:
            raise ValueError(
                "Given range outside of interpolated range to non-extrapolator."
            )
        match index:
            case ExtrapolateIndex.FRONT:
                result = self._ys[0]
            case ExtrapolateIndex.BACK:
                result = self._ys[-1]
            case _:
                x_delta = self._convert_to_float(self._xs[index + 1] - self._xs[index])
                y_delta = self._ys[index + 1] - self._ys[index]
                slope = y_delta / x_delta
                result = (
                    self._ys[index]
                    + self._convert_to_float(x - self._xs[index]) * slope
                )
        # enforce float -> float signature of interpolator
        return float(result)

class CubicSplineInterpolator(Interpolator):
    """ The cubic-spline method with so-called natural boundary conditions. """

    def __call__(self, 
                 x: float | dt.date,
                 boundary_condition : BoundaryCondition = BoundaryCondition.NATURAL_CUBIC_SPLINE
                ) -> float:
        """Call to get interpolated y value."""
        index = self._find_index(x)

         # negative index mean outside range
        if index < 0 and not self.is_extrapolator:
            raise ValueError(
                "Given range outside of interpolated range to non-extrapolator."
            )
        match index:
            case ExtrapolateIndex.FRONT:
                result = self._ys[0]
            case ExtrapolateIndex.BACK:
                result = self._ys[-1]
            case _:
                n = len(self) - 1   #n is the index of the last data-point. 
                h = np.array([self._xs[j+1] - self._xs[j] for j in range(n)])
                a = np.array(self._ys[:n+1])

                # We are interested to solve the system Ux = v. 
                v = np.concat([
                    [0], 
                    [(3/h[j]*(a[j+1] - a[j]) - 3/h[j-1] * (a[j] - a[j-1])) for j in range(1,n)],
                    [0]
                ], axis=0)

                # U is a tridiagonal matrix
                U = np.zeros(shape=(n+1,n+1))
                U[0][0] = 1.0
                U[n][n] = 1.0
                for i in range(1,n):
                    U[i][i-1] = h[i-1]              # elements below the diagonal
                    U[i][i] = 2*(h[i-1] + h[i])   #principal diagonal element
                    U[i][i+1] = h[i]              # elements above the diagonal
                
                c = np.linalg.solve(U, v)

                b = np.array([(
                        1.0/h[j] * (a[j+1] - a[j]) 
                        - h[j]/3.0 * (2 * c[j] + c[j+1])
                    ) for j in range(n) 
                    ])
                
                d = np.array(
                    [
                        (c[j+1] - c[j])/(3 * h[j]) for j in range(n)
                    ]
                )

                result = (a[index] + b[index] * (x - self._xs[index])
                        + c[index] * (x - self._xs[index])**2 
                        + d[index] * (x - self._xs[index])**3
                )

        return float(result)
            
class HermiteCubicSplineInterpolator(Interpolator):
    """ The hermite cubic-spline method with so-called natural boundary conditions. """

    def __call__(self, 
                 x: float | dt.date,) -> float:
        """Call to get interpolated y value.""" 
        index = self.__find_index(x)

         # negative index mean outside range
        if index < 0 and not self.is_extrapolator:
            raise ValueError(
                "Given range outside of interpolated range to non-extrapolator."
            )
        match index:
            case ExtrapolateIndex.FRONT:
                result = self._ys[0]
            case ExtrapolateIndex.BACK:
                result = self._ys[-1]
            case _:
                n = len(self) - 1   #n is the index of the last data-point. 
                h = np.array([self._xs[j+1] - self._xs[j] for j in range(n)])
                a = np.array(self._ys[:n+1])                        
                m = np.array([ (self._ys[i+1] - self._ys[i])/h[i] for i in range(n) ])

                b = np.concat(
                    [1/(self._xs[2] - self._xs[0]) * 
                     (
                         ((self._xs[2] + self._xs[1] - 2 * self._xs[0]) * (self._ys[1] - self._ys[0]) / h[0])
                         -( h[0] * (self._ys[1] - self._ys[0]) / h[1] )
                     )
                     ],
                    [
                        (1/(self._xs[i+1] - self._xs[i-1])) *
                        (
                            h[i] * (self._ys[i] - self._ys[i]) / h[i-1]
                            - h[i-1] * (self._ys[i+1] - self._ys[i]) / h[i]
                        )
                        for i in range(1,n)
                    ],
                    [
                        -1/(self._xs[n] - self._xs[n-2]) *
                        (
                            (h[n-1] * (self._ys[n-1] - self._ys[n-2])/h[n-2])
                            - ( (2 * self._xs[n] - self._xs[n-1] - self._xs[n-2]) 
                               * (self._ys[n] - self._ys[n-1]) 
                               )
                        )
                    ]
                )

                c = np.array(
                    [
                        (3 * (self._ys[i+1] - self._ys[i]) / (h[i] ** 2)
                        - (b[i+1] + 2*b[i])/h[i])
                        for i in range(n)
                    ]
                )

                d = np.array(
                    [
                        (b[i+1] + b[i])/(h[i] ** 2)
                        - 2*(self._ys[i+1] - self._ys[i])/(h[i] ** 3)
                        for i in range(n)
                    ]
                )

                result = (a[index] + b[index] * (x - self._xs[index])
                        + c[index] * (x - self._xs[index])**2 
                        + d[index] * (x - self._xs[index])**3
                )
        
        return float(result)
    
if __name__ == "__main__":
    x = [0.0,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0]
    y = np.sin(x)
    cs = CubicSplineInterpolator(
        x_values=x,
        y_values=y,
        extrapolate=True
    )

    y_approx = [cs(x) for x in np.linspace(0.0,10.0,20,endpoint=True)]


