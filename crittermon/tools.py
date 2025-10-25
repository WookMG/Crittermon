import sys
import termios

from crittermon.inputManager import InputManager
from crittermon.player import Player
from rich.console import Console

def clearTerminal():
    sys.stdout.write("\033[2J\033[3J\033[H")
    sys.stdout.write('\r\033[K')
    sys.stdout.flush()

def flush_stdin():
        #Flush any pending characters in stdin (Linux/macOS)
        termios.tcflush(sys.stdin, termios.TCIFLUSH)

class GlobalVariables:
    def __init__(self, player_pos, player_name):
        self.input_manager = InputManager()
        self.player = Player(player_pos, player_name)
        self.console = Console()
        

gv = None
        