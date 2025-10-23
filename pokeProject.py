import sys
import time
import termios
from pynput import keyboard
from rich.console import Console

from player import Player
from world import World
from critter import Critter

'''
*** Implementations/TO DO! ***
- Overworld (DONE)
- Pausing / Menu (DONE)
- Creatures (DONE)
- Party Summary
- Encounters
- Fighting
- Catching
- Starters
- Healing
- Stats
- Trainers
- Leveling
- Bag
- items
- pokemon items
- Evolution
'''
class InputManager:
    def __init__(self, world=None, summary=None, fight=None, state=None):
        self.world = world
        self.summary = summary
        self.fight = fight
        self.state = state

        # Define key maps for each state
        self.keymaps = {}
        
        # Taken from pynput documentation
        self.listener = keyboard.Listener(on_press=self.onPress)
        self.listener.daemon = True
        self.listener.start()

    def pause(self):
        if self.listener.running:
            self.listener.stop()

    def unpause(self):
        self.listener = keyboard.Listener(on_press=self.onPress)
        self.listener.daemon = True
        self.listener.start()

    # -------------------- -----
    # State-specific key maps
    # -------------------------
    def _worldKeymap(self):
        return {} if not self.world else {
            'w': lambda: self.world.movePlayer('w'),
            'a': lambda: self.world.movePlayer('a'),
            's': lambda: self.world.movePlayer('s'),
            'd': lambda: self.world.movePlayer('d'),
            'm': self.world.openMenu,
            keyboard.Key.up: lambda: self.world.movePlayer(keyboard.Key.up),
            keyboard.Key.down: lambda: self.world.movePlayer(keyboard.Key.down),
            keyboard.Key.left: lambda: self.world.movePlayer(keyboard.Key.left),
            keyboard.Key.right: lambda: self.world.movePlayer(keyboard.Key.right),
            keyboard.Key.esc: self.world.openMenu
        }

    def _menuKeymap(self):
        return {} if not self.world else {
            'w': lambda: self.world.moveMenu('w'),
            's': lambda: self.world.moveMenu('s'),
            'c': self.world.confirmMenu,
            'm': self.world.closeMenu,
            keyboard.Key.up: lambda: self.world.moveMenu(keyboard.Key.up),
            keyboard.Key.down: lambda: self.world.moveMenu(keyboard.Key.down),
            keyboard.Key.enter: self.world.confirmMenu,
            keyboard.Key.esc: self.world.closeMenu
        }

    def _summaryKeymap(self):
        return {} if not self.summary else {
            'w': lambda: self.summary.move('w'),
            's': lambda: self.summary.move('s'),
            'd': lambda: self.summary.move('d'),
            'a': lambda: self.summary.move('a'),
            'c': self.summary.confirm,
            keyboard.Key.up: lambda: self.summary.move(keyboard.Key.up),
            keyboard.Key.down: lambda: self.summary.move(keyboard.Key.down),
            keyboard.Key.right: lambda: self.summary.move(keyboard.Key.right),
            keyboard.Key.left: lambda: self.summary.move(keyboard.Key.left),
            keyboard.Key.enter: self.summary.confirm,
            keyboard.Key.esc: self.summary.close
        }

    def _fightKeymap(self):
        return {} if not self.fight else {}

    # -------------------------
    # Core listener logic
    # -------------------------
    def onPress(self, key):
        if not self.state:
            return  # ignore input if no state is set yet

        # Get keymap dynamically
        keymap = self.keymaps.get(self.state)
        if keymap is None:
            # Build keymap on demand
            keymap = getattr(self, f"_{self.state}Keymap")()
            self.keymaps[self.state] = keymap

        try:
            if key.char in keymap:
                keymap[key.char]()
        except AttributeError:
            if key in keymap:
                keymap[key]()

    def changeState(self, new_state):
        if new_state not in ("world", "menu", "summary", "fight"):
            raise ValueError(f"Unknown state '{new_state}'")
        self.state = new_state
        # Rebuild keymap when switching
        self.keymaps[self.state] = getattr(self, f"_{self.state}Keymap")()

def main():
    console = Console()
    inputManager = InputManager()

    start_pos = [10,10] #y, x instead of x, y
    player = Player(start_pos, "Jerold")

    a = Critter("Excadrill", shiny=True)
    b = Critter("Rayquaza", "Rayray")

    player.addCritter(a)
    player.addCritter(b)

    world = World(console, player, inputManager)
    world.drawWorld()

    while True:
        pass

if __name__ == "__main__":
    main()