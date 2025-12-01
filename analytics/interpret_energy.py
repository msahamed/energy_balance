#!/usr/bin/env python3
"""
Energy Balance Geological Interpretation Tool

Analyzes the geological significance of energy balance terms in DynEarthSol simulations.
Provides insights into deformation mechanisms, heat generation, and thermal evolution.

Usage:
    python interpret_energy.py experiment_name
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from analyze_results import ExperimentAnalyzer, VTKParser


class EnergyInterpreter:
    """Interpret energy balance terms in geological context."""
    
    def __init__(self, experiment: ExperimentAnalyzer):
        self.experiment = experiment
        self.data = experiment.data
        
    def analyze_power_contributions(self):
        """Analyze the relative contributions of different power terms."""
        if not all(k in self.data for k in ['tenergy', 'venergy', 'denergy']):
            print("Warning: Not all energy terms available")
            return None
        
        time = self.data['time']
        
        # Get mean values
        thermal_power = self.data['tenergy']['mean']
        viscous_power = self.data['venergy']['mean']
        plastic_power = self.data['denergy']['mean']  # denergy = dissipative/plastic power
        
        # Calculate total and percentages
        total_power = thermal_power + viscous_power + plastic_power
        
        # Avoid division by zero
        total_power_safe = np.where(np.abs(total_power) > 1e-20, total_power, 1.0)
        
        thermal_pct = 100 * thermal_power / total_power_safe
        viscous_pct = 100 * viscous_power / total_power_safe
        plastic_pct = 100 * plastic_power / total_power_safe
        
        return {
            'time': time,
            'thermal_power': thermal_power,
            'viscous_power': viscous_power,
            'plastic_power': plastic_power,
            'total_power': total_power,
            'thermal_pct': thermal_pct,
            'viscous_pct': viscous_pct,
            'plastic_pct': plastic_pct
        }
    
    def interpret_deformation_regime(self, power_data):
        """Interpret the dominant deformation mechanism."""
        if power_data is None:
            return None
        
        # Use the last 20% of simulation for steady-state analysis
        n = len(power_data['time'])
        start_idx = int(0.8 * n)
        
        avg_viscous = np.mean(np.abs(power_data['viscous_pct'][start_idx:]))
        avg_plastic = np.mean(np.abs(power_data['plastic_pct'][start_idx:]))
        avg_thermal = np.mean(np.abs(power_data['thermal_pct'][start_idx:]))
        
        regime = {
            'viscous': avg_viscous,
            'plastic': avg_plastic,
            'thermal': avg_thermal
        }
        
        dominant = max(regime, key=regime.get)
        
        interpretations = {
            'viscous': "Viscous-dominated: Ductile flow, slow deformation, typical of lower crust/mantle",
            'plastic': "Plastic-dominated: Brittle failure, faulting, typical of upper crust",
            'thermal': "Thermally-dominated: Thermal expansion/contraction effects significant"
        }
        
        return {
            'regime': regime,
            'dominant': dominant,
            'interpretation': interpretations[dominant]
        }
    
    def calculate_thermal_impact(self):
        """Calculate the thermal impact of mechanical work."""
        if 'temperature' not in self.data or 'power' not in self.data:
            return None
        
        time = self.data['time']
        temp_mean = self.data['temperature']['mean']
        temp_max = self.data['temperature']['max']
        power_mean = self.data['power']['mean']
        
        # Calculate temperature change rate
        if len(time) > 1:
            dt = np.diff(time)
            dT_mean = np.diff(temp_mean)
            dT_max = np.diff(temp_max)
            
            # Heating rate (K/year)
            heating_rate_mean = dT_mean / dt
            heating_rate_max = dT_max / dt
            
            return {
                'time': time[1:],
                'heating_rate_mean': heating_rate_mean,
                'heating_rate_max': heating_rate_max,
                'power_mean': power_mean[1:],
                'temp_increase': temp_mean[-1] - temp_mean[0],
                'max_temp_increase': temp_max[-1] - temp_max[0]
            }
        return None
    
    def geological_summary(self):
        """Generate a geological interpretation summary."""
        power_data = self.analyze_power_contributions()
        regime = self.interpret_deformation_regime(power_data)
        thermal = self.calculate_thermal_impact()
        
        print("\n" + "="*70)
        print(f"GEOLOGICAL INTERPRETATION: {self.experiment.name}")
        print("="*70)
        
        if regime:
            print("\n1. DEFORMATION REGIME (Late-stage steady state):")
            print(f"   Dominant mechanism: {regime['dominant'].upper()}")
            print(f"   {regime['interpretation']}")
            print(f"\n   Power distribution:")
            print(f"   - Viscous:  {regime['regime']['viscous']:.1f}%")
            print(f"   - Plastic:  {regime['regime']['plastic']:.1f}%")
            print(f"   - Thermal:  {regime['regime']['thermal']:.1f}%")
        
        if thermal:
            print(f"\n2. THERMAL EVOLUTION:")
            print(f"   Total temperature increase (mean): {thermal['temp_increase']:.2f} K")
            print(f"   Total temperature increase (max):  {thermal['max_temp_increase']:.2f} K")
            print(f"   Average heating rate: {np.mean(thermal['heating_rate_mean']):.2e} K/year")
            
            if thermal['temp_increase'] > 10:
                print(f"   ⚠ Significant shear heating detected!")
                print(f"   → May affect rheology and deformation patterns")
        
        if power_data:
            print(f"\n3. ENERGY BUDGET:")
            total_avg = np.mean(np.abs(power_data['total_power']))
            print(f"   Average total power density: {total_avg:.2e} W/m³")
            
            # Geological context
            if total_avg > 1e-6:
                print(f"   → High power dissipation: Active deformation zone")
            elif total_avg > 1e-9:
                print(f"   → Moderate power: Typical tectonic deformation")
            else:
                print(f"   → Low power: Slow/quiescent deformation")
        
        print("\n" + "="*70 + "\n")
    
    def plot_comprehensive_analysis(self, output_dir: Path):
        """Generate comprehensive energy analysis plots."""
        power_data = self.analyze_power_contributions()
        thermal = self.calculate_thermal_impact()
        
        if power_data is None:
            print("Cannot generate plots: missing energy data")
            return
        
        fig = plt.figure(figsize=(16, 12))
        
        # 1. Power contributions over time
        ax1 = plt.subplot(3, 3, 1)
        ax1.plot(power_data['time'], power_data['thermal_power'], 'r-', label='Thermal', linewidth=2)
        ax1.plot(power_data['time'], power_data['viscous_power'], 'b-', label='Viscous', linewidth=2)
        ax1.plot(power_data['time'], power_data['plastic_power'], 'g-', label='Plastic', linewidth=2)
        ax1.set_xlabel('Time (years)')
        ax1.set_ylabel('Power Density (W/m³)')
        ax1.set_title('Power Contributions')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_yscale('symlog', linthresh=1e-10)
        
        # 2. Percentage contributions
        ax2 = plt.subplot(3, 3, 2)
        ax2.stackplot(power_data['time'], 
                     np.abs(power_data['thermal_pct']),
                     np.abs(power_data['viscous_pct']),
                     np.abs(power_data['plastic_pct']),
                     labels=['Thermal', 'Viscous', 'Plastic'],
                     colors=['red', 'blue', 'green'], alpha=0.7)
        ax2.set_xlabel('Time (years)')
        ax2.set_ylabel('Contribution (%)')
        ax2.set_title('Relative Power Contributions')
        ax2.legend(loc='upper right')
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim([0, 100])
        
        # 3. Total power evolution
        ax3 = plt.subplot(3, 3, 3)
        ax3.plot(power_data['time'], np.abs(power_data['total_power']), 'k-', linewidth=2)
        ax3.set_xlabel('Time (years)')
        ax3.set_ylabel('Total Power Density (W/m³)')
        ax3.set_title('Total Power Dissipation')
        ax3.grid(True, alpha=0.3)
        ax3.set_yscale('log')
        
        # 4. Temperature evolution
        if 'temperature' in self.data:
            ax4 = plt.subplot(3, 3, 4)
            ax4.plot(self.data['time'], self.data['temperature']['mean'], 'r-', label='Mean', linewidth=2)
            ax4.plot(self.data['time'], self.data['temperature']['max'], 'r--', label='Max', linewidth=1.5)
            ax4.set_xlabel('Time (years)')
            ax4.set_ylabel('Temperature (K)')
            ax4.set_title('Temperature Evolution')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
        
        # 5. Heating rate
        if thermal:
            ax5 = plt.subplot(3, 3, 5)
            ax5.plot(thermal['time'], thermal['heating_rate_mean'], 'r-', linewidth=2)
            ax5.axhline(y=0, color='k', linestyle='--', alpha=0.5)
            ax5.set_xlabel('Time (years)')
            ax5.set_ylabel('Heating Rate (K/year)')
            ax5.set_title('Temperature Change Rate')
            ax5.grid(True, alpha=0.3)
        
        # 6. Power vs Temperature correlation
        if thermal:
            ax6 = plt.subplot(3, 3, 6)
            scatter = ax6.scatter(thermal['power_mean'], thermal['heating_rate_mean'], 
                                 c=thermal['time'], cmap='viridis', alpha=0.6)
            ax6.set_xlabel('Power Density (W/m³)')
            ax6.set_ylabel('Heating Rate (K/year)')
            ax6.set_title('Power-Temperature Correlation')
            ax6.grid(True, alpha=0.3)
            plt.colorbar(scatter, ax=ax6, label='Time (years)')
        
        # 7. Deformation regime pie chart (late stage)
        regime = self.interpret_deformation_regime(power_data)
        if regime:
            ax7 = plt.subplot(3, 3, 7)
            sizes = [regime['regime']['viscous'], regime['regime']['plastic'], regime['regime']['thermal']]
            labels = ['Viscous', 'Plastic', 'Thermal']
            colors = ['blue', 'green', 'red']
            ax7.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax7.set_title('Late-Stage Deformation Regime')
        
        # 8. Cumulative energy
        ax8 = plt.subplot(3, 3, 8)
        if len(power_data['time']) > 1:
            dt = np.diff(power_data['time'])
            dt = np.append(dt, dt[-1])  # Extend to match length
            cumulative_thermal = np.cumsum(power_data['thermal_power'] * dt)
            cumulative_viscous = np.cumsum(power_data['viscous_power'] * dt)
            cumulative_plastic = np.cumsum(power_data['plastic_power'] * dt)
            
            ax8.plot(power_data['time'], cumulative_thermal, 'r-', label='Thermal', linewidth=2)
            ax8.plot(power_data['time'], cumulative_viscous, 'b-', label='Viscous', linewidth=2)
            ax8.plot(power_data['time'], cumulative_plastic, 'g-', label='Plastic', linewidth=2)
            ax8.set_xlabel('Time (years)')
            ax8.set_ylabel('Cumulative Energy (J/m³·year)')
            ax8.set_title('Cumulative Energy Budget')
            ax8.legend()
            ax8.grid(True, alpha=0.3)
        
        # 9. Geological interpretation text
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        if regime:
            interp_text = f"GEOLOGICAL INTERPRETATION\n\n"
            interp_text += f"Dominant Mechanism:\n{regime['dominant'].upper()}\n\n"
            interp_text += f"{regime['interpretation']}\n\n"
            
            if thermal:
                interp_text += f"Thermal Impact:\n"
                interp_text += f"ΔT = {thermal['temp_increase']:.1f} K\n"
                if thermal['temp_increase'] > 10:
                    interp_text += "⚠ Significant shear heating!"
            
            ax9.text(0.1, 0.5, interp_text, fontsize=10, verticalalignment='center',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.suptitle(f'Energy Balance Analysis: {self.experiment.name}', 
                    fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        output_file = output_dir / 'energy_geological_interpretation.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Saved geological interpretation to {output_file}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python interpret_energy.py experiment_name")
        print("Example: python interpret_energy.py energy")
        return 1
    
    experiment_name = sys.argv[1]
    
    # Analyze experiment
    analyzer = ExperimentAnalyzer(experiment_name)
    analyzer.analyze()
    
    if not analyzer.data:
        print(f"Error: No data found for experiment '{experiment_name}'")
        return 1
    
    # Create interpreter
    interpreter = EnergyInterpreter(analyzer)
    
    # Generate geological summary
    interpreter.geological_summary()
    
    # Create visualization directory
    if analyzer.run_dir:
        viz_dir = analyzer.run_dir / "viz"
        viz_dir.mkdir(exist_ok=True)
        
        # Generate comprehensive plots
        interpreter.plot_comprehensive_analysis(viz_dir)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
