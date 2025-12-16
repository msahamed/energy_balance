# Bengal Basin - Madhupur Fault Region: Basement Structure

## Overview

This document summarizes the realistic geological structure of the Bengal Basin in the Madhupur Fault region, compiled from peer-reviewed scientific literature. This information is used to configure the DynEarthSol earthquake cycle simulation.

---

## 1. Regional Tectonic Setting

The Bengal Basin is the world's largest fluvio-deltaic sedimentary basin, located at the convergence of the Indian, Eurasian, and Burmese plates. The Indian Plate's northward motion (~5 cm/yr) drives compression and seismicity along internal fault systems including the Madhupur Fault.

**Key Tectonic Features:**
- **Indian Craton**: To the west, stable continental crust
- **Hinge Zone**: Transition from craton to deep basin (3→17 km sediment thickness increase)
- **Madhupur High**: Structural uplift where basement reaches 128 m depth (shallowest)
- **Deep Foredeep**: Central basin with up to 20 km sediments

---

## 2. Sedimentary Structure

### Sediment Thickness Distribution

| Region | Sediment Thickness | Notes |
|--------|-------------------|-------|
| **Madhupur High** | 3-5 km | Basement uplift, shallowest at 128 m |
| **Hinge Zone** | 2.8-3.1 km | Transition zone |
| **Central Basin** | 12.2-17.4 km | Deep foredeep |
| **Coastal Area** | 18-20 km | Maximum thickness |

**For Madhupur Fault modeling**: Use **3-5 km** sediment thickness (Madhupur High setting)

### Sedimentary Layering

**Three-layer sedimentary sequence** (from seismic velocity analysis):

1. **Unconsolidated Sediments** (Quaternary)
   - Depth: 0-0.5 km
   - Lithology: Alluvium, silt, sand, weathered laterite
   - Vs: 0.5-1.0 km/s (very low - soft sediments)
   - Vp: 1.8-2.5 km/s
   - Density: 2000-2200 kg/m³

2. **Consolidated Sediments** (Tertiary)
   - Depth: 0.5-3 km
   - Lithology: Sandstones, shales, siltstones (Oligocene-Pliocene)
   - Vs: 2.0-2.5 km/s
   - Vp: 3.5-4.5 km/s
   - Density: 2400-2600 kg/m³

3. **Meta-sediments** (Pre-Tertiary)
   - Depth: 3-5 km (transition to basement)
   - Lithology: Indurated, metamorphosed sediments
   - Vs: 2.8-3.2 km/s
   - Vp: 5.0-5.8 km/s
   - Density: 2650-2750 kg/m³

---

## 3. Crustal Structure

### Crystalline Crust Configuration

**Crustal thickness varies across Bengal Basin:**
- Indian Craton: 38 km
- Hinge Zone: 34 km
- **Madhupur Area: ~34 km** (used for modeling)
- Deep Basin: 16-19 km (extreme thinning)

### Crustal Layering (Madhupur Region)

| Layer | Depth (km) | Thickness (km) | Density (kg/m³) | Vp (km/s) | Vs (km/s) |
|-------|-----------|---------------|-----------------|-----------|-----------|
| **Sediments** | 0-3 | 3 | 2200-2600 | 2.5-4.5 | 1.0-2.5 |
| **Upper Crust** | 3-15 | 12 | 2780 | 6.0-6.2 | 3.5-3.6 |
| **Middle Crust** | 15-25 | 10 | 2830 | 6.4-6.6 | 3.7-3.8 |
| **Lower Crust** | 25-34 | 9 | 2900-3000 | 6.8-7.0 | 3.9-4.0 |
| **Mantle** | 34+ | - | 3300 | 8.0-8.2 | 4.5-4.7 |

**Average crustal S-wave velocity**: 3.7 km/s

---

## 4. Madhupur Fault Characteristics

### Geometry (from 2025 Narsingdi M5.4 Earthquake)

- **Strike**: NNW-SSE (roughly N-S)
- **Dip**: ~40° (north-dipping blind thrust)
- **Fault zone width**: 5-10 km
- **Along-strike length**: >150 km (Tangail-Mymensingh-Gazipur-Kishoreganj)

### Depth Extent

- **Shallow limit**: ~5 km (base of consolidated sediments)
- **Seismogenic zone**: 5-20 km (where earthquakes nucleate)
- **Deep extent**: 30-40 km (brittle-ductile transition)

**2025 Narsingdi Earthquake focal depth**: 10 km (mid-seismogenic zone)

### Seismic Potential

- **Historical activity**: M5-6 earthquakes documented
- **Maximum credible earthquake**: M7.0-7.5 (expert estimates)
- **Recurrence interval**: Unknown (insufficient historical data)
- **Risk area**: 10 million people (Dhaka, Gazipur, Mymensingh, Tangail)

---

## 5. Material Properties for DynEarthSol Modeling

### Recommended 5-Layer Structure

#### Layer 1: Alluvium (Hanging Wall + Footwall)
```
Depth: 0-0.5 km
rho0 = 2200 kg/m³
bulk_modulus = 5 GPa (soft)
shear_modulus = 2 GPa
cohesion = 1 MPa (weak)
friction_angle = 20-25°
```

#### Layer 2: Tertiary Sediments (Hanging Wall + Footwall)
```
Depth: 0.5-3 km
rho0 = 2500 kg/m³
bulk_modulus = 15 GPa
shear_modulus = 8 GPa
cohesion = 10 MPa
friction_angle = 25-30°
```

#### Layer 3: Upper Crust (Hanging Wall + Footwall)
```
Depth: 3-15 km
rho0 = 2780 kg/m³
bulk_modulus = 40 GPa (crystalline basement)
shear_modulus = 25 GPa
cohesion = 20 MPa
friction_angle = 30°
```

#### Layer 4: Middle Crust (Hanging Wall + Footwall)
```
Depth: 15-25 km
rho0 = 2830 kg/m³
bulk_modulus = 45 GPa
shear_modulus = 28 GPa
cohesion = 30 MPa
friction_angle = 30-35°
min_viscosity = 1e21 Pa·s (starting to flow)
```

#### Layer 5: Lower Crust (Hanging Wall + Footwall)
```
Depth: 25-100 km
rho0 = 2950 kg/m³
bulk_modulus = 50 GPa
shear_modulus = 30 GPa
cohesion = 40 MPa
friction_angle = 35°
min_viscosity = 1e20 Pa·s (more ductile)
```

### Rate-State Friction Parameters (Fault Zone Only)

**Velocity-weakening zone** (5-20 km depth - seismogenic):
```
direct_a = 0.008
evolution_b = 0.015
(a < b → unstable, generates earthquakes)
```

**Velocity-strengthening zones** (0-5 km, >20 km depth - stable):
```
direct_a = 0.015
evolution_b = 0.012
(a > b → stable, aseismic creep)
```

**Reference velocity**: 1 μm/s (1e-6 m/s)

**State evolution distance**: Dc = 10-20 mm

---

## 6. Boundary Conditions

### Velocity Boundary Conditions

**Convergence rate**: 1 cm/yr total (Indian Plate motion component)

```
Left boundary (x=0):   vx = +0.5 cm/yr = +1.585e-10 m/s
Right boundary (x=200km): vx = -0.5 cm/yr = -1.585e-10 m/s
Bottom (z=100km): vz = 0 (fixed)
Top (z=0): Free surface
```

### Thermal Boundary Conditions

```
Surface temperature: T0 = 273 K (0°C)
Basal temperature (100 km): T100 = 1573 K (1300°C)
Geothermal gradient: ~13°C/km
```

---

## 7. Model Domain Configuration

### 2D Cross-Section (Perpendicular to Fault Strike)

```
Horizontal extent: 200 km (100 km either side of fault)
Vertical extent: 100 km (includes crust + upper mantle)
Fault location: x = 100 km (center)
Fault dip: 40° north-dipping
```

### Mesh Resolution

**For earthquake cycle modeling:**
- Coarse POC: 500 m (797 nodes) - fast, suitable for long-term testing
- Medium: 200 m (3,000-5,000 nodes) - good compromise
- Fine: 100 m (10,000-20,000 nodes) - high resolution, slow

**Requirement**: At least 5 elements across nucleation zone (~2-5 km for typical RSF parameters)

---

## 8. Scientific Objectives

### Short-term (POC)
1. Verify model setup with realistic structure
2. Demonstrate stress accumulation on Madhupur Fault
3. Generate synthetic earthquake cycles
4. Compare synthetic vs. 2025 Narsingdi M5.4

### Long-term (Publication-quality)
1. Estimate maximum credible earthquake (MCE)
2. Calculate recurrence intervals
3. Assess seismic hazard for Dhaka metropolitan area
4. Explore effect of sediment structure on ground motion amplification

---

## References

1. **Crustal Structure:**
   - [Crustal structure and tectonics of Bangladesh (2016)](https://www.sciencedirect.com/science/article/abs/pii/S0040195116301184)
   - [Receiver function study (2016)](https://www.researchgate.net/publication/302905450)

2. **Bengal Basin Synthesis:**
   - [Tectonic and Structural Elements (2018)](https://link.springer.com/chapter/10.1007/978-3-319-99341-6_6)
   - [Sedimentary geology overview (2003)](https://www.sciencedirect.com/science/article/abs/pii/S003707380200180X)

3. **Density Models:**
   - [Crustal density model West Bengal (1997)](https://link.springer.com/article/10.1007/BF02841734)

4. **2025 Narsingdi Earthquake:**
   - [USGS Event Page](https://earthquake.usgs.gov/earthquakes/eventpage/us6000rpht)
   - [Wikipedia article](https://en.wikipedia.org/wiki/2025_Bangladesh_earthquake)
   - [Expert analysis](https://www.tbsnews.net/features/panorama/whats-behind-consecutive-earthquakes-bangladesh-1292131)

---

## Document History

- **Created**: December 15, 2024
- **Author**: DynEarthSol Bengal Basin Project
- **Purpose**: Provide geological constraints for earthquake cycle modeling
- **Last Updated**: December 15, 2024

---

## Notes for Modelers

1. **Simplified vs. Reality**: This model simplifies complex 3D geology to 2D cross-section
2. **Lateral variations**: Real basin has significant E-W variations not captured in 2D
3. **Fault geometry**: Actual fault may have multiple splays and bends
4. **RSF parameters**: Laboratory-derived, may differ from in-situ values
5. **Validation needed**: Synthetic earthquakes should match observed seismicity patterns

**Recommendation**: Start with coarse POC model, then increase resolution and complexity as validation improves.
