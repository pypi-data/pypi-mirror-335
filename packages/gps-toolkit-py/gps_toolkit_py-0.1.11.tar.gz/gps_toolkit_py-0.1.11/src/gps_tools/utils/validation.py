"""
Centralized validation module for GPS coordinates.

This module provides unified validation functions for all coordinate types
used throughout the GPS Tools package.
"""
from typing import Any, Union, Optional, Tuple, Dict, Callable
import re
from functools import wraps

# Constants for validation
LATITUDE_MIN = -90.0
LATITUDE_MAX = 90.0
LONGITUDE_MIN = -180.0
LONGITUDE_MAX = 180.0
UTM_ZONE_MIN = 1
UTM_ZONE_MAX = 60
UTM_ZONE_LETTERS = "CDEFGHJKLMNPQRSTUVWX"  # Excludes I and O which can be confused with 1 and 0


def validate_input(input_type: str, value: Any) -> bool:
    """
    Validate a given input based on its type.
    
    Args:
        input_type: The type of input to validate ('latitude', 'longitude', etc.)
        value: The value to validate
        
    Returns:
        True if valid, False otherwise
    """
    if input_type == 'latitude':
        try:
            lat = float(value)
            return LATITUDE_MIN <= lat <= LATITUDE_MAX
        except (ValueError, TypeError):
            return False
    
    elif input_type == 'longitude':
        try:
            lon = float(value)
            return LONGITUDE_MIN <= lon <= LONGITUDE_MAX
        except (ValueError, TypeError):
            return False
    
    elif input_type == 'elevation':
        try:
            float(value)  # Just check if it's a valid number
            return True
        except (ValueError, TypeError):
            return False
    
    elif input_type == 'utm_zone_number':
        try:
            zone = int(value)
            return UTM_ZONE_MIN <= zone <= UTM_ZONE_MAX
        except (ValueError, TypeError):
            return False
            
    elif input_type == 'utm_zone_letter':
        return isinstance(value, str) and len(value) == 1 and value.upper() in UTM_ZONE_LETTERS
    
    else:
        raise ValueError(f"Unknown input type: {input_type}")


def validate_coordinates(lat: float, lon: float) -> bool:
    """
    Validate a coordinate pair.
    
    Args:
        lat: Latitude value
        lon: Longitude value
        
    Returns:
        True if both latitude and longitude are valid, False otherwise
    """
    return validate_input('latitude', lat) and validate_input('longitude', lon)


def validate_latitude(latitude: float, allow_none: bool = False) -> None:
    """
    Validate that a latitude value is within the valid range.
    
    Args:
        latitude: The latitude value to validate
        allow_none: If True, None values are allowed
        
    Raises:
        ValueError: If the latitude is not within -90 to 90 degrees
        TypeError: If the latitude is not a number or None when allow_none is True
    """
    if latitude is None:
        if allow_none:
            return
        raise ValueError("Latitude cannot be None")
        
    try:
        lat_float = float(latitude)
    except (ValueError, TypeError):
        raise TypeError(f"Latitude must be a number, got {type(latitude).__name__}")
        
    if lat_float < LATITUDE_MIN or lat_float > LATITUDE_MAX:
        raise ValueError(
            f"Latitude must be between {LATITUDE_MIN} and {LATITUDE_MAX} degrees, got {lat_float}"
        )


def validate_longitude(longitude: float, allow_none: bool = False) -> None:
    """
    Validate that a longitude value is within the valid range.
    
    Args:
        longitude: The longitude value to validate
        allow_none: If True, None values are allowed
        
    Raises:
        ValueError: If the longitude is not within -180 to 180 degrees
        TypeError: If the longitude is not a number or None when allow_none is True
    """
    if longitude is None:
        if allow_none:
            return
        raise ValueError("Longitude cannot be None")
        
    try:
        lon_float = float(longitude)
    except (ValueError, TypeError):
        raise TypeError(f"Longitude must be a number, got {type(longitude).__name__}")
        
    if lon_float < LONGITUDE_MIN or lon_float > LONGITUDE_MAX:
        raise ValueError(
            f"Longitude must be between {LONGITUDE_MIN} and {LONGITUDE_MAX} degrees, got {lon_float}"
        )


def validate_elevation(elevation: Optional[float]) -> None:
    """
    Validate an elevation value if provided.
    
    Args:
        elevation: The elevation value to validate, or None
        
    Raises:
        TypeError: If the elevation is not a number or None
    """
    if elevation is not None:
        try:
            float(elevation)
        except (ValueError, TypeError):
            raise TypeError(f"Elevation must be a number or None, got {type(elevation).__name__}")


def validate_utm_zone_number(zone_number: int) -> None:
    """
    Validate that a UTM zone number is within the valid range.
    
    Args:
        zone_number: The UTM zone number to validate (1-60)
        
    Raises:
        ValueError: If the zone number is not within 1 to 60
        TypeError: If the zone number is not an integer
    """
    if not isinstance(zone_number, int):
        try:
            zone_number = int(zone_number)
        except (ValueError, TypeError):
            raise TypeError(f"UTM zone number must be an integer, got {type(zone_number).__name__}")
    
    if zone_number < UTM_ZONE_MIN or zone_number > UTM_ZONE_MAX:
        raise ValueError(
            f"UTM zone number must be between {UTM_ZONE_MIN} and {UTM_ZONE_MAX}, got {zone_number}"
        )


def validate_utm_zone_letter(zone_letter: str) -> None:
    """
    Validate that a UTM zone letter is valid.
    
    Args:
        zone_letter: The UTM zone letter to validate (C-X, excluding I and O)
        
    Raises:
        ValueError: If the zone letter is not valid
        TypeError: If the zone letter is not a string
    """
    if not isinstance(zone_letter, str):
        raise TypeError(f"UTM zone letter must be a string, got {type(zone_letter).__name__}")
    
    zone_letter = zone_letter.upper()
    if len(zone_letter) != 1 or zone_letter not in UTM_ZONE_LETTERS:
        raise ValueError(
            f"UTM zone letter must be one of {', '.join(UTM_ZONE_LETTERS)}, got {zone_letter}"
        )


def validate_easting_northing(easting: float, northing: float) -> None:
    """
    Validate UTM easting and northing values.
    
    Args:
        easting: The UTM easting value (normally 100,000 to 900,000)
        northing: The UTM northing value (0 to 10,000,000)
        
    Raises:
        TypeError: If the values are not numbers
    """
    try:
        float(easting)
    except (ValueError, TypeError):
        raise TypeError(f"Easting must be a number, got {type(easting).__name__}")
        
    try:
        float(northing)
    except (ValueError, TypeError):
        raise TypeError(f"Northing must be a number, got {type(northing).__name__}")
    
    # Note: We don't check ranges strictly because they depend on the UTM zone


def validate_dms_string(dms_string: str) -> None:
    """
    Validate that a string is in a valid DMS (Degrees-Minutes-Seconds) format.
    
    Args:
        dms_string: The DMS string to validate
        
    Raises:
        ValueError: If the string is not in a valid DMS format
        TypeError: If the input is not a string
    """
    if not isinstance(dms_string, str):
        raise TypeError(f"DMS value must be a string, got {type(dms_string).__name__}")
    
    # Remove all whitespace for easier parsing
    dms_string = dms_string.strip()
    
    # Basic pattern for DMS: degrees, optional minutes, optional seconds, direction
    dms_pattern = r'^(-?\d+(?:\.\d+)?)[°⁰\s]*(?:(\d+(?:\.\d+)?)[\'′\s]*)?(?:(\d+(?:\.\d+)?)[\"″\s]*)?([NSEW])?$'
    
    match = re.match(dms_pattern, dms_string, re.IGNORECASE)
    if not match:
        raise ValueError(
            f"Invalid DMS format: {dms_string}. Expected format like '40°26'46\"N' or '40.446°N'"
        )
    
    degrees, minutes, seconds, direction = match.groups()
    
    # Convert matched components to float if they exist
    degrees = float(degrees)
    minutes = float(minutes) if minutes else 0.0
    seconds = float(seconds) if seconds else 0.0
    
    # Validate the components
    if minutes < 0 or minutes >= 60:
        raise ValueError(f"Minutes must be between 0 and 60, got {minutes}")
    
    if seconds < 0 or seconds >= 60:
        raise ValueError(f"Seconds must be between 0 and 60, got {seconds}")
    
    # Check if the overall coordinate is valid based on direction
    is_latitude = direction and direction.upper() in 'NS'
    coordinate_value = degrees + minutes/60 + seconds/3600
    
    if is_latitude:
        if coordinate_value < LATITUDE_MIN or coordinate_value > LATITUDE_MAX:
            raise ValueError(
                f"Latitude must be between {LATITUDE_MIN} and {LATITUDE_MAX} degrees, got {coordinate_value}"
            )
    else:  # Longitude
        if coordinate_value < LONGITUDE_MIN or coordinate_value > LONGITUDE_MAX:
            raise ValueError(
                f"Longitude must be between {LONGITUDE_MIN} and {LONGITUDE_MAX} degrees, got {coordinate_value}"
            )


def validate_mgrs_string(mgrs_string: str) -> None:
    """
    Validate that a string is in a valid MGRS (Military Grid Reference System) format.
    
    Args:
        mgrs_string: The MGRS string to validate
        
    Raises:
        ValueError: If the string is not in a valid MGRS format
        TypeError: If the input is not a string
    """
    if not isinstance(mgrs_string, str):
        raise TypeError(f"MGRS value must be a string, got {type(mgrs_string).__name__}")
    
    # Remove spaces and convert to uppercase
    mgrs_string = mgrs_string.replace(" ", "").upper()
    
    # MGRS pattern: zone number (1-60), zone letter (C-X except I and O), 
    # 100km grid square (two letters), easting (2, 4, 6, 8, or 10 digits), northing (same length as easting)
    mgrs_pattern = r'^(\d{1,2})([C-HJ-NP-X])([A-HJ-NP-Z][A-HJ-NP-V])(\d{2,10})$'
    
    match = re.match(mgrs_pattern, mgrs_string)
    if not match:
        raise ValueError(
            f"Invalid MGRS format: {mgrs_string}. Expected format like '18TXM8346013559'"
        )
    
    zone_number, zone_letter, grid_square, location = match.groups()
    
    # Validate zone number
    try:
        validate_utm_zone_number(int(zone_number))
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid UTM zone number in MGRS string: {e}")
    
    # Validate zone letter
    try:
        validate_utm_zone_letter(zone_letter)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid UTM zone letter in MGRS string: {e}")
    
    # Check that the location coordinate has an even number of digits
    if len(location) % 2 != 0:
        raise ValueError("MGRS easting and northing must have the same number of digits")
    
    # Valid lengths for the combined easting and northing are 4, 8, 12, 16, or 20 digits
    valid_lengths = [4, 8, 12, 16, 20]
    if len(location) not in valid_lengths:
        raise ValueError(
            f"MGRS easting and northing combined must have {', '.join(map(str, valid_lengths))} digits"
        )


def validate_coordinate_input(
    func: Callable[..., Any]
) -> Callable[..., Any]:
    """
    Decorator to validate coordinate inputs for functions.
    
    Args:
        func: The function to decorate
        
    Returns:
        The decorated function with input validation
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get function signature to know what parameters to validate
        # In a real implementation, this would use inspect.signature to get parameter names
        
        # For demonstration, we'll just check common parameter names
        for name, value in kwargs.items():
            if name in ['latitude', 'lat']:
                validate_latitude(value)
            elif name in ['longitude', 'lon', 'lng']:
                validate_longitude(value)
            elif name == 'elevation':
                validate_elevation(value)
            elif name == 'zone_number':
                validate_utm_zone_number(value)
            elif name == 'zone_letter':
                validate_utm_zone_letter(value)
            elif name == 'easting':
                # Validate with dummy northing value, will be checked properly when both are present
                pass
            elif name == 'northing':
                # If we have both easting and northing, validate them together
                if 'easting' in kwargs:
                    validate_easting_northing(kwargs['easting'], value)
        
        # Call the original function
        return func(*args, **kwargs)
    
    return wrapper 