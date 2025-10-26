import csv
import ast

from typing import Literal
from random import randint
from random import choice
from math import floor
from math import cbrt

from crittermon.infoMessage import message
from crittermon.paths import csvPath
from crittermon.move import Move

Nature = Literal[
    "Adamant", "Bashful", "Bold", "Brave",
    "Calm", "Careful", "Docile", "Gentle",
    "Hardy", "Hasty", "Impish", "Jolly", "Lax",
    "Lonely", "Mild", "Modest", "Naive", "Naughty",
    "Quiet", "Quirky", "Rash", "Relaxed",
    "Sassy", "Serious", "Timid"
]

NATURES: dict[str, tuple[str, str]] = {
    "Adamant": ("attack", "sp_attack"),
    "Bashful": ("sp_attack", "sp_attack"),
    "Bold": ("defense", "attack"),
    "Brave": ("attack", "speed"),
    "Calm": ("sp_defense", "attack"),
    "Careful": ("sp_defense", "sp_attack"),
    "Docile": ("sp_attack", "sp_attack"),
    "Gentle": ("sp_defense", "defense"),
    "Hardy": ("attack", "attack"),
    "Hasty": ("speed", "defense"),
    "Impish": ("defense", "sp_attack"),
    "Jolly": ("speed", "sp_attack"),
    "Lax": ("defense", "sp_defense"),
    "Lonely": ("attack", "defense"),
    "Mild": ("sp_attack", "defense"),
    "Modest": ("sp_attack", "attack"),
    "Naive": ("speed", "sp_defense"),
    "Naughty": ("attack", "sp_defense"),
    "Quiet": ("sp_attack", "speed"),
    "Quirky": ("sp_attack", "sp_attack"),
    "Rash": ("sp_attack", "sp_defense"),
    "Relaxed": ("defense", "speed"),
    "Sassy": ("sp_defense", "speed"),
    "Serious": ("attack", "attack"),
    "Timid": ("speed", "attack"),
}

class Critter:

    def __init__(self,
                name: str,
                level: int,
                nickname: str="",
                nature: Nature="",
                evs: dict = {}, ivs: dict = {},
                shiny: bool=False,
                moves: list[str] = [None] * 4):
        
        # name
        self.name = name
        if nickname:
            self.nickname = nickname
        else:
            self.nickname = name

        #level
        self.level = level
        self.exp = level ** 3

        #nature
        if nature:
            self.nature = nature
        else:
            self.nature = choice(list(NATURES.keys()))

        #evs / ivs
        if evs:
            self.evs = evs
            self.total_evs = 0
            for ev in self.evs.keys:
                self.total_evs += self.evs[ev]
        else:
            self.total_evs = 0
            self.evs = {
                "hp": 0,
                "attack": 0,
                "sp_attack": 0,
                "defense": 0,
                "sp_defense": 0,
                "speed": 0
            }
        if ivs:
            self.ivs = ivs
        else:
            self.ivs = {
                "hp": randint(0, 31),
                "attack": randint(0, 31),
                "sp_attack": randint(0, 31),
                "defense": randint(0, 31),
                "sp_defense": randint(0, 31),
                "speed": randint(0, 31)
                }
        
        #shiny
        if not shiny:
            self.shiny = (randint(1, 999) == 1)
        else:
            self.shiny = shiny

        #moves
        self.moves = [None, None, None, None]
        for i, move in enumerate(moves):
            self.moves[i] = Move(move)
        
        #stats
        with open(csvPath("metadata_pokemon.csv"), newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if (row["name"] == self.name):
                    self.base_hp = int(row["hp"])
                    self.base_attack = int(row["attack"])
                    self.base_sp_attack = int(row["special_attack"])
                    self.base_defense = int(row["defense"])
                    self.base_sp_defense = int(row["special_defense"])
                    self.base_speed = int(row["speed"])

                    self.type = [row["type_1"], row["type_2"]]
                    if self.type[1] == '':
                        self.type[1] = None
                    break
            else:
                raise ValueError(f"Pokemon '{name}' not found in metadata_pokemon.csv")
        
        self.hp = self.getStat("hp")
        self.attack = self.getStat("attack")
        self.sp_attack = self.getStat("sp_attack")
        self.defense = self.getStat("defense")
        self.sp_defense = self.getStat("sp_defense")
        self.speed = self.getStat("speed")

        #exp and ev yield when killed
        with open(csvPath("pokemon_exp_ev_yield.csv"), newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if (row["name"] == self.name):
                    self.base_exp_yield = int(row["base_exp"]) 
                    self.ev_yield = ast.literal_eval(row["evs"]) 
                    self.ev_yield = [int(i) for i in self.ev_yield] #converts strings to int

        self.current_hp = self.hp
        self.fainted = False
    
    def getStat(self, stat):
        temp = stat
        stat = "base_" + stat

        returned_stat = 0
        base_stat = getattr(self, stat) #gets self.stat

        stat = temp

        if stat == "hp":
            returned_stat = floor((2 * base_stat + self.ivs[stat] + floor(self.evs[stat])) * self.level / 100) + self.level + 10
        else:
            returned_stat = floor((2 * base_stat + self.ivs[stat] + floor(self.evs[stat])) * self.level / 100) + 5
        
        nature = NATURES.get(self.nature)
        if (nature[0] == nature[1]):
            return returned_stat
        else:
            if nature[0] == stat:
                returned_stat = floor(returned_stat * 1.10)
            elif nature[1] == stat:
                returned_stat = floor(returned_stat * 0.90)

        return returned_stat
    
    def getName(self):
        if self.fainted:
            if self.shiny:
                return f"[red1]{self.nickname} ✦[/red1]"
            else:
                return f"[red1]{self.nickname}[/red1]"
        else:
            if self.shiny:
                return f"[yellow1]{self.nickname} ✦[/yellow1]"
            else:
                return self.nickname

    def hasFainted(self):
        self.current_hp = 0
        self.fainted = True
    
    def heal(self):
        pass

    def fullHeal(self):
        pass

    def revive(self):
        pass
    
    def gainEVS(self, evs):
        if self.total_evs < 510:
            for i, ev in enumerate(evs):
                match i:
                    case 0:
                        if self.evs["hp"] < 252:
                            self.evs["hp"] += ev
                    case 1:
                        if self.evs["attack"] < 252:
                            self.evs["attack"] += ev
                    case 2:
                        if self.evs["defense"] < 252:
                            self.evs["defense"] += ev
                    case 3:
                        if self.evs["sp_attack"] < 252:
                            self.evs["sp_attack"] += ev
                    case 4:
                        if self.evs["sp_defense"] < 252:
                            self.evs["sp_defense"] += ev
                    case 5:
                        if self.evs["speed"] < 252:
                            self.evs["speed"] += ev

    def gainEXP(self, exp):
        if self.level != 100:
            self.exp += exp
            if self.exp > 1000000:
                self.exp = 1000000

            old_level = self.level
            if old_level != floor(cbrt(self.exp)):
                self.levelUp(floor(cbrt(self.exp)))
    
    def levelUp(self, new_level):
        self.level = new_level
        message(f"[bold]{self.getName()}[/bold] has leveled up to level [bold]{self.level}[/bold]")


        
        
