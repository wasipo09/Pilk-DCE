"""
Utility functions for Pilk-DCE WebUI

Helper functions for data processing, file operations, and UI enhancements.
"""

import yaml
import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path
from io import BytesIO
import zipfile
import json

from pilk_dce.design import DCEModel
from pilk_dce.optimize import DesignOptimizer
from pilk_dce.visualize import DesignVisualizer


def load_yaml_config(file_content):
    """
    Load YAML configuration from uploaded file
    
    Parameters:
    -----------
    file_content : bytes or str
        Raw file content
    
    Returns:
    --------
    dict : Parsed YAML configuration
    """
    if isinstance(file_content, str):
        file_content = file_content.encode('utf-8')
    try:
        config = yaml.safe_load(file_content)
        return config
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML format: {str(e)}")


def validate_config(config):
    """
    Validate DCE configuration structure
    
    Parameters:
    -----------
    config : dict
        Configuration dictionary
    
    Returns:
    --------
    tuple : (is_valid, error_messages)
    """
    errors = []
    
    # Check required keys
    required_keys = ['attributes']
    for key in required_keys:
        if key not in config:
            errors.append(f"Missing required key: {key}")
    
    # Validate attributes
    if 'attributes' in config:
        if not isinstance(config['attributes'], list):
            errors.append("Attributes must be a list")
        else:
            for i, attr in enumerate(config['attributes']):
                if 'name' not in attr:
                    errors.append(f"Attribute {i}: Missing 'name'")
                if 'levels' not in attr:
                    errors.append(f"Attribute {i}: Missing 'levels'")
                elif not isinstance(attr['levels'], list) or len(attr['levels']) < 2:
                    errors.append(f"Attribute {i}: Levels must be a list with at least 2 values")
    
    # Validate numerical parameters
    if 'alternatives' in config:
        if not isinstance(config['alternatives'], int) or config['alternatives'] < 2:
            errors.append("Alternatives must be an integer >= 2")
    
    if 'choice_sets' in config:
        if not isinstance(config['choice_sets'], int) or config['choice_sets'] < 1:
            errors.append("Choice sets must be an integer >= 1")
    
    return (len(errors) == 0, errors)


def create_dce_model(config):
    """
    Create DCEModel instance from configuration
    
    Parameters:
    -----------
    config : dict
        Configuration dictionary
    
    Returns:
    --------
    DCEModel : Model instance
    """
    return DCEModel(config)


def generate_design(model, optimization_type='d-optimal', **kwargs):
    """
    Generate and optimize DCE design
    
    Parameters:
    -----------
    model : DCEModel
        DCE model instance
    optimization_type : str
        Type of optimization ('d-optimal', 'g-optimal', 'i-optimal', 'bayesian', 'sample-size')
    **kwargs : dict
        Additional optimization parameters
    
    Returns:
    --------
    dict : Optimization results
    """
    optimizer = DesignOptimizer(model, verbose=True)
    
    if optimization_type == 'd-optimal':
        results = optimizer.optimize_d_optimal(**kwargs)
    elif optimization_type == 'g-optimal':
        results = optimizer.optimize_g_optimal(**kwargs)
    elif optimization_type == 'i-optimal':
        results = optimizer.optimize_i_optimal(**kwargs)
    elif optimization_type == 'bayesian':
        results = optimizer.optimize_bayesian(**kwargs)
    elif optimization_type == 'sample-size':
        results = optimizer.optimize_sample_size(**kwargs)
    else:
        raise ValueError(f"Unknown optimization type: {optimization_type}")
    
    return results


def calculate_part_worth_utilities(results):
    """
    Calculate part-worth utilities from optimization results
    
    Parameters:
    -----------
    results : dict
        Optimization results
    
    Returns:
    --------
    pandas.DataFrame : Part-worth utilities
    """
    if 'optimized_design' not in results:
        return None
    
    design = results['optimized_design']
    utilities = {}
    
    # Calculate utilities for each attribute level
    numeric_cols = design.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if col not in ['choice_set', 'alternative', 'weight']:
            utilities[col] = design[col].mean()
    
    return pd.DataFrame.from_dict(utilities, orient='index', columns=['Utility'])


def calculate_wtp(utilities, price_attr='price'):
    """
    Calculate willingness-to-pay (WTP) from utilities
    
    Parameters:
    -----------
    utilities : pandas.DataFrame
        Part-worth utilities
    price_attr : str
        Name of price attribute
    
    Returns:
    --------
    pandas.DataFrame : WTP values
    """
    if price_attr not in utilities.index:
        return None
    
    price_utility = utilities.loc[price_attr, 'Utility']
    wtp = utilities.copy()
    
    if price_utility != 0:
        wtp['WTP'] = wtp['Utility'] / abs(price_utility)
    
    return wtp


def simulate_market_share(utilities, price_scenarios):
    """
    Simulate market share for different price scenarios
    
    Parameters:
    -----------
    utilities : pandas.DataFrame
        Part-worth utilities
    price_scenarios : list
        List of price values to simulate
    
    Returns:
    --------
    pandas.DataFrame : Market share results
    """
    results = []
    
    for price in price_scenarios:
        # Simplified market share simulation
        # In practice, this would use the full multinomial logit model
        base_utility = utilities['Utility'].sum()
        price_impact = price * 0.01  # Simplified price sensitivity
        total_utility = base_utility - price_impact
        
        # Convert to probabilities using softmax
        share = np.exp(total_utility) / (1 + np.exp(total_utility))
        
        results.append({
            'Price': price,
            'Utility': total_utility,
            'Market Share': share
        })
    
    return pd.DataFrame(results)


def create_download_csv(df, filename='data.csv'):
    """
    Create downloadable CSV file
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Data to export
    filename : str
        Default filename
    
    Returns:
    --------
    tuple : (filename, data)
    """
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return filename, output.getvalue()


def create_download_json(data, filename='data.json'):
    """
    Create downloadable JSON file
    
    Parameters:
    -----------
    data : dict
        Data to export
    filename : str
        Default filename
    
    Returns:
    --------
    tuple : (filename, data)
    """
    output = BytesIO()
    output.write(json.dumps(data, indent=2, default=str).encode('utf-8'))
    output.seek(0)
    return filename, output.getvalue()


def create_download_zip(files):
    """
    Create downloadable ZIP file
    
    Parameters:
    -----------
    files : list of tuples
        List of (filename, data) tuples
    
    Returns:
    --------
    tuple : (filename, data)
    """
    output = BytesIO()
    
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for filename, data in files:
            zipf.writestr(filename, data)
    
    output.seek(0)
    return 'export.zip', output.getvalue()


def calculate_confidence_interval(values, confidence=0.95):
    """
    Calculate confidence interval for values
    
    Parameters:
    -----------
    values : array-like
        Values to calculate CI for
    confidence : float
        Confidence level (0-1)
    
    Returns:
    --------
    tuple : (lower, upper)
    """
    values = np.array(values)
    mean = np.mean(values)
    std_err = np.std(values) / np.sqrt(len(values))
    
    z_score = {
        0.90: 1.645,
        0.95: 1.96,
        0.99: 2.576
    }.get(confidence, 1.96)
    
    margin = z_score * std_err
    return (mean - margin, mean + margin)


def format_number(value, decimals=2):
    """
    Format number for display
    
    Parameters:
    -----------
    value : float
        Value to format
    decimals : int
        Number of decimal places
    
    Returns:
    --------
    str : Formatted number
    """
    if pd.isna(value):
        return "N/A"
    return f"{value:.{decimals}f}"


def create_efficiency_trace(baseline, target, iterations=100, noise_scale=0.05):
    """
    Create synthetic efficiency optimization trace
    
    Parameters:
    -----------
    baseline : float
        Starting efficiency value
    target : float
        Target efficiency value
    iterations : int
        Number of iterations
    noise_scale : float
        Scale of random noise
    
    Returns:
    --------
    numpy.ndarray : Trace values
    """
    # Simulate convergence
    trace = baseline + (target - baseline) * (1 - np.exp(-np.arange(iterations) / 20))
    
    # Add noise
    scale = abs(target - baseline) * noise_scale
    if scale < 0.01:
        scale = 0.01
    trace += np.random.normal(0, scale, iterations)
    
    return trace


def get_example_config():
    """
    Get example DCE configuration
    
    Returns:
    --------
    str : YAML configuration string
    """
    return """
# Example DCE Configuration

attributes:
  - name: price
    levels: [100, 150, 200, 250]
    description: "Price in cents"
    
  - name: origin
    levels: ["Colombia", "Ethiopia", "Brazil", "Sumatra"]
    description: "Coffee origin"
    
  - name: roast
    levels: ["Light", "Medium", "Dark"]
    description: "Roast level"
    
  - name: organic
    levels: ["No", "Yes"]
    description: "Organic certification"

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
    
metadata:
  study_name: "Example Study"
  researcher: "Pilk Research Team"
"""


def create_sample_dataset(n_rows=100):
    """
    Create sample dataset for testing
    
    Parameters:
    -----------
    n_rows : int
        Number of rows to generate
    
    Returns:
    --------
    pandas.DataFrame : Sample dataset
    """
    np.random.seed(42)
    
    data = {
        'respondent_id': np.repeat(range(n_rows // 10), 10),
        'choice_set': np.tile(range(10), n_rows // 10),
        'alternative': np.random.randint(0, 3, n_rows),
        'choice': np.random.randint(0, 2, n_rows),
        'price': np.random.choice([100, 150, 200, 250], n_rows),
        'origin': np.random.choice(['Colombia', 'Ethiopia', 'Brazil', 'Sumatra'], n_rows),
        'roast': np.random.choice(['Light', 'Medium', 'Dark'], n_rows),
        'organic': np.random.choice(['No', 'Yes'], n_rows)
    }
    
    return pd.DataFrame(data)


def check_session_data():
    """
    Check if session has required data
    
    Returns:
    --------
    dict : Status of session data
    """
    status = {
        'design_loaded': st.session_state.get('design_data') is not None,
        'optimized': st.session_state.get('optimization_results') is not None,
        'has_design_matrix': False,
        'has_utilities': False
    }
    
    if status['optimized']:
        results = st.session_state.optimization_results
        status['has_design_matrix'] = 'optimized_design' in results
        status['has_utilities'] = 'X_matrix' in results
    
    return status


def get_optimization_summary(results):
    """
    Get summary of optimization results
    
    Parameters:
    -----------
    results : dict
        Optimization results
    
    Returns:
    --------
    dict : Summary metrics
    """
    summary = {
        'design_type': results.get('design_type', 'Unknown'),
        'iterations': 0,
        'success': False,
        'metrics': {}
    }
    
    if 'metrics' in results:
        summary['success'] = results['metrics'].get('Success', False)
        summary['iterations'] = results['metrics'].get('Iterations', 0)
        
        # Extract key metrics
        key_metrics = ['D-efficiency', 'G-efficiency', 'I-efficiency', 
                      'Mean prediction variance', 'Max leverage']
        for metric in key_metrics:
            if metric in results['metrics']:
                summary['metrics'][metric] = results['metrics'][metric]
    
    return summary
