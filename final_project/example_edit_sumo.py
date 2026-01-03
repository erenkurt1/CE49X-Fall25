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


