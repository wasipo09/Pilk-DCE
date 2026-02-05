"""DCE Design Model and Matrix Generation"""

import numpy as np
import pandas as pd
from itertools import product
from scipy.linalg import det, inv


class DCEModel:
    """Discrete Choice Experiment Model"""
    
    def __init__(self, design_spec):
        """
        Initialize DCE model with design specification
        
        Parameters:
        -----------
        design_spec : dict
            Design specification containing:
            - attributes: list of attribute dicts with 'name' and 'levels'
            - alternatives: number of alternatives per choice set
            - choice_sets: number of choice sets to generate
        """
        self.design_spec = design_spec
        self.attributes = design_spec['attributes']
        self.n_alternatives = design_spec.get('alternatives', 2)
        self.n_choice_sets = design_spec.get('choice_sets', 12)
        
        # Build attribute mapping
        self.attribute_names = [attr['name'] for attr in self.attributes]
        self.attribute_levels = {attr['name']: attr['levels'] for attr in self.attributes}
        self.n_attributes = len(self.attributes)
        
        # Calculate total number of parameters (including alternative-specific constants)
        self.n_parameters = self.n_alternatives - 1 + self.n_attributes
        
        # Design matrix placeholder
        self.design_matrix = None
        self.info_matrix = None
        
    def generate_design(self):
        """Generate full factorial design matrix"""
        all_combinations = list(product(*[self.attribute_levels[name] 
                                           for name in self.attribute_names]))
        
        df = pd.DataFrame(all_combinations, columns=self.attribute_names)
        
        # Randomly sample choice sets
        if len(df) > self.n_choice_sets * self.n_alternatives:
            df = df.sample(n=self.n_choice_sets * self.n_alternatives, random_state=42)
        
        # Assign to choice sets and alternatives
        df['choice_set'] = np.repeat(range(self.n_choice_sets), self.n_alternatives)
        df['alternative'] = np.tile(range(self.n_alternatives), self.n_choice_sets)
        
        self.design_matrix = df
        return df
    
    def encode_effects(self, row):
        """Effects coding for categorical attributes"""
        encoded = []
        
        # Alternative-specific constants (ASC)
        for i in range(self.n_alternatives - 1):
            encoded.append(1 if row['alternative'] == i else 0)
        
        # Attribute effects coding
        for attr_name in self.attribute_names:
            levels = self.attribute_levels[attr_name]
            n_levels = len(levels)
            
            if isinstance(levels[0], (int, float)):
                # Numeric attribute: center the value
                value = row[attr_name]
                centered = value - np.mean(levels)
                encoded.append(centered)
            else:
                # Categorical attribute: effects coding
                for i in range(n_levels - 1):
                    encoded.append(1 if row[attr_name] == levels[i] else 0)
        
        return np.array(encoded)
    
    def build_model_matrix(self):
        """Build the model matrix (X) for analysis"""
        if self.design_matrix is None:
            self.generate_design()
        
        X = np.array([self.encode_effects(row) 
                      for _, row in self.design_matrix.iterrows()])
        
        return X
    
    def compute_information_matrix(self, X=None):
        """Compute Fisher information matrix"""
        if X is None:
            X = self.build_model_matrix()
        
        # MNL information matrix approximation: X'X
        info_matrix = X.T @ X
        self.info_matrix = info_matrix
        
        return info_matrix
    
    def compute_efficiency_metrics(self):
        """Compute various design efficiency metrics"""
        X = self.build_model_matrix()
        info_matrix = self.compute_information_matrix(X)
        
        # Avoid singular matrix
        if det(info_matrix) < 1e-10:
            info_matrix += np.eye(info_matrix.shape[0]) * 1e-6
        
        # D-efficiency: |X'X|^(1/p) / N
        n_observations = len(X)
        n_params = X.shape[1]
        
        d_eff = (np.power(det(info_matrix), 1/n_params) / n_observations) * n_params
        
        # A-efficiency: trace(inv(X'X)) / p
        a_eff = n_params / np.trace(inv(info_matrix))
        
        # G-efficiency: max leverage
        leverage = np.diag(X @ inv(info_matrix) @ X.T)
        g_eff = 1 / np.max(leverage)
        
        # I-efficiency (average variance)
        prediction_var = np.mean(np.diag(X @ inv(info_matrix) @ X.T))
        i_eff = 1 / prediction_var
        
        return {
            'D-efficiency': d_eff,
            'A-efficiency': a_eff,
            'G-efficiency': g_eff,
            'I-efficiency': i_eff,
            'Determinant': det(info_matrix),
            'Trace': np.trace(info_matrix),
            'Condition number': np.linalg.cond(info_matrix)
        }
    
    def compute_prediction_variance(self, X=None):
        """Compute prediction variance across design space"""
        if X is None:
            X = self.build_model_matrix()
        
        info_matrix = self.compute_information_matrix(X)
        
        # Avoid singular matrix
        if det(info_matrix) < 1e-10:
            info_matrix += np.eye(info_matrix.shape[0]) * 1e-6
        
        # Prediction variance: diag(X * inv(X'X) * X')
        pred_var = np.diag(X @ inv(info_matrix) @ X.T)
        
        return pred_var
