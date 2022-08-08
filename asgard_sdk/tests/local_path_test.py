import unittest, os

from asgard_sdk.models.file import LocalPath

class LocalPathTest(unittest.TestCase):

    def setUp(self) -> None:
        self.path = LocalPath("~/Desktop/test.txt")
    
    def test_validation(self):
        self.assertEqual(self.path.file_name, "test.txt")
    
    def test_type(self):
        self.assertEqual(self.path.file_type, "document")

    def test_location(self):
        self.assertEqual(self.path.file_location, "{}/Desktop".format(os.getenv("HOME")))

if __name__ == "__main__":
    unittest.main()