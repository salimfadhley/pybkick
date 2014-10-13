import logging
from pyboard import Pyboard

def main():
    text = ["import pyb", "pyb.LED(1).on()"]
    
    pb = Pyboard('/dev/ttyACM0')
    
    with pb.raw_repl():
        pb.exec("import pyb")
        pb.exec("pyb.LED(4).on()")
        
if __name__ == '__main__':
    logging.basicConfig()
    main()