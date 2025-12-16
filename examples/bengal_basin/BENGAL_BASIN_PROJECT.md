# Bengal Basin Earthquake Modeling Project

**Motivation:** Recent Narsingdi earthquake (November 21, 2025, M5.4) and ongoing seismic hazard  
**Goal:** Develop physics-based earthquake simulation for Bengal Basin using DynEarthSol  
**Impact:** Seismic hazard assessment for 170+ million people in Bangladesh

---

## Executive Summary

This project proposes using DynEarthSol to model earthquake cycles and stress accumulation in the Bengal Basin, with focus on the recent **November 21, 2025 Narsingdi earthquake (M5.4)** and major active fault systems. The code already has **rate-and-state friction (RSF)** capability for earthquake modeling, making it ideal for this application.

### Key Innovation
- **First physics-based** earthquake cycle model for Bengal Basin
- Combines **tectonic loading + rate-and-state friction** to predict seismic hazard
- Integrates **open seismic data** (USGS, BMD) with geophysical constraints
- **GPU-accelerated** for parameter exploration and uncertainty quantification

---

## 1. Recent Earthquake Context

### Narsingdi Earthquake (November 21, 2025)

**Details:**
- **Magnitude:** M5.4 (USGS), ML5.7 (Bangladesh Meteorological Department)
- **Location:** 14 km SW of Narsingdi (23.86°N, 90.70°E)
- **Depth:** 10 km (shallow crustal)
- **Mechanism:** Reverse faulting in the Indian plate
- **Duration:** 26 seconds of shaking

**Impact:**
- **Deaths:** 10 people (5 in Narsingdi, 4 in Dhaka, 1 in Narayanganj)
- **Injuries:** 629+ across Bangladesh
- **Significance:** Strongest earthquake in recent Bangladesh history

**Aftershocks:**
- ML4.3 on November 22, 2025 (epicenter in Narsingdi)
- Multiple smaller events

**Expert Assessment:**
> "Less than 1% of stored energy was released. High possibility of M8.2-9 earthquake in near geological future." - Humayun Akhtar, earthquake expert

### Why This Matters
Bangladesh is one of the most densely populated regions globally (~1,200 people/km²). A M7+ earthquake near Dhaka could affect **10+ million people**. Understanding stress accumulation and earthquake cycles is critical.

---

## 2. Tectonic Setting of Bengal Basin

### Plate Boundary Configuration

Bengal Basin sits at the **triple junction** of:
1. **Eurasian Plate** (north)
2. **Indian Plate** (west/south)
3. **Burmese Plate** (east)

### Key Geological Features

**Basin characteristics:**
- One of the world's largest sedimentary basins
- **Sediment thickness:** ~22 km (among the thickest globally)
- Formed by collision of Indian and Eurasian plates
- Active since ~50 Ma (India-Asia collision)

**Structural boundaries:**
- **North:** Shillong Plateau with Dauki Fault
- **East:** Chittagong-Tripura Fold Belt (Indo-Burman Ranges)
- **West/South:** Stable Indian craton
- **Interior:** Network of buried faults

---

## 3. Major Active Fault Systems

### 3.1 Dauki Fault (Shillong Plateau Southern Margin)

**Characteristics:**
- **Orientation:** E-W trending
- **Type:** Thrust fault (reverse faulting)
- **Width:** 5-6 km fault zone
- **Dip:** ~45° north-dipping
- **Slip rate:** ~2-6 mm/yr

**Seismic History:**
- **1897 Assam Earthquake:** M8.1 (most recent major event)
- **16th century event:** Confirmed by trench investigation at Gabrakhari
- **Recurrence interval:** 350-700 years
- **Elapsed time:** 128 years since 1897 → **stress building up**

**Hazard:**
- Capable of M7.5-8.5 earthquakes
- Affects northern Bangladesh (Sylhet, Mymensingh divisions)

### 3.2 Madhupur Fault (Intra-plate)

**Characteristics:**
- **Orientation:** N-S trending
- **Type:** Blind thrust (buried fault)
- **Location:** Runs through Madhupur Tract, east of Dhaka
- **Depth:** 10-15 km

**Seismic History:**
- **1885 Bengal Earthquake:** M7.0 (attributed to this fault)
- **Recurrence interval:** Several thousand years (longer than Dauki)
- **Elapsed time:** 140 years since 1885

**Hazard:**
- Capable of M6.5-7.5 earthquakes
- **Critical:** Runs near Dhaka metro (10+ million people)
- 2025 Narsingdi earthquake may be related to this fault system

### 3.3 Other Significant Faults

| Fault | Type | Orientation | Hazard Level |
|-------|------|-------------|--------------|
| **Padma Fault** | Strike-slip | WNW-ESE | Moderate (M6-6.5) |
| **Dhaleswari Fault** | Normal/strike-slip | WNW-ESE | Moderate (M5.5-6.5) |
| **Bogra Fault System** | Reverse | NW-SE | Moderate-High (M6.5-7) |
| **Jamuna Fault** | Strike-slip | N-S | Moderate (M6-6.5) |
| **Haluaghat Fault** | Thrust | E-W | Moderate (M6-6.5) |

---

## 4. Available Open Data Sources

### 4.1 Seismic Catalogs (FREE & OPEN)

**USGS Earthquake Catalog:**
- URL: https://earthquake.usgs.gov/earthquakes/search/
- **Coverage:** Global, 1900-present
- **Bangladesh events:** 500+ earthquakes M4+ since 1900
- **Format:** CSV, GeoJSON, KML
- **Parameters:** Location, depth, magnitude, mechanism (for M5.5+)

**ISC Bulletin (International Seismological Centre):**
- URL: http://www.isc.ac.uk/iscbulletin/
- **Coverage:** 1900-present, more detailed than USGS
- **Reviewed catalog:** Higher quality locations
- **Format:** CSV, QuakeML

**Bangladesh Meteorological Department (BMD):**
- Local catalog with more events (lower magnitude threshold)
- May require direct request

### 4.2 Focal Mechanisms (Fault Orientations)

**Global CMT Catalog:**
- URL: https://www.globalcmt.org/
- **Coverage:** M5.5+ events since 1976
- **Data:** Strike, dip, rake (fault geometry)
- **Bangladesh:** ~20 events with focal mechanisms

**Format example for Narsingdi 2025:**
```
Strike: 280°, Dip: 40°, Rake: 85° (reverse faulting)
Nodal plane: N80°E striking, 40° north-dipping
```

### 4.3 GPS/Geodesy Data

**UNAVCO (University NAVSTAR Consortium):**
- URL: https://www.unavco.org/
- **Limited in Bangladesh**, but some stations in:
  - Dhaka
  - Chittagong
  - Sylhet

**Expected velocities:**
- Indian plate: ~45 mm/yr northward
- Local strain rate: ~10⁻⁸ /yr (very slow)

### 4.4 Geological/Geophysical Data

**GEM (Global Earthquake Model) Active Faults Database:**
- URL: https://github.com/GEMScienceTools/gem-global-active-faults
- **Bangladesh faults:** Partial coverage (Dauki, some others)
- **Format:** Shapefile, GeoJSON

**USGS Slab2 Model:**
- URL: https://www.sciencebase.gov/catalog/item/5aa1b00ee4b0b1c392e86467
- **Subduction geometry:** For Burma subduction zone (eastern boundary)

**ETOPO1 Global Relief:**
- URL: https://www.ngdc.noaa.gov/mgg/global/
- **Topography/bathymetry:** 1 arc-minute resolution
- Useful for mesh generation

### 4.5 Academic Publications (Open Access)

Recent papers with data/models:

1. **"Probabilistic seismic hazard mapping for Bangladesh"** (2025)
   - Updated fault source models
   - Recurrence parameters (a-value, b-value)
   
2. **"Crustal structure of Bangladesh from receiver functions"** (2016)
   - Moho depth: 35-42 km
   - Crustal velocity structure

3. **"Site-specific seismic hazard of Bengal Basin"** (Frontiers, 2022)
   - Soil amplification factors
   - Vs30 maps

---

## 5. DynEarthSol Capabilities for Earthquake Modeling

### 5.1 Rate-and-State Friction (RSF)

DynEarthSol **already has RSF implemented!**

**Location:** `examples/rate_and_state_friction/`

**Rheology option:**
```cfg
[mat]
rheology_type = elasto-plastic-rsf
```

**RSF Parameters:**
```cfg
direct_a = [0.01, 0.015, 0.01]      # Direct effect (instantaneous response)
evolution_b = [0.012, 0.018, 0.012] # Evolution effect (time-dependent)
```

**Friction behavior:**
- **Velocity-weakening** (a < b): Unstable → **Earthquakes**
- **Velocity-strengthening** (a > b): Stable → **Aseismic creep**

This is **exactly what's needed** for earthquake cycle modeling!

### 5.2 Stick-Slip Earthquake Cycles

Example already exists: `vel_weakening/rsf_tri_layer_shear_test_vel_weakening.cfg`

**What it does:**
1. Apply slow tectonic loading (e.g., 1 cm/yr)
2. Fault initially locked (friction > driving stress)
3. Stress builds up over years/decades
4. **Nucleation:** Small patch starts slipping
5. **Dynamic rupture:** Earthquake propagates
6. **Post-seismic:** Fault re-locks, cycle repeats

**Output:**
- Slip history (seismograms)
- Recurrence intervals
- Stress evolution
- Magnitude-frequency distribution

### 5.3 Full Thermomechanical Coupling

Unlike most earthquake codes, DynEarthSol includes:
- **Energy balance equation** (shear heating)
- **Temperature-dependent rheology**
- **Viscous relaxation** in lower crust/mantle

**Why this matters for Bengal Basin:**
- Thick sediments (22 km) → thermal insulation
- Affects fault strength at depth
- Post-seismic relaxation timescales

---

## 6. Proposed Modeling Strategy

### Phase 1: Single Fault Model (3 months)

**Objective:** Reproduce 2025 Narsingdi earthquake

**Setup:**
- **Geometry:** 2D cross-section through Madhupur Fault
- **Domain:** 200 km × 100 km (horizontal × vertical)
- **Fault:** 40° dipping thrust, 10-30 km depth range
- **Loading:** 1 cm/yr convergence (Indian plate motion)

**Model configuration:**
```cfg
[mesh]
xlength = 200e3
ylength = 100e3
resolution = 500  # 500 m resolution near fault

[mat]
rheology_type = elasto-plastic-rsf
num_materials = 4  # Upper crust, lower crust, fault core, fault damage zone

# Fault core: velocity-weakening
direct_a = [0.01, 0.01, 0.008, 0.01]
evolution_b = [0.012, 0.012, 0.015, 0.012]

# Realistic properties
rho0 = [2500, 2700, 2600, 2600]  # kg/m³
bulk_modulus = [30e9, 50e9, 40e9, 40e9]
shear_modulus = [20e9, 30e9, 25e9, 25e9]

[bc]
vbc_x0 = 3  # Horizontal velocity at left boundary
vbc_val_x0 = -3.17e-10  # 1 cm/yr

[control]
max_time_in_yr = 5000  # Simulate 5000 years
inertial_scaling = 1e5  # For quasi-dynamic earthquakes
```

**Expected results:**
- Earthquake cycles every 500-2000 years
- M5-6 events (consistent with 2025 Narsingdi)
- Stress accumulation patterns
- Comparison with USGS focal mechanism

### Phase 2: Multi-Fault System (6 months)

**Objective:** Regional model with fault interactions

**Faults included:**
1. Madhupur Fault (blind thrust)
2. Dauki Fault (plate boundary)
3. Padma Fault (strike-slip)
4. Jamuna Fault (strike-slip)

**Setup:**
- **3D model** (200 km × 200 km × 100 km)
- **GPU-accelerated** (RTX 2080 Ti → cluster)
- **Realistic fault geometry** from GEM database

**Key questions:**
- Do faults interact? (Coulomb stress transfer)
- What's the probability of M7+ event?
- Which fault poses highest hazard to Dhaka?

### Phase 3: Seismic Hazard Assessment (6 months)

**Objective:** Probabilistic hazard maps

**Approach:**
1. Run 100+ simulations with varied parameters:
   - Fault friction (a, b values)
   - Loading rate (GPS uncertainty)
   - Initial stress state
2. Generate synthetic earthquake catalogs (10,000 years)
3. Calculate:
   - Peak ground acceleration (PGA)
   - Spectral acceleration at different periods
   - Probability of exceeding threshold in 50 years

**Output:**
- Seismic hazard maps for Bangladesh
- Comparison with existing hazard models
- **Policy-relevant:** Building code recommendations

---

## 7. Data Integration Workflow

### Step 1: Compile Seismic Catalog

```python
# Download USGS data
import urllib.request
import pandas as pd

url = "https://earthquake.usgs.gov/fdsnws/event/1/query?"
params = {
    'starttime': '1900-01-01',
    'endtime': '2025-12-31',
    'minlatitude': 20.0,
    'maxlatitude': 27.0,
    'minlongitude': 87.0,
    'maxlongitude': 93.0,
    'minmagnitude': 4.0,
    'format': 'csv'
}

catalog = pd.read_csv(url + '&'.join([f"{k}={v}" for k,v in params.items()]))
catalog.to_csv('bangladesh_earthquakes_1900_2025.csv')
```

### Step 2: Extract Fault Geometry from Focal Mechanisms

```python
# For Narsingdi 2025 earthquake
focal_mechanism = {
    'strike': 280,  # N80°E
    'dip': 40,      # 40° north-dipping
    'rake': 85      # Reverse faulting
}

# Use in DynEarthSol mesh generation
# Fault orientation matches this geometry
```

### Step 3: Constrain Model with Geodesy

```python
# GPS velocity field (if available)
# Partition into elastic strain accumulation
# Infer locking depth on faults
```

### Step 4: Calibrate Friction Parameters

Use observed recurrence intervals:
- Dauki: 350-700 years → tune (a,b) to match
- Madhupur: 1000s of years → different friction

---

## 8. Expected Scientific Outcomes

### 8.1 Publications (3-4 papers)

**Paper 1:** "Physics-based earthquake cycle modeling for Bengal Basin" (JGR: Solid Earth)
- First RSF model for Bangladesh
- Reproduce 2025 Narsingdi earthquake
- Validate against seismic/geodetic data

**Paper 2:** "Seismic hazard from multi-fault interactions in Bengal Basin" (BSSA)
- 3D model with fault network
- Stress transfer between faults
- Probability of cascading ruptures

**Paper 3:** "Updated seismic hazard maps for Bangladesh" (Nature Geoscience / Seismological Research Letters)
- Probabilistic hazard assessment
- Policy implications
- Comparison with existing models

**Paper 4:** "Thermal effects on earthquake cycles in thick sedimentary basins" (Tectonophysics)
- Role of thermal structure (22 km sediments!)
- Lower crustal/mantle relaxation
- Methodological contribution

### 8.2 Societal Impact

**Direct applications:**
- **Building codes:** Inform seismic design requirements
- **Emergency planning:** Identify high-risk areas
- **Infrastructure:** Prioritize retrofitting in Dhaka metro area
- **Insurance:** Risk assessment for coverage

**Stakeholders:**
- Bangladesh Meteorological Department (BMD)
- Disaster Management Ministry
- Dhaka city planning authorities
- International development banks (World Bank, ADB)

### 8.3 Methodology Advancement

**Novel contributions:**
- First thermomechanical earthquake model for thick sedimentary basin
- GPU-accelerated RSF for uncertainty quantification
- Open-source workflow (reproducible science)

---

## 9. Comparison with Existing Approaches

### Current Hazard Models for Bangladesh

Most use **empirical methods:**
1. **Gutenberg-Richter relation:** Statistical (a-value, b-value)
2. **Seismic zonation:** Divide region into zones, assign hazard
3. **Ground motion prediction equations (GMPEs):** Empirical attenuation

**Limitations:**
- ❌ Don't capture fault-specific physics
- ❌ Struggle with low-seismicity regions (sparse data)
- ❌ Can't predict fault interactions
- ❌ No physical basis for recurrence intervals

### DynEarthSol Physics-Based Approach

**Advantages:**
- ✅ **Fault-specific:** Each fault has distinct behavior
- ✅ **Physics-based:** RSF governs earthquake cycles
- ✅ **Predictive:** Can extrapolate beyond historical record
- ✅ **Captures interactions:** Coulomb stress transfer
- ✅ **Uncertainty quantification:** Run ensembles on GPU

**Example:**
> "The Madhupur fault hasn't ruptured in 140 years (since 1885). Is it overdue?"

- **Empirical model:** Can't answer (need more earthquakes for statistics)
- **Physics-based model:** Calculate stress accumulation rate → estimate probability

---

## 10. Technical Implementation Plan

### Month 1-2: Setup & Validation
- [ ] Install DynEarthSol with RSF on GPU
- [ ] Run existing stick-slip examples
- [ ] Compile Bangladesh earthquake catalog
- [ ] Download fault maps and geodetic data

### Month 3-4: Single Fault Model
- [ ] Create 2D mesh for Madhupur Fault
- [ ] Calibrate friction parameters
- [ ] Run 5000-year simulation
- [ ] Compare with 2025 Narsingdi earthquake

### Month 5-7: Multi-Fault Model
- [ ] Extend to 3D geometry
- [ ] Include Dauki + Madhupur + Padma faults
- [ ] Test fault interactions
- [ ] Optimize on GPU cluster

### Month 8-10: Hazard Assessment
- [ ] Parameter ensemble (100+ runs)
- [ ] Synthetic catalog generation
- [ ] Ground motion calculation
- [ ] Hazard map production

### Month 11-12: Publication & Outreach
- [ ] Write papers
- [ ] Present to BMD and stakeholders
- [ ] Open-source release (code + data)
- [ ] Policy brief for government

---

## 11. Resource Requirements

### Computational
- **Development:** Mac + RTX 2080 Ti (local testing)
- **Production:** GPU cluster (for ensembles)
  - ~1000 GPU-hours for single fault
  - ~10,000 GPU-hours for multi-fault + uncertainty

### Data Storage
- **Input:** ~1 GB (catalogs, DEMs, fault traces)
- **Output:** ~100 GB (VTK files for 100 simulations)

### Personnel
- 1 PhD student / Postdoc (full-time, 12 months)
- Access to seismology expertise
- Collaboration with BMD (data access)

### Funding Opportunities
- **NSF PREEVENTS:** Natural hazard prediction
- **USAID:** Disaster risk reduction in Bangladesh
- **World Bank GFDRR:** Global Facility for Disaster Reduction
- **Royal Society:** International collaboration grants

---

## 12. Potential Challenges & Solutions

### Challenge 1: Limited Geodetic Data in Bangladesh

**Problem:** Few GPS stations → poorly constrained loading rates

**Solution:**
- Use plate motion models (UNAVCO, GSRM)
- Explore parameter space (ensemble approach)
- Focus on relative hazard (fault A vs. fault B)

### Challenge 2: Uncertain Fault Geometry

**Problem:** Many faults are buried (thick sediments) → poor surface expression

**Solution:**
- Use seismic reflection data (if accessible)
- Infer from earthquake locations (USGS catalog)
- Test multiple geometries (sensitivity analysis)

### Challenge 3: Computational Cost

**Problem:** 3D multi-fault models are expensive

**Solution:**
- **GPU acceleration** (10-20x speedup)
- Hierarchical approach (2D → 3D)
- Focus on key faults (Madhupur, Dauki)

### Challenge 4: Validating Against Sparse Historical Record

**Problem:** Only ~100 years of instrumental data

**Solution:**
- Use paleoseismic data (where available)
- Compare statistical properties (magnitude-frequency)
- Focus on physics validation (stress drop, slip, etc.)

---

## 13. Quick Start: Minimal Viable Model

Want to start immediately? Here's a **1-week proof-of-concept:**

### Simple 2D Madhupur Fault Model

```bash
cd ~/Documents/dynearthsol_energy/examples

# Create bengal_basin directory
mkdir bengal_basin
cd bengal_basin

# Copy rate-and-state friction template
cp ../rate_and_state_friction/vel_weakening/rsf_tri_layer_shear_test_vel_weakening.cfg \
   madhupur_fault.cfg

# Edit configuration (see below)
```

**Minimal configuration (`madhupur_fault.cfg`):**

```cfg
[sim]
modelname = bengal_madhupur
max_time_in_yr = 2000
output_time_interval_in_yr = 10

[mesh]
meshing_option = 91
poly_filename = madhupur_fault.poly
resolution = 1e3  # 1 km resolution
xlength = 200e3
ylength = 100e3

[mat]
rheology_type = elasto-plastic-rsf
num_materials = 2

# Crust (stable)
direct_a = [0.015, 0.008]
evolution_b = [0.012, 0.015]  # Fault: velocity-weakening (a<b)

rho0 = [2600]
bulk_modulus = [40e9]
shear_modulus = [25e9]

[bc]
# Simulate 1 cm/yr convergence
vbc_x0 = 3
vbc_val_x0 = -3.17e-10  # m/s

[control]
inertial_scaling = 1e5  # Quasi-dynamic
```

**Create fault geometry (`madhupur_fault.poly`):**

```
# 2D cross-section: 200 km wide, 100 km deep
4 2 0 0
1  0.0  0.0
2  200e3  0.0
3  200e3  -100e3
4  0.0  -100e3

4 1
1  1 2 1    # Surface
2  2 3 1    # Right boundary
3  3 4 1    # Bottom
4  4 1 1    # Left boundary

1              # 1 fault
4              # 4 points for fault
1  100e3  -10e3  # Fault top (10 km depth)
2  120e3  -20e3  # Fault segment
3  140e3  -30e3
4  160e3  -40e3  # Fault bottom (40 km depth, 40° dip)
```

**Run:**
```bash
../../dynearthsol2d madhupur_fault.cfg
```

**Expected output:**
- Earthquake every ~500-1000 years
- Magnitude ~M5-6 (similar to Narsingdi 2025)
- Slip vs. time showing stick-slip cycles

---

## 14. Timeline to First Results

| Milestone | Time | Deliverable |
|-----------|------|-------------|
| Setup environment | 1 week | GPU build working |
| Simple fault model | 2 weeks | Earthquake cycles reproduced |
| Calibrate to Narsingdi | 1 month | Match M5.4 event |
| Multi-fault prototype | 3 months | 3D model with 2-3 faults |
| Hazard maps (draft) | 6 months | Preliminary seismic hazard |
| **First paper** | **9 months** | Submitted to journal |
| Full hazard assessment | 12 months | Policy-ready product |

---

## 15. Collaboration Opportunities

### Academic Partners (Bangladesh)
- **BUET (Bangladesh University of Engineering and Technology)**
  - Department of Civil Engineering
  - Earthquake Engineering Research
  
- **University of Dhaka**
  - Department of Geology
  - Institute of Disaster Management

### Government Agencies
- **Bangladesh Meteorological Department (BMD)**
  - Seismic data access
  - Validation and feedback
  
- **Disaster Management & Relief Ministry**
  - Policy implementation
  - Hazard communication

### International Collaborators
- **USGS** (earthquake hazards program)
- **GEM Foundation** (Global Earthquake Model)
- **UNAVCO** (geodesy)

---

## 16. Summary & Recommendation

### Why This Project Matters

1. **Urgent need:** Bangladesh faces M7+ earthquake risk
2. **Recent event:** 2025 Narsingdi (M5.4) highlights vulnerability
3. **Dense population:** 170+ million people at risk
4. **Limited understanding:** Few physics-based models exist
5. **Open data available:** Can start immediately

### Why DynEarthSol is Ideal

1. ✅ **Rate-and-state friction:** Already implemented
2. ✅ **Thermomechanical:** Handles thick sediments (22 km)
3. ✅ **GPU support:** Fast enough for ensembles
4. ✅ **Open-source:** Reproducible science
5. ✅ **Proven:** Used for subduction zones (Tonga)

### Recommended Action Plan

**Immediate (1 month):**
1. Set up GPU environment (RTX 2080 Ti)
2. Run existing RSF examples
3. Download Bangladesh earthquake catalog
4. Create simple Madhupur fault model

**Short-term (3 months):**
1. Calibrate to 2025 Narsingdi earthquake
2. Test parameter sensitivity
3. Write technical report

**Medium-term (6-12 months):**
1. Expand to multi-fault system
2. Run ensemble on cluster
3. Publish first paper

### Expected Impact

- **Science:** 3-4 high-impact publications
- **Society:** Improved hazard maps for building codes
- **Methodology:** New approach for low-seismicity regions
- **Capacity building:** Train Bangladeshi researchers

---

## Resources & Links

### Data Sources
- [USGS Earthquake Catalog](https://earthquake.usgs.gov/earthquakes/search/)
- [Global CMT (Focal Mechanisms)](https://www.globalcmt.org/)
- [GEM Active Faults Database](https://github.com/GEMScienceTools/gem-global-active-faults)
- [ISC Bulletin](http://www.isc.ac.uk/iscbulletin/)

### Key Publications
- [2025 Bangladesh earthquake - Wikipedia](https://en.wikipedia.org/wiki/2025_Bangladesh_earthquake)
- [Probabilistic seismic hazard mapping for Bangladesh (2025)](https://www.tandfonline.com/doi/full/10.1080/19475705.2025.2454537)
- [Active fault map of Bangladesh (ResearchGate)](https://www.researchgate.net/figure/a-An-active-fault-map-of-Bangladesh-The-Dauki-fault-passes-along-the-southern-margin_fig1_263391442)
- [Crustal structure of Bangladesh from receiver functions (2016)](https://www.sciencedirect.com/science/article/abs/pii/S0040195116301184)
- [Site-specific seismic hazard of Bengal Basin (Frontiers, 2022)](https://www.frontiersin.org/journals/earth-science/articles/10.3389/feart.2022.959108/full)

### DynEarthSol Resources
- Main repository: Check examples/rate_and_state_friction/
- GPU guide: `GPU_SETUP_GUIDE.md` (created earlier)

---

**Contact for collaboration:**
- Bangladesh Meteorological Department: http://www.bmd.gov.bd/
- BUET Earthquake Engineering: http://cee.buet.ac.bd/

---

**Next Steps:**
1. Review this document
2. Decide on scope (single fault vs. multi-fault)
3. Set up development environment
4. Start with minimal viable model (1-2 weeks)
5. Iterate based on results

**Let's build something impactful! 🇧🇩🌍**
