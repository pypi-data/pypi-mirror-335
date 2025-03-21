# VarCall

![License](https://img.shields.io/badge/license-MIT-green)
[![PyPI - Version](https://img.shields.io/pypi/v/varcall.svg)](https://pypi.org/project/varcall)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/varcall.svg)](https://pypi.org/project/varcall)

A modern, user-friendly Text-based User Interface (TUI) for genomic variant calling workflows. VarCall simplifies bioinformatics analysis by providing an intuitive interface to popular variant calling tools, making genomic analysis accessible to researchers without extensive command-line experience.

## 📋 Table of Contents

- [🌟 Features](#-features)
- [🔧 Installation](#-installation)
- [🚀 Usage](#-usage)
- [📊 Screenshots](#-screenshots)
- [🔧 Customization](#-customization)
- [🤝 Contributing](#-contributing)
- [📜 License](#-license)

## 🌟 Features

- **Intuitive TUI Interface**: Navigate through genomic analysis workflows with ease
- **Multi-tool Integration**: Access FastQC, MultiQC, BWA, Samtools, Bcftools, and GATK from a single interface
- **Workflow Automation**: Execute complex pipelines with simple inputs
- **Real-time Notifications**: Get immediate feedback on process status
- **Organized Output**: Results automatically saved in a structured directory hierarchy
- **Customizable**: Extend functionality by adding new tools or modifying existing ones
- **Comprehensive Logging**: Detailed logs for troubleshooting and tracking analysis history

## 🔧 Installation

> [!NOTE]
> v2.0.0 is available for use. <br>
> v2.0.0 can create widgets in runtime, using config dictionaries, making it maintainable and customizable <br>
> YAML file configuration coming soon!!!

### Prerequisites

VarCall requires Python 3.7+ and works best in a conda environment with bioinformatics tools pre-installed.

1. **Install Miniconda** (if not already installed):
   Visit [Miniconda](https://docs.anaconda.com/miniconda/) for installation instructions.

2. **Create a conda environment with required tools**:
   ```console
   conda create -n varcall -y
   conda activate varcall
   conda install -c bioconda fastqc multiqc bwa samtools bcftools
   ```

3. **For GATK functionality** (optional):
   ```console
   conda install -c bioconda gatk4
   ```

### Install VarCall

```console
pip install varcall
```

## 🚀 Usage

### Starting VarCall

After installation, simply run:

```console
varcall
```

### Keyboard Navigation

- `Tab`: Navigate between tabs
- `Arrow Keys`: Navigate within a tab
- `Enter`: Select/Execute
- `F1`: Access Help
- `Q`: Quit application
- `T`: Toggle theme

### Basic Workflow

1. **Prepare your data** following the recommended project structure
2. **Quality control** your sequence data using FastQC and MultiQC
3. **Index** your reference genome with BWA Index
4. **Align** your reads using BWA mem
5. **Process alignments** with Samtools (convert, sort, index)
6. **Call variants** using Bcftools or GATK
7. **Filter and analyze** your variants

### Project Structure

VarCall works best with the following project structure:

```
Project_Directory/
├── Data/
│   ├── Reference_Genome/
│   ├── Reads/
│   │   ├── Sample_1_1.fastq
│   │   ├── Sample_1_2.fastq
│   │   └── ...
│   └── BED/
└── Results/
    ├── FastQC/
    ├── MultiQC/
    ├── Samfile/
    ├── Bamfile/
    ├── VCF/
    └── BCF/
```

## 📊 Screenshots

### Home Tab
![Home tab image](./doc/images/Hometab-image.jpg?raw=true "Home tab")

### Samtools Tab
![Samtools tab image](./doc/images/Samtoolstab-image.jpg?raw=true "Samtools tab")

### Bcftools Tab
![Bcftools tab image](./doc/images/Bcftoolstab-image.jpg?raw=true "Bcftools tab")

### GATK Tab
![GATK tab image](./doc/images/gatktab-image.jpg?raw=true "GATK tab")

### Pipeline Tab
![Pipeline tab image](./doc/images/Pipelinetab-image.jpg?raw=true "Pipeline")

### Help Tab
![Help tab image](./doc/images/Helptab-image.jpg?raw=true "Help tab")

## 🔧 Customization

VarCall is designed to be extensible and adaptable to various bioinformatics workflows:

### Current Customization

You can customize VarCall by modifying the process dictionary source code in `process_dict.py`. This allows you to:

- Add new bioinformatics tools with custom parameters
- Modify existing tool configurations
- Create specialized pipelines for your specific workflows

Each tool is defined using a `ProcessConfig` object that specifies command templates, required fields, descriptions, and more.

### Upcoming Features

- **YAML Configuration**: Define tools and workflows through YAML files without modifying source code
- **Custom Widgets**: Additional UI components for enhanced user experience
- **Pipeline Builder**: Visual interface for connecting tools into complex workflows

## 🤝 Contributing

Contributions to VarCall are welcome and appreciated! Here are ways you can contribute:

- **Report Bugs**: Submit issues for any bugs you encounter
- **Feature Requests**: Suggest new features or improvements
- **Code Contributions**: Submit pull requests with bug fixes or new features
- **Documentation**: Help improve documentation or add tutorials
- **Tool Integration**: Add configurations for additional bioinformatics tools

Please follow standard GitHub workflow for contributions:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📜 License

`varcall` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
