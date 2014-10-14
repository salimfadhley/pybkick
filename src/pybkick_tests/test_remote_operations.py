import unittest
from pybkick.pyboard import Pyboard

class TestRemoteOperations(unittest.TestCase):
    
    def setUp(self):
        self.pb = Pyboard('/dev/ttyACM0')
    
    def tearDpwm(self):
        self.pb.close()
    
    def test_ls(self):
        result = self.pb.ls('.')
        self.assertIsInstance(result, list)
        self.assertTrue('boot.py' in result)
        
    def test_eval_ints(self):
        statement = "1+1"
        result = self.pb.eval(statement)
        self.assertEqual(result, 2)
            
    def test_eval_strings(self):
        statement = "'one' + 'one'"
        result = self.pb.eval(statement)
        self.assertEqual(result, 'oneone')
            