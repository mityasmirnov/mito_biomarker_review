#!/usr/bin/env python3
"""
Enhanced Systematic Review Framework for Biofluid Biomarkers in Mitochondrial Diseases
This framework integrates multiple data sources, performs meta-analysis, and creates
a comprehensive knowledge base for systematic review and future research.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import chi2_contingency
import json
import re
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

class BiomarkerMetaAnalysis:
    """Class for performing meta-analysis on biomarker data"""
    
    def __init__(self):
        self.studies_data = []
        self.biomarker_data = {}
        
    def load_all_data_sources(self):
        """Load and integrate all available data sources"""
        data_sources = {}
        
        # Load uploaded CSV files
        csv_files = [
            'systematic_review_cohorts.csv',
            'systematic_review_biomarkers.csv', 
            'disease_specific_biomarkers.csv',
            'mitochondrial_biomarkers_performance.csv',
            'mitochondrial_biomarkers_comparison.csv',
            'mitochondrial_biomarkers_cohorts.csv'
        ]
        
        for file in csv_files:
            try:
                df = pd.read_csv(f'/home/ubuntu/upload/{file}')
                data_sources[file.replace('.csv', '')] = df
                print(f"Loaded {file}: {len(df)} rows")
            except Exception as e:
                print(f"Could not load {file}: {e}")
        
        # Load our original analysis
        try:
            original_data = pd.read_csv('/home/ubuntu/biomarker_summary_table.csv')
            data_sources['original_analysis'] = original_data
            print(f"Loaded original analysis: {len(original_data)} rows")
        except Exception as e:
            print(f"Could not load original analysis: {e}")
            
        return data_sources
    
    def create_master_study_database(self, data_sources):
        """Create comprehensive study database with unique study IDs"""
        studies = []
        study_id = 1
        
        # Process systematic review cohorts
        if 'systematic_review_cohorts' in data_sources:
            df = data_sources['systematic_review_cohorts']
            for _, row in df.iterrows():
                study = {
                    'study_id': f'S{study_id:03d}',
                    'first_author': row.get('Study_First_Author', 'Unknown'),
                    'year': self.extract_year(row.get('Study_First_Author', '')),
                    'primary_biomarker': row.get('Primary_Biomarker', ''),
                    'total_cohort_size': self.parse_cohort_size(row.get('Total_Cohort_Size', '')),
                    'age_range': row.get('Age_Range', ''),
                    'conditions': row.get('Specific_Conditions', ''),
                    'location': row.get('Geographic_Location', ''),
                    'key_findings': row.get('Key_Findings', ''),
                    'data_source': 'systematic_review_cohorts'
                }
                studies.append(study)
                study_id += 1
        
        # Add studies from other sources
        # Process original analysis data
        if 'original_analysis' in data_sources:
            df = data_sources['original_analysis']
            conditions = df['Condition'].unique()
            for condition in conditions:
                study = {
                    'study_id': f'S{study_id:03d}',
                    'first_author': 'Multiple Studies',
                    'year': '2024',
                    'primary_biomarker': 'Multiple',
                    'total_cohort_size': len(df[df['Condition'] == condition]),
                    'age_range': 'Mixed',
                    'conditions': condition,
                    'location': 'Multiple',
                    'key_findings': f'Analysis of {condition} biomarkers',
                    'data_source': 'original_analysis'
                }
                studies.append(study)
                study_id += 1
        
        return pd.DataFrame(studies)
    
    def create_master_biomarker_database(self, data_sources):
        """Create comprehensive biomarker database"""
        biomarkers = []
        biomarker_id = 1
        
        # Process systematic review biomarkers
        if 'systematic_review_biomarkers' in data_sources:
            df = data_sources['systematic_review_biomarkers']
            for _, row in df.iterrows():
                biomarker = {
                    'biomarker_id': f'B{biomarker_id:03d}',
                    'biomarker_name': row.get('Biomarker', ''),
                    'molecular_class': row.get('Molecular_Class', ''),
                    'biomaterial': row.get('Biomaterial', ''),
                    'analytical_method': row.get('Analytical_Method', ''),
                    'sensitivity_percent': self.parse_performance_metric(row.get('Sensitivity_%', '')),
                    'specificity_percent': self.parse_performance_metric(row.get('Specificity_%', '')),
                    'disease_specificity': row.get('Disease_Specificity', ''),
                    'age_group_performance': row.get('Age_Group_Performance', ''),
                    'data_source': 'systematic_review_biomarkers'
                }
                biomarkers.append(biomarker)
                biomarker_id += 1
        
        # Process performance data
        if 'mitochondrial_biomarkers_performance' in data_sources:
            df = data_sources['mitochondrial_biomarkers_performance']
            for _, row in df.iterrows():
                biomarker = {
                    'biomarker_id': f'B{biomarker_id:03d}',
                    'biomarker_name': row.get('Biomarker', ''),
                    'molecular_class': row.get('Molecular_Origin', ''),
                    'biomaterial': row.get('Biomaterial', ''),
                    'analytical_method': row.get('Analytical_Method', ''),
                    'sensitivity_percent': self.parse_performance_metric(row.get('Sensitivity_%', '')),
                    'specificity_percent': self.parse_performance_metric(row.get('Specificity_%', '')),
                    'clinical_application': row.get('Clinical_Application', ''),
                    'data_source': 'mitochondrial_biomarkers_performance'
                }
                biomarkers.append(biomarker)
                biomarker_id += 1
        
        # Process original analysis
        if 'original_analysis' in data_sources:
            df = data_sources['original_analysis']
            for _, row in df.iterrows():
                biomarker = {
                    'biomarker_id': f'B{biomarker_id:03d}',
                    'biomarker_name': row.get('Biomarker', ''),
                    'molecular_class': row.get('Molecular_Type', ''),
                    'biomaterial': row.get('Biomaterial', ''),
                    'analytical_method': row.get('Analytical_Methods', ''),
                    'sensitivity_range': row.get('Sensitivity_Range', ''),
                    'specificity_range': row.get('Specificity_Range', ''),
                    'auc_range': row.get('AUC_Range', ''),
                    'condition': row.get('Condition', ''),
                    'clinical_application': row.get('Clinical_Application', ''),
                    'data_source': 'original_analysis'
                }
                biomarkers.append(biomarker)
                biomarker_id += 1
        
        return pd.DataFrame(biomarkers)
    
    def create_detailed_performance_table(self, data_sources):
        """Create detailed performance table for meta-analysis"""
        performance_data = []
        entry_id = 1
        
        # Extract detailed performance metrics from all sources
        for source_name, df in data_sources.items():
            if source_name == 'systematic_review_biomarkers':
                for _, row in df.iterrows():
                    entry = {
                        'entry_id': f'E{entry_id:03d}',
                        'study_reference': 'Multiple studies',
                        'biomarker_name': row.get('Biomarker', ''),
                        'condition': row.get('Disease_Specificity', ''),
                        'biomaterial': row.get('Biomaterial', ''),
                        'analytical_method': row.get('Analytical_Method', ''),
                        'sensitivity': self.parse_performance_metric(row.get('Sensitivity_%', '')),
                        'specificity': self.parse_performance_metric(row.get('Specificity_%', '')),
                        'n_patients': None,
                        'n_controls': None,
                        'age_group': row.get('Age_Group_Performance', ''),
                        'molecular_type': row.get('Molecular_Class', ''),
                        'data_source': source_name
                    }
                    performance_data.append(entry)
                    entry_id += 1
        
        return pd.DataFrame(performance_data)
    
    def perform_meta_analysis_by_biomarker(self, performance_df):
        """Perform meta-analysis for each biomarker"""
        meta_results = {}
        
        biomarkers = performance_df['biomarker_name'].unique()
        
        for biomarker in biomarkers:
            if pd.isna(biomarker) or biomarker == '':
                continue
                
            biomarker_data = performance_df[performance_df['biomarker_name'] == biomarker]
            
            # Extract sensitivity and specificity data
            sens_data = []
            spec_data = []
            
            for _, row in biomarker_data.iterrows():
                if pd.notna(row['sensitivity']):
                    sens_values = self.extract_numeric_values(str(row['sensitivity']))
                    sens_data.extend(sens_values)
                
                if pd.notna(row['specificity']):
                    spec_values = self.extract_numeric_values(str(row['specificity']))
                    spec_data.extend(spec_values)
            
            if sens_data or spec_data:
                meta_results[biomarker] = {
                    'n_studies': len(biomarker_data),
                    'sensitivity_mean': np.mean(sens_data) if sens_data else None,
                    'sensitivity_std': np.std(sens_data) if len(sens_data) > 1 else None,
                    'sensitivity_range': f"{min(sens_data)}-{max(sens_data)}" if sens_data else None,
                    'specificity_mean': np.mean(spec_data) if spec_data else None,
                    'specificity_std': np.std(spec_data) if len(spec_data) > 1 else None,
                    'specificity_range': f"{min(spec_data)}-{max(spec_data)}" if spec_data else None,
                    'conditions_studied': list(biomarker_data['condition'].unique()),
                    'biomaterials': list(biomarker_data['biomaterial'].unique()),
                    'analytical_methods': list(biomarker_data['analytical_method'].unique())
                }
        
        return meta_results
    
    def create_forest_plots(self, meta_results, output_dir='/home/ubuntu'):
        """Create forest plots for meta-analysis results"""
        
        # Prepare data for forest plot
        biomarkers = []
        sensitivities = []
        specificities = []
        n_studies = []
        
        for biomarker, results in meta_results.items():
            if results['sensitivity_mean'] is not None and results['specificity_mean'] is not None:
                biomarkers.append(biomarker)
                sensitivities.append(results['sensitivity_mean'])
                specificities.append(results['specificity_mean'])
                n_studies.append(results['n_studies'])
        
        if not biomarkers:
            print("No data available for forest plots")
            return
        
        # Create forest plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, max(8, len(biomarkers) * 0.5)))
        
        # Sensitivity forest plot
        y_pos = np.arange(len(biomarkers))
        ax1.barh(y_pos, sensitivities, alpha=0.7, color='blue')
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(biomarkers)
        ax1.set_xlabel('Sensitivity (%)')
        ax1.set_title('Meta-Analysis: Biomarker Sensitivity')
        ax1.set_xlim(0, 100)
        
        # Add study counts
        for i, (sens, n) in enumerate(zip(sensitivities, n_studies)):
            ax1.text(sens + 2, i, f'n={n}', va='center')
        
        # Specificity forest plot
        ax2.barh(y_pos, specificities, alpha=0.7, color='red')
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(biomarkers)
        ax2.set_xlabel('Specificity (%)')
        ax2.set_title('Meta-Analysis: Biomarker Specificity')
        ax2.set_xlim(0, 100)
        
        # Add study counts
        for i, (spec, n) in enumerate(zip(specificities, n_studies)):
            ax2.text(spec + 2, i, f'n={n}', va='center')
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/biomarker_meta_analysis_forest_plot.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Forest plot saved to {output_dir}/biomarker_meta_analysis_forest_plot.png")
    
    def create_comprehensive_summary_table(self, studies_df, biomarkers_df, performance_df, meta_results):
        """Create comprehensive summary table for systematic review"""
        
        summary_data = []
        
        for biomarker, results in meta_results.items():
            if results['sensitivity_mean'] is not None or results['specificity_mean'] is not None:
                summary_data.append({
                    'Biomarker': biomarker,
                    'N_Studies': results['n_studies'],
                    'Sensitivity_Mean': f"{results['sensitivity_mean']:.1f}" if results['sensitivity_mean'] else 'NR',
                    'Sensitivity_Range': results['sensitivity_range'] if results['sensitivity_range'] else 'NR',
                    'Specificity_Mean': f"{results['specificity_mean']:.1f}" if results['specificity_mean'] else 'NR',
                    'Specificity_Range': results['specificity_range'] if results['specificity_range'] else 'NR',
                    'Conditions_Studied': '; '.join([c for c in results['conditions_studied'] if pd.notna(c) and c != '']),
                    'Biomaterials': '; '.join([b for b in results['biomaterials'] if pd.notna(b) and b != '']),
                    'Analytical_Methods': '; '.join([m for m in results['analytical_methods'] if pd.notna(m) and m != ''])
                })
        
        return pd.DataFrame(summary_data)
    
    # Helper methods
    def extract_year(self, author_string):
        """Extract year from author string"""
        year_match = re.search(r'\((\d{4})\)', str(author_string))
        return year_match.group(1) if year_match else '2024'
    
    def parse_cohort_size(self, size_string):
        """Parse cohort size from string"""
        if pd.isna(size_string):
            return None
        numbers = re.findall(r'\d+', str(size_string))
        return int(numbers[0]) if numbers else None
    
    def parse_performance_metric(self, metric_string):
        """Parse performance metric from string"""
        if pd.isna(metric_string):
            return None
        # Extract first number found
        numbers = re.findall(r'\d+(?:\.\d+)?', str(metric_string))
        return float(numbers[0]) if numbers else None
    
    def extract_numeric_values(self, text):
        """Extract all numeric values from text"""
        if pd.isna(text) or text == '':
            return []
        
        # Find all numeric patterns including ranges
        patterns = re.findall(r'(\d+(?:\.\d+)?)', str(text))
        return [float(p) for p in patterns]

def main():
    """Main function to run enhanced systematic review analysis"""
    
    print("=== Enhanced Systematic Review Framework ===")
    print("Loading and integrating all data sources...")
    
    # Initialize meta-analysis framework
    meta_analyzer = BiomarkerMetaAnalysis()
    
    # Load all data sources
    data_sources = meta_analyzer.load_all_data_sources()
    
    # Create master databases
    print("\nCreating master study database...")
    studies_df = meta_analyzer.create_master_study_database(data_sources)
    studies_df.to_csv('/home/ubuntu/master_study_database.csv', index=False)
    print(f"Created master study database with {len(studies_df)} studies")
    
    print("\nCreating master biomarker database...")
    biomarkers_df = meta_analyzer.create_master_biomarker_database(data_sources)
    biomarkers_df.to_csv('/home/ubuntu/master_biomarker_database.csv', index=False)
    print(f"Created master biomarker database with {len(biomarkers_df)} biomarkers")
    
    print("\nCreating detailed performance table...")
    performance_df = meta_analyzer.create_detailed_performance_table(data_sources)
    performance_df.to_csv('/home/ubuntu/detailed_performance_table.csv', index=False)
    print(f"Created detailed performance table with {len(performance_df)} entries")
    
    # Perform meta-analysis
    print("\nPerforming meta-analysis by biomarker...")
    meta_results = meta_analyzer.perform_meta_analysis_by_biomarker(performance_df)
    
    # Save meta-analysis results
    with open('/home/ubuntu/meta_analysis_results.json', 'w') as f:
        json.dump(meta_results, f, indent=2, default=str)
    print(f"Meta-analysis completed for {len(meta_results)} biomarkers")
    
    # Create forest plots
    print("\nCreating forest plots...")
    meta_analyzer.create_forest_plots(meta_results)
    
    # Create comprehensive summary table
    print("\nCreating comprehensive summary table...")
    summary_df = meta_analyzer.create_comprehensive_summary_table(
        studies_df, biomarkers_df, performance_df, meta_results
    )
    summary_df.to_csv('/home/ubuntu/comprehensive_meta_analysis_summary.csv', index=False)
    print(f"Created comprehensive summary with {len(summary_df)} biomarkers")
    
    # Print summary statistics
    print("\n=== SUMMARY STATISTICS ===")
    print(f"Total studies analyzed: {len(studies_df)}")
    print(f"Total biomarkers identified: {len(biomarkers_df)}")
    print(f"Biomarkers with meta-analysis data: {len(meta_results)}")
    print(f"Data sources integrated: {len(data_sources)}")
    
    # Top performing biomarkers
    if not summary_df.empty:
        print("\n=== TOP PERFORMING BIOMARKERS ===")
        # Sort by sensitivity mean (convert to numeric first)
        summary_df['Sensitivity_Numeric'] = pd.to_numeric(summary_df['Sensitivity_Mean'].replace('NR', np.nan), errors='coerce')
        top_biomarkers = summary_df.dropna(subset=['Sensitivity_Numeric']).nlargest(5, 'Sensitivity_Numeric')
        
        for _, row in top_biomarkers.iterrows():
            print(f"{row['Biomarker']}: Sensitivity {row['Sensitivity_Mean']}%, Specificity {row['Specificity_Mean']}% ({row['N_Studies']} studies)")
    
    print("\n=== FILES CREATED ===")
    print("- master_study_database.csv")
    print("- master_biomarker_database.csv") 
    print("- detailed_performance_table.csv")
    print("- meta_analysis_results.json")
    print("- comprehensive_meta_analysis_summary.csv")
    print("- biomarker_meta_analysis_forest_plot.png")
    
    print("\nEnhanced systematic review framework completed!")

if __name__ == "__main__":
    main()

