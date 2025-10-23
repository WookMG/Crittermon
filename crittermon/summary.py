import sys
import termios
import time
from pynput import keyboard
from prompt_toolkit import prompt

'''
TO DO
- add move summary
- add colour to pokemon typings in summary
- add confirmation for releasing
'''
class Summary:

    def __init__(self, player, console, input_manager, controller):
        self.player = player
        self.party = player.party
        self.console = console
        self.input_manager = input_manager

        self.controller = controller # if we are fighting or in overworld
        self.state = "party" # 'party' / 'critter' / 'move' / 'option_party' / 'option_rename' / 'option_release'

        self.selected_slot = 0
        self.reposition_slot = 0
        self.party_option = 0

    def clearTerminal(self):
        sys.stdout.write("\033[2J\033[3J\033[H")
        sys.stdout.write('\r\033[K')
        sys.stdout.flush()
    
    def flush_stdin(self):
        #Flush any pending characters in stdin (Linux/macOS)
        termios.tcflush(sys.stdin, termios.TCIFLUSH)

    # -------------------------
    # Summary Functions
    # -------------------------

    def openSummary(self):
        self.input_manager.summary = self
        self.input_manager.changeState("summary")

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

    # -------------------------
    # Party Functions
    # -------------------------

    def drawPartySummary(self):
        #evil fucking function of pain and suffering ( I WILL NOT USE AI TO MAKE IT SMALLER RAHHH )
        self.clearTerminal()
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

    def drawPartyOption(self):
        critter = self.party[self.selected_slot]
        self.clearTerminal()
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
        match self.party_option:
            case 0: #critter summary
                self.openCritterSummary()
            case 1: #change name
                self.renameCritter()
            case 2: #change position
                self.repositionCritter()
            case 3: #release critter
                self.player.removeCritter(self.selected_slot)
                time.sleep(0.1)
                self.openPartySummary()
            case 4: #close
                self.closePartyOption()

    def renameCritter(self):
        self.state = "renaming"
        self.clearTerminal()
        self.flush_stdin()  

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
        self.clearTerminal()
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
        type = f"Type: {critter.type[0]}"
        if critter.type[1]:
            type = type + f"/{critter.type[1]}"
        self.console.print(f"[bright_white]{type}[/bright_white]\n")

        # list nature
        # pass for now

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
        self.clearTerminal()

        #moves
        self.console.print(
            f"[bright_black]Summary[/bright_black]"
            f"             "
            f"[bold bright_white]Moves[/bold bright_white] <-\n")

    def openMoveSummary(self):
        self.state = "move"
        self.drawMoveSummary()

    def closeMoveSummary(self):
        self.openPartySummary()
    
    def moveMoveSummary(self, key):
        if key in ('a', keyboard.Key.left):
            self.openCritterSummary()
