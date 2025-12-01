#ifndef ENERGY_BALANCE_HPP
#define ENERGY_BALANCE_HPP

#include "parameters.hpp"
#include <fstream>

#ifdef ENABLE_ENERGY_BALANCE

// Full energy balance implementation
namespace EnergyBalance {

    // Computes nodal power, pressure, and density terms for energy balance.
    void compute_nodal_sources(const Param& param, const Variables& var);

    // Computes the temperature update for a single node based on energy balance terms.
    // Returns the extra term to be added to the temperature.
    double compute_nodal_update(const Param& param, const Variables& var, int node_idx, double& temp_val, double dt);

    // Computes the thermal stress increment.
    double compute_thermal_stress_increment(double bulkm, double alpha, double dT);

    // Records the energy and power contributions for an element.
    void record_element_contribution(Variables& var, int elem_idx, 
                                     double t_power, double v_power, double d_power, 
                                     double pressure_new, double pressure_old);

    // Write energy balance fields to binary output
    template<typename BinaryOutput>
    void write_binary_output(BinaryOutput& bin, const Variables& var);

    // Write energy balance fields to VTK output
    void write_vtk_output(std::ofstream& vtk_file, const Variables& var);

}

#else

// Stub implementations when energy balance is disabled (zero overhead)
namespace EnergyBalance {

    // No-op stubs - these will be optimized away by the compiler
    inline void compute_nodal_sources(const Param&, const Variables&) {}
    
    inline double compute_nodal_update(const Param&, const Variables&, int, double&, double) {
        return 0.0;  // No energy balance contribution
    }
    
    inline double compute_thermal_stress_increment(double, double, double) {
        return 0.0;  // No thermal stress
    }
    
    inline void record_element_contribution(Variables&, int, double, double, double, double, double) {}
    
    template<typename BinaryOutput>
    inline void write_binary_output(BinaryOutput&, const Variables&) {}
    
    inline void write_vtk_output(std::ofstream&, const Variables&) {}

}

#endif // ENABLE_ENERGY_BALANCE

#endif // ENERGY_BALANCE_HPP
