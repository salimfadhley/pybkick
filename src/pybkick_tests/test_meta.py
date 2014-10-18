import unittest

class TestMeta(unittest.TestCase):
    
    def test_version(self):
        from pybkick import __version__ as version
        parts = version.split('.')
        self.assertEqual(len(parts), 3)
        for part in parts:
            int(part)