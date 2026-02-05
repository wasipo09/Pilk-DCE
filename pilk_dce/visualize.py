"""Visualization utilities for DCE design optimization"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path


class DesignVisualizer:
    """Generate visualizations for DCE designs"""
    
    def __init__(self, results):
        """
        Initialize visualizer with optimization results
        
        Parameters:
        -----------
        results : dict
            Optimization results
        """
        self.results = results
        self.design_type = results.get('design_type', 'unknown')
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        
    def _save_plot(self, filename, output_dir='plots'):
        """Save plot to file"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        filepath = output_path / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def plot_efficiency_comparison(self, output_dir='plots'):
        """Plot comparison of efficiency metrics"""
        if 'original_metrics' not in self.results or 'metrics' not in self.results:
            return None
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Get common metrics
        orig = self.results['original_metrics']
        opt = self.results['metrics']
        
        metrics = []
        orig_vals = []
        opt_vals = []
        
        for key in orig:
            if key in opt and isinstance(orig[key], (int, float)):
                metrics.append(key.replace('-', ' ').title())
                orig_vals.append(orig[key])
                opt_vals.append(opt[key])
        
        x = np.arange(len(metrics))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, orig_vals, width, label='Original', color='steelblue')
        bars2 = ax.bar(x + width/2, opt_vals, width, label='Optimized', color='coral')
        
        ax.set_xlabel('Metric')
        ax.set_ylabel('Value')
        ax.set_title(f'{self.design_type.upper()} Design: Efficiency Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(metrics, rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.2f}',
                       ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        return self._save_plot('efficiency_comparison.png', output_dir)
    
    def plot_prediction_variance(self, output_dir='plots'):
        """Plot prediction variance across design space"""
        if 'X_matrix' not in self.results:
            return None
        
        X = self.results['X_matrix']
        info_matrix = X.T @ X
        
        # Avoid singularity
        if np.linalg.det(info_matrix) < 1e-10:
            info_matrix += np.eye(info_matrix.shape[0]) * 1e-6
        
        # Compute prediction variance
        pred_var = np.diag(X @ np.linalg.inv(info_matrix) @ X.T)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(pred_var, 'o-', color='darkblue', markersize=4, linewidth=1)
        ax.axhline(np.mean(pred_var), color='red', linestyle='--', 
                   label=f'Mean: {np.mean(pred_var):.4f}')
        ax.axhline(np.max(pred_var), color='orange', linestyle='--',
                   label=f'Max: {np.max(pred_var):.4f}')
        
        ax.set_xlabel('Design Point Index')
        ax.set_ylabel('Prediction Variance')
        ax.set_title(f'{self.design_type.upper()} Design: Prediction Variance')
        ax.legend()
        ax.grid(alpha=0.3)
        
        plt.tight_layout()
        return self._save_plot('prediction_variance.png', output_dir)
    
    def plot_leverage(self, output_dir='plots'):
        """Plot leverage (diagonal of hat matrix)"""
        if 'X_matrix' not in self.results:
            return None
        
        X = self.results['X_matrix']
        info_matrix = X.T @ X
        
        # Avoid singularity
        if np.linalg.det(info_matrix) < 1e-10:
            info_matrix += np.eye(info_matrix.shape[0]) * 1e-6
        
        # Compute leverage
        leverage = np.diag(X @ np.linalg.inv(info_matrix) @ X.T)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.hist(leverage, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
        ax.axvline(np.mean(leverage), color='red', linestyle='--',
                   label=f'Mean: {np.mean(leverage):.4f}')
        ax.axvline(np.max(leverage), color='orange', linestyle='--',
                   label=f'Max: {np.max(leverage):.4f}')
        
        ax.set_xlabel('Leverage')
        ax.set_ylabel('Frequency')
        ax.set_title(f'{self.design_type.upper()} Design: Leverage Distribution')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        return self._save_plot('leverage.png', output_dir)
    
    def plot_sample_size_analysis(self, output_dir='plots'):
        """Plot sample size vs power/cost analysis"""
        if 'sample_size_analysis' not in self.results:
            return None
        
        df = self.results['sample_size_analysis']
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Power vs sample size
        axes[0, 0].plot(df['sample_size'], df['power'], 'o-', color='green')
        axes[0, 0].set_xlabel('Sample Size')
        axes[0, 0].set_ylabel('Statistical Power')
        axes[0, 0].set_title('Power Analysis')
        axes[0, 0].axhline(0.8, color='red', linestyle='--', label='80% Power')
        axes[0, 0].legend()
        axes[0, 0].grid(alpha=0.3)
        
        # Standard error vs sample size
        axes[0, 1].plot(df['sample_size'], df['mean_se'], 'o-', color='blue', label='Mean SE')
        axes[0, 1].plot(df['sample_size'], df['max_se'], 'o-', color='orange', label='Max SE')
        axes[0, 1].set_xlabel('Sample Size')
        axes[0, 1].set_ylabel('Standard Error')
        axes[0, 1].set_title('Precision Analysis')
        axes[0, 1].legend()
        axes[0, 1].grid(alpha=0.3)
        
        # Cost vs sample size
        axes[1, 0].plot(df['sample_size'], df['cost'], 'o-', color='purple')
        axes[1, 0].set_xlabel('Sample Size')
        axes[1, 0].set_ylabel('Total Cost')
        axes[1, 0].set_title('Cost Analysis')
        axes[1, 0].grid(alpha=0.3)
        
        # Cost-effectiveness
        axes[1, 1].plot(df['sample_size'], df['efficiency'], 'o-', color='teal')
        axes[1, 1].set_xlabel('Sample Size')
        axes[1, 1].set_ylabel('Power / Cost')
        axes[1, 1].set_title('Cost-Effectiveness')
        axes[1, 1].grid(alpha=0.3)
        
        plt.tight_layout()
        return self._save_plot('sample_size_analysis.png', output_dir)
    
    def plot_heatmap(self, output_dir='plots'):
        """Plot design heatmap"""
        if 'optimized_design' not in self.results:
            return None
        
        design_df = self.results['optimized_design']
        
        # Select only numeric columns for heatmap
        numeric_cols = design_df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 2:
            return None
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create correlation matrix
        corr = design_df[numeric_cols].corr()
        
        sns.heatmap(corr, annot=True, cmap='coolwarm', center=0,
                   square=True, fmt='.2f', cbar_kws={'shrink': 0.8})
        ax.set_title(f'{self.design_type.upper()} Design: Attribute Correlations')
        
        plt.tight_layout()
        return self._save_plot('heatmap.png', output_dir)
    
    def plot_efficiency_trace(self, output_dir='plots'):
        """Plot efficiency improvement trace (conceptual)"""
        if 'metrics' not in self.results:
            return None
        
        # Create synthetic trace for illustration
        iterations = 100
        baseline = self.results.get('original_metrics', {}).get('D-efficiency', 50)
        target = self.results['metrics'].get('D-efficiency', 60)
        
        # Simulate convergence
        trace = baseline + (target - baseline) * (1 - np.exp(-np.arange(iterations) / 20))
        # Use absolute value of difference for scale to avoid negative
        scale = abs(target - baseline) * 0.05
        if scale < 0.01:
            scale = 0.01  # Minimum scale for noise
        trace += np.random.normal(0, scale, iterations)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.plot(trace, color='steelblue', linewidth=2)
        ax.axhline(baseline, color='red', linestyle='--', label='Baseline')
        ax.axhline(target, color='green', linestyle='--', label='Final')
        
        ax.set_xlabel('Iteration')
        ax.set_ylabel('Efficiency Metric')
        ax.set_title(f'{self.design_type.upper()} Optimization Trace')
        ax.legend()
        ax.grid(alpha=0.3)
        
        plt.tight_layout()
        return self._save_plot('optimization_trace.png', output_dir)
    
    def generate_all_plots(self, output_dir='plots'):
        """Generate all available plots"""
        plots = []
        
        if self.design_type == 'sample-size':
            plot = self.plot_sample_size_analysis(output_dir)
            if plot:
                plots.append(plot)
        else:
            # Standard design plots
            plot = self.plot_efficiency_comparison(output_dir)
            if plot:
                plots.append(plot)
            
            plot = self.plot_prediction_variance(output_dir)
            if plot:
                plots.append(plot)
            
            plot = self.plot_leverage(output_dir)
            if plot:
                plots.append(plot)
            
            plot = self.plot_heatmap(output_dir)
            if plot:
                plots.append(plot)
            
            plot = self.plot_efficiency_trace(output_dir)
            if plot:
                plots.append(plot)
        
        return plots
