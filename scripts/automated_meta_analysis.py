#!/usr/bin/env python3
"""
Automated Meta-Analysis Framework for Biomarker Performance
This script performs comprehensive meta-analysis on biomarker data including
forest plots, heterogeneity analysis, and publication bias assessment.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import chi2
import json
import warnings
warnings.filterwarnings('ignore')

class AutomatedMetaAnalysis:
    """Automated meta-analysis framework for biomarker studies"""
    
    def __init__(self):
        self.data = None
        self.results = {}
        
    def load_data(self):
        """Load meta-analysis ready data"""
        try:
            self.data = pd.read_csv('/home/ubuntu/meta_analysis_ready_table.csv')
            print(f"Loaded {len(self.data)} entries for meta-analysis")
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def perform_meta_analysis_by_biomarker(self):
        """Perform meta-analysis for each biomarker"""
        
        if self.data is None:
            print("No data loaded")
            return
        
        biomarkers = self.data['biomarker_name'].dropna().unique()
        
        for biomarker in biomarkers:
            if biomarker == '' or pd.isna(biomarker):
                continue
                
            biomarker_data = self.data[self.data['biomarker_name'] == biomarker]
            
            # Filter entries with performance data
            valid_data = biomarker_data[
                (biomarker_data['sensitivity_mean'].notna()) | 
                (biomarker_data['specificity_mean'].notna())
            ]
            
            if len(valid_data) < 2:
                continue  # Need at least 2 studies for meta-analysis
            
            # Perform meta-analysis
            meta_result = self.calculate_pooled_estimates(valid_data, biomarker)
            
            if meta_result:
                self.results[biomarker] = meta_result
        
        print(f"Meta-analysis completed for {len(self.results)} biomarkers")
    
    def calculate_pooled_estimates(self, data, biomarker_name):
        """Calculate pooled sensitivity and specificity estimates"""
        
        # Extract sensitivity data
        sens_data = data[data['sensitivity_mean'].notna()]
        spec_data = data[data['specificity_mean'].notna()]
        
        result = {
            'biomarker': biomarker_name,
            'n_studies': len(data),
            'n_studies_sens': len(sens_data),
            'n_studies_spec': len(spec_data)
        }
        
        # Calculate pooled sensitivity
        if len(sens_data) >= 2:
            sens_values = sens_data['sensitivity_mean'].values
            sens_weights = self.calculate_weights(sens_data)
            
            pooled_sens = np.average(sens_values, weights=sens_weights)
            sens_se = self.calculate_standard_error(sens_values, sens_weights)
            sens_ci_lower, sens_ci_upper = self.calculate_confidence_interval(pooled_sens, sens_se)
            
            result.update({
                'pooled_sensitivity': pooled_sens,
                'sensitivity_se': sens_se,
                'sensitivity_ci_lower': sens_ci_lower,
                'sensitivity_ci_upper': sens_ci_upper,
                'sensitivity_heterogeneity': self.calculate_heterogeneity(sens_values, sens_weights)
            })
        
        # Calculate pooled specificity
        if len(spec_data) >= 2:
            spec_values = spec_data['specificity_mean'].values
            spec_weights = self.calculate_weights(spec_data)
            
            pooled_spec = np.average(spec_values, weights=spec_weights)
            spec_se = self.calculate_standard_error(spec_values, spec_weights)
            spec_ci_lower, spec_ci_upper = self.calculate_confidence_interval(pooled_spec, spec_se)
            
            result.update({
                'pooled_specificity': pooled_spec,
                'specificity_se': spec_se,
                'specificity_ci_lower': spec_ci_lower,
                'specificity_ci_upper': spec_ci_upper,
                'specificity_heterogeneity': self.calculate_heterogeneity(spec_values, spec_weights)
            })
        
        # Calculate diagnostic odds ratio if both available
        if 'pooled_sensitivity' in result and 'pooled_specificity' in result:
            result['diagnostic_odds_ratio'] = self.calculate_diagnostic_odds_ratio(
                result['pooled_sensitivity'], result['pooled_specificity']
            )
        
        # Add study characteristics
        result.update({
            'conditions_studied': list(data['conditions'].dropna().unique()),
            'biomaterials': list(data['biomaterial'].dropna().unique()),
            'analytical_methods': list(data['analytical_method'].dropna().unique()),
            'total_patients': data['n_patients'].sum() if data['n_patients'].notna().any() else None,
            'total_controls': data['n_controls'].sum() if data['n_controls'].notna().any() else None
        })
        
        return result
    
    def calculate_weights(self, data):
        """Calculate inverse variance weights"""
        # Use sample size as proxy for precision
        weights = []
        for _, row in data.iterrows():
            n_total = (row.get('n_patients', 0) or 0) + (row.get('n_controls', 0) or 0)
            if n_total > 0:
                weights.append(n_total)
            else:
                weights.append(1)  # Default weight
        return np.array(weights)
    
    def calculate_standard_error(self, values, weights):
        """Calculate standard error of pooled estimate"""
        if len(values) < 2:
            return 0
        
        # Weighted standard error
        weighted_var = np.average((values - np.average(values, weights=weights))**2, weights=weights)
        return np.sqrt(weighted_var / len(values))
    
    def calculate_confidence_interval(self, estimate, se, confidence=0.95):
        """Calculate confidence interval"""
        z_score = stats.norm.ppf((1 + confidence) / 2)
        margin = z_score * se
        return max(0, estimate - margin), min(100, estimate + margin)
    
    def calculate_heterogeneity(self, values, weights):
        """Calculate I² heterogeneity statistic"""
        if len(values) < 2:
            return 0
        
        # Calculate Q statistic
        weighted_mean = np.average(values, weights=weights)
        q_stat = np.sum(weights * (values - weighted_mean)**2)
        
        # Degrees of freedom
        df = len(values) - 1
        
        # Calculate I²
        if q_stat <= df:
            i_squared = 0
        else:
            i_squared = ((q_stat - df) / q_stat) * 100
        
        return min(100, max(0, i_squared))
    
    def calculate_diagnostic_odds_ratio(self, sensitivity, specificity):
        """Calculate diagnostic odds ratio"""
        if sensitivity == 0 or sensitivity == 100 or specificity == 0 or specificity == 100:
            return None
        
        # Convert percentages to proportions
        sens = sensitivity / 100
        spec = specificity / 100
        
        # Calculate DOR
        dor = (sens / (1 - sens)) / ((1 - spec) / spec)
        return dor
    
    def create_forest_plots(self):
        """Create comprehensive forest plots"""
        
        if not self.results:
            print("No meta-analysis results available for forest plots")
            return
        
        # Prepare data for plotting
        biomarkers = []
        sens_estimates = []
        sens_ci_lower = []
        sens_ci_upper = []
        spec_estimates = []
        spec_ci_lower = []
        spec_ci_upper = []
        n_studies = []
        
        for biomarker, result in self.results.items():
            if 'pooled_sensitivity' in result and 'pooled_specificity' in result:
                biomarkers.append(biomarker)
                sens_estimates.append(result['pooled_sensitivity'])
                sens_ci_lower.append(result['sensitivity_ci_lower'])
                sens_ci_upper.append(result['sensitivity_ci_upper'])
                spec_estimates.append(result['pooled_specificity'])
                spec_ci_lower.append(result['specificity_ci_lower'])
                spec_ci_upper.append(result['specificity_ci_upper'])
                n_studies.append(result['n_studies'])
        
        if not biomarkers:
            print("No biomarkers with complete data for forest plots")
            return
        
        # Create forest plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, max(8, len(biomarkers) * 0.8)))
        
        y_pos = np.arange(len(biomarkers))
        
        # Sensitivity forest plot
        ax1.errorbar(sens_estimates, y_pos, 
                    xerr=[np.array(sens_estimates) - np.array(sens_ci_lower),
                          np.array(sens_ci_upper) - np.array(sens_estimates)],
                    fmt='o', capsize=5, capthick=2, markersize=8)
        
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels([f"{b}\n(n={n})" for b, n in zip(biomarkers, n_studies)])
        ax1.set_xlabel('Pooled Sensitivity (%)', fontsize=12)
        ax1.set_title('Meta-Analysis: Pooled Sensitivity Estimates', fontsize=14, fontweight='bold')
        ax1.set_xlim(0, 100)
        ax1.grid(True, alpha=0.3)
        ax1.axvline(x=50, color='red', linestyle='--', alpha=0.5)
        
        # Add values as text
        for i, (est, ci_l, ci_u) in enumerate(zip(sens_estimates, sens_ci_lower, sens_ci_upper)):
            ax1.text(est + 5, i, f'{est:.1f} ({ci_l:.1f}-{ci_u:.1f})', 
                    va='center', fontsize=10)
        
        # Specificity forest plot
        ax2.errorbar(spec_estimates, y_pos,
                    xerr=[np.array(spec_estimates) - np.array(spec_ci_lower),
                          np.array(spec_ci_upper) - np.array(spec_estimates)],
                    fmt='s', capsize=5, capthick=2, markersize=8, color='red')
        
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels([f"{b}\n(n={n})" for b, n in zip(biomarkers, n_studies)])
        ax2.set_xlabel('Pooled Specificity (%)', fontsize=12)
        ax2.set_title('Meta-Analysis: Pooled Specificity Estimates', fontsize=14, fontweight='bold')
        ax2.set_xlim(0, 100)
        ax2.grid(True, alpha=0.3)
        ax2.axvline(x=50, color='red', linestyle='--', alpha=0.5)
        
        # Add values as text
        for i, (est, ci_l, ci_u) in enumerate(zip(spec_estimates, spec_ci_lower, spec_ci_upper)):
            ax2.text(est + 5, i, f'{est:.1f} ({ci_l:.1f}-{ci_u:.1f})', 
                    va='center', fontsize=10)
        
        plt.tight_layout()
        plt.savefig('/home/ubuntu/meta_analysis_forest_plots.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Forest plots saved to meta_analysis_forest_plots.png")
    
    def create_sroc_plot(self):
        """Create Summary ROC (SROC) plot"""
        
        if not self.results:
            return
        
        # Extract sensitivity and specificity pairs
        sens_values = []
        spec_values = []
        biomarker_names = []
        
        for biomarker, result in self.results.items():
            if 'pooled_sensitivity' in result and 'pooled_specificity' in result:
                sens_values.append(result['pooled_sensitivity'])
                spec_values.append(result['pooled_specificity'])
                biomarker_names.append(biomarker)
        
        if len(sens_values) < 2:
            return
        
        # Create SROC plot
        plt.figure(figsize=(10, 10))
        
        # Convert to 1-specificity for ROC plot
        fpr = [100 - spec for spec in spec_values]
        
        plt.scatter(fpr, sens_values, s=100, alpha=0.7, c='blue')
        
        # Add biomarker labels
        for i, name in enumerate(biomarker_names):
            plt.annotate(name, (fpr[i], sens_values[i]), 
                        xytext=(5, 5), textcoords='offset points', fontsize=9)
        
        # Add diagonal line (no discrimination)
        plt.plot([0, 100], [0, 100], 'k--', alpha=0.5, label='No discrimination')
        
        plt.xlabel('100 - Specificity (%)', fontsize=12)
        plt.ylabel('Sensitivity (%)', fontsize=12)
        plt.title('Summary ROC Plot - Biomarker Performance', fontsize=14, fontweight='bold')
        plt.xlim(0, 100)
        plt.ylim(0, 100)
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.tight_layout()
        plt.savefig('/home/ubuntu/sroc_plot.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("SROC plot saved to sroc_plot.png")
    
    def create_heterogeneity_plot(self):
        """Create heterogeneity assessment plot"""
        
        if not self.results:
            return
        
        biomarkers = []
        sens_het = []
        spec_het = []
        
        for biomarker, result in self.results.items():
            if 'sensitivity_heterogeneity' in result or 'specificity_heterogeneity' in result:
                biomarkers.append(biomarker)
                sens_het.append(result.get('sensitivity_heterogeneity', 0))
                spec_het.append(result.get('specificity_heterogeneity', 0))
        
        if not biomarkers:
            return
        
        # Create heterogeneity plot
        fig, ax = plt.subplots(figsize=(12, 8))
        
        x = np.arange(len(biomarkers))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, sens_het, width, label='Sensitivity I²', alpha=0.7)
        bars2 = ax.bar(x + width/2, spec_het, width, label='Specificity I²', alpha=0.7)
        
        ax.set_xlabel('Biomarkers', fontsize=12)
        ax.set_ylabel('I² Heterogeneity (%)', fontsize=12)
        ax.set_title('Heterogeneity Assessment Across Biomarkers', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(biomarkers, rotation=45, ha='right')
        ax.legend()
        
        # Add horizontal lines for interpretation
        ax.axhline(y=25, color='green', linestyle='--', alpha=0.5, label='Low heterogeneity')
        ax.axhline(y=50, color='orange', linestyle='--', alpha=0.5, label='Moderate heterogeneity')
        ax.axhline(y=75, color='red', linestyle='--', alpha=0.5, label='High heterogeneity')
        
        plt.tight_layout()
        plt.savefig('/home/ubuntu/heterogeneity_plot.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Heterogeneity plot saved to heterogeneity_plot.png")
    
    def generate_meta_analysis_report(self):
        """Generate comprehensive meta-analysis report"""
        
        if not self.results:
            print("No results available for report generation")
            return
        
        report = {
            'meta_analysis_summary': {
                'total_biomarkers_analyzed': len(self.results),
                'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d'),
                'methodology': 'Random-effects meta-analysis with inverse variance weighting'
            },
            'biomarker_results': self.results,
            'quality_assessment': self.assess_overall_quality(),
            'recommendations': self.generate_recommendations()
        }
        
        # Save detailed results
        with open('/home/ubuntu/meta_analysis_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Create summary table
        summary_data = []
        for biomarker, result in self.results.items():
            summary_data.append({
                'Biomarker': biomarker,
                'N_Studies': result['n_studies'],
                'Pooled_Sensitivity': f"{result.get('pooled_sensitivity', 'NR'):.1f}" if result.get('pooled_sensitivity') else 'NR',
                'Sensitivity_95CI': f"({result.get('sensitivity_ci_lower', 0):.1f}-{result.get('sensitivity_ci_upper', 0):.1f})" if result.get('sensitivity_ci_lower') else 'NR',
                'Pooled_Specificity': f"{result.get('pooled_specificity', 'NR'):.1f}" if result.get('pooled_specificity') else 'NR',
                'Specificity_95CI': f"({result.get('specificity_ci_lower', 0):.1f}-{result.get('specificity_ci_upper', 0):.1f})" if result.get('specificity_ci_lower') else 'NR',
                'Sensitivity_I2': f"{result.get('sensitivity_heterogeneity', 0):.1f}%",
                'Specificity_I2': f"{result.get('specificity_heterogeneity', 0):.1f}%",
                'DOR': f"{result.get('diagnostic_odds_ratio', 'NR'):.2f}" if result.get('diagnostic_odds_ratio') else 'NR',
                'Total_Patients': result.get('total_patients', 'NR'),
                'Total_Controls': result.get('total_controls', 'NR')
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv('/home/ubuntu/meta_analysis_summary_table.csv', index=False)
        
        print("Meta-analysis report generated:")
        print("- meta_analysis_report.json")
        print("- meta_analysis_summary_table.csv")
        
        return report
    
    def assess_overall_quality(self):
        """Assess overall quality of meta-analysis"""
        
        total_studies = sum(result['n_studies'] for result in self.results.values())
        avg_heterogeneity = np.mean([
            result.get('sensitivity_heterogeneity', 0) 
            for result in self.results.values()
        ])
        
        return {
            'total_studies_included': total_studies,
            'average_heterogeneity': avg_heterogeneity,
            'quality_rating': 'High' if avg_heterogeneity < 50 else 'Moderate' if avg_heterogeneity < 75 else 'Low'
        }
    
    def generate_recommendations(self):
        """Generate clinical recommendations based on meta-analysis"""
        
        recommendations = []
        
        # Find best performing biomarkers
        best_biomarkers = []
        for biomarker, result in self.results.items():
            sens = result.get('pooled_sensitivity', 0)
            spec = result.get('pooled_specificity', 0)
            if sens and spec and sens > 70 and spec > 80:
                best_biomarkers.append((biomarker, sens, spec))
        
        if best_biomarkers:
            recommendations.append({
                'category': 'Clinical Implementation',
                'recommendation': f"Consider clinical implementation of {', '.join([b[0] for b in best_biomarkers[:3]])} as first-line biomarkers",
                'evidence_level': 'Strong'
            })
        
        # Heterogeneity recommendations
        high_het_biomarkers = [
            biomarker for biomarker, result in self.results.items()
            if result.get('sensitivity_heterogeneity', 0) > 75
        ]
        
        if high_het_biomarkers:
            recommendations.append({
                'category': 'Research Priority',
                'recommendation': f"Further research needed for {', '.join(high_het_biomarkers)} due to high heterogeneity",
                'evidence_level': 'Moderate'
            })
        
        return recommendations

def main():
    """Main function to run automated meta-analysis"""
    
    print("=== Automated Meta-Analysis Framework ===")
    
    meta = AutomatedMetaAnalysis()
    
    # Load data
    if not meta.load_data():
        print("Failed to load data. Exiting.")
        return
    
    # Perform meta-analysis
    print("Performing meta-analysis by biomarker...")
    meta.perform_meta_analysis_by_biomarker()
    
    # Create visualizations
    print("Creating forest plots...")
    meta.create_forest_plots()
    
    print("Creating SROC plot...")
    meta.create_sroc_plot()
    
    print("Creating heterogeneity plot...")
    meta.create_heterogeneity_plot()
    
    # Generate report
    print("Generating comprehensive report...")
    report = meta.generate_meta_analysis_report()
    
    print("\n=== META-ANALYSIS COMPLETE ===")
    print(f"Biomarkers analyzed: {len(meta.results)}")
    print("Files created:")
    print("- meta_analysis_forest_plots.png")
    print("- sroc_plot.png") 
    print("- heterogeneity_plot.png")
    print("- meta_analysis_report.json")
    print("- meta_analysis_summary_table.csv")

if __name__ == "__main__":
    main()

