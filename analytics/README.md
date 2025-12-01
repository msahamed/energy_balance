# DynEarthSol Analytics Tools

This directory contains Python scripts for analyzing DynEarthSol simulation results with energy balance.

## Scripts

### 1. `analyze_results.py`
**Purpose:** Basic field analysis and multi-experiment comparison

**Features:**
- Parses all VTK fields automatically
- Computes statistics (max, min, mean, std)
- Generates evolution plots
- Supports multi-experiment comparison

**Usage:**
```bash
python3 analyze_results.py experiment1 [experiment2 ...]
```

**Output:**
- `temperature_evolution.png`
- `velocity_evolution.png`
- `pressure_evolution.png`
- `energy_terms.png` (if energy balance enabled)
- `comparison_*.png` (for multiple experiments)

---

### 2. `interpret_energy.py`
**Purpose:** Geological interpretation of energy balance terms

**Features:**
- Analyzes power contributions (thermal, viscous, plastic)
- Identifies dominant deformation mechanism
- Calculates thermal impact
- Provides geological context

**Usage:**
```bash
python3 interpret_energy.py experiment_name
```

**Output:**
- `energy_geological_interpretation.png`
- Console output with geological interpretation

---

### 3. `analyze_feedback.py`
**Purpose:** Thermal-mechanical feedback loop analysis

**Features:**
- Analyzes Power → Temperature coupling
- Analyzes Temperature → Power coupling
- Detects thermal runaway risk
- Identifies strain localization
- Compares feedback between experiments

**Usage:**
```bash
python3 analyze_feedback.py experiment1 [experiment2]
```

**Output:**
- `feedback_analysis.png`
- Console output with feedback interpretation

---

## Quick Start

### Run All Analyses (Recommended)
```bash
cd /path/to/dynearthsol_upstream
./run_analysis.sh energy no_energy
```

This runs all three analysis scripts automatically.

### Individual Analysis
```bash
cd /path/to/dynearthsol_upstream

# Basic analysis
python3 analytics/analyze_results.py energy no_energy

# Energy interpretation
python3 analytics/interpret_energy.py energy

# Feedback analysis
python3 analytics/analyze_feedback.py energy no_energy
```

---

## Requirements

**Python 3.6+** with packages:
- `numpy`
- `matplotlib`
- `scipy`

Install with:
```bash
pip3 install numpy matplotlib scipy
```

---

## Input/Output

### Input
Scripts automatically find the latest timestamped output directory for each experiment:
```
output/
├── energy_20251201_120546/
│   └── vtk/
│       ├── energy_000000.vtk
│       └── ...
└── no_energy_20251201_112012/
    └── vtk/
        └── ...
```

### Output
Visualizations are saved to `viz/` folder within each experiment directory:
```
output/
└── energy_20251201_120546/
    └── viz/
        ├── temperature_evolution.png
        ├── velocity_evolution.png
        ├── energy_terms.png
        ├── energy_geological_interpretation.png
        └── feedback_analysis.png
```

---

## Workflow

### Typical Analysis Workflow

1. **Run simulations:**
   ```bash
   ./dynearthsol2d test_energy.cfg
   ./dynearthsol2d test_no_energy.cfg
   ```

2. **Run complete analysis:**
   ```bash
   ./run_analysis.sh energy no_energy
   ```

3. **Review results:**
   - Check console output for interpretations
   - View plots in `output/*/viz/` folders

---

## Customization

### Analyzing Specific Directories
You can pass full directory paths instead of experiment names:
```bash
python3 analytics/analyze_results.py output/energy_20251201_120546
```

### Custom Output Directory
```bash
python3 analytics/analyze_results.py --output-dir /custom/path energy
```

---

## Interpretation Guides

See the documentation in the parent directory:
- `ENERGY_INTERPRETATION_GUIDE.md` - Energy balance terms explained
- `FEEDBACK_GUIDE.md` - Thermal-mechanical feedback explained

---

## Troubleshooting

**No output directory found:**
- Check experiment name matches config file `modelname`
- Verify simulation completed successfully

**Missing energy fields:**
- Ensure simulation was run with `has_energy_balance = yes`
- Verify code was compiled with `-DENABLE_ENERGY_BALANCE`

**Python errors:**
- Check Python version: `python3 --version` (need 3.6+)
- Install missing packages: `pip3 install numpy matplotlib scipy`

---

## Development

### Adding New Analysis
1. Create new Python script in `analytics/`
2. Import `ExperimentAnalyzer` from `analyze_results.py`
3. Add to `run_analysis.sh` if desired

### Example:
```python
from analyze_results import ExperimentAnalyzer

analyzer = ExperimentAnalyzer('energy')
analyzer.analyze()
# Access data via analyzer.data
```
