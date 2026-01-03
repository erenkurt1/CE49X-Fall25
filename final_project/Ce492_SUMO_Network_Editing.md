# CE492 - Micromobility Network Design Project
## SUMO Network Editing Tools

**Project**: Designing a Micromobility Network for University South Campus  
**Course**: CE492  
**Date**: December 2024

---

## Table of Contents

1. [Overview](#overview)
2. [SUMO Network Editor (`edit_sumo_network.py`)](#sumo-network-editor)
3. [Micromobility Network Designer (`micromobility_network_designer.py`)](#micromobility-network-designer)
4. [Example Usage (`example_edit_sumo.py`)](#example-usage)
5. [Quick Start Guide](#quick-start-guide)
6. [Common Modifications](#common-modifications)
7. [File Structure](#file-structure)

---

## Overview

This document contains the complete implementation for programmatically editing SUMO network files without using netedit. The tools are designed specifically for micromobility network design, allowing you to:

- Modify edge properties (speed limits, vehicle classes, priority)
- Add/remove lanes
- Configure micromobility-friendly routes
- Analyze network structure
- Bulk modify edges by type

**SUMO Network File Location**: `C:\Users\erenb\Sumo\2025-12-21-11-53-40\osm.net.xml.gz`

---

## SUMO Network Editor

### File: `edit_sumo_network.py`

Complete implementation of the core SUMO network editing library.

```python
"""
SUMO Network Editor - Edit SUMO network files programmatically without netedit

This script allows you to modify SUMO network files (.net.xml) using Python.
Common modifications include:
- Changing edge/lane properties (speed limits, priority, etc.)
- Adding/removing lanes
- Modifying junction properties
- Changing traffic light programs
- Adding/removing edges or nodes
"""

import gzip
import xml.etree.ElementTree as ET
from pathlib import Path
import shutil
from typing import Optional, Dict, List, Tuple


class SUMONetworkEditor:
    """Class to edit SUMO network files programmatically"""
    
    def __init__(self, network_file: str):
        """
        Initialize the editor with a network file
        
        Args:
            network_file: Path to the .net.xml or .net.xml.gz file
        """
        self.network_file = Path(network_file)
        self.tree = None
        self.root = None
        self.is_compressed = network_file.endswith('.gz')
        self._load_network()
    
    def _load_network(self):
        """Load the network file (handles both compressed and uncompressed)"""
        if self.is_compressed:
            with gzip.open(self.network_file, 'rb') as f:
                self.tree = ET.parse(f)
        else:
            self.tree = ET.parse(self.network_file)
        self.root = self.tree.getroot()
        print(f"Loaded network: {self.network_file}")
        print(f"  Nodes: {len(self.root.findall('.//junction'))}")
        print(f"  Edges: {len(self.root.findall('.//edge'))}")
    
    def save(self, output_file: Optional[str] = None, compress: Optional[bool] = None):
        """
        Save the modified network to a file
        
        Args:
            output_file: Output file path (if None, overwrites original)
            compress: Whether to compress (if None, uses original format)
        """
        if output_file is None:
            output_file = self.network_file
        else:
            output_file = Path(output_file)
        
        if compress is None:
            compress = self.is_compressed
        
        # Format XML nicely
        self._indent(self.root)
        
        if compress:
            if not str(output_file).endswith('.gz'):
                output_file = Path(str(output_file) + '.gz')
            with gzip.open(output_file, 'wb') as f:
                self.tree.write(f, encoding='utf-8', xml_declaration=True)
        else:
            if str(output_file).endswith('.gz'):
                output_file = Path(str(output_file).replace('.gz', ''))
            self.tree.write(output_file, encoding='utf-8', xml_declaration=True)
        
        print(f"Saved network to: {output_file}")
    
    def _indent(self, elem, level=0):
        """Add indentation to XML for readability"""
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for child in elem:
                self._indent(child, level+1)
            if not child.tail or not child.tail.strip():
                child.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
    
    # ========== EDGE MODIFICATIONS ==========
    
    def get_edge(self, edge_id: str):
        """Get an edge element by ID"""
        return self.root.find(f".//edge[@id='{edge_id}']")
    
    def get_all_edges(self) -> List[ET.Element]:
        """Get all edge elements"""
        return self.root.findall('.//edge')
    
    def modify_edge_speed(self, edge_id: str, speed: float):
        """Modify the speed limit of an edge (m/s)"""
        edge = self.get_edge(edge_id)
        if edge is None:
            print(f"Warning: Edge '{edge_id}' not found")
            return False
        
        # Update speed in all lanes
        for lane in edge.findall('lane'):
            lane.set('speed', str(speed))
        
        print(f"Modified speed of edge '{edge_id}' to {speed} m/s")
        return True
    
    def modify_edge_priority(self, edge_id: str, priority: int):
        """Modify the priority of an edge"""
        edge = self.get_edge(edge_id)
        if edge is None:
            print(f"Warning: Edge '{edge_id}' not found")
            return False
        
        edge.set('priority', str(priority))
        print(f"Modified priority of edge '{edge_id}' to {priority}")
        return True
    
    def modify_edge_allowed_classes(self, edge_id: str, allowed_classes: List[str]):
        """Modify allowed vehicle classes on an edge"""
        edge = self.get_edge(edge_id)
        if edge is None:
            print(f"Warning: Edge '{edge_id}' not found")
            return False
        
        allowed_str = ' '.join(allowed_classes)
        for lane in edge.findall('lane'):
            lane.set('allow', allowed_str)
        
        print(f"Modified allowed classes of edge '{edge_id}' to: {allowed_str}")
        return True
    
    def modify_edge_disallowed_classes(self, edge_id: str, disallowed_classes: List[str]):
        """Modify disallowed vehicle classes on an edge"""
        edge = self.get_edge(edge_id)
        if edge is None:
            print(f"Warning: Edge '{edge_id}' not found")
            return False
        
        disallowed_str = ' '.join(disallowed_classes)
        for lane in edge.findall('lane'):
            lane.set('disallow', disallowed_str)
        
        print(f"Modified disallowed classes of edge '{edge_id}' to: {disallowed_str}")
        return True
    
    def add_lane(self, edge_id: str, width: float = 3.2, speed: Optional[float] = None):
        """Add a lane to an edge"""
        edge = self.get_edge(edge_id)
        if edge is None:
            print(f"Warning: Edge '{edge_id}' not found")
            return False
        
        # Get existing lanes to determine new lane index
        existing_lanes = edge.findall('lane')
        new_index = len(existing_lanes)
        
        # Get properties from first existing lane
        if existing_lanes:
            first_lane = existing_lanes[0]
            shape = first_lane.get('shape', '')
            speed_limit = speed if speed is not None else first_lane.get('speed', '13.89')
        else:
            print(f"Warning: Edge '{edge_id}' has no lanes to copy properties from")
            return False
        
        # Create new lane
        new_lane = ET.SubElement(edge, 'lane')
        new_lane.set('id', f"{edge_id}_{new_index}")
        new_lane.set('index', str(new_index))
        new_lane.set('speed', str(speed_limit))
        new_lane.set('length', first_lane.get('length', '0'))
        new_lane.set('shape', shape)
        new_lane.set('width', str(width))
        new_lane.set('allow', first_lane.get('allow', ''))
        new_lane.set('disallow', first_lane.get('disallow', ''))
        
        print(f"Added lane {new_index} to edge '{edge_id}'")
        return True
    
    def remove_lane(self, edge_id: str, lane_index: int):
        """Remove a lane from an edge"""
        edge = self.get_edge(edge_id)
        if edge is None:
            print(f"Warning: Edge '{edge_id}' not found")
            return False
        
        lane = edge.find(f"lane[@index='{lane_index}']")
        if lane is None:
            print(f"Warning: Lane {lane_index} not found on edge '{edge_id}'")
            return False
        
        edge.remove(lane)
        print(f"Removed lane {lane_index} from edge '{edge_id}'")
        return True
    
    # ========== JUNCTION MODIFICATIONS ==========
    
    def get_junction(self, junction_id: str):
        """Get a junction element by ID"""
        return self.root.find(f".//junction[@id='{junction_id}']")
    
    def get_all_junctions(self) -> List[ET.Element]:
        """Get all junction elements"""
        return self.root.findall('.//junction')
    
    def modify_junction_type(self, junction_id: str, junction_type: str):
        """Modify the type of a junction"""
        junction = self.get_junction(junction_id)
        if junction is None:
            print(f"Warning: Junction '{junction_id}' not found")
            return False
        
        junction.set('type', junction_type)
        print(f"Modified type of junction '{junction_id}' to {junction_type}")
        return True
    
    # ========== TRAFFIC LIGHT MODIFICATIONS ==========
    
    def get_traffic_light(self, tl_id: str):
        """Get a traffic light element by ID"""
        return self.root.find(f".//tlLogic[@id='{tl_id}']")
    
    def modify_traffic_light_phase(self, tl_id: str, phase_index: int, 
                                   duration: Optional[int] = None,
                                   state: Optional[str] = None):
        """Modify a traffic light phase"""
        tl = self.get_traffic_light(tl_id)
        if tl is None:
            print(f"Warning: Traffic light '{tl_id}' not found")
            return False
        
        phases = tl.findall('phase')
        if phase_index >= len(phases):
            print(f"Warning: Phase {phase_index} not found in traffic light '{tl_id}'")
            return False
        
        phase = phases[phase_index]
        if duration is not None:
            phase.set('duration', str(duration))
        if state is not None:
            phase.set('state', state)
        
        print(f"Modified phase {phase_index} of traffic light '{tl_id}'")
        return True
    
    # ========== BULK OPERATIONS ==========
    
    def modify_all_edges_by_type(self, edge_type: str, speed: Optional[float] = None,
                                 priority: Optional[int] = None):
        """Modify all edges of a certain type"""
        edges = self.root.findall(f".//edge[@type='{edge_type}']")
        count = 0
        for edge in edges:
            if speed is not None:
                self.modify_edge_speed(edge.get('id'), speed)
            if priority is not None:
                self.modify_edge_priority(edge.get('id'), priority)
            count += 1
        print(f"Modified {count} edges of type '{edge_type}'")
        return count
    
    def set_micromobility_allowed(self, edge_ids: List[str], 
                                  vehicle_classes: List[str] = None):
        """
        Set edges to allow micromobility vehicles
        
        Args:
            edge_ids: List of edge IDs to modify
            vehicle_classes: List of vehicle classes (default: ['bicycle', 'motorcycle'])
        """
        if vehicle_classes is None:
            vehicle_classes = ['bicycle', 'motorcycle', 'moped']
        
        count = 0
        for edge_id in edge_ids:
            if self.modify_edge_allowed_classes(edge_id, vehicle_classes):
                count += 1
        
        print(f"Set {count} edges to allow micromobility")
        return count
    
    def set_micromobility_disallowed(self, edge_ids: List[str]):
        """Set edges to disallow micromobility vehicles"""
        vehicle_classes = ['bicycle', 'motorcycle', 'moped']
        count = 0
        for edge_id in edge_ids:
            if self.modify_edge_disallowed_classes(edge_id, vehicle_classes):
                count += 1
        
        print(f"Set {count} edges to disallow micromobility")
        return count
    
    # ========== QUERY METHODS ==========
    
    def list_edges(self, filter_by_type: Optional[str] = None) -> List[Dict]:
        """List all edges with their properties"""
        edges = self.get_all_edges()
        result = []
        
        for edge in edges:
            if filter_by_type and edge.get('type') != filter_by_type:
                continue
            
            edge_info = {
                'id': edge.get('id'),
                'from': edge.get('from'),
                'to': edge.get('to'),
                'type': edge.get('type'),
                'priority': edge.get('priority'),
                'num_lanes': len(edge.findall('lane')),
                'speed': edge.find('lane').get('speed') if edge.find('lane') is not None else None
            }
            result.append(edge_info)
        
        return result
    
    def find_edges_by_attribute(self, attribute: str, value: str) -> List[str]:
        """Find edge IDs by attribute value"""
        edges = self.root.findall(f".//edge[@{attribute}='{value}']")
        return [edge.get('id') for edge in edges]


# ========== EXAMPLE USAGE ==========

def example_usage():
    """Example of how to use the SUMO Network Editor"""
    
    # Path to your SUMO network file
    network_file = r"C:\Users\erenb\Sumo\2025-12-21-11-53-40\osm.net.xml.gz"
    
    # Create editor instance
    editor = SUMONetworkEditor(network_file)
    
    # Example 1: Modify speed limit of a specific edge
    # editor.modify_edge_speed('edge_id_here', 8.33)  # 30 km/h in m/s
    
    # Example 2: Allow micromobility on specific edges
    # editor.set_micromobility_allowed(['edge1', 'edge2', 'edge3'])
    
    # Example 3: Modify all edges of a certain type
    # editor.modify_all_edges_by_type('highway.primary', speed=11.11)  # 40 km/h
    
    # Example 4: List all edges
    # edges = editor.list_edges()
    # for edge in edges[:10]:  # Show first 10
    #     print(edge)
    
    # Example 5: Find edges by type
    # primary_edges = editor.find_edges_by_attribute('type', 'highway.primary')
    # print(f"Found {len(primary_edges)} primary highway edges")
    
    # Save the modified network
    # editor.save()  # Overwrites original
    # editor.save('modified_network.net.xml.gz')  # Save to new file
    
    print("\nExample usage shown. Uncomment the lines above to use.")


if __name__ == "__main__":
    example_usage()
```

---

## Micromobility Network Designer

### File: `micromobility_network_designer.py`

Specialized tool for designing micromobility networks.

```python
"""
Micromobility Network Designer for SUMO
Customize your SUMO network for micromobility (bicycles, e-scooters, etc.)
"""

from edit_sumo_network import SUMONetworkEditor
from pathlib import Path
import shutil
import json


def design_micromobility_network(network_file: str, output_file: str = None):
    """
    Design a micromobility network by modifying SUMO network file
    
    Args:
        network_file: Path to input SUMO network file
        output_file: Path to output file (if None, creates backup and modifies original)
    """
    
    # Initialize editor
    editor = SUMONetworkEditor(network_file)
    
    print("\n" + "="*60)
    print("MICROMOBILITY NETWORK DESIGNER")
    print("="*60)
    
    # Step 1: Analyze current network
    print("\n1. Analyzing current network...")
    all_edges = editor.list_edges()
    print(f"   Total edges: {len(all_edges)}")
    
    # Group edges by type
    edge_types = {}
    for edge in all_edges:
        edge_type = edge.get('type', 'unknown')
        edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
    
    print(f"   Edge types found: {len(edge_types)}")
    for etype, count in sorted(edge_types.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"     {etype}: {count} edges")
    
    # Step 2: Identify suitable edges for micromobility
    print("\n2. Identifying edges suitable for micromobility...")
    
    # Common edge types that might be suitable for micromobility
    suitable_types = [
        'highway.residential',
        'highway.service',
        'highway.living_street',
        'highway.cycleway',
        'highway.path',
        'highway.footway',
        'highway.pedestrian',
        'highway.secondary',
        'highway.tertiary'
    ]
    
    micromobility_edges = []
    for edge in all_edges:
        edge_type = edge.get('type', '')
        if any(suitable in edge_type for suitable in suitable_types):
            micromobility_edges.append(edge['id'])
    
    print(f"   Found {len(micromobility_edges)} potentially suitable edges")
    
    # Step 3: Configure micromobility-friendly settings
    print("\n3. Configuring micromobility-friendly settings...")
    
    # Allow micromobility on suitable edges
    editor.set_micromobility_allowed(micromobility_edges[:100])  # Limit to first 100 for demo
    print(f"   Configured {min(100, len(micromobility_edges))} edges for micromobility")
    
    # Step 4: Adjust speed limits for safer micromobility
    print("\n4. Adjusting speed limits for micromobility safety...")
    
    # Set lower speed limits on residential and service roads
    residential_edges = editor.find_edges_by_attribute('type', 'highway.residential')
    if residential_edges:
        for edge_id in residential_edges[:50]:  # Limit for demo
            editor.modify_edge_speed(edge_id, 8.33)  # 30 km/h
        print(f"   Set speed limit to 30 km/h on {min(50, len(residential_edges))} residential edges")
    
    # Step 5: Save the modified network
    print("\n5. Saving modified network...")
    if output_file is None:
        # Create backup
        backup_file = str(network_file).replace('.xml.gz', '_backup.xml.gz').replace('.xml', '_backup.xml')
        print(f"   Creating backup: {backup_file}")
        shutil.copy(network_file, backup_file)
        editor.save()
    else:
        editor.save(output_file)
    
    print("\n" + "="*60)
    print("NETWORK DESIGN COMPLETE!")
    print("="*60)
    
    return editor


def customize_specific_edges(network_file: str, edge_config: dict, output_file: str = None):
    """
    Customize specific edges based on configuration
    
    Args:
        network_file: Path to SUMO network file
        edge_config: Dictionary with edge configurations
                    Example: {
                        'edge_id_1': {'speed': 8.33, 'allowed': ['bicycle', 'motorcycle']},
                        'edge_id_2': {'speed': 11.11, 'priority': 5}
                    }
        output_file: Output file path
    """
    editor = SUMONetworkEditor(network_file)
    
    print(f"\nCustomizing {len(edge_config)} edges...")
    
    for edge_id, config in edge_config.items():
        if 'speed' in config:
            editor.modify_edge_speed(edge_id, config['speed'])
        if 'priority' in config:
            editor.modify_edge_priority(edge_id, config['priority'])
        if 'allowed' in config:
            editor.modify_edge_allowed_classes(edge_id, config['allowed'])
        if 'disallowed' in config:
            editor.modify_edge_disallowed_classes(edge_id, config['disallowed'])
    
    editor.save(output_file)
    print("Customization complete!")


def create_micromobility_lanes(network_file: str, edge_ids: list, output_file: str = None):
    """
    Add dedicated micromobility lanes to specific edges
    
    Args:
        network_file: Path to SUMO network file
        edge_ids: List of edge IDs to add lanes to
        output_file: Output file path
    """
    editor = SUMONetworkEditor(network_file)
    
    print(f"\nAdding micromobility lanes to {len(edge_ids)} edges...")
    
    for edge_id in edge_ids:
        # Add a new lane for micromobility
        editor.add_lane(edge_id, width=2.0, speed=8.33)  # 2m wide, 30 km/h
        
        # Set the new lane to only allow micromobility
        edge = editor.get_edge(edge_id)
        if edge is not None:
            lanes = edge.findall('lane')
            if lanes:
                last_lane = lanes[-1]
                last_lane.set('allow', 'bicycle motorcycle moped')
                last_lane.set('disallow', 'passenger bus truck')
    
    editor.save(output_file)
    print("Micromobility lanes added!")


# ========== MAIN EXAMPLE ==========

if __name__ == "__main__":
    # Path to your SUMO network file
    network_file = r"C:\Users\erenb\Sumo\2025-12-21-11-53-40\osm.net.xml.gz"
    
    # Check if file exists
    if not Path(network_file).exists():
        print(f"Error: Network file not found: {network_file}")
        print("\nPlease update the network_file path in this script.")
    else:
        # Option 1: Automated micromobility network design
        print("Running automated micromobility network design...")
        design_micromobility_network(network_file, output_file=None)
        
        # Option 2: Customize specific edges (uncomment to use)
        # edge_config = {
        #     'edge_123': {'speed': 8.33, 'allowed': ['bicycle', 'motorcycle']},
        #     'edge_456': {'speed': 11.11, 'priority': 5}
        # }
        # customize_specific_edges(network_file, edge_config)
        
        # Option 3: Add dedicated lanes (uncomment to use)
        # important_edges = ['edge_123', 'edge_456', 'edge_789']
        # create_micromobility_lanes(network_file, important_edges)
```

---

## Example Usage

### File: `example_edit_sumo.py`

Simple example script for quick edits.

```python
"""
Simple example script to edit your SUMO network file
Modify this script according to your needs
"""

from edit_sumo_network import SUMONetworkEditor
from pathlib import Path

# ========== CONFIGURATION ==========
# Update this path to your SUMO network file
NETWORK_FILE = r"C:\Users\erenb\Sumo\2025-12-21-11-53-40\osm.net.xml.gz"

# Output file (None = overwrite original, or specify a new file)
OUTPUT_FILE = None  # Or: "modified_network.net.xml.gz"

# ========== YOUR MODIFICATIONS ==========

def main():
    """Main function to edit your SUMO network"""
    
    # Check if file exists
    if not Path(NETWORK_FILE).exists():
        print(f"Error: Network file not found: {NETWORK_FILE}")
        print("\nPlease update the NETWORK_FILE path in this script.")
        return
    
    # Create editor
    print("Loading SUMO network...")
    editor = SUMONetworkEditor(NETWORK_FILE)
    
    # ========== EXAMPLE 1: Analyze your network ==========
    print("\n" + "="*60)
    print("ANALYZING NETWORK")
    print("="*60)
    
    # List all edges (first 10)
    edges = editor.list_edges()
    print(f"\nTotal edges in network: {len(edges)}")
    print("\nFirst 10 edges:")
    for i, edge in enumerate(edges[:10], 1):
        print(f"  {i}. {edge['id']} - Type: {edge.get('type', 'N/A')}, "
              f"Lanes: {edge['num_lanes']}, Speed: {edge.get('speed', 'N/A')} m/s")
    
    # Count edges by type
    edge_types = {}
    for edge in edges:
        edge_type = edge.get('type', 'unknown')
        edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
    
    print(f"\nEdge types (top 10):")
    for etype, count in sorted(edge_types.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {etype}: {count} edges")
    
    # ========== EXAMPLE 2: Find specific edges ==========
    print("\n" + "="*60)
    print("FINDING EDGES")
    print("="*60)
    
    # Find residential roads
    residential = editor.find_edges_by_attribute('type', 'highway.residential')
    print(f"\nResidential edges found: {len(residential)}")
    if residential:
        print(f"  Examples: {residential[:5]}")
    
    # ========== EXAMPLE 3: Make modifications ==========
    print("\n" + "="*60)
    print("MAKING MODIFICATIONS")
    print("="*60)
    
    # Uncomment the modifications you want to make:
    
    # Option A: Modify speed of specific edges
    # if residential:
    #     print(f"\nModifying speed of {min(5, len(residential))} residential edges...")
    #     for edge_id in residential[:5]:
    #         editor.modify_edge_speed(edge_id, 8.33)  # 30 km/h
    
    # Option B: Allow micromobility on specific edges
    # if residential:
    #     print(f"\nAllowing micromobility on {min(10, len(residential))} edges...")
    #     editor.set_micromobility_allowed(residential[:10])
    
    # Option C: Modify all edges of a type
    # print("\nModifying all residential edges...")
    # editor.modify_all_edges_by_type('highway.residential', speed=8.33)
    
    # Option D: Customize specific edges (replace with your edge IDs)
    # custom_edges = {
    #     'edge_id_1': {'speed': 8.33, 'allowed': ['bicycle', 'motorcycle']},
    #     'edge_id_2': {'speed': 11.11, 'priority': 5}
    # }
    # for edge_id, config in custom_edges.items():
    #     if 'speed' in config:
    #         editor.modify_edge_speed(edge_id, config['speed'])
    #     if 'allowed' in config:
    #         editor.modify_edge_allowed_classes(edge_id, config['allowed'])
    
    print("\n(No modifications made - uncomment examples above to make changes)")
    
    # ========== EXAMPLE 4: Save the network ==========
    print("\n" + "="*60)
    print("SAVING NETWORK")
    print("="*60)
    
    if OUTPUT_FILE is None:
        response = input("\nSave changes? This will modify the original file. (yes/no): ")
        if response.lower() != 'yes':
            print("Saving cancelled.")
            return
    
    editor.save(OUTPUT_FILE)
    print("\nDone! Network file has been updated.")


if __name__ == "__main__":
    main()
```

---

## Quick Start Guide

### 1. Basic Usage

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

### 2. Run the Example Script

```bash
python example_edit_sumo.py
```

This will analyze your network and show you what's available.

### 3. Use the Micromobility Designer

```python
from micromobility_network_designer import design_micromobility_network

network_file = r"C:\Users\erenb\Sumo\2025-12-21-11-53-40\osm.net.xml.gz"
design_micromobility_network(network_file)
```

---

## Common Modifications

### Speed Limits

```python
# Set speed limit to 30 km/h (8.33 m/s) for safer micromobility
editor.modify_edge_speed('edge_123', 8.33)

# Set speed limit to 40 km/h (11.11 m/s)
editor.modify_edge_speed('edge_456', 11.11)
```

### Vehicle Classes

```python
# Allow only micromobility vehicles
editor.modify_edge_allowed_classes('edge_123', ['bicycle', 'motorcycle', 'moped'])

# Disallow large vehicles
editor.modify_edge_disallowed_classes('edge_123', ['truck', 'bus', 'trailer'])
```

### Bulk Operations

```python
# Modify all residential roads
editor.modify_all_edges_by_type('highway.residential', speed=8.33)

# Set multiple edges for micromobility
edge_list = ['edge_1', 'edge_2', 'edge_3']
editor.set_micromobility_allowed(edge_list)
```

---

## Speed Conversion Reference

Common speed limits in m/s (SUMO uses meters per second):

- 20 km/h = 5.56 m/s
- 30 km/h = 8.33 m/s
- 40 km/h = 11.11 m/s
- 50 km/h = 13.89 m/s
- 60 km/h = 16.67 m/s
- 70 km/h = 19.44 m/s
- 80 km/h = 22.22 m/s

---

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

---

## File Structure

```
final_project/
├── edit_sumo_network.py              # Core SUMO network editor
├── micromobility_network_designer.py  # Micromobility-specific tools
├── example_edit_sumo.py               # Simple example script
├── SUMO_NETWORK_EDITING_GUIDE.md     # Detailed documentation
└── Ce492_SUMO_Network_Editing.md    # This file
```

---

## Notes

- The editor handles both compressed (`.net.xml.gz`) and uncompressed (`.net.xml`) files automatically
- Always create backups before making major modifications
- Test changes in SUMO GUI before running full simulations
- Edge IDs in SUMO are often auto-generated (e.g., `-12345_0`)

---

**For more detailed documentation, see `SUMO_NETWORK_EDITING_GUIDE.md`**


