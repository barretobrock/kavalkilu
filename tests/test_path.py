import unittest

from kavalkilu import Path


class TestPath(unittest.TestCase):
    def setUp(self) -> None:
        self.path = Path()

    def test_paths(self):
        files_only = self.path.get_files_in_dir(self.path.download_dir, full_paths=False)
        self.assertTrue(all(['/' not in x for x in files_only]))
        full_file_path = self.path.get_files_in_dir(self.path.download_dir, full_paths=True)
        self.assertTrue(all(['/' in x for x in full_file_path]))

    def test_recursive(self):
        top_level = self.path.get_files_in_dir(self.path.download_dir, recursive=False)
        all_level = self.path.get_files_in_dir(self.path.download_dir, recursive=True)
        self.assertTrue(len(top_level) <= len(all_level))


if __name__ == '__main__':
    unittest.main()
