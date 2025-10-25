from rich.console import Console

import crittermon.tools as tools
from crittermon.player import Player
from crittermon.world import World
from crittermon.critter import Critter

'''
*** Implementations/TO DO! ***
- Overworld (DONE)
- Pausing / Menu (DONE)
- Creatures (DONE)
- Party Summary (Mainly Done)
- Encounters
- Fighting
- Catching
- Starters
- Healing
- Stats
- Trainers
- Leveling
- Bag
- itemsw
- pokemon items 
- Evolution
'''

def main():
    tools.gv = tools.GlobalVariables()

    start_pos = [10,10] #y, x instead of x, y
    player = Player(start_pos, "Jerold")

    a_moves = ["rapid spin", "earthquake", "metal claw", "swords dance"]
    b_moves = ["substitute", None, "substitute", None]

    a = Critter("Excadrill", 100, nature="Adamant", shiny=True, moves=a_moves)
    b = Critter("Rayquaza", 100, nickname="Rayray", nature="Jolly", moves=b_moves)

    player.addCritter(a)
    player.addCritter(b)

    world = World(player)
    world.open()

    while True:
        pass

if __name__ == "__main__":
    main()