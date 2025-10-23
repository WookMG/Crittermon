import sys
import time
from pynput import keyboard
from rich.markup import escape

from summary import Summary

class World:

    ascii_world = [["#","#","#","#","#","#","#","#","#","#","#","#","#","#","#","#","#","#","#","#"],
                   ["#","%","%","%","%","%","\\","\\","\\","%","%","%","%","%","%","%","%","%","\\","#"],
                   ["#","%","%","%","%","\\","\\","\\","\\","\\","%","%","%","%","%","%","%","%","\\","#"],
                   ["#","%","%","%","~","~","~","\\","\\","\\","%","%","%","%","%","%","%","%","\\","#"],
                   ["#","%","%","~","~","~","~","~","\\","\\","\\","%","%","%","%","%","%","%","\\","#"],
                   ["#","%","\\","~","~","~","~","~","\\","\\","\\","%","%","%","%","%","%","\\","\\","#"],
                   ["#","\\","\\","~","~","~","~","~","\\","\\","\\","\\","%","%","%","%","\\","\\","\\","#"],
                   ["#","\\","\\","\\","~","~","~","\\","\\","\\","\\","\\","\\","\\","\\","\\","\\","\\","\\","#"],
                   ["#","\\","\\","\\","\\","\\","\\","\\","\\","\\","\\","\\","\\","\\","\\","\\","\\","\\","\\","#"],
                   ["#","\\","\\","%","%","\\","\\","\\","\\","\\","\\","\\","\\","\\","%","%","%","\\","\\","#"],
                   ["#","\\","%","%","%","%","\\","\\","\\","\\","\\","\\","\\","%","%","%","%","%","\\","#"],
                   ["#","\\","%","%","%","%","\\","\\","\\","\\","\\","\\","\\","%","%","%","%","%","\\","#"],
                   ["#","\\","\\","%","%","%","\\","\\","\\","\\","\\","\\","\\","%","%","%","%","%","\\","#"],
                   ["#","\\","\\","\\","\\","\\","\\","\\","\\","\\","\\","\\","\\","\\","%","%","%","\\","\\","#"],
                   ["#","\\","\\","\\","\\","%","%","%","%","\\","\\","\\","\\","\\","\\","\\","\\","\\","\\","#"],
                   ["#","\\","\\","%","%","%","%","%","%","%","\\","\\","\\","\\","\\","\\","\\","%","%","#"],
                   ["#","\\","\\","%","%","%","%","%","%","%","\\","\\","\\","\\","\\","\\","%","%","%","#"],
                   ["#","\\","%","%","%","%","%","%","%","%","%","\\","\\","\\","\\","%","%","%","%","#"],
                   ["#","\\","%","%","%","%","%","%","%","%","%","\\","\\","\\","%","%","%","%","%","#"],
                   ["#","#","#","#","#","#","#","#","#","#","#","#","#","#","#","#","#","#","#","#"]]

    def __init__(self, console, player, input_manager=None) -> str:
        self.console = console
        self.player = player
        self.input_manager = input_manager

        self.input_manager.world = self

        self.menu_state = 0
        self.summary = Summary(self.player, self.console, self.input_manager, self)

    def clearTerminal(self):
        sys.stdout.write("\033[2J\033[3J\033[H")
        sys.stdout.write('\r\033[K')
        sys.stdout.flush()

    def getColour(self, text) -> str:
        coloured_text = ''
        match text:
            case "%":
                coloured_text = "spring_green1"
            case "#":
                coloured_text = "dark_green"
            case "\\":
                coloured_text = "grey37"
            case "~":
                coloured_text = "turquoise2"
            case _:
                coloured_text = 'deep_pink1'
        return coloured_text
    
    def isWalkable(self, text) -> bool:
        unpassables = ("~", "#")
        if text in unpassables:
            return False
        return True
    
    def drawWorld(self):
        self.input_manager.changeState("world")
        self.clearTerminal()

        player_pos = self.player.player_pos
        view_radius = 10  # how far around the player to render

        # compute safe boundaries
        min_y = max(0, player_pos[0] - view_radius)
        max_y = min(len(self.ascii_world), player_pos[0] + view_radius + 1)
        min_x = max(0, player_pos[1] - view_radius)
        max_x = min(len(self.ascii_world[0]), player_pos[1] + view_radius + 1)

        lines = []
        for y in range(min_y, max_y):
            line_parts = []
            for x in range(min_x, max_x):
                if (x == player_pos[1] and y == player_pos[0]): #if current is player
                    line_parts.append("[bold red]O[/bold red] ")
                else:
                    colouredText = self.getColour(self.ascii_world[y][x]) #get colour of ascii
                    escaped_ascii = escape(self.ascii_world[y][x]) #escape stuff like '\\' to make sure rich works
                    line_parts.append(f"[{colouredText}]{escaped_ascii}[/{colouredText}] ")
            lines.append(''.join(line_parts))

        # Print all at once so it is not slow at printing
        self.console.print('\n'.join(lines))

    def movePlayer(self, direciton):
        player_pos = self.player.player_pos.copy()
        if direciton in ('w', keyboard.Key.up):
            player_pos[0] -= 1
        elif direciton in ('s', keyboard.Key.down):
            player_pos[0] += 1
        elif direciton in ('d', keyboard.Key.right):
            player_pos[1] += 1
        elif direciton in ('a', keyboard.Key.left):
            player_pos[1] -= 1
        
        if (player_pos[0] >= 0 and player_pos[0] < len(self.ascii_world) and
            player_pos[1] >= 0 and player_pos[1] < len(self.ascii_world[0])):
            if self.isWalkable(self.ascii_world[player_pos[0]][player_pos[1]]):
                self.player.player_pos = player_pos
    
        self.drawWorld()

    def drawMenu(self):
        self.clearTerminal()
        options = [
            "Close Menu",
            "Party Summary",
            "Save Game",
            "Save & Exit"
        ]

        for state, option in enumerate(options):
            if state == self.menu_state:
                colour = "bright_white"
                arrow = " <-"
            else:
                colour = "bright_black"
                arrow = ""
            self.console.print(f"[{colour}]{option}[/{colour}]{arrow}\n")
    
    def moveMenu(self, key):
        if key in ('w', keyboard.Key.up):
            if self.menu_state > 0:
                self.menu_state -= 1
        elif key in ('s', keyboard.Key.down):
            if self.menu_state < 3:
                self.menu_state += 1
        self.drawMenu()

    def openMenu(self):
        self.input_manager.changeState("menu")
        self.drawMenu()

    def closeMenu(self):
        self.drawWorld()

    def confirmMenu(self):
        match self.menu_state:
            case 0: #close menu
                self.closeMenu()
            case 1: #summary
                self.summary.openSummary()
            case 2: #save game
                pass
            case 3: #save & exit
                exit()
    
    def closeSummary(self):
        self.openMenu()
