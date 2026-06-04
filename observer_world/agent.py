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

        self.memories = []
        self.relationships = {}

    def update_needs(self):
        self.hunger = min(self.hunger + 5, 100)
        self.energy = max(self.energy - 3, 0)
        self.social = max(self.social - 2, 0)

    def remember(self, memory):
        self.memories.append(memory)

        if len(self.memories) > 10:
            self.memories.pop(0)

    def get_trust(self, other_name):
        return self.relationships.get(other_name, 0)

    def change_trust(self, other_name, amount):
        current = self.relationships.get(other_name, 0)
        self.relationships[other_name] = max(-100, min(100, current + amount))

    def choose_action(self):
        if self.hunger > 70:
            return "gather food"

        if self.energy < 30:
            return "sleep"

        if self.social < 35:
            return "talk"

        return random.choice([
            "explore",
            "rest",
            "observe",
            "walk",
            "talk"
        ])