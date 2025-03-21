# **VarCall: Bioinformatics Variant Calling TUI**

VarCall is a text-based user interface (TUI) designed to simplify genomic variant calling workflows. This guide will help you understand how to use VarCall effectively.

## **Getting Started**

### **System Requirements**

- Python 3.7 or higher
- Conda environment management system

### **Installation**

Log file is located at `/tmp/varcall.log`

> **NOTE**
> It is recommended to run `varcall` in a conda environment

To install conda refer to [miniconda](https://docs.anaconda.com/miniconda/)

VarCall requires variant calling tools to run, you can download them by:
```console
conda create -n varcall -y
conda activate varcall
conda install -c bioconda fastqc multiqc bwa samtools bcftools
```

For GATK functionality, additional installation is required:
```console
conda install -c bioconda gatk4
```

## **Interface Navigation**

VarCall features a tabbed interface with the following sections:
- **Home**: Basic operations like downloading data, FastQC, MultiQC, BWA indexing, and alignment
- **Samtools**: SAM/BAM file manipulation tools
- **Bcftools**: Variant calling and filtering operations
- **GATK**: Advanced variant calling and analysis using the GATK toolkit
- **Pipeline**: Automated analysis workflows
- **Help**: This documentation

### **Keyboard Shortcuts**
- `F1`: Show help documentation
- `Q`: Exit application
- `T`: Change theme
- `P`: Debug - print theme data

## **Project Structure**

VarCall expects your project to be organized as follows:

- Project Name (*working dir*)
    - Data
         - Reference Genome
         - Reads
            - Sample_1_1.fastq
            - Sample_1_2.fastq
            - Sample_2_1.fastq
            - Sample_2_2.fastq
        - BED
    - Results
        - FastQC
            - Raw
            - Trimmed
        - MultiQC
            - Alignment
            - Raw
            - Trimmed
        - Samfile
        - Bamfile
        - VCF
        - BCF

## **Available Tools**

### **Home Tab**

#### **Download Dataset (curl)**
Downloads data from a specified URL.
- Required: URL
- Optional: Output file path (auto-generated if not specified)

#### **FastQC**
Quality control tool for high throughput sequence data.
- Required: Input file
- Optional: Output directory

#### **MultiQC**
Aggregates results from bioinformatics analyses into a single report.
- Required: Input directory
- Optional: Output directory

#### **BWA Index**
Indexes reference genome for BWA alignment.
- Required: Reference genome path

#### **BWA mem Alignment**
Aligns reads to reference genome using BWA mem algorithm.
- Required: Reference genome, Read1, Read2
- Optional: Output SAM file path

### **Samtools Tab**

#### **Samtools View**
Converts SAM file to BAM format.
- Required: Input SAM file
- Optional: Output BAM file path

#### **Samtools Stats**
Generates statistics for BAM file.
- Required: Input BAM file
- Optional: Output statistics file path

#### **BAM Sorting**
Sorts BAM file by coordinates.
- Required: Input BAM file, Number of threads
- Optional: Output sorted BAM file path

#### **Samtools Index**
Indexes BAM file for fast random access.
- Required: Input BAM file
- Optional: Output BAI file path

### **Bcftools Tab**

#### **Bcftools Mpileup**
Generates VCF file containing genotype likelihoods for variants.
- Required: Reference genome, Input BAM file
- Optional: Output VCF file path, Additional parameters

#### **Bcftools Call**
Calls variants from VCF file containing genotype likelihoods.
- Required: Input VCF file
- Optional: Output VCF file path, Additional parameters

#### **Bcftools Filter**
Filters variants in VCF file based on specified criteria.
- Required: Input VCF file, Filter expression
- Optional: Output VCF file path

### **GATK Tab**

#### **GATK HaplotypeCaller**
Calls germline SNPs and indels via local assembly of haplotypes.
- Required: Reference genome, Input BAM file
- Optional: Output VCF file path, Additional parameters

#### **GATK BaseRecalibrator**
Generates recalibration table for base quality score recalibration.
- Required: Reference genome, Input BAM file, Known sites, Output table path

#### **GATK ApplyBQSR**
Applies base quality score recalibration.
- Required: Reference genome, Input BAM file, Recalibration table
- Optional: Output BAM file path

#### **GATK VariantFiltration**
Filters variants based on specified criteria.
- Required: Reference genome, Input VCF file, Filter expression, Filter name
- Optional: Output VCF file path

#### **GATK SelectVariants**
Selects a subset of variants from a VCF file.
- Required: Reference genome, Input VCF file, Output VCF file path
- Optional: Variant type, Additional parameters

### **Pipeline Tab**

#### **Mpileup Pipeline**
Executes an end-to-end variant calling pipeline using the mpileup method.
- Required: Reference genome, Read 1, Read 2
- Optional: Additional parameters

## **Output Files**

All output files are automatically saved to the appropriate subdirectory under the `results` directory in your working directory. The file naming convention includes the tool name and timestamp.

## **Troubleshooting**

### **Common Issues**

1. **Missing executable**: Ensure all required tools are installed in your conda environment
2. **Input file not found**: Check file paths and ensure they exist
3. **Permission denied**: Ensure you have write permissions to the output directory

### **Log File**

For detailed troubleshooting, check the log file at:
```
/tmp/varcall.log
```

### **Error Messages**

VarCall provides notifications for:
- Missing required fields
- Command execution errors
- Process completion status

## **Best Practices**

1. **Organize your data** according to the recommended project structure
2. **Index your reference genome** before performing alignments
3. **Check quality with FastQC** before proceeding with variant calling
4. **Sort and index BAM files** before variant calling
5. **Use appropriate filtering criteria** to obtain high-quality variants

## **Required Tools and Their Roles**

- **FastQC**: Quality control for sequencing reads
- **MultiQC**: Aggregation of bioinformatics results
- **BWA**: Read alignment to reference genome
- **Samtools**: SAM/BAM file manipulation
- **Bcftools**: Variant calling and filtering
- **GATK**: Advanced variant analysis toolkit

## **Customization Options**

VarCall is designed to be extensible and customizable to meet your specific needs:

### **Current Customization**
You can customize VarCall by modifying the process dictionary source code in `process_dict.py`. This allows you to:
- Add new bioinformatics tools with custom parameters
- Modify existing tool configurations
- Create specialized pipelines for your specific workflows

Each tool is defined using a `ProcessConfig` object that specifies:
- Command template
- Required and optional input fields
- Description and help messages
- Default extensions for output files

### **Upcoming Features**
- **YAML Configuration**: Future versions will support YAML files for tool and widget configuration without modifying source code
- **Custom Widgets**: Additional UI components will be available to create more interactive and user-friendly interfaces
- **Pipeline Builder**: A visual pipeline builder to connect different tools without writing code

## **Getting Additional Help**

If you encounter issues not covered in this documentation, please check:
- Tool-specific documentation (FastQC, BWA, Samtools, etc.)
- Log file for detailed error messages
- Source code repository for updates and bug fixes
