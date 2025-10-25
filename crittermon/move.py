import csv
from crittermon.paths import csvPath

class Move:

    def __init__(self, name):
        if name:
            with open(csvPath("metadata_pokemon_moves.csv"), newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row["name"].lower() == name.lower(): 
                        self.name = row["name"]
                        self.accuracy = float(row["accuracy"]) if row["accuracy"] else '-'
                        self.pp = int(row["pp"])
                        self.power = float(row["power"]) if row["power"] else '-'
                        self.priority = int(row["priority"])
                        self.type = row["type"]
                        self.category = row["damage_class"]
                        break
                else:
                    raise ValueError(f"Move '{name}' not found in metadata_pokemon_moves.csv")
                
                self.cur_pp = self.pp
        else:
            self.name = "Empty"
            self.accuracy = '-'
            self.pp = '0'
            self.power = '-'
            self.priority = '-'
            self.type = '-'
            self.category = '-'
            self.cur_pp = '0'

            
                    
                    
                    

