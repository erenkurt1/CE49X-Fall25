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


