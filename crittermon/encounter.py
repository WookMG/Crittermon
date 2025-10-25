from random import choice
from random import randint

import crittermon.tools as tools
from crittermon.tools import clearTerminal
from crittermon.critter import Critter

IMPLEMENTED_CRITTERS: dict[str, list[list[str]]] = {
    "Bulbasaur": [["Vine Whip", "Tackle", None, None], ["Vine Whipe", "Scratch", None, None]],
    "Charmander": [["Ember", "Tackle", None, None], ["Ember", "Dragon Breath", None, None]],
    "Mudkip": [["Water Gun", "Tackle", None, None], ["Water Gun", "Mud Slap", None, None]],
}

MIN_LVL = 5
MAX_LVL = 15
class Encounter:
    def __init__(self, controller):
        self.input_manager = tools.gv.input_manager
        self.player = tools.gv.player
        self.console = tools.gv.console
        self.controller = controller
    
        self.critter = self.chooseRandomCritter()

        #We should only get into an encounter if the player has a critter in their party
        for critter in self.player.party: 
            if critter:
                self.player_critter = critter
                break

    def draw(self):
        clearTerminal()
        self.console.print(f"you are in a fight with a lvl{self.critter.level} {self.critter.name} who is fighting your lvl{self.player_critter.level} {self.player_critter.name}")
    
    def move(self):
        pass

    def open(self):
        self.input_manager.changeState(self)
        self.draw()

    def close(self):
        self.controller.open()
    
    def win(self):
        pass

    def lose(self):
        pass

    def catch(self):
        pass

    def chooseRandomCritter(self) -> Critter:
        critter = choice(list(IMPLEMENTED_CRITTERS.keys()))
        moves = choice(IMPLEMENTED_CRITTERS[critter])

        return Critter(critter, randint(MIN_LVL, MAX_LVL), moves=moves)
    
    def __str__(self):
        return "fight"
            
