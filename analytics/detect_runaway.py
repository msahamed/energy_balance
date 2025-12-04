#!/usr/bin/env python3
"""
Thermal Runaway Detection for DynEarthSol Simulations

Detects thermal runaway by analyzing:
1. Heating rate vs. cooling rate (Runaway Index)
2. Exponential strain rate acceleration
3. Temperature acceleration
4. Feedback strength

Usage:
    python detect_runaway.py <model_name>
    
Example:
    python detect_runaway.py energy
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys

try:
    import vtktools
except ImportError:
    print("Warning: vtktools not found. Using basic VTK reading.")
    import vtk
    from vtk.util.numpy_support import vtk_to_numpy

class RunawayDetector:
    """Detect thermal runaway in tectonic simulations"""
    
    def __init__(self, model_name):
        self.model_name = model_name
        self.output_dir = Path('.')
        self.results = []
        
    def load_vtk_files(self):
        """Load all VTK output files"""
        # Try .vtu first (unstructured grid XML format)
        vtk_files = sorted(self.output_dir.glob(f'{self.model_name}.*.vtu'))
        
        # If not found, try .vtk (legacy format)
        if not vtk_files:
            vtk_files = sorted(self.output_dir.glob(f'{self.model_name}_*.vtk'))
        
        # Also try without underscore
        if not vtk_files:
            vtk_files = sorted(self.output_dir.glob(f'{self.model_name}*.vtk'))
        
        if not vtk_files:
            print(f"No VTK files found for model '{self.model_name}'")
            print(f"Searched in: {self.output_dir.absolute()}")
            print(f"Patterns tried: {self.model_name}.*.vtu, {self.model_name}_*.vtk, {self.model_name}*.vtk")
            return []
        
        print(f"Found {len(vtk_files)} VTK files")
        return vtk_files
    
    def read_vtk_simple(self, filename):
        """Simple VTK reader using basic vtk library"""
        filename_str = str(filename)
        
        # Choose reader based on file extension
        if filename_str.endswith('.vtu'):
            reader = vtk.vtkXMLUnstructuredGridReader()
        elif filename_str.endswith('.vtk'):
            reader = vtk.vtkUnstructuredGridReader()
        else:
            raise ValueError(f"Unknown VTK format: {filename}")
        
        reader.SetFileName(filename_str)
        reader.Update()
        
        output = reader.GetOutput()
        point_data = output.GetPointData()
        cell_data = output.GetCellData()
        
        data = {}
        
        # Read point data
        for i in range(point_data.GetNumberOfArrays()):
            array_name = point_data.GetArrayName(i)
            array = vtk_to_numpy(point_data.GetArray(i))
            data[array_name] = array
        
        # Read cell data
        for i in range(cell_data.GetNumberOfArrays()):
            array_name = cell_data.GetArrayName(i)
            array = vtk_to_numpy(cell_data.GetArray(i))
            data[f'cell_{array_name}'] = array
        
        # Get coordinates
        points = output.GetPoints()
        coords = vtk_to_numpy(points.GetData())
        data['coordinates'] = coords
        
        return data
    
    def compute_runaway_index(self, data, time):
        """
        Compute runaway index = heating_rate / cooling_rate
        
        RI > 1.0 indicates thermal runaway
        """
        # Get power (shear heating rate) - W/m³
        if 'cell_power' in data:
            power = data['cell_power']
        elif 'power' in data:
            power = data['power']
        else:
            print("Warning: No power field found")
            return None, None, None
        
        # Get temperature
        if 'temperature' in data:
            temperature = data['temperature']
        else:
            print("Warning: No temperature field found")
            return None, None, None
        
        # Get coordinates for depth calculation
        coords = data['coordinates']
        depths = -coords[:, 2] if coords.shape[1] > 2 else -coords[:, 1]  # Depth is negative z
        
        # Compute heating rate (mean power)
        heating_rate = np.mean(np.abs(power))
        
        # Compute cooling rate (thermal diffusion)
        # Approximate: k * ∇²T ≈ k * ΔT / L²
        k = 3.3  # W/m/K (thermal conductivity)
        temp_gradient = np.gradient(temperature)
        temp_laplacian = np.mean(np.abs(temp_gradient))
        L_char = 10e3  # Characteristic length scale (10 km)
        cooling_rate = k * temp_laplacian / L_char
        
        # Runaway index
        if cooling_rate > 1e-10:  # Avoid division by zero
            runaway_index = heating_rate / cooling_rate
        else:
            runaway_index = np.inf
        
        return runaway_index, heating_rate, cooling_rate
    
    def compute_feedback_strength(self, data):
        """
        Compute thermal-mechanical feedback strength
        
        F = correlation(temperature, strain_rate)
        Strong positive correlation → Strong feedback
        """
        if 'temperature' not in data:
            return None
        
        temperature = data['temperature']
        
        # Get strain rate
        if 'cell_strain-rate' in data:
            strain_rate = data['cell_strain-rate']
            # Compute second invariant if tensor
            if len(strain_rate.shape) > 1:
                strain_rate_mag = np.sqrt(np.sum(strain_rate**2, axis=1))
            else:
                strain_rate_mag = np.abs(strain_rate)
        else:
            print("Warning: No strain-rate field found")
            return None
        
        # Interpolate temperature to cell centers (if needed)
        if len(temperature) != len(strain_rate_mag):
            # Simple averaging (assumes triangular elements)
            # This is approximate - better to use proper interpolation
            print("Warning: Temperature and strain-rate have different sizes")
            return None
        
        # Compute correlation
        if len(temperature) > 1 and len(strain_rate_mag) > 1:
            correlation = np.corrcoef(temperature, strain_rate_mag)[0, 1]
            return correlation
        else:
            return None
    
    def detect_exponential_acceleration(self, strain_rates, times):
        """
        Detect exponential acceleration in strain rate
        
        If log(strain_rate) increases linearly → Exponential growth → Runaway
        """
        if len(strain_rates) < 3:
            return False, 0.0
        
        # Fit linear trend to log(strain_rate)
        log_strain_rates = np.log10(strain_rates + 1e-20)  # Avoid log(0)
        
        # Linear fit
        coeffs = np.polyfit(times, log_strain_rates, 1)
        slope = coeffs[0]
        
        # Positive slope → Acceleration
        # Large slope → Exponential acceleration
        is_accelerating = slope > 0.1  # Threshold: 10x increase per unit time
        
        return is_accelerating, slope
    
    def analyze_simulation(self):
        """Main analysis routine"""
        vtk_files = self.load_vtk_files()
        if not vtk_files:
            return
        
        times = []
        runaway_indices = []
        heating_rates = []
        cooling_rates = []
        feedback_strengths = []
        max_temperatures = []
        mean_strain_rates = []
        
        print("\nAnalyzing thermal runaway...")
        print("-" * 80)
        print(f"{'Frame':<10} {'Time':<15} {'RI':<10} {'Heating':<15} {'Cooling':<15} {'Feedback':<10}")
        print("-" * 80)
        
        for i, vtk_file in enumerate(vtk_files):
            # Extract time from filename (assumes format: model.NNNNNN.vtu)
            frame_num = int(vtk_file.stem.split('.')[-1])
            time = frame_num  # Placeholder - extract from VTK if available
            
            # Read data
            try:
                data = self.read_vtk_simple(vtk_file)
            except Exception as e:
                print(f"Error reading {vtk_file}: {e}")
                continue
            
            # Compute runaway index
            ri, heating, cooling = self.compute_runaway_index(data, time)
            
            # Compute feedback strength
            feedback = self.compute_feedback_strength(data)
            
            # Track metrics
            if ri is not None:
                times.append(time)
                runaway_indices.append(ri)
                heating_rates.append(heating)
                cooling_rates.append(cooling)
                feedback_strengths.append(feedback if feedback is not None else 0.0)
                
                # Temperature stats
                if 'temperature' in data:
                    max_temperatures.append(np.max(data['temperature']))
                
                # Strain rate stats
                if 'cell_strain-rate' in data:
                    sr = data['cell_strain-rate']
                    if len(sr.shape) > 1:
                        sr_mag = np.sqrt(np.sum(sr**2, axis=1))
                    else:
                        sr_mag = np.abs(sr)
                    mean_strain_rates.append(np.mean(sr_mag))
                
                # Print status
                print(f"{frame_num:<10} {time:<15.2e} {ri:<10.3f} {heating:<15.3e} {cooling:<15.3e} {feedback if feedback else 0.0:<10.3f}")
        
        print("-" * 80)
        
        # Store results
        self.results = {
            'times': np.array(times),
            'runaway_indices': np.array(runaway_indices),
            'heating_rates': np.array(heating_rates),
            'cooling_rates': np.array(cooling_rates),
            'feedback_strengths': np.array(feedback_strengths),
            'max_temperatures': np.array(max_temperatures) if max_temperatures else None,
            'mean_strain_rates': np.array(mean_strain_rates) if mean_strain_rates else None,
        }
        
        return self.results
    
    def interpret_results(self):
        """Interpret runaway analysis results"""
        if not self.results:
            print("No results to interpret")
            return
        
        ri = self.results['runaway_indices']
        times = self.results['times']
        feedback = self.results['feedback_strengths']
        
        print("\n" + "=" * 80)
        print("THERMAL RUNAWAY ANALYSIS SUMMARY")
        print("=" * 80)
        
        # Check for runaway
        runaway_detected = np.any(ri > 1.0)
        
        if runaway_detected:
            runaway_times = times[ri > 1.0]
            runaway_ri = ri[ri > 1.0]
            
            print(f"\n⚠️  THERMAL RUNAWAY DETECTED!")
            print(f"   First occurrence: Frame {runaway_times[0]:.0f}")
            print(f"   Maximum RI: {np.max(runaway_ri):.3f}")
            print(f"   Duration: {len(runaway_times)} frames")
        else:
            print(f"\n✓  No thermal runaway detected (all RI < 1.0)")
            print(f"   Maximum RI: {np.max(ri):.3f}")
        
        # Feedback strength
        mean_feedback = np.mean(feedback)
        print(f"\nFeedback Strength:")
        print(f"   Mean correlation: {mean_feedback:.3f}")
        if mean_feedback > 0.5:
            print(f"   → Strong positive feedback (runaway likely)")
        elif mean_feedback > 0.2:
            print(f"   → Moderate feedback")
        else:
            print(f"   → Weak feedback (stable)")
        
        # Exponential acceleration check
        if self.results['mean_strain_rates'] is not None:
            is_accel, slope = self.detect_exponential_acceleration(
                self.results['mean_strain_rates'],
                times
            )
            print(f"\nStrain Rate Evolution:")
            print(f"   Exponential acceleration: {'YES' if is_accel else 'NO'}")
            print(f"   Growth rate: {slope:.3e} /frame")
        
        # Temperature evolution
        if self.results['max_temperatures'] is not None:
            temp_increase = np.max(self.results['max_temperatures']) - np.min(self.results['max_temperatures'])
            print(f"\nTemperature Evolution:")
            print(f"   Total increase: {temp_increase:.1f} K")
            print(f"   Max temperature: {np.max(self.results['max_temperatures']):.1f} K")
        
        print("\n" + "=" * 80)
    
    def plot_results(self):
        """Plot runaway analysis results"""
        if not self.results:
            print("No results to plot")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f'Thermal Runaway Analysis: {self.model_name}', fontsize=16, fontweight='bold')
        
        times = self.results['times']
        
        # Plot 1: Runaway Index
        ax = axes[0, 0]
        ax.plot(times, self.results['runaway_indices'], 'b-', linewidth=2, label='Runaway Index')
        ax.axhline(y=1.0, color='r', linestyle='--', linewidth=2, label='Runaway Threshold')
        ax.fill_between(times, 0, self.results['runaway_indices'], 
                        where=self.results['runaway_indices']>1.0, 
                        alpha=0.3, color='red', label='Runaway Zone')
        ax.set_xlabel('Frame', fontsize=12)
        ax.set_ylabel('Runaway Index (RI)', fontsize=12)
        ax.set_title('Heating Rate / Cooling Rate', fontsize=13, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_yscale('log')
        
        # Plot 2: Heating vs Cooling
        ax = axes[0, 1]
        ax.plot(times, self.results['heating_rates'], 'r-', linewidth=2, label='Heating Rate')
        ax.plot(times, self.results['cooling_rates'], 'b-', linewidth=2, label='Cooling Rate')
        ax.set_xlabel('Frame', fontsize=12)
        ax.set_ylabel('Power Density (W/m³)', fontsize=12)
        ax.set_title('Energy Balance Components', fontsize=13, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_yscale('log')
        
        # Plot 3: Feedback Strength
        ax = axes[1, 0]
        ax.plot(times, self.results['feedback_strengths'], 'g-', linewidth=2)
        ax.axhline(y=0.5, color='orange', linestyle='--', linewidth=1, label='Strong Feedback')
        ax.set_xlabel('Frame', fontsize=12)
        ax.set_ylabel('Correlation(T, ε̇)', fontsize=12)
        ax.set_title('Thermal-Mechanical Feedback', fontsize=13, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim([-1, 1])
        
        # Plot 4: Temperature Evolution
        ax = axes[1, 1]
        if self.results['max_temperatures'] is not None:
            ax.plot(times, self.results['max_temperatures'], 'r-', linewidth=2, label='Max Temperature')
            ax.set_ylabel('Temperature (K)', fontsize=12, color='r')
            ax.tick_params(axis='y', labelcolor='r')
        
        if self.results['mean_strain_rates'] is not None:
            ax2 = ax.twinx()
            ax2.semilogy(times, self.results['mean_strain_rates'], 'b-', linewidth=2, label='Mean Strain Rate')
            ax2.set_ylabel('Strain Rate (1/s)', fontsize=12, color='b')
            ax2.tick_params(axis='y', labelcolor='b')
        
        ax.set_xlabel('Frame', fontsize=12)
        ax.set_title('Temperature & Strain Rate Evolution', fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save figure
        output_file = f'{self.model_name}_runaway_analysis.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"\nPlot saved to: {output_file}")
        
        plt.show()


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python detect_runaway.py <model_name>")
        print("Example: python detect_runaway.py energy")
        sys.exit(1)
    
    model_name = sys.argv[1]
    
    print(f"\n{'='*80}")
    print(f"THERMAL RUNAWAY DETECTOR")
    print(f"Model: {model_name}")
    print(f"{'='*80}\n")
    
    detector = RunawayDetector(model_name)
    detector.analyze_simulation()
    detector.interpret_results()
    detector.plot_results()


if __name__ == '__main__':
    main()
