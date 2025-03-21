import unittest
from varcall.modules.exec.common import Command

class TestCommand(unittest.TestCase):
    def test_download_cmd(self):
        cmd = Command(name="download", workingDir = "trial", first_path="https://example.com/file.txt", second_path="file.txt")
        commands = cmd.get_command()
        expected = "curl -L https://example.com/file.txt -o file.txt"
        self.assertEqual(commands, expected)

    def test_fastqc_cmd(self):
        cmd = Command(name="fastqc", workingDir = "trial", first_path="sample.fastq", second_path="results/")
        commands = cmd.get_command()
        expected = "fastqc sample.fastq -o results/"
        self.assertEqual(commands, expected)

    def test_bwa_mem_cmd(self):
        cmd = Command(
            name="bwa_mem",
            workingDir = "trial",
            first_path="ref_genome.fa",
            second_path="8",
            third_input="reads_1.fastq",
            fourth_input="reads_2.fastq",
            fifth_input="aligned.sam"
        )
        commands = cmd.get_command()
        expected = (
            "bwa mem -t 8 ref_genome.fa reads_1.fastq reads_2.fastq -o aligned.sam"
        )
        self.assertEqual(commands, expected)

    def test_samtools_view_cmd(self):
        cmd = Command(
            name="samtools_view",
            workingDir = "trial",
            first_path="input.bam",
            second_path="output.sam",
            third_input="chr1:1000-2000"  # Region to view
        )
        commands = cmd.get_command()
        expected = "samtools view -b -h input.bam -o output.sam region=chr1:1000-2000"
        self.assertEqual(commands, expected)

    def test_bcf_filter_cmd(self):
        cmd = Command(
            name="bcf_filter",
            workingDir = "trial",
            first_path="variants.bcf",
            second_path="filtered.bcf",
            third_input="QUAL<20"  # Filter expression
        )
        commands = cmd.get_command()
        expected = "bcftools filter -s LOWQUAL -e 'QUAL<20' variants.bcf -o filtered.bcf"
        self.assertEqual(commands, expected)

    def test_bcf_stats_cmd(self):
        cmd = Command(name="bcf_stats", workingDir = "trial", first_path="variants.bcf", second_path="stats.txt")
        commands = cmd.get_command()
        expected = "bcftools stats variants.bcf > stats.txt"
        self.assertEqual(commands, expected)

    def test_error(self):
        cmd = Command(name="no_cmd", workingDir = "trial", first_path="no_input", second_path="no_output")
        commands = cmd.get_command()
        expected = "Error: 'no_cmd' command not found."
        self.assertEqual(commands, expected)

if __name__ == "__main__":
    unittest.main()
