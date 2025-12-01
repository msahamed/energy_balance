#ifndef ENERGY_BALANCE_HPP
#define ENERGY_BALANCE_HPP

#include "parameters.hpp"

namespace EnergyBalance {

    // Computes nodal power, pressure, and density terms for energy balance.
    // Iterates over elements and scatters contributions to nodes.
    void compute_nodal_sources(const Param& param, const Variables& var);

    // Computes the temperature update for a single node based on energy balance terms.
    // Returns the extra term to be added to the temperature.
    // Also updates var.temp_power, var.temp_pressure, var.temp_density, and var.dtemp.
    double compute_nodal_update(const Param& param, const Variables& var, int node_idx, double& temp_val, double dt);

    // Computes the thermal stress increment.
    double compute_thermal_stress_increment(double bulkm, double alpha, double dT);

    // Records the energy and power contributions for an element.
    void record_element_contribution(Variables& var, int elem_idx, 
                                     double t_power, double v_power, double d_power, 
                                     double pressure_new, double pressure_old);

}

#endif
