import crittermon.tools as tools
from crittermon.world import World
from crittermon.critter import Critter

'''
*** Implementations/TO DO! ***
- Overworld (DONE)d
- Pausing / Menu (DONE (NEED TO FINISH SAVING))
- Creatures (DONE)
- Party Summary (DONE)
- Encounters (DONE (JUST NEED TO ADD A LOT MORE POKEMON))
- Fighting (DONE)
- Catching

- multiple "maps" and buildings

- Stat raises 
- Statuses
- Secondary Effects
- Status moves

- Starters
- Healing

- Trainers
- Leveling (ie move level ups)
- Bag
- items
- pokemon items 

- Evolution
'''

def main():
    start_pos = [10,10] #y, x instead of x, y
    tools.gv = tools.GlobalVariables(start_pos, "Jerold")
    gv = tools.gv

    a_moves = ["rapid spin", "earthquake", "metal claw", "Petal Dance"]
    b_moves = ["substitute", "air slash", "substitute", None]

    a = Critter("Excadrill", 10, nature="Adamant", shiny=True, moves=a_moves)
    b = Critter("Rayquaza", 10, nickname="Rayray", nature="Jolly", moves=b_moves)

    gv.player.addCritter(a)
    gv.player.addCritter(b)

    world = World()

    world.open()

    while True:
        pass

if __name__ == "__main__":
    main()