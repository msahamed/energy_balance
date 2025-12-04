#!/usr/bin/env python3
"""
Plot field statistics from DynEarthSol VTK output
Generates overview plots of key simulation fields
"""

import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import sys
import os

def extract_scalar(lines, field_name, n_points):
    """Extract scalar field data from VTK file"""
    for i, line in enumerate(lines):
        if f'SCALARS {field_name}' in line:
            values = []
            start_idx = i + 2
            for j in range(start_idx, min(start_idx + n_points, len(lines))):
                try:
                    val = float(lines[j].strip())
                    values.append(val)
                except:
                    break
            return np.array(values)
    return None

def analyze_latest_frame(vtk_dir, output_dir):
    """Analyze latest VTK frame and generate plots"""

    # Find latest VTK file
    vtk_files = sorted([f for f in os.listdir(vtk_dir) if f.endswith('.vtk')])
    if not vtk_files:
        print("No VTK files found!")
        return

    latest = os.path.join(vtk_dir, vtk_files[-1])
    print(f"Analyzing: {vtk_files[-1]}")

    with open(latest, 'r') as f:
        lines = f.readlines()

    # Extract metadata
    time_match = re.search(r'time ([0-9.e+\-]+)', lines[1])
    time_sec = float(time_match.group(1))
    time_yr = time_sec / 3.15e7

    n_points = int(lines[4].split()[1])

    # Extract coordinates
    coords = []
    for i in range(5, 5 + n_points):
        x, z, y = map(float, lines[i].strip().split())
        coords.append([x/1000, z/1000])  # Convert to km
    coords = np.array(coords)

    # Extract fields
    temp = extract_scalar(lines, 'temperature', n_points)
    strain_rate = extract_scalar(lines, 'strain_rate', n_points)
    plastic_strain = extract_scalar(lines, 'plastic_strain', n_points)
    material = extract_scalar(lines, 'material_type', n_points)
    power = extract_scalar(lines, 'power', n_points)
    power_term = extract_scalar(lines, 'powerTerm', n_points)
    viscosity = extract_scalar(lines, 'viscosity', n_points)

    # Create figure with subplots
    fig = plt.figure(figsize=(16, 12))

    # 1. Temperature field
    ax1 = plt.subplot(3, 3, 1)
    if temp is not None:
        scatter = ax1.scatter(coords[:,0], coords[:,1], c=temp-273, s=10,
                            cmap='hot', vmin=0, vmax=1300)
        plt.colorbar(scatter, ax=ax1, label='Temperature (°C)')
        ax1.set_title(f'Temperature Field\nt = {time_yr/1000:.1f} kyr')
        ax1.set_xlabel('X (km)')
        ax1.set_ylabel('Z (km)')
        ax1.set_aspect('equal')

    # 2. Temperature histogram
    ax2 = plt.subplot(3, 3, 2)
    if temp is not None:
        ax2.hist(temp-273, bins=50, color='red', alpha=0.7, edgecolor='black')
        ax2.axvline((temp-273).mean(), color='blue', linestyle='--',
                   label=f'Mean: {(temp-273).mean():.0f}°C')
        ax2.set_xlabel('Temperature (°C)')
        ax2.set_ylabel('Frequency')
        ax2.set_title('Temperature Distribution')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

    # 3. Plastic strain field
    ax3 = plt.subplot(3, 3, 3)
    if plastic_strain is not None:
        scatter = ax3.scatter(coords[:,0], coords[:,1], c=plastic_strain,
                            s=10, cmap='YlOrRd', vmin=0, vmax=0.5)
        plt.colorbar(scatter, ax=ax3, label='Plastic Strain')
        ax3.set_title('Plastic Strain')
        ax3.set_xlabel('X (km)')
        ax3.set_ylabel('Z (km)')
        ax3.set_aspect('equal')

    # 4. Strain rate field (log scale)
    ax4 = plt.subplot(3, 3, 4)
    if strain_rate is not None:
        scatter = ax4.scatter(coords[:,0], coords[:,1],
                            c=np.log10(strain_rate + 1e-20),
                            s=10, cmap='viridis', vmin=-16, vmax=-12)
        plt.colorbar(scatter, ax=ax4, label='log₁₀(Strain Rate) [s⁻¹]')
        ax4.set_title('Strain Rate (log scale)')
        ax4.set_xlabel('X (km)')
        ax4.set_ylabel('Z (km)')
        ax4.set_aspect('equal')

    # 5. Strain rate histogram
    ax5 = plt.subplot(3, 3, 5)
    if strain_rate is not None:
        log_sr = np.log10(strain_rate + 1e-20)
        ax5.hist(log_sr, bins=50, color='purple', alpha=0.7, edgecolor='black')
        ax5.axvline(log_sr.mean(), color='red', linestyle='--',
                   label=f'Mean: 10^{log_sr.mean():.1f}')
        ax5.set_xlabel('log₁₀(Strain Rate) [s⁻¹]')
        ax5.set_ylabel('Frequency')
        ax5.set_title('Strain Rate Distribution')
        ax5.legend()
        ax5.grid(True, alpha=0.3)

    # 6. Power dissipation field (log scale)
    ax6 = plt.subplot(3, 3, 6)
    if power_term is not None:
        scatter = ax6.scatter(coords[:,0], coords[:,1],
                            c=np.log10(power_term + 1),
                            s=10, cmap='plasma', vmin=6, vmax=10)
        plt.colorbar(scatter, ax=ax6, label='log₁₀(Power Term)')
        ax6.set_title('Power Dissipation')
        ax6.set_xlabel('X (km)')
        ax6.set_ylabel('Z (km)')
        ax6.set_aspect('equal')

    # 7. Viscosity field (log scale)
    ax7 = plt.subplot(3, 3, 7)
    if viscosity is not None:
        scatter = ax7.scatter(coords[:,0], coords[:,1],
                            c=np.log10(viscosity + 1),
                            s=10, cmap='coolwarm', vmin=19, vmax=24)
        plt.colorbar(scatter, ax=ax7, label='log₁₀(Viscosity) [Pa·s]')
        ax7.set_title('Viscosity')
        ax7.set_xlabel('X (km)')
        ax7.set_ylabel('Z (km)')
        ax7.set_aspect('equal')

    # 8. Material distribution
    ax8 = plt.subplot(3, 3, 8)
    if material is not None:
        scatter = ax8.scatter(coords[:,0], coords[:,1], c=material,
                            s=10, cmap='tab10', vmin=0, vmax=2)
        plt.colorbar(scatter, ax=ax8, label='Material Type', ticks=[0, 1, 2])
        ax8.set_title('Material Distribution')
        ax8.set_xlabel('X (km)')
        ax8.set_ylabel('Z (km)')
        ax8.set_aspect('equal')

    # 9. Statistics summary text
    ax9 = plt.subplot(3, 3, 9)
    ax9.axis('off')

    stats_text = f"SIMULATION STATISTICS\n"
    stats_text += f"=" * 40 + "\n\n"
    stats_text += f"Time: {time_yr:.2e} yr ({time_yr/1000:.1f} kyr)\n"
    stats_text += f"Nodes: {n_points}\n\n"

    if temp is not None:
        stats_text += f"Temperature:\n"
        stats_text += f"  Range: {temp.min()-273:.0f} - {temp.max()-273:.0f} °C\n"
        stats_text += f"  Mean: {temp.mean()-273:.0f} °C\n\n"

    if plastic_strain is not None:
        faulted = (plastic_strain > 0.05).sum()
        stats_text += f"Plastic Strain:\n"
        stats_text += f"  Max: {plastic_strain.max():.3f}\n"
        stats_text += f"  Faulted (>0.05): {faulted} ({100*faulted/n_points:.1f}%)\n\n"

    if strain_rate is not None:
        stats_text += f"Strain Rate:\n"
        stats_text += f"  Range: {strain_rate.min():.2e} - {strain_rate.max():.2e} s⁻¹\n\n"

    if viscosity is not None:
        stats_text += f"Viscosity:\n"
        stats_text += f"  Range: 10^{np.log10(viscosity.min()):.1f} - 10^{np.log10(viscosity.max()):.1f} Pa·s\n"
        stats_text += f"  Contrast: {viscosity.max()/viscosity.min():.1e}×\n\n"

    if power_term is not None:
        stats_text += f"Power Dissipation:\n"
        stats_text += f"  Max: {power_term.max():.2e}\n"
        hotspots = (power_term > np.percentile(power_term, 95)).sum()
        stats_text += f"  Hotspots (top 5%): {hotspots}\n"

    ax9.text(0.05, 0.95, stats_text, transform=ax9.transAxes,
            fontsize=10, verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()

    # Save figure
    output_file = os.path.join(output_dir, 'field_statistics.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✓ Saved: {output_file}")
    plt.close()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        vtk_dir = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else 'viz'
    else:
        # Default paths
        vtk_dir = 'output/subduction_tonga_20251203_151418/vtk'
        output_dir = 'output/subduction_tonga_20251203_151418/viz'

    os.makedirs(output_dir, exist_ok=True)
    analyze_latest_frame(vtk_dir, output_dir)
    print(f"\n✓ Analysis complete!")
