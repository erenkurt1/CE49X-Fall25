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

