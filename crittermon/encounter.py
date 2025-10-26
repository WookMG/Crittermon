from random import choice
from random import randint
from pynput import keyboard
from math import floor
import time

import crittermon.tools as tools
from crittermon.tools import clearTerminal, typeColour
from crittermon.critter import Critter
from crittermon.summary import FightSummary
from crittermon.infoMessage import message

IMPLEMENTED_CRITTERS: dict[str, list[list[str]]] = {
    "Bulbasaur": [["Vine Whip", "Tackle", None, None], ["Vine Whip", "Scratch", None, None]],
    "Charmander": [["Ember", "Tackle", None, None], ["Ember", "Dragon Breath", None, None]],
    "Mudkip": [["Water Gun", "Tackle", None, None], ["Water Gun", "Mud Slap", None, None]],
}

TYPE_EFFECTIVENESS: dict[str, list[list[float]]] = {
    "bug": [["grass", "psychic", "dark"], ["fire", "fighting", "poison", "flying", "ghost", "steel", "fairy"], []],
    "dark": [["psychic", "ghost"], ["fighting", "dark", "fairy"], []],
    "dragon": [["dragon"], ["steel"], ["fairy"]],
    "electric": [["water", "flying"], ["electric", "grass", "dragon"], ["ground"]],
    "fairy": [["fighting", "dragon", "dark"], ["fire", "poison", "steel"], []],
    "fighting": [["normal", "ice", "rock", "dark", "steel"], ["poison", "flying", "psychic", "bug", "fairy"], ["ghost"]],
    "fire": [["grass", "ice", "bug", "steel"], ["fire", "water", "rock", "dragon"], []],
    "flying": [["grass", "fighting", "bug"], ["electric", "rock", "steel"], []],
    "ghost": [["psychic", "ghost"], ["dark"], ["normal"]],
    "grass": [["water", "ground", "rock"], ["fire", "grass", "poison", "flying", "bug", "dragon", "steel"], []],
    "ground": [["fire", "electric", "poison", "rock", "steel"], ["grass", "bug"], ["flying"]],
    "ice": [["grass", "ground", "flying", "dragon"], ["fire", "water", "ice", "steel"], []],
    "normal": [[], ["rock", "steel"], ["ghost"]],
    "poison": [["grass", "fairy"], ["poison", "ground", "rock", "ghost"], ["steel"]],
    "psychic": [["fighting", "poison"], ["psychic", "steel"], ["dark"]],
    "rock": [["fire", "ice", "flying", "bug"], ["fighting", "ground", "steel"], []],
    "steel": [["ice", "rock", "fairy"], ["fire", "water", "electric", "steel"], []],
    "water": [["fire", "ground", "rock"], ["water", "grass", "dragon"], []],
}

EFFECTIVENESS: dict[float, str] = {
    0.0: "Immune",
    0.25: "Not Very Effective",
    0.5: "Not Very Effective",
    1.0: "",
    2.0: "Super Effective",
    4.0: "Supper Effective",
}

HEALTH_COLORS = [
    "red",       # 0-10%
    "red3",      # 10-20%
    "orange_red1",  # 20-30%
    "dark_orange",  # 30-40%
    "orange1",      # 40-50%
    "yellow1",      # 50-60%
    "yellow3",      # 60-70%
    "chartreuse3",  # 70-80%
    "green3",       # 80-90%
    "green1"        # 90-100%
]

MIN_LVL = 95
MAX_LVL = 99

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
        
        self.summary = FightSummary(self, self.player_critter)
        self.state = 0 # 0 = picking/fight/catch etc. | 1 = picking move | 2 = catch | 3 = attacking
        self.option = 0 # 0 = fight | 1 = summary | 2 = catch | 3 = run
        self.move_slot = 0

        self.critters_involved = [self.player_critter]

    # -------------------------
    # Encounter Functions
    # -------------------------

    def draw(self):
        clearTerminal()

        critter = self.critter
        pcritter = self.player_critter

        indent1 = " " * 2 #spacing between critter name and lvl
        indent2 = " " * 30 #spacing between critters
        
        critter_hp_colour = self.getHealthColour(critter.current_hp, critter.hp)
        pcritter_hp_colour = self.getHealthColour(pcritter.current_hp, pcritter.hp)

        #Critters
        self.console.print(
            f"{critter.getName()}{indent1}Lv.{critter.level}\n"
            f"HP: [bold {critter_hp_colour}]{critter.current_hp}[/bold {critter_hp_colour}]/{critter.hp}\n\n\n"
            f"{indent2}{pcritter.getName()}{indent1}Lv.{pcritter.level}\n"
            f"{indent2}HP: [bold {pcritter_hp_colour}]{pcritter.current_hp}[/bold {pcritter_hp_colour}]/{pcritter.hp}\n"
            , style="bright_white")

        #State dependant
        match self.state:
            case 0:
                self.drawOptions()
            case 1:
                self.drawMove()
            case 2:
                self.drawCatch()

    def move(self, key):
        match self.state:
            case 0:
                self.moveOption(key)
            case 1:
                self.moveMove(key)
            case 2:
                self.moveCatch(key)

    def confirm(self):
        match self.state:
            case 0:
                self.confirmOptions()
            case 1:
                self.confirmMove()
            case 2:
                self.confirmCatch()

    def open(self):
        self.input_manager.changeState(self)
        self.state = 0
        self.draw()

    def close(self):
        if self.state == 1 or self.state == 2:
            self.openOptions()

    def closeEncounter(self):
        self.controller.open()

    def closeSummary(self):
        self.open()

    def attack(self, move):
        self.state = 3

        critter = self.critter
        pcritter = self.player_critter

        enemy_move = None
        while(not enemy_move or enemy_move.name == "Empty"):
            enemy_move = choice(critter.moves)

        if not move:
            self.drawAttack(enemy_move, critter, pcritter)
            self.checkFainted(pcritter)
        else:
            if pcritter.speed >= critter.speed:
                self.drawAttack(move, pcritter, critter)
                if self.checkFainted(critter):
                    return

                self.drawAttack(enemy_move, critter, pcritter)
                if self.checkFainted(pcritter):
                    return
            else:
                self.drawAttack(enemy_move, critter, pcritter)
                if self.checkFainted(pcritter):
                    return

                self.drawAttack(move, pcritter, critter)
                if self.checkFainted(critter):
                    return
        self.open()

    def getAttacked(self):
        self.attack(None)
    
    def drawAttack(self, attacker_move, attacker, victim):
        if attacker_move.category == "status":
            return
        
        hp_drain = 0.075

        self.draw()
        self.console.print(
            f"[bold]{attacker.getName()}[/bold] used "
            f"[bold]{attacker_move.name}[/bold] on "
            f"[bold]{victim.getName()}[/bold]"
            , style="bright_white")

        time.sleep(1.5)

        if randint(1,100) > attacker_move.accuracy:
            self.draw()
            message(f"{attacker.getName()} missed...")
            return

        old_hp = victim.current_hp
        hp = victim.current_hp - self.damageCalc(attacker_move, attacker, victim)
        effectiveness = EFFECTIVENESS[self.getMoveEffectiveness(attacker_move, victim)]

        if effectiveness != "Immune" and effectiveness: #if the move is super or not super effective
            for new_hp in reversed(range(hp, old_hp)):
                if new_hp < 0:
                    break

                victim.current_hp = new_hp

                self.draw()
                self.console.print(
                    f"It's [bold]{effectiveness}[/bold]"
                    , style="bright_white")
                time.sleep(hp_drain)
        elif effectiveness == "Immune": # if the move is immune
            self.draw()
            self.console.print(
                    f"[bold]{victim.getName()}[/bold] is "
                    f"[bold]{effectiveness}[/bold] to "
                    f"[bold]{attacker_move.name}[/bold]"
                    , style="bright_white")
            time.sleep(1.5)
        else: #if the move is neutral
            for new_hp in reversed(range(hp, old_hp)):
                if new_hp < 0:
                    break
                victim.current_hp = new_hp

                self.draw()
                self.console.print(
                    f"[bold]{attacker.getName()}[/bold] used "
                    f"[bold]{attacker_move.name}[/bold] on "
                    f"[bold]{victim.getName()}[/bold]"
                    , style="bright_white")
                time.sleep(hp_drain)
        time.sleep(1.5)

    def checkFainted(self, critter):
        if critter.current_hp <= 0:
            critter.hasFainted()
            if critter == self.player_critter:
                self.lose()
            else:
                self.win()
            return True
        return False

    def win(self):
        #gain exp and evs
        victim = self.critter
        exp = floor(((victim.base_exp_yield*victim.level/5)*(((2*victim.level+10)/(victim.level+self.player_critter.level+10))**2.5))+1)
        evs = victim.ev_yield
        for critter in self.critters_involved:
            self.draw()
            message(f"[bold]{critter.getName()}[/bold] has gained [bold]{exp}[/bold] EXP")
            critter.gainEXP(exp)
            critter.gainEVS(evs)

        message("[green1]You have won the battle! Congratulations![/green1]")
        self.controller.open() # TODO

    def lose(self):
        lose = True
        for critter in self.player.party:
            if critter and not critter.fainted:
                lose = False
                break
        
        if lose:
            self.draw()
            message(f"All your Critters have fainted! You have lost the battle...")
            time.sleep(0.25)
            self.controller.open() # TODO
        else:
            self.openSwitchCritter(False)

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
        return round(round(round(round(round((((((2*critter1.level)/5)+2)*move.power*(atk/defense))/50)+2)*crit)*random)*stab)*effectiveness)

    def getMoveEffectiveness(self, move, critter) -> float:
        effectiveness = 1
        if move.name == "Struggle":
            return 1
        else:
            for list_num, lst in enumerate(TYPE_EFFECTIVENESS[move.type.lower()]):
                if critter.type[0].lower() in lst:
                    match list_num:
                        case 0:
                            effectiveness *= 2
                        case 1:
                            effectiveness *= 0.5
                        case 2:
                            effectiveness *= 0
                if critter.type[1] and critter.type[1].lower() in lst:
                    match list_num:
                        case 0:
                            effectiveness *= 2
                        case 1:
                            effectiveness *= 0.5
                        case 2:
                            effectiveness *= 0    
            return effectiveness

    def getHealthColour(self, current, maximum):
        percent = max(0, min(current / maximum, 1))
        index = int(percent * 10)
        index = 9 if index == 10 else index

        return HEALTH_COLORS[index]

    def chooseRandomCritter(self) -> Critter:
        critter = choice(list(IMPLEMENTED_CRITTERS.keys()))
        moves = choice(IMPLEMENTED_CRITTERS[critter])

        return Critter(critter, randint(MIN_LVL, MAX_LVL), moves=moves)
    
    def openSwitchCritter(self, optional_switch):
        self.summary.optional_switch = optional_switch
        self.summary.open()

    def switchCritter(self, new_critter, optional_switch):
        self.player_critter = new_critter
        if new_critter not in self.critters_involved:
            self.critters_involved.append(new_critter)

        if optional_switch:
            self.getAttacked()
        else:
            self.open()
        
    def __str__(self):
        return "fight"
    
    # -------------------------
    # Option Functions
    # -------------------------

    def drawOptions(self):
        options = {
            0: "Fight",
            1: "Summary",
            2: "Catch",
            3: "Run"
        }
        for state in range(0, 4):
            if state % 2 == 0: 

                colour1 = "bright_white" if state == self.option else "bright_black"
                colour2 = "bright_white" if state+1 == self.option else "bright_black"

                indent = " " * 16
                indent1 = " " * round((13 - len(options[state])) / 2)
                indent2 = " " * round((13 - len(options[state+1])) /2)

                self.console.print(
                    f"[{colour1}]---------------[/{colour1}]"
                    f"{indent}"
                    f"[{colour2}]---------------[/{colour2}]\n"
                    f"[{colour1}]|{indent1}{options[state]}{indent1}|[/{colour1}]"
                    f"{indent}"
                    f"[{colour2}]|{indent2}{options[state+1]}{indent2}|[/{colour2}]\n"
                    f"[{colour1}]---------------[/{colour1}]"
                    f"{indent}"
                    f"[{colour2}]---------------[/{colour2}]\n"
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
                self.summary.open()
            case 2:
                self.openCatch
            case 3:
                self.run()
    
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
        self.attack(self.player_critter.moves[self.move_slot]) 

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
    
    # -------------------------
    # Run Functions
    # -------------------------

    def run(self):
        if randint(0, 1) == 1:
            self.draw()
            message("You got away safely!")
            self.closeEncounter()
        else:
            message(f"{self.player_critter.getName()} couldn't get away!")
            self.getAttacked()