#!/bin/bash
#
# DynEarthSol Energy Balance Analysis Suite
# 
# Runs comprehensive analysis on simulation results including:
# - Basic field analysis and comparison
# - Energy balance interpretation
# - Thermal-mechanical feedback analysis
#
# Usage:
#   ./run_analysis.sh experiment1 [experiment2 ...]
#
# Examples:
#   ./run_analysis.sh energy                    # Analyze single experiment
#   ./run_analysis.sh energy no_energy          # Compare two experiments
#   ./run_analysis.sh exp1 exp2 exp3            # Analyze multiple experiments
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ANALYTICS_DIR="${SCRIPT_DIR}"

# Check if analytics directory exists
if [ ! -d "$ANALYTICS_DIR" ]; then
    echo -e "${RED}Error: analytics directory not found!${NC}"
    echo "Expected location: $ANALYTICS_DIR"
    exit 1
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 not found!${NC}"
    echo "Please install Python 3 to run analysis scripts."
    exit 1
fi

# Check for required Python packages
echo -e "${BLUE}Checking Python dependencies...${NC}"
python3 -c "import numpy, matplotlib, scipy" 2>/dev/null || {
    echo -e "${YELLOW}Warning: Some Python packages may be missing.${NC}"
    echo "Required: numpy, matplotlib, scipy"
    echo "Install with: pip3 install numpy matplotlib scipy"
}

# Parse arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 experiment1 [experiment2 ...]"
    echo ""
    echo "Examples:"
    echo "  $0 energy                    # Analyze single experiment"
    echo "  $0 energy no_energy          # Compare two experiments"
    echo "  $0 exp1 exp2 exp3            # Analyze multiple experiments"
    echo ""
    exit 1
fi

EXPERIMENTS=("$@")
NUM_EXPERIMENTS=${#EXPERIMENTS[@]}

echo ""
echo "========================================================================"
echo "  DynEarthSol Energy Balance Analysis Suite"
echo "========================================================================"
echo ""
echo "Experiments to analyze: ${EXPERIMENTS[*]}"
echo "Number of experiments: $NUM_EXPERIMENTS"
echo ""

# ============================================================================
# 1. Basic Analysis and Comparison
# ============================================================================
echo -e "${GREEN}[1/4] Running basic field analysis...${NC}"
echo "----------------------------------------------------------------------"

cd "$SCRIPT_DIR/.."
python3 "${ANALYTICS_DIR}/analyze_results.py" "${EXPERIMENTS[@]}" || {
    echo -e "${RED}Error running analyze_results.py${NC}"
    exit 1
}

echo ""
echo -e "${GREEN}✓ Basic analysis complete${NC}"
echo ""

# ============================================================================
# 2. Energy Interpretation (for experiments with energy balance)
# ============================================================================
echo -e "${GREEN}[2/4] Running energy balance interpretation...${NC}"
echo "----------------------------------------------------------------------"

for exp in "${EXPERIMENTS[@]}"; do
    # Check if experiment has energy data
    latest_dir=$(ls -dt output/${exp}_* 2>/dev/null | head -n 1)
    
    if [ -n "$latest_dir" ]; then
        # Check if VTK files contain energy fields
        vtk_file=$(ls "$latest_dir"/vtk/*.vtk 2>/dev/null | head -n 1)
        
        if [ -n "$vtk_file" ] && grep -q "SCALARS tenergy" "$vtk_file" 2>/dev/null; then
            echo "Analyzing energy balance for: $exp"
            python3 "${ANALYTICS_DIR}/interpret_energy.py" "$exp" || {
                echo -e "${YELLOW}Warning: Energy interpretation failed for $exp${NC}"
            }
            echo ""
        else
            echo -e "${YELLOW}Skipping $exp (no energy balance data)${NC}"
            echo ""
        fi
    else
        echo -e "${YELLOW}Warning: No output directory found for $exp${NC}"
        echo ""
    fi
done

echo -e "${GREEN}✓ Energy interpretation complete${NC}"
echo ""

# ============================================================================
# 3. Feedback Analysis
# ============================================================================
echo -e "${GREEN}[3/4] Running thermal-mechanical feedback analysis...${NC}"
echo "----------------------------------------------------------------------"

if [ $NUM_EXPERIMENTS -eq 1 ]; then
    # Single experiment
    echo "Analyzing feedback for: ${EXPERIMENTS[0]}"
    python3 "${ANALYTICS_DIR}/analyze_feedback.py" "${EXPERIMENTS[0]}" || {
        echo -e "${YELLOW}Warning: Feedback analysis failed${NC}"
    }
elif [ $NUM_EXPERIMENTS -eq 2 ]; then
    # Two experiments - compare
    echo "Comparing feedback: ${EXPERIMENTS[0]} vs ${EXPERIMENTS[1]}"
    python3 "${ANALYTICS_DIR}/analyze_feedback.py" "${EXPERIMENTS[0]}" "${EXPERIMENTS[1]}" || {
        echo -e "${YELLOW}Warning: Feedback comparison failed${NC}"
    }
else
    # Multiple experiments - analyze each
    for exp in "${EXPERIMENTS[@]}"; do
        echo "Analyzing feedback for: $exp"
        python3 "${ANALYTICS_DIR}/analyze_feedback.py" "$exp" || {
            echo -e "${YELLOW}Warning: Feedback analysis failed for $exp${NC}"
        }
        echo ""
    done
fi

echo ""
echo -e "${GREEN}✓ Feedback analysis complete${NC}"
echo ""

# ============================================================================
# 4. Structural/Fault Analysis (NEW)
# ============================================================================
echo -e "${GREEN}[4/4] Running structural and fault analysis...${NC}"
echo "----------------------------------------------------------------------"

for exp in "${EXPERIMENTS[@]}"; do
    latest_dir=$(ls -dt output/${exp}_* 2>/dev/null | head -n 1)

    if [ -n "$latest_dir" ]; then
        vtk_dir="${latest_dir}/vtk"
        viz_dir="${latest_dir}/viz"

        if [ -d "$vtk_dir" ]; then
            echo "Generating fault development analysis for: $exp"
            python3 "${ANALYTICS_DIR}/plot_fault_development.py" "$vtk_dir" "$viz_dir" || {
                echo -e "${YELLOW}Warning: Fault analysis failed for $exp${NC}"
            }

            echo "Generating field statistics overview for: $exp"
            python3 "${ANALYTICS_DIR}/plot_field_statistics.py" "$vtk_dir" "$viz_dir" || {
                echo -e "${YELLOW}Warning: Field statistics failed for $exp${NC}"
            }
            echo ""
        else
            echo -e "${YELLOW}Warning: No VTK directory found for $exp${NC}"
            echo ""
        fi
    fi
done

echo -e "${GREEN}✓ Structural analysis complete${NC}"
echo ""

# ============================================================================
# Summary
# ============================================================================
echo "========================================================================"
echo "  Analysis Complete!"
echo "========================================================================"
echo ""
echo "Results saved to:"
for exp in "${EXPERIMENTS[@]}"; do
    latest_dir=$(ls -dt output/${exp}_* 2>/dev/null | head -n 1)
    if [ -n "$latest_dir" ]; then
        viz_dir="${latest_dir}/viz"
        if [ -d "$viz_dir" ]; then
            num_plots=$(ls "$viz_dir"/*.png 2>/dev/null | wc -l)
            echo "  • $viz_dir ($num_plots plots)"
        fi
    fi
done

echo ""
echo "Visualizations generated:"
echo "  • temperature_evolution.png       - Temperature over time"
echo "  • velocity_evolution.png          - Velocity over time"
echo "  • energy_terms.png                - Energy balance components"
echo "  • energy_geological_interpretation.png - Energy analysis"
echo "  • feedback_analysis.png           - Thermal-mechanical feedback"
echo "  • field_statistics.png            - Current field overview (NEW)"
echo "  • fault_development.png           - Structural/fault analysis (NEW)"
if [ $NUM_EXPERIMENTS -gt 1 ]; then
    echo "  • comparison_*.png                - Multi-experiment comparisons"
fi

echo ""
echo -e "${GREEN}All analyses completed successfully!${NC}"
echo ""
