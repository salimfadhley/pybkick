import logging
import serial
from contextlib import contextmanager
from fdpexpect import fdspawn

@contextmanager
def connect(port=r'/dev/ttyACM0'):
    ser = serial.Serial(port, timeout=1)
    yield fdspawn(ser)
    ser.close()
    
log = logging.getLogger(__name__)

def main():
    text = ["import pyb", "pyb.LED(1).on()"]
    with connect() as ser:
        for line in text:
            ser.expect_exact('>>>', timeout=1)
            ser.send("%s\n" % line)
        
if __name__ == '__main__':
    logging.basicConfig()
    main()