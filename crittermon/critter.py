import csv
from random import randint
from math import floor

from crittermon.paths import csvPath

class Critter:

    def __init__(self, name: str, nickname="", nature=["Attack", "Attack"], shiny=False):
        self.name = name
        if nickname:
            self.nickname = nickname
        else:
            self.nickname = name
        self.nature = nature

        self.evs = {
            "hp": 0,
            "attack": 0,
            "sp_attack": 0,
            "defense": 0,
            "sp_defense": 0,
            "speed": 0
        }

        self.ivs = {
            "hp": randint(0, 31),
            "attack": randint(0, 31),
            "sp_attack": randint(0, 31),
            "defense": randint(0, 31),
            "sp_defense": randint(0, 31),
            "speed": randint(0, 31)
            }
        
        self.shiny = shiny
        self.level = 100
        
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
        
        return returned_stat
