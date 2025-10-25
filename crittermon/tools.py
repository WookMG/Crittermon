import sys
import termios

from crittermon.inputManager import InputManager
from rich.console import Console

def clearTerminal():
    sys.stdout.write("\033[2J\033[3J\033[H")
    sys.stdout.write('\r\033[K')
    sys.stdout.flush()

def flush_stdin():
        #Flush any pending characters in stdin (Linux/macOS)
        termios.tcflush(sys.stdin, termios.TCIFLUSH)

class GlobalVariables:
    def __init__(self):
        self.input_manager = InputManager()
        self.console = Console()

gv = None
        