#!/usr/bin/env python3
"""
Thermal-Mechanical Feedback Analysis Tool

Analyzes the feedback loop between:
Temperature → Rheology → Deformation → Heat Generation → Temperature

This is critical for understanding geological evolution, strain localization,
and long-term tectonic behavior.

Usage:
    python analyze_feedback.py experiment1 [experiment2]
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats
from analyze_results import ExperimentAnalyzer


class FeedbackAnalyzer:
    """Analyze thermal-mechanical feedback loops."""
    
    def __init__(self, experiment: ExperimentAnalyzer):
        self.experiment = experiment
        self.data = experiment.data
        
    def analyze_temperature_velocity_coupling(self):
        """Analyze how temperature affects deformation rate."""
        if 'temperature' not in self.data or 'velocity' not in self.data:
            return None
        
        time = self.data['time']
        temp_mean = self.data['temperature']['mean']
        temp_max = self.data['temperature']['max']
        vel_max = self.data['velocity']['max']
        
        # Calculate correlation
        if len(temp_mean) > 2:
            corr_mean, p_mean = stats.pearsonr(temp_mean, vel_max)
            corr_max, p_max = stats.pearsonr(temp_max, vel_max)
        else:
            corr_mean, corr_max = 0, 0
            p_mean, p_max = 1, 1
        
        return {
            'time': time,
            'temp_mean': temp_mean,
            'temp_max': temp_max,
            'vel_max': vel_max,
            'correlation_mean': corr_mean,
            'correlation_max': corr_max,
            'p_value_mean': p_mean,
            'p_value_max': p_max
        }
    
    def analyze_power_temperature_feedback(self):
        """Analyze the feedback: Power → Temperature → Rheology → Power."""
        if 'power' not in self.data or 'temperature' not in self.data:
            return None
        
        time = self.data['time']
        power_mean = self.data['power']['mean']
        temp_mean = self.data['temperature']['mean']
        
        # Calculate time derivatives
        if len(time) > 1:
            dt = np.diff(time)
            dT_dt = np.diff(temp_mean) / dt
            dP_dt = np.diff(power_mean) / dt
            
            # Lag correlation: does power at time t affect temperature at t+1?
            if len(power_mean) > 2:
                # Correlation between power and future temperature change
                corr_forward = np.corrcoef(power_mean[:-1], dT_dt)[0, 1]
                # Correlation between temperature and future power change
                corr_backward = np.corrcoef(temp_mean[:-1], dP_dt)[0, 1]
            else:
                corr_forward, corr_backward = 0, 0
            
            return {
                'time': time[1:],
                'power_mean': power_mean[1:],
                'temp_mean': temp_mean[1:],
                'dT_dt': dT_dt,
                'dP_dt': dP_dt,
                'power_to_temp_correlation': corr_forward,
                'temp_to_power_correlation': corr_backward
            }
        return None
    
    def detect_thermal_runaway(self):
        """Detect signs of thermal runaway (positive feedback instability)."""
        feedback = self.analyze_power_temperature_feedback()
        if feedback is None:
            return None
        
        # Thermal runaway indicators:
        # 1. Both correlations positive and strong
        # 2. Accelerating temperature increase
        # 3. Accelerating power increase
        
        power_to_temp = feedback['power_to_temp_correlation']
        temp_to_power = feedback['temp_to_power_correlation']
        
        # Check for acceleration
        dT_dt = feedback['dT_dt']
        dP_dt = feedback['dP_dt']
        
        temp_accelerating = np.mean(dT_dt[-10:]) > np.mean(dT_dt[:10]) if len(dT_dt) > 20 else False
        power_accelerating = np.mean(dP_dt[-10:]) > np.mean(dP_dt[:10]) if len(dP_dt) > 20 else False
        
        # Runaway criteria
        strong_feedback = (power_to_temp > 0.3) and (temp_to_power > 0.3)
        runaway_risk = strong_feedback and temp_accelerating and power_accelerating
        
        return {
            'power_to_temp_corr': power_to_temp,
            'temp_to_power_corr': temp_to_power,
            'temp_accelerating': temp_accelerating,
            'power_accelerating': power_accelerating,
            'strong_feedback': strong_feedback,
            'runaway_risk': runaway_risk
        }
    
    def analyze_strain_localization(self):
        """Analyze if thermal weakening causes strain localization."""
        if 'power' not in self.data or 'temperature' not in self.data:
            return None
        
        time = self.data['time']
        power_std = self.data['power']['std']
        power_mean = self.data['power']['mean']
        temp_std = self.data['temperature']['std']
        temp_mean = self.data['temperature']['mean']
        
        # Coefficient of variation (normalized std dev)
        power_cv = power_std / (np.abs(power_mean) + 1e-20)
        temp_cv = temp_std / (temp_mean + 1e-20)
        
        # Increasing CV suggests localization
        if len(time) > 20:
            early_power_cv = np.mean(power_cv[:10])
            late_power_cv = np.mean(power_cv[-10:])
            localization_factor = late_power_cv / (early_power_cv + 1e-10)
        else:
            localization_factor = 1.0
        
        return {
            'time': time,
            'power_cv': power_cv,
            'temp_cv': temp_cv,
            'localization_factor': localization_factor,
            'is_localizing': localization_factor > 1.5
        }
    
    def geological_evolution_summary(self):
        """Provide geological interpretation of feedback effects."""
        temp_vel = self.analyze_temperature_velocity_coupling()
        runaway = self.detect_thermal_runaway()
        localization = self.analyze_strain_localization()
        
        print("\n" + "="*80)
        print(f"THERMAL-MECHANICAL FEEDBACK ANALYSIS: {self.experiment.name}")
        print("="*80)
        
        print("\n1. FEEDBACK LOOP STRENGTH:")
        if runaway:
            print(f"   Power → Temperature correlation: {runaway['power_to_temp_corr']:.3f}")
            print(f"   Temperature → Power correlation: {runaway['temp_to_power_corr']:.3f}")
            
            if runaway['strong_feedback']:
                print(f"   ✓ STRONG POSITIVE FEEDBACK DETECTED")
                print(f"     → Shear heating significantly affects system evolution")
            else:
                print(f"   ○ Moderate feedback")
            
            if runaway['runaway_risk']:
                print(f"\n   ⚠⚠⚠ THERMAL RUNAWAY RISK DETECTED ⚠⚠⚠")
                print(f"   → Temperature and power both accelerating")
                print(f"   → System may be approaching instability")
                print(f"   → Geological implication: Rapid strain localization likely")
        
        print("\n2. TEMPERATURE-DEFORMATION COUPLING:")
        if temp_vel:
            print(f"   Temperature-Velocity correlation: {temp_vel['correlation_mean']:.3f}")
            if abs(temp_vel['correlation_mean']) > 0.5:
                if temp_vel['correlation_mean'] > 0:
                    print(f"   ✓ Strong positive coupling: Higher T → Faster deformation")
                    print(f"     → Thermal weakening is active")
                else:
                    print(f"   ○ Negative coupling: Complex thermal structure")
            else:
                print(f"   ○ Weak coupling: Temperature not strongly affecting deformation")
        
        print("\n3. STRAIN LOCALIZATION:")
        if localization:
            print(f"   Localization factor: {localization['localization_factor']:.2f}")
            if localization['is_localizing']:
                print(f"   ✓ STRAIN LOCALIZATION DETECTED")
                print(f"     → Deformation becoming more concentrated over time")
                print(f"     → Likely forming shear zones or fault zones")
                print(f"     → Geological implication: Focused deformation, potential for")
                print(f"       fault development, mylonite zones, or plate boundaries")
            else:
                print(f"   ○ Distributed deformation")
                print(f"     → Strain remains relatively uniform")
        
        print("\n4. GEOLOGICAL EVOLUTION IMPLICATIONS:")
        
        if runaway and runaway['strong_feedback']:
            print("\n   FEEDBACK-DRIVEN EVOLUTION:")
            print("   • Initial deformation → Heat generation")
            print("   • Heat → Temperature increase → Rheological weakening")
            print("   • Weakening → More deformation → More heat")
            print("   • Cycle continues, potentially accelerating")
            
            if localization and localization['is_localizing']:
                print("\n   LOCALIZATION PATHWAY:")
                print("   • Thermal weakening creates 'soft spots'")
                print("   • Deformation concentrates in weak zones")
                print("   • More deformation → More heating → Weaker")
                print("   • Result: Formation of discrete shear zones/faults")
                print("\n   GEOLOGICAL ANALOGS:")
                print("   - Continental rifts (e.g., East African Rift)")
                print("   - Transform faults (e.g., San Andreas)")
                print("   - Subduction shear zones")
                print("   - Orogenic shear zones (e.g., Alpine mylonites)")
        else:
            print("\n   STABLE EVOLUTION:")
            print("   • Feedback is weak or negative")
            print("   • System evolves without strong thermal effects")
            print("   • Deformation controlled by boundary conditions")
            print("   • Typical of: Slow deformation, cold lithosphere")
        
        print("\n" + "="*80 + "\n")
    
    def plot_feedback_analysis(self, output_dir: Path):
        """Generate comprehensive feedback analysis plots."""
        temp_vel = self.analyze_temperature_velocity_coupling()
        feedback = self.analyze_power_temperature_feedback()
        localization = self.analyze_strain_localization()
        runaway = self.detect_thermal_runaway()
        
        fig = plt.figure(figsize=(18, 12))
        
        # 1. Temperature-Velocity coupling
        if temp_vel:
            ax1 = plt.subplot(3, 3, 1)
            ax1_twin = ax1.twinx()
            
            line1 = ax1.plot(temp_vel['time'], temp_vel['temp_mean'], 'r-', 
                            label='Temperature', linewidth=2)
            line2 = ax1_twin.plot(temp_vel['time'], temp_vel['vel_max'], 'b-', 
                                 label='Velocity', linewidth=2)
            
            ax1.set_xlabel('Time (years)')
            ax1.set_ylabel('Mean Temperature (K)', color='r')
            ax1_twin.set_ylabel('Max Velocity (m/s)', color='b')
            ax1.set_title(f'Temperature-Velocity Coupling\n(r={temp_vel["correlation_mean"]:.3f})')
            ax1.tick_params(axis='y', labelcolor='r')
            ax1_twin.tick_params(axis='y', labelcolor='b')
            ax1.grid(True, alpha=0.3)
            
            lines = line1 + line2
            labels = [l.get_label() for l in lines]
            ax1.legend(lines, labels, loc='upper left')
        
        # 2. Power-Temperature feedback
        if feedback:
            ax2 = plt.subplot(3, 3, 2)
            scatter = ax2.scatter(feedback['power_mean'], feedback['temp_mean'],
                                 c=feedback['time'], cmap='viridis', s=20, alpha=0.6)
            ax2.set_xlabel('Power Density (W/m³)')
            ax2.set_ylabel('Mean Temperature (K)')
            ax2.set_title('Power-Temperature Phase Space')
            ax2.grid(True, alpha=0.3)
            plt.colorbar(scatter, ax=ax2, label='Time (years)')
            
            # Add arrow showing evolution direction
            if len(feedback['power_mean']) > 10:
                n = len(feedback['power_mean'])
                for i in range(0, n-10, max(1, n//20)):
                    ax2.annotate('', xy=(feedback['power_mean'][i+10], feedback['temp_mean'][i+10]),
                               xytext=(feedback['power_mean'][i], feedback['temp_mean'][i]),
                               arrowprops=dict(arrowstyle='->', color='red', alpha=0.3, lw=1))
        
        # 3. Temperature rate vs Power
        if feedback:
            ax3 = plt.subplot(3, 3, 3)
            ax3.scatter(feedback['power_mean'], feedback['dT_dt'], alpha=0.6, s=20)
            ax3.set_xlabel('Power Density (W/m³)')
            ax3.set_ylabel('Heating Rate (K/year)')
            ax3.set_title(f'Power → Temperature\n(r={feedback["power_to_temp_correlation"]:.3f})')
            ax3.grid(True, alpha=0.3)
            ax3.axhline(y=0, color='k', linestyle='--', alpha=0.5)
            
            # Add trend line
            if len(feedback['power_mean']) > 2:
                z = np.polyfit(feedback['power_mean'], feedback['dT_dt'], 1)
                p = np.poly1d(z)
                x_trend = np.linspace(feedback['power_mean'].min(), feedback['power_mean'].max(), 100)
                ax3.plot(x_trend, p(x_trend), 'r--', alpha=0.8, linewidth=2, label='Trend')
                ax3.legend()
        
        # 4. Power rate vs Temperature
        if feedback:
            ax4 = plt.subplot(3, 3, 4)
            ax4.scatter(feedback['temp_mean'], feedback['dP_dt'], alpha=0.6, s=20)
            ax4.set_xlabel('Mean Temperature (K)')
            ax4.set_ylabel('Power Change Rate (W/m³/year)')
            ax4.set_title(f'Temperature → Power\n(r={feedback["temp_to_power_correlation"]:.3f})')
            ax4.grid(True, alpha=0.3)
            ax4.axhline(y=0, color='k', linestyle='--', alpha=0.5)
            
            # Add trend line
            if len(feedback['temp_mean']) > 2:
                z = np.polyfit(feedback['temp_mean'], feedback['dP_dt'], 1)
                p = np.poly1d(z)
                x_trend = np.linspace(feedback['temp_mean'].min(), feedback['temp_mean'].max(), 100)
                ax4.plot(x_trend, p(x_trend), 'r--', alpha=0.8, linewidth=2, label='Trend')
                ax4.legend()
        
        # 5. Strain localization indicator
        if localization:
            ax5 = plt.subplot(3, 3, 5)
            ax5.plot(localization['time'], localization['power_cv'], 'b-', 
                    label='Power CV', linewidth=2)
            ax5.plot(localization['time'], localization['temp_cv'], 'r-', 
                    label='Temp CV', linewidth=2)
            ax5.set_xlabel('Time (years)')
            ax5.set_ylabel('Coefficient of Variation')
            ax5.set_title(f'Strain Localization\n(Factor: {localization["localization_factor"]:.2f})')
            ax5.legend()
            ax5.grid(True, alpha=0.3)
            
            if localization['is_localizing']:
                ax5.text(0.5, 0.95, 'LOCALIZING', transform=ax5.transAxes,
                        ha='center', va='top', fontsize=12, fontweight='bold',
                        bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        # 6. Feedback loop diagram
        ax6 = plt.subplot(3, 3, 6)
        ax6.axis('off')
        
        if runaway:
            feedback_text = "FEEDBACK LOOP ANALYSIS\n\n"
            feedback_text += f"Power → Temp: {runaway['power_to_temp_corr']:.3f}\n"
            feedback_text += f"Temp → Power: {runaway['temp_to_power_corr']:.3f}\n\n"
            
            if runaway['strong_feedback']:
                feedback_text += "✓ STRONG FEEDBACK\n"
                feedback_text += "Thermal weakening active\n\n"
            
            if runaway['runaway_risk']:
                feedback_text += "⚠ RUNAWAY RISK\n"
                feedback_text += "System accelerating\n"
                color = 'red'
            elif runaway['strong_feedback']:
                color = 'orange'
            else:
                color = 'lightgreen'
            
            ax6.text(0.5, 0.5, feedback_text, transform=ax6.transAxes,
                    ha='center', va='center', fontsize=11,
                    bbox=dict(boxstyle='round', facecolor=color, alpha=0.7))
        
        # 7. Temperature evolution with phases
        if 'temperature' in self.data:
            ax7 = plt.subplot(3, 3, 7)
            time = self.data['time']
            temp_mean = self.data['temperature']['mean']
            
            ax7.plot(time, temp_mean, 'k-', linewidth=2)
            ax7.fill_between(time, self.data['temperature']['min'], 
                            self.data['temperature']['max'], alpha=0.3)
            ax7.set_xlabel('Time (years)')
            ax7.set_ylabel('Temperature (K)')
            ax7.set_title('Temperature Evolution')
            ax7.grid(True, alpha=0.3)
            
            # Mark acceleration phase if detected
            if runaway and runaway['temp_accelerating']:
                ax7.axvspan(time[int(0.8*len(time))], time[-1], 
                           alpha=0.2, color='red', label='Acceleration')
                ax7.legend()
        
        # 8. Power evolution with phases
        if 'power' in self.data:
            ax8 = plt.subplot(3, 3, 8)
            time = self.data['time']
            power_mean = self.data['power']['mean']
            
            ax8.plot(time, power_mean, 'k-', linewidth=2)
            ax8.fill_between(time, self.data['power']['min'], 
                            self.data['power']['max'], alpha=0.3)
            ax8.set_xlabel('Time (years)')
            ax8.set_ylabel('Power Density (W/m³)')
            ax8.set_title('Power Evolution')
            ax8.grid(True, alpha=0.3)
            ax8.set_yscale('symlog', linthresh=1e-10)
            
            # Mark acceleration phase if detected
            if runaway and runaway['power_accelerating']:
                ax8.axvspan(time[int(0.8*len(time))], time[-1], 
                           alpha=0.2, color='red', label='Acceleration')
                ax8.legend()
        
        # 9. Geological interpretation
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        interp_text = "GEOLOGICAL EVOLUTION\n\n"
        
        if runaway and runaway['strong_feedback']:
            interp_text += "Feedback-Driven:\n"
            interp_text += "• Thermal weakening\n"
            interp_text += "• Self-reinforcing\n"
            if localization and localization['is_localizing']:
                interp_text += "• Strain localizing\n"
                interp_text += "\nForming:\n"
                interp_text += "Shear zones/Faults\n"
        else:
            interp_text += "Stable Evolution:\n"
            interp_text += "• Weak feedback\n"
            interp_text += "• Boundary-driven\n"
            interp_text += "• Distributed strain\n"
        
        ax9.text(0.1, 0.5, interp_text, transform=ax9.transAxes,
                fontsize=10, verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        
        plt.suptitle(f'Thermal-Mechanical Feedback Analysis: {self.experiment.name}',
                    fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        output_file = output_dir / 'feedback_analysis.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Saved feedback analysis to {output_file}")


def compare_feedback(exp1: ExperimentAnalyzer, exp2: ExperimentAnalyzer, output_dir: Path):
    """Compare feedback effects between two experiments."""
    analyzer1 = FeedbackAnalyzer(exp1)
    analyzer2 = FeedbackAnalyzer(exp2)
    
    runaway1 = analyzer1.detect_thermal_runaway()
    runaway2 = analyzer2.detect_thermal_runaway()
    
    loc1 = analyzer1.analyze_strain_localization()
    loc2 = analyzer2.analyze_strain_localization()
    
    print("\n" + "="*80)
    print(f"FEEDBACK COMPARISON: {exp1.name} vs {exp2.name}")
    print("="*80)
    
    if runaway1 and runaway2:
        print(f"\nFeedback Strength:")
        print(f"  {exp1.name:20s}: Power→Temp={runaway1['power_to_temp_corr']:6.3f}, "
              f"Temp→Power={runaway1['temp_to_power_corr']:6.3f}")
        print(f"  {exp2.name:20s}: Power→Temp={runaway2['power_to_temp_corr']:6.3f}, "
              f"Temp→Power={runaway2['temp_to_power_corr']:6.3f}")
        
        diff = abs(runaway1['power_to_temp_corr']) - abs(runaway2['power_to_temp_corr'])
        if abs(diff) > 0.2:
            stronger = exp1.name if diff > 0 else exp2.name
            print(f"\n  → {stronger} shows STRONGER thermal-mechanical coupling")
            print(f"    Implication: More sensitive to shear heating effects")
    
    if loc1 and loc2:
        print(f"\nStrain Localization:")
        print(f"  {exp1.name:20s}: Factor={loc1['localization_factor']:.2f} "
              f"({'LOCALIZING' if loc1['is_localizing'] else 'Distributed'})")
        print(f"  {exp2.name:20s}: Factor={loc2['localization_factor']:.2f} "
              f"({'LOCALIZING' if loc2['is_localizing'] else 'Distributed'})")
        
        if loc1['is_localizing'] != loc2['is_localizing']:
            localizing = exp1.name if loc1['is_localizing'] else exp2.name
            print(f"\n  → {localizing} develops focused deformation")
            print(f"    Geological implication: Fault/shear zone formation")
    
    print("\n" + "="*80 + "\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_feedback.py experiment1 [experiment2]")
        print("Example: python analyze_feedback.py energy no_energy")
        return 1
    
    # Analyze first experiment
    exp1 = ExperimentAnalyzer(sys.argv[1])
    exp1.analyze()
    
    if not exp1.data:
        print(f"Error: No data found for '{sys.argv[1]}'")
        return 1
    
    analyzer1 = FeedbackAnalyzer(exp1)
    analyzer1.geological_evolution_summary()
    
    if exp1.run_dir:
        viz_dir = exp1.run_dir / "viz"
        viz_dir.mkdir(exist_ok=True)
        analyzer1.plot_feedback_analysis(viz_dir)
    
    # Compare if second experiment provided
    if len(sys.argv) > 2:
        exp2 = ExperimentAnalyzer(sys.argv[2])
        exp2.analyze()
        
        if exp2.data:
            analyzer2 = FeedbackAnalyzer(exp2)
            analyzer2.geological_evolution_summary()
            
            if exp2.run_dir:
                viz_dir2 = exp2.run_dir / "viz"
                viz_dir2.mkdir(exist_ok=True)
                analyzer2.plot_feedback_analysis(viz_dir2)
            
            # Comparison
            if exp1.run_dir:
                compare_feedback(exp1, exp2, exp1.run_dir / "viz")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
