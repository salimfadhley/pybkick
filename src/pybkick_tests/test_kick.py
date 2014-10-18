import os
import sys
import mock
import unittest
import pkg_resources
from pybkick.kick import kick, main as kick_main, MissingSourceCode
from pybkick.pyboard import Pyboard

class TestKick(unittest.TestCase):
    """Test that we can kick code over to the PyBoard
    """
    
    def testBasicKick(self):
        test_data_path = pkg_resources.resource_filename(__name__, 'test_data')
        
        kick(
             port='/dev/ttyACM0',
             src=test_data_path,
             entry_point=None
        )
        
    def testKickFromCommandLine(self):
        test_data_path = pkg_resources.resource_filename(__name__, 'test_data')
        
        fake_argv = [sys.argv[0], '--src=%s' % test_data_path, '--dst=tmp']
        with mock.patch('sys.argv', fake_argv):
            fake_kick = mock.Mock()
            with mock.patch('pybkick.kick', fake_kick):
                kick_main()
                fake_kick.assert_called_once()
                
    def testKickMissingDirectory(self):
        missing_test_data_path = os.path.join(pkg_resources.resource_filename(__name__, 'test_data'), 'missing')
        
        with self.assertRaises(MissingSourceCode):
            kick(
                 port='/dev/ttyACM0',
                 src=missing_test_data_path,
                 dst='tmp',
                 entry_point=None
            )
            
    def testKickTestData(self):
        test_dir = pkg_resources.resource_filename(__name__, 'test_data')
        port = '/dev/ttyACM0'
        kick(port=port,
             src=test_dir
        )
        
        pb = Pyboard(port)
        with pb.raw_repl():
            for filename in ['a.txt', 'b.txt']:
                self.assertTrue(pb.file_exists(filename))
                pb.rm(filename)
                self.assertFalse(pb.file_exists(filename))


            
                
        
       
        