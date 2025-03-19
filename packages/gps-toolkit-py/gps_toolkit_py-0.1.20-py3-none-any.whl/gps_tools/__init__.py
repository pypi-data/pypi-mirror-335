"""
GPS Tools - A Python package for working with GPS coordinates.

This package provides tools for working with different GPS coordinate systems,
calculating distances, performing coordinate conversions, and more.
"""

__version__ = '0.1.20'

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


def help(topic=None):
    """
    Display help information about GPS Toolkit.
    
    Args:
        topic (str, optional): Specific topic to get help on.
            Valid topics: 'coordinate', 'distance', 'conversion', 'utm', 'mgrs', 'examples'
            
    Returns:
        None - prints help information directly
        
    Examples:
        >>> import gps_tools as gps
        >>> gps.help()              # General help
        >>> gps.help('coordinate')  # Help on coordinate usage
        >>> gps.help('examples')    # Show usage examples
    """
    topics = {
        'coordinate': """
Coordinate Objects:
------------------
Create and work with geographic coordinates:

    from gps_tools import Coordinate
    
    # Create a coordinate
    nyc = Coordinate(40.7128, -74.0060, name="New York")
    
    # Access properties
    print(nyc.latitude)        # 40.7128
    print(nyc.longitude)       # -74.006
    print(nyc.name)            # "New York"
    
    # String representation
    print(nyc)                 # New York: 40.7128°N, 74.0060°W
        """,
        
        'distance': """
Distance Calculations:
--------------------
Calculate distances between coordinates:

    from gps_tools import Coordinate
    from gps_tools import haversine_distance, vincenty_distance
    
    nyc = Coordinate(40.7128, -74.0060, name="New York")
    la = Coordinate(34.0522, -118.2437, name="Los Angeles")
    
    # Calculate distances
    dist_haversine = haversine_distance(nyc, la)    # Great-circle distance
    dist_vincenty = vincenty_distance(nyc, la)      # Ellipsoidal distance
    
    # Get the bearing between points
    bearing_value = bearing(nyc, la)                # In degrees
    
    # Find destination point
    dest = destination_point(nyc, bearing_value, 500000)  # 500km in that direction
        """,
        
        'conversion': """
Coordinate Conversions:
---------------------
Convert between different coordinate systems:

    from gps_tools import Coordinate
    from gps_tools import latlon_to_utm, utm_to_latlon, decimal_to_dms
    
    # Convert lat/lon to UTM
    zone_num, zone_letter, easting, northing = latlon_to_utm(40.7128, -74.0060)
    
    # Convert UTM to lat/lon
    lat, lon = utm_to_latlon(zone_num, zone_letter, easting, northing)
    
    # Convert decimal degrees to DMS format
    deg, min, sec, direction = decimal_to_dms(40.7128, 'lat')
    print(f"{deg}° {min}' {sec}\" {direction}")  # 40° 42' 46" N
        """,
        
        'utm': """
UTM Coordinates:
--------------
Work with Universal Transverse Mercator coordinates:

    from gps_tools import UTMCoordinate
    from gps_tools import latlon_to_utm, utm_to_latlon
    
    # Create a UTM coordinate
    zone_num, zone_letter, easting, northing = latlon_to_utm(40.7128, -74.0060)
    utm_coord = UTMCoordinate(easting, northing, zone_num, zone_letter)
    
    # Convert back to lat/lon
    lat, lon = utm_to_latlon(utm_coord.zone_number, utm_coord.zone_letter, 
                             utm_coord.easting, utm_coord.northing)
        """,
        
        'mgrs': """
MGRS Coordinates:
--------------
Work with Military Grid Reference System coordinates:

    from gps_tools import MGRSCoordinate
    from gps_tools import latlon_to_mgrs, mgrs_to_latlon
    
    # Convert lat/lon to MGRS
    mgrs_str = latlon_to_mgrs(40.7128, -74.0060)
    
    # Create MGRS coordinate from string
    mgrs_parts = mgrs_str.split(' ')  # Parse components
    mgrs_coord = MGRSCoordinate(
        int(mgrs_parts[0][0:2]),                # zone_number
        mgrs_parts[0][2],                       # zone_letter
        mgrs_parts[1],                          # grid_square
        int(mgrs_parts[2][0:precision]),        # easting
        int(mgrs_parts[2][precision:]),         # northing
        precision                               # precision
    )
    
    # Convert MGRS to lat/lon
    lat, lon = mgrs_to_latlon(mgrs_str)
        """,
        
        'examples': """
Usage Examples:
-------------
Example 1: Distance between cities
    from gps_tools import Coordinate, haversine_distance
    
    nyc = Coordinate(40.7128, -74.0060, name="New York")
    sf = Coordinate(37.7749, -122.4194, name="San Francisco")
    
    distance = haversine_distance(nyc, sf)
    print(f"Distance: {distance/1000:.1f} km")

Example 2: Calculate a path distance
    from gps_tools import Coordinate, CoordinateList
    from gps_tools import calculate_path_distance
    
    route = CoordinateList([
        Coordinate(40.7128, -74.0060, name="New York"),
        Coordinate(39.9526, -75.1652, name="Philadelphia"),
        Coordinate(38.9072, -77.0369, name="Washington DC")
    ])
    
    total_distance = calculate_path_distance(route.coordinates)
    print(f"Total route distance: {total_distance/1000:.1f} km")

Example 3: Convert coordinates
    from gps_tools import convert_to_latlon
    
    # Convert from various formats to lat/lon
    lat, lon, _ = convert_to_latlon("40°42'46\"N, 74°0'21\"W")
    lat, lon, _ = convert_to_latlon("18TWL8369052410")  # MGRS
        """
    }
    
    if topic is None:
        print("""
GPS Toolkit for Python - Help
============================

Main Features:
- Coordinate handling (lat/lon, UTM, MGRS)
- Distance calculations
- Coordinate conversions
- Path calculations and utilities

Available Topics:
- 'coordinate': Working with coordinate objects
- 'distance': Distance and bearing calculations
- 'conversion': Converting between coordinate systems
- 'utm': Working with UTM coordinates
- 'mgrs': Working with MGRS coordinates
- 'examples': Usage examples

For detailed help on a specific topic, use:
    >>> gps_tools.help('topic')
        """)
        return
    
    topic = topic.lower()
    if topic in topics:
        print(topics[topic])
    else:
        print(f"Topic '{topic}' not found. Valid topics: {', '.join(topics.keys())}")
        print("For general help, use gps_tools.help()")


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
    "convert_to_latlon",
    
    # Help function
    "help"
]

__author__ = 'GPS Toolkit Team'
__email__ = 'example@example.com'

# Add any package-level imports here 