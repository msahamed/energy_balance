#!/usr/bin/env python3
"""
DynEarthSol VTK Analysis Tool

Analyzes VTK output files from DynEarthSol simulations and generates
comprehensive visualizations. Supports single or multiple experiments
for comparison.

Usage:
    python analyze_results.py experiment1 [experiment2 ...]
    
Example:
    python analyze_results.py energy no_energy
"""

import os
import sys
import glob
import argparse
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class VTKParser:
    """Parse ASCII VTK files from DynEarthSol."""
    
    @staticmethod
    def read_vtk(filename: str) -> Dict[str, np.ndarray]:
        """Read a VTK file and extract all scalar and vector fields."""
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f.readlines()]
        
        data = {}
        
        def find_section(keyword: str) -> int:
            """Find line index containing keyword."""
            for i, line in enumerate(lines):
                if keyword in line:
                    return i
            return -1
        
        # Extract time from comment (format: "DynEarthSol output, frame X, time Y years")
        for line in lines[:10]:
            if 'time' in line.lower() and 'years' in line.lower():
                parts = line.split()
                for i, part in enumerate(parts):
                    if part.lower() == 'time' and i + 1 < len(parts):
                        try:
                            data['time'] = float(parts[i + 1])
                            break
                        except ValueError:
                            pass
                if 'time' in data:
                    break
        
        # If time not found, try to extract from filename
        if 'time' not in data:
            # Filename format: modelname_XXXXXX.vtk where XXXXXX is frame number
            import re
            match = re.search(r'_(\d{6})\.vtk$', filename)
            if match:
                data['time'] = float(match.group(1))  # Use frame number as proxy
        
        # Read all SCALARS fields
        i = 0
        while i < len(lines):
            if lines[i].startswith('SCALARS'):
                parts = lines[i].split()
                if len(parts) >= 2:
                    field_name = parts[1]
                    # Skip LOOKUP_TABLE line
                    i += 2
                    values = []
                    while i < len(lines) and not lines[i].startswith(('SCALARS', 'VECTORS', 'POINT_DATA', 'CELL_DATA')):
                        line = lines[i].strip()
                        if line and not line[0].isalpha():
                            try:
                                val = float(line)
                                values.append(val)
                            except ValueError:
                                pass
                        i += 1
                    if values:
                        data[field_name] = np.array(values)
                    continue
            
            # Read VECTORS fields
            if lines[i].startswith('VECTORS'):
                parts = lines[i].split()
                if len(parts) >= 2:
                    field_name = parts[1]
                    i += 1
                    vectors = []
                    while i < len(lines) and not lines[i].startswith(('SCALARS', 'VECTORS', 'POINT_DATA', 'CELL_DATA')):
                        line = lines[i].strip()
                        if line and not line[0].isalpha():
                            try:
                                vec = list(map(float, line.split()))
                                if len(vec) >= 2:  # At least 2D vector
                                    vectors.append(vec)
                            except ValueError:
                                pass
                        i += 1
                    if vectors:
                        data[field_name] = np.array(vectors)
                    continue
            
            i += 1
        
        return data


class ExperimentAnalyzer:
    """Analyze a single experiment's VTK files."""
    
    def __init__(self, experiment_name: str, output_base: str = "output"):
        self.name = experiment_name
        self.output_base = output_base
        self.run_dir = self._find_run_directory()
        self.vtk_files = self._get_vtk_files()
        self.data = {}
    
    def _find_run_directory(self) -> Optional[Path]:
        """Find the run directory - supports both experiment names and direct paths."""
        # Check if it's a direct path to an existing directory
        direct_path = Path(self.name)
        if direct_path.exists() and direct_path.is_dir():
            # Extract experiment name from directory name
            dir_name = direct_path.name
            # Remove timestamp suffix if present (format: name_YYYYMMDD_HHMMSS)
            import re
            match = re.match(r'(.+?)_\d{8}_\d{6}$', dir_name)
            if match:
                self.name = match.group(1)
            else:
                self.name = dir_name
            return direct_path
        
        # Check if it's a path relative to output_base
        rel_path = Path(self.output_base) / self.name
        if rel_path.exists() and rel_path.is_dir():
            return rel_path
        
        # Try to find latest timestamped directory for this experiment name
        pattern = os.path.join(self.output_base, f"{self.name}_*")
        dirs = sorted(glob.glob(pattern))
        if not dirs:
            print(f"Warning: No output directory found for '{self.name}'")
            return None
        return Path(dirs[-1])
    
    def _get_vtk_files(self) -> List[Path]:
        """Get sorted list of VTK files."""
        if not self.run_dir:
            return []
        vtk_dir = self.run_dir / "vtk"
        if not vtk_dir.exists():
            print(f"Warning: No vtk directory in {self.run_dir}")
            return []
        files = sorted(vtk_dir.glob("*.vtk"))
        if not files:
            print(f"Warning: No VTK files found in {vtk_dir}")
        return files
    
    def analyze(self) -> Dict[str, np.ndarray]:
        """Analyze all VTK files and extract time series data."""
        if not self.vtk_files:
            print(f"Warning: No VTK files found for '{self.name}'")
            return {}
        
        print(f"Analyzing {len(self.vtk_files)} VTK files for '{self.name}'...")
        
        # Initialize storage
        time_series = {'time': []}
        
        for vtk_file in self.vtk_files:
            frame_data = VTKParser.read_vtk(str(vtk_file))
            
            # Store time
            if 'time' in frame_data:
                time_series['time'].append(frame_data['time'])
            
            # Process each field
            for field_name, field_data in frame_data.items():
                if field_name == 'time':
                    continue
                
                # Initialize field storage if needed
                if field_name not in time_series:
                    time_series[field_name] = {
                        'max': [],
                        'min': [],
                        'mean': [],
                        'std': []
                    }
                
                # Compute statistics
                if len(field_data.shape) == 1:  # Scalar field
                    time_series[field_name]['max'].append(np.max(field_data))
                    time_series[field_name]['min'].append(np.min(field_data))
                    time_series[field_name]['mean'].append(np.mean(field_data))
                    time_series[field_name]['std'].append(np.std(field_data))
                elif len(field_data.shape) == 2:  # Vector field
                    magnitude = np.linalg.norm(field_data, axis=1)
                    time_series[field_name]['max'].append(np.max(magnitude))
                    time_series[field_name]['min'].append(np.min(magnitude))
                    time_series[field_name]['mean'].append(np.mean(magnitude))
                    time_series[field_name]['std'].append(np.std(magnitude))
        
        # Convert lists to arrays
        for field_name in time_series:
            if field_name == 'time':
                time_series[field_name] = np.array(time_series[field_name])
            else:
                for stat in time_series[field_name]:
                    time_series[field_name][stat] = np.array(time_series[field_name][stat])
        
        self.data = time_series
        return time_series


class Visualizer:
    """Generate visualizations for experiment data."""
    
    def __init__(self, experiments: List[ExperimentAnalyzer]):
        self.experiments = experiments
        
    def create_viz_dir(self, experiment: ExperimentAnalyzer) -> Path:
        """Create viz directory for an experiment."""
        if not experiment.run_dir:
            return Path(".")
        viz_dir = experiment.run_dir / "viz"
        viz_dir.mkdir(exist_ok=True)
        return viz_dir
    
    def plot_single_experiment(self, experiment: ExperimentAnalyzer):
        """Generate comprehensive plots for a single experiment."""
        if not experiment.data:
            return
        
        viz_dir = self.create_viz_dir(experiment)
        time = experiment.data.get('time', [])
        
        # Plot temperature evolution
        if 'temperature' in experiment.data:
            self._plot_field_evolution(
                time, experiment.data['temperature'],
                'Temperature', 'K',
                viz_dir / 'temperature_evolution.png',
                experiment.name
            )
        
        # Plot velocity evolution
        if 'velocity' in experiment.data:
            self._plot_field_evolution(
                time, experiment.data['velocity'],
                'Velocity', 'm/s',
                viz_dir / 'velocity_evolution.png',
                experiment.name,
                log_scale=True
            )
        
        # Plot energy terms if available
        energy_fields = ['power', 'tenergy', 'venergy', 'denergy']
        available_energy = [f for f in energy_fields if f in experiment.data]
        
        if available_energy:
            self._plot_energy_terms(
                time, experiment.data, available_energy,
                viz_dir / 'energy_terms.png',
                experiment.name
            )
        
        # Plot pressure and stress
        if 'pressure' in experiment.data:
            self._plot_field_evolution(
                time, experiment.data['pressure'],
                'Pressure', 'Pa',
                viz_dir / 'pressure_evolution.png',
                experiment.name
            )
        
        print(f"✓ Saved visualizations to {viz_dir}")
    
    def plot_comparison(self, experiments: List[ExperimentAnalyzer]):
        """Generate comparison plots for multiple experiments."""
        if len(experiments) < 2:
            return
        
        # Use first experiment's viz dir for comparisons
        viz_dir = self.create_viz_dir(experiments[0])
        
        # Compare temperature
        self._compare_field(
            experiments, 'temperature',
            'Temperature Comparison', 'K',
            viz_dir / 'comparison_temperature.png'
        )
        
        # Compare velocity
        self._compare_field(
            experiments, 'velocity',
            'Velocity Comparison', 'm/s',
            viz_dir / 'comparison_velocity.png',
            log_scale=True
        )
        
        # Temperature difference
        if len(experiments) == 2:
            self._plot_difference(
                experiments[0], experiments[1], 'temperature',
                viz_dir / 'temperature_difference.png'
            )
        
        print(f"✓ Saved comparison plots to {viz_dir}")
    
    def _plot_field_evolution(self, time, field_data, field_name, units,
                               output_path, exp_name, log_scale=False):
        """Plot field evolution over time."""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Max/Min plot
        ax1.plot(time, field_data['max'], 'r-', label='Max', linewidth=2)
        ax1.plot(time, field_data['min'], 'b-', label='Min', linewidth=2)
        ax1.fill_between(time, field_data['min'], field_data['max'], alpha=0.3)
        ax1.set_ylabel(f'{field_name} ({units})')
        ax1.set_title(f'{field_name} Range - {exp_name}')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        if log_scale:
            ax1.set_yscale('log')
        
        # Mean ± std plot
        mean = field_data['mean']
        std = field_data['std']
        ax2.plot(time, mean, 'g-', label='Mean', linewidth=2)
        ax2.fill_between(time, mean - std, mean + std, alpha=0.3, label='±1σ')
        ax2.set_xlabel('Time (years)')
        ax2.set_ylabel(f'{field_name} ({units})')
        ax2.set_title(f'{field_name} Mean ± Std Dev')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        if log_scale:
            ax2.set_yscale('log')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.close()
    
    def _plot_energy_terms(self, time, data, energy_fields, output_path, exp_name):
        """Plot energy balance terms."""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes = axes.flatten()
        
        for idx, field in enumerate(energy_fields):
            if idx >= 4:
                break
            ax = axes[idx]
            field_data = data[field]
            ax.plot(time, field_data['mean'], linewidth=2)
            ax.fill_between(time, 
                           field_data['mean'] - field_data['std'],
                           field_data['mean'] + field_data['std'],
                           alpha=0.3)
            ax.set_xlabel('Time (years)')
            ax.set_ylabel(f'{field} (mean ± std)')
            ax.set_title(f'{field.capitalize()}')
            ax.grid(True, alpha=0.3)
        
        plt.suptitle(f'Energy Balance Terms - {exp_name}', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.close()
    
    def _compare_field(self, experiments, field_name, title, units,
                       output_path, log_scale=False):
        """Compare a field across multiple experiments."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        for exp in experiments:
            if field_name not in exp.data:
                continue
            time = exp.data['time']
            field_data = exp.data[field_name]
            
            # Max values
            ax1.plot(time, field_data['max'], label=exp.name, linewidth=2)
            
            # Mean values
            ax2.plot(time, field_data['mean'], label=exp.name, linewidth=2)
        
        ax1.set_xlabel('Time (years)')
        ax1.set_ylabel(f'Max {field_name} ({units})')
        ax1.set_title(f'Maximum {field_name}')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        if log_scale:
            ax1.set_yscale('log')
        
        ax2.set_xlabel('Time (years)')
        ax2.set_ylabel(f'Mean {field_name} ({units})')
        ax2.set_title(f'Mean {field_name}')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        if log_scale:
            ax2.set_yscale('log')
        
        plt.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.close()
    
    def _plot_difference(self, exp1, exp2, field_name, output_path):
        """Plot difference between two experiments."""
        if field_name not in exp1.data or field_name not in exp2.data:
            return
        
        time1 = exp1.data['time']
        time2 = exp2.data['time']
        
        # Interpolate to common time points
        min_len = min(len(time1), len(time2))
        time = time1[:min_len]
        
        diff_max = exp1.data[field_name]['max'][:min_len] - exp2.data[field_name]['max'][:min_len]
        diff_mean = exp1.data[field_name]['mean'][:min_len] - exp2.data[field_name]['mean'][:min_len]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        ax1.plot(time, diff_max, 'r-', linewidth=2)
        ax1.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        ax1.set_ylabel(f'Δ Max {field_name}')
        ax1.set_title(f'Difference: {exp1.name} - {exp2.name}')
        ax1.grid(True, alpha=0.3)
        
        ax2.plot(time, diff_mean, 'b-', linewidth=2)
        ax2.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        ax2.set_xlabel('Time (years)')
        ax2.set_ylabel(f'Δ Mean {field_name}')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.close()


def main():
    parser = argparse.ArgumentParser(
        description='Analyze DynEarthSol VTK output files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s energy                              # Analyze latest 'energy' experiment
  %(prog)s energy no_energy                    # Compare two experiments (auto-finds latest)
  %(prog)s output/energy_20251201_120546       # Analyze specific directory
  %(prog)s energy_20251201_120546 no_energy_*  # Mix names and paths
        """
    )
    parser.add_argument('experiments', nargs='+', 
                       help='Experiment names or directory paths (supports both)')
    parser.add_argument('--output-dir', default='output',
                       help='Base output directory (default: output)')
    
    args = parser.parse_args()
    
    # Analyze experiments
    experiments = []
    for exp_name in args.experiments:
        analyzer = ExperimentAnalyzer(exp_name, args.output_dir)
        analyzer.analyze()
        if analyzer.data:
            experiments.append(analyzer)
    
    if not experiments:
        print("Error: No valid experiments found!")
        return 1
    
    # Generate visualizations
    visualizer = Visualizer(experiments)
    
    # Individual experiment plots
    for exp in experiments:
        visualizer.plot_single_experiment(exp)
    
    # Comparison plots if multiple experiments
    if len(experiments) > 1:
        visualizer.plot_comparison(experiments)
    
    print(f"\n✓ Analysis complete for {len(experiments)} experiment(s)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
