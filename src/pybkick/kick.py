import os
import logging
from .pyboard import Pyboard
import argparse

log = logging.getLogger(__name__)


# We do not modify these files
NO_MODIFY = ['main.py', 'pybcdc.inf', 'README.txt', 'boot.py']

class MissingSourceCode(RuntimeError):
    """Raised when the source code the user is trying to kick does not exist.
    """


def kick(port, src, dst, entry_point, delay=1):
    if not os.path.exists(src):
        raise MissingSourceCode('%s does not exist' % src)
    pb = Pyboard(port)
    with pb.raw_repl():
        for file_path in os.walk(src):
            log.info("Kicking %s", file_path)
            kick_single_file(pb, file_path, src, dst)
            

def kick_single_file(pb, file_path, src, dst):
    statement = get_kick_statement(file_path, src, dst)
    pb.exec(statement)
    

def get_kick_statement(file_path, src, dst):
    """Generates a python statement that will re-create the specified file in dst on the pyboard
    """
    return "import pyb; pyb.LED(1).on()"


def cmd_line_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', dest='src', help='source path')
    parser.add_argument('--dst', dest='dst', help='remote destination path')
    parser.add_argument('--entry_point', dest='entry_point', help='dotted path to the script that has to be run after kicking')
    parser.add_argument('--port', dest='port', default='/dev/ttyACM0', help='Which serial port should we use')
    return parser


def main():
    parser = cmd_line_parser()
    opts = parser.parse_args()
    
    if not opts.src:
        parser.print_help("--src must be defined.")
        raise SystemExit()
    
    return kick(
         port = opts.port,
         src = opts.src,
         dst = opts.dst,
         entry_point = opts.entry_point
    )
    
    
# def main():
#     text = ["import pyb", "pyb.LED(1).on()"]
#     
#     pb = Pyboard('/dev/ttyACM0')
#     
#     with pb.raw_repl():
#         pb.exec("import pyb")
#         pb.exec("pyb.LED(1).on()")
        
if __name__ == '__main__':
    logging.basicConfig()
    main()