import random


class Agent:
    def __init__(self, name):
        self.name = name

        self.hunger = random.randint(20, 40)
        self.energy = random.randint(60, 100)
        self.social = random.randint(40, 80)

        self.location = "Camp"

        self.curiosity = random.randint(1, 100)
        self.kindness = random.randint(1, 100)
        self.aggression = random.randint(1, 100)

    def update_needs(self):
        self.hunger += 5
        self.energy -= 3
        self.social -= 2

        self.hunger = min(self.hunger, 100)
        self.energy = max(self.energy, 0)
        self.social = max(self.social, 0)

    def choose_action(self):

        if self.hunger > 70:
            return "gather food"

        if self.energy < 30:
            return "sleep"

        if self.social < 30:
            return "talk"

        return random.choice([
            "explore",
            "rest",
            "observe",
            "walk"
        ])