import random

from config import CONFIG
from utils import clamp


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
        self.known_best_friend = None
        self.known_rival = None
        self.wealth = 0
        self.debts = {}
        self.risk_taking = random.randint(1, 100)
        self.greed = random.randint(1, 100)
        self.faction = None
        self.journal = []
        self.life_goal = None
        self.completed_goals = []
        self.grudges = {}
        self.bonds = {}
        self.gossip_memory = []
        self.location_affinity = {}
        self.emotional_state = "Stable"
        self.emotion_history = []

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
    
    def get_best_friend(self):
        if not self.relationships:
            return None

        best_name = None
        best_score = -999

        for name, rel in self.relationships.items():
            score = (
                rel.get("trust", 0)
                + rel.get("friendship", 0)
                + rel.get("respect", 0)
                - rel.get("fear", 0)
            )

            if score > best_score:
                best_score = score
                best_name = name

        if best_score <= 0:
            return None

        return best_name


    def get_rival(self):
        if not self.relationships:
            return None

        rival_name = None
        worst_score = 999

        for name, rel in self.relationships.items():
            score = (
                rel.get("trust", 0)
                + rel.get("friendship", 0)
                + rel.get("respect", 0)
                - rel.get("fear", 0)
            )

            if score < worst_score:
                worst_score = score
                rival_name = name

        if worst_score >= 0:
            return None

        return rival_name

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

        if self.grudges and self.age >= 18:
            choices += ["argue"]

            if self.aggression > 60:
                choices += ["fight"]
        
        if self.bonds and self.age >= 13:
            choices += ["help", "talk"]

            if self.role == "Medic":
                choices += ["heal"]

            if self.role == "Teacher":
                choices += ["talk"]
        
        if self.get_favorite_place() and self.energy > 40:
            choices += ["visit favorite place"]

        if self.emotional_state == "Lonely":
            choices += ["talk", "bond"]

        elif self.emotional_state == "Connected":
            choices += ["help", "talk"]

        elif self.emotional_state == "Troubled":
            choices += ["argue"]

            if self.aggression > 60:
                choices += ["fight"]

        elif self.emotional_state == "Desperate":
            choices += ["gather food"]

            if self.kindness < 40:
                choices += ["steal food"]

        elif self.emotional_state == "Suffering":
            choices += ["rest", "sleep"]

        return random.choice(choices)

    def write_journal(self, day, hour, thought):
        entry = f"Day {day}, {hour}:00 — {thought}"
        self.journal.append(entry)

        if len(self.journal) > CONFIG["max_journal_entries"]:
            self.journal.pop(0)
    
    def add_grudge(self, other_name, reason):
        if other_name not in self.grudges:
            self.grudges[other_name] = []

        self.grudges[other_name].append(reason)

        if len(self.grudges[other_name]) > 5:
            self.grudges[other_name].pop(0)
    
    def add_bond(self, other_name, reason):
        if other_name not in self.bonds:
            self.bonds[other_name] = []

        self.bonds[other_name].append(reason)

        if len(self.bonds[other_name]) > 5:
            self.bonds[other_name].pop(0)
        
    def add_gossip(self, gossip):
        self.gossip_memory.append(gossip)

        if len(self.gossip_memory) > 10:
            self.gossip_memory.pop(0)

    def add_location_affinity(self, location, amount=1):
        self.location_affinity[location] = self.location_affinity.get(location, 0) + amount


    def get_favorite_place(self):
        if not self.location_affinity:
            return None

        return max(self.location_affinity, key=self.location_affinity.get)
    
    def update_emotional_state(self):
        if not self.alive:
            self.emotional_state = "Dead"
            return

        if self.health < 35:
            self.emotional_state = "Suffering"
        elif self.hunger > 85:
            self.emotional_state = "Desperate"
        elif self.get_rival():
            self.emotional_state = "Troubled"
        elif self.get_best_friend() or self.partner:
            self.emotional_state = "Connected"
        elif self.social < 25:
            self.emotional_state = "Lonely"
        else:
            self.emotional_state = "Stable"
    
    def set_emotion(self, emotion):
        if self.emotional_state != emotion:
            self.emotion_history.append(emotion)

            if len(self.emotion_history) > 10:
                self.emotion_history.pop(0)

        self.emotional_state = emotion
    
    def get_social_score(self):
        if not self.relationships:
            return 0

        total = 0

        for rel in self.relationships.values():
            total += (
                rel.get("trust", 0)
                + rel.get("friendship", 0)
                + rel.get("respect", 0)
                - rel.get("fear", 0)
            )

        return total