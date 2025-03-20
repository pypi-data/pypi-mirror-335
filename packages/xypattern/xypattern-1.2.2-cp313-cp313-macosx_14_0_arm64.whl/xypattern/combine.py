from __future__ import annotations
import numpy as np
from scipy.interpolate import interp1d
from .pattern import Pattern

"""
Functions for combining multiple Pattern objects.

This module provides utilities for working with multiple patterns, including
scaling patterns to match each other and stitching them together to create
a single continuous pattern.
"""

def stitch_patterns(patterns: list[Pattern], binning=None) -> Pattern:
    """
    Stitch together multiple patterns into a single continuous pattern.
    
    This function concatenates the x and y values from all patterns and then
    applies rebinning to create a uniform x-spacing. The patterns should be
    properly scaled before stitching (see scale_patterns function).
    
    :param patterns: List of Pattern objects to be stitched together
    :param binning: Bin size for the output pattern. If None, the bin size of the
                   first pattern will be used.
    :return: A new Pattern object containing the stitched data
    
    Example:
        >>> p1 = Pattern.from_file('low_angle.xy')
        >>> p2 = Pattern.from_file('high_angle.xy')
        >>> scale_patterns([p1, p2])  # Scale patterns to match each other
        >>> stitched = stitch_patterns([p1, p2])
    """
    if binning is None:
        binning = patterns[0].x[1] - patterns[0].x[0]

    x = np.concatenate([pattern.x for pattern in patterns])
    y = np.concatenate([pattern.y for pattern in patterns])
    return Pattern(x, y).rebin(binning)


def scale_patterns(patterns: list[Pattern]):
    """
    Scale multiple patterns to match each other in overlapping regions.
    
    This function scales patterns in place by modifying their scaling attribute.
    The first pattern (after sorting by x[0]) is used as the reference with a
    scaling of 1.0. Each subsequent pattern is scaled to match the previous one
    in their overlapping region.
    
    The patterns must have overlapping x-ranges for scaling to work properly.
    
    :param patterns: List of Pattern objects to be scaled
    :raises ValueError: If no overlap is found between adjacent patterns
    
    Example:
        >>> p1 = Pattern.from_file('low_angle.xy')
        >>> p2 = Pattern.from_file('high_angle.xy')
        >>> scale_patterns([p1, p2])
        >>> # p1.scaling will be 1.0, p2.scaling will be adjusted to match p1
    """
    for pattern in patterns:
        pattern.scaling = 1

    sorted_patterns = sorted(patterns, key=lambda p: p.x[0])
    for ind, pattern in enumerate(sorted_patterns):
        if ind == 0:
            pattern.scaling = 1
            continue

        scale_ind = ind - 1
        scaling = find_scaling(sorted_patterns[scale_ind], pattern)
        while scaling is None:
            scale_ind -= 1
            if scale_ind < 0:
                raise ValueError("No overlap found between patterns")
            scaling = find_scaling(sorted_patterns[scale_ind], pattern)

        pattern.scaling = scaling


def find_overlap(p1: Pattern, p2: Pattern) -> tuple[float, float] | None:
    """
    Find the overlapping x-range between two patterns.
    
    :param p1: First Pattern object
    :param p2: Second Pattern object
    :return: Tuple of (x_min, x_max) for the overlapping region, or None if no overlap exists
    
    Example:
        >>> overlap = find_overlap(pattern1, pattern2)
        >>> if overlap:
        >>>     x_min, x_max = overlap
        >>>     print(f"Patterns overlap from {x_min} to {x_max}")
        >>> else:
        >>>     print("No overlap between patterns")
    """
    x_min = max(p1.x[0], p2.x[0])
    x_max = min(p1.x[-1], p2.x[-1])
    if x_min > x_max:
        return None
    return x_min, x_max


def find_scaling(p1: Pattern, p2: Pattern) -> float | None:
    """
    Calculate the scaling factor to match p2 to p1 in their overlapping region.
    
    This function finds the average ratio of y-values between p1 and p2 in their
    overlapping x-range. If the x-values don't exactly match, linear interpolation
    is used to estimate the y-values at matching x-positions.
    
    :param p1: Reference Pattern object
    :param p2: Pattern object to be scaled
    :return: Scaling factor to apply to p2 to match p1, or None if no overlap exists
    
    Example:
        >>> scaling = find_scaling(reference_pattern, pattern_to_scale)
        >>> if scaling is not None:
        >>>     pattern_to_scale.scaling = scaling
    """
    overlap = find_overlap(p1, p2)
    if overlap is None:
        return None

    p1_indices = np.where((p1.x >= overlap[0]) & (p1.x <= overlap[1]))
    p2_indices = np.where((p2.x >= overlap[0]) & (p2.x <= overlap[1]))
    x1 = p1.x[p1_indices]
    x2 = p2.x[p2_indices]
    y1 = p1.y[p1_indices]
    y2 = p2.y[p2_indices]

    if len(x1) == len(x2) and np.allclose(x1, x2):
        return np.mean(y1 / y2)

    f2 = interp1d(x2, y2, kind="linear", fill_value="extrapolate")
    p2_interpolated = f2(x1)
    return np.mean(y1 / p2_interpolated)
