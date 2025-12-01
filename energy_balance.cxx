#include "energy_balance.hpp"
#include "matprops.hpp"
#include <algorithm>
#include <iostream>

namespace EnergyBalance {

    void compute_nodal_sources(const Param& param, const Variables& var) {
        if (!param.sim.has_energy_balance) return;

        // Reset nodal terms
        std::fill(var.powerTerm->begin(), var.powerTerm->end(), 0.0);
        std::fill(var.pressureTerm->begin(), var.pressureTerm->end(), 0.0);
        std::fill(var.densityTerm->begin(), var.densityTerm->end(), 0.0);
        
        #pragma omp parallel for default(none) shared(param, var)
        for (int e=0; e<var.nelem; e++) {
            const int *conn = (*var.connectivity)[e];
            double *s = (*var.stress)[e];
            double *edot = (*var.strain_rate)[e];
            double& syy = (*var.stressyy)[e];
            
            double temp = 0;
            for (int i = 0; i < NODES_PER_ELEM; ++i) {
                temp += (*var.temperature)[conn[i]];
            }
            double T = temp / NODES_PER_ELEM;
            
            #ifdef THREED
            double P = -(s[0] + s[1] + s[2]) / NDIMS;
            double vedot = edot[0]+ edot[1] + edot[2];
            #else
            double P = -(s[0] + s[1] + syy) / 3;
            double vedot = edot[0]+ edot[1];
            #endif
            
            double alpha = var.mat->get_alpha(e);
            double plastic = (*var.power)[e] * (*var.volume)[e]/NODES_PER_ELEM;
            double pressure = T * alpha * (*var.dP)[e] * (*var.volume)[e] / NODES_PER_ELEM;
            // Corrected density term with dt multiplication
            double den = P * T * alpha * vedot * (*var.volume)[e] * var.dt / NODES_PER_ELEM;
            
            for (int i = 0; i < NODES_PER_ELEM; ++i) {
                #pragma omp atomic
                (*var.powerTerm)[conn[i]] += plastic;
                #pragma omp atomic
                (*var.pressureTerm)[conn[i]] += pressure;
                #pragma omp atomic
                (*var.densityTerm)[conn[i]] += den;
            }
        }
    }

    double compute_nodal_update(const Param& param, const Variables& var, int node_idx, double& temp_val, double dt) {
        if (!param.sim.has_energy_balance) return 0.0;

        double power_term = (*var.powerTerm)[node_idx] / (*var.tmass)[node_idx];
        double pressure_term = (*var.pressureTerm)[node_idx] / (*var.tmass)[node_idx];
        double density_term = (*var.densityTerm)[node_idx] / (*var.tmass)[node_idx];
        
        double extra_term = power_term + pressure_term + density_term;
        
        (*var.temp_power)[node_idx] += power_term;
        (*var.temp_pressure)[node_idx] += pressure_term;
        (*var.temp_density)[node_idx] += density_term;
        
        // If we only return extra_term, the caller adds it.
        // But we also need to update dtemp.
        // Let's stick to the fields.cxx logic:
        // The caller handles the diffusion term addition.
        // We just return extra_term. 
        // BUT, we are also supposed to update var.dtemp? 
        // In fields.cxx, var.dtemp is updated with the FINAL temperature difference.
        // So we can't fully update var.dtemp here without knowing the diffusion term.
        // Wait, looking at fields.cxx:
        // double temp_old = temperature[n];
        // temperature[n] += diffusion_term + extra_term;
        // (*var.dtemp)[n] = temperature[n] - temp_old;
        
        // My proposed function signature: compute_nodal_update(..., double& temp_val, ...)
        // If I pass the temp_val *after* diffusion is added, or before?
        // Let's assume the caller handles diffusion.
        // Maybe I should just return the values and let the caller do the update?
        // Or pass the diffusion term in?
        // Let's keep it simple: just calculate the terms and update the diagnostic variables (temp_power, etc).
        // The caller will handle the final temperature update and dtemp calculation.
        // I will remove dtemp update from here to avoid confusion.
        
        return extra_term;
    }

    double compute_thermal_stress_increment(double bulkm, double alpha, double dT) {
        return -bulkm * alpha * dT;
    }

    void record_element_contribution(Variables& var, int elem_idx, 
                                     double t_power, double v_power, double d_power, 
                                     double pressure_new, double pressure_old) {
        (*var.tenergy)[elem_idx] = t_power;
        (*var.venergy)[elem_idx] = v_power;
        (*var.denergy)[elem_idx] = d_power;
        (*var.power)[elem_idx] = t_power + v_power + d_power;
        (*var.dP)[elem_idx] = pressure_new - pressure_old;
    }

}
