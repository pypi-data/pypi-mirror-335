"""
Unified coordinate conversion module.

This module provides a single function to convert any coordinate format
to latitude/longitude format.
"""

import re
from typing import Tuple, Optional, Union, Dict, Any

from .core import Coordinate, UTMCoordinate, MGRSCoordinate
from .converters import utm_to_latlon, dms_to_decimal, mgrs_to_utm


def convert_to_latlon(coordinate_input: Union[str, Coordinate, UTMCoordinate, MGRSCoordinate, 
                                            Tuple[float, float], Dict[str, Any]]) -> Tuple[float, float, Optional[float]]:
    """
    Convert any coordinate format to latitude/longitude format.
    
    Args:
        coordinate_input: The input coordinate in any supported format:
            - String: Can be DMS format ("40°26'46\"N, 74°0'21\"W") or MGRS format ("18TXM8346013559")
            - Coordinate object
            - UTMCoordinate object
            - MGRSCoordinate object
            - Tuple of (latitude, longitude)
            - Dictionary with 'lat'/'latitude' and 'lon'/'longitude' keys
    
    Returns:
        Tuple of (latitude, longitude, elevation) where elevation is None if not provided
    
    Raises:
        ValueError: If the input format can't be recognized or converted
        
    Examples:
        >>> convert_to_latlon("40°26'46\"N, 74°0'21\"W")
        (40.7128, -74.0060, None)
        >>> convert_to_latlon(Coordinate(40.7128, -74.0060, elevation=10.0))
        (40.7128, -74.0060, 10.0)
        >>> convert_to_latlon({"latitude": 40.7128, "longitude": -74.0060})
        (40.7128, -74.0060, None)
    """
    elevation = None
    
    # Process based on input type
    if isinstance(coordinate_input, str):
        # Check if it's a DMS string
        if any(direction in coordinate_input.upper() for direction in ['N', 'S', 'E', 'W']):
            # DMS format
            # Split into lat and lon components if there's a comma
            if ',' in coordinate_input:
                lat_str, lon_str = coordinate_input.split(',', 1)
                lat = dms_to_decimal(lat_str.strip())
                lon = dms_to_decimal(lon_str.strip())
            else:
                # Try to determine if it's lat or lon based on direction
                direction = coordinate_input[-1].upper()
                if direction in ['N', 'S']:
                    lat = dms_to_decimal(coordinate_input)
                    lon = 0.0  # Default longitude
                else:
                    lat = 0.0  # Default latitude
                    lon = dms_to_decimal(coordinate_input)
            
            return lat, lon, elevation
            
        # Check if it's an MGRS string
        elif re.match(r'^\d{1,2}[A-Z][A-Z][A-Z]\d+$', coordinate_input.upper().replace(' ', '')):
            # MGRS format
            try:
                zone_number, zone_letter, easting, northing = mgrs_to_utm(coordinate_input)
                lat, lon = utm_to_latlon(zone_number, zone_letter, easting, northing)
                return lat, lon, elevation
            except ValueError as e:
                raise ValueError(f"Invalid MGRS coordinate: {str(e)}")
        
        else:
            raise ValueError(f"Unrecognized coordinate string format: {coordinate_input}")
    
    elif isinstance(coordinate_input, Coordinate):
        # Coordinate object
        return coordinate_input.latitude, coordinate_input.longitude, coordinate_input.elevation
    
    elif isinstance(coordinate_input, UTMCoordinate):
        # UTMCoordinate object
        lat, lon = utm_to_latlon(coordinate_input.zone_number, coordinate_input.zone_letter, 
                                 coordinate_input.easting, coordinate_input.northing)
        return lat, lon, coordinate_input.elevation
    
    elif isinstance(coordinate_input, MGRSCoordinate):
        # MGRSCoordinate object
        try:
            # Convert MGRS to UTM first
            zone_number, zone_letter, easting, northing = mgrs_to_utm(
                f"{coordinate_input.zone_number}{coordinate_input.zone_letter}"
                f"{coordinate_input.grid_square}{coordinate_input.easting}{coordinate_input.northing}"
            )
            # Then UTM to lat/lon
            lat, lon = utm_to_latlon(zone_number, zone_letter, easting, northing)
            return lat, lon, coordinate_input.elevation
        except ValueError as e:
            raise ValueError(f"Invalid MGRS coordinate: {str(e)}")
    
    elif isinstance(coordinate_input, tuple) and len(coordinate_input) >= 2:
        # Tuple of (latitude, longitude, [elevation])
        lat, lon = coordinate_input[0], coordinate_input[1]
        if len(coordinate_input) > 2:
            elevation = coordinate_input[2]
        return lat, lon, elevation
    
    elif isinstance(coordinate_input, dict):
        # Dictionary with lat/lon keys
        lat_key = next((k for k in ('lat', 'latitude') if k in coordinate_input), None)
        lon_key = next((k for k in ('lon', 'lng', 'longitude') if k in coordinate_input), None)
        elev_key = next((k for k in ('elev', 'elevation', 'alt', 'altitude') if k in coordinate_input), None)
        
        if lat_key is None or lon_key is None:
            raise ValueError(f"Dict must contain latitude and longitude keys: {coordinate_input}")
            
        lat = coordinate_input[lat_key]
        lon = coordinate_input[lon_key]
        if elev_key:
            elevation = coordinate_input[elev_key]
            
        return lat, lon, elevation
    
    else:
        raise ValueError(f"Unsupported coordinate input format: {type(coordinate_input)}") 