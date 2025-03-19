"""
GPS Tools - A Python package for working with GPS coordinates.

This package provides tools for working with different GPS coordinate systems,
calculating distances, performing coordinate conversions, and more.
"""

__version__ = '0.1.7'

from .core import Coordinate, UTMCoordinate, MGRSCoordinate, CoordinateList
from .converters import (
    latlon_to_utm, utm_to_latlon, decimal_to_dms, dms_to_decimal, 
    haversine_distance, latlon_to_mgrs, mgrs_to_utm, mgrs_to_latlon
)
from .distance import (
    haversine_distance, vincenty_distance, bearing,
    destination_point, path_distance, midpoint
)
from .calculations import (
    calculate_distance, calculate_destination, 
    normalize_longitude, calculate_path_distance,
    calculate_centroid, calculate_bbox
)
from .unified_converter import convert_to_latlon

__all__ = [
    # Version
    "__version__",
    
    # Core classes
    "Coordinate", "UTMCoordinate", "MGRSCoordinate", "CoordinateList",
    
    # Converters
    "latlon_to_utm", "utm_to_latlon", "decimal_to_dms", "dms_to_decimal",
    "latlon_to_mgrs", "mgrs_to_utm", "mgrs_to_latlon",
    
    # Distance calculations
    "haversine_distance", "vincenty_distance", "bearing",
    "destination_point", "path_distance", "midpoint",
    
    # Calculations
    "calculate_distance", "calculate_destination",
    "normalize_longitude", "calculate_path_distance",
    "calculate_centroid", "calculate_bbox",
    
    # Unified Converter
    "convert_to_latlon"
]

__author__ = 'Your Name'
__email__ = 'your.email@example.com'

# Add any package-level imports here 