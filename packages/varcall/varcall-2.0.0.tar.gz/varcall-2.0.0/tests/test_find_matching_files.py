import unittest
from unittest.mock import patch
from varcall.modules.exec.common import find_matching_files

class TestFindMatchingFiles(unittest.TestCase):

    @patch("glob.glob")
    def test_find_matching_files_simple_pattern(self, mock_glob):
        # Mocking glob to return files matching a simple pattern
        mock_glob.return_value = ["file1.txt", "file2.txt"]
        
        result = find_matching_files("*.txt")
        self.assertEqual(result, "file1.txt file2.txt")

        mock_glob.assert_called_once_with("*.txt")

    @patch("glob.glob")
    def test_find_matching_files_no_match(self, mock_glob):
        # Mocking no matching files
        mock_glob.return_value = []

        result = find_matching_files("*.csv")
        self.assertEqual(result, "")

        mock_glob.assert_called_once_with("*.csv")

    @patch("glob.glob")
    def test_find_matching_files_nested_directories(self, mock_glob):
        # Mocking files in nested directories
        mock_glob.return_value = [
            "./trial/a/file1.txt", 
            "./trial/b/file2.txt"
        ]

        result = find_matching_files("./trial/*/file*.txt")
        self.assertEqual(result, "./trial/a/file1.txt ./trial/b/file2.txt")

        mock_glob.assert_called_once_with("./trial/*/file*.txt")

    @patch("glob.glob")
    def test_find_matching_files_partial_file_name(self, mock_glob):
        # Mocking files matching partial names
        mock_glob.return_value = [
            "./trial/reads/sample1.fastq", 
            "./trial/reads/sample1.log"
        ]

        result = find_matching_files("./trial/reads/sample1*")
        self.assertEqual(result, "./trial/reads/sample1.fastq ./trial/reads/sample1.log")

        mock_glob.assert_called_once_with("./trial/reads/sample1*")


    @patch("glob.glob")
    def test_find_matching_files_empty_string(self, mock_glob):
        # Mocking no pattern given (empty string)
        mock_glob.return_value = []

        result = find_matching_files("")
        self.assertEqual(result, "")

        mock_glob.assert_called_once_with("")

if __name__ == "__main__":
    unittest.main()
