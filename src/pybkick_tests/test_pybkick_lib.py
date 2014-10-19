import unittest
import pybkick
from pybkick.pyboard import Pyboard

class testPybkickLib(unittest.TestCase):
    
    def setUp(self):
        self.pb = Pyboard('/dev/ttyACM0')
    
    def tearDpwm(self):
        self.pb.close()
    
    def test_lib_exists(self):
        with self.pb.pybkick_lib():
            self.assertTrue(self.pb.file_exists('pybkick_lib.py'))
        with self.pb.raw_repl():
            self.assertFalse(self.pb.file_exists('pybkick_lib.py'))
            
    def test_activate(self):
        self.assertFalse(self.pb.pybkick_lib_active)
        with self.pb.pybkick_lib():
            self.assertTrue(self.pb.pybkick_lib_active)
        self.assertFalse(self.pb.pybkick_lib_active)
        
    def test_get_version(self):
        with self.pb.pybkick_lib():
            self.assertEqual(self.pb.eval('__import__("pybkick_lib").version()'), pybkick.__version__)
        