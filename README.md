**🏷️ Title: Genomic Variant Annotation using Ensembl VEP and Nextflow**

**Name:** Jahnavi Iyer

**Assignment:** CloverTex Genomic Annotation Project (Assignment 1 & 2)

**Environment:** Ubuntu (via WSL2) + Nextflow DSL2 + Docker + Jupyter Notebook

**📘 Overview**
This project implements a reproducible genomic variant annotation pipeline using Ensembl VEP (Variant Effect Predictor).
Two assignments were completed:

**Assignment 1:** Manual annotation and variant analysis using Ensembl VEP and Jupyter Notebook.

**Assignment 2:** Automated large-scale variant annotation using a containerized Nextflow DSL2 pipeline.

**🧩 Folder Structure**

<img width="871" height="528" alt="image" src="https://github.com/user-attachments/assets/1a6c374e-e084-4941-919f-e0d853b51e09" />


**⚙️ Environment Setup**

Tools Installed
 - Ubuntu 24.04 (WSL2)
 - Docker
 - Nextflow (version 25.04.7)
 - Python 3.12 + JupyterLab
 - Pandas, Matplotlib

**🧠 Assignment 1 — Manual VEP Annotation & Analysis**
**Steps:**

1. Ran VEP online for 50 variants each from test1_data.vcf and test2_data.vcf using Docker.
   
2. Generated annotated VCFs:
 - test1_first50_vep_output.vcf
 - test2_first50_vep_output.vcf
   
3. Opened JupyterLab and analyzed:
 - Total variant counts
 - Unique gene counts
 - Disease/trait-related variants
 - Pathogenic and likely pathogenic variants
 - SIFT & PolyPhen deleterious predictions

4. Saved outputs in results/ folder:
 - Annotated CSVs
 - Summary logs
 - Validation reports
 - Visual plots (per-chromosome variant barplot)

**Outcome:**
Generated clear and reproducible annotations with validation summaries.

**⚡ Assignment 2 — Automated VEP Annotation using Nextflow**
**Steps:**

1. Created samples.csv manifest file listing sample names, file paths, gender, and assembly.

2. Built main.nf Nextflow DSL2 pipeline:
 - Reads manifest file
 - Runs VEP annotation inside container (ensemblorg/ensembl-vep:latest)
 - Publishes annotated VCFs to results/

3. Configured nextflow.config for Docker executor, memory, CPUs, and report generation.

4. Executed: nextflow run main.nf -c nextflow.config --input samples.csv --outdir results

5. Generated:
 - report.html (resource summary)
 - timeline.html (execution flow)
 - Annotated VCFs in results/

**Outcome:**
Pipeline successfully annotated multiple samples in parallel and produced reproducible outputs.

**🧾 Post-run Validation**

Validation performed using Python/Jupyter to confirm:
 - Annotated files contain ##INFO=<ID=CSQ...> header
 - Each variant line includes CSQ= annotation
 - Output counts match expected inputs

**Generated:**
✅ validation_report_nextflow.csv

**🔍 Results Summary**

<img width="874" height="124" alt="image" src="https://github.com/user-attachments/assets/b2ada7e9-7537-4d0c-b478-414db9831a9e" />

**📊 Reports Included**

Nextflow Execution Report: report.html

Timeline: timeline.html

Validation Reports:
 - validation_report_first50.csv
 - validation_report_nextflow.csv
