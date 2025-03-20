![codecov](https://codecov.io/gh/CPrescher/xypattern/graph/badge.svg?token=05FUJFOV3R)
![CI](https://github.com/CPrescher/xypattern/actions/workflows/CI.yml/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/xypattern/badge/?version=latest)](https://xypattern.readthedocs.io/en/latest/?badge=latest)

# xypattern

## Description

A simple small library to handle x-y patterns, such as are collected with x-ray diffraction or Raman spectroscopy. 

## Installation

```bash
pip install xypattern
```

## Features

- Load and save patterns from/to various file formats (.xy, .chi, .fxye)
- Apply scaling, offset, and smoothing to patterns
- Background subtraction (manual or automatic)
- Pattern manipulation (limiting, extending, deleting ranges)
- Mathematical operations (addition, subtraction, multiplication)
- Pattern transformation (x-axis transformation)
- Pattern rebinning
- Pattern serialization to/from dictionaries

## Usage Examples

### Reading a file
```python
from xypattern import Pattern
import matplotlib.pyplot as plt

p1 = Pattern.from_file('path/to/file')
p1.scaling = 0.5
p1.offset = 0.1

plt.plot(p1.x, p1.y)
plt.show()
```

### Use a background pattern

```python
p2 = Pattern.from_file('path/to/file')
p2.scaling = 0.9
p1.background_pattern = p2
```

### Automatic background subtraction

```python
from xypattern.auto_background import SmoothBrucknerBackground

p1 = Pattern.from_file('path/to/file')
p1.auto_bkg = SmoothBrucknerBackground(smooth_width=0.2, iterations=30, cheb_order=20)
p1.auto_bkg_roi = [10.0, 60.0]  # Optional region of interest for background calculation
```

### Pattern manipulation

```python
# Limit pattern to a specific x-range
limited_pattern = p1.limit(10.0, 60.0)

# Extend pattern to a specific x-value
extended_pattern = p1.extend_to(5.0, 0.0)

# Delete specific x-ranges
cleaned_pattern = p1.delete_ranges([[10.0, 15.0], [40.0, 45.0]])

# Transform x-axis (e.g., convert from 2theta to q-space)
from math import pi, sin
wavelength = 0.3344  # Å
transformed_pattern = p1.transform_x(lambda x: 4 * pi * sin(x * pi / 360) / wavelength)
```

### Scale and stitch multiple patterns

```python
p1 = Pattern.from_file('path/to/file1')
p2 = Pattern.from_file('path/to/file2')
p3 = Pattern.from_file('path/to/file3')

from xypattern.combine import scale_patterns, stitch_patterns

patterns = [p1, p2, p3]
scale_patterns(patterns)
stitched_pattern = stitch_patterns(patterns)
```

### Pattern serialization

```python
# Save pattern to dictionary (useful for JSON serialization)
pattern_dict = p1.to_dict()

# Create pattern from dictionary
p2 = Pattern.from_dict(pattern_dict)

# Create a deep copy of a pattern
p2 = p1.copy()
```

## API Documentation

For detailed API documentation, please visit [https://xypattern.readthedocs.io/](https://xypattern.readthedocs.io/) or [https://cprescher.github.io/xypattern/](https://cprescher.github.io/xypattern/).

### Building Documentation

The project documentation is built using Sphinx. To build the documentation locally:

```bash
# Install development dependencies
poetry install --with dev

# Navigate to the docs directory
cd docs

# Build the documentation
make html
```

The built documentation will be available in the `docs/_build/html` directory. Open `index.html` in your web browser to view it.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
