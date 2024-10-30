import sys
import unittest
import os
import tempfile
import shutil
from gpt_repository_loader import process_repository, get_ignore_list


class TestGPTRepositoryLoader(unittest.TestCase):

    def setUp(self):
        self.test_data_path = os.path.join(os.path.dirname(__file__), 'test_data')
        self.example_repo_path = os.path.join(self.test_data_path, 'example_repo')

    def test_end_to_end(self):
       # Set up the output file and the expected output file paths
       output_file_path = os.path.join(tempfile.mkdtemp(), 'output.txt')
       expected_output_file_path = os.path.join(self.test_data_path, 'expected_output.txt')

       # Create an ignore list for the example repository
       ignore_file_path = os.path.join(self.example_repo_path, ".gptignore")
       gitignore_path = os.path.join(self.example_repo_path, ".gitignore")
       if os.path.exists(ignore_file_path):
           ignore_list = get_ignore_list(ignore_file_path)
       else:
           ignore_list = []
       if os.path.exists(gitignore_path):
           ignore_list += get_ignore_list(gitignore_path)

       # Run the gpt-repository-loader script on the example repository
       with open(output_file_path, 'w') as output_file:
           process_repository(self.example_repo_path, ignore_list, output_file)

       # Compare the output to the expected output
       with open(output_file_path, 'r') as output_file, open(expected_output_file_path, 'r') as expected_output_file:
           expected_output = expected_output_file.read()
           output = output_file.read()
           if sys.platform == "win32":
               expected_output = expected_output.replace("/", "\\")
           self.assertEqual(output, expected_output)

       # Clean up the output file
       shutil.rmtree(os.path.dirname(output_file_path))

    def test_placeholder(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
