"""Command-line interface for Pilk-DCE"""

import click
import sys
from pathlib import Path

from pilk_dce.optimize import DesignOptimizer
from pilk_dce.design import DCEModel
from pilk_dce.utils import load_design, save_results


@click.group()
@click.version_option()
def main():
    """Pilk-DCE: Discrete Choice Experiment Design and Optimization Tool"""
    pass


@main.command()
@click.option(
    '--design-type',
    type=click.Choice(['d-optimal', 'g-optimal', 'i-optimal', 'bayesian', 'sample-size']),
    required=True,
    help='Type of design optimization'
)
@click.option(
    '--data',
    type=click.Path(exists=True),
    help='Path to DCE design file (YAML format)'
)
@click.option(
    '--output',
    type=click.Path(),
    default='optimized_design.yaml',
    help='Output file for optimized design'
)
@click.option(
    '--prior-distribution',
    type=click.Choice(['normal', 'beta', 'uniform']),
    help='Prior distribution for Bayesian optimization'
)
@click.option(
    '--prior-params',
    help='Comma-separated prior parameters (e.g., mean=0.5,sd=0.1 or alpha=2,beta=2)'
)
@click.option(
    '--sample-size',
    type=int,
    help='Sample size for optimization'
)
@click.option(
    '--iterations',
    type=int,
    default=1000,
    help='Number of optimization iterations'
)
@click.option(
    '--visualize',
    is_flag=True,
    help='Generate visualization plots'
)
@click.option(
    '--verbose',
    is_flag=True,
    help='Show detailed output'
)
def optimize(design_type, data, output, prior_distribution, prior_params,
             sample_size, iterations, visualize, verbose):
    """Optimize experimental design for discrete choice experiments"""
    try:
        # Load design specification
        if data:
            design_spec = load_design(data)
        else:
            # Create default coffee DCE design
            design_spec = {
                'attributes': [
                    {'name': 'price', 'levels': [100, 150, 200, 250]},
                    {'name': 'origin', 'levels': ['Colombia', 'Ethiopia', 'Brazil', 'Sumatra']},
                    {'name': 'roast', 'levels': ['Light', 'Medium', 'Dark']},
                    {'name': 'organic', 'levels': ['No', 'Yes']}
                ],
                'alternatives': 3,
                'choice_sets': 12
            }
            click.echo("No design file specified, using default coffee DCE design")
        
        # Parse prior parameters if provided
        prior_dict = None
        if prior_params:
            prior_dict = {}
            for param in prior_params.split(','):
                key, value = param.split('=')
                try:
                    prior_dict[key] = float(value)
                except ValueError:
                    prior_dict[key] = value
        
        # Initialize model
        model = DCEModel(design_spec)
        
        # Initialize optimizer
        optimizer = DesignOptimizer(model, verbose=verbose)
        
        click.echo(f"\n{'='*60}")
        click.echo(f"Running {design_type.upper()} Design Optimization")
        click.echo(f"{'='*60}\n")
        
        # Run appropriate optimization
        if design_type == 'd-optimal':
            results = optimizer.optimize_d_optimal(iterations=iterations)
        elif design_type == 'g-optimal':
            results = optimizer.optimize_g_optimal(iterations=iterations)
        elif design_type == 'i-optimal':
            results = optimizer.optimize_i_optimal(iterations=iterations)
        elif design_type == 'bayesian':
            if not prior_distribution:
                click.echo("Error: --prior-distribution required for Bayesian optimization")
                sys.exit(1)
            results = optimizer.optimize_bayesian(
                prior_distribution=prior_distribution,
                prior_params=prior_dict,
                iterations=iterations
            )
        elif design_type == 'sample-size':
            if not sample_size:
                click.echo("Error: --sample-size required for sample size optimization")
                sys.exit(1)
            results = optimizer.optimize_sample_size(target_size=sample_size, iterations=iterations)
        
        # Display results
        click.echo(f"\n{'='*60}")
        click.echo("Optimization Results")
        click.echo(f"{'='*60}\n")
        
        for key, value in results.get('metrics', {}).items():
            click.echo(f"{key}: {value:.4f}")
        
        # Save results
        output_path = Path(output)
        save_results(results, output_path)
        click.echo(f"\nOptimized design saved to: {output_path}")
        
        # Generate visualizations if requested
        if visualize:
            from pilk_dce.visualize import DesignVisualizer
            viz = DesignVisualizer(results)
            viz_output = output_path.stem + '_plots'
            viz.generate_all_plots(output_dir=viz_output)
            click.echo(f"Visualizations saved to: {viz_output}/")
        
        click.echo("\n✓ Optimization complete!")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@main.command()
@click.option(
    '--data',
    type=click.Path(exists=True),
    required=True,
    help='Path to DCE design file'
)
@click.option(
    '--output',
    type=click.Path(),
    default='dce_design.csv',
    help='Output file for generated design'
)
def generate(data, output):
    """Generate a DCE design from specification"""
    try:
        design_spec = load_design(data)
        model = DCEModel(design_spec)
        design_matrix = model.generate_design()
        
        output_path = Path(output)
        design_matrix.to_csv(output_path, index=False)
        click.echo(f"Design generated with {len(design_matrix)} choice sets")
        click.echo(f"Saved to: {output_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option(
    '--data',
    type=click.Path(exists=True),
    required=True,
    help='Path to DCE design file'
)
def analyze(data):
    """Analyze design efficiency metrics"""
    try:
        design_spec = load_design(data)
        model = DCEModel(design_spec)
        
        click.echo("\nDesign Efficiency Analysis")
        click.echo("="*50 + "\n")
        
        metrics = model.compute_efficiency_metrics()
        
        for metric, value in metrics.items():
            click.echo(f"{metric:20s}: {value:.4f}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
