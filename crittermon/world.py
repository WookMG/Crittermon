import sys
from pynput import keyboard
from rich.markup import escape
from random import randint


import crittermon.tools as tools
from crittermon.tools import clearTerminal

from crittermon.summary import Summary
from crittermon.encounter import Encounter

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

    def __init__(self):
        self.console = tools.gv.console
        self.input_manager = tools.gv.input_manager
        self.player = tools.gv.player
        
        self.pause_menu = PauseMenu(self)

    def getTileColour(self, text) -> str:
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
    
    def isTileWalkable(self, text) -> bool:
        unpassables = ("~", "#")
        if text in unpassables:
            return False
        return True
    
    def isTileDangerous(self, text) -> bool:
        dangerous = ("%")
        if text in dangerous:
            return True
        return False

    def draw(self):
        clearTerminal()

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
                    colouredText = self.getTileColour(self.ascii_world[y][x]) #get colour of ascii
                    escaped_ascii = escape(self.ascii_world[y][x]) #escape stuff like '\\' to make sure rich works
                    line_parts.append(f"[{colouredText}]{escaped_ascii}[/{colouredText}] ")
            lines.append(''.join(line_parts))

        # Print all at once so it is not slow at printing
        self.console.print('\n'.join(lines))

    def open(self):
        self.input_manager.changeState(self)
        self.draw()
    
    def openPauseMenu(self):
        self.pause_menu.open()
    
    def move(self, direciton):
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
            if self.isTileWalkable(self.ascii_world[player_pos[0]][player_pos[1]]):
                self.player.player_pos = player_pos
            if self.isTileDangerous(self.ascii_world[player_pos[0]][player_pos[1]]):
                self.draw()
                self.trySpawnEncounter()
                return
    
        self.draw()
    
    def trySpawnEncounter(self):
        spawn = True if randint(1, 10) == 1 else False
        if spawn:
            encounter = Encounter(self)
            encounter.open()
        
    def __str__(self):
        return "world"

class PauseMenu():

    def __init__(self, world):
        self.console = tools.gv.console
        self.input_manager = tools.gv.input_manager
        self.world = world

        self.state = 0
        self.summary = Summary(self)

    def draw(self):
        clearTerminal()
        options = [
            "Close Menu",
            "Party Summary",
            "Save Game",
            "Save & Exit"
        ]

        for state, option in enumerate(options):
            if state == self.state:
                colour = "bright_white"
                arrow = " <-"
            else:
                colour = "bright_black"
                arrow = ""
            self.console.print(f"[{colour}]{option}[/{colour}]{arrow}\n")
    
    def move(self, key):
        if key in ('w', keyboard.Key.up):
            if self.state > 0:
                self.state -= 1
        elif key in ('s', keyboard.Key.down):
            if self.state < 3:
                self.state += 1
        self.draw()

    def open(self):
        self.input_manager.changeState(self)
        self.draw()

    def close(self):
        self.world.open()
    
    def closeSummary(self):
        self.open()

    def confirm(self):
        match self.state:
            case 0: #close menu
                self.close()
            case 1: #summary
                self.summary.open()
            case 2: #save game
                pass
            case 3: #save & exit
                exit()
    
    def __str__(self):
        return "pause"
