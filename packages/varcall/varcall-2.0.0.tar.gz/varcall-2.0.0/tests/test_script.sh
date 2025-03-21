#!/usr/bin/bash

WKDIR="/home/vs/github/varcall/python/varcall/tests/test_trial"

mkdir -p $WKDIR $WKDIR/results $WKDIR/data $WKDIR/data/reads $WKDIR/data/reference/ $WKDIR/results/fastqc $WKDIR/results/multiqc $WKDIR/results/multiqc/sam $WKDIR/results/sam $WKDIR/results/bam $WKDIR/results/vcf $WKDIR/results/bcf && \

fastqc $WKDIR/data/reads/* -o $WKDIR/results/fastqc/ && \
multiqc $WKDIR/results/fastqc/ -o $WKDIR/results/multiqc/ && \

bwa index $WKDIR/data/reference/ecoli.fasta && \
bwa mem -t 8 $WKDIR/data/reference/ecoli.fasta $WKDIR/data/reads/s1_1.fastq $WKDIR/data/reads/s1_2.fastq -o $WKDIR/results/sam/aligned.sam && \
samtools flagstats $WKDIR/results/sam/aligned.sam > $WKDIR/results/sam/aligned.sam.flagstats && \
multiqc $WKDIR/results/sam/aligned.sam.flagstats -o $WKDIR/results/multiqc/sam/ && \

samtools view -bS -o $WKDIR/results/bam/aligned.bam $WKDIR/results/sam/aligned.sam && \
samtools sort -o $WKDIR/results/bam/aligned.sorted.bam $WKDIR/results/bam/aligned.bam && \
samtools index $WKDIR/results/bam/aligned.sorted.bam && \

bcftools mpileup -f $WKDIR/data/reference/ecoli.fasta $WKDIR/results/bam/aligned.sorted.bam | bcftools call -mv -Oz -o $WKDIR/results/vcf/aligned.vcf && \
bcftools filter  -s LOWQUAL -e 'QUAL>20' $WKDIR/results/vcf/aligned.vcf -o $WKDIR/results/vcf/aligned.filtered.vcf && \
bcftools norm $WKDIR/results/vcf/aligned.filtered.vcf -o $WKDIR/results/vcf/aligned.filtered.norm.vcf && \
bcftools stats $WKDIR/results/vcf/aligned.filtered.vcf > $WKDIR/results/vcf/aligned.filtered.vcf.stats

notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "test files generated"
