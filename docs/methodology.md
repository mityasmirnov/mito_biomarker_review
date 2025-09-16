# Methodology Documentation

## Systematic Review Protocol

### Search Strategy

**Databases Searched:**
- PubMed/MEDLINE (1966-2024)
- EMBASE (1974-2024)  
- Cochrane Central Register of Controlled Trials
- Web of Science Core Collection

**Search Terms:**
- Mitochondrial diseases: "mitochondrial disease*", "mitochondrial disorder*", "MELAS", "MERRF", "Leigh syndrome"
- Biomarkers: "biomarker*", "GDF-15", "FGF-21", "lactate", "pyruvate"
- Study types: "diagnostic", "sensitivity", "specificity", "ROC"

### Inclusion/Exclusion Criteria

**Inclusion:**
- Human studies (all ages)
- Circulating biomarkers in biofluids
- Confirmed mitochondrial disease patients
- Appropriate control groups
- Sufficient data for 2x2 tables

**Exclusion:**
- Genetic or imaging biomarkers
- Animal/in vitro studies
- Case reports (<10 patients)
- No control groups

### Quality Assessment

**Framework:** QUADAS-2 (Quality Assessment of Diagnostic Accuracy Studies-2)

**Domains:**
1. Patient Selection
2. Index Test  
3. Reference Standard
4. Flow and Timing

**Risk of Bias Categories:**
- Low risk
- High risk  
- Unclear risk

### Statistical Methods

**Meta-Analysis Model:**
- Bivariate random-effects model
- DerSimonian-Laird method for heterogeneity

**Primary Outcomes:**
- Pooled sensitivity and specificity
- Summary receiver operating characteristic (SROC) curves
- Area under the curve (AUC)
- Diagnostic odds ratios (DOR)

**Heterogeneity Assessment:**
- I² statistic (>50% = substantial heterogeneity)
- Cochran's Q test (p<0.10 = significant heterogeneity)
- Tau² (between-study variance)

**Subgroup Analyses:**
- Age groups (pediatric vs adult)
- Disease conditions (MELAS, MERRF, muscle diseases)
- Analytical methods (ELISA, Simoa)
- Study quality (high vs moderate/low)

**Publication Bias:**
- Funnel plots (visual assessment)
- Egger's test (statistical test)
- Deeks' test (diagnostic accuracy specific)

### Software Used

**Primary Analysis:**
- R version 4.3.0
- Python 3.11+

**R Packages:**
- meta (general meta-analysis)
- mada (diagnostic accuracy meta-analysis)
- metafor (advanced methods)

**Python Packages:**
- pandas, numpy (data manipulation)
- scipy (statistical analysis)
- matplotlib, seaborn (visualization)

### Data Extraction

**Study Characteristics:**
- Author, year, country, design
- Sample sizes, demographics
- Inclusion/exclusion criteria
- Funding sources

**Biomarker Data:**
- Biomarker name and type
- Biomaterial (serum, plasma, CSF)
- Analytical method and platform
- Cutoff values and determination
- Performance metrics (sensitivity, specificity, AUC)
- Raw data (TP, FP, FN, TN when available)

**Quality Indicators:**
- QUADAS-2 domain scores
- Overall risk of bias assessment
- Applicability concerns

### Validation Procedures

**Double Extraction:**
- Two independent reviewers
- Consensus resolution for disagreements
- Third reviewer for unresolved conflicts

**Data Verification:**
- Cross-checking of extracted data
- Calculation verification
- Statistical analysis validation

**Reproducibility:**
- Complete code availability
- Version-controlled analysis
- Documented procedures

