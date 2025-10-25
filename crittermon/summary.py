import sys
import termios
import time
from pynput import keyboard
from prompt_toolkit import prompt

import crittermon.tools as tools
from crittermon.tools import clearTerminal, flush_stdin
from crittermon.confirmMenu import ConfirmMenu
from crittermon.critter import NATURES

TYPE_COLORS = {
    "bug": "chartreuse3",
    "dark": "grey19",
    "dragon": "royal_blue1",
    "electric": "yellow1",
    "fairy": "pink1",
    "fighting": "indian_red",
    "fire": "orange1",
    "flying": "sky_blue1",
    "ghost": "dark_violet",
    "grass": "green3",
    "ground": "tan",
    "ice": "light_cyan1",
    "normal": "grey70",
    "poison": "medium_purple3",
    "psychic": "deep_pink1",
    "rock": "dark_goldenrod",
    "steel": "light_steel_blue3",
    "water": "deep_sky_blue1",
}
class Summary:

    def __init__(self, controller):
        self.console = tools.gv.console
        self.input_manager = tools.gv.input_manager
        self.player = tools.gv.player
        self.party = self.player.party

        self.controller = controller # if we are fighting or in overworld
        self.state = "party" # 'party' / 'critter' / 'move' / 'option_party' / 'option_rename' / 'option_release'

        self.selected_slot = 0
        self.reposition_slot = 0
        self.party_option = 0
        self.move_slot = 0

    # -------------------------
    # Summary Functions
    # -------------------------

    def open(self):
        self.input_manager.changeState(self)
        self.openPartySummary()

    def close(self):
        match self.state:
            case "party":
                self.controller.closeSummary()
            case "party_option":
                self.closePartyOption()
            case "critter":
                self.closeCritterSummary()
            case "move":
                self.closeMoveSummary()

    def move(self, key):
        match self.state:
            case "party":
                self.movePartySummary(key)
            case "party_option":
                self.movePartyOption(key)
            case "repositioning":
                self.movePartySummary(key)
            case "critter":
                self.moveCritterSummary(key)
            case "move":
                self.moveMoveSummary(key)
    
    def confirm(self):
        match self.state:
            case "party":
                self.confirmPartySummary()
            case "party_option":
                self.confirmPartyOption()
            case "repositioning":
                self.confrimRepositionCritter()
            case "critter":
                self.closeCritterSummary()
            case "move":
                pass
    
    def _typeColour(self, type: str) -> str:
        ''' Returns a rich colour code to colour types in drawCritterSummary '''
        return TYPE_COLORS.get(type.lower(), "bright_white")
    
    def __str__(self):
        return "summary"

    # -------------------------
    # Party Functions
    # -------------------------

    def drawPartySummary(self):
        #evil fucking function of pain and suffering ( I WILL NOT USE AI TO MAKE IT SMALLER RAHHH )
        clearTerminal()
        for slot, critter in enumerate(self.party):
            if critter != None:
                if slot == self.selected_slot:
                    if critter.shiny:
                        colour = "yellow1"
                    else:
                        colour = "bright_white"
                    hp_colour = "spring_green1"
                    arrow = " <-"
                else:
                    if critter.shiny:
                        colour = "dark_goldenrod"
                    else:
                        colour = "bright_black"
                    hp_colour = "dark_sea_green4"
                    arrow = ""
                if slot % 2 == 0:
                    if critter.shiny:
                        self.console.print(
                            f"[{colour}]{critter.nickname} ✦[/{colour}]{arrow}\n"
                            f"  [{hp_colour}]{critter.current_hp}[/{hp_colour}]/{critter.hp}",
                            end='')
                    else:
                        self.console.print(
                            f"[{colour}]{critter.nickname}[/{colour}]{arrow}\n"
                            f"  [{hp_colour}]{critter.current_hp}[/{hp_colour}]/{critter.hp}",
                            end='')
                else:
                    if critter.shiny:
                        self.console.print(
                            f"              "
                            f"[{colour}]{critter.nickname} ✦[/{colour}]{arrow}\n"
                            f"                          "
                            f"[{hp_colour}]{critter.current_hp}[/{hp_colour}]/{critter.hp}\n",
                            end='')
                    else:
                        self.console.print(
                            f"              "
                            f"[{colour}]{critter.nickname}[/{colour}]{arrow}\n"
                            f"                          "
                            f"[{hp_colour}]{critter.current_hp}[/{hp_colour}]/{critter.hp}\n",
                            end='')
            else:
                if slot == self.selected_slot:
                    colour = "bright_white"
                    hp_colour = "bright_white"
                    arrow = " <-"
                else:
                    colour = "bright_black"
                    hp_colour = "bright_black"
                    arrow = ''
                if slot % 2 == 0:
                    self.console.print(
                        f"[{colour}]NONE[/{colour}]{arrow}\n"
                        f"[{hp_colour}]   -/-[{hp_colour}]",
                        end='')
                else:
                    self.console.print(
                        f"                  "
                        f"[{colour}]NONE[/{colour}]{arrow}\n"
                        f"                           "
                        f"[{hp_colour}]-/-[/{hp_colour}]\n",
                        end='')

    def openPartySummary(self):
        self.state = "party"
        self.selected_slot = 0
        self.drawPartySummary()

    def movePartySummary(self, key):
        if key in ('w', keyboard.Key.up):
            self.selected_slot = (self.selected_slot - 2) % 6
        elif key in ('s', keyboard.Key.down):
            self.selected_slot = (self.selected_slot + 2) % 6
        elif key in ('d', keyboard.Key.right):
            self.selected_slot = (self.selected_slot + 1) % 6
        elif key in ('a', keyboard.Key.left):
            self.selected_slot = (self.selected_slot - 1) % 6
        self.drawPartySummary()
    
    def confirmPartySummary(self):
        if self.party[self.selected_slot]:
            self.openPartyOption()

    # -------------------------
    # Party Option Functions
    # -------------------------

    def drawPartyOption(self):
        critter = self.party[self.selected_slot]
        clearTerminal()
        options = [
            f"{critter.nickname}'s Summary",
            "Rename",
            "Change Position",
            "Release",
            "Close"
        ]

        question = f"What would you like to do with {critter.nickname}"
        self.console.print(f"[bold bright_white]{question}[/bold bright_white]\n")
        for state, option in enumerate(options):
            if state == self.party_option:
                colour = "bright_white"
                arrow = " <-"
            else:
                colour = "bright_black"
                arrow = ""
            self.console.print(f"[{colour}]{option}[/{colour}]{arrow}\n")

    def openPartyOption(self):
        self.state = "party_option"
        self.party_option = 0
        self.drawPartyOption()

    def closePartyOption(self):
        self.openPartySummary()
    
    def movePartyOption(self, key):
        if key in ('w', keyboard.Key.up):
            if self.party_option > 0:
                self.party_option -= 1
        elif key in ('s', keyboard.Key.down):
            if self.party_option < 4:
                self.party_option += 1
        self.drawPartyOption()
    
    def confirmPartyOption(self):
        critter = self.party[self.selected_slot]
        match self.party_option:
            case 0: #critter summary
                self.openCritterSummary()
            case 1: #change name
                self.renameCritter()
            case 2: #change position
                self.repositionCritter()
            case 3: #release critter
                confirm = ConfirmMenu(
                    self,
                    f"Are you sure you want to release {critter.nickname}?",
                    "releaseCritter",
                    "closeReleaseCritter")
            case 4: #close
                self.closePartyOption()

    def releaseCritter(self):
        self.input_manager.changeState(self)
        self.player.removeCritter(self.selected_slot)
        time.sleep(0.1)
        self.openPartySummary()
    
    def closeReleaseCritter(self):
        self.input_manager.changeState(self)
        self.openPartyOption()

    def renameCritter(self):
        self.state = "renaming"
        clearTerminal()
        flush_stdin()  

        self.input_manager.pause()

        critter = self.party[self.selected_slot]
        new_name = prompt(f"Please enter {critter.nickname}'s new name: ", default=critter.nickname).strip()

        if not new_name:
            critter.nickname = critter.name
        else:
            critter.nickname = new_name

        self.input_manager.unpause()
        time.sleep(0.1)

        self.openPartySummary()
    
    def repositionCritter(self):
        self.state = "repositioning"

        self.reposition_slot = self.selected_slot
        self.drawPartySummary()

    def confrimRepositionCritter(self):
        critter1 = self.party[self.reposition_slot]
        critter2 = self.party[self.selected_slot]

        self.party[self.reposition_slot] = critter2
        self.party[self.selected_slot] = critter1

        time.sleep(0.1)
        self.openPartySummary()

    # -------------------------
    # Critter Functions
    # -------------------------

    def drawCritterSummary(self):
        clearTerminal()
        critter = self.party[self.selected_slot]

        # summary
        self.console.print(
            f"[bold bright_white]Summary <-[/bold bright_white]"
            f"          "
            f"[bright_black]Moves[/bright_black]\n")
        
        # list nickname + (name) (if they are different)
        if critter.name == critter.nickname:
            if critter.shiny:
                name = f"{critter.name} ✦   [bright_white]lvl {critter.level}[/bright_white]"
                colour = "yellow1"
            else:
                name = f"{critter.name}   lvl {critter.level}"
                colour = "bright_white"
            self.console.print(f"[{colour}]{name}[/{colour}]\n")
        else:
            if critter.shiny:
                name = f"{critter.nickname} ({critter.name}) ✦   [bright_white]lvl {critter.level}[/bright_white]"
                colour = "yellow1"
            else:
                name = f"{critter.nickname} ({critter.name})   lvl {critter.level}"
                colour = "bright_white"
            self.console.print(f"[{colour}]{name}[/{colour}]\n")

        # list type
        colour1 = ""
        colour2 = ""

        type1 = critter.type[0]
        colour1 = self._typeColour(type1)
        if critter.type[1]:
            type2 = critter.type[1]
            colour2 = self._typeColour(type2)
            self.console.print(f"[bright_white]Type: [{colour1}]{type1}[/{colour1}]/[{colour2}]{type2}[/{colour2}][/bright_white]\n")
        else:
            self.console.print(f"[bright_white]Type: [{colour1}]{type1}[/{colour1}][/bright_white]\n")

        # list nature
        self.console.print(f"[bright_white]Nature: {critter.nature}[/bright_white]\n")

        # list stats
        hp_colour = "green1"
        speed_colour = "deep_sky_blue1"
        attack_colour = "red1"
        sp_attack_colour = "magenta1"
        defense_colour = "orange1"
        sp_defense_colour = "yellow1"

        cur_hp = critter.current_hp
        hp = critter.hp
        spd = critter.speed
        atk = critter.attack
        spatk = critter.sp_attack
        defense = critter.defense
        spdef = critter.sp_defense

        indent1 = " " * (13 - len(str(critter.current_hp)) - len(str(critter.hp)))
        indent2 = " " * (10 - len(str(critter.attack)))
        indent3 = " " * (9 - len(str(critter.defense)))

        nature = NATURES.get(critter.nature)
        if nature[0] != nature[1]:
            nature_buff = nature[0]
            nature_nerf = nature[1]

            hp = str(hp) + " [red1]▲[/red1]" if nature_buff == "hp" else hp
            hp = str(hp) + " [deep_sky_blue1]▼[/deep_sky_blue1]" if nature_nerf == "hp" else hp
            spd = str(spd) + " [red1]▲[/red1]" if nature_buff == "speed" else spd
            spd = str(spd) + " [deep_sky_blue1]▼[/deep_sky_blue1]" if nature_nerf == "speed" else spd
            atk = str(atk) + " [red1]▲[/red1]" if nature_buff == "attack" else atk
            atk = str(atk) + " [deep_sky_blue1]▼[/deep_sky_blue1]" if nature_nerf == "attack" else atk
            spatk = str(spatk) + " [red1]▲[/red1]" if nature_buff == "sp_attack" else spatk
            spatk = str(spatk) + " [deep_sky_blue1]▼[/deep_sky_blue1]" if nature_nerf == "sp_attack" else spatk
            defense = str(defense) + " [red1]▲[/red1]" if nature_buff == "defense" else defense
            defense = str(defense) + " [deep_sky_blue1]▼[/deep_sky_blue1]" if nature_nerf == "defense" else defense
            spdef = str(spdef) + " [red1]▲[/red1]" if nature_buff == "sp_defense" else spdef
            spdef = str(spdef) + " [deep_sky_blue1]▼[/deep_sky_blue1]" if nature_nerf == "sp_defense" else spdef

            indent1 = " " (11 - len(str(critter.current_hp)) - len(str(critter.hp))) if nature_buff == "hp" or nature_nerf == "hp" else indent1
            indent2 = " " * (8 - len(str(critter.attack))) if nature_buff == "attack" or nature_nerf == "attack" else indent2
            indent3 = " " * (7 - len(str(critter.defense))) if nature_buff == "defense" or nature_nerf == "defense" else indent3

        self.console.print(
            f"[{hp_colour}]HP[/{hp_colour}][bright_white]: {cur_hp}/{hp}[/bright_white]"
            f"{indent1}"
            f"[{speed_colour}]Speed[/{speed_colour}][bright_white]: {spd}[/bright_white]\n"
            f"[{attack_colour}]Attack[/{attack_colour}][bright_white]: {atk}[/bright_white]"
            f"{indent2}"
            f"[{sp_attack_colour}]Special Attack[/{sp_attack_colour}][bright_white]: {spatk}[/bright_white]\n"
            f"[{defense_colour}]Defense[/{defense_colour}][bright_white]: {defense}[/bright_white]"
            f"{indent3}"
            f"[{sp_defense_colour}]Special Defense[/{sp_defense_colour}][bright_white]: {spdef}[/bright_white]"        
            )

    def openCritterSummary(self):
        self.state = "critter"
        self.drawCritterSummary()

    def closeCritterSummary(self):
        self.openPartySummary()
    
    def moveCritterSummary(self, key):
        if key in ('d', keyboard.Key.right):
            self.openMoveSummary()

    # -------------------------
    # Move Functions
    # -------------------------

    def drawMoveSummary(self):
        clearTerminal()
        critter = self.party[self.selected_slot]

        #moves
        colour = "bright_white" if self.move_slot == 4 else "bright_black"
        self.console.print(
            f"[bright_black]Summary[/bright_black]"
            f"             "
            f"[bold {colour}]Moves <-[/bold {colour}]\n")

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
                    f"[{colour1}]|[{self._typeColour(move.type)}]{move.name}[/{self._typeColour(move.type)}]"
                    f"{name_indent1}{move.cur_pp}/{move.pp}|[/{colour1}]"
                    f"{indent}"
                    f"[{colour2}]|[{self._typeColour(move2.type)}]{move2.name}[/{self._typeColour(move2.type)}]"
                    f"{name_indent2}{move2.cur_pp}/{move2.pp}|[/{colour2}]\n"
                    f"[{colour1}]------------------------[/{colour1}]"
                    f"{indent}"
                    f"[{colour2}]------------------------[/{colour2}]\n"
                )
        
        #selected move info
        if self.move_slot != 4:
            move = critter.moves[self.move_slot]
            if move:
                indent = " " * 4
                self.console.print(
                    f"[bright_white][indian_red]𓊍[/indian_red] Power: {move.power}{indent}"
                    f"[chartreuse3]⌖[/chartreuse3] Accuracy: {move.accuracy}%{indent}"
                    f"Type: {move.category}[/bright_white]\n"
                    f"This move does stuff... I think"
                )

    def openMoveSummary(self):
        self.state = "move"
        self.move_slot = 4
        self.drawMoveSummary()

    def closeMoveSummary(self):
        self.openPartySummary()
    
    def moveMoveSummary(self, key):
        if key in ('w', keyboard.Key.up):
            if self.move_slot == 4:
                self.move_slot = 3
            elif self.move_slot == 0 or self.move_slot == 1:
                self.move_slot = 4
            else:
                self.move_slot = (self.move_slot + 2) % 4
        if key in ('s', keyboard.Key.down):
            if self.move_slot == 4:
                self.move_slot = 0
            else:
                self.move_slot = (self.move_slot - 2) % 4
        if key in ('a', keyboard.Key.left):
            if self.move_slot == 4:
                self.openCritterSummary()
                return
            else:
                self.move_slot = (self.move_slot - 1) % 4
        if key in ('d', keyboard.Key.right):
            if self.move_slot == 4:
                self.move_slot = 0
            self.move_slot = (self.move_slot + 1) % 4
        self.drawMoveSummary()
        
