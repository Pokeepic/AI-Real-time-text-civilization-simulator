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
        self.discipline = random.randint(1, 100)
        self.pride = random.randint(1, 100)

        self.skills = {
            "hunting": random.randint(1, 5),
            "building": random.randint(1, 5),
            "farming": random.randint(1, 5),
            "social": random.randint(1, 5),
            "teaching": random.randint(1, 5),
        }

        self.memories = []
        self.relationships = {}
        self.role = "Wanderer"

    def update_needs(self):
        self.hunger = min(self.hunger + 5, 100)
        self.energy = max(self.energy - 3, 0)
        self.social = max(self.social - 2, 0)

    def remember(self, memory):
        self.memories.append(memory)

        if len(self.memories) > 15:
            self.memories.pop(0)

    def get_relationship(self, other_name):
        if other_name not in self.relationships:
            self.relationships[other_name] = {
                "trust": 0,
                "friendship": 0,
                "respect": 0,
                "fear": 0
            }

        return self.relationships[other_name]

    def change_relationship(self, other_name, key, amount):
        rel = self.get_relationship(other_name)
        rel[key] = max(-100, min(100, rel[key] + amount))

    def improve_skill(self, skill, amount=1):
        self.skills[skill] = min(100, self.skills[skill] + amount)

    def choose_action(self):
        if self.hunger > 70:
            return "gather food"

        if self.energy < 30:
            return "sleep"

        if self.social < 35:
            return "talk"

        choices = ["rest", "observe", "walk", "talk"]

        if self.curiosity > 60:
            choices += ["explore", "explore"]

        if self.discipline > 60:
            choices += ["practice", "gather food"]

        if self.kindness > 65:
            choices += ["talk", "help"]

        if self.aggression > 70:
            choices += ["argue"]

        if self.skills["building"] >= 3 or self.discipline > 55:
            choices += ["gather materials", "build"]

        if self.hunger > 60 and self.kindness < 40:
            choices += ["steal food"]

        if self.aggression > 75:
            choices += ["fight"]

        if self.role == "Hunter":
            choices += ["gather food", "gather food"]

        if self.role == "Builder":
            choices += ["gather materials", "build"]

        if self.role == "Farmer":
            choices += ["gather food", "observe"]

        if self.role == "Mediator":
            choices += ["talk", "help"]

        if self.role == "Teacher":
            choices += ["talk", "practice"]

        if self.role == "Leader":
            choices += ["talk", "help", "observe"]

        return random.choice(choices)