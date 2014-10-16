import random
import string
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
        with self.pb.raw_repl():
            result = self.pb.eval(statement)
        self.assertEqual(result, 2)
            
    def test_eval_strings(self):
        statement = "'one' + 'one'"
        with self.pb.raw_repl():
            result = self.pb.eval(statement)
        self.assertEqual(result, 'oneone')
        
    def test_read_file(self):
        filename = 'boot.py'
        with self.pb.raw_repl():
            thetext = self.pb.read_file(filename)
        self.assertTrue(thetext.startswith("# boot.py -- run on boot-up"))
        
    def test_write_file(self):
        filename = "foo.txt"
        sample_size = 12
        sample_text = "".join(random.sample(string.ascii_lowercase, sample_size))
        with self.pb.raw_repl():
            length = self.pb.write_file(file_path=filename, data=sample_text)
            self.assertEqual(sample_size, length)
            self.assertEqual(self.pb.read_file(filename), sample_text)
            
            
            