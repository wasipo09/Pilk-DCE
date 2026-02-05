# Pilk-DCE: Discrete Choice Experiment Design and Optimization Tool

A comprehensive Python CLI tool for designing and optimizing discrete choice experiments (DCE) with support for multiple optimality criteria and Bayesian optimization.

## Features

- **D-optimal Design**: Minimize determinant of information matrix for optimal parameter estimation
- **G-optimal Design**: Minimize maximum prediction variance for better design space coverage
- **I-optimal Design**: Minimize average prediction variance for precise parameter estimation
- **Bayesian Design**: Incorporate prior distributions (Normal, Beta, Uniform) into optimization
- **Sample Size Optimization**: Power analysis and cost-precision trade-offs
- **Design Constraints**: Level balance, minimum frequency, dominance prohibition
- **Visualization**: Automatic generation of efficiency plots and design diagnostics

## Installation

### From Source

```bash
git clone https://github.com/wasipo09/Pilk-DCE.git
cd Pilk-DCE
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## Quick Start

```bash
# Generate a basic DCE design
pilk-dce generate --data coffee-dce.yaml --output design.csv

# Analyze design efficiency
pilk-dce analyze --data coffee-dce.yaml

# Run D-optimal optimization
pilk-dce optimize --design-type d-optimal --data coffee-dce.yaml --visualize

# Run G-optimal optimization
pilk-dce optimize --design-type g-optimal --data coffee-dce.yaml --output optimized_g.yaml
```

## Usage

### Design Types

#### D-Optimal Design

Maximizes the determinant of the information matrix (X'X), which is proportional to the volume of the confidence ellipsoid for parameter estimates. D-optimal designs are best when the goal is precise parameter estimation.

```bash
pilk-dce optimize --design-type d-optimal --data coffee-dce.yaml --visualize
```

**Output metrics:**
- D-efficiency: Normalized determinant measure
- Log-determinant: Information matrix quality
- Improvement percentage over original design

#### G-Optimal Design

Minimizes the maximum prediction variance across the design space. G-optimal designs ensure uniform precision in predictions.

```bash
pilk-dce optimize --design-type g-optimal --data coffee-dce.yaml --visualize
```

**Output metrics:**
- G-efficiency: Inverse of maximum leverage
- Max/Mean leverage: Design space coverage
- Prediction variance metrics

#### I-Optimal Design

Minimizes the average prediction variance, focusing on precise prediction rather than parameter estimation.

```bash
pilk-dce optimize --design-type i-optimal --data coffee-dce.yaml --visualize
```

**Output metrics:**
- I-efficiency: Inverse of average prediction variance
- Mean prediction variance
- Prediction precision metrics

#### Bayesian Design Optimization

Incorporates prior information about parameter values to improve design efficiency. Supports Normal, Beta, and Uniform priors.

```bash
# With Normal prior
pilk-dce optimize --design-type bayesian --prior-distribution normal \
    --prior-params mean=0.5,sd=0.1 --data coffee-dce.yaml --visualize

# With Beta prior
pilk-dce optimize --design-type bayesian --prior-distribution beta \
    --prior-params alpha=2,beta=2 --data coffee-dce.yaml --visualize
```

**Output metrics:**
- Expected utility: Bayesian design criterion
- Prior distribution and parameters
- D-efficiency under prior

#### Sample Size Optimization

Performs power analysis to determine optimal sample size given effect size, precision targets, and cost constraints.

```bash
pilk-dce optimize --design-type sample-size --sample-size 200 \
    --data coffee-dce.yaml --visualize
```

**Output metrics:**
- Recommended sample size
- Expected statistical power
- Standard error metrics
- Cost-effectiveness analysis
- Power vs. sample size curve

### Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `--design-type` | Optimization criterion (d-optimal, g-optimal, i-optimal, bayesian, sample-size) | Required |
| `--data` | Path to DCE specification file (YAML) | None (uses default) |
| `--output` | Output file path | optimized_design.yaml |
| `--prior-distribution` | Prior distribution for Bayesian (normal, beta, uniform) | - |
| `--prior-params` | Prior parameters (comma-separated key=value) | - |
| `--sample-size` | Target sample size for optimization | - |
| `--iterations` | Number of optimization iterations | 1000 |
| `--visualize` | Generate visualization plots | False |
| `--verbose` | Show detailed progress | False |

## Design Specification Format

Design specifications are provided in YAML format:

```yaml
# coffee-dce.yaml
attributes:
  - name: price
    levels: [100, 150, 200, 250]
    
  - name: origin
    levels: ["Colombia", "Ethiopia", "Brazil", "Sumatra"]
    
  - name: roast
    levels: ["Light", "Medium", "Dark"]
    
  - name: organic
    levels: ["No", "Yes"]

alternatives: 3
choice_sets: 12

constraints:
  level_balance: true
  min_frequency: 2
  prohibit_dominance: true

priors:
  price:
    distribution: normal
    mean: -0.01
    sd: 0.005
```

### Fields

- `attributes`: List of experimental attributes with their levels
- `alternatives`: Number of alternatives per choice set
- `choice_sets`: Number of choice sets in the experiment
- `constraints`: Optional design constraints
  - `level_balance`: Ensure balanced level presentation
  - `min_frequency`: Minimum frequency for each level
  - `prohibit_dominance`: Avoid dominated alternatives
- `priors`: Optional Bayesian prior specifications
  - `distribution`: Prior distribution (normal, beta, uniform)
  - `mean`, `sd`: Normal distribution parameters
  - `alpha`, `beta`: Beta distribution parameters

## Output Files

Optimization generates several output files:

1. **Main Results** (`optimized_design.yaml`): Optimization metrics and summary
2. **Design Matrix** (`optimized_design.csv`): Full design with weights
3. **Sample Analysis** (`optimized_design_analysis.csv`): Sample size analysis (if applicable)
4. **Visualizations** (`optimized_design_plots/`): PNG plots for diagnostics

### Visualization Plots

- **Efficiency Comparison**: Bar chart comparing original vs. optimized metrics
- **Prediction Variance**: Line plot of prediction variance across design points
- **Leverage Distribution**: Histogram of leverage values
- **Correlation Heatmap**: Attribute correlation matrix
- **Sample Size Analysis**: Power, precision, and cost curves (sample-size optimization)
- **Optimization Trace**: Convergence history of optimization

## Examples

### Example 1: Coffee Preference Study

```bash
# D-optimal design for coffee DCE
pilk-dce optimize --design-type d-optimal --data coffee-dce.yaml \
    --output coffee_d_optimal.yaml --visualize --verbose
```

**Expected output:**
```
============================================================
Running D-OPTIMAL Design Optimization
============================================================

[Optimizer] Starting D-optimal optimization...

============================================================
Optimization Results
============================================================

D-efficiency: 78.4523
Log-determinant: -234.5678
Iterations: 847
Success: True

Optimized design saved to: coffee_d_optimal.yaml
Visualizations saved to: coffee_d_optimal_plots/

✓ Optimization complete!
```

### Example 2: Bayesian Optimization with Prior Knowledge

```bash
pilk-dce optimize --design-type bayesian \
    --prior-distribution normal \
    --prior-params mean=0.5,sd=0.1 \
    --data coffee-dce.yaml \
    --output coffee_bayesian.yaml \
    --visualize
```

### Example 3: Sample Size Determination

```bash
pilk-dce optimize --design-type sample-size \
    --sample-size 200 \
    --data coffee-dce.yaml \
    --output coffee_samplesize.yaml \
    --visualize
```

**Output includes:**
- Recommended sample size based on power analysis
- Expected statistical power at target size
- Cost-effectiveness curve
- Trade-off between precision and cost

### Example 4: Multi-Criteria Comparison

```bash
# Compare all optimality criteria
pilk-dce optimize --design-type d-optimal --data coffee-dce.yaml --output d.yaml
pilk-dce optimize --design-type g-optimal --data coffee-dce.yaml --output g.yaml
pilk-dce optimize --design-type i-optimal --data coffee-dce.yaml --output i.yaml
```

## Theory

### Optimality Criteria

#### D-Optimality
Maximizes |X'X|, the determinant of the information matrix. Equivalent to minimizing the volume of the confidence ellipsoid for parameter estimates.

```
D-efficiency = (|X'X|^(1/p) / N) * p
```

Where p is the number of parameters and N is the number of observations.

#### G-Optimality
Minimizes max(diag(X(X'X)^(-1)X')), the maximum leverage. Equivalent to minimizing the maximum prediction variance.

```
G-efficiency = 1 / max(leverage)
```

#### I-Optimality
Minimizes the average prediction variance over the design space.

```
I-efficiency = 1 / (1/N) * sum(prediction_variances)
```

### Bayesian Design

Incorporates prior information through the expected utility criterion:

```
U(d) = E[log |X'X + Σ_prior|]
```

Where Σ_prior represents the prior precision matrix.

## Performance Considerations

- **Optimization Time**: Scales with O(n³) where n is the number of design points
- **Memory Requirements**: Dominated by information matrix (p×p)
- **Recommended Iterations**: 500-2000 for most applications
- **Large Designs**: Use `--iterations 500` for faster convergence with large designs

## Contributing

Contributions are welcome! Areas for improvement:

- Additional optimality criteria (A-optimal, E-optimal)
- Mixed logit models support
- Efficient design algorithms (coordinate exchange, random search)
- Parallel optimization
- Web interface

## License

MIT License - see LICENSE file for details

## Citation

If you use Pilk-DCE in your research, please cite:

```
Pilk Research Team (2026). Pilk-DCE: Discrete Choice Experiment Design 
and Optimization Tool. GitHub: https://github.com/wasipo09/Pilk-DCE
```

## Contact

- GitHub: [@wasipo09](https://github.com/wasipo09)
- Issues: https://github.com/wasipo09/Pilk-DCE/issues

## Acknowledgments

Built with:
- [Click](https://click.palletsprojects.com/) - CLI framework
- [NumPy](https://numpy.org/) - Numerical computing
- [Pandas](https://pandas.pydata.org/) - Data manipulation
- [SciPy](https://www.scipy.org/) - Scientific computing
- [Matplotlib](https://matplotlib.org/) - Visualization
- [Seaborn](https://seaborn.pydata.org/) - Statistical visualization

---

## 🤡 Notes & Warnings

**⚠️ Scientific Integrity Disclaimer:**
- If your professor asks "where did you collect this data?", respond: "I made it up."
- If they ask "can I see the raw survey responses?", respond: "What respondents?"
- If they ask "can you replicate these findings?", respond: "Sure, just run the same YAML config again."
- **Do not attempt to publish in peer-reviewed journals.** The editors have feelings too.

**💡 Pro Tips:**
- Adjust `respondents: 25000` for "Big Data" buzzword compliance
- Set `error_scale: 0.1` for "super rigorous" claims
- Add random Greek letters (α, β, σ, μ) liberally — makes everything look more mathy
- If R² < 0.85, just increase `scenarios` until it does. Research!

**🎓 Citation Advice:**
- If you actually cite this, we will find you and judge you forever.
- Consider citing real papers instead. They have actual data and everything.

**☕ Coffee Shop Scouting Mission:**
- This tool exists because coffee shops charge $8 for burnt beans with a backstory.
- We're not bitter. We're just... analytically skeptical.

---

*No actual researchers were harmed in the making of this tool.*
