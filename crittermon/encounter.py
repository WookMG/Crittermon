from random import choice
from random import randint
from pynput import keyboard

import crittermon.tools as tools
from crittermon.tools import clearTerminal, typeColour
from crittermon.critter import Critter

IMPLEMENTED_CRITTERS: dict[str, list[list[str]]] = {
    "Bulbasaur": [["Vine Whip", "Tackle", None, None], ["Vine Whip", "Scratch", None, None]],
    "Charmander": [["Ember", "Tackle", None, None], ["Ember", "Dragon Breath", None, None]],
    "Mudkip": [["Water Gun", "Tackle", None, None], ["Water Gun", "Mud Slap", None, None]],
}

TYPE_EFFECTIVENESS: dict[str, list[list[float]]] = {
    "Bug": [["grass", "psychic", "dark"], ["fire", "fighting", "poison", "flying", "ghost", "steel", "fairy"], []],
    "Dark": [["psychic", "ghost"], ["fighting", "dark", "fairy"], []],
    "Dragon": [["dragon"], ["steel"], ["fairy"]],
    "Electric": [["water", "flying"], ["electric", "grass", "dragon"], ["ground"]],
    "Fairy": [["fighting", "dragon", "dark"], ["fire", "poison", "steel"], []],
    "Fighting": [["normal", "ice", "rock", "dark", "steel"], ["poison", "flying", "psychic", "bug", "fairy"], ["ghost"]],
    "Fire": [["grass", "ice", "bug", "steel"], ["fire", "water", "rock", "dragon"], []],
    "Flying": [["grass", "fighting", "bug"], ["electric", "rock", "steel"], []],
    "Ghost": [["psychic", "ghost"], ["dark"], ["normal"]],
    "Grass": [["water", "ground", "rock"], ["fire", "grass", "poison", "flying", "bug", "dragon", "steel"], []],
    "Ground": [["fire", "electric", "poison", "rock", "steel"], ["grass", "bug"], ["flying"]],
    "Ice": [["grass", "ground", "flying", "dragon"], ["fire", "water", "ice", "steel"], []],
    "Normal": [[], ["rock", "steel"], ["ghost"]],
    "Poison": [["grass", "fairy"], ["poison", "ground", "rock", "ghost"], ["steel"]],
    "Psychic": [["fighting", "poison"], ["psychic", "steel"], ["dark"]],
    "Rock": [["fire", "ice", "flying", "bug"], ["fighting", "ground", "steel"], []],
    "Steel": [["ice", "rock", "fairy"], ["fire", "water", "electric", "steel"], []],
    "Water": [["fire", "ground", "rock"], ["water", "grass", "dragon"], []],
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
                self.player_critter: Critter = critter
                break

        self.state = 0 # 0 = picking fight catch etc. 1 = picking move 2 = catch
        self.option = 0 # 0 = fight 1 = summary 2 = catch 3 = run
        self.move_slot = 0

    # -------------------------
    # Encounter Functions
    # -------------------------

    def draw(self):
        clearTerminal()

        critter = self.critter
        pcritter = self.player_critter

        indent1 = " " * 2
        indent2 = " " * 30
        indent3 = " " * 2
        
        #Critters
        self.console.print(
            f"{critter.name}{indent1}Lv.{critter.level}\n"
            f"HP: {critter.current_hp}/{critter.hp}\n\n\n"
            f"{indent2}{pcritter.nickname}{indent3}Lv.{pcritter.level}\n"
            f"{indent2}HP: {pcritter.current_hp}/{pcritter.hp}\n"
        )

        #State dependant
        match self.state:
            case 0:
                self.drawOptions()
            case 1:
                self.drawMove()
            case 2:
                self.drawCatch()
            case 3:
                pass

    def move(self, key):
        match self.state:
            case 0:
                self.moveOption(key)
            case 1:
                self.moveMove(key)
            case 2:
                self.moveCatch(key)
            case 3:
                pass

    def confirm(self):
        match self.state:
            case 0:
                self.confirmOptions()
            case 1:
                self.confirmMove()
            case 2:
                self.confirmCatch()
            case 3:
                pass

    def open(self):
        self.input_manager.changeState(self)
        self.draw()

    def close(self):
        self.controller.open()
    
    def attack(self, move):
        critter = self.critter
        pcritter = self.player_critter

        enemy_move = None
        while(not enemy_move or enemy_move.name == "Empty"):
            enemy_move = choice(critter.moves)

        #used later for damage animation maybe
        pcritter_old_hp = pcritter.current_hp
        critter_old_hp = critter.current_hp

        if pcritter.speed >= critter.speed:
            critter.current_hp -= self.damageCalc(move, pcritter, critter)
            if critter.current_hp <= 0:
                self.win()
                return
            pcritter.current_hp -= self.damageCalc(enemy_move, critter, pcritter)
            if pcritter.current_hp <= 0:
                self.lose()
                return
        else:
            pcritter.current_hp -= self.damageCalc(enemy_move, critter, pcritter)
            if pcritter.current_hp <= 0:
                self.lose()
                return
            critter.current_hp -= self.damageCalc(move, pcritter, critter)
            if critter.current_hp <= 0:
                self.win()
                return
        self.openOptions()

    def win(self):
        self.controller.open()

    def lose(self):
        pass

    def catch(self):
        pass

    def damageCalc(self, move, critter1, critter2) -> int:
        atk = critter1.attack if move.category == "Physical" else critter1.sp_attack
        defense = critter2.defense if move.category == "Physical" else critter2.sp_defense

        crit = 1.5 if randint(1, 24) == 1 else 1
        random = randint(85,100) / 100
        stab = 1.5 if move.type == critter1.type[0] or move.type == critter1.type[1] else 1
        effectiveness = self.getMoveEffectiveness(move, critter2)

        #why nintendo
        return round(round(round(round(round((((((2*critter1.level)/5) + 2) * move.power * (atk/defense))/50) + 2) * crit) * random) * stab) * effectiveness)

    def getMoveEffectiveness(self, move, critter) -> float:
        effectiveness = 1
        if move.name == "Struggle":
            return 1
        else:
            for list_num, lst in enumerate(TYPE_EFFECTIVENESS[move.type]):
                if critter.type[0] in lst:
                    match list_num:
                        case 0:
                            effectiveness *= 2
                        case 1:
                            effectiveness *= 0.5
                        case 2:
                            effectiveness *= 0
                if critter.type[1] and critter.type[1] in lst:
                    match list_num:
                        case 0:
                            effectiveness *= 2
                        case 1:
                            effectiveness *= 0.5
                        case 2:
                            effectiveness *= 0    
            return effectiveness

    def chooseRandomCritter(self) -> Critter:
        critter = choice(list(IMPLEMENTED_CRITTERS.keys()))
        moves = choice(IMPLEMENTED_CRITTERS[critter])

        return Critter(critter, randint(MIN_LVL, MAX_LVL), moves=moves)
    
    def __str__(self):
        return "fight"
    
    # -------------------------
    # Option Functions
    # -------------------------

    def drawOptions(self):
        options = {
            0: "Fight",
            1: "Critters",
            2: "Catch",
            3: "Run"
        }
        for state in range(0, 4):
            if state % 2 == 0: 

                colour1 = "bright_white" if state == self.option else "bright_black"
                colour2 = "bright_white" if state+1 == self.option else "bright_black"

                indent = " " * 20
                indent11 = " " * 1
                indent12 = " " * 1
                indent21 = " " * 1
                indent22 = " " * 1

                self.console.print(
                    f"[{colour1}]------------[/{colour1}]"
                    f"{indent}"
                    f"[{colour2}]------------[/{colour2}]\n"
                    f"[{colour1}]|{indent11}{options[state]}{indent12}|[/{colour1}]"
                    f"{indent}"
                    f"[{colour2}]|{indent21}{options[state+1]}{indent22}|[/{colour2}]\n"
                    f"[{colour1}]------------[/{colour1}]"
                    f"{indent}"
                    f"[{colour2}]------------[/{colour2}]\n"
                )
    def moveOption(self, key):
        if key in ('w', keyboard.Key.up):
            self.option = (self.option + 2) % 4
        if key in ('s', keyboard.Key.down):
            self.option = (self.option - 2) % 4
        if key in ('a', keyboard.Key.left):
            self.option = (self.option - 1) % 4
        if key in ('d', keyboard.Key.right):
            self.option = (self.option + 1) % 4
        self.draw()
    
    def confirmOptions(self):
        match self.option:
            case 0:
                self.openMove()
            case 1:
                pass
            case 2:
                self.openCatch
            case 3:
                pass
    
    def openOptions(self):
        self.state = 0
        self.draw()

    # -------------------------
    # Move Functions
    # -------------------------

    def drawMove(self):
        critter = self.player_critter

        for state, move in enumerate(critter.moves):
            if state % 2 == 0:
                move2 = critter.moves[state+1]

                name_indent1 = " " * (21 - len(move.name) - len(str(move.cur_pp)) - len(str(move.cur_pp)))
                name_indent2 = " " * (21 - len(move2.name) - len(str(move2.pp)) - len(str(move2.pp)))
                indent = " " * 10
                
                colour1 = "bright_white" if state == self.move_slot else "bright_black"
                colour2 = "bright_white" if state+1 == self.move_slot else "bright_black"

                self.console.print(
                    f"[{colour1}]------------------------[/{colour1}]"
                    f"{indent}"
                    f"[{colour2}]------------------------[/{colour2}]\n"
                    f"[{colour1}]|[{typeColour(move.type)}]{move.name}[/{typeColour(move.type)}]"
                    f"{name_indent1}{move.cur_pp}/{move.pp}|[/{colour1}]"
                    f"{indent}"
                    f"[{colour2}]|[{typeColour(move2.type)}]{move2.name}[/{typeColour(move2.type)}]"
                    f"{name_indent2}{move2.cur_pp}/{move2.pp}|[/{colour2}]\n"
                    f"[{colour1}]------------------------[/{colour1}]"
                    f"{indent}"
                    f"[{colour2}]------------------------[/{colour2}]\n"
                )

    def moveMove(self, key):
        if key in ('w', keyboard.Key.up):
            self.move_slot = (self.move_slot + 2) % 4
        if key in ('s', keyboard.Key.down):
            self.move_slot = (self.move_slot - 2) % 4
        if key in ('a', keyboard.Key.left):
            self.move_slot = (self.move_slot - 1) % 4
        if key in ('d', keyboard.Key.right):
            self.move_slot = (self.move_slot + 1) % 4
        self.draw()

    def confirmMove(self):
        self.attack(self.critter.moves[self.move_slot]) 

    def openMove(self):
        self.state = 1
        self.draw()

    def closeMove(self):
        self.openOptions

    # -------------------------
    # Catch Functions
    # -------------------------

    def drawCatch(self):
        pass

    def moveCatch(self, key):
        pass

    def confirmCatch(self):
        pass

    def openCatch(self):
        pass

    def closeCatch(self):
        pass


            
