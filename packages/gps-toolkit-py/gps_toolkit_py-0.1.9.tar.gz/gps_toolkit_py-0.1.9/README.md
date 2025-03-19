# GPS Toolkit for Python

[![PyPI version](https://img.shields.io/pypi/v/gps-toolkit-py.svg)](https://pypi.org/project/gps-toolkit-py/)
[![Python versions](https://img.shields.io/pypi/pyversions/gps-toolkit-py.svg)](https://pypi.org/project/gps-toolkit-py/)
[![License](https://img.shields.io/pypi/l/gps-toolkit-py.svg)](https://github.com/username/gps-toolkit-py/blob/main/LICENSE)

A powerful, comprehensive Python library for working with GPS coordinates, with support for multiple coordinate systems, distance calculations, and coordinate transformations.

## Features

- **Multiple Coordinate Systems**
  - Decimal degrees (latitude/longitude)
  - Universal Transverse Mercator (UTM)
  - Military Grid Reference System (MGRS)

- **Distance Calculations**
  - Haversine formula (great-circle distance)
  - Vincenty's formula (ellipsoidal distance)
  - Path distances for multiple points

- **Coordinate Conversions**
  - Convert between lat/lon, UTM, and MGRS
  - Parse coordinates from various string formats
  - Unified conversion interface

- **Advanced Utilities**
  - Calculate bearings between points
  - Find destination points from a starting position
  - Calculate centroids and bounding boxes
  - Create coordinate collections with custom properties

## Installation

### Basic Installation

```bash
pip install gps-toolkit-py
```

### With Optional Features

```bash
# For visualization capabilities (matplotlib, folium)
pip install gps-toolkit-py[viz]

# For GIS integrations (shapely, geopandas)
pip install gps-toolkit-py[gis]

# For development (testing, linting, etc.)
pip install gps-toolkit-py[dev]
```

## Quick Start

### Basic Coordinate Usage

```python
from gps_toolkit_py import Coordinate

# Create a coordinate
nyc = Coordinate(40.7128, -74.0060, name="New York")
sf = Coordinate(37.7749, -122.4194, name="San Francisco")

# Access properties
print(f"NYC is at {nyc.latitude}°N, {abs(nyc.longitude)}°W")
# Output: NYC is at 40.7128°N, 74.006°W

# String representation
print(nyc)
# Output: New York: 40.7128°N, 74.0060°W
```

### Distance Calculations

```python
from gps_toolkit_py import Coordinate
from gps_toolkit_py.distance import haversine_distance, vincenty_distance

# Create coordinates
nyc = Coordinate(40.7128, -74.0060, name="New York")
la = Coordinate(34.0522, -118.2437, name="Los Angeles")

# Calculate distances
haversine_dist = haversine_distance(nyc, la)
vincenty_dist = vincenty_distance(nyc, la)

print(f"Haversine distance: {haversine_dist/1000:.2f} km")
print(f"Vincenty distance: {vincenty_dist/1000:.2f} km")
```

### Coordinate Conversions

```python
from gps_toolkit_py import Coordinate
from gps_toolkit_py.converters import latlon_to_utm, utm_to_latlon, latlon_to_mgrs

# Convert to UTM
lat, lon = 40.7128, -74.0060  # NYC
zone_number, zone_letter, easting, northing = latlon_to_utm(lat, lon)
print(f"UTM: {zone_number}{zone_letter} {easting:.1f}E {northing:.1f}N")

# Convert back to lat/lon
lat2, lon2 = utm_to_latlon(zone_number, zone_letter, easting, northing)
print(f"Back to lat/lon: {lat2:.4f}, {lon2:.4f}")

# Convert to MGRS
mgrs = latlon_to_mgrs(lat, lon)
print(f"MGRS: {mgrs}")
```

### Working with Coordinate Collections

```python
from gps_toolkit_py import Coordinate, CoordinateList
from gps_toolkit_py.calculations import calculate_path_distance, calculate_centroid

# Create a path of coordinates
path = CoordinateList([
    Coordinate(40.7128, -74.0060, name="New York"),
    Coordinate(39.9526, -75.1652, name="Philadelphia"),
    Coordinate(38.9072, -77.0369, name="Washington DC")
])

# Calculate the total path distance
total_distance = calculate_path_distance(path.coordinates)
print(f"Total path distance: {total_distance/1000:.2f} km")

# Find the centroid of the coordinates
centroid = calculate_centroid(path.coordinates)
print(f"Centroid: {centroid}")
```

## API Reference

### Core Classes

- `Coordinate` - Basic latitude/longitude coordinate representation
- `UTMCoordinate` - UTM coordinate representation
- `MGRSCoordinate` - MGRS coordinate representation
- `CoordinateList` - Collection of coordinates

### Distance Calculation Functions

- `haversine_distance` - Great-circle distance
- `vincenty_distance` - Ellipsoidal distance
- `bearing` - Calculate bearing between two points
- `destination_point` - Find destination from start point
- `path_distance` - Total distance along a path
- `midpoint` - Find midpoint between two coordinates

### Conversion Functions

- `latlon_to_utm`, `utm_to_latlon` - UTM conversions
- `decimal_to_dms`, `dms_to_decimal` - DMS format conversions
- `latlon_to_mgrs`, `mgrs_to_latlon` - MGRS conversions
- `convert_to_latlon` - Unified conversion interface

### Calculation Functions

- `calculate_distance` - High-level distance calculator
- `calculate_destination` - Calculate destination coordinate
- `calculate_path_distance` - Distance along multiple points
- `calculate_centroid` - Find centroid of multiple coordinates
- `calculate_bbox` - Calculate a bounding box

## Requirements

- Python 3.7+
- numpy
- scipy
- pyproj

## Contributing

Contributions are welcome! Whether it's bug reports, feature requests, or pull requests, all contributions help improve the library.

1. **Fork the repository**
2. **Create your feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add some amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

Before submitting:
- Make sure your code follows the project's style
- Add or update tests as necessary
- Update documentation to reflect your changes

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all contributors who have helped improve GPS Toolkit
- Inspired by various GPS and geospatial libraries

---

Made with ❤️ by the GPS Toolkit Team 