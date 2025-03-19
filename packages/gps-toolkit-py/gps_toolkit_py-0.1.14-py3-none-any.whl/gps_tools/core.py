"""
Core coordinate classes for the GPS Tools package.

This module provides the core coordinate classes and functionality.
"""

import math
from dataclasses import dataclass
from typing import Optional, Union, List, Tuple, Dict, Any


class Coordinate:
    """
    A class representing a geographic coordinate with latitude and longitude.
    
    Attributes:
        latitude: Latitude in decimal degrees (-90 to 90)
        longitude: Longitude in decimal degrees (-180 to 180)
        name: Optional name for this coordinate
        elevation: Optional elevation in meters above sea level
    
    Examples:
        >>> nyc = Coordinate(40.7128, -74.0060, name="New York City")
        >>> sf = Coordinate(37.7749, -122.4194, name="San Francisco")
    """
    
    def __init__(self, latitude: Union[float, str], longitude: Union[float, str], 
                 name: Optional[str] = None, elevation: Optional[float] = None):
        """
        Initialize a Coordinate instance.
        
        Args:
            latitude: Latitude in decimal degrees (-90 to 90)
            longitude: Longitude in decimal degrees (-180 to 180)
            name: Optional name for this coordinate
            elevation: Optional elevation in meters above sea level
            
        Raises:
            ValueError: If latitude or longitude are outside valid ranges
        """
        # Convert inputs to float
        try:
            latitude = float(latitude)
        except (TypeError, ValueError):
            raise ValueError(f"Latitude must be a number, got {latitude}")
            
        try:
            longitude = float(longitude)
        except (TypeError, ValueError):
            raise ValueError(f"Longitude must be a number, got {longitude}")
            
        if elevation is not None:
            try:
                elevation = float(elevation)
            except (TypeError, ValueError):
                raise ValueError(f"Elevation must be a number or None, got {elevation}")
        
        # Validate inputs
        if not (-90 <= latitude <= 90):
            raise ValueError(f"Latitude must be between -90 and 90, got {latitude}")
        
        if not (-180 <= longitude <= 180):
            raise ValueError(f"Longitude must be between -180 and 180, got {longitude}")
        
        # Store as private attributes
        self._latitude = latitude
        self._longitude = longitude
        self._name = name
        self._elevation = elevation
    
    @property
    def latitude(self) -> float:
        """Get the latitude value."""
        return self._latitude
    
    @property
    def longitude(self) -> float:
        """Get the longitude value."""
        return self._longitude
    
    @property
    def name(self) -> Optional[str]:
        """Get the name value."""
        return self._name
    
    @property
    def elevation(self) -> Optional[float]:
        """Get the elevation value."""
        return self._elevation
    
    def __eq__(self, other):
        """Test equality of coordinates (compares lat/lon only)."""
        if not isinstance(other, Coordinate):
            return False
        return (self.latitude == other.latitude and 
                self.longitude == other.longitude)
    
    def __hash__(self):
        """Return a hash of the coordinate."""
        return hash((self.latitude, self.longitude))
    
    def __str__(self):
        """Return a string representation of the coordinate."""
        lat_dir = "N" if self.latitude >= 0 else "S"
        lon_dir = "E" if self.longitude >= 0 else "W"
        
        lat_str = f"{abs(self.latitude):.4f}°{lat_dir}"
        lon_str = f"{abs(self.longitude):.4f}°{lon_dir}"
        
        result = f"{lat_str}, {lon_str}"
        
        if self.name:
            result = f"{self.name}: {result}"
            
        if self.elevation is not None:
            result += f", {self.elevation}m"
            
        return result
    
    def __repr__(self):
        """Return a string that could be used to recreate this object."""
        return f"Coordinate(latitude={self.latitude}, longitude={self.longitude}, elevation={self.elevation}, name={repr(self.name) if self.name is not None else None})"
    
    def to_tuple(self) -> Tuple:
        """
        Convert the coordinate to a tuple.
        
        Returns:
            If elevation is None: (latitude, longitude)
            If elevation is not None: (latitude, longitude, elevation)
        """
        if self.elevation is None:
            return (self.latitude, self.longitude)
        else:
            return (self.latitude, self.longitude, self.elevation)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the coordinate to a dictionary.
        
        Returns:
            Dictionary with keys: latitude, longitude, elevation, name
        """
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "elevation": self.elevation,
            "name": self.name
        }


@dataclass
class UTMCoordinate:
    """
    A geographic coordinate in Universal Transverse Mercator (UTM) format.
    
    Attributes:
        easting: Easting in meters
        northing: Northing in meters
        zone_number: UTM zone number (1-60)
        zone_letter: UTM zone letter (C-X, excluding I and O)
        altitude: Optional altitude in meters above sea level
    """
    easting: float
    northing: float
    zone_number: int
    zone_letter: str
    altitude: Optional[float] = None
    
    def __post_init__(self):
        """Validate coordinate values after initialization"""
        if not 1 <= self.zone_number <= 60:
            raise ValueError(f"Zone number must be between 1 and 60, got {self.zone_number}")
        
        if self.zone_letter not in "CDEFGHJKLMNPQRSTUVWX":
            raise ValueError(f"Zone letter must be one of CDEFGHJKLMNPQRSTUVWX, got {self.zone_letter}")
        
    def __str__(self) -> str:
        """String representation of the coordinate"""
        if self.altitude is not None:
            return f"UTM {self.zone_number}{self.zone_letter} {self.easting:.1f}E {self.northing:.1f}N {self.altitude:.1f}m"
        return f"UTM {self.zone_number}{self.zone_letter} {self.easting:.1f}E {self.northing:.1f}N"


@dataclass
class MGRSCoordinate:
    """
    A geographic coordinate in Military Grid Reference System (MGRS) format.
    
    Attributes:
        zone_number: MGRS grid zone number (1-60)
        zone_letter: MGRS grid zone letter (C-X, excluding I and O)
        grid_square: 100,000-meter grid square identifier (two letters)
        easting: Easting within the grid square (up to 5 digits)
        northing: Northing within the grid square (up to 5 digits)
        precision: Precision level (0-5 digits)
        altitude: Optional altitude in meters above sea level
    """
    zone_number: int
    zone_letter: str
    grid_square: str
    easting: int
    northing: int
    precision: int
    altitude: Optional[float] = None
    
    def __post_init__(self):
        """Validate coordinate values after initialization"""
        if not 1 <= self.zone_number <= 60:
            raise ValueError(f"Zone number must be between 1 and 60, got {self.zone_number}")
        
        if self.zone_letter not in "CDEFGHJKLMNPQRSTUVWX":
            raise ValueError(f"Zone letter must be one of CDEFGHJKLMNPQRSTUVWX, got {self.zone_letter}")
        
        if len(self.grid_square) != 2:
            raise ValueError(f"Grid square must be 2 letters, got {self.grid_square}")
        
        if not 0 <= self.precision <= 5:
            raise ValueError(f"Precision must be between 0 and 5, got {self.precision}")
        
        max_value = 10 ** self.precision
        if not 0 <= self.easting < max_value:
            raise ValueError(f"Easting must be between 0 and {max_value-1}, got {self.easting}")
            
        if not 0 <= self.northing < max_value:
            raise ValueError(f"Northing must be between 0 and {max_value-1}, got {self.northing}")
    
    def __str__(self) -> str:
        """String representation of the coordinate"""
        format_str = f"{{:0{self.precision}d}}"
        easting_str = format_str.format(self.easting)
        northing_str = format_str.format(self.northing)
        
        if self.altitude is not None:
            return f"{self.zone_number}{self.zone_letter} {self.grid_square} {easting_str} {northing_str} {self.altitude:.1f}m"
        return f"{self.zone_number}{self.zone_letter} {self.grid_square} {easting_str} {northing_str}"


class CoordinateList:
    """
    A class representing a list of coordinates.
    
    This class provides functionality for working with collections of 
    coordinates, such as calculating path distances, bounding boxes, etc.
    
    Attributes:
        coordinates: List of Coordinate objects
        name: Optional name for this collection
    """
    
    def __init__(self, coordinates: List[Coordinate], name: Optional[str] = None):
        """
        Initialize a CoordinateList instance.
        
        Args:
            coordinates: List of Coordinate objects
            name: Optional name for this collection
        """
        self.coordinates = coordinates.copy()
        self.name = name
    
    def __len__(self):
        """Return the number of coordinates in the list."""
        return len(self.coordinates)
    
    def __getitem__(self, index):
        """Access coordinates by index."""
        return self.coordinates[index]
    
    def __iter__(self):
        """Iterate over coordinates."""
        return iter(self.coordinates)
    
    def __str__(self):
        """Return a string representation of the coordinate list."""
        if self.name:
            header = f"{self.name} ({len(self.coordinates)} points):"
        else:
            header = f"CoordinateList ({len(self.coordinates)} points):"
            
        if not self.coordinates:
            return f"{header} Empty"
        
        # Show up to 3 coordinates for brevity
        coord_strs = [str(coord) for coord in self.coordinates[:3]]
        
        if len(self.coordinates) > 3:
            coord_strs.append(f"... and {len(self.coordinates) - 3} more")
            
        return f"{header}\n" + "\n".join(f"- {cs}" for cs in coord_strs)
    
    def add(self, coordinate: Coordinate):
        """
        Add a coordinate to the list.
        
        Args:
            coordinate: The Coordinate object to add
        """
        self.coordinates.append(coordinate)
    
    def get_bounding_box(self) -> Tuple[float, float, float, float]:
        """
        Calculate the bounding box of the coordinates.
        
        Returns:
            Tuple of (min_lat, min_lon, max_lat, max_lon)
            
        Raises:
            ValueError: If the list is empty
        """
        if not self.coordinates:
            raise ValueError("Cannot calculate bounding box of empty list")
            
        lats = [coord.latitude for coord in self.coordinates]
        lons = [coord.longitude for coord in self.coordinates]
        
        return (min(lats), min(lons), max(lats), max(lons))
    
    def get_center(self) -> Coordinate:
        """
        Calculate the geometric center (average) of the coordinates.
        
        Returns:
            A Coordinate object at the center
            
        Raises:
            ValueError: If the list is empty
        """
        if not self.coordinates:
            raise ValueError("Cannot calculate center of empty list")
            
        lats = [coord.latitude for coord in self.coordinates]
        lons = [coord.longitude for coord in self.coordinates]
        
        return Coordinate(
            sum(lats) / len(lats),
            sum(lons) / len(lons),
            name=f"Center of {self.name}" if self.name else "Center"
        )


def parse_coordinate(coord_str: str) -> Coordinate:
    """
    Parse a coordinate string in various formats and return a Coordinate object.
    
    Accepted formats:
    - Decimal degrees: "40.7128, -74.0060"
    - Degrees minutes seconds: "40°26'46\"N, 74°0'21\"W"
    - Decimal degrees with direction: "40.7128 N, 74.0060 W"
    
    Args:
        coord_str: The coordinate string to parse
        
    Returns:
        A Coordinate object
        
    Raises:
        ValueError: If the coordinate string cannot be parsed
    """
    # First try decimal degrees format
    if ',' in coord_str:
        try:
            lat_str, lon_str = coord_str.split(',', 1)
            lat = float(lat_str.strip())
            lon = float(lon_str.strip())
            return Coordinate(lat, lon)
        except ValueError:
            pass
    
    # Try decimal degrees with direction
    if ('N' in coord_str.upper() or 'S' in coord_str.upper()) and ('E' in coord_str.upper() or 'W' in coord_str.upper()):
        parts = coord_str.upper().replace(',', ' ').split()
        lat, lon = None, None
        for i, part in enumerate(parts):
            try:
                value = float(part)
                if 'N' in parts[i+1]:
                    lat = value
                elif 'S' in parts[i+1]:
                    lat = -value
                elif 'E' in parts[i+1]:
                    lon = value
                elif 'W' in parts[i+1]:
                    lon = -value
            except (ValueError, IndexError):
                continue
        
        if lat is not None and lon is not None:
            return Coordinate(lat, lon)
    
    # Try DMS format - this is complex, so simplified implementation
    if '°' in coord_str:
        try:
            # Simplified DMS parsing - would need more robust implementation for real use
            lat_dms, lon_dms = coord_str.split(',', 1)
            
            # Parse latitude
            lat_parts = lat_dms.strip().split('°')
            lat_deg = float(lat_parts[0].strip())
            lat_min_sec = lat_parts[1].strip()
            
            if "'" in lat_min_sec:
                lat_min_parts = lat_min_sec.split("'")
                lat_min = float(lat_min_parts[0].strip())
                lat_sec_dir = lat_min_parts[1].strip()
                if '"' in lat_sec_dir:
                    lat_sec, lat_dir = lat_sec_dir.split('"')
                    lat_sec = float(lat_sec.strip())
                else:
                    lat_sec = 0
                    lat_dir = lat_sec_dir
            else:
                lat_min = 0
                lat_sec = 0
                lat_dir = lat_min_sec
            
            latitude = lat_deg + lat_min/60 + lat_sec/3600
            if 'S' in lat_dir.upper():
                latitude = -latitude
            
            # Parse longitude (similar logic)
            lon_parts = lon_dms.strip().split('°')
            lon_deg = float(lon_parts[0].strip())
            lon_min_sec = lon_parts[1].strip()
            
            if "'" in lon_min_sec:
                lon_min_parts = lon_min_sec.split("'")
                lon_min = float(lon_min_parts[0].strip())
                lon_sec_dir = lon_min_parts[1].strip()
                if '"' in lon_sec_dir:
                    lon_sec, lon_dir = lon_sec_dir.split('"')
                    lon_sec = float(lon_sec.strip())
                else:
                    lon_sec = 0
                    lon_dir = lon_sec_dir
            else:
                lon_min = 0
                lon_sec = 0
                lon_dir = lon_min_sec
            
            longitude = lon_deg + lon_min/60 + lon_sec/3600
            if 'W' in lon_dir.upper():
                longitude = -longitude
            
            return Coordinate(latitude, longitude)
        except Exception:
            pass
    
    raise ValueError(f"Could not parse coordinate string: {coord_str}")


def create_coordinate(lat: float, lon: float, alt: Optional[float] = None) -> Coordinate:
    """
    Create a coordinate object with the given latitude and longitude.
    
    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
        alt: Optional altitude in meters
        
    Returns:
        A Coordinate object
    """
    return Coordinate(lat, lon, alt) 