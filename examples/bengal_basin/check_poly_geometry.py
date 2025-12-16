#!/usr/bin/env python3
"""
Visualize the geometry from a .poly file
This allows checking the model structure without running the full simulation.
"""

import matplotlib.pyplot as plt
import numpy as np
import sys

def parse_poly_file(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    
    # Iterator over lines
    it = iter(lines)
    
    # 1. Read Nodes
    try:
        # First line: npoints ndims 0 0
        header = next(it).split()
        npoints = int(header[0])
        
        nodes = {}
        for _ in range(npoints):
            # i x z
            parts = next(it).split()
            idx = int(parts[0])
            x = float(parts[1])
            z = float(parts[2])
            nodes[idx] = (x, z)
            
        # 2. Read Segments
        # Header: nsegments 1
        header = next(it).split()
        nsegments = int(header[0])
        
        segments = []
        for _ in range(nsegments):
            # j p1 p2 flag
            parts = next(it).split()
            p1 = int(parts[1])
            p2 = int(parts[2])
            segments.append((p1, p2))
            
        # 3. Read Regions (if holes section is skipped or empty)
        # Check for holes header
        # The file format often has "0" for holes if none
        line = next(it)
        nholes = int(line.split()[0])
        for _ in range(nholes):
            next(it) # Valid hole lines if any
            
        # Regions header: nregions
        header = next(it).split()
        nregions = int(header[0])
        
        regions = []
        for _ in range(nregions):
            # k x z mattype max_area
            parts = next(it).split()
            x = float(parts[1])
            z = float(parts[2])
            mattype = int(float(parts[3])) # Handle 0.0 or 0
            regions.append({'x': x, 'z': z, 'mat': mattype})
            
        return nodes, segments, regions
        
    except StopIteration:
        print("Error: Unexpected end of file")
        return None, None, None
    except Exception as e:
        print(f"Error parsing file: {e}")
        return None, None, None

def plot_geometry(nodes, segments, regions, output_file="geometry_check.png"):
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot segments
    for p1, p2 in segments:
        x = [nodes[p1][0], nodes[p2][0]]
        z = [nodes[p1][1], nodes[p2][1]]
        ax.plot(x, z, 'k-', linewidth=0.5, alpha=0.7)
        
    # Plot regions
    mat_colors = plt.cm.tab10(np.linspace(0, 1, 10))
    
    # Group regions by material for legend
    mat_regions = {}
    for r in regions:
        mat = r['mat']
        if mat not in mat_regions:
            mat_regions[mat] = {'x': [], 'z': []}
        mat_regions[mat]['x'].append(r['x'])
        mat_regions[mat]['z'].append(r['z'])
        
    layer_names = {
        0: "Alluvium",
        1: "Tertiary",
        2: "Upper Crust",
        3: "Middle Crust",
        4: "Lower Crust"
    }
    
    for mat in sorted(mat_regions.keys()):
        label = f"Mat {mat}: {layer_names.get(mat, 'Unknown')}"
        ax.scatter(mat_regions[mat]['x'], mat_regions[mat]['z'], 
                   color=mat_colors[mat], label=label, s=100, edgecolors='w', zorder=10)
        
    ax.set_xlabel("Distance (m)")
    ax.set_ylabel("Depth (m)")
    ax.set_title("Madhupur Fault Geometry Check\n(Segments + Region Markers)")
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150)
    print(f"Plot saved to {output_file}")

if __name__ == "__main__":
    poly_file = "madhupur_fault.poly"
    print(f"Reading {poly_file}...")
    nodes, segments, regions = parse_poly_file(poly_file)
    
    if nodes:
        print(f"Found {len(nodes)} nodes, {len(segments)} segments, {len(regions)} regions.")
        plot_geometry(nodes, segments, regions)
    else:
        print("Failed to read geometry.")
