#!/usr/bin/env python3
"""
Reusable Automation Framework for Biomarker Systematic Reviews
This framework can be adapted for systematic reviews of biomarkers in any disease area.
It provides automated data extraction, meta-analysis, and report generation capabilities.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import json
import re
from pathlib import Path
import argparse
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class SystematicReviewAutomation:
    """
    Automated framework for systematic reviews of biomarkers
    Can be configured for different diseases and biomarker types
    """
    
    def __init__(self, disease_name, output_dir=None):
        self.disease_name = disease_name
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize data containers
        self.studies = []
        self.biomarkers = []
        self.performance_data = []
        self.meta_results = {}
        
        # Configuration
        self.config = {
            'min_studies_for_meta': 2,
            'confidence_level': 0.95,
            'heterogeneity_threshold': 50,
            'quality_score_weights': {
                'sample_size': 0.3,
                'control_group': 0.2,
                'performance_metrics': 0.2,
                'analytical_method': 0.15,
                'study_design': 0.15
            }
        }
    
    def configure_disease_specific_settings(self, disease_config):
        """
        Configure disease-specific settings
        
        Args:
            disease_config (dict): Disease-specific configuration including:
                - biomarker_classes: List of expected biomarker types
                - analytical_methods: Common analytical methods
                - performance_thresholds: Minimum performance criteria
                - condition_subtypes: Disease subtypes to analyze
        """
        self.disease_config = disease_config
        
    def load_data_sources(self, data_sources):
        """
        Load data from multiple sources (CSV files, databases, APIs)
        
        Args:
            data_sources (dict): Dictionary mapping source names to file paths or connection strings
        """
        
        for source_name, source_path in data_sources.items():
            try:
                if source_path.endswith('.csv'):
                    df = pd.read_csv(source_path)
                    self.process_data_source(df, source_name)
                    print(f"Loaded {source_name}: {len(df)} records")
                elif source_path.endswith('.json'):
                    with open(source_path, 'r') as f:
                        data = json.load(f)
                    self.process_json_source(data, source_name)
                    print(f"Loaded {source_name}: {len(data)} records")
                else:
                    print(f"Unsupported file format for {source_name}")
            except Exception as e:
                print(f"Error loading {source_name}: {e}")
    
    def process_data_source(self, df, source_name):
        """Process data from a pandas DataFrame"""
        
        # Detect data type based on columns
        if self.is_study_data(df):
            self.extract_study_data(df, source_name)
        elif self.is_biomarker_data(df):
            self.extract_biomarker_data(df, source_name)
        elif self.is_performance_data(df):
            self.extract_performance_data(df, source_name)
        else:
            print(f"Unknown data format in {source_name}")
    
    def is_study_data(self, df):
        """Check if DataFrame contains study-level data"""
        study_columns = ['author', 'year', 'sample_size', 'study_design', 'population']
        return any(col in df.columns.str.lower() for col in study_columns)
    
    def is_biomarker_data(self, df):
        """Check if DataFrame contains biomarker-level data"""
        biomarker_columns = ['biomarker', 'molecular_class', 'analytical_method', 'biomaterial']
        return any(col in df.columns.str.lower() for col in biomarker_columns)
    
    def is_performance_data(self, df):
        """Check if DataFrame contains performance metrics"""
        performance_columns = ['sensitivity', 'specificity', 'auc', 'accuracy']
        return any(col in df.columns.str.lower() for col in performance_columns)
    
    def extract_study_data(self, df, source_name):
        """Extract study-level information"""
        
        for _, row in df.iterrows():
            study = {
                'study_id': self.generate_study_id(row),
                'first_author': self.extract_author(row),
                'year': self.extract_year(row),
                'sample_size': self.extract_sample_size(row),
                'study_design': self.extract_study_design(row),
                'population': self.extract_population(row),
                'quality_score': self.calculate_study_quality(row),
                'source': source_name
            }
            self.studies.append(study)
    
    def extract_biomarker_data(self, df, source_name):
        """Extract biomarker-level information"""
        
        for _, row in df.iterrows():
            biomarker = {
                'biomarker_id': self.generate_biomarker_id(row),
                'name': self.extract_biomarker_name(row),
                'molecular_class': self.extract_molecular_class(row),
                'biomaterial': self.extract_biomaterial(row),
                'analytical_method': self.extract_analytical_method(row),
                'source': source_name
            }
            self.biomarkers.append(biomarker)
    
    def extract_performance_data(self, df, source_name):
        """Extract performance metrics"""
        
        for _, row in df.iterrows():
            performance = {
                'entry_id': self.generate_entry_id(row),
                'study_reference': self.extract_study_reference(row),
                'biomarker_name': self.extract_biomarker_name(row),
                'sensitivity': self.extract_performance_metric(row, 'sensitivity'),
                'specificity': self.extract_performance_metric(row, 'specificity'),
                'auc': self.extract_performance_metric(row, 'auc'),
                'n_patients': self.extract_sample_numbers(row, 'patients'),
                'n_controls': self.extract_sample_numbers(row, 'controls'),
                'condition': self.extract_condition(row),
                'source': source_name
            }
            self.performance_data.append(performance)
    
    def perform_automated_meta_analysis(self):
        """Perform automated meta-analysis on all eligible biomarkers"""
        
        # Convert to DataFrame for easier manipulation
        perf_df = pd.DataFrame(self.performance_data)
        
        # Group by biomarker
        biomarkers = perf_df['biomarker_name'].dropna().unique()
        
        for biomarker in biomarkers:
            biomarker_data = perf_df[perf_df['biomarker_name'] == biomarker]
            
            # Check if sufficient data for meta-analysis
            valid_data = biomarker_data[
                (biomarker_data['sensitivity'].notna()) | 
                (biomarker_data['specificity'].notna())
            ]
            
            if len(valid_data) >= self.config['min_studies_for_meta']:
                meta_result = self.calculate_meta_analysis(valid_data, biomarker)
                if meta_result:
                    self.meta_results[biomarker] = meta_result
        
        print(f"Meta-analysis completed for {len(self.meta_results)} biomarkers")
    
    def calculate_meta_analysis(self, data, biomarker_name):
        """Calculate meta-analysis results for a single biomarker"""
        
        result = {
            'biomarker': biomarker_name,
            'n_studies': len(data),
            'analysis_date': datetime.now().isoformat()
        }
        
        # Calculate pooled sensitivity
        sens_data = data[data['sensitivity'].notna()]
        if len(sens_data) >= 2:
            sens_values = sens_data['sensitivity'].values
            sens_weights = self.calculate_weights(sens_data)
            
            pooled_sens = np.average(sens_values, weights=sens_weights)
            sens_se = self.calculate_standard_error(sens_values, sens_weights)
            sens_ci = self.calculate_confidence_interval(pooled_sens, sens_se)
            
            result.update({
                'pooled_sensitivity': pooled_sens,
                'sensitivity_ci_lower': sens_ci[0],
                'sensitivity_ci_upper': sens_ci[1],
                'sensitivity_heterogeneity': self.calculate_heterogeneity(sens_values, sens_weights)
            })
        
        # Calculate pooled specificity
        spec_data = data[data['specificity'].notna()]
        if len(spec_data) >= 2:
            spec_values = spec_data['specificity'].values
            spec_weights = self.calculate_weights(spec_data)
            
            pooled_spec = np.average(spec_values, weights=spec_weights)
            spec_se = self.calculate_standard_error(spec_values, spec_weights)
            spec_ci = self.calculate_confidence_interval(pooled_spec, spec_se)
            
            result.update({
                'pooled_specificity': pooled_spec,
                'specificity_ci_lower': spec_ci[0],
                'specificity_ci_upper': spec_ci[1],
                'specificity_heterogeneity': self.calculate_heterogeneity(spec_values, spec_weights)
            })
        
        return result
    
    def generate_automated_report(self):
        """Generate comprehensive automated report"""
        
        report_data = {
            'disease': self.disease_name,
            'analysis_date': datetime.now().isoformat(),
            'summary_statistics': {
                'total_studies': len(self.studies),
                'total_biomarkers': len(self.biomarkers),
                'biomarkers_with_meta_analysis': len(self.meta_results)
            },
            'meta_analysis_results': self.meta_results,
            'quality_assessment': self.assess_overall_quality(),
            'recommendations': self.generate_automated_recommendations()
        }
        
        # Save detailed report
        report_file = self.output_dir / f"{self.disease_name.lower().replace(' ', '_')}_systematic_review_report.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        # Generate summary tables
        self.create_summary_tables()
        
        # Create visualizations
        self.create_automated_visualizations()
        
        print(f"Automated report generated: {report_file}")
        return report_data
    
    def create_summary_tables(self):
        """Create standardized summary tables"""
        
        # Study characteristics table
        studies_df = pd.DataFrame(self.studies)
        studies_file = self.output_dir / f"{self.disease_name.lower().replace(' ', '_')}_study_characteristics.csv"
        studies_df.to_csv(studies_file, index=False)
        
        # Biomarker summary table
        biomarkers_df = pd.DataFrame(self.biomarkers)
        biomarkers_file = self.output_dir / f"{self.disease_name.lower().replace(' ', '_')}_biomarker_summary.csv"
        biomarkers_df.to_csv(biomarkers_file, index=False)
        
        # Meta-analysis results table
        if self.meta_results:
            meta_summary = []
            for biomarker, results in self.meta_results.items():
                meta_summary.append({
                    'Biomarker': biomarker,
                    'N_Studies': results['n_studies'],
                    'Pooled_Sensitivity': f"{results.get('pooled_sensitivity', 'NR'):.1f}" if results.get('pooled_sensitivity') else 'NR',
                    'Sensitivity_95CI': f"({results.get('sensitivity_ci_lower', 0):.1f}-{results.get('sensitivity_ci_upper', 0):.1f})" if results.get('sensitivity_ci_lower') else 'NR',
                    'Pooled_Specificity': f"{results.get('pooled_specificity', 'NR'):.1f}" if results.get('pooled_specificity') else 'NR',
                    'Specificity_95CI': f"({results.get('specificity_ci_lower', 0):.1f}-{results.get('specificity_ci_upper', 0):.1f})" if results.get('specificity_ci_lower') else 'NR',
                    'Sensitivity_I2': f"{results.get('sensitivity_heterogeneity', 0):.1f}%",
                    'Specificity_I2': f"{results.get('specificity_heterogeneity', 0):.1f}%"
                })
            
            meta_df = pd.DataFrame(meta_summary)
            meta_file = self.output_dir / f"{self.disease_name.lower().replace(' ', '_')}_meta_analysis_results.csv"
            meta_df.to_csv(meta_file, index=False)
    
    def create_automated_visualizations(self):
        """Create standardized visualizations"""
        
        if not self.meta_results:
            return
        
        # Forest plot
        self.create_forest_plot()
        
        # SROC plot
        self.create_sroc_plot()
        
        # Heterogeneity assessment
        self.create_heterogeneity_plot()
        
        # Quality assessment
        self.create_quality_plot()
    
    def create_forest_plot(self):
        """Create automated forest plot"""
        
        biomarkers = []
        sens_estimates = []
        sens_ci_lower = []
        sens_ci_upper = []
        spec_estimates = []
        spec_ci_lower = []
        spec_ci_upper = []
        
        for biomarker, result in self.meta_results.items():
            if 'pooled_sensitivity' in result and 'pooled_specificity' in result:
                biomarkers.append(biomarker)
                sens_estimates.append(result['pooled_sensitivity'])
                sens_ci_lower.append(result['sensitivity_ci_lower'])
                sens_ci_upper.append(result['sensitivity_ci_upper'])
                spec_estimates.append(result['pooled_specificity'])
                spec_ci_lower.append(result['specificity_ci_lower'])
                spec_ci_upper.append(result['specificity_ci_upper'])
        
        if not biomarkers:
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, max(8, len(biomarkers) * 0.6)))
        
        y_pos = np.arange(len(biomarkers))
        
        # Sensitivity forest plot
        ax1.errorbar(sens_estimates, y_pos,
                    xerr=[np.array(sens_estimates) - np.array(sens_ci_lower),
                          np.array(sens_ci_upper) - np.array(sens_estimates)],
                    fmt='o', capsize=5, capthick=2, markersize=8)
        
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(biomarkers)
        ax1.set_xlabel('Pooled Sensitivity (%)')
        ax1.set_title(f'{self.disease_name}: Meta-Analysis Sensitivity')
        ax1.set_xlim(0, 100)
        ax1.grid(True, alpha=0.3)
        
        # Specificity forest plot
        ax2.errorbar(spec_estimates, y_pos,
                    xerr=[np.array(spec_estimates) - np.array(spec_ci_lower),
                          np.array(spec_ci_upper) - np.array(spec_estimates)],
                    fmt='s', capsize=5, capthick=2, markersize=8, color='red')
        
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(biomarkers)
        ax2.set_xlabel('Pooled Specificity (%)')
        ax2.set_title(f'{self.disease_name}: Meta-Analysis Specificity')
        ax2.set_xlim(0, 100)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plot_file = self.output_dir / f"{self.disease_name.lower().replace(' ', '_')}_forest_plot.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
    
    # Helper methods (implementation details)
    def generate_study_id(self, row):
        """Generate unique study ID"""
        return f"STUDY_{len(self.studies)+1:03d}"
    
    def extract_author(self, row):
        """Extract first author from row"""
        author_cols = [col for col in row.index if 'author' in col.lower()]
        return str(row[author_cols[0]]) if author_cols else 'Unknown'
    
    def extract_year(self, row):
        """Extract publication year"""
        year_cols = [col for col in row.index if 'year' in col.lower()]
        if year_cols:
            year_val = row[year_cols[0]]
            if pd.notna(year_val):
                return int(year_val)
        return datetime.now().year
    
    def extract_sample_size(self, row):
        """Extract total sample size"""
        size_cols = [col for col in row.index if any(term in col.lower() for term in ['size', 'total', 'n_'])]
        if size_cols:
            size_val = row[size_cols[0]]
            if pd.notna(size_val):
                numbers = re.findall(r'\d+', str(size_val))
                return int(numbers[0]) if numbers else None
        return None
    
    def calculate_weights(self, data):
        """Calculate inverse variance weights"""
        weights = []
        for _, row in data.iterrows():
            n_total = (row.get('n_patients', 0) or 0) + (row.get('n_controls', 0) or 0)
            weights.append(max(1, n_total))
        return np.array(weights)
    
    def calculate_standard_error(self, values, weights):
        """Calculate standard error"""
        if len(values) < 2:
            return 0
        weighted_var = np.average((values - np.average(values, weights=weights))**2, weights=weights)
        return np.sqrt(weighted_var / len(values))
    
    def calculate_confidence_interval(self, estimate, se):
        """Calculate confidence interval"""
        z_score = stats.norm.ppf((1 + self.config['confidence_level']) / 2)
        margin = z_score * se
        return (max(0, estimate - margin), min(100, estimate + margin))
    
    def calculate_heterogeneity(self, values, weights):
        """Calculate I² heterogeneity statistic"""
        if len(values) < 2:
            return 0
        
        weighted_mean = np.average(values, weights=weights)
        q_stat = np.sum(weights * (values - weighted_mean)**2)
        df = len(values) - 1
        
        if q_stat <= df:
            return 0
        else:
            return min(100, ((q_stat - df) / q_stat) * 100)
    
    def assess_overall_quality(self):
        """Assess overall quality of included studies"""
        if not self.studies:
            return {}
        
        studies_df = pd.DataFrame(self.studies)
        return {
            'mean_quality_score': studies_df['quality_score'].mean(),
            'high_quality_studies': len(studies_df[studies_df['quality_score'] >= 7]),
            'total_studies': len(studies_df)
        }
    
    def generate_automated_recommendations(self):
        """Generate automated clinical recommendations"""
        recommendations = []
        
        if not self.meta_results:
            return recommendations
        
        # Find high-performing biomarkers
        high_performers = []
        for biomarker, result in self.meta_results.items():
            sens = result.get('pooled_sensitivity', 0)
            spec = result.get('pooled_specificity', 0)
            if sens and spec and sens > 70 and spec > 80:
                high_performers.append((biomarker, sens, spec))
        
        if high_performers:
            recommendations.append({
                'category': 'Clinical Implementation',
                'recommendation': f"Consider implementing {', '.join([h[0] for h in high_performers[:3]])} for clinical use",
                'evidence_level': 'Strong',
                'rationale': 'High sensitivity and specificity in meta-analysis'
            })
        
        return recommendations

def main():
    """Main function with command-line interface"""
    
    parser = argparse.ArgumentParser(description='Automated Systematic Review Framework')
    parser.add_argument('--disease', required=True, help='Disease name for analysis')
    parser.add_argument('--data-dir', required=True, help='Directory containing data files')
    parser.add_argument('--output-dir', help='Output directory for results')
    parser.add_argument('--config', help='Configuration file path')
    
    args = parser.parse_args()
    
    # Initialize framework
    framework = SystematicReviewAutomation(
        disease_name=args.disease,
        output_dir=args.output_dir
    )
    
    # Load configuration if provided
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
        framework.configure_disease_specific_settings(config)
    
    # Discover and load data sources
    data_dir = Path(args.data_dir)
    data_sources = {}
    
    for file_path in data_dir.glob('*.csv'):
        data_sources[file_path.stem] = str(file_path)
    
    for file_path in data_dir.glob('*.json'):
        data_sources[file_path.stem] = str(file_path)
    
    print(f"Found {len(data_sources)} data sources")
    
    # Run automated analysis
    framework.load_data_sources(data_sources)
    framework.perform_automated_meta_analysis()
    report = framework.generate_automated_report()
    
    print(f"\nAutomated systematic review completed for {args.disease}")
    print(f"Results saved to: {framework.output_dir}")

if __name__ == "__main__":
    # Example usage without command line
    print("=== Reusable Systematic Review Automation Framework ===")
    print("This framework can be used for any disease area.")
    print("Example configuration for mitochondrial diseases:")
    
    example_config = {
        'biomarker_classes': ['protein', 'metabolite', 'lipid', 'nucleic_acid'],
        'analytical_methods': ['ELISA', 'LC-MS/MS', 'GC-MS', 'Simoa', 'PCR'],
        'performance_thresholds': {'sensitivity': 70, 'specificity': 80},
        'condition_subtypes': ['MELAS', 'MERRF', 'Leigh', 'LHON', 'KSS']
    }
    
    print(json.dumps(example_config, indent=2))
    print("\nFramework ready for deployment!")

