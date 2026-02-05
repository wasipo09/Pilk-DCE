"""Utility functions for Pilk-DCE"""

import yaml
import json
import pandas as pd
import numpy as np
from pathlib import Path


def load_design(filepath):
    """
    Load DCE design specification from YAML file
    
    Parameters:
    -----------
    filepath : str or Path
        Path to design file
        
    Returns:
    --------
    dict : Design specification
    """
    filepath = Path(filepath)
    
    if filepath.suffix in ['.yaml', '.yml']:
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)
    elif filepath.suffix == '.json':
        with open(filepath, 'r') as f:
            return json.load(f)
    else:
        raise ValueError(f"Unsupported file format: {filepath.suffix}")


def save_design(design, filepath):
    """
    Save design specification to file
    
    Parameters:
    -----------
    design : dict
        Design specification or DataFrame
    filepath : str or Path
        Output file path
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    if isinstance(design, pd.DataFrame):
        if filepath.suffix == '.csv':
            design.to_csv(filepath, index=False)
        elif filepath.suffix in ['.yaml', '.yml']:
            design.to_yaml(filepath, index=False)
        elif filepath.suffix == '.json':
            design.to_json(filepath, orient='records', indent=2)
        else:
            design.to_csv(filepath.with_suffix('.csv'), index=False)
    else:
        if filepath.suffix in ['.yaml', '.yml']:
            with open(filepath, 'w') as f:
                yaml.dump(design, f, default_flow_style=False)
        elif filepath.suffix == '.json':
            with open(filepath, 'w') as f:
                json.dump(design, f, indent=2)
        else:
            with open(filepath.with_suffix('.yaml'), 'w') as f:
                yaml.dump(design, f, default_flow_style=False)


def save_results(results, filepath):
    """
    Save optimization results to file
    
    Parameters:
    -----------
    results : dict
        Optimization results
    filepath : str or Path
        Output file path
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Prepare saveable results (remove non-serializable items)
    saveable = {}
    
    for key, value in results.items():
        if key == 'optimized_design' and isinstance(value, pd.DataFrame):
            # Save DataFrame separately
            df_path = filepath.with_suffix('.csv')
            value.to_csv(df_path, index=False)
            saveable['optimized_design_file'] = str(df_path)
        elif key == 'X_matrix' and isinstance(value, np.ndarray):
            saveable['X_matrix_shape'] = value.shape
            saveable['X_matrix_summary'] = {
                'mean': float(np.mean(value)),
                'std': float(np.std(value)),
                'min': float(np.min(value)),
                'max': float(np.max(value))
            }
        elif key == 'sample_size_analysis' and isinstance(value, pd.DataFrame):
            # Save analysis separately
            analysis_path = filepath.parent / f"{filepath.stem}_analysis.csv"
            value.to_csv(analysis_path, index=False)
            saveable['sample_size_analysis_file'] = str(analysis_path)
        elif isinstance(value, (int, float, str, bool, list, dict)):
            saveable[key] = value
        elif isinstance(value, np.ndarray):
            saveable[key] = value.tolist()
    
    # Save to YAML
    if filepath.suffix in ['.yaml', '.yml']:
        with open(filepath, 'w') as f:
            yaml.dump(saveable, f, default_flow_style=False)
    else:
        with open(filepath.with_suffix('.yaml'), 'w') as f:
            yaml.dump(saveable, f, default_flow_style=False)


def format_number(x, decimals=4):
    """Format number for display"""
    if isinstance(x, (int, float)):
        return round(x, decimals)
    return x


def print_comparison(original, optimized):
    """Print comparison between original and optimized designs"""
    print("\n" + "="*60)
    print("DESIGN COMPARISON")
    print("="*60)
    
    if 'original_metrics' in optimized:
        print("\nOriginal Design:")
        for key, value in optimized['original_metrics'].items():
            print(f"  {key:20s}: {format_number(value)}")
        
        print("\nOptimized Design:")
        for key, value in optimized['metrics'].items():
            print(f"  {key:20s}: {format_number(value)}")
        
        print("\nImprovement:")
        for key in optimized['original_metrics']:
            if key in optimized['metrics']:
                orig = optimized['original_metrics'][key]
                opt = optimized['metrics'][key]
                if orig != 0:
                    improvement = ((opt - orig) / orig) * 100
                    symbol = "↑" if improvement > 0 else "↓"
                    print(f"  {key:20s}: {improvement:+.2f}% {symbol}")


def compute_level_balance(design_df, attribute_name):
    """
    Compute level balance for an attribute
    
    Parameters:
    -----------
    design_df : DataFrame
        Design matrix
    attribute_name : str
        Attribute to check
        
    Returns:
    --------
    dict : Balance statistics
    """
    level_counts = design_df[attribute_name].value_counts().to_dict()
    total = len(design_df)
    
    return {
        'level_counts': level_counts,
        'balance': 1 - np.std(list(level_counts.values())) / np.mean(list(level_counts.values())),
        'min_freq': min(level_counts.values()),
        'max_freq': max(level_counts.values())
    }


def check_dominance(design_df):
    """
    Check for dominated alternatives in design
    
    An alternative is dominated if it is worse on all attributes
    """
    dominated_pairs = []
    
    # Group by choice set
    for choice_set, group in design_df.groupby('choice_set'):
        alternatives = group.drop('choice_set', axis=1)
        
        for i, alt1 in alternatives.iterrows():
            for j, alt2 in alternatives.iterrows():
                if i < j:
                    # Check if alt1 dominates alt2 or vice versa
                    # This is a simplified check - actual depends on utility function
                    pass  # Placeholder for actual dominance check
    
    return dominated_pairs


def estimate_power(effect_size, n, alpha=0.05, two_sided=True):
    """
    Estimate statistical power for detecting an effect
    
    Parameters:
    -----------
    effect_size : float
        Standardized effect size (Cohen's d)
    n : int
        Sample size
    alpha : float
        Significance level
    two_sided : bool
        Two-tailed test
        
    Returns:
    --------
    float : Power (probability of detecting effect)
    """
    from scipy.stats import norm
    
    z_alpha = norm.ppf(1 - alpha/2 if two_sided else alpha)
    z_beta = effect_size * np.sqrt(n) - z_alpha
    power = 1 - norm.cdf(-z_beta)
    
    return power


def wtp_ci(beta, se_beta, price_beta, price_se, alpha=0.05):
    """
    Compute confidence interval for willingness-to-pay (WTP)
    
    WTP = -beta_attribute / beta_price
    
    Uses delta method for CI calculation
    
    Parameters:
    -----------
    beta : float
        Attribute coefficient
    se_beta : float
        Standard error of attribute coefficient
    price_beta : float
        Price coefficient
    price_se : float
        Standard error of price coefficient
    alpha : float
        Significance level
        
    Returns:
    --------
    tuple : (lower, upper) CI bounds
    """
    from scipy.stats import norm
    
    z = norm.ppf(1 - alpha/2)
    
    # Delta method variance
    var_wtp = (se_beta**2 * price_beta**2 + beta**2 * price_se**2) / (price_beta**4)
    
    wtp = -beta / price_beta
    margin = z * np.sqrt(var_wtp)
    
    return (wtp - margin, wtp + margin)
