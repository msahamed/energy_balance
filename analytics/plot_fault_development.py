#!/usr/bin/env python3
"""
Analyze and visualize fault development in subduction zone
Generates comprehensive fault analysis plots
"""

import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import sys
import os

def get_scalar_data(lines, field_name, n_points):
    """Extract scalar field from VTK"""
    for i, line in enumerate(lines):
        if f'SCALARS {field_name}' in line:
            values = []
            start = i + 2
            for j in range(start, min(start + n_points, len(lines))):
                try:
                    values.append(float(lines[j].strip()))
                except:
                    break
            return np.array(values)
    return None

def analyze_fault_development(vtk_dir, output_dir):
    """Generate fault development plots"""

    vtk_files = sorted([f for f in os.listdir(vtk_dir) if f.endswith('.vtk')])
    if not vtk_files:
        print("No VTK files found!")
        return

    latest = os.path.join(vtk_dir, vtk_files[-1])
    print(f"Analyzing fault development from: {vtk_files[-1]}")

    with open(latest, 'r') as f:
        lines = f.readlines()

    # Get time
    time_match = re.search(r'time ([0-9.e+\-]+)', lines[1])
    time_yr = float(time_match.group(1)) / 3.15e7

    # Get data
    n_points = int(lines[4].split()[1])

    # Extract coordinates
    coords = []
    for i in range(5, 5 + n_points):
        x, z, y = map(float, lines[i].strip().split())
        coords.append([x/1000, z/1000])
    coords = np.array(coords)

    # Extract fields
    plstrain = get_scalar_data(lines, 'plastic_strain', n_points)
    material = get_scalar_data(lines, 'material_type', n_points)
    strain_rate = get_scalar_data(lines, 'strain_rate', n_points)
    temp = get_scalar_data(lines, 'temperature', n_points)
    power_term = get_scalar_data(lines, 'powerTerm', n_points)

    # Create comprehensive fault analysis figure
    fig = plt.figure(figsize=(18, 12))

    # 1. Plastic strain field with fault zones highlighted
    ax1 = plt.subplot(3, 3, 1)
    if plstrain is not None:
        scatter = ax1.scatter(coords[:,0], coords[:,1], c=plstrain,
                            s=15, cmap='YlOrRd', vmin=0, vmax=1.0)
        plt.colorbar(scatter, ax=ax1, label='Plastic Strain')

        # Highlight fault zones
        faulted = plstrain > 0.05
        if faulted.any():
            ax1.scatter(coords[faulted,0], coords[faulted,1],
                       s=30, facecolors='none', edgecolors='blue',
                       linewidths=1, label='Faulted (>0.05)')

        ax1.set_title(f'Fault Zones (t = {time_yr/1000:.1f} kyr)')
        ax1.set_xlabel('X (km)')
        ax1.set_ylabel('Z (km)')
        ax1.set_aspect('equal')
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3)

    # 2. Fault classification
    ax2 = plt.subplot(3, 3, 2)
    if plstrain is not None:
        moderate = (plstrain > 0.05) & (plstrain <= 0.2)
        active = (plstrain > 0.2) & (plstrain <= 0.5)
        mature = plstrain > 0.5

        ax2.scatter(coords[:,0], coords[:,1], c='lightgray', s=5, alpha=0.3, label='Unfaulted')
        if moderate.any():
            ax2.scatter(coords[moderate,0], coords[moderate,1], c='yellow',
                       s=20, label=f'Moderate ({moderate.sum()})')
        if active.any():
            ax2.scatter(coords[active,0], coords[active,1], c='orange',
                       s=30, label=f'Active ({active.sum()})')
        if mature.any():
            ax2.scatter(coords[mature,0], coords[mature,1], c='red',
                       s=40, marker='*', label=f'Mature ({mature.sum()})')

        ax2.set_title('Fault Classification')
        ax2.set_xlabel('X (km)')
        ax2.set_ylabel('Z (km)')
        ax2.set_aspect('equal')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

    # 3. Depth distribution of faults
    ax3 = plt.subplot(3, 3, 3)
    if plstrain is not None:
        faulted = plstrain > 0.05
        if faulted.any():
            fault_depths = -coords[faulted, 1]
            ax3.hist(fault_depths, bins=30, color='steelblue',
                    alpha=0.7, edgecolor='black')
            ax3.axvline(fault_depths.mean(), color='red', linestyle='--',
                       linewidth=2, label=f'Mean: {fault_depths.mean():.1f} km')
            ax3.set_xlabel('Depth (km)')
            ax3.set_ylabel('Number of Faulted Nodes')
            ax3.set_title('Fault Depth Distribution')
            ax3.legend()
            ax3.grid(True, alpha=0.3)

    # 4. Material-specific faulting
    ax4 = plt.subplot(3, 3, 4)
    if material is not None and plstrain is not None:
        materials = np.unique(material)
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

        for idx, mat in enumerate(materials):
            mat = int(mat)
            mask = material == mat
            mat_name = f"Mat {mat} (Slab)" if mat == 0 else f"Mat {mat} (Wedge)"

            # Plot all nodes of this material
            ax4.scatter(coords[mask,0], coords[mask,1],
                       c=colors[mat], s=5, alpha=0.2, label=mat_name)

            # Highlight faulted nodes
            faulted_mask = mask & (plstrain > 0.05)
            if faulted_mask.any():
                ax4.scatter(coords[faulted_mask,0], coords[faulted_mask,1],
                           c=colors[mat], s=30, edgecolors='black',
                           linewidths=0.5)

        ax4.set_title('Faulting by Material Type')
        ax4.set_xlabel('X (km)')
        ax4.set_ylabel('Z (km)')
        ax4.set_aspect('equal')
        ax4.legend()
        ax4.grid(True, alpha=0.3)

    # 5. Brittle vs Ductile deformation
    ax5 = plt.subplot(3, 3, 5)
    if temp is not None and plstrain is not None:
        faulted = plstrain > 0.05
        if faulted.any():
            brittle_temp = 450 + 273
            ductile_temp = 600 + 273

            brittle = faulted & (temp < brittle_temp)
            transitional = faulted & (temp >= brittle_temp) & (temp < ductile_temp)
            ductile = faulted & (temp >= ductile_temp)

            ax5.scatter(coords[:,0], coords[:,1], c='lightgray',
                       s=5, alpha=0.2, label='Unfaulted')
            if brittle.any():
                ax5.scatter(coords[brittle,0], coords[brittle,1],
                           c='blue', s=20, label=f'Brittle ({brittle.sum()})')
            if transitional.any():
                ax5.scatter(coords[transitional,0], coords[transitional,1],
                           c='green', s=20, label=f'Transitional ({transitional.sum()})')
            if ductile.any():
                ax5.scatter(coords[ductile,0], coords[ductile,1],
                           c='red', s=20, label=f'Ductile ({ductile.sum()})')

            ax5.set_title('Deformation Style (by Temperature)')
            ax5.set_xlabel('X (km)')
            ax5.set_ylabel('Z (km)')
            ax5.set_aspect('equal')
            ax5.legend()
            ax5.grid(True, alpha=0.3)

    # 6. Plastic strain vs depth profile
    ax6 = plt.subplot(3, 3, 6)
    if plstrain is not None:
        depth = -coords[:,1]
        ax6.scatter(plstrain, depth, s=10, alpha=0.5, c=depth, cmap='viridis')
        ax6.axvline(0.05, color='orange', linestyle='--', label='Moderate')
        ax6.axvline(0.2, color='red', linestyle='--', label='Active')
        ax6.axvline(0.5, color='darkred', linestyle='--', label='Mature')
        ax6.set_xlabel('Plastic Strain')
        ax6.set_ylabel('Depth (km)')
        ax6.set_title('Plastic Strain vs Depth')
        ax6.legend()
        ax6.grid(True, alpha=0.3)

    # 7. Strain rate in fault zones
    ax7 = plt.subplot(3, 3, 7)
    if strain_rate is not None and plstrain is not None:
        faulted = plstrain > 0.05
        unfaulted = plstrain <= 0.05

        ax7.hist(np.log10(strain_rate[unfaulted] + 1e-20), bins=30,
                alpha=0.5, label='Unfaulted', color='gray')
        ax7.hist(np.log10(strain_rate[faulted] + 1e-20), bins=30,
                alpha=0.7, label='Faulted', color='red')
        ax7.set_xlabel('log₁₀(Strain Rate) [s⁻¹]')
        ax7.set_ylabel('Frequency')
        ax7.set_title('Strain Rate: Faulted vs Unfaulted')
        ax7.legend()
        ax7.grid(True, alpha=0.3)

    # 8. Power dissipation in fault zones
    ax8 = plt.subplot(3, 3, 8)
    if power_term is not None and plstrain is not None:
        faulted = plstrain > 0.05
        if faulted.any():
            scatter = ax8.scatter(coords[faulted,0], coords[faulted,1],
                                c=np.log10(power_term[faulted] + 1),
                                s=30, cmap='plasma', vmin=6, vmax=10)
            plt.colorbar(scatter, ax=ax8, label='log₁₀(Power)')
            ax8.set_title('Power Dissipation in Fault Zones')
            ax8.set_xlabel('X (km)')
            ax8.set_ylabel('Z (km)')
            ax8.set_aspect('equal')
            ax8.grid(True, alpha=0.3)

    # 9. Summary statistics
    ax9 = plt.subplot(3, 3, 9)
    ax9.axis('off')

    stats_text = "FAULT DEVELOPMENT SUMMARY\n"
    stats_text += "=" * 45 + "\n\n"
    stats_text += f"Time: {time_yr/1000:.1f} kyr\n\n"

    if plstrain is not None:
        stats_text += f"Plastic Strain:\n"
        stats_text += f"  Max: {plstrain.max():.3f}\n"

        moderate = ((plstrain > 0.05) & (plstrain <= 0.2)).sum()
        active = ((plstrain > 0.2) & (plstrain <= 0.5)).sum()
        mature = (plstrain > 0.5).sum()
        total_faulted = (plstrain > 0.05).sum()

        stats_text += f"  Moderate (0.05-0.2): {moderate} ({100*moderate/n_points:.1f}%)\n"
        stats_text += f"  Active (0.2-0.5): {active} ({100*active/n_points:.1f}%)\n"
        stats_text += f"  Mature (>0.5): {mature} ({100*mature/n_points:.1f}%)\n"
        stats_text += f"  Total faulted: {total_faulted} ({100*total_faulted/n_points:.1f}%)\n\n"

        if total_faulted > 0:
            faulted_coords = coords[plstrain > 0.05]
            stats_text += f"Spatial Extent:\n"
            stats_text += f"  X: {faulted_coords[:,0].min():.1f} - {faulted_coords[:,0].max():.1f} km\n"
            stats_text += f"  Z: {faulted_coords[:,1].min():.1f} - {faulted_coords[:,1].max():.1f} km\n"
            stats_text += f"  Max depth: {abs(faulted_coords[:,1].min()):.1f} km\n\n"

    if material is not None and plstrain is not None:
        stats_text += "By Material:\n"
        for mat in np.unique(material):
            mat = int(mat)
            mask = material == mat
            faulted_mat = (mask & (plstrain > 0.05)).sum()
            pct = 100 * faulted_mat / mask.sum()
            mat_name = "Slab" if mat == 0 else "Wedge"
            stats_text += f"  Mat {mat} ({mat_name}): {faulted_mat}/{mask.sum()} ({pct:.1f}%)\n"
        stats_text += "\n"

    if temp is not None and plstrain is not None:
        faulted = plstrain > 0.05
        if faulted.any():
            brittle = (faulted & (temp < 723)).sum()
            ductile = (faulted & (temp >= 873)).sum()
            stats_text += "Deformation Style:\n"
            stats_text += f"  Brittle (<450°C): {brittle} ({100*brittle/faulted.sum():.1f}%)\n"
            stats_text += f"  Ductile (>600°C): {ductile} ({100*ductile/faulted.sum():.1f}%)\n"

    ax9.text(0.05, 0.95, stats_text, transform=ax9.transAxes,
            fontsize=9, verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

    plt.suptitle(f'Fault Development Analysis - t = {time_yr/1000:.1f} kyr',
                fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()

    # Save
    output_file = os.path.join(output_dir, 'fault_development.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✓ Saved: {output_file}")
    plt.close()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        vtk_dir = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else 'viz'
    else:
        vtk_dir = 'output/subduction_tonga_20251203_151418/vtk'
        output_dir = 'output/subduction_tonga_20251203_151418/viz'

    os.makedirs(output_dir, exist_ok=True)
    analyze_fault_development(vtk_dir, output_dir)
    print("✓ Fault development analysis complete!")
