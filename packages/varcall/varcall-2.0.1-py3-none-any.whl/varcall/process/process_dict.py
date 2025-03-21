from varcall.process.process_class import ProcessConfig

# dictionary to track running processes
running_processes = {}

# configure bioinformatics tools
HOME_PROCESSES = {
    # data download tool
    "curl": ProcessConfig(
        name="curl",
        display_name="Download Dataset",
        command="curl -l {url} -o {output_file}",
        input_fields=["url", "output_file"],
        required_fields=["url"],
        description="fastqcs the files in the workingdir/data/reads directory [u]if the input field is left empty[/u]",
        success_message="dataset downloaded successfully",
        error_message="dataset download failed",
    ),
    "fastqc": ProcessConfig(
        name="fastqc",
        display_name="FastQC",
        command="fastqc {input_file} -o {output_dir}",
        input_fields=["input_file", "output_dir"],
        required_fields=["input_file"],
        description="quality control tool for high throughput sequence data",
        success_message="fastqc analysis completed successfully",
        error_message="fastqc analysis failed",
    ),
    "multiqc": ProcessConfig(
        name="multiqc",
        display_name="MultiQC",
        command="multiqc {input_dir} -o {output_dir}",
        input_fields=["input_dir", "output_dir"],
        required_fields=["input_dir"],
        description="aggregate results from bioinformatics analyses into a single report",
        success_message="multiqc report generated successfully",
        error_message="multiqc report generation failed",
    ),
    "bwa_index": ProcessConfig(
        name="bwa_index",
        display_name="BWA Index",
        command="bwa index {reference_genome}",
        input_fields=["reference_genome"],
        required_fields=["reference_genome"],
        description="index reference genome for bwa alignment",
        success_message="reference genome indexed successfully",
        error_message="reference genome indexing failed",
    ),
    "bwa_mem": ProcessConfig(
        name="bwa_mem",
        display_name="BWA mem Alignment",
        command="bwa mem {reference_genome} {read1} {read2} > {output_sam}",
        input_fields=["reference_genome", "read1", "read2", "output_sam"],
        required_fields=["reference_genome", "read1", "read2"],
        description="align reads to reference genome using bwa mem algorithm",
        success_message="read alignment completed successfully",
        error_message="read alignment failed",
        default_output_ext=".sam",
    ),
}
SAMTOOLS_PROCESSES = {
    "samtools_view": ProcessConfig(
        name="samtools_view",
        command="samtools view -bs {input_sam} > {output_bam}",
        input_fields=["input_sam", "output_bam"],
        required_fields=["input_sam"],
        description="convert sam file to bam format",
        success_message="sam to bam conversion completed successfully",
        error_message="sam to bam conversion failed",
        default_output_ext=".bam",
    ),
    "samtools_stats": ProcessConfig(
        name="samtools_stats",
        command="samtools stats -in {input_bam} > {output_stats}",
        input_fields=["input_bam"],
        required_fields=["input_bam"],
        description="generate statistics for bam file",
        success_message="bam statistics generated successfully",
        error_message="bam statistics generation failed",
        default_output_ext=".txt",
    ),
    "samtools_sort": ProcessConfig(
        name="bam_sorting",
        command="samtools sort {input_bam} -o {output_sorted_bam}",
        input_fields=["input_bam", "output_sorted_bam", "threads"],
        required_fields=["input_bam", "threads"],
        description="sort bam file by coordinates",
        success_message="bam file sorted successfully",
        error_message="bam sorting failed",
        default_output_ext=".bam",
    ),
    "samtools_index": ProcessConfig(
        name="samtools_index",
        command="samtools index {input_bam} {output_bai}",
        input_fields=["input_bam", "output_bai"],
        required_fields=["input_bam"],
        description="index bam file for fast random access",
        success_message="bam file indexed successfully",
        error_message="bam indexing failed",
    ),
}

BCFTOOLS_PROCESS = {
    # bcftools operations
    "bcftools_mpileup": ProcessConfig(
        name="bcftools_mpileup",
        command="bcftools mpileup -f {reference_genome} {input_bam} -o {output_vcf}",
        input_fields=[
            "reference_genome",
            "input_bam",
            "output_vcf",
            "additional_params",
        ],
        required_fields=["reference_genome", "input_bam"],
        description="generate vcf file containing genotype likelihoods for variants",
        success_message="variant calling (mpileup) completed successfully",
        error_message="variant calling (mpileup) failed",
        default_output_ext=".vcf",
    ),
    "bcftools_call": ProcessConfig(
        name="bcftools_call",
        command="bcftools call -m -v {input_vcf} -o {output_vcf}",
        input_fields=["input_vcf", "output_vcf", "additional_params"],
        required_fields=["input_vcf"],
        description="call variants from vcf file containing genotype likelihoods",
        success_message="variant calling completed successfully",
        error_message="variant calling failed",
        default_output_ext=".vcf",
    ),
    "bcftools_filter": ProcessConfig(
        name="bcftools_filter",
        command="bcftools filter -i'{filter_expression}' {input_vcf} -o {output_vcf}",
        input_fields=["input_vcf", "output_vcf", "filter_expression"],
        required_fields=["input_vcf", "filter_expression"],
        description="filter variants in vcf file based on specified criteria",
        success_message="variant filtering completed successfully",
        error_message="variant filtering failed",
        default_output_ext=".vcf",
    ),
}

GATK_PROCESS = {
    # gatk tools
    "GATK_haplotypecaller": ProcessConfig(
        name="GATK_haplotypecaller",
        command="gatk haplotypecaller -r {reference_genome} -i {input_bam} -o {output_vcf}",
        input_fields=[
            "reference_genome",
            "input_bam",
            "output_vcf",
            "additional_params",
        ],
        required_fields=["reference_genome", "input_bam"],
        description="call germline snps and indels via local assembly of haplotypes",
        success_message="variant calling with haplotypecaller completed successfully",
        error_message="variant calling with haplotypecaller failed",
        default_output_ext=".vcf",
    ),
    "GATK_baserecalibrator": ProcessConfig(
        name="GATK_baserecalibrator",
        command="gatk baserecalibrator -r {reference_genome} -i {input_bam} --known-sites {known_sites} -o {output_table}",
        input_fields=["reference_genome", "input_bam", "known_sites", "output_table"],
        required_fields=[
            "reference_genome",
            "input_bam",
            "known_sites",
            "output_table",
        ],
        description="generate recalibration table for base quality score recalibration",
        success_message="base recalibration table generated successfully",
        error_message="base recalibration table generation failed",
    ),
    "GATK_applybqsr": ProcessConfig(
        name="GATK_applybqsr",
        command="gatk applybqsr -r {reference_genome} -i {input_bam} --bqsr-recal-file {recalibration_table} -o {output_bam}",
        input_fields=[
            "reference_genome",
            "input_bam",
            "recalibration_table",
            "output_bam",
        ],
        required_fields=[
            "reference_genome",
            "input_bam",
            "recalibration_table",
        ],
        description="apply base quality score recalibration",
        success_message="base quality score recalibration applied successfully",
        error_message="base quality score recalibration failed",
        default_output_ext=".bam",
    ),
    "GATK_variantfiltration": ProcessConfig(
        name="GATK_variantfiltration",
        command="gatk variantfiltration -r {reference_genome} -v {input_vcf} --filter-expression '{filter_expression}' --filter-name '{filter_name}' -o {output_vcf}",
        input_fields=[
            "reference_genome",
            "input_vcf",
            "output_vcf",
            "filter_expression",
            "filter_name",
        ],
        required_fields=[
            "reference_genome",
            "input_vcf",
            "filter_expression",
            "filter_name",
        ],
        description="filter variants based on specified criteria",
        success_message="variant filtration completed successfully",
        error_message="variant filtration failed",
        default_output_ext=".vcf",
    ),
    "GATK_selectvariants": ProcessConfig(
        name="GATK_selectvariants",
        command="gatk selectvariants -r {reference_genome} -v {input_vcf} --select-type-to-include {variant_type} -o {output_vcf}",
        input_fields=[
            "reference_genome",
            "input_vcf",
            "variant_type",
            "additional_params",
        ],
        required_fields=["reference_genome", "input_vcf", "output_vcf"],
        description="select a subset of variants from a vcf file",
        success_message="variant selection completed successfully",
        error_message="variant selection failed",
        default_output_ext=".vcf",
    ),
}

PIPLELINES = {
    "mpliup_pipeline": ProcessConfig(
        name = "mpliup_pipeline",
        display_name = "Mpliup Pipeline (mock)",
        command="echo {read_1} > {read_2}",
        input_fields=[
            "reference_genome",
            "read_1",
            "read_2",
            "additional_params",
        ],
        required_fields=["reference_genome", "read_1", "read_2" ],
        description="mpileup pipeline",
        success_message="mpileup pipeline completed successfully",
        error_message="an error occured during the execution of the mpileup pipeline",
        default_output_ext=".vcf",
    )
}


master_config: dict[str, dict[str, ProcessConfig]] = {
    "home": HOME_PROCESSES,
    "samtools": SAMTOOLS_PROCESSES,
    "bcftools": BCFTOOLS_PROCESS,
    "gatk": GATK_PROCESS,
    "pipeline": PIPLELINES,
}
