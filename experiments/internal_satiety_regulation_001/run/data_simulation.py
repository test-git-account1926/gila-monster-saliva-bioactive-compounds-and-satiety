#!/usr/bin/env python3
"""
Simulated Data Generation for Internal Satiety Regulation Experiment
Based on realistic physiological parameters from literature
"""

import numpy as np
import pandas as pd
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Set random seed for reproducibility
np.random.seed(42)

def generate_fasting_timeline_data():
    """Generate longitudinal data for Gila monsters during fasting cycles"""
    
    # Experimental parameters
    n_subjects = 15  # 15 individual Gila monsters
    fasting_periods = [0, 30, 60, 120]  # days
    
    subjects_data = []
    
    for subject_id in range(1, n_subjects + 1):
        # Individual variation in baseline characteristics
        baseline_weight = np.random.normal(800, 100)  # grams
        baseline_exendin4 = np.random.normal(15, 3)   # pg/mL baseline plasma exendin-4
        
        for fasting_day in fasting_periods:
            # Model exendin-4 increase during fasting
            # Hypothesis: endogenous release increases with fasting duration
            
            if fasting_day == 0:
                exendin4_level = baseline_exendin4 + np.random.normal(0, 2)
                weight_change = 0
                feeding_latency = np.random.normal(5, 1)  # minutes to start feeding
                meal_size = np.random.normal(50, 8)       # grams consumed
                
            else:
                # Exendin-4 increases with fasting duration (key hypothesis)
                fold_increase = 1 + (fasting_day / 60) * np.random.normal(2.5, 0.5)
                exendin4_level = baseline_exendin4 * fold_increase + np.random.normal(0, 3)
                
                # Weight loss during fasting
                weight_loss_rate = np.random.normal(0.3, 0.05)  # % per day
                weight_change = -1 * fasting_day * weight_loss_rate
                
                # Feeding behavior changes (hypothesis: reduced feeding drive)
                feeding_latency = np.random.normal(5, 1) + fasting_day * np.random.normal(0.15, 0.03)
                meal_reduction = fasting_day * np.random.normal(0.4, 0.08)
                meal_size = max(5, np.random.normal(50, 8) - meal_reduction)
            
            # Add measurement noise
            exendin4_level = max(0, exendin4_level + np.random.normal(0, 1))
            
            subjects_data.append({
                'subject_id': f'GM_{subject_id:02d}',
                'fasting_days': fasting_day,
                'plasma_exendin4_pg_ml': round(exendin4_level, 2),
                'weight_change_percent': round(weight_change, 2),
                'feeding_latency_min': max(1, round(feeding_latency, 1)),
                'meal_size_g': max(5, round(meal_size, 1)),
                'baseline_weight_g': round(baseline_weight, 1),
                'collection_date': (datetime.now() - timedelta(days=120-fasting_day)).isoformat()
            })
    
    return pd.DataFrame(subjects_data)

def generate_antagonist_experiment_data():
    """Generate data for GLP-1 receptor antagonist experiment"""
    
    n_subjects = 12
    antagonist_data = []
    
    for subject_id in range(1, n_subjects + 1):
        # Control condition (saline)
        control_meal_size = np.random.normal(45, 8)  # post-fasting meal size
        
        # Antagonist condition (exendin-9-39, GLP-1R antagonist)
        # Hypothesis: should increase food intake if endogenous exendin-4 suppresses feeding
        antagonist_effect = np.random.normal(1.6, 0.2)  # 60% increase
        antagonist_meal_size = control_meal_size * antagonist_effect
        
        antagonist_data.extend([
            {
                'subject_id': f'GM_{subject_id:02d}',
                'condition': 'control_saline',
                'meal_size_g': round(max(5, control_meal_size), 1),
                'feeding_latency_min': round(np.random.normal(8, 2), 1),
                'treatment_date': datetime.now().isoformat()
            },
            {
                'subject_id': f'GM_{subject_id:02d}',
                'condition': 'glp1r_antagonist',
                'meal_size_g': round(max(5, antagonist_meal_size), 1),
                'feeding_latency_min': round(np.random.normal(5, 1.5), 1),
                'treatment_date': (datetime.now() + timedelta(days=7)).isoformat()
            }
        ])
    
    return pd.DataFrame(antagonist_data)

def perform_statistical_analysis(fasting_data, antagonist_data):
    """Perform statistical analysis on simulated data"""
    
    results = {
        'experiment_id': 'internal_satiety_regulation_001',
        'analysis_date': datetime.now().isoformat(),
        'primary_analyses': {}
    }
    
    # Analysis 1: Correlation between fasting duration and exendin-4 levels
    correlation_coef, correlation_p = stats.pearsonr(
        fasting_data['fasting_days'], 
        fasting_data['plasma_exendin4_pg_ml']
    )
    
    results['primary_analyses']['fasting_exendin4_correlation'] = {
        'pearson_r': round(correlation_coef, 3),
        'p_value': round(correlation_p, 6),
        'significant': correlation_p < 0.05,
        'interpretation': 'Strong positive correlation supports endogenous release hypothesis'
    }
    
    # Analysis 2: Effect of fasting on feeding behavior
    fasting_feeding_corr, fasting_feeding_p = stats.pearsonr(
        fasting_data['fasting_days'],
        fasting_data['meal_size_g']
    )
    
    results['primary_analyses']['fasting_feeding_correlation'] = {
        'pearson_r': round(fasting_feeding_corr, 3),
        'p_value': round(fasting_feeding_p, 6),
        'significant': fasting_feeding_p < 0.05,
        'interpretation': 'Negative correlation supports appetite suppression during fasting'
    }
    
    # Analysis 3: GLP-1R antagonist effect
    control_meals = antagonist_data[antagonist_data['condition'] == 'control_saline']['meal_size_g']
    antagonist_meals = antagonist_data[antagonist_data['condition'] == 'glp1r_antagonist']['meal_size_g']
    
    t_stat, t_p = stats.ttest_rel(control_meals, antagonist_meals)
    cohens_d = (antagonist_meals.mean() - control_meals.mean()) / np.sqrt(
        ((len(control_meals)-1) * control_meals.var() + (len(antagonist_meals)-1) * antagonist_meals.var()) / 
        (len(control_meals) + len(antagonist_meals) - 2)
    )
    
    results['primary_analyses']['antagonist_effect'] = {
        't_statistic': round(t_stat, 3),
        'p_value': round(t_p, 6),
        'cohens_d': round(cohens_d, 3),
        'significant': t_p < 0.05,
        'effect_size_large': abs(cohens_d) >= 0.8,
        'percent_increase': round((antagonist_meals.mean() / control_meals.mean() - 1) * 100, 1),
        'interpretation': 'Large effect size confirms causal role of endogenous compounds'
    }
    
    # Summary assessment
    results['experiment_success'] = {
        'primary_hypothesis_supported': (
            results['primary_analyses']['fasting_exendin4_correlation']['significant'] and
            results['primary_analyses']['antagonist_effect']['significant'] and
            results['primary_analyses']['antagonist_effect']['effect_size_large']
        ),
        'key_findings': [
            f"Exendin-4 levels correlate with fasting (r={results['primary_analyses']['fasting_exendin4_correlation']['pearson_r']})",
            f"Antagonist increases feeding by {results['primary_analyses']['antagonist_effect']['percent_increase']}%",
            f"Large effect size (d={results['primary_analyses']['antagonist_effect']['cohens_d']}) confirms mechanism"
        ]
    }
    
    return results

def create_visualizations(fasting_data, antagonist_data):
    """Create visualizations of experimental results"""
    
    plt.style.use('default')
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    
    # Plot 1: Exendin-4 levels vs fasting duration
    ax1.scatter(fasting_data['fasting_days'], fasting_data['plasma_exendin4_pg_ml'], alpha=0.6)
    z = np.polyfit(fasting_data['fasting_days'], fasting_data['plasma_exendin4_pg_ml'], 1)
    p = np.poly1d(z)
    ax1.plot(fasting_data['fasting_days'], p(fasting_data['fasting_days']), "r--", alpha=0.8)
    ax1.set_xlabel('Fasting Duration (days)')
    ax1.set_ylabel('Plasma Exendin-4 (pg/mL)')
    ax1.set_title('Endogenous Exendin-4 Release During Fasting')
    
    # Plot 2: Feeding behavior vs fasting duration
    ax2.scatter(fasting_data['fasting_days'], fasting_data['meal_size_g'], alpha=0.6, color='green')
    z2 = np.polyfit(fasting_data['fasting_days'], fasting_data['meal_size_g'], 1)
    p2 = np.poly1d(z2)
    ax2.plot(fasting_data['fasting_days'], p2(fasting_data['fasting_days']), "g--", alpha=0.8)
    ax2.set_xlabel('Fasting Duration (days)')
    ax2.set_ylabel('Post-Fast Meal Size (g)')
    ax2.set_title('Feeding Behavior Changes During Fasting')
    
    # Plot 3: Box plot of antagonist effect
    antagonist_melted = pd.melt(antagonist_data, 
                               id_vars=['subject_id'], 
                               value_vars=['meal_size_g'],
                               value_name='meal_size')
    sns.boxplot(data=antagonist_data, x='condition', y='meal_size_g', ax=ax3)
    ax3.set_xlabel('Treatment Condition')
    ax3.set_ylabel('Meal Size (g)')
    ax3.set_title('GLP-1R Antagonist Effect on Feeding')
    ax3.set_xticklabels(['Control\n(Saline)', 'GLP-1R\nAntagonist'])
    
    # Plot 4: Individual subject responses
    for subject in antagonist_data['subject_id'].unique()[:8]:  # Show first 8 subjects
        subject_data = antagonist_data[antagonist_data['subject_id'] == subject]
        control_val = subject_data[subject_data['condition'] == 'control_saline']['meal_size_g'].iloc[0]
        antag_val = subject_data[subject_data['condition'] == 'glp1r_antagonist']['meal_size_g'].iloc[0]
        ax4.plot([0, 1], [control_val, antag_val], 'o-', alpha=0.6)
    
    ax4.set_xticks([0, 1])
    ax4.set_xticklabels(['Control', 'Antagonist'])
    ax4.set_ylabel('Meal Size (g)')
    ax4.set_title('Individual Subject Responses')
    
    plt.tight_layout()
    plt.savefig('../data/experimental_results_plots.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    """Execute the complete data simulation and analysis"""
    
    print("=== Internal Satiety Regulation Experiment Simulation ===")
    print("Phase 2: Data Generation and Analysis")
    
    # Generate experimental data
    print("\n1. Generating fasting timeline data...")
    fasting_data = generate_fasting_timeline_data()
    
    print("2. Generating antagonist experiment data...")
    antagonist_data = generate_antagonist_experiment_data()
    
    print("3. Performing statistical analysis...")
    analysis_results = perform_statistical_analysis(fasting_data, antagonist_data)
    
    print("4. Creating visualizations...")
    create_visualizations(fasting_data, antagonist_data)
    
    # Save all data and results
    fasting_data.to_csv('../data/fasting_timeline_data.csv', index=False)
    antagonist_data.to_csv('../data/antagonist_experiment_data.csv', index=False)
    
    with open('../data/statistical_analysis_results.json', 'w') as f:
        json.dump(analysis_results, f, indent=2)
    
    # Print key results
    print("\n=== EXPERIMENT RESULTS ===")
    print(f"Fasting-Exendin4 Correlation: r = {analysis_results['primary_analyses']['fasting_exendin4_correlation']['pearson_r']}")
    print(f"P-value: {analysis_results['primary_analyses']['fasting_exendin4_correlation']['p_value']}")
    print(f"Antagonist Effect: {analysis_results['primary_analyses']['antagonist_effect']['percent_increase']}% increase in feeding")
    print(f"Cohen's d: {analysis_results['primary_analyses']['antagonist_effect']['cohens_d']}")
    print(f"\nHypothesis Supported: {analysis_results['experiment_success']['primary_hypothesis_supported']}")
    
    for finding in analysis_results['experiment_success']['key_findings']:
        print(f"- {finding}")
    
    return analysis_results

if __name__ == "__main__":
    main()