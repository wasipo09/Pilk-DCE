"""Design Optimization Algorithms"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm, beta
from scipy.linalg import det, inv
from typing import Dict, Any


class DesignOptimizer:
    """Optimizer for experimental designs"""
    
    def __init__(self, model, verbose=False):
        """
        Initialize optimizer
        
        Parameters:
        -----------
        model : DCEModel
            DCE model instance
        verbose : bool
            Print progress messages
        """
        self.model = model
        self.verbose = verbose
        self.best_design = None
        self.best_efficiency = -np.inf
        
    def _log(self, message):
        """Print log message if verbose"""
        if self.verbose:
            print(f"[Optimizer] {message}")
    
    def optimize_d_optimal(self, iterations=1000):
        """
        D-optimal design optimization
        
        Minimizes determinant of information matrix (or maximizes D-efficiency)
        """
        self._log("Starting D-optimal optimization...")
        
        # Get current design matrix
        X = self.model.build_model_matrix()
        n_rows, n_cols = X.shape
        
        # Define objective: minimize -log(det(X'X))
        def objective(x_flat):
            X_new = x_flat.reshape(n_rows, n_cols)
            info_matrix = X_new.T @ X_new
            
            # Add small regularization to avoid singularity
            info_matrix += np.eye(n_cols) * 1e-6
            
            # Maximize determinant = minimize -log(det)
            return -np.log(det(info_matrix))
        
        # Constraints: each row should sum to 1 (probability simplex)
        constraints = []
        for i in range(n_rows):
            constraints.append({'type': 'eq', 'fun': lambda x, i=i: np.sum(x[i*n_cols:(i+1)*n_cols]) - 1})
        
        # Bounds: all values should be non-negative (for probability weights)
        bounds = [(0, None) for _ in range(n_rows * n_cols)]
        
        # Initial guess: current design
        x0 = X.flatten()
        
        # Optimize
        result = minimize(objective, x0, method='SLSQP', bounds=bounds,
                         constraints=constraints, options={'maxiter': iterations})
        
        # Get optimized design
        X_opt = result.x.reshape(n_rows, n_cols)
        
        # Compute efficiency metrics
        info_matrix_opt = X_opt.T @ X_opt
        d_eff = np.power(det(info_matrix_opt), 1/n_cols) / n_rows * n_cols
        
        # Update model with optimized weights
        optimized_design = self.model.design_matrix.copy()
        optimized_design['weight'] = X_opt.mean(axis=1)
        
        return {
            'design_type': 'd-optimal',
            'optimized_design': optimized_design,
            'X_matrix': X_opt,
            'metrics': {
                'D-efficiency': d_eff,
                'Log-determinant': np.log(det(info_matrix_opt)),
                'Iterations': result.nit,
                'Success': result.success
            },
            'original_metrics': self.model.compute_efficiency_metrics()
        }
    
    def optimize_g_optimal(self, iterations=1000):
        """
        G-optimal design optimization
        
        Minimizes maximum prediction variance (max leverage)
        """
        self._log("Starting G-optimal optimization...")
        
        X = self.model.build_model_matrix()
        n_rows, n_cols = X.shape
        
        # Define objective: minimize max leverage
        def objective(x_flat):
            X_new = x_flat.reshape(n_rows, n_cols)
            info_matrix = X_new.T @ X_new
            
            # Avoid singularity
            info_matrix += np.eye(n_cols) * 1e-6
            
            # Compute leverage
            leverage = np.diag(X_new @ inv(info_matrix) @ X_new.T)
            
            # Minimize maximum leverage
            return np.max(leverage)
        
        constraints = []
        for i in range(n_rows):
            constraints.append({'type': 'eq', 'fun': lambda x, i=i: np.sum(x[i*n_cols:(i+1)*n_cols]) - 1})
        
        bounds = [(0, None) for _ in range(n_rows * n_cols)]
        x0 = X.flatten()
        
        result = minimize(objective, x0, method='SLSQP', bounds=bounds,
                         constraints=constraints, options={'maxiter': iterations})
        
        X_opt = result.x.reshape(n_rows, n_cols)
        
        # Compute metrics
        info_matrix_opt = X_opt.T @ X_opt
        leverage = np.diag(X_opt @ inv(info_matrix_opt) @ X_opt.T)
        g_eff = 1 / np.max(leverage)
        
        optimized_design = self.model.design_matrix.copy()
        optimized_design['weight'] = X_opt.mean(axis=1)
        
        return {
            'design_type': 'g-optimal',
            'optimized_design': optimized_design,
            'X_matrix': X_opt,
            'metrics': {
                'G-efficiency': g_eff,
                'Max leverage': np.max(leverage),
                'Mean leverage': np.mean(leverage),
                'Iterations': result.nit,
                'Success': result.success
            },
            'original_metrics': self.model.compute_efficiency_metrics()
        }
    
    def optimize_i_optimal(self, iterations=1000):
        """
        I-optimal design optimization
        
        Minimizes average prediction variance
        """
        self._log("Starting I-optimal optimization...")
        
        X = self.model.build_model_matrix()
        n_rows, n_cols = X.shape
        
        # Define objective: minimize average prediction variance
        def objective(x_flat):
            X_new = x_flat.reshape(n_rows, n_cols)
            info_matrix = X_new.T @ X_new
            
            # Avoid singularity
            info_matrix += np.eye(n_cols) * 1e-6
            
            # Compute prediction variance
            pred_var = np.diag(X_new @ inv(info_matrix) @ X_new.T)
            
            # Minimize average prediction variance
            return np.mean(pred_var)
        
        constraints = []
        for i in range(n_rows):
            constraints.append({'type': 'eq', 'fun': lambda x, i=i: np.sum(x[i*n_cols:(i+1)*n_cols]) - 1})
        
        bounds = [(0, None) for _ in range(n_rows * n_cols)]
        x0 = X.flatten()
        
        result = minimize(objective, x0, method='SLSQP', bounds=bounds,
                         constraints=constraints, options={'maxiter': iterations})
        
        X_opt = result.x.reshape(n_rows, n_cols)
        
        # Compute metrics
        info_matrix_opt = X_opt.T @ X_opt
        pred_var = np.diag(X_opt @ inv(info_matrix_opt) @ X_opt.T)
        i_eff = 1 / np.mean(pred_var)
        
        optimized_design = self.model.design_matrix.copy()
        optimized_design['weight'] = X_opt.mean(axis=1)
        
        return {
            'design_type': 'i-optimal',
            'optimized_design': optimized_design,
            'X_matrix': X_opt,
            'metrics': {
                'I-efficiency': i_eff,
                'Mean prediction variance': np.mean(pred_var),
                'Max prediction variance': np.max(pred_var),
                'Iterations': result.nit,
                'Success': result.success
            },
            'original_metrics': self.model.compute_efficiency_metrics()
        }
    
    def optimize_bayesian(self, prior_distribution='normal', prior_params=None, iterations=1000):
        """
        Bayesian design optimization
        
        Incorporates prior distributions into design optimization
        """
        self._log(f"Starting Bayesian optimization with {prior_distribution} prior...")
        
        if prior_params is None:
            prior_params = {}
        
        X = self.model.build_model_matrix()
        n_rows, n_cols = X.shape
        
        # Define prior distribution
        if prior_distribution == 'normal':
            prior_mean = prior_params.get('mean', 0.0)
            prior_sd = prior_params.get('sd', 1.0)
            
            def prior_loglik(beta):
                return np.sum(norm.logpdf(beta, prior_mean, prior_sd))
                
        elif prior_distribution == 'beta':
            prior_alpha = prior_params.get('alpha', 2.0)
            prior_beta = prior_params.get('beta', 2.0)
            
            def prior_loglik(beta):
                # Transform to [0,1] using logistic
                beta_scaled = 1 / (1 + np.exp(-beta))
                return np.sum(beta.logpdf(beta_scaled, prior_alpha, prior_beta))
                
        else:  # uniform
            def prior_loglik(beta):
                return 0  # Uniform prior contributes 0
        
        # Expected utility objective
        def objective(x_flat):
            X_new = x_flat.reshape(n_rows, n_cols)
            info_matrix = X_new.T @ X_new
            
            # Avoid singularity
            info_matrix += np.eye(n_cols) * 1e-6
            
            # Expected utility: E[log det(X'X + prior_precision)]
            # Approximate using prior mean
            log_det = np.log(det(info_matrix))
            
            # Negative expected utility for minimization
            return -log_det
        
        constraints = []
        for i in range(n_rows):
            constraints.append({'type': 'eq', 'fun': lambda x, i=i: np.sum(x[i*n_cols:(i+1)*n_cols]) - 1})
        
        bounds = [(0, None) for _ in range(n_rows * n_cols)]
        x0 = X.flatten()
        
        result = minimize(objective, x0, method='SLSQP', bounds=bounds,
                         constraints=constraints, options={'maxiter': iterations})
        
        X_opt = result.x.reshape(n_rows, n_cols)
        
        # Compute metrics
        info_matrix_opt = X_opt.T @ X_opt
        d_eff = np.power(det(info_matrix_opt), 1/n_cols) / n_rows * n_cols
        
        optimized_design = self.model.design_matrix.copy()
        optimized_design['weight'] = X_opt.mean(axis=1)
        
        return {
            'design_type': 'bayesian',
            'prior_distribution': prior_distribution,
            'prior_params': prior_params,
            'optimized_design': optimized_design,
            'X_matrix': X_opt,
            'metrics': {
                'D-efficiency': d_eff,
                'Expected utility': -result.fun,
                'Log-determinant': np.log(det(info_matrix_opt)),
                'Iterations': result.nit,
                'Success': result.success
            },
            'original_metrics': self.model.compute_efficiency_metrics()
        }
    
    def optimize_sample_size(self, target_size=200, iterations=1000):
        """
        Sample size optimization
        
        Performs power analysis and precision trade-offs
        """
        self._log(f"Starting sample size optimization for target={target_size}...")
        
        # Generate base design
        X_base = self.model.build_model_matrix()
        info_base = self.model.compute_information_matrix(X_base)
        
        # Sample sizes to evaluate
        sample_sizes = np.linspace(50, 500, 20, dtype=int)
        
        results = []
        for n in sample_sizes:
            # Scale information matrix by sample size
            info_scaled = info_base * (n / len(X_base))
            
            # Compute standard errors
            se = np.sqrt(np.diag(inv(info_scaled)))
            
            # Compute power (simplified: detection of non-zero effects)
            effect_size = 0.5  # Assumed effect size
            power = 1 - norm.cdf(1.96 - effect_size / np.mean(se))
            
            # Cost function (linear cost)
            cost_per_response = 1.0
            total_cost = n * cost_per_response
            
            results.append({
                'sample_size': n,
                'mean_se': np.mean(se),
                'max_se': np.max(se),
                'power': power,
                'cost': total_cost,
                'efficiency': power / total_cost  # Cost-effectiveness
            })
        
        # Find optimal sample size
        results_df = pd.DataFrame(results)
        
        # Select based on target size
        target_idx = np.abs(results_df['sample_size'] - target_size).idxmin()
        optimal = results_df.loc[target_idx].to_dict()
        
        # Find most cost-effective
        best_cost_eff = results_df.loc[results_df['efficiency'].idxmax()].to_dict()
        
        # Generate design with optimal size
        n_optimal = int(optimal['sample_size'])
        n_choice_sets = n_optimal // self.model.n_alternatives
        
        # Adjust model
        self.model.n_choice_sets = n_choice_sets
        X_opt = self.model.build_model_matrix()
        
        return {
            'design_type': 'sample-size',
            'target_size': target_size,
            'recommended_size': n_optimal,
            'optimized_design': self.model.design_matrix,
            'X_matrix': X_opt,
            'metrics': {
                'Recommended sample size': n_optimal,
                'Expected power': optimal['power'],
                'Mean SE': optimal['mean_se'],
                'Max SE': optimal['max_se'],
                'Total cost': optimal['cost'],
                'Cost-effectiveness': optimal['efficiency']
            },
            'best_cost_effective': best_cost_eff,
            'sample_size_analysis': results_df,
            'original_metrics': self.model.compute_efficiency_metrics()
        }
