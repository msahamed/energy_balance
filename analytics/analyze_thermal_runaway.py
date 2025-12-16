#!/usr/bin/env python3
"""
Thermal Runaway Analysis for DynEarthSol Subduction Simulations

Analyzes VTK output to detect early signs of thermal runaway in the slab interface.

Usage:
    python3 analyze_thermal_runaway.py <vtk_file>

Example:
    python3 analyze_thermal_runaway.py ../output/subduction_tonga_mmg_v2/vtk/subduction_tonga_mmg_v2_000995.vtk
"""

import sys
import re
import math

def read_vtk_file(filename):
    """Read VTK file and extract scalar fields."""
    with open(filename, 'r') as f:
        lines = f.readlines()

    # Extract simulation time
    time_years = 0
    for line in lines[:10]:
        if 'frame' in line:
            match = re.search(r'time\s+([\d.e+-]+)', line)
            if match:
                time_sec = float(match.group(1))
                time_years = time_sec / 3.15576e7

    # Find number of points and field locations
    num_points = 0
    field_lines = {}

    for i, line in enumerate(lines):
        if line.startswith('POINTS'):
            num_points = int(line.split()[1])
        elif line.startswith('SCALARS'):
            field_name = line.split()[1]
            field_lines[field_name] = i

    # Extract data
    def extract_field(field_name):
        if field_name not in field_lines:
            return []
        start = field_lines[field_name] + 2
        data = []
        for i in range(start, min(start + num_points, len(lines))):
            try:
                data.append(float(lines[i].strip()))
            except:
                break
        return data

    return {
        'time_years': time_years,
        'num_points': num_points,
        'temperature': extract_field('temperature'),
        'plastic_strain': extract_field('plastic_strain'),
        'power': extract_field('power'),
        'powerTerm': extract_field('powerTerm'),
        'strain_rate': extract_field('strain_rate')
    }

def analyze_thermal_runaway(data, strain_threshold=0.3):
    """Analyze thermal runaway indicators."""

    time_years = data['time_years']
    temperatures = data['temperature']
    strains = data['plastic_strain']
    powers = data['power']
    power_terms = data['powerTerm']

    # Constants
    COLD_SLAB_400C = 673  # K
    COLD_SLAB_500C = 773  # K
    RUNAWAY_THRESHOLD = 973  # K (700°C)

    print("=" * 70)
    print("THERMAL RUNAWAY ANALYSIS")
    print("=" * 70)
    print(f"\nSimulation Time: {time_years:.0f} years ({time_years/1e6:.3f} My)")
    print(f"Progress: {time_years/2e6*100:.1f}% toward 2 My target")
    print()

    # Overall temperature
    print("=" * 70)
    print("1. OVERALL TEMPERATURE FIELD")
    print("=" * 70)
    if temperatures:
        print(f"Nodes: {len(temperatures)}")
        print(f"Min: {min(temperatures):.1f} K ({min(temperatures)-273.15:.1f}°C)")
        print(f"Max: {max(temperatures):.1f} K ({max(temperatures)-273.15:.1f}°C)")
        print(f"Mean: {sum(temperatures)/len(temperatures):.1f} K ({sum(temperatures)/len(temperatures)-273.15:.1f}°C)")
    print()

    # Temperature by deformation zone
    print("=" * 70)
    print("2. TEMPERATURE BY DEFORMATION INTENSITY")
    print("=" * 70)

    if strains and temperatures and len(strains) == len(temperatures):
        zones = [
            (f"Interface (strain > {strain_threshold})", lambda s: s > strain_threshold),
            ("High strain (0.1-0.3)", lambda s: 0.1 <= s <= 0.3),
            ("Moderate strain (0.05-0.1)", lambda s: 0.05 <= s < 0.1),
            ("Background (strain < 0.05)", lambda s: s < 0.05)
        ]

        for zone_name, condition in zones:
            zone_temps = [temperatures[i] for i in range(len(strains)) if condition(strains[i])]
            zone_powers = [powers[i] for i in range(len(strains)) if condition(strains[i])] if powers else []
            zone_pterm = [power_terms[i] for i in range(len(strains)) if condition(strains[i])] if power_terms else []

            if zone_temps:
                mean_t = sum(zone_temps) / len(zone_temps)
                max_t = max(zone_temps)

                print(f"\n{zone_name}:")
                print(f"  Nodes: {len(zone_temps)}")
                print(f"  Mean T: {mean_t:.1f} K ({mean_t-273.15:.1f}°C)")
                print(f"  Max T: {max_t:.1f} K ({max_t-273.15:.1f}°C)")
                if zone_powers:
                    print(f"  Total power: {sum(zone_powers):.2e} W/m³")
                if zone_pterm:
                    print(f"  Max accumulated: {max(zone_pterm):.2e} J/m³")

    print()
    print("=" * 70)
    print("3. SLAB INTERFACE DETAILED ANALYSIS")
    print("=" * 70)

    interface_temps = [temperatures[i] for i in range(len(strains)) if strains[i] > strain_threshold]
    interface_strains = [strains[i] for i in range(len(strains)) if strains[i] > strain_threshold]
    interface_powers = [powers[i] for i in range(len(strains)) if strains[i] > strain_threshold] if powers else []
    interface_pterm = [power_terms[i] for i in range(len(strains)) if strains[i] > strain_threshold] if power_terms else []

    if interface_temps:
        print(f"\nInterface nodes (plastic_strain > {strain_threshold}): {len(interface_temps)}")
        print(f"Plastic strain: {min(interface_strains):.3f} - {max(interface_strains):.3f}")

        print(f"\nTemperature:")
        print(f"  Min: {min(interface_temps):.1f} K ({min(interface_temps)-273.15:.1f}°C)")
        print(f"  Max: {max(interface_temps):.1f} K ({max(interface_temps)-273.15:.1f}°C)")
        print(f"  Mean: {sum(interface_temps)/len(interface_temps):.1f} K ({sum(interface_temps)/len(interface_temps)-273.15:.1f}°C)")

        if interface_pterm:
            print(f"\nAccumulated shear heating:")
            print(f"  Max: {max(interface_pterm):.2e} J/m³")
            print(f"  Total: {sum(interface_pterm):.2e} J/m³")
    else:
        high_strain = [s for s in strains if s > 0.1]
        print(f"\n⚠️  Only {len(high_strain)} nodes with strain > 0.1")
        print(f"    Consider lowering threshold (current: {strain_threshold})")

    print()
    print("=" * 70)
    print("4. THERMAL RUNAWAY INDICATORS")
    print("=" * 70)

    score = 0

    if interface_temps:
        mean_interface = sum(interface_temps) / len(interface_temps)
        max_interface = max(interface_temps)

        print(f"\nCurrent interface state:")
        print(f"  Mean: {mean_interface-273.15:.1f}°C")
        print(f"  Peak: {max_interface-273.15:.1f}°C")
        print(f"  vs. cold slab 400°C: {mean_interface-COLD_SLAB_400C:+.1f} K")

        print(f"\nIndicators:")

        if mean_interface > COLD_SLAB_400C:
            score += 1
            print(f"  ✓ Warmer than cold slab (+{mean_interface-COLD_SLAB_400C:.1f} K)")
        else:
            print(f"  ✗ Cooler than cold slab ({COLD_SLAB_400C-mean_interface:.1f} K)")

        if max_interface > COLD_SLAB_500C:
            score += 1
            print(f"  ✓ Peak > 500°C ({max_interface-273.15:.1f}°C)")
        else:
            print(f"  ✗ Peak < 500°C ({max_interface-273.15:.1f}°C)")

        if max_interface > RUNAWAY_THRESHOLD:
            score += 1
            print(f"  ✓ Strong heating > 700°C")
        else:
            print(f"  ✗ Below 700°C threshold")

        if interface_pterm and sum(interface_pterm) > 1e9:
            score += 1
            print(f"  ✓ Significant heat accumulation")
        else:
            print(f"  ✗ Low heat accumulation")

        print(f"\nRunaway Score: {score}/4")

        if score >= 3:
            print("Status: 🔥 STRONG runaway developing")
        elif score >= 2:
            print("Status: ⚠️  MODERATE heating")
        elif score >= 1:
            print("Status: ℹ️  WEAK heating")
        else:
            print("Status: ❄️  NO runaway")

    print()
    print("=" * 70)
    print("5. EXTRAPOLATION TO 2 MY")
    print("=" * 70)

    if interface_temps and time_years > 0:
        current_my = time_years / 1e6
        target_my = 2.0

        mean_interface = sum(interface_temps) / len(interface_temps)
        temp_excess = mean_interface - COLD_SLAB_400C

        if temp_excess > 0:
            heating_rate = temp_excess / current_my
            linear_pred = COLD_SLAB_400C + heating_rate * target_my

            print(f"\nLinear extrapolation:")
            print(f"  Heating rate: {heating_rate:.0f} K/My")
            print(f"  Predicted at 2 My: {linear_pred:.0f} K ({linear_pred-273.15:.0f}°C)")

            # Exponential with feedback
            k = 0.5  # growth rate /My
            if current_my > 0.01:
                A = temp_excess / (math.exp(k * current_my) - 1)
                nonlin_excess = A * (math.exp(k * target_my) - 1)
                nonlin_pred = COLD_SLAB_400C + nonlin_excess

                print(f"\nWith thermal feedback (k=0.5/My):")
                print(f"  Predicted at 2 My: {nonlin_pred:.0f} K ({nonlin_pred-273.15:.0f}°C)")

            print(f"\n{'='*70}")
            if linear_pred > RUNAWAY_THRESHOLD:
                print("🔥 PREDICTION: Strong runaway expected by 2 My")
                print(f"   Interface: {linear_pred-273.15:.0f}°C")
                print("   → Viscosity reduction 10-100x")
                print("   → Deep earthquakes likely")
            elif linear_pred > COLD_SLAB_500C:
                print("⚠️  PREDICTION: Moderate heating by 2 My")
                print(f"   Interface: {linear_pred-273.15:.0f}°C")
            else:
                print("ℹ️  PREDICTION: Weak heating by 2 My")
        else:
            print("\n⚠️  Interface cooler than reference - too early to predict")

    print()
    print("=" * 70)
    print("RECOMMENDATION")
    print("=" * 70)

    if interface_temps and sum(interface_temps)/len(interface_temps) > COLD_SLAB_400C:
        print("\n✅ Continue simulation - thermal signal developing")
        print("   Check again at ~0.5 My for trend confirmation")
    else:
        print("\n⏸️  Signal weak - check at 0.5 My before full 2 My run")

    print()

    return score

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nError: No VTK file specified")
        print("\nUsage: python3 analyze_thermal_runaway.py <vtk_file>")
        sys.exit(1)

    vtk_file = sys.argv[1]

    try:
        data = read_vtk_file(vtk_file)
        score = analyze_thermal_runaway(data)
        sys.exit(0)
    except FileNotFoundError:
        print(f"Error: File not found: {vtk_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
