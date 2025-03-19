import unittest

class TestCICD(unittest.TestCase):
    def test_cicd(self):
        print("This is a dry run test to enable cicd")
        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()