# SUMO Network Editing Guide

This guide explains how to edit SUMO network files programmatically without using netedit.

## Overview

SUMO network files are XML-based and can be edited using Python. This project provides two main scripts:

1. **`edit_sumo_network.py`** - Core library for editing SUMO networks
2. **`micromobility_network_designer.py`** - Specialized tool for micromobility network design

## Quick Start

### Basic Usage

```python
from edit_sumo_network import SUMONetworkEditor

# Load your network file
network_file = r"C:\Users\erenb\Sumo\2025-12-21-11-53-40\osm.net.xml.gz"
editor = SUMONetworkEditor(network_file)

# Make modifications
editor.modify_edge_speed('edge_id_here', 8.33)  # 30 km/h in m/s

# Save changes
editor.save()  # Overwrites original
# OR
editor.save('modified_network.net.xml.gz')  # Save to new file
```

## Common Modifications for Micromobility Networks

### 1. Modify Speed Limits

```python
# Set speed limit to 30 km/h (8.33 m/s) for safer micromobility
editor.modify_edge_speed('edge_123', 8.33)

# Set speed limit to 40 km/h (11.11 m/s)
editor.modify_edge_speed('edge_456', 11.11)
```

### 2. Allow/Disallow Vehicle Classes

```python
# Allow only micromobility vehicles
editor.modify_edge_allowed_classes('edge_123', ['bicycle', 'motorcycle', 'moped'])

# Disallow large vehicles
editor.modify_edge_disallowed_classes('edge_123', ['truck', 'bus', 'trailer'])
```

### 3. Bulk Operations

```python
# Modify all residential roads
editor.modify_all_edges_by_type('highway.residential', speed=8.33)

# Set multiple edges for micromobility
edge_list = ['edge_1', 'edge_2', 'edge_3']
editor.set_micromobility_allowed(edge_list)
```

### 4. Add/Remove Lanes

```python
# Add a new lane to an edge
editor.add_lane('edge_123', width=2.0, speed=8.33)

# Remove a lane
editor.remove_lane('edge_123', lane_index=0)
```

### 5. Modify Junction Properties

```python
# Change junction type
editor.modify_junction_type('junction_123', 'priority')
```

### 6. Modify Traffic Lights

```python
# Change traffic light phase duration
editor.modify_traffic_light_phase('tl_123', phase_index=0, duration=30)

# Change traffic light state
editor.modify_traffic_light_phase('tl_123', phase_index=0, state='GGGrrrGGGrrr')
```

## Querying the Network

### List All Edges

```python
# Get all edges with their properties
edges = editor.list_edges()
for edge in edges:
    print(f"Edge {edge['id']}: {edge['num_lanes']} lanes, speed={edge['speed']} m/s")

# Filter by type
residential_edges = editor.list_edges(filter_by_type='highway.residential')
```

### Find Edges by Attribute

```python
# Find all edges of a specific type
primary_edges = editor.find_edges_by_attribute('type', 'highway.primary')

# Find edges connected to a specific junction
from_junction = editor.find_edges_by_attribute('from', 'junction_123')
```

## Using the Micromobility Network Designer

The `micromobility_network_designer.py` script provides automated network design:

```python
from micromobility_network_designer import design_micromobility_network

network_file = r"C:\Users\erenb\Sumo\2025-12-21-11-53-40\osm.net.xml.gz"
design_micromobility_network(network_file)
```

This will:
1. Analyze your network
2. Identify suitable edges for micromobility
3. Configure speed limits
4. Set vehicle class permissions
5. Save the modified network (with backup)

## Customizing Specific Edges

```python
from micromobility_network_designer import customize_specific_edges

edge_config = {
    'edge_123': {
        'speed': 8.33,  # 30 km/h
        'allowed': ['bicycle', 'motorcycle'],
        'priority': 5
    },
    'edge_456': {
        'speed': 11.11,  # 40 km/h
        'disallowed': ['truck', 'bus']
    }
}

customize_specific_edges(network_file, edge_config)
```

## Adding Dedicated Micromobility Lanes

```python
from micromobility_network_designer import create_micromobility_lanes

# Add dedicated lanes to important edges
important_edges = ['edge_123', 'edge_456', 'edge_789']
create_micromobility_lanes(network_file, important_edges)
```

## File Formats

The editor handles both compressed (`.net.xml.gz`) and uncompressed (`.net.xml`) files automatically.

- **Input**: Can be either format
- **Output**: Will match input format unless specified

```python
# Load compressed, save uncompressed
editor = SUMONetworkEditor('network.net.xml.gz')
editor.save('network.net.xml', compress=False)

# Load uncompressed, save compressed
editor = SUMONetworkEditor('network.net.xml')
editor.save('network.net.xml.gz', compress=True)
```

## Speed Conversion Reference

Common speed limits in m/s (SUMO uses meters per second):

- 20 km/h = 5.56 m/s
- 30 km/h = 8.33 m/s
- 40 km/h = 11.11 m/s
- 50 km/h = 13.89 m/s
- 60 km/h = 16.67 m/s
- 70 km/h = 19.44 m/s
- 80 km/h = 22.22 m/s

## Vehicle Classes in SUMO

Common vehicle classes:
- `bicycle` - Bicycles
- `motorcycle` - Motorcycles
- `moped` - Mopeds
- `passenger` - Passenger cars
- `bus` - Buses
- `truck` - Trucks
- `trailer` - Trailers
- `pedestrian` - Pedestrians (for pedestrian networks)

## Tips for Micromobility Network Design

1. **Start with Analysis**: Use `list_edges()` to understand your network structure
2. **Identify Suitable Roads**: Focus on residential, service, and secondary roads
3. **Set Appropriate Speeds**: Lower speeds (20-30 km/h) are safer for micromobility
4. **Create Dedicated Lanes**: Add separate lanes for micromobility on busy roads
5. **Restrict Large Vehicles**: Disallow trucks and buses on micromobility routes
6. **Test Incrementally**: Make small changes and test in SUMO before major modifications

## Troubleshooting

### Edge Not Found
If you get "Edge not found" warnings:
- Use `list_edges()` to see available edge IDs
- Edge IDs in SUMO are often auto-generated (e.g., `-12345_0`)

### Junction Not Found
- Use `get_all_junctions()` to list available junctions
- Junction IDs follow similar patterns to edges

### File Not Loading
- Ensure the file path is correct
- Check if the file is compressed (.gz) or uncompressed
- Verify the file is a valid SUMO network XML file

## Advanced Usage

### Direct XML Manipulation

For advanced modifications, you can access the XML tree directly:

```python
editor = SUMONetworkEditor(network_file)

# Access root element
root = editor.root

# Find and modify any element
for edge in root.findall('.//edge'):
    # Your custom modifications here
    pass

editor.save()
```

## Example Workflow

```python
from edit_sumo_network import SUMONetworkEditor

# 1. Load network
editor = SUMONetworkEditor('network.net.xml.gz')

# 2. Analyze
edges = editor.list_edges()
print(f"Total edges: {len(edges)}")

# 3. Find suitable edges
residential = editor.find_edges_by_attribute('type', 'highway.residential')
print(f"Residential edges: {len(residential)}")

# 4. Modify for micromobility
for edge_id in residential[:50]:  # First 50
    editor.modify_edge_speed(edge_id, 8.33)  # 30 km/h
    editor.modify_edge_allowed_classes(edge_id, ['bicycle', 'motorcycle'])

# 5. Save
editor.save('micromobility_network.net.xml.gz')
```

## Next Steps

1. Run the analysis to understand your network
2. Identify key routes for micromobility
3. Make targeted modifications
4. Test in SUMO GUI or simulation
5. Iterate based on results

For more information about SUMO, visit: https://sumo.dlr.de/docs/


