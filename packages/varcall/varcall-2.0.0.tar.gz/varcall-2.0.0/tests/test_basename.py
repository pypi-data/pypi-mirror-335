import unittest
from varcall.modules.exec.common import get_basename_and_ext, get_file_extension

class TestBasename(unittest.TestCase):

    def test_two_out(self):
        commands = get_basename_and_ext("aligned.sam")
        expected = ("aligned", ".sam")
        self.assertEqual(commands, expected)

    def test_two_three(self):
        commands = get_basename_and_ext("aligned.sorted.sam")
        expected = ("aligned.sorted", ".sam")
        self.assertEqual(commands, expected)

    def test_none(self):
        commands = get_basename_and_ext("")
        expected = ("", "")
        self.assertEqual(commands, expected)

class TestExtension(unittest.TestCase):

    def test_two_out(self):
        commands = get_file_extension("aligned.sam")
        expected = ".sam"
        self.assertEqual(commands, expected)

    def test_two_three(self):
        commands = get_file_extension("aligned.sorted.sam")
        expected = ".sam"
        self.assertEqual(commands, expected)

    def test_none(self):
        commands = get_file_extension("")
        expected = ("")
        self.assertEqual(commands, expected)

if __name__ == "__main__":
    unittest.main()
