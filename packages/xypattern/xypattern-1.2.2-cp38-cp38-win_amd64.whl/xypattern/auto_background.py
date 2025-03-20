from __future__ import annotations
from abc import abstractmethod
from typing import TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from .pattern import Pattern

try:
    from .util.smooth_bruckner import smooth_bruckner
except ImportError as e:
    print(e)
    print("Could not import the Cython version of smooth_bruckner. Using python implementation instead.")
    from .util.smooth_bruckner_py import smooth_bruckner


class AutoBackground:
    """
    Abstract base class for automatic background extraction algorithms.
    
    This class defines the interface for background extraction algorithms.
    Concrete implementations should override the extract_background method
    to provide specific background extraction functionality.
    """
    
    @abstractmethod
    def extract_background(self, pattern: Pattern):
        """
        Extracts the background from a pattern.
        
        This method should be implemented by subclasses to provide specific
        background extraction functionality.
        
        :param pattern: Pattern object from which to extract the background
        :return: numpy array of y values representing the extracted background
        """
        raise NotImplementedError

    @staticmethod
    def transform_x(self, fcn: callable):
        """
        Transforms the variables dependent on x.
        
        This method should be implemented by subclasses to handle
        transformation of x-dependent parameters when the x-axis is transformed.
        
        :param fcn: Function to transform the x-variable
        """
        raise NotImplementedError


class SmoothBrucknerBackground(AutoBackground):
    """
    Background extraction using Bruckner smoothing and Chebyshev polynomial fitting.
    
    This algorithm performs background extraction in two steps:
    1. Applies Bruckner smoothing to the input pattern
    2. Fits a Chebyshev polynomial to the smoothed data
    
    The Bruckner smoothing algorithm is particularly effective for extracting
    backgrounds from patterns with sharp peaks, such as X-ray diffraction data.
    
    Standard parameters are optimized for synchrotron XRD data but can be
    adjusted for other types of data.
    
    :param smooth_width: Width of the window in x-units used for Bruckner smoothing.
                        Larger values result in smoother backgrounds.
    :param iterations: Number of iterations for the Bruckner smoothing algorithm.
                      More iterations typically result in better background fitting.
    :param cheb_order: Order of the fitted Chebyshev polynomial.
                      Higher orders can fit more complex background shapes.
    """

    def __init__(self, smooth_width=0.1, iterations=50, cheb_order=50):
        self.smooth_width = smooth_width
        self.iterations = iterations
        self.cheb_order = cheb_order

    def extract_background(self, pattern: Pattern):
        """
        Extract background from a pattern using Bruckner smoothing and Chebyshev polynomial fitting.
        
        The method first applies Bruckner smoothing to the pattern data, then fits
        a Chebyshev polynomial to the smoothed data to create a continuous background.
        
        :param pattern: Pattern object from which to extract the background
        :return: numpy array of y values representing the extracted background
        """
        x, y = pattern.data
        smooth_points = int((float(self.smooth_width) / (x[1] - x[0])))

        y_smooth = smooth_bruckner(y, abs(smooth_points), self.iterations)
        # get cheb input parameters
        x_cheb = 2. * (x - x[0]) / (x[-1] - x[0]) - 1.
        cheb_parameters = np.polynomial.chebyshev.chebfit(x_cheb, y_smooth, self.cheb_order)

        return np.polynomial.chebyshev.chebval(x_cheb, cheb_parameters)

    def transform_x(self, fcn: callable):
        """
        Transform x-dependent parameters when the x-axis is transformed.
        
        This method adjusts the smooth_width parameter when the x-axis is transformed,
        ensuring that the background extraction behaves consistently after transformation.
        
        :param fcn: Function to transform the x-variable
        """
        self.smooth_width = fcn(self.smooth_width)
    