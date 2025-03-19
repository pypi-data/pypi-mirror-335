# GPS Tools

A comprehensive Python package for working with GPS coordinates, handling conversions, distance calculations, and geofencing operations.

## Features

- **Coordinate handling**: Work with latitude/longitude, UTM, and MGRS coordinates
- **Conversions**: Convert between different coordinate systems
- **Distance calculations**: Calculate distances, bearings, and midpoints
- **Geofencing**: Create and work with geographical boundaries
- **Validation**: Robust coordinate validation functions

## Installation

```bash
pip install gps-tools
```

## Quick Example

```python
from gps_tools import Coordinate
from gps_tools.distance import haversine_distance

# Create coordinates for two cities
new_york = Coordinate(40.7128, -74.0060, name="New York")
los_angeles = Coordinate(34.0522, -118.2437, name="Los Angeles")

# Calculate the distance between them
distance = haversine_distance(new_york, los_angeles)
print(f"The distance between {new_york.name} and {los_angeles.name} is {distance/1000:.2f} km")
```

## Documentation

For complete documentation, examples, and API reference, visit the [documentation directory](documentation/).

## Optional Dependencies

GPS Tools has optional dependencies for advanced features:

```bash
# For visualization features
pip install gps-tools[viz]

# For GIS integration
pip install gps-tools[gis]

# For development
pip install gps-tools[dev]
```

## Contributing

Contributions are welcome! Please check our [contributing guide](documentation/guides/contributing.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 