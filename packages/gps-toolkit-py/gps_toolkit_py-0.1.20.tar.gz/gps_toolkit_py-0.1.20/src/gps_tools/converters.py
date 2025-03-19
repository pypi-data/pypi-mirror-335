"""
Coordinate conversion utilities for GPS data.

This module provides functions to convert between different coordinate systems,
including latitude/longitude to UTM and back, decimal degrees to DMS, etc.
"""

import math
import re
from typing import Tuple, Union, Optional

from .core import Coordinate, UTMCoordinate, MGRSCoordinate

# WGS84 ellipsoid constants
WGS84_SEMI_MAJOR_AXIS = 6378137.0  # meters
WGS84_SEMI_MINOR_AXIS = 6356752.314245  # meters
WGS84_FLATTENING = 1 / 298.257223563
WGS84_ECCENTRICITY = math.sqrt(2 * WGS84_FLATTENING - WGS84_FLATTENING**2)
WGS84_ECCENTRICITY_SQ = WGS84_ECCENTRICITY**2


def validate_latitude(latitude: float) -> bool:
    """
    Validate if a latitude value is within the valid range (-90 to 90 degrees).
    
    Args:
        latitude: The latitude value to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        lat_value = float(latitude)
        return -90 <= lat_value <= 90
    except (ValueError, TypeError):
        return False


def validate_longitude(longitude: float) -> bool:
    """
    Validate if a longitude value is within the valid range (-180 to 180 degrees).
    
    Args:
        longitude: The longitude value to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        lon_value = float(longitude)
        return -180 <= lon_value <= 180
    except (ValueError, TypeError):
        return False


def latlon_to_utm(latitude: float, longitude: float) -> Tuple[int, str, float, float]:
    """
    Convert latitude/longitude to UTM coordinates.
    
    Args:
        latitude: Latitude in decimal degrees (-90 to 90)
        longitude: Longitude in decimal degrees (-180 to 180)
    
    Returns:
        Tuple of (zone_number, zone_letter, easting, northing)
    
    Raises:
        ValueError: If latitude or longitude are outside valid ranges
        
    Examples:
        >>> latlon_to_utm(40.7128, -74.0060)  # New York City
        (18, 'T', 583591.9, 4507213.2)
    """
    # Validate input
    if not validate_latitude(latitude):
        raise ValueError(f"Latitude must be between -90 and 90, got {latitude}")
    if not validate_longitude(longitude):
        raise ValueError(f"Longitude must be between -180 and 180, got {longitude}")
    
    # WGS84 Parameters
    a = 6378137.0  # semi-major axis
    f = 1 / 298.257223563  # flattening
    
    # Compute UTM zone number
    if 56 <= latitude < 64 and 3 <= longitude < 12:
        zone_number = 32
    elif 72 <= latitude <= 84 and longitude >= 0:
        if longitude < 9:
            zone_number = 31
        elif longitude < 21:
            zone_number = 33
        elif longitude < 33:
            zone_number = 35
        elif longitude < 42:
            zone_number = 37
        else:
            zone_number = int((longitude + 180) / 6) + 1
    else:
        zone_number = int((longitude + 180) / 6) + 1
    
    # Compute central meridian of the zone
    central_meridian = (zone_number - 1) * 6 - 180 + 3
    
    # Compute zone letter - FIXED to match standard UTM/MGRS bands
    # Each latitude band is 8 degrees except X which is 12 degrees
    if latitude < -80:
        zone_letter = 'C'
    elif latitude < -72:
        zone_letter = 'D'
    elif latitude < -64:
        zone_letter = 'E'
    elif latitude < -56:
        zone_letter = 'F'
    elif latitude < -48:
        zone_letter = 'G'
    elif latitude < -40:
        zone_letter = 'H'
    elif latitude < -32:
        zone_letter = 'J'
    elif latitude < -24:
        zone_letter = 'K'
    elif latitude < -16:
        zone_letter = 'L'
    elif latitude < -8:
        zone_letter = 'M'
    elif latitude < 0:
        zone_letter = 'N'
    elif latitude < 8:
        zone_letter = 'P'
    elif latitude < 16:
        zone_letter = 'Q'
    elif latitude < 24:
        zone_letter = 'R'
    elif latitude < 32:
        zone_letter = 'S'
    elif latitude < 40:
        zone_letter = 'S'  # 32 to 40
    elif latitude < 48:
        zone_letter = 'T'  # 40 to 48
    elif latitude < 56:
        zone_letter = 'U'  # 48 to 56
    elif latitude < 64:
        zone_letter = 'V'  # 56 to 64
    elif latitude < 72:
        zone_letter = 'W'  # 64 to 72
    else:
        zone_letter = 'X'  # 72 to 84
    
    # Convert to radians
    lat_rad = math.radians(latitude)
    lon_rad = math.radians(longitude)
    central_meridian_rad = math.radians(central_meridian)
    
    # Compute UTM parameters
    e_squared = 2 * f - f * f
    e_fourth = e_squared * e_squared
    e_sixth = e_fourth * e_squared
    
    # Intermediate calculations
    n = a / math.sqrt(1 - e_squared * math.sin(lat_rad) * math.sin(lat_rad))
    t = math.tan(lat_rad) * math.tan(lat_rad)
    c = e_squared / (1 - e_squared) * math.cos(lat_rad) * math.cos(lat_rad)
    a_prime = (lon_rad - central_meridian_rad) * math.cos(lat_rad)
    
    # Terms used in the calculation
    term1 = (1 - e_squared / 4 - 3 * e_fourth / 64 - 5 * e_sixth / 256) * lat_rad
    term2 = (3 * e_squared / 8 + 3 * e_fourth / 32 + 45 * e_sixth / 1024) * math.sin(2 * lat_rad)
    term3 = (15 * e_fourth / 256 + 45 * e_sixth / 1024) * math.sin(4 * lat_rad)
    term4 = (35 * e_sixth / 3072) * math.sin(6 * lat_rad)
    
    m = a * (term1 - term2 + term3 - term4)
    
    # Calculate UTM coordinates
    k0 = 0.9996  # scale factor
    
    # Easting
    easting = k0 * n * (a_prime + (1 - t + c) * a_prime**3 / 6 +
                        (5 - 18 * t + t * t + 72 * c - 58 * (e_squared / (1 - e_squared))) *
                        a_prime**5 / 120) + 500000.0
    
    # Northing
    northing = k0 * (m + n * math.tan(lat_rad) * (a_prime * a_prime / 2 +
                                              (5 - t + 9 * c + 4 * c * c) * a_prime**4 / 24 +
                                              (61 - 58 * t + t * t + 600 * c - 330 * (e_squared / (1 - e_squared))) *
                                              a_prime**6 / 720))
    
    # Adjust northing based on hemisphere
    if latitude < 0:
        northing += 10000000.0  # Southern hemisphere
    
    return (zone_number, zone_letter, easting, northing)


def utm_to_latlon(zone_number: int, zone_letter: str, easting: float, northing: float) -> Tuple[float, float]:
    """
    Convert UTM coordinates to latitude/longitude.
    
    Args:
        zone_number: UTM zone number (1-60)
        zone_letter: UTM zone letter (C-X, excluding I and O)
        easting: Easting coordinate in meters
        northing: Northing coordinate in meters
    
    Returns:
        A tuple of (latitude, longitude) in decimal degrees
        
    Raises:
        ValueError: If zone_number, zone_letter, easting, or northing are invalid
        
    Examples:
        >>> utm_to_latlon(18, 'T', 583326.92, 4507426.19)  # NYC
        (40.7128, -74.0060)
    """
    if not 1 <= zone_number <= 60:
        raise ValueError(f"Zone number must be between 1 and 60, got {zone_number}")
    
    if zone_letter not in "CDEFGHJKLMNPQRSTUVWX":
        raise ValueError(f"Zone letter must be one of C-X (excluding I and O), got {zone_letter}")
    
    # Check if easting is within range
    if not 100000 <= easting <= 900000:
        raise ValueError(f"Easting should be between 100,000 and 900,000 meters, got {easting}")
    
    # WGS84 Parameters
    a = 6378137.0  # semi-major axis
    f = 1 / 298.257223563  # flattening
    
    # Derived parameters
    e_squared = 2 * f - f * f
    e2_squared = e_squared / (1 - e_squared)
    
    # Adjust for southern hemisphere
    is_northern = zone_letter >= 'N'
    if not is_northern:
        northing -= 10000000.0
    
    # Calculate central meridian in degrees (center of the UTM zone)
    central_meridian = (zone_number - 1) * 6 - 180 + 3
    
    # Scale factor
    k0 = 0.9996
    
    # Intermediate calculations
    x = easting - 500000.0  # Remove false easting
    y = northing
    
    # Footpoint latitude
    e1 = (1 - math.sqrt(1 - e_squared)) / (1 + math.sqrt(1 - e_squared))
    m = y / k0
    
    mu = m / (a * (1 - e_squared / 4 - 3 * e_squared**2 / 64 - 5 * e_squared**3 / 256))
    
    p1 = (3 * e1 / 2 - 27 * e1**3 / 32) * math.sin(2 * mu)
    p2 = (21 * e1**2 / 16 - 55 * e1**4 / 32) * math.sin(4 * mu)
    p3 = (151 * e1**3 / 96) * math.sin(6 * mu)
    
    footpoint_latitude = mu + p1 + p2 + p3
    
    # Calculate latitude and longitude
    cf = math.cos(footpoint_latitude)
    sf = math.sin(footpoint_latitude)
    tf = math.tan(footpoint_latitude)
    
    n = a / math.sqrt(1 - e_squared * sf * sf)
    c = e2_squared * cf * cf
    r = n * (1 - e_squared) / (1 - e_squared * sf * sf)
    d = x / (n * k0)
    
    q1 = n * tf / r
    q2 = d * d / 2
    q3 = (5 + 3 * tf * tf + 10 * c - 4 * c * c - 9 * e2_squared) * d**4 / 24
    q4 = (61 + 90 * tf * tf + 298 * c + 45 * tf**4 - 252 * e2_squared - 3 * c * c) * d**6 / 720
    
    latitude = footpoint_latitude - q1 * (q2 - q3 + q4)
    
    q5 = d
    q6 = (1 + 2 * tf * tf + c) * d**3 / 6
    q7 = (5 - 2 * c + 28 * tf * tf - 3 * c * c + 8 * e2_squared + 24 * tf**4) * d**5 / 120
    
    # Calculate longitude offset in radians, then convert to degrees
    longitude_offset_rad = (q5 - q6 + q7) / cf
    longitude_offset_deg = math.degrees(longitude_offset_rad)
    
    # Final longitude is the central meridian plus the offset
    longitude_deg = central_meridian + longitude_offset_deg
    
    # Convert latitude to degrees
    latitude_deg = math.degrees(latitude)
    
    return (latitude_deg, longitude_deg)


def decimal_to_dms(decimal_degrees: float, is_latitude: bool = True) -> str:
    """
    Convert decimal degrees to degrees-minutes-seconds (DMS) format.
    
    Args:
        decimal_degrees: The value in decimal degrees
        is_latitude: True if this is a latitude value, False for longitude
    
    Returns:
        DMS representation as a string
        
    Examples:
        >>> decimal_to_dms(40.7128, is_latitude=True)
        "40°42'46.08"N"
        >>> decimal_to_dms(-74.0060, is_latitude=False)
        "74°0'21.6"W"
    """
    # Determine the direction
    if is_latitude:
        direction = "N" if decimal_degrees >= 0 else "S"
    else:
        direction = "E" if decimal_degrees >= 0 else "W"
    
    # Get the absolute value
    decimal_degrees = abs(decimal_degrees)
    
    # Extract degrees, minutes, and seconds
    degrees = int(decimal_degrees)
    minutes_decimal = (decimal_degrees - degrees) * 60
    minutes = int(minutes_decimal)
    seconds = (minutes_decimal - minutes) * 60
    
    # Format the result
    return f"{degrees}°{minutes}'{seconds:.2f}\"{direction}"


def dms_to_decimal(dms_str: str) -> float:
    """
    Convert a degrees-minutes-seconds (DMS) string to decimal degrees.
    
    Args:
        dms_str: The DMS string to convert
    
    Returns:
        Value in decimal degrees
        
    Raises:
        ValueError: If the DMS string is invalid
        
    Examples:
        >>> dms_to_decimal("40°42'46.08"N")
        40.7128
        >>> dms_to_decimal("74°0'21.6"W")
        -74.0060
    """
    # Remove spaces
    dms_str = dms_str.replace(" ", "")
    
    # Check if the string is valid
    if not re.search(r'[NSEWnsew]$', dms_str):
        raise ValueError(f"Invalid DMS string: {dms_str}. Must end with N, S, E, or W.")
    
    # Get the direction
    direction = dms_str[-1].upper()
    dms_str = dms_str[:-1]
    
    # Initialize values
    degrees = minutes = seconds = 0
    
    # Extract degrees, minutes, and seconds
    if "°" in dms_str:
        parts = dms_str.split("°")
        degrees = float(parts[0])
        dms_str = parts[1]
    
    if "'" in dms_str:
        parts = dms_str.split("'")
        minutes = float(parts[0])
        dms_str = parts[1]
    
    if '"' in dms_str:
        seconds = float(dms_str.strip('"'))
    
    # Calculate decimal degrees
    decimal_degrees = degrees + minutes / 60 + seconds / 3600
    
    # Apply direction
    if direction in "SW":
        decimal_degrees = -decimal_degrees
    
    return decimal_degrees


def latlon_to_mgrs(latitude: float, longitude: float, precision: int = 5) -> str:
    """
    Convert latitude/longitude to MGRS (Military Grid Reference System) coordinates.
    
    Args:
        latitude: Latitude in decimal degrees (-90 to 90)
        longitude: Longitude in decimal degrees (-180 to 180)
        precision: Precision level (1-5, where 5 is 1m precision)
    
    Returns:
        MGRS coordinate string
        
    Raises:
        ValueError: If latitude or longitude are outside the valid range
        
    Examples:
        >>> latlon_to_mgrs(40.7128, -74.0060)  # NYC
        "18TWL8345505695"
    """
    if not validate_latitude(latitude):
        raise ValueError(f"Latitude must be between -90 and 90, got {latitude}")
    
    if not validate_longitude(longitude):
        raise ValueError(f"Longitude must be between -180 and 180, got {longitude}")
    
    if not 1 <= precision <= 5:
        raise ValueError(f"Precision must be between 1 and 5, got {precision}")
    
    # First, convert to UTM
    zone_number, zone_letter, easting, northing = latlon_to_utm(latitude, longitude)
    
    # Then convert to MGRS
    return _utm_to_mgrs(zone_number, zone_letter, easting, northing, precision)


def _utm_to_mgrs(zone_number: int, zone_letter: str, easting: float, northing: float, precision: int = 5) -> str:
    """
    Convert UTM coordinates to MGRS.
    
    Args:
        zone_number: UTM zone number (1-60)
        zone_letter: UTM zone letter (C-X, excluding I and O)
        easting: Easting coordinate in meters
        northing: Northing coordinate in meters
        precision: Precision level (1-5, where 5 is 1m precision)
        
    Returns:
        MGRS coordinate string
    """
    # 100km grid square row letters
    row_letters = "ABCDEFGHJKLMNPQRSTUV"
    
    # 100km grid square column letters
    col_letters = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    
    # Calculate the column letter
    col_index = int(easting / 100000) % len(col_letters)
    
    # Calculate the row letter (depends on UTM zone number)
    row_index = int(northing / 100000) % len(row_letters)
    if zone_number % 2 == 0:  # Even zone number
        row_index = (row_index + len(row_letters) // 2) % len(row_letters)
    
    # Get the grid square letters
    grid_square = col_letters[col_index] + row_letters[row_index]
    
    # Calculate the easting and northing within the 100km grid square
    easting_remainder = int(easting % 100000)
    northing_remainder = int(northing % 100000)
    
    # Format based on precision
    if precision == 1:
        # 10km precision
        easting_str = f"{easting_remainder // 10000}"
        northing_str = f"{northing_remainder // 10000}"
    elif precision == 2:
        # 1km precision
        easting_str = f"{easting_remainder // 1000:02d}"
        northing_str = f"{northing_remainder // 1000:02d}"
    elif precision == 3:
        # 100m precision
        easting_str = f"{easting_remainder // 100:03d}"
        northing_str = f"{northing_remainder // 100:03d}"
    elif precision == 4:
        # 10m precision
        easting_str = f"{easting_remainder // 10:04d}"
        northing_str = f"{northing_remainder // 10:04d}"
    else:  # precision == 5
        # 1m precision
        easting_str = f"{easting_remainder:05d}"
        northing_str = f"{northing_remainder:05d}"
    
    # Construct the MGRS reference
    return f"{zone_number}{zone_letter}{grid_square}{easting_str}{northing_str}"


def mgrs_to_utm(mgrs_str: str) -> Tuple[int, str, float, float]:
    """
    Convert an MGRS (Military Grid Reference System) string to UTM coordinates.
    
    Args:
        mgrs_str: The MGRS string to convert
    
    Returns:
        A tuple of (zone_number, zone_letter, easting, northing)
    
    Raises:
        ValueError: If the MGRS string is invalid
        
    Examples:
        >>> mgrs_to_utm("18TWL8345505695")
        (18, 'T', 583455.0, 4505695.0)
    """
    # Clean up the MGRS string
    mgrs_str = mgrs_str.replace(" ", "").upper()
    
    # Parse zone number
    i = 0
    while i < len(mgrs_str) and mgrs_str[i].isdigit():
        i += 1
    
    if i == 0:
        raise ValueError(f"Invalid MGRS reference: {mgrs_str}. Must start with zone number.")
    
    zone_number = int(mgrs_str[:i])
    
    if not 1 <= zone_number <= 60:
        raise ValueError(f"Invalid zone number in MGRS reference: {zone_number}")
    
    # Parse zone letter (latitude band)
    if i >= len(mgrs_str) or mgrs_str[i] not in "CDEFGHJKLMNPQRSTUVWX":
        raise ValueError(f"Invalid zone letter in MGRS reference: {mgrs_str[i:i+1]}")
    
    zone_letter = mgrs_str[i]
    i += 1
    
    # Parse 100km grid square letters
    if i+1 >= len(mgrs_str):
        raise ValueError(f"Invalid MGRS reference: {mgrs_str}. Missing 100km grid square.")
    
    grid_square = mgrs_str[i:i+2]
    
    # Convert 100km grid square letters to easting and northing origins
    col_letter = grid_square[0]
    row_letter = grid_square[1]
    
    # 100km grid square column letters
    col_letters = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    
    # 100km grid square row letters
    row_letters = "ABCDEFGHJKLMNPQRSTUV"
    
    # Check if the letters are valid
    if col_letter not in col_letters:
        raise ValueError(f"Invalid column letter in MGRS reference: {col_letter}")
    
    if row_letter not in row_letters:
        raise ValueError(f"Invalid row letter in MGRS reference: {row_letter}")
    
    # Calculate the column index
    col_index = col_letters.index(col_letter)
    
    # Calculate the row index (depends on UTM zone number)
    row_index = row_letters.index(row_letter)
    if zone_number % 2 == 0:  # Even zone number
        row_index = (row_index - len(row_letters) // 2) % len(row_letters)
    
    # Calculate the easting and northing origins
    easting_origin = col_index * 100000
    northing_origin = row_index * 100000
    
    # Parse the numeric portion
    i += 2
    numeric_part = mgrs_str[i:]
    
    # The length of the numeric part determines the precision
    precision = len(numeric_part) // 2
    
    if len(numeric_part) % 2 != 0:
        raise ValueError(f"Invalid MGRS reference: {mgrs_str}. Numeric part must have even length.")
    
    easting_str = numeric_part[:precision]
    northing_str = numeric_part[precision:]
    
    # Add trailing zeros to fill to 5-digit precision
    easting_str = easting_str.ljust(5, '0')
    northing_str = northing_str.ljust(5, '0')
    
    # Parse the easting and northing
    try:
        easting_offset = int(easting_str)
        northing_offset = int(northing_str)
    except ValueError:
        raise ValueError(f"Invalid numeric part in MGRS reference: {numeric_part}")
    
    # Calculate the final easting and northing
    easting = easting_origin + easting_offset
    northing = northing_origin + northing_offset
    
    # Add the false northing
    # For latitudes 0-8, the false northing is 0
    # For other northern hemisphere latitudes, it's the bottom edge of the latitude band
    # For southern hemisphere, we add 10,000,000 to keep northing values positive
    
    # For zone 'S' (32-40° latitude), add 3,500,000
    # For zone 'T' (40-48° latitude), add 4,000,000
    # For zone 'U' (48-56° latitude), add 4,800,000
    # For zone 'V' (56-64° latitude), add 5,500,000
    # For zone 'W' (64-72° latitude), add 6,500,000
    # For zone 'X' (72-84° latitude), add 7,300,000
    
    # False northing values for each zone letter
    false_northings = {
        'N': 0.0,         # 0° to 8°
        'P': 0.0,         # 8° to 16°
        'Q': 1000000.0,   # 16° to 24°
        'R': 2000000.0,   # 24° to 32°
        'S': 3000000.0,   # 32° to 40°
        'T': 4000000.0,   # 40° to 48°
        'U': 5000000.0,   # 48° to 56°
        'V': 6000000.0,   # 56° to 64°
        'W': 7000000.0,   # 64° to 72°
        'X': 7000000.0,   # 72° to 84°
    }
    
    # Apply false northing for northern hemisphere
    if zone_letter in false_northings:
        northing += false_northings[zone_letter]
    
    # For southern hemisphere, add 10,000,000m offset
    if zone_letter <= 'M':  # Southern hemisphere
        northing += 10000000.0
    
    return (zone_number, zone_letter, float(easting), float(northing))


def mgrs_to_latlon(mgrs_str: str) -> Tuple[float, float]:
    """
    Convert an MGRS (Military Grid Reference System) string to latitude/longitude.
    
    Args:
        mgrs_str: The MGRS string to convert
    
    Returns:
        A tuple of (latitude, longitude) in decimal degrees
        
    Raises:
        ValueError: If the MGRS string is invalid
        
    Examples:
        >>> mgrs_to_latlon("18TWL8345505695")
        (40.7128, -74.0060)
    """
    # First convert to UTM
    zone_number, zone_letter, easting, northing = mgrs_to_utm(mgrs_str)
    
    # Then convert to latitude/longitude
    return utm_to_latlon(zone_number, zone_letter, easting, northing)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth using the Haversine formula.
    
    Args:
        lat1: Latitude of the first point in decimal degrees
        lon1: Longitude of the first point in decimal degrees
        lat2: Latitude of the second point in decimal degrees
        lon2: Longitude of the second point in decimal degrees
        
    Returns:
        Distance between the points in meters
    """
    # Earth's radius in meters
    earth_radius = 6371000
    
    # Convert coordinates to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Differences
    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return earth_radius * c 