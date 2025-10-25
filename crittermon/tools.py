import sys
import termios

from crittermon.inputManager import InputManager
from crittermon.player import Player
from rich.console import Console

TYPE_COLORS = {
    "Bug": "chartreuse3",
    "Dark": "grey19",
    "Dragon": "royal_blue1",
    "Electric": "yellow1",
    "Fairy": "pink1",
    "Fighting": "indian_red",
    "Fire": "orange1",
    "Flying": "sky_blue1",
    "Ghost": "dark_violet",
    "Grass": "green3",
    "Ice": "light_cyan1",
    "Normal": "grey70",
    "Poison": "medium_purple3",
    "Psychic": "deep_pink1",
    "Rock": "dark_goldenrod",
    "Steel": "light_steel_blue3",
    "Water": "deep_sky_blue1",
}


def clearTerminal():
    sys.stdout.write("\033[2J\033[3J\033[H")
    sys.stdout.write('\r\033[K')
    sys.stdout.flush()

def flush_stdin():
        #Flush any pending characters in stdin (Linux/macOS)
        termios.tcflush(sys.stdin, termios.TCIFLUSH)

def typeColour(type: str) -> str:
        ''' Returns a rich colour code to colour types in drawCritterSummary '''
        return TYPE_COLORS.get(type.lower(), "bright_white")

class GlobalVariables:
    def __init__(self, player_pos, player_name):
        self.input_manager = InputManager()
        self.player = Player(player_pos, player_name)
        self.console = Console()
        

gv = None
        