"""
pyboard interface

This module provides the Pyboard class, used to communicate with and
control the pyboard over a serial USB connection.

Example usage:

    import pyboard
    pyb = pyboard.Pyboard('/dev/ttyACM0')
    pyb.enter_raw_repl()
    pyb.exec('pyb.LED(1).on()')
    pyb.exit_raw_repl()

To run a script from the local machine on the board and print out the results:

    import pyboard
    pyboard.execfile('test.py', device='/dev/ttyACM0')

This script can also be run directly.  To execute a local script, use:

    python pyboard.py test.py

"""

import time
import serial
from contextlib import contextmanager
import posixpath

class PyboardError(BaseException):
    pass

class Pyboard:
    def __init__(self, serial_device):
        self.serial_device = serial_device
        self.serial = serial.Serial(serial_device)
        self.in_raw_repl = False
        
    def __repr__(self):
        return "{}(serial_device={})".format(self.__class__.__name__, repr(self.serial_device))

    def close(self):
        self.serial.close()

    def read_until(self, min_num_bytes, ending, timeout=10):
        data = self.serial.read(min_num_bytes)
        timeout_count = 0
        while True:
            if self.serial.inWaiting() > 0:
                data = data + self.serial.read(self.serial.inWaiting())
                time.sleep(0.01)
                timeout_count = 0
            elif data.endswith(ending):
                break
            else:
                timeout_count += 1
                if timeout_count >= 10 * timeout:
                    break
                time.sleep(0.1)
        return data

    def enter_raw_repl(self):
        assert not self.in_raw_repl, "raw_repl is already active!"
        self.serial.write(b'\r\x03') # ctrl-C: interrupt any running program
        self.serial.write(b'\r\x01') # ctrl-A: enter raw REPL
        self.serial.write(b'\x04') # ctrl-D: soft reset
        data = self.read_until(1, b'to exit\r\n>')
        if not data.endswith(b'raw REPL; CTRL-B to exit\r\n>'):
            print(data)
            raise PyboardError('could not enter raw repl')
        self.in_raw_repl = True

    def exit_raw_repl(self):
        assert self.in_raw_repl, "raw_repl was not active!"
        self.serial.write(b'\r\x02') # ctrl-B: enter friendly REPL
        self.in_raw_repl = False
        
    @contextmanager
    def raw_repl(self):
        self.enter_raw_repl()
        yield
        self.exit_raw_repl()

    def eval(self, expression):
        """Execute an expression on the pyboard, returning it's value back to Python.
        Only works for expressions that return reprs that can be evaled
        """
        assert self.in_raw_repl, "raw_repl must be active!"
        eval_expression = '__import__(\'sys\').stdout.write(repr({}))'.format(expression)
        returned_expression = self.exec(eval_expression)
        try:
            return eval(returned_expression)
        except SyntaxError:
            
            import pdb
            pdb.set_trace()
            
            raise RuntimeError("Invalid python returned: %s" % returned_expression)

    def exec(self, command):
        command_bytes = bytes(command, encoding='ascii')
        for i in range(0, len(command_bytes), 32):
            self.serial.write(command_bytes[i:min(i+32, len(command_bytes))])
            time.sleep(0.01)
        self.serial.write(b'\x04')
        data = self.serial.read(2)
        if data != b'OK':
            raise PyboardError('could not exec command')
        data = self.read_until(2, b'\x04>')
        if not data.endswith(b'\x04>'):
            print(data)
            raise PyboardError('timeout waiting for EOF reception')
        if data.startswith(b'Traceback') or data.startswith(b'  File '):
            raise PyboardError(data, command)
        return data[:-2]

    def execfile(self, filename):
        with open(filename) as f:
            pyfile = f.read()
        return self.exec(pyfile)

    def get_time(self):
        t = str(self.eval('pyb.RTC().datetime()'), encoding='ascii')[1:-1].split(', ')
        return int(t[4]) * 3600 + int(t[5]) * 60 + int(t[6])
    
    def ls(self, dir='.'):
        statement = '__import__("os").listdir("{dir}")'.format(dir=dir)
        return self.eval(statement)
        
    def read_file(self, file_path):
        expression = "open({file_path}).read()".format(
            file_path=repr(file_path)
        )
        foo = self.eval(expression)        
        return foo
    
    def write_file(self, file_path, data='', mode='w'):
        """This function intentionally involved using context managers, or more sophisticated
        python syntaxes which might auto-close, so that we can have a single eval-able expression
        that returns the number of bytes written.
        """
        self.exec('tmpfile = open({file_path},{mode})'.format(
            file_path=repr(file_path),
            mode=repr(mode))
        )
        expression = "tmpfile.write({data})".format(
            data=repr(data)
        )
        result = self.eval(expression)
        self.exec('tmpfile.close()')
                
        return result
    
    def mkdir(self, dir_path):
        """Make a directory if it does not exist.
        """
        if not self.file_exists(dir_path):
            statement = 'import os;os.mkdir({dir_path})'.format(dir_path=repr(dir_path))
            self.exec(statement)
    
    def file_exists(self, file_path):
        dir_path, file_name = posixpath.split(file_path)
        try:
            listing = self.ls(dir_path)
        except PyboardError:
            return False
        return file_name in listing
    
    def rm(self, file_path):
        statement = '__import__("os").unlink({file_path})'.format(file_path=repr(file_path))
        return self.exec(statement)
    
    def rmdir(self, dir_path):
        pass
            
        
def execfile(filename, device='/dev/ttyACM0'):
    pyb = Pyboard(device)
    pyb.enter_raw_repl()
    output = pyb.execfile(filename)
    print(str(output, encoding='ascii'), end='')
    pyb.exit_raw_repl()
    pyb.close()

def run_test(device):
    pyb = Pyboard(device)
    pyb.enter_raw_repl()
    print('opened device {}'.format(device))

    pyb.exec('import pyb')  # module pyb no longer imported by default, required for pyboard tests
    print('seconds since boot:', pyb.get_time())

    pyb.exec('def apply(l, f):\r\n for item in l:\r\n  f(item)\r\n')

    pyb.exec('leds=[pyb.LED(l) for l in range(1, 5)]')
    pyb.exec('apply(leds, lambda l:l.off())')

    ## USR switch test

    pyb.exec('switch = pyb.Switch()')

    for i in range(2):
        print("press USR button")
        pyb.exec('while switch(): pyb.delay(10)')
        pyb.exec('while not switch(): pyb.delay(10)')

    print('USR switch passed')

    ## accel test

    if True:
        print("hold level")
        pyb.exec('accel = pyb.Accel()')
        pyb.exec('while abs(accel.x()) > 10 or abs(accel.y()) > 10: pyb.delay(10)')

        print("tilt left")
        pyb.exec('while accel.x() > -10: pyb.delay(10)')
        pyb.exec('leds[0].on()')

        print("tilt forward")
        pyb.exec('while accel.y() < 10: pyb.delay(10)')
        pyb.exec('leds[1].on()')

        print("tilt right")
        pyb.exec('while accel.x() < 10: pyb.delay(10)')
        pyb.exec('leds[2].on()')

        print("tilt backward")
        pyb.exec('while accel.y() > -10: pyb.delay(10)')
        pyb.exec('leds[3].on()')

        print('accel passed')

    print('seconds since boot:', pyb.get_time())

    pyb.exec('apply(leds, lambda l:l.off())')

    pyb.exit_raw_repl()
    pyb.close()

def main():
    import argparse
    cmd_parser = argparse.ArgumentParser(description='Run scripts on the pyboard.')
    cmd_parser.add_argument('--device', default='/dev/ttyACM0', help='the serial device of the pyboard')
    cmd_parser.add_argument('--test', action='store_true', help='run a small test suite on the pyboard')
    cmd_parser.add_argument('files', nargs='*', help='input files')
    args = cmd_parser.parse_args()

    if args.test:
        run_test(device=args.device)

    for file in args.files:
        execfile(file, device=args.device)

if __name__ == "__main__":
    main()