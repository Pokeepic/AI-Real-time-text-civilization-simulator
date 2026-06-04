import random

from utils import clamp
from config import CONFIG


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
            "medicine": random.randint(1, 5),
            "combat": random.randint(1, 5),
        }

        self.memories = []
        self.relationships = {}
        self.role = "Wanderer"
        self.health = 100
        self.alive = True
        self.status = "Healthy"
        self.age = random.randint(18, 40)
        self.partner = None
        self.family = []
        self.pregnant = False
        self.pregnancy_timer = 0
        self.parents = []
        self.generation = 1
        self.inventory = {
            "food": random.randint(0, 5),
            "wood": random.randint(0, 3),
            "stone": random.randint(0, 2)
        }
        self.wealth = 0
        self.debts = {}
        self.risk_taking = random.randint(1, 100)
        self.greed = random.randint(1, 100)
        self.faction = None
        self.journal = []
        self.life_goal = None
        self.completed_goals = []

    def update_needs(self):
        self.hunger = clamp(self.hunger + 5, 0, 100)
        self.energy = clamp(self.energy - 3, 0, 100)
        self.social = clamp(self.social - 2, 0, 100)

        if self.hunger >= 95:
            self.health = max(self.health - 5, 0)

        if self.energy <= 5:
            self.health = max(self.health - 2, 0)

        if self.health <= 0:
            self.alive = False
            self.status = "Dead"
        elif self.health < 30:
            self.status = "Critical"
        elif self.health < 60:
            self.status = "Injured"
        else:
            self.status = "Healthy"

    def remember(self, memory):
        self.memories.append(memory)

        if len(self.memories) > CONFIG["max_memories"]:
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
        rel[key] = clamp(rel[key] + amount, -100, 100)

    def improve_skill(self, skill, amount=1):
        self.skills[skill] = min(100, self.skills[skill] + amount)

    def choose_action(self, hour):
        if self.age < 6:
            return random.choice(["rest", "observe"])

        if self.age < 13:
            return random.choice(["observe", "learn", "talk", "rest"])

        if self.age < 18:
            return random.choice(["learn", "practice", "help", "talk"])

        if self.hunger > 70:
            return "gather food"

        if self.energy < 30:
            return "sleep"

        if self.social < 35:
            return "talk"

        # Night behavior
        if hour >= 22 or hour <= 5:
            if self.energy < 80:
                return "sleep"
            return random.choice(["rest", "observe"])

        # Morning behavior
        if 6 <= hour <= 11:
            if self.role == "Hunter":
                return random.choice(["gather food", "explore"])
            if self.role == "Builder":
                return random.choice(["gather materials", "build"])
            if self.role == "Farmer":
                return random.choice(["gather food", "observe"])

        # Afternoon behavior
        if 12 <= hour <= 17:
            if self.role == "Teacher":
                return "talk"
            if self.role == "Mediator":
                return random.choice(["talk", "help"])
            if self.role == "Guard":
                return random.choice(["patrol", "observe", "help"])
            if self.role == "Medic":
                return random.choice(["heal", "help", "observe"])
            if self.role == "Leader":
                return random.choice(["observe", "talk", "help"])

        # Evening behavior
        if 18 <= hour <= 21:
            return random.choice(["talk", "rest", "observe"])

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

        if self.role == "Guard":
            choices += ["patrol", "observe", "help"]

        if self.role == "Teacher":
            choices += ["talk", "practice", "help", "talk"]

        if self.role == "Leader":
            choices += ["talk", "help", "observe"]

        if self.role == "Medic":
            choices += ["heal", "help", "observe"]

        if self.role == "Merchant":
            choices += ["trade", "talk", "observe"]

        if self.social < 60 and self.age >= 18:
            choices += ["trade"]

        if self.age >= 18 and self.risk_taking > 65:
            choices += ["gamble"]

        if self.age >= 18 and self.greed > 70:
            choices += ["gamble", "trade"]

        if self.age >= 18 and self.debts:
            choices += ["repay debt"]

        if self.age >= 18 and self.greed > 60:
            choices += ["demand debt"]

        if self.age >= 18 and self.aggression > 90 and self.kindness < 30:
            choices += ["severe violence"]

        if self.social < 50 and self.kindness > 50:
            choices += ["bond"]

        if self.life_goal == "become leader":
            choices += ["talk", "help", "observe"]

        if self.life_goal == "become wealthy":
            choices += ["trade", "gamble"]

        if self.life_goal == "become great healer":
            choices += ["heal", "help"]

        if self.life_goal == "seek knowledge":
            choices += ["learn", "practice", "talk"]

        if self.life_goal == "become protector":
            choices += ["patrol", "practice"]

        if self.life_goal == "protect family":
            choices += ["help", "gather food", "talk"]

        if self.life_goal == "seek revenge":
            choices += ["argue", "fight"]

        return random.choice(choices)

    def write_journal(self, day, hour, thought):
        entry = f"Day {day}, {hour}:00 — {thought}"
        self.journal.append(entry)

        if len(self.journal) > CONFIG["max_journal_entries"]:
            self.journal.pop(0)