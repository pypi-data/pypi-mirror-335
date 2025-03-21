"""
Distance calculation functions for GPS coordinates.

This module provides various functions for calculating distances, bearings,
and other spatial relationships between coordinates.
"""

import math
from typing import List, Tuple, Union, Optional

from .core import Coordinate


def haversine_distance(point1: Coordinate, point2: Coordinate, 
                       radius: float = 6371000.0) -> float:
    """
    Calculate the great-circle distance between two points on a sphere
    using the haversine formula.
    
    Args:
        point1: The first coordinate
        point2: The second coordinate
        radius: Radius of the sphere in meters (default Earth's radius)
    
    Returns:
        Distance in meters
        
    Examples:
        >>> from gps_tools import Coordinate
        >>> new_york = Coordinate(40.7128, -74.0060)
        >>> london = Coordinate(51.5074, -0.1278)
        >>> distance = haversine_distance(new_york, london)
        >>> round(distance / 1000)  # Convert to km and round
        5570
    """
    # Convert latitude and longitude from degrees to radians
    lat1 = math.radians(point1.latitude)
    lon1 = math.radians(point1.longitude)
    lat2 = math.radians(point2.latitude)
    lon2 = math.radians(point2.longitude)
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Calculate the distance
    distance = radius * c
    
    return distance


def vincenty_distance(point1: Coordinate, point2: Coordinate, 
                      iterations: int = 100, tolerance: float = 1e-12) -> float:
    """
    Calculate the distance between two points using the Vincenty formula.
    
    This is a more accurate method for calculating distances on an ellipsoid (Earth).
    
    Args:
        point1: The first coordinate
        point2: The second coordinate
        iterations: Maximum number of iterations for convergence
        tolerance: Convergence tolerance
        
    Returns:
        Distance in meters
        
    Raises:
        ValueError: If the algorithm fails to converge
    """
    # WGS-84 ellipsoid parameters
    a = 6378137.0  # semi-major axis in meters
    f = 1 / 298.257223563  # flattening
    b = (1 - f) * a  # semi-minor axis
    
    # Convert latitude and longitude from degrees to radians
    lat1 = math.radians(point1.latitude)
    lon1 = math.radians(point1.longitude)
    lat2 = math.radians(point2.latitude)
    lon2 = math.radians(point2.longitude)
    
    # Difference in longitude
    L = lon2 - lon1
    
    # Reduced latitudes (latitudes on the auxiliary sphere)
    U1 = math.atan((1 - f) * math.tan(lat1))
    U2 = math.atan((1 - f) * math.tan(lat2))
    
    sinU1 = math.sin(U1)
    cosU1 = math.cos(U1)
    sinU2 = math.sin(U2)
    cosU2 = math.cos(U2)
    
    # Initial value
    lambda_old = L
    
    for _ in range(iterations):
        sinLambda = math.sin(lambda_old)
        cosLambda = math.cos(lambda_old)
        
        sinSigma = math.sqrt((cosU2 * sinLambda) ** 2 + 
                            (cosU1 * sinU2 - sinU1 * cosU2 * cosLambda) ** 2)
        
        # Check for coincident points
        if sinSigma == 0:
            return 0.0
        
        cosSigma = sinU1 * sinU2 + cosU1 * cosU2 * cosLambda
        sigma = math.atan2(sinSigma, cosSigma)
        
        sinAlpha = cosU1 * cosU2 * sinLambda / sinSigma
        cosSqAlpha = 1 - sinAlpha ** 2
        
        # To avoid division by zero
        if cosSqAlpha == 0:
            cos2SigmaM = 0
        else:
            cos2SigmaM = cosSigma - 2 * sinU1 * sinU2 / cosSqAlpha
        
        C = f / 16 * cosSqAlpha * (4 + f * (4 - 3 * cosSqAlpha))
        
        lambda_new = L + (1 - C) * f * sinAlpha * (
            sigma + C * sinSigma * (
                cos2SigmaM + C * cosSigma * (
                    -1 + 2 * cos2SigmaM ** 2
                )
            )
        )
        
        # Check for convergence
        if abs(lambda_new - lambda_old) < tolerance:
            break
            
        lambda_old = lambda_new
    else:
        raise ValueError("Vincenty formula failed to converge")
    
    # Calculate the square of the semi-minor axis / semi-major axis
    u2 = cosSqAlpha * (a ** 2 - b ** 2) / b ** 2
    
    # Final formulas
    A = 1 + u2 / 16384 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
    B = u2 / 1024 * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))
    
    deltaSigma = B * sinSigma * (
        cos2SigmaM + B / 4 * (
            cosSigma * (-1 + 2 * cos2SigmaM ** 2) -
            B / 6 * cos2SigmaM * (-3 + 4 * sinSigma ** 2) * (-3 + 4 * cos2SigmaM ** 2)
        )
    )
    
    # Calculate the distance
    distance = b * A * (sigma - deltaSigma)
    
    return distance


def bearing(point1: Coordinate, point2: Coordinate) -> float:
    """
    Calculate the initial bearing from point1 to point2.
    
    Args:
        point1: The starting coordinate
        point2: The ending coordinate
        
    Returns:
        Bearing in degrees (0-360, where 0 is north)
    """
    # Convert latitude and longitude from degrees to radians
    lat1 = math.radians(point1.latitude)
    lon1 = math.radians(point1.longitude)
    lat2 = math.radians(point2.latitude)
    lon2 = math.radians(point2.longitude)
    
    # Calculate the bearing
    dLon = lon2 - lon1
    y = math.sin(dLon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dLon)
    
    initial_bearing = math.atan2(y, x)
    
    # Convert to degrees and normalize
    initial_bearing = math.degrees(initial_bearing)
    bearing = (initial_bearing + 360) % 360
    
    return bearing


def destination_point(start: Coordinate, bearing: float, distance: float, 
                     radius: float = 6371000.0) -> Coordinate:
    """
    Calculate the destination point given a starting point, bearing, and distance.
    
    Args:
        start: The starting coordinate
        bearing: The bearing in degrees (0-360, where 0 is north)
        distance: The distance to travel in meters
        radius: Radius of the sphere in meters (default Earth's radius)
        
    Returns:
        The destination coordinate
    """
    # Convert latitude, longitude, and bearing from degrees to radians
    lat1 = math.radians(start.latitude)
    lon1 = math.radians(start.longitude)
    brng = math.radians(bearing)
    
    # Angular distance
    angular_distance = distance / radius
    
    # Calculate the destination point
    lat2 = math.asin(
        math.sin(lat1) * math.cos(angular_distance) +
        math.cos(lat1) * math.sin(angular_distance) * math.cos(brng)
    )
    
    lon2 = lon1 + math.atan2(
        math.sin(brng) * math.sin(angular_distance) * math.cos(lat1),
        math.cos(angular_distance) - math.sin(lat1) * math.sin(lat2)
    )
    
    # Convert back to degrees
    lat2 = math.degrees(lat2)
    lon2 = math.degrees(lon2)
    
    # Normalize longitude to range -180 to 180
    lon2 = ((lon2 + 180) % 360) - 180
    
    return Coordinate(
        latitude=lat2, 
        longitude=lon2,
        name=f"Destination from {start.name}" if start.name else "Destination point"
    )


def path_distance(points: List[Coordinate], method: str = "haversine") -> float:
    """
    Calculate the total distance along a path of points.
    
    Args:
        points: List of coordinates representing the path
        method: Distance calculation method ('haversine' or 'vincenty')
        
    Returns:
        Total distance in meters
    """
    if len(points) < 2:
        return 0.0
    
    total_distance = 0.0
    
    for i in range(len(points) - 1):
        if method == "haversine":
            segment_distance = haversine_distance(points[i], points[i + 1])
        elif method == "vincenty":
            segment_distance = vincenty_distance(points[i], points[i + 1])
        else:
            raise ValueError(f"Unknown distance calculation method: {method}")
            
        total_distance += segment_distance
    
    return total_distance


def midpoint(point1: Coordinate, point2: Coordinate) -> Coordinate:
    """
    Calculate the midpoint between two coordinates.
    
    Args:
        point1: The first coordinate
        point2: The second coordinate
        
    Returns:
        The midpoint coordinate
    """
    # Convert latitude and longitude from degrees to radians
    lat1 = math.radians(point1.latitude)
    lon1 = math.radians(point1.longitude)
    lat2 = math.radians(point2.latitude)
    lon2 = math.radians(point2.longitude)
    
    # Calculate the midpoint
    Bx = math.cos(lat2) * math.cos(lon2 - lon1)
    By = math.cos(lat2) * math.sin(lon2 - lon1)
    
    lat3 = math.atan2(
        math.sin(lat1) + math.sin(lat2),
        math.sqrt((math.cos(lat1) + Bx) ** 2 + By ** 2)
    )
    
    lon3 = lon1 + math.atan2(By, math.cos(lat1) + Bx)
    
    # Convert back to degrees
    lat3 = math.degrees(lat3)
    lon3 = math.degrees(lon3)
    
    # Normalize longitude to range -180 to 180
    lon3 = ((lon3 + 180) % 360) - 180
    
    return Coordinate(
        latitude=lat3, 
        longitude=lon3,
        name=f"Midpoint of {point1.name} and {point2.name}" if (point1.name and point2.name) else "Midpoint"
    ) 