import csv
from crittermon.paths import csvPath

class Move:

    def __init__(self, name):
        self.name = name

        with open(csvPath("metadata_pokemon_moves.cvs"), newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["name"].lower() == name.lower(): 
                    self.accuracy = int(row["accuracy"])
                    self.pp = int(row["pp"])
                    self.power = int(row["power"])
                    self.priority = int(row["priority"])
                    self.type = row["type"]
                    self.category = row["damage_class"]
                    break
            else:
                raise ValueError(f"Move '{name}' not found in metadata_pokemon_moves.csv")
                
            
                    
                    
                    

