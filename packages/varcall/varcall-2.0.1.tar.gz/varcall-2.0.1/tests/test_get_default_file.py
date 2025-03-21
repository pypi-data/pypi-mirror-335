import unittest
from unittest.mock import patch
from datetime import datetime
from pathlib import Path

from varcall.process.process_class import Process, ProcessConfig


class TestProcessDefaultOutput(unittest.TestCase):

    @patch('varcall.process.process_class.datetime')
    @patch('pathlib.Path.cwd')
    def test_get_default_output_file(self, mock_cwd, mock_datetime):
        # Setup mocks
        # Mock current working directory
        mock_cwd.return_value = Path('/mock/working/dir')

        # Mock datetime to return a fixed value
        mock_datetime_obj = datetime(2023, 5, 15, 14, 30, 0)
        mock_datetime.now.return_value = mock_datetime_obj
        mock_datetime.strftime = datetime.strftime

        # Create test configs
        configs = [
            # Test case 1: FastQC with HTML extension
            ProcessConfig(
                name="FastQC",
                command="fastqc {input_file} -o {output_dir}",
                input_fields=["input_file", "output_dir"],
                required_fields=["input_file"],
                default_output_ext=""
            ),
            # Test case 2: BWA MEM with SAM extension
            ProcessConfig(
                name="BWA MEM Alignment",
                command="bwa mem {reference_genome} {read1} {read2} > {output_sam}",
                input_fields=["reference_genome", "read1", "read2", "output_sam"],
                required_fields=["reference_genome", "read1", "output_sam"],
                default_output_ext=".sam"
            ),
            # Test case 3: Bcftools with no extension
            ProcessConfig(
                name="BCF Stats",
                command="bcftools stats {input_vcf} > {output_stats}",
                input_fields=["input_vcf", "output_stats"],
                required_fields=["input_vcf", "output_stats"],
                default_output_ext=".stats"
            )
        ]

        # Expected results
        expected_results = [
            # Expected for FastQC
            Path('/mock/working/dir/fastqc/fastqc_1430_15052023'),
            # Expected for BWA MEM
            Path('/mock/working/dir/bwa/bwa_mem_alignment_1430_15052023.sam'),
            # Expected for BCF Stats
            Path('/mock/working/dir/bcftools/bcf_stats_1430_15052023.stats')
        ]

        # Test each config
        for i, config in enumerate(configs):
            # Create a Process instance with mock app and config
            process = Process(None, config)

            # Get default output file
            default_file = process.get_default_output_file()

            # Assert
            self.assertEqual(
                default_file,
                expected_results[i],
                f"Failed for {config.name}: expected {expected_results[i]}, got {default_file}"
            )

    def test_different_extensions(self):
        """Test that different extensions are properly appended"""
        # Create test config
        config = ProcessConfig(
            name="Test Process",
            command="test {input} {output}",
            input_fields=["input", "output"],
            required_fields=["input"],
            default_output_ext=".txt"
        )

        # Create another config with different extension
        config2 = ProcessConfig(
            name="Test Process",
            command="test {input} {output}",
            input_fields=["input", "output"],
            required_fields=["input"],
            default_output_ext=".vcf"
        )

        # Create Process instances
        process1 = Process(None, config)
        process2 = Process(None, config2)

        # Get default output files
        file1 = process1.get_default_output_file()
        file2 = process2.get_default_output_file()

        # Assert extensions are different
        self.assertTrue(str(file1).endswith(".txt"), f"Expected file1 to end with .txt, got {file1}")
        self.assertTrue(str(file2).endswith(".vcf"), f"Expected file2 to end with .vcf, got {file2}")
        self.assertNotEqual(file1.suffix, file2.suffix)


if __name__ == '__main__':
    unittest.main()
