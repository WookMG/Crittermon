import csv
from typing import Literal
from random import randint
from random import choice
from math import floor

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

        #nature
        if nature:
            self.nature = nature
        else:
            self.nature = choice(list(NATURES.keys()))

        #evs / ivs
        if evs:
            self.evs = evs
        else:
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

        self.current_hp = self.hp
    
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
        
        
