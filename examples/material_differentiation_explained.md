# Material Property Differentiation: Slab vs Wedge

## Why Some Properties Are the Same

In a 2-material subduction model, **both materials are essentially mantle rock** (peridotite/olivine). The main difference is:
1. **Temperature**: Slab is cold, wedge is hot
2. **Hydration**: Wedge is hydrated by slab dewatering
3. **Stress state**: Different deformation regimes

### Properties That SHOULD Be the Same:

| Property | Value | Why Same? |
|----------|-------|-----------|
| **Density** (rho0) | 3300 kg/m³ | Both are upper mantle peridotite. Density differences come from thermal expansion (ρ = ρ₀(1 - αΔT)), not material type |
| **Thermal expansion** (alpha) | 3.0×10⁻⁵ K⁻¹ | Intrinsic property of olivine crystal structure |
| **Bulk modulus** | 50 GPa | Elastic property of olivine, not strongly affected by hydration |
| **Shear modulus** | 30 GPa | Elastic property of olivine |
| **Heat capacity** | 1000 J/kg/K | Intrinsic thermal property of mantle rocks |
| **Thermal conductivity** | 3.3 W/m/K | Similar for dry vs wet mantle (difference ~10%, not critical) |
| **Dilation angle** | 0° | Volume-conserving deformation at mantle depths |

**Key Point**: Temperature-dependent density variations are calculated dynamically as:
```
ρ(T) = ρ₀ × [1 - α(T - T₀)]
```
So even with same ρ₀, cold slab is denser than hot wedge!

---

## Properties That SHOULD Be Different

### 1. Viscosity Parameters ✓ (UPDATED)

**Why different?** Hydration dramatically affects viscosity

| Parameter | Mat 0 (Slab) | Mat 1 (Wedge) | Ratio |
|-----------|--------------|---------------|-------|
| **Activation Energy** | 5.3×10⁵ J/mol | 4.8×10⁵ J/mol | 1.1× |
| **Type** | Dry olivine | Wet olivine | - |
| **Viscosity at 1000 K** | ~10²¹ Pa·s | ~10¹⁹ Pa·s | 100× |
| **Viscosity at 1500 K** | ~10¹⁹ Pa·s | ~10¹⁸ Pa·s | 10× |

**Reference**: Hirth & Kohlstedt (2003)
- Dry olivine: E = 530 kJ/mol (strong when cold)
- Wet olivine: E = 480 kJ/mol (weak even when hot)
- Water content in wedge: 100-1000 ppm H/Si

---

### 2. Plastic Yield Properties ✓ (UPDATED)

**Why different?** Hydration weakens plastic strength

#### Cohesion

| | Mat 0 (Slab) | Mat 1 (Wedge) | Justification |
|-|--------------|---------------|---------------|
| **Initial** | 40 MPa | 20 MPa | Hydration reduces cohesion by ~50% |
| **Final** | 4 MPa | 2 MPa | Same weakening ratio |

**Literature basis**:
- Dry mantle rocks: 40-100 MPa (Ranalli 1995)
- Hydrated/serpentinized: 10-40 MPa (50-75% reduction)
- Fully serpentinized: <10 MPa

#### Friction Angle

| | Mat 0 (Slab) | Mat 1 (Wedge) | Justification |
|-|--------------|---------------|---------------|
| **Angle** | 30° | 15° | Hydration reduces friction coefficient |

**Literature basis**:
- Byerlee's law (dry rocks): μ = 0.6-0.85 → φ = 30-40°
- Hydrated mantle: μ = 0.27 → φ = 15°
- Serpentinized: μ = 0.2-0.3 → φ = 11-17°

**Reference**: Moore et al. (1997), Collettini et al. (2009)

---

## Physical Interpretation

### Material 0: OCEANIC LITHOSPHERE (Cold Slab)
```
Composition: Dry peridotite
Temperature: 700-1000 K
Hydration: Minimal (<100 ppm H₂O)
State: Cold, strong, rigid

Rheology:
  • Viscous: High activation energy (530 kJ/mol)
            → Very temperature-sensitive
            → Strong when cold (10²⁰-10²¹ Pa·s)

  • Plastic: High cohesion (40 MPa)
             High friction (30°)
             → Strong yield strength
             → Resists deformation until high stress

Behavior: Acts as rigid plate, bends elastically
```

### Material 1: ASTHENOSPHERIC MANTLE (Hot Wedge)
```
Composition: Hydrated peridotite (± serpentine)
Temperature: 1200-1600 K
Hydration: High (100-1000 ppm H₂O)
State: Hot, weak, flowing

Rheology:
  • Viscous: Lower activation energy (480 kJ/mol)
            → Less temperature-sensitive
            → Weak even when warm (10¹⁸-10¹⁹ Pa·s)

  • Plastic: Low cohesion (20 MPa)
             Low friction (15°)
             → Low yield strength
             → Deforms easily, flows around slab

Behavior: Convects in corner flow, weak coupling with slab
```

---

## Summary of Material Contrast

| Property | Slab/Wedge Ratio | Effect |
|----------|------------------|--------|
| **Viscosity** (at same T) | 10-100× | Slab is much stronger |
| **Cohesion** | 2× | Slab is twice as strong plastically |
| **Friction** | 2× (tan30°/tan15°) | Slab has higher friction |
| **Combined** | **Very strong contrast** | Enables decoupling, corner flow |

---

## Expected Simulation Behavior

With these differentiated properties:

1. **Slab Behavior**:
   - Rigid when cold
   - High viscosity (10²⁰-10²¹ Pa·s)
   - Minimal internal deformation
   - Bends elastically at trench

2. **Wedge Behavior**:
   - Weak and flowing
   - Low viscosity (10¹⁸-10¹⁹ Pa·s)
   - Strong internal deformation
   - Corner flow circulation

3. **Interface**:
   - Large viscosity contrast → stress localization
   - Low friction in wedge → decoupling
   - High strain rates → potential for thermal runaway

4. **Thermal Structure**:
   - Cold slab maintains low temperature (conduction)
   - Hot wedge maintains high temperature (advection)
   - Sharp thermal boundary at interface

---

## Why This Matters for Thermal Runaway

**Thermal runaway** occurs when: Viscous heating > Heat conduction

With realistic differentiation:
- ✓ **High strain rates** at interface (large viscosity contrast)
- ✓ **Temperature-sensitive viscosity** (high activation energy)
- ✓ **Positive feedback**: heating → lower viscosity → more deformation → more heating

The differentiated properties create the conditions necessary for thermal runaway:
1. Strong cold slab (high viscosity)
2. Weak hot wedge (low viscosity)
3. Concentrated deformation at interface
4. Strong thermal-mechanical coupling

---

## References

1. **Hirth, G., & Kohlstedt, D. L. (2003)**. Rheology of the upper mantle and the mantle wedge. AGU Monograph 138, 83-105.

2. **Ranalli, G. (1995)**. Rheology of the Earth (2nd ed.). Chapman & Hall.

3. **Moore, D. E., et al. (1997)**. The role of serpentinization in the deformation of subduction zones. Geology, 25(5), 459-462.

4. **Collettini, C., et al. (2009)**. Fault zone fabric and fault weakness. Nature, 462(7275), 907-910.

5. **Billen, M. I., & Gurnis, M. (2001)**. A low viscosity wedge in subduction zones. EPSL, 193(1-2), 227-236.
