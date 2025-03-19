"""
Coordinate calculation utilities for GPS data.

This module provides functions to calculate distances, bearings,
centroids, and other properties related to GPS coordinates.
"""

import math
from typing import Tuple, List, Dict, Union, Optional

from .core import Coordinate
from .distance import haversine_distance


def calculate_distance(coord1: Coordinate, coord2: Coordinate) -> float:
    """
    Calculate the distance between two coordinates.
    
    Args:
        coord1: First coordinate
        coord2: Second coordinate
        
    Returns:
        Distance in meters
        
    Examples:
        >>> nyc = Coordinate(40.7128, -74.0060)
        >>> sf = Coordinate(37.7749, -122.4194)
        >>> calculate_distance(nyc, sf)
        4130000.0  # approximately
    """
    return haversine_distance(
        coord1.latitude, coord1.longitude,
        coord2.latitude, coord2.longitude
    )


def calculate_destination(
    start: Coordinate, 
    bearing: float, 
    distance: float
) -> Coordinate:
    """
    Calculate the destination coordinate given a starting point, bearing, and distance.
    
    Args:
        start: Starting coordinate
        bearing: Bearing in degrees (0 = North, 90 = East, 180 = South, 270 = West)
        distance: Distance in meters
        
    Returns:
        Destination coordinate
        
    Examples:
        >>> start = Coordinate(40.7128, -74.0060)  # NYC
        >>> calculate_destination(start, 90.0, 10000.0)  # 10km east
        Coordinate(latitude=40.7128, longitude=-73.8779, elevation=None, name=None)
    """
    # Earth's radius in meters
    earth_radius = 6371000
    
    # Convert to radians
    lat1 = math.radians(start.latitude)
    lon1 = math.radians(start.longitude)
    bearing_rad = math.radians(bearing)
    
    # Angular distance in radians
    angular_distance = distance / earth_radius
    
    # Calculate new latitude
    lat2 = math.asin(
        math.sin(lat1) * math.cos(angular_distance) +
        math.cos(lat1) * math.sin(angular_distance) * math.cos(bearing_rad)
    )
    
    # Calculate new longitude
    lon2 = lon1 + math.atan2(
        math.sin(bearing_rad) * math.sin(angular_distance) * math.cos(lat1),
        math.cos(angular_distance) - math.sin(lat1) * math.sin(lat2)
    )
    
    # Normalize longitude to -180 to 180
    lon2 = normalize_longitude(math.degrees(lon2))
    
    # Return new coordinate
    return Coordinate(
        math.degrees(lat2),
        lon2,
        elevation=start.elevation,
        name=f"Destination from {start.name}" if start.name else None
    )


def normalize_longitude(longitude: float) -> float:
    """
    Normalize a longitude value to be within -180 to 180 degrees.
    
    Args:
        longitude: Longitude in degrees
        
    Returns:
        Normalized longitude in degrees
        
    Examples:
        >>> normalize_longitude(185.0)
        -175.0
        >>> normalize_longitude(-185.0)
        175.0
    """
    # Normalize to -180 to 180
    while longitude > 180:
        longitude -= 360
    while longitude < -180:
        longitude += 360
    return longitude


def calculate_path_distance(coordinates: List[Coordinate]) -> float:
    """
    Calculate the total distance along a path of coordinates.
    
    Args:
        coordinates: List of coordinates forming the path
        
    Returns:
        Total distance in meters
        
    Examples:
        >>> nyc = Coordinate(40.7128, -74.0060)
        >>> philly = Coordinate(39.9526, -75.1652)
        >>> dc = Coordinate(38.9072, -77.0369)
        >>> calculate_path_distance([nyc, philly, dc])
        328000.0  # approximately
    """
    if len(coordinates) < 2:
        return 0.0
    
    total_distance = 0.0
    for i in range(len(coordinates) - 1):
        total_distance += calculate_distance(coordinates[i], coordinates[i + 1])
    
    return total_distance


def calculate_centroid(coordinates: List[Coordinate]) -> Coordinate:
    """
    Calculate the centroid (average position) of a set of coordinates.
    
    Args:
        coordinates: List of coordinates
        
    Returns:
        Centroid coordinate
        
    Examples:
        >>> nyc = Coordinate(40.7128, -74.0060)
        >>> sf = Coordinate(37.7749, -122.4194)
        >>> calculate_centroid([nyc, sf])
        Coordinate(latitude=39.2439, longitude=-98.2127, elevation=None, name=None)
    """
    if not coordinates:
        raise ValueError("Cannot calculate centroid of empty list")
    
    # Convert to cartesian coordinates
    x_sum = y_sum = z_sum = 0.0
    elevation_sum = 0.0
    elevation_count = 0
    
    for coord in coordinates:
        # Convert to radians
        lat_rad = math.radians(coord.latitude)
        lon_rad = math.radians(coord.longitude)
        
        # Convert to cartesian coordinates
        x = math.cos(lat_rad) * math.cos(lon_rad)
        y = math.cos(lat_rad) * math.sin(lon_rad)
        z = math.sin(lat_rad)
        
        # Sum cartesian coordinates
        x_sum += x
        y_sum += y
        z_sum += z
        
        # Track elevation if available
        if coord.elevation is not None:
            elevation_sum += coord.elevation
            elevation_count += 1
    
    # Calculate average
    x_avg = x_sum / len(coordinates)
    y_avg = y_sum / len(coordinates)
    z_avg = z_sum / len(coordinates)
    
    # Convert back to lat/lon
    lon = math.atan2(y_avg, x_avg)
    hyp = math.sqrt(x_avg * x_avg + y_avg * y_avg)
    lat = math.atan2(z_avg, hyp)
    
    # Calculate average elevation if available
    elevation = elevation_sum / elevation_count if elevation_count > 0 else None
    
    # Return centroid coordinate
    return Coordinate(
        math.degrees(lat),
        math.degrees(lon),
        elevation=elevation,
        name="Centroid"
    )


def calculate_bbox(coordinates: List[Coordinate]) -> Tuple[Coordinate, Coordinate]:
    """
    Calculate the bounding box of a set of coordinates.
    
    Args:
        coordinates: List of coordinates
        
    Returns:
        Tuple of (southwest corner, northeast corner) coordinates
        
    Examples:
        >>> nyc = Coordinate(40.7128, -74.0060)
        >>> sf = Coordinate(37.7749, -122.4194)
        >>> sw, ne = calculate_bbox([nyc, sf])
        >>> sw
        Coordinate(latitude=37.7749, longitude=-122.4194, elevation=None, name="Southwest Corner")
        >>> ne
        Coordinate(latitude=40.7128, longitude=-74.0060, elevation=None, name="Northeast Corner")
    """
    if not coordinates:
        raise ValueError("Cannot calculate bounding box of empty list")
    
    # Initialize min/max values
    min_lat = max_lat = coordinates[0].latitude
    min_lon = max_lon = coordinates[0].longitude
    
    # Find min/max lat/lon
    for coord in coordinates:
        min_lat = min(min_lat, coord.latitude)
        max_lat = max(max_lat, coord.latitude)
        min_lon = min(min_lon, coord.longitude)
        max_lon = max(max_lon, coord.longitude)
    
    # Create southwest and northeast corners
    sw = Coordinate(min_lat, min_lon, name="Southwest Corner")
    ne = Coordinate(max_lat, max_lon, name="Northeast Corner")
    
    return (sw, ne) 