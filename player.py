from critter import Critter
class Player:

    def __init__(self, player_pos, name, party=[None, None, None, None, None, None]):
        self.player_pos = player_pos
        self.name = name

        self.party = party
    
    def addCritter(self, critter: Critter):
        for i in range(len(self.party)):
            if not self.party[i]:
                self.party[i] = critter
                break
        else:
            raise ValueError("Party Full")

    def removeCritter(self, party_slot):
        self.party[party_slot] = None