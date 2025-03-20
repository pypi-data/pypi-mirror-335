# -*- coding: utf-8 -*-
from __future__ import annotations
import os

import numpy as np
from scipy.interpolate import interp1d
from scipy.ndimage import gaussian_filter1d

from .util.signal import Signal
from .auto_background import AutoBackground


class Pattern(object):
    """
    A Pattern represents a set of x and y values for scientific data analysis.
    
    The Pattern class provides a comprehensive set of tools for working with x-y data,
    such as those collected in x-ray diffraction, spectroscopy, or other scientific
    measurements. It supports loading from and saving to various file formats,
    background subtraction, data manipulation, and mathematical operations.
    
    Key features:
    - Loading and saving patterns from/to various file formats (.xy, .chi, .fxye)
    - Applying scaling, offset, and smoothing to patterns
    - Background subtraction (manual or automatic)
    - Pattern manipulation (limiting, extending, deleting ranges)
    - Mathematical operations (addition, subtraction, multiplication)
    - Pattern transformation (x-axis transformation)
    - Pattern rebinning
    - Pattern serialization to/from dictionaries

    :param x: x values of the pattern (numpy array)
    :param y: y values of the pattern (numpy array)
    :param name: name of the pattern (string)
    """

    def __init__(self, x: np.ndarray = None, y: np.ndarray = None, name: str = ""):
        """
        Create a new Pattern object.
        
        Initializes a Pattern with the provided x and y data arrays. If no data is provided,
        default values will be generated: x as a linear space from 0.1 to 15 with 100 points,
        and y as a function of x.
        
        :param x: Array of x values. If None, default values will be generated.
        :param y: Array of y values. If None, default values will be generated.
        :param name: Name identifier for the pattern. Useful for display and when working with multiple patterns.
        
        :raises ValueError: If x and y arrays have different lengths.
        
        Example:
            >>> # Create a pattern with custom data
            >>> x = np.linspace(0, 10, 100)
            >>> y = np.sin(x)
            >>> pattern = Pattern(x, y, name="Sine Wave")
            >>> 
            >>> # Create a pattern with default data
            >>> default_pattern = Pattern()
        """
        if x is None:
            self._original_x = np.linspace(0.1, 15, 100)
        else:
            self._original_x = x
        if y is None:
            self._original_y = (
                np.log(self._original_x**2) - (self._original_x * 0.2) ** 2
            )
        else:
            self._original_y = y

        self.name = name
        self.filename = ""
        self._offset = 0.0
        self._scaling = 1.0
        self._smoothing = 0.0
        self._background_pattern = None

        self._auto_bkg: AutoBackground | None = None
        self._auto_bkg_roi: list[float] | None = None

        self._pattern_x = self._original_x
        self._pattern_y = self._original_y

        self._auto_background_before_subtraction_pattern = None
        self._auto_background_pattern = None

        # Initialize the changed signal
        self._changed = Signal()

    def load(self, filename: str, skiprows: int = 0):
        """
        Load pattern data from a file.
        
        Reads x-y data from various file formats and updates the current Pattern object.
        Supported formats:
        - .xy: Simple two-column text file with x values in the first column and y values in the second
        - .chi: Standard format used in X-ray diffraction, automatically skips 4 header rows
        - Other text-based formats with columns of x-y data
        
        The pattern name will be set to the filename (without extension).
        
        :param filename: Path to the file to load
        :param skiprows: Number of header rows to skip when loading the data
                        (automatically set to 4 for .chi files)
        :raises ValueError: If the file format is incorrect or file cannot be read
        
        Example:
            >>> pattern = Pattern()
            >>> pattern.load("data.xy")
            >>> # For a file with header rows:
            >>> pattern.load("data_with_header.xy", skiprows=2)
        """
        try:
            if filename.endswith(".chi"):
                skiprows = 4
            data = np.loadtxt(filename, skiprows=skiprows)
            self._original_x = data.T[0]
            self._original_y = data.T[1]
            self.filename = filename
            self.name = os.path.basename(filename).split(".")[:-1][0]
            self.recalculate_pattern()

        except ValueError:
            raise ValueError("Wrong data format for pattern file! - " + filename)

    @staticmethod
    def from_file(filename: str, skiprows: int = 0) -> Pattern:
        """
        Create a new Pattern object by loading data from a file.
        
        This is a convenience static method that creates a new Pattern instance
        and loads data from the specified file.
        
        Supported formats:
        - .xy: Simple two-column text file with x values in the first column and y values in the second
        - .chi: Standard format used in X-ray diffraction, automatically skips 4 header rows
        - Other text-based formats with columns of x-y data
        
        :param filename: Path to the file to load
        :param skiprows: Number of header rows to skip when loading the data
                        (automatically set to 4 for .chi files)
        :return: A new Pattern object containing the loaded data
        :raises ValueError: If the file format is incorrect or file cannot be read
        
        Example:
            >>> # Create a pattern directly from a file:
            >>> pattern = Pattern.from_file("data.xy")
            >>> 
            >>> # For a file with header rows:
            >>> pattern = Pattern.from_file("data_with_header.xy", skiprows=2)
        """
        try:
            pattern = Pattern()
            pattern.load(filename, skiprows)
            return pattern

        except ValueError:
            raise ValueError("Wrong data format for pattern file! - " + filename)

    def save(self, filename, header="", subtract_background=False, unit="2th_deg"):
        """
        Save pattern data to a file.
        
        Writes the pattern's x-y data to a file in various formats.
        The format is determined by the file extension:
        - .xy: Simple two-column text file
        - .chi: Standard format used in X-ray diffraction, includes header information
        - .fxye: Format with x, y, and error values (errors calculated as sqrt(|y|))
        
        :param filename: Path where the file should be saved
        :param header: Optional header text to include in the file
        :param subtract_background: If True, saves the background-subtracted data;
                                   if False, saves the original data
        :param unit: X-axis unit descriptor used in the .chi file header
                    (only used for .chi format)
        
        Example:
            >>> pattern = Pattern(x, y)
            >>> # Save as .xy file:
            >>> pattern.save("data.xy")
            >>> 
            >>> # Save as .chi file with background subtraction:
            >>> pattern.save("data.chi", subtract_background=True, unit="q_A^-1")
            >>> 
            >>> # Save with custom header:
            >>> pattern.save("data.xy", header="# X Y data\n# Measured on 2023-01-01")
        """
        if subtract_background:
            x, y = self.data
        else:
            x, y = self.original_data

        num_points = len(x)

        file_handle = open(filename, "w")

        if filename.endswith(".chi"):
            if header is None or header == "":
                file_handle.write(filename + "\n")
                file_handle.write(unit + "\n\n")
                file_handle.write("       {0}\n".format(num_points))
            else:
                file_handle.write(header)
            for ind in range(num_points):
                file_handle.write(" {0:.7E}  {1:.7E}\n".format(x[ind], y[ind]))
        elif filename.endswith(".fxye"):
            factor = 100
            if "CONQ" in header:
                factor = 1
            header = header.replace("NUM_POINTS", "{0:.6g}".format(num_points))
            header = header.replace("MIN_X_VAL", "{0:.6g}".format(factor * x[0]))
            header = header.replace(
                "STEP_X_VAL", "{0:.6g}".format(factor * (x[1] - x[0]))
            )

            file_handle.write(header)
            file_handle.write("\n")
            for ind in range(num_points):
                file_handle.write(
                    "\t{0:.6g}\t{1:.6g}\t{2:.6g}\n".format(
                        factor * x[ind], y[ind], np.sqrt(abs(y[ind]))
                    )
                )
        else:

            data = np.dstack((x, y))
            np.savetxt(file_handle, data[0], header=header)
        file_handle.close()

    @property
    def background_pattern(self) -> Pattern:
        """
        Get or set the background pattern for this Pattern.
        
        The background pattern is used for background subtraction during data processing.
        When a background pattern is set, its y values will be subtracted from this pattern's
        y values during the recalculation process. If the x values of the background pattern
        don't match this pattern's x values, interpolation will be used.
        
        When a background pattern is set, it will be connected to this pattern's recalculation
        process, so any changes to the background pattern will automatically trigger a 
        recalculation of this pattern.
        
        :return: The current background Pattern object or None if no background is set
        
        Example:
            >>> # Create a main pattern and a background pattern
            >>> main_pattern = Pattern(x_data, y_data, name="sample")
            >>> background = Pattern(x_data, background_data, name="background")
            >>> 
            >>> # Set the background pattern
            >>> main_pattern.background_pattern = background
            >>> 
            >>> # Remove the background pattern
            >>> main_pattern.background_pattern = None
        """
        return self._background_pattern

    @background_pattern.setter
    def background_pattern(self, pattern: Pattern | None):
        """
        Set a new background pattern.
        
        :param pattern: A Pattern object to use as background or None to remove the background
        """
        if self._background_pattern is not None:
            self._background_pattern.changed.disconnect(self.recalculate_pattern)

        self._background_pattern = pattern
        if self._background_pattern is not None:
            self._background_pattern.changed.connect(self.recalculate_pattern)
        
        # Recalculate the pattern with the new background
        self.recalculate_pattern()

    def rebin(self, bin_size: float) -> Pattern:
        """
        Creates a new pattern with data rebinned to the specified bin size.
        
        Rebinning is the process of combining adjacent data points into bins of a specified size,
        which can be useful for reducing noise or matching the resolution of different patterns.
        This method uses histogram-based rebinning, which preserves the total intensity.
        
        This method does not modify the current pattern but returns a new Pattern object.
        
        :param bin_size: Size of the bins in the same units as the x-axis
        :return: A new Pattern object with rebinned data
        
        Example:
            >>> pattern = Pattern(x_data, y_data)
            >>> # Rebin to 0.1 unit bins
            >>> rebinned = pattern.rebin(0.1)
            >>> # Rebin to coarser 0.5 unit bins
            >>> coarse_rebinned = pattern.rebin(0.5)
        """
        x, y = self.data
        x_min = np.round(np.min(x) / bin_size) * bin_size
        x_max = np.round(np.max(x) / bin_size) * bin_size
        new_x = np.arange(x_min, x_max + 0.1 * bin_size, bin_size)

        bins = np.hstack((x_min - bin_size * 0.5, new_x + bin_size * 0.5))
        new_y = np.histogram(x, bins, weights=y)[0] / np.histogram(x, bins)[0]

        return Pattern(new_x, new_y)

    @property
    def data(self) -> tuple[np.ndarray, np.ndarray]:
        """
        Returns the data of the pattern. If a background pattern is set, the background will be subtracted from the
        pattern. If smoothing is set, the pattern will be smoothed.

        :return: Tuple of x and y values
        """
        return self._pattern_x, self._pattern_y

    def recalculate_pattern(self):
        """
        Recalculates the pattern data based on the current settings.
        Applies background subtraction, auto background, scaling, offset, and smoothing.
        This method is called automatically when any of these settings are changed.
        """
        if self._background_pattern is not None:
            # create background function
            x_bkg, y_bkg = self._background_pattern.data

            if not np.array_equal(x_bkg, self._original_x):
                # the background will be interpolated
                f_bkg = interp1d(x_bkg, y_bkg, kind="linear")

                # find overlapping x and y values:
                ind = np.where(
                    (self._original_x <= np.max(x_bkg))
                    & (self._original_x >= np.min(x_bkg))
                )
                x = self._original_x[ind]
                y = self._original_y[ind]

                if len(x) == 0:
                    # if there is no overlapping between background and pattern, raise an error
                    raise BkgNotInRangeError(self.name)

                y = y * self._scaling + self.offset - f_bkg(x)
            else:
                # if pattern and bkg have the same x basis we just delete y-y_bkg
                x, y = (
                    self._original_x,
                    self._original_y * self._scaling + self.offset - y_bkg,
                )
        else:
            x, y = self.original_data
            y = y * self.scaling + self.offset

        if self.auto_bkg is not None:
            self._auto_background_before_subtraction_pattern = Pattern(x, y)
            roi = (
                self.auto_bkg_roi
                if self.auto_bkg_roi is not None
                else [x[0] - 0.1, x[-1] + 0.1]
            )
            x, y = self._auto_background_before_subtraction_pattern.limit(*roi).data
            y_bkg = self.auto_bkg.extract_background(Pattern(x, y))
            self._auto_background_pattern = Pattern(
                x, y_bkg, name="auto_bkg_" + self.name
            )
            y -= y_bkg

        if self.smoothing > 0:
            y = gaussian_filter1d(y, self.smoothing)

        self._pattern_x = x
        self._pattern_y = y
        self._changed.emit(self)

    @data.setter
    def data(self, data: tuple[np.ndarray, np.ndarray]):
        """
        Sets the data of the pattern. Also resets the scaling and offset to 1 and 0 respectively.

        :param data: tuple of x and y values
        """
        (x, y) = data
        self._original_x = x
        self._original_y = y
        self.scaling = 1.0
        self.offset = 0

    @property
    def original_data(self) -> tuple[np.ndarray, np.ndarray]:
        """
        Returns the original data of the pattern without any background subtraction or smoothing.

        :return: tuple of x and y values
        """
        return self._original_x, self._original_y

    @property
    def x(self) -> np.ndarray:
        """Returns the x values of the pattern"""
        return self._pattern_x

    @x.setter
    def x(self, new_value: np.ndarray):
        """Sets the x values of the pattern"""
        self._original_x = new_value
        self.recalculate_pattern()

    @property
    def y(self) -> np.ndarray:
        """Returns the y values of the pattern"""
        return self._pattern_y

    @y.setter
    def y(self, new_y: np.ndarray):
        """Sets the y values of the pattern"""
        self._original_y = new_y
        self.recalculate_pattern()

    @property
    def scaling(self) -> float:
        """
        Get or set the scaling factor applied to the pattern's y values.
        
        The scaling factor is a multiplicative factor applied to the y values
        during pattern recalculation. This allows for adjusting the intensity
        of the pattern without modifying the original data.
        
        The scaling is applied before the offset and after any background subtraction.
        
        :return: The current scaling factor (default: 1.0)
        
        Example:
            >>> pattern = Pattern(x_data, y_data)
            >>> pattern.scaling = 2.0  # Double the intensity
            >>> pattern.scaling = 0.5  # Halve the intensity
        """
        return self._scaling

    @scaling.setter
    def scaling(self, value):
        """
        Set the scaling factor for the pattern's y values.
        
        :param value: The scaling factor to apply (must be >= 0)
        :note: If a negative value is provided, scaling will be set to 0.0
        """
        if value < 0:
            self._scaling = 0.0
        else:
            self._scaling = value
        self.recalculate_pattern()

    @property
    def offset(self) -> float:
        """
        Get or set the vertical offset applied to the pattern's y values.
        
        The offset is an additive value applied to the y values during pattern
        recalculation. This allows for shifting the pattern up or down without
        modifying the original data.
        
        The offset is applied after the scaling factor and after any background subtraction.
        
        :return: The current offset value (default: 0.0)
        
        Example:
            >>> pattern = Pattern(x_data, y_data)
            >>> pattern.offset = 100  # Shift the pattern up by 100 units
            >>> pattern.offset = -50  # Shift the pattern down by 50 units
        """
        return self._offset

    @offset.setter
    def offset(self, value):
        """
        Set the vertical offset for the pattern's y values.
        
        :param value: The offset value to apply
        """
        self._offset = value
        self.recalculate_pattern()

    @property
    def smoothing(self) -> float:
        """
        Get or set the smoothing factor applied to the pattern's y values.
        
        The smoothing factor controls the amount of Gaussian smoothing applied to
        the pattern data during recalculation. A value of 0 means no smoothing is
        applied. Higher values result in more smoothing.
        
        The smoothing is implemented using scipy's gaussian_filter1d function, where
        the smoothing value represents the standard deviation of the Gaussian kernel.
        
        Smoothing is applied after background subtraction, scaling, and offset.
        
        :return: The current smoothing factor (default: 0.0)
        
        Example:
            >>> pattern = Pattern(x_data, y_data)
            >>> pattern.smoothing = 0.0  # No smoothing
            >>> pattern.smoothing = 0.5  # Light smoothing
            >>> pattern.smoothing = 2.0  # Stronger smoothing
        """
        return self._smoothing

    @smoothing.setter
    def smoothing(self, value):
        """
        Set the smoothing factor for the pattern's y values.
        
        :param value: The smoothing factor to apply (0.0 for no smoothing)
        """
        self._smoothing = value
        self.recalculate_pattern()

    @property
    def auto_bkg(self) -> AutoBackground | None:
        """
        Get or set the automatic background extraction algorithm.
        
        This property allows you to specify an algorithm for automatic background extraction.
        When set to a valid AutoBackground implementation (such as SmoothBrucknerBackground),
        the algorithm will be applied during pattern recalculation to automatically extract
        and subtract a background from the pattern data.
        
        The automatic background is calculated within the region specified by auto_bkg_roi
        if provided, otherwise it uses the full pattern range.
        
        Setting this property to None disables automatic background extraction.
        
        :return: The current AutoBackground object or None if automatic background
                extraction is disabled
        
        Example:
            >>> pattern = Pattern(x_data, y_data)
            >>> # Enable automatic background extraction with SmoothBrucknerBackground
            >>> pattern.auto_bkg = SmoothBrucknerBackground(
            ...     smooth_width=0.2, 
            ...     iterations=30, 
            ...     cheb_order=20
            ... )
            >>> # Disable automatic background extraction
            >>> pattern.auto_bkg = None
        """
        return self._auto_bkg

    @auto_bkg.setter
    def auto_bkg(self, value: AutoBackground | None):
        """
        Set the automatic background extraction algorithm.
        
        :param value: An AutoBackground implementation or None to disable
                     automatic background extraction
        """
        self._auto_bkg = value
        self.recalculate_pattern()

    @property
    def auto_bkg_roi(self) -> list[float] | None:
        """
        Get or set the region of interest for automatic background extraction.
        
        This property defines the x-range (region of interest) within which the
        automatic background extraction algorithm will operate. It should be a
        list of two float values [min_x, max_x] specifying the lower and upper
        bounds of the region.
        
        If set to None, the full pattern range will be used for background extraction.
        
        :return: A list of two float values [min_x, max_x] or None if no specific
                region is defined
        
        Example:
            >>> pattern = Pattern(x_data, y_data)
            >>> pattern.auto_bkg = SmoothBrucknerBackground()
            >>> # Set region of interest for background extraction
            >>> pattern.auto_bkg_roi = [10.0, 60.0]
            >>> # Use the full pattern range
            >>> pattern.auto_bkg_roi = None
        """
        return self._auto_bkg_roi

    @auto_bkg_roi.setter
    def auto_bkg_roi(self, value: list[float] | None):
        """
        Set the region of interest for automatic background extraction.
        
        :param value: A list of two float values [min_x, max_x] or None to use
                     the full pattern range
        :raises ValueError: If value is not None and not a list with exactly two elements
        """
        if value is not None and (not isinstance(value, list) or len(value) != 2):
            raise ValueError("auto_bkg_roi must be a list with exactly two elements")
        
        self._auto_bkg_roi = value
        self.recalculate_pattern()

    @property
    def auto_background_pattern(self) -> Pattern:
        """
        Get the automatically calculated background pattern.
        
        This property provides access to the background pattern that was automatically
        calculated using the auto_bkg algorithm (if enabled). This is different from
        the manually set background_pattern property.
        
        The auto background is calculated during the recalculate_pattern method when
        auto_bkg is not None. The calculation uses the specified auto_bkg algorithm
        and auto_bkg_roi (region of interest) if provided.
        
        :return: The automatically calculated background Pattern object or None if
                auto background calculation is not enabled or hasn't been performed yet
        
        Example:
            >>> pattern = Pattern(x_data, y_data)
            >>> pattern.auto_bkg = AutoBackgroundBruckner(width=5, iterations=10)
            >>> # After recalculation, access the auto background pattern:
            >>> auto_bkg = pattern.auto_background_pattern
            >>> # Plot the auto background
            >>> plt.plot(auto_bkg.x, auto_bkg.y)
        """
        return self._auto_background_pattern

    @property
    def auto_background_before_subtraction_pattern(self) -> Pattern:
        """
        Returns the pattern before the auto background subtraction
        :return: background Pattern
        """
        return self._auto_background_before_subtraction_pattern

    def limit(self, x_min: float, x_max: float) -> Pattern:
        """
        Creates a new pattern limited to a specific x-range.
        
        This method extracts a subset of the pattern data that falls within the specified
        x-range boundaries. Only data points where x_min < x < x_max will be included in
        the resulting pattern.
        
        This method does not modify the current pattern but returns a new Pattern object.
        
        :param x_min: Lower limit of the x-range (exclusive)
        :param x_max: Upper limit of the x-range (exclusive)
        :return: A new Pattern object containing only data within the specified range
        
        Example:
            >>> pattern = Pattern(x_data, y_data)
            >>> # Extract data between x=10 and x=20
            >>> limited_pattern = pattern.limit(10.0, 20.0)
            >>> # Extract a small region of interest
            >>> roi_pattern = pattern.limit(15.5, 16.5)
        """
        x, y = self.data
        return Pattern(
            x[np.where((x_min < x) & (x < x_max))],
            y[np.where((x_min < x) & (x < x_max))],
        )

    def extend_to(self, x_value: float, y_value: float) -> Pattern:
        """
        Creates a new pattern by extending the current pattern to a specified x-value.
        
        This method extends the pattern's x-range by adding new data points with the specified
        y-value. The extension can be either to a lower x-value than the current minimum or to
        a higher x-value than the current maximum. The step size of the extension is determined
        by the average step size of the current pattern.
        
        This method is useful for padding patterns to match ranges, creating baseline extensions,
        or preparing data for operations that require matching x-ranges.
        
        This method does not modify the current pattern but returns a new Pattern object.

        :param x_value: Target x-value to extend to. Should be smaller than the minimum x-value or 
                       larger than the maximum x-value of the current pattern.
        :param y_value: Y-value to use for all extension points
        :return: A new Pattern object with the extended x-range
        
        Example:
            >>> pattern = Pattern(x_data, y_data)  # x-range: [10, 50]
            >>> # Extend to lower x-values
            >>> extended_low = pattern.extend_to(5.0, 0.0)  # x-range: [5, 50]
            >>> # Extend to higher x-values
            >>> extended_high = pattern.extend_to(60.0, 0.0)  # x-range: [10, 60]
        """
        x_step = np.mean(np.diff(self.x))
        x_min = np.min(self.x)
        x_max = np.max(self.x)
        if x_value < x_min:
            x_fill = np.arange(x_min - x_step, x_value - x_step * 0.5, -x_step)[::-1]
            y_fill = np.zeros(x_fill.shape)
            y_fill.fill(y_value)

            new_x = np.concatenate((x_fill, self.x))
            new_y = np.concatenate((y_fill, self.y))
        elif x_value > x_max:
            x_fill = np.arange(x_max + x_step, x_value + x_step * 0.5, x_step)
            y_fill = np.zeros(x_fill.shape)
            y_fill.fill(y_value)

            new_x = np.concatenate((self.x, x_fill))
            new_y = np.concatenate((self.y, y_fill))
        else:
            return self

        return Pattern(new_x, new_y)

    def to_dict(self) -> dict:
        """
        Converts the pattern to a dictionary representation.
        
        This method serializes the pattern and all its properties into a dictionary format,
        which can be used for JSON serialization, storage, or transmission. The dictionary
        includes all essential properties of the pattern:
        - name: The pattern name
        - x, y: The original x and y data arrays (converted to lists)
        - scaling, offset, smoothing: The pattern's transformation parameters
        - bkg_pattern: The background pattern (if any), also converted to a dictionary
        - auto_bkg: Information about automatic background extraction settings (if any)
        
        :return: A dictionary containing all pattern properties and data
        
        Example:
            >>> pattern = Pattern(x_data, y_data, name="sample")
            >>> pattern_dict = pattern.to_dict()
            >>> # Save to JSON
            >>> import json
            >>> with open("pattern.json", "w") as f:
            >>>     json.dump(pattern_dict, f)
        """
        return {
            "name": self.name,
            "x": self._original_x.tolist(),
            "y": self._original_y.tolist(),
            "scaling": self.scaling,
            "offset": self.offset,
            "smoothing": self.smoothing,
            "bkg_pattern": (
                self._background_pattern.to_dict()
                if self._background_pattern is not None
                else None
            ),
            "auto_bkg": self._auto_bkg.__class__.__name__ if self._auto_bkg is not None else None,
            "auto_bkg_params": self._auto_bkg.__dict__ if self._auto_bkg is not None else None,
            "auto_bkg_roi": self._auto_bkg_roi if self._auto_bkg_roi is not None else None,
        }

    @staticmethod
    def from_dict(json_dict: dict) -> Pattern:
        """
        Creates a new Pattern object from a dictionary representation.
        
        This static method deserializes a dictionary (typically created by the to_dict method)
        back into a Pattern object, restoring all properties and data. It handles:
        - Basic pattern data (x, y arrays, name)
        - Transformation parameters (scaling, offset, smoothing)
        - Background pattern (if present in the dictionary)
        - Automatic background extraction settings (if present)
        
        This method is the counterpart to to_dict() and is useful for loading patterns
        from JSON files or other serialized formats.
        
        :param json_dict: A dictionary containing pattern data and properties
        :return: A new Pattern object with all properties restored
        
        Example:
            >>> # Load from a dictionary
            >>> pattern = Pattern.from_dict(pattern_dict)
            >>> 
            >>> # Load from a JSON file
            >>> import json
            >>> with open("pattern.json", "r") as f:
            >>>     pattern_dict = json.load(f)
            >>> pattern = Pattern.from_dict(pattern_dict)
        """
        pattern = Pattern(
            np.array(json_dict["x"]), np.array(json_dict["y"]), json_dict["name"]
        )

        pattern.scaling = json_dict["scaling"]
        pattern.offset = json_dict["offset"]

        if json_dict["bkg_pattern"] is not None:
            bkg_pattern = Pattern.from_dict(json_dict["bkg_pattern"])
        else:
            bkg_pattern = None
        pattern.background_pattern = bkg_pattern

        pattern.smoothing = json_dict["smoothing"]
        
        # Restore auto background settings if available
        if "auto_bkg" in json_dict and json_dict["auto_bkg"] is not None:
            from .auto_background import SmoothBrucknerBackground
            if json_dict["auto_bkg"] == "SmoothBrucknerBackground":
                auto_bkg = SmoothBrucknerBackground()
                if "auto_bkg_params" in json_dict and json_dict["auto_bkg_params"] is not None:
                    for key, value in json_dict["auto_bkg_params"].items():
                        setattr(auto_bkg, key, value)
                pattern.auto_bkg = auto_bkg
        
        if "auto_bkg_roi" in json_dict and json_dict["auto_bkg_roi"] is not None:
            pattern.auto_bkg_roi = json_dict["auto_bkg_roi"]
            
        pattern.recalculate_pattern()

        return pattern

    def delete_range(self, x_range: list) -> Pattern:
        """
        Creates a new pattern with data points within a specified x-range removed.
        
        This method is useful for removing unwanted regions from a pattern, such as
        detector artifacts, spurious peaks, or regions with known interference.
        
        This method does not modify the current pattern but returns a new Pattern object.
        
        :param x_range: A list of two float values [min_x, max_x] defining the range
                       of x-values to remove from the pattern
        :return: A new Pattern object with the specified range removed
        
        Example:
            >>> pattern = Pattern(x_data, y_data)
            >>> # Remove data between x=15 and x=20
            >>> filtered_pattern = pattern.delete_range([15.0, 20.0])
            >>> 
            >>> # Remove a detector gap
            >>> no_gap_pattern = pattern.delete_range([41.2, 42.8])
        
        See also:
            delete_ranges: For removing multiple ranges at once
        """
        x, y = self.data
        ind = np.where((x < x_range[0]) | (x > x_range[1]))

        return Pattern(x[ind], y[ind])

    def delete_ranges(self, x_ranges: list) -> Pattern:
        """
        Creates a new pattern with data points within multiple specified x-ranges removed.
        
        This method is similar to delete_range but allows for removing multiple ranges at once,
        which is more efficient than calling delete_range multiple times. It's useful for
        removing multiple artifacts, gaps, or unwanted regions from a pattern.
        
        This method does not modify the current pattern but returns a new Pattern object.
        
        :param x_ranges: A list of lists, where each inner list contains two float values
                        [min_x, max_x] defining a range of x-values to remove
        :return: A new Pattern object with all specified ranges removed
        
        Example:
            >>> pattern = Pattern(x_data, y_data)
            >>> # Remove multiple ranges
            >>> filtered_pattern = pattern.delete_ranges([
            >>>     [15.0, 20.0],  # Remove first region
            >>>     [41.2, 42.8],  # Remove detector gap
            >>>     [55.0, 60.0]   # Remove third region
            >>> ])
        
        See also:
            delete_range: For removing a single range
        """
        x, y = self.data
        for r in x_ranges:
            ind = np.where((x < r[0]) | (x > r[1]))
            x, y = x[ind], y[ind]

        return Pattern(x, y)

    def transform_x(self, fcn: callable) -> Pattern:
        """
        Transforms the x-values of the pattern using the provided function.
        
        This method applies a transformation function to all x-values in the pattern,
        which is useful for converting between different units or scales (e.g., 2θ to q-space,
        wavelength to energy, etc.). The method takes care of also updating any associated
        background patterns and automatic background parameters to maintain consistency.
        
        Unlike most other methods in this class, this method modifies the pattern in-place
        and returns self for method chaining.
        
        :param fcn: A callable function that takes an array of x-values and returns
                   a transformed array of the same shape
        :return: Self (the current Pattern object) with transformed x-values
        
        Example:
            >>> pattern = Pattern(x_data, y_data)  # x in degrees 2θ
            >>> 
            >>> # Convert from 2θ to q-space (Å⁻¹)
            >>> from math import pi, sin
            >>> wavelength = 0.3344  # Å
            >>> pattern.transform_x(lambda x: 4 * pi * sin(x * pi / 360) / wavelength)
            >>> 
            >>> # Convert from eV to keV
            >>> pattern.transform_x(lambda x: x / 1000)
        """
        # Store original values to avoid triggering recalculate_pattern multiple times
        original_x = self._original_x
        self._original_x = fcn(original_x)
        
        if self._background_pattern is not None:
            self._background_pattern.transform_x(fcn)

        if self.auto_bkg_roi is not None:
            self.auto_bkg_roi = fcn(np.array(self.auto_bkg_roi)).tolist()

        if self.auto_bkg is not None:
            self.auto_bkg.transform_x(fcn)

        self.recalculate_pattern()

        return self

    ###########################################################
    # Operators:

    def __sub__(self, other: Pattern) -> Pattern:
        """
        Subtracts another pattern from this pattern (self - other).
        
        This operator allows for pattern subtraction, which is useful for background
        subtraction, reference subtraction, or differential analysis. The method handles
        two cases:
        
        1. If both patterns have identical x-values: Direct subtraction is performed
        2. If patterns have different x-values: The other pattern is linearly interpolated
           to match the x-values of this pattern, but only in the overlapping x-range
        
        This method does not modify either pattern but returns a new Pattern object.
        
        :param other: The Pattern object to subtract from this pattern
        :return: A new Pattern object representing the difference
        :raises BkgNotInRangeError: If there is no overlap between the x-ranges of the two patterns
        
        Example:
            >>> sample = Pattern(x_data, sample_data)
            >>> background = Pattern(x_data, background_data)
            >>> # Subtract background from sample
            >>> subtracted = sample - background
            >>> 
            >>> # Works even with different x-ranges (where they overlap)
            >>> wide_range = Pattern(x_wide, y_wide)  # x: [0, 100]
            >>> narrow_range = Pattern(x_narrow, y_narrow)  # x: [20, 80]
            >>> result = wide_range - narrow_range  # Result has x-range [20, 80]
        """
        orig_x, orig_y = self.data
        other_x, other_y = other.data

        if orig_x.shape != other_x.shape:
            # the background will be interpolated
            other_fcn = interp1d(other_x, other_y, kind="linear")

            # find overlapping x and y values:
            ind = np.where((orig_x <= np.max(other_x)) & (orig_x >= np.min(other_x)))
            x = orig_x[ind]
            y = orig_y[ind]

            if len(x) == 0:
                # if there is no overlapping between background and pattern, raise an error
                raise BkgNotInRangeError(self.name)
            return Pattern(x, y - other_fcn(x))
        else:
            return Pattern(orig_x, orig_y - other_y)

    def __add__(self, other: Pattern) -> Pattern:
        """
        Adds another pattern to this pattern (self + other).
        
        This operator allows for pattern addition, which is useful for combining patterns,
        merging datasets, or creating composite patterns. The method handles two cases:
        
        1. If both patterns have identical x-values: Direct addition is performed
        2. If patterns have different x-values: The other pattern is linearly interpolated
           to match the x-values of this pattern, but only in the overlapping x-range
        
        This method does not modify either pattern but returns a new Pattern object.
        
        :param other: The Pattern object to add to this pattern
        :return: A new Pattern object representing the sum
        :raises BkgNotInRangeError: If there is no overlap between the x-ranges of the two patterns
        
        Example:
            >>> pattern1 = Pattern(x_data1, y_data1)
            >>> pattern2 = Pattern(x_data2, y_data2)
            >>> # Add patterns together
            >>> combined = pattern1 + pattern2
            >>> 
            >>> # Works even with different x-ranges (where they overlap)
            >>> low_range = Pattern(x_low, y_low)  # x: [0, 50]
            >>> high_range = Pattern(x_high, y_high)  # x: [40, 100]
            >>> result = low_range + high_range  # Result has x-range [40, 50]
        """
        orig_x, orig_y = self.data
        other_x, other_y = other.data

        if orig_x.shape != other_x.shape:
            # the background will be interpolated
            other_fcn = interp1d(other_x, other_y, kind="linear")

            # find overlapping x and y values:
            ind = np.where((orig_x <= np.max(other_x)) & (orig_x >= np.min(other_x)))
            x = orig_x[ind]
            y = orig_y[ind]

            if len(x) == 0:
                # if there is no overlapping between background and pattern, raise an error
                raise BkgNotInRangeError(self.name)
            return Pattern(x, y + other_fcn(x))
        else:
            return Pattern(orig_x, orig_y + other_y)

    def __rmul__(self, other: float) -> Pattern:
        """
        Multiplies this pattern by a scalar value (other * self).
        
        This operator enables scalar multiplication of patterns, which is useful for
        scaling, normalization, or applying weighting factors. The multiplication
        affects only the y-values; x-values remain unchanged.
        
        This is the right multiplication operator, allowing expressions like:
        `2.5 * pattern` (where pattern is a Pattern object).
        
        This method does not modify the current pattern but returns a new Pattern object.
        
        :param other: A scalar value to multiply the pattern's y-values by
        :return: A new Pattern object with scaled y-values
        
        Example:
            >>> pattern = Pattern(x_data, y_data)
            >>> # Scale the pattern by a factor of 2
            >>> doubled = 2.0 * pattern
            >>> # Scale the pattern by a factor of 0.5
            >>> halved = 0.5 * pattern
        """
        orig_x, orig_y = self.data
        return Pattern(np.copy(orig_x), np.copy(orig_y) * other)

    def __eq__(self, other: Pattern) -> bool:
        """
        Checks if this pattern is equal to another pattern (self == other).
        
        Two patterns are considered equal if they have identical x and y data arrays.
        Other properties like name, scaling, offset, etc. are not considered in the
        equality check.
        
        :param other: The Pattern object to compare with
        :return: True if the patterns have identical data, False otherwise
        
        Example:
            >>> pattern1 = Pattern(x_data, y_data)
            >>> pattern2 = Pattern(x_data, y_data)
            >>> pattern3 = Pattern(x_data, different_y_data)
            >>> 
            >>> pattern1 == pattern2  # Returns: True
            >>> pattern1 == pattern3  # Returns: False
            >>> pattern1 == "not a pattern"  # Returns: False
        """
        if not isinstance(other, Pattern):
            return False
        if np.array_equal(self.data, other.data):
            return True
        return False

    def __len__(self):
        """
        Returns the number of data points in the pattern.
        
        This method allows using the built-in len() function with Pattern objects.
        
        :return: The number of data points (length of the x and y arrays)
        
        Example:
            >>> pattern = Pattern(x_data, y_data)
            >>> num_points = len(pattern)  # Get the number of data points
        """
        return len(self.x)

    def __str__(self):
        """
        Returns a string representation of the pattern.
        
        This method provides a human-readable description of the pattern when
        it is printed or converted to a string.
        
        :return: A string describing the pattern name and number of data points
        
        Example:
            >>> pattern = Pattern(x_data, y_data, name="sample")
            >>> print(pattern)  # Outputs: "Pattern 'sample' with 1000 points"
            >>> str(pattern)    # Returns: "Pattern 'sample' with 1000 points"
        """
        return f"Pattern '{self.name}' with {len(self)} points"

    def copy(self) -> Pattern:
        """
        Creates a deep copy of the pattern.
        
        This method creates a completely independent copy of the pattern with all its
        properties and data. The copy includes:
        - Original x and y data arrays (copied, not referenced)
        - Pattern name
        - Transformation parameters (scaling, offset, smoothing)
        - Background pattern (if present, also deeply copied)
        - Automatic background extraction settings (if present)
        
        Deep copying is useful when you need to modify a pattern without affecting
        the original, or when you need to preserve a pattern state.
        
        :return: A new Pattern object that is a deep copy of this pattern
        
        Example:
            >>> original = Pattern(x_data, y_data, name="original")
            >>> original.scaling = 2.0
            >>> 
            >>> # Create a deep copy
            >>> copy = original.copy()
            >>> 
            >>> # Modify the copy without affecting the original
            >>> copy.scaling = 1.5
            >>> copy.name = "modified"
            >>> 
            >>> print(original.scaling)  # Still 2.0
            >>> print(copy.scaling)      # Now 1.5
        """
        pattern = Pattern(
            np.copy(self._original_x),
            np.copy(self._original_y),
            self.name
        )
        
        pattern.scaling = self.scaling
        pattern.offset = self.offset
        pattern.smoothing = self.smoothing
        
        if self._background_pattern is not None:
            pattern.background_pattern = self._background_pattern.copy()
            
        if self._auto_bkg is not None:
            # Import here to avoid circular imports
            from .auto_background import SmoothBrucknerBackground
            if isinstance(self._auto_bkg, SmoothBrucknerBackground):
                auto_bkg = SmoothBrucknerBackground()
                for key, value in self._auto_bkg.__dict__.items():
                    setattr(auto_bkg, key, value)
                pattern.auto_bkg = auto_bkg
                
        if self._auto_bkg_roi is not None:
            pattern.auto_bkg_roi = list(self._auto_bkg_roi)
            
        return pattern

    @property
    def changed(self) -> Signal:
        """
        Signal that is emitted whenever the pattern data changes.
        
        This signal allows other objects to react to changes in this pattern's data.
        It is emitted after any operation that modifies the pattern data, such as:
        - Setting a new background pattern
        - Changing scaling, offset, or smoothing
        - Modifying x or y data
        - Applying automatic background subtraction
        
        When emitted, this signal passes the pattern itself (self) as an argument
        to all connected callbacks, allowing them to directly access the pattern
        that changed.
        
        The signal can be connected to callback functions that will be executed
        when the pattern changes. This is particularly useful for implementing
        reactive UI updates or for chaining pattern processing steps.
        
        Example:
            >>> pattern = Pattern(x_data, y_data)
            >>> 
            >>> # Connect a callback to the changed signal
            >>> def on_pattern_changed(pattern):
            >>>     print(f"Pattern '{pattern.name}' has changed")
            >>>     print(f"New max value: {pattern.y.max()}")
            >>> 
            >>> pattern.changed.connect(on_pattern_changed)
            >>> 
            >>> # Now when we modify the pattern, our callback will be called with the pattern as argument
            >>> pattern.scaling = 2.0  # Triggers callback with pattern as argument
            >>> 
            >>> # Disconnect the callback when no longer needed
            >>> pattern.changed.disconnect(on_pattern_changed)
        
        See also:
            The Signal class in xypattern.util.signal for more details on
            connecting and disconnecting callbacks.
        """
        return self._changed
        
    @changed.setter
    def changed(self, value):
        """
        Setter for the changed property.
        
        This setter is provided to prevent direct assignment to the changed property.
        The changed signal should not be replaced, only connected to or disconnected from.
        
        :param value: Ignored
        :raises AttributeError: Always raised to prevent assignment
        """
        raise AttributeError("Cannot assign to the 'changed' property. Use connect() and disconnect() methods instead.")


class BkgNotInRangeError(Exception):
    def __init__(self, pattern_name: str):
        self.pattern_name = pattern_name

    def __str__(self):
        return (
            "The background range does not overlap with the Pattern range for "
            + self.pattern_name
        )
