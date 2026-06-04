import random

from world import LOCATIONS
from dialogue import get_line
from config import CONFIG, get_setting, get_scenario, ACTIVE_SCENARIO
from utils import find_agent, clamp


class Simulation:
    def __init__(self, agents):
        self.agents = agents
        self.day = 1
        self.hour = 8
        self.world_history = []
        self.resources = {
            "food": 0,
            "wood": 0,
            "stone": 0
        }

        scenario = get_scenario()

        self.resources["food"] = scenario.get("starting_food", self.resources["food"])
        self.resources["wood"] = scenario.get("starting_wood", self.resources["wood"])
        self.resources["stone"] = scenario.get("starting_stone", self.resources["stone"])
        self.village_tension = scenario.get("starting_tension", 0)
        self.scenario = ACTIVE_SCENARIO

        self.settlement = {
            "name": None,
            "buildings": [],
            "shelter_progress": 0
        }
        
        self.laws = []
        self.crime_records = {}
        self.leader = None
        self.weather = "Clear"
        self.season = "Spring"
        self.death_records = []
        self.memorials = []
        self.current_project = None
        self.milestones = set()
        self.settlement_stage = "Camp"
        self.culture = {
            "cooperation": 0,
            "fear": 0,
            "discipline": 0,
            "violence": 0,
            "knowledge": 0,
            "trade": 0
        }
        self.traditions = []
        self.beliefs = {
            "nature_spirits": 0,
            "ancestor_memory": 0,
            "leader_destiny": 0,
            "healing_faith": 0,
            "strength_worship": 0
        }
        self.factions = {}
        self.faction_conflicts = []
        self.rebellions = []
        self.extra_settlements = []
        self.wars = []
        self.treaties = []
        self.technologies = []
        self.research_points = 0
        self.daily_events = []
        self.chronicles = []
        self.current_era = "Age of Survival"
        self.eras = [
            {
                "name": "Age of Survival",
                "start_day": 1
            }
        ]
        self.world_state = "Ongoing"
        self.collapse_reasons = []
        self.world_name = self.generate_world_name()

    def generate_world_name(self):
        prefixes = ["Eld", "Aru", "Nora", "Vey", "Sol", "Mira", "Kael", "Orin"]
        suffixes = ["mere", "vale", "reach", "hollow", "fall", "spire", "wood", "heim"]

        return random.choice(prefixes) + random.choice(suffixes)

    def generate_settlement_name(self):
        first = ["First", "Old", "New", "Stone", "River", "Ash", "Sun", "Moon"]
        second = ["Hearth", "Hollow", "Rest", "Crossing", "Gate", "Field", "Watch"]

        return random.choice(first) + " " + random.choice(second)

    def is_extra_settlement_location(self, location):
        return any(s["name"] == location for s in self.extra_settlements)

    def get_extra_settlement_by_name(self, name):
        return next(
            (s for s in self.extra_settlements if s["name"] == name),
            None
        )

    def get_first_extra_settlement(self):
        if not self.extra_settlements:
            return None

        return self.extra_settlements[0]

    def unlock_milestone(self, key, text, logs):
        if key in self.milestones:
            return

        self.milestones.add(key)
        logs.append(f"MILESTONE UNLOCKED: {text}")
        self.add_history(f"Milestone unlocked: {text}")

    def update_culture(self, logs):
        if self.hour != 20:
            return

        alive = [a for a in self.agents if a.alive and a.location != "Exiled Lands"]

        if not alive:
            return

        avg_kindness = sum(a.kindness for a in alive) / len(alive)
        avg_aggression = sum(a.aggression for a in alive) / len(alive)
        avg_discipline = sum(a.discipline for a in alive) / len(alive)

        teachers = len([a for a in alive if a.role == "Teacher"])
        merchants = len([a for a in alive if a.role == "Merchant"])
        guards = len([a for a in alive if a.role == "Guard"])

        if avg_kindness > 55:
            self.culture["cooperation"] += 1

        if avg_aggression > 60 or self.village_tension > 60:
            self.culture["violence"] += 1

        if avg_discipline > 55:
            self.culture["discipline"] += 1

        if teachers > 0:
            self.culture["knowledge"] += teachers

        if merchants > 0:
            self.culture["trade"] += merchants

        if guards > 0 and self.village_tension > 30:
            self.culture["fear"] += guards

        dominant = max(self.culture, key=self.culture.get)

        if self.culture[dominant] > 0:
            logs.append(f"The culture of {self.settlement['name'] or 'the camp'} is slowly leaning toward {dominant}.")

    def get_culture_identity(self):
        dominant = max(self.culture, key=self.culture.get)

        if self.culture[dominant] < 10:
            return "Undefined"

        identities = {
            "cooperation": "Cooperative Society",
            "fear": "Fear-Driven Society",
            "discipline": "Disciplined Society",
            "violence": "Violent Society",
            "knowledge": "Knowledge-Seeking Society",
            "trade": "Trade-Oriented Society"
        }

        return identities.get(dominant, "Undefined")

    def create_tradition(self, logs):
        if self.hour != 21:
            return

        identity = self.get_culture_identity()

        if identity == "Undefined":
            return

        if len(self.traditions) >= 3:
            return

        tradition_map = {
            "Cooperative Society": "Sharing Feast",
            "Fear-Driven Society": "Night Watch",
            "Disciplined Society": "Training Day",
            "Violent Society": "Trial of Strength",
            "Knowledge-Seeking Society": "Story Circle",
            "Trade-Oriented Society": "Market Day"
        }

        tradition = tradition_map.get(identity)

        if tradition and tradition not in self.traditions:
            self.traditions.append(tradition)
            logs.append(f"New tradition created: {tradition}.")
            self.add_history(f"A new tradition began: {tradition}.")

    def run_traditions(self, logs):
        if self.day % 7 != 0 or self.hour != 18:
            return

        for tradition in self.traditions:
            logs.append(f"Tradition held: {tradition}.")

            if tradition == "Sharing Feast":
                if self.resources["food"] >= 20:
                    self.resources["food"] -= 20
                    self.village_tension = clamp(self.village_tension - 15, 0, 100)

                    for agent in self.agents:
                        if agent.alive and agent.location != "Exiled Lands":
                            agent.social = min(agent.social + 20, 100)

                    logs.append("The Sharing Feast reduced tension and raised social bonds.")
                else:
                    logs.append("The Sharing Feast failed because there was not enough food.")
                    self.village_tension = clamp(self.village_tension + 8, 0, 100)

            elif tradition == "Night Watch":
                self.village_tension = clamp(self.village_tension - 8, 0, 100)

                for agent in self.agents:
                    if agent.alive and agent.role == "Guard":
                        agent.improve_skill("combat", 1)

                logs.append("The Night Watch made the settlement feel safer.")

            elif tradition == "Training Day":
                for agent in self.agents:
                    if agent.alive and agent.age >= 13 and agent.location != "Exiled Lands":
                        agent.discipline = min(agent.discipline + 1, 100)
                        agent.improve_skill("combat", 1)

                logs.append("Training Day improved discipline and combat readiness.")

            elif tradition == "Trial of Strength":
                fighters = [
                    a for a in self.agents
                    if a.alive and a.age >= 18 and a.location != "Exiled Lands"
                ]

                if len(fighters) >= 2:
                    winner = random.choice(fighters)
                    winner.improve_skill("combat", 2)
                    winner.wealth += 2
                    self.village_tension = clamp(self.village_tension + 5, 0, 100)
                    logs.append(f"{winner.name} won the Trial of Strength.")

            elif tradition == "Story Circle":
                for agent in self.agents:
                    if agent.alive and agent.age < 18 and agent.location != "Exiled Lands":
                        agent.improve_skill("teaching", 1)
                        agent.improve_skill("social", 1)

                logs.append("The Story Circle helped children learn from village stories.")

            elif tradition == "Market Day":
                for agent in self.agents:
                    if agent.alive and agent.age >= 13 and agent.location != "Exiled Lands":
                        agent.wealth += 1
                        agent.improve_skill("social", 1)

                logs.append("Market Day increased wealth and social skill.")

    def update_beliefs(self, logs):
        if self.hour != 22:
            return

        if self.weather in ["Storm", "Snow"]:
            self.beliefs["nature_spirits"] += 1

        if self.death_records:
            self.beliefs["ancestor_memory"] += 1

        if self.leader:
            self.beliefs["leader_destiny"] += 1

        if "Clinic" in self.settlement["buildings"]:
            self.beliefs["healing_faith"] += 1

        if "Trial of Strength" in self.traditions:
            self.beliefs["strength_worship"] += 1

        dominant = max(self.beliefs, key=self.beliefs.get)

        if self.beliefs[dominant] > 5:
            logs.append(f"A shared belief is forming around {dominant.replace('_', ' ')}.")

    def get_belief_identity(self):
        dominant = max(self.beliefs, key=self.beliefs.get)

        if self.beliefs[dominant] < 8:
            return "None"

        names = {
            "nature_spirits": "Belief in Nature Spirits",
            "ancestor_memory": "Ancestor Reverence",
            "leader_destiny": "Chosen Leader Myth",
            "healing_faith": "Faith in Healers",
            "strength_worship": "Cult of Strength"
        }

        return names.get(dominant, "None")

    def update_factions(self, logs):
        if self.hour != 19:
            return

        if self.settlement["name"] is None:
            return

        alive = [
            a for a in self.agents
            if a.alive and a.location != "Exiled Lands" and a.age >= 13
        ]

        if len(alive) < 6:
            return

        possible_factions = []

        if self.leader:
            possible_factions.append(("Leader Loyalists", "loyalty"))

        if self.get_belief_identity() != "None":
            possible_factions.append(("Faith Circle", "belief"))

        if self.village_tension > 60:
            possible_factions.append(("Reform Seekers", "tension"))

        if any(a.wealth >= 5 for a in alive):
            possible_factions.append(("Trade Guild", "wealth"))

        if any(a.role == "Guard" for a in alive):
            possible_factions.append(("Watch Order", "guard"))

        for faction_name, reason in possible_factions:
            if faction_name not in self.factions:
                self.factions[faction_name] = {
                    "reason": reason,
                    "members": []
                }

                logs.append(f"New faction formed: {faction_name}.")
                self.add_history(f"Faction formed: {faction_name}.")

        for agent in alive:
            chosen_faction = None

            if self.leader:
                rel = agent.get_relationship(self.leader)

                if rel["trust"] > 20 or rel["respect"] > 20:
                    chosen_faction = "Leader Loyalists"

            if agent.role == "Guard" and "Watch Order" in self.factions:
                chosen_faction = "Watch Order"

            if agent.wealth >= 5 and "Trade Guild" in self.factions:
                chosen_faction = "Trade Guild"

            if self.get_belief_identity() != "None" and agent.kindness > 50:
                chosen_faction = "Faith Circle"

            if self.village_tension > 60 and agent.aggression > 50:
                chosen_faction = "Reform Seekers"

            agent.faction = chosen_faction

        for faction in self.factions.values():
            faction["members"] = []

        for agent in alive:
            if agent.faction and agent.faction in self.factions:
                self.factions[agent.faction]["members"].append(agent.name)

    def update_faction_influence(self, logs):
        if self.hour != 20:
            return

        if not self.factions:
            return

        for faction_name, data in self.factions.items():
            members = data["members"]

            if not members:
                data["influence"] = 0
                continue

            influence = len(members) * 5

            for member_name in members:
                member = next((a for a in self.agents if a.name == member_name), None)

                if not member:
                    continue

                influence += member.wealth
                influence += member.skills["social"]
                influence += member.skills["combat"] // 2

                if member.role == "Leader":
                    influence += 15

                if member.role == "Guard":
                    influence += 8

                if member.role == "Merchant":
                    influence += 6

            data["influence"] = influence

            if influence >= 40:
                logs.append(f"{faction_name} has become influential.")

            if influence >= 70:
                logs.append(f"{faction_name} is now a major power in the settlement.")

    def handle_faction_conflict(self, logs):
        if self.hour != 21:
            return

        if len(self.factions) < 2:
            return

        active_factions = [
            (name, data) for name, data in self.factions.items()
            if data.get("members")
        ]

        if len(active_factions) < 2:
            return

        faction_a, data_a = random.choice(active_factions)
        faction_b, data_b = random.choice([
            item for item in active_factions
            if item[0] != faction_a
        ])

        influence_gap = abs(data_a.get("influence", 0) - data_b.get("influence", 0))

        conflict_chance = 0.05
        conflict_chance += self.village_tension / 300

        if data_a["reason"] != data_b["reason"]:
            conflict_chance += 0.05

        if random.random() > conflict_chance:
            return

        conflict = {
            "day": self.day,
            "hour": self.hour,
            "factions": [faction_a, faction_b],
            "reason": "influence dispute"
        }

        self.faction_conflicts.append(conflict)

        self.village_tension = min(self.village_tension + int(10 * get_setting("tension_multiplier")), 100)

        logs.append(f"Faction conflict erupted between {faction_a} and {faction_b}.")
        logs.append(f"Village tension increased to {self.village_tension}.")

        if influence_gap > 30:
            stronger = faction_a if data_a.get("influence", 0) > data_b.get("influence", 0) else faction_b
            logs.append(f"{stronger} dominated the dispute through influence.")
        else:
            logs.append("Neither faction gained clear control from the dispute.")

        self.add_history(f"Faction conflict: {faction_a} vs {faction_b}.")

    def handle_rebellion(self, logs):
        if self.hour != 22:
            return

        if not self.leader:
            return

        if self.village_tension < 70:
            return

        rebel_factions = [
            (name, data) for name, data in self.factions.items()
            if data.get("members")
            and name != "Leader Loyalists"
            and data.get("influence", 0) >= 50
        ]

        if not rebel_factions:
            return

        faction_name, faction_data = random.choice(rebel_factions)

        leader = next((a for a in self.agents if a.name == self.leader), None)

        if not leader:
            return

        rebellion_power = faction_data.get("influence", 0) + self.village_tension

        loyalist_power = 0

        if "Leader Loyalists" in self.factions:
            loyalist_power += self.factions["Leader Loyalists"].get("influence", 0)

        loyalist_power += leader.skills["social"] * 3
        loyalist_power += leader.skills["combat"] * 2
        loyalist_power += leader.discipline

        logs.append(f"Rebellion began against leader {self.leader}.")
        logs.append(f"Rebel faction: {faction_name}.")

        rebellion_record = {
            "day": self.day,
            "hour": self.hour,
            "against": self.leader,
            "faction": faction_name
        }

        self.rebellions.append(rebellion_record)

        if rebellion_power > loyalist_power:
            old_leader = self.leader

            possible_new_leaders = [
                a for a in self.agents
                if a.name in faction_data["members"] and a.alive
            ]

            if possible_new_leaders:
                new_leader = max(
                    possible_new_leaders,
                    key=lambda a: a.skills["social"] + a.skills["combat"] + a.discipline
                )

                self.leader = new_leader.name
                new_leader.role = "Leader"

                leader.change_relationship(new_leader.name, "trust", -30)
                new_leader.change_relationship(leader.name, "trust", -30)

                self.village_tension = max(self.village_tension - 25, 0)

                logs.append(f"The rebellion succeeded.")
                logs.append(f"{old_leader} was overthrown.")
                logs.append(f"{new_leader.name} became the new leader.")

                self.add_history(f"{old_leader} was overthrown by {new_leader.name} of {faction_name}.")
            else:
                logs.append("The rebellion succeeded, but no clear leader emerged.")
                self.leader = None
                self.village_tension = min(self.village_tension + 10, 100)
        else:
            self.village_tension = max(self.village_tension - 10, 0)

            logs.append("The rebellion failed.")
            logs.append(f"{self.leader} remained in power.")

            for member_name in faction_data["members"]:
                rebel = next((a for a in self.agents if a.name == member_name), None)

                if rebel and rebel.alive:
                    rebel.change_relationship(self.leader, "fear", 10)
                    rebel.change_relationship(self.leader, "trust", -10)

            self.add_history(f"A rebellion by {faction_name} against {self.leader} failed.")

    def handle_exile_settlements(self, logs):
        if self.hour != 12:
            return

        exiles = [
            a for a in self.agents
            if a.alive and a.location == "Exiled Lands"
        ]

        if len(exiles) < 3:
            return

        if len(self.extra_settlements) >= 1:
            return

        settlement_name = self.generate_settlement_name()

        founder = max(
            exiles,
            key=lambda a: a.skills["social"] + a.discipline + a.aggression
        )

        new_settlement = {
            "name": settlement_name,
            "founder": founder.name,
            "leader": founder.name,
            "population": len(exiles),
            "stage": "Camp",
            "tension": 30,
            "relationship_to_main": -20,
            "resources": {
                "food": 20,
                "wood": 10,
                "stone": 5
            },
            "buildings": [],
            "laws": [],
            "culture": {
                "cooperation": 0,
                "fear": 0,
                "discipline": 0,
                "violence": 0,
                "knowledge": 0,
                "trade": 0
            },
            "technologies": [],
            "research_points": 0
        }

        self.extra_settlements.append(new_settlement)

        for exile in exiles:
            exile.location = settlement_name

        logs.append(f"The exiles founded a new camp: {settlement_name}.")
        logs.append(f"Founder: {founder.name}. Population: {len(exiles)}.")
        self.add_history(f"Exiles founded {settlement_name} under {founder.name}.")

    def get_agent_settlement(self, agent):
        return self.get_extra_settlement_by_name(agent.location)

    def handle_settlement_relations(self, logs):
        if self.hour != 15:
            return

        if not self.extra_settlements:
            return

        for settlement in self.extra_settlements:
            relation = settlement["relationship_to_main"]

            if relation >= 40:
                event = random.choice(["trade", "alliance"])
            elif relation <= -40:
                event = random.choice(["raid", "threat"])
            else:
                event = random.choice(["trade", "tension", "nothing"])

            if event == "trade":
                food_gain = random.randint(5, 15)
                self.resources["food"] += food_gain
                settlement["relationship_to_main"] += 5

                logs.append(f"{settlement['name']} traded with {self.settlement['name'] or 'the main camp'}.")
                logs.append(f"Main storage gained food +{food_gain}. Relations +5.")

            elif event == "alliance":
                settlement["relationship_to_main"] += 3
                self.village_tension = max(self.village_tension - 5, 0)

                logs.append(f"{settlement['name']} reaffirmed friendly ties with the main settlement.")
                logs.append("Village tension -5.")

            elif event == "raid":
                stolen_food = min(self.resources["food"], random.randint(5, 20))
                self.resources["food"] -= stolen_food
                settlement["relationship_to_main"] -= 5
                self.village_tension = min(self.village_tension + int(15 * get_setting("tension_multiplier")), 100)

                logs.append(f"{settlement['name']} raided the main settlement.")
                logs.append(f"Food stolen: {stolen_food}. Relations -5. Tension +15.")

                self.add_history(f"{settlement['name']} raided the main settlement.")

            elif event == "threat":
                settlement["relationship_to_main"] -= 3
                self.village_tension = min(self.village_tension + 8, 100)

                logs.append(f"{settlement['name']} sent threats to the main settlement.")
                logs.append("Relations -3. Village tension +8.")

            elif event == "tension":
                settlement["relationship_to_main"] -= 2

                logs.append(f"Tension grew between {settlement['name']} and the main settlement.")
                logs.append("Relations -2.")

    def handle_migration(self, logs):
        if self.hour != 10:
            return

        extra_settlement = self.get_first_extra_settlement()

        if not extra_settlement:
            return

        for agent in self.agents:
            if not agent.alive or agent.age < 18:
                continue

            if agent.location == "Exiled Lands":
                continue

            # Main settlement -> Extra settlement
            if not self.is_extra_settlement_location(agent.location):
                desire_to_leave = 0

                if self.village_tension > 70:
                    desire_to_leave += 30

                if self.leader:
                    rel = agent.get_relationship(self.leader)
                    if rel["fear"] > 30 or rel["trust"] < -30:
                        desire_to_leave += 20

                if agent.faction == "Reform Seekers":
                    desire_to_leave += 25

                if agent.greed > 70 and extra_settlement["relationship_to_main"] < 0:
                    desire_to_leave += 15

                if agent.partner:
                    desire_to_leave -= 10

                if random.randint(1, 100) < desire_to_leave:
                    agent.location = extra_settlement["name"]
                    extra_settlement["population"] += 1

                    logs.append(f"{agent.name} migrated to {extra_settlement['name']}.")
                    self.add_history(f"{agent.name} left the main settlement for {extra_settlement['name']}.")

            # Extra settlement -> Main settlement
            else:
                desire_to_return = 0

                if extra_settlement["relationship_to_main"] > 20:
                    desire_to_return += 20

                if agent.kindness > 70:
                    desire_to_return += 15

                if agent.family:
                    desire_to_return += 15

                if random.randint(1, 100) < desire_to_return:
                    agent.location = "Camp"
                    extra_settlement["population"] = max(0, extra_settlement["population"] - 1)

                    logs.append(f"{agent.name} returned from {extra_settlement['name']} to the main settlement.")
                    self.add_history(f"{agent.name} returned from {extra_settlement['name']}.")

    def handle_extra_settlement_growth(self, logs):
        if self.hour != 14:
            return

        for settlement in self.extra_settlements:
            resources = settlement.get("resources", {})
            buildings = settlement.get("buildings", [])

            population = len([
                a for a in self.agents
                if a.alive and a.location == settlement["name"]
            ])

            settlement["population"] = population

            if population <= 0:
                continue

            if "Shelter" not in buildings:
                project = "Shelter"
                wood_cost = 10
                stone_cost = 5

            elif "Farm" not in buildings:
                project = "Farm"
                wood_cost = 15
                stone_cost = 5

            elif "Guard Post" not in buildings and settlement["tension"] > 40:
                project = "Guard Post"
                wood_cost = 20
                stone_cost = 10

            else:
                continue

            if resources.get("wood", 0) >= wood_cost and resources.get("stone", 0) >= stone_cost:
                resources["wood"] -= wood_cost
                resources["stone"] -= stone_cost
                buildings.append(project)

                logs.append(f"{settlement['name']} completed a new building: {project}.")

                if project == "Shelter":
                    settlement["stage"] = "Settlement"
                    logs.append(f"{settlement['name']} is no longer just a camp.")

                elif project == "Farm":
                    resources["food"] += 20
                    logs.append(f"{settlement['name']}'s Farm produced food +20.")

                elif project == "Guard Post":
                    settlement["tension"] = max(settlement["tension"] - 15, 0)
                    logs.append(f"{settlement['name']}'s Guard Post reduced local tension.")

                self.add_history(f"{settlement['name']} built {project}.")

    def update_extra_settlement_leaders(self, logs):
        if self.hour != 18:
            return

        for settlement in self.extra_settlements:
            residents = [
                a for a in self.agents
                if a.alive
                and a.age >= 18
                and a.location == settlement["name"]
            ]

            if not residents:
                settlement["leader"] = None
                continue

            best_candidate = max(
                residents,
                key=lambda a: (
                    a.skills["social"] * 3
                    + a.skills["combat"] * 2
                    + a.discipline
                    + a.aggression // 2
                    + a.wealth
                )
            )

            old_leader = settlement.get("leader")

            if old_leader != best_candidate.name:
                settlement["leader"] = best_candidate.name
                logs.append(f"{best_candidate.name} became the leader of {settlement['name']}.")
                self.add_history(f"{best_candidate.name} became leader of {settlement['name']}.")

    def update_extra_settlement_culture(self, logs):
        if self.hour != 20:
            return

        for settlement in self.extra_settlements:
            residents = [
                a for a in self.agents
                if a.alive and a.location == settlement["name"]
            ]

            if not residents:
                continue

            avg_kindness = sum(a.kindness for a in residents) / len(residents)
            avg_aggression = sum(a.aggression for a in residents) / len(residents)
            avg_discipline = sum(a.discipline for a in residents) / len(residents)

            if avg_kindness > 55:
                settlement["culture"]["cooperation"] += 1

            if avg_aggression > 60 or settlement["tension"] > 60:
                settlement["culture"]["violence"] += 1

            if avg_discipline > 55:
                settlement["culture"]["discipline"] += 1

            if any(a.role == "Teacher" for a in residents):
                settlement["culture"]["knowledge"] += 1

            if any(a.role == "Merchant" for a in residents):
                settlement["culture"]["trade"] += 1

            if any(a.role == "Guard" for a in residents):
                settlement["culture"]["fear"] += 1

    def get_extra_settlement_culture_identity(self, settlement):
        culture = settlement.get("culture", {})

        if not culture:
            return "Undefined"

        dominant = max(culture, key=culture.get)

        if culture[dominant] < 10:
            return "Undefined"

        identities = {
            "cooperation": "Cooperative Society",
            "fear": "Fear-Driven Society",
            "discipline": "Disciplined Society",
            "violence": "Violent Society",
            "knowledge": "Knowledge-Seeking Society",
            "trade": "Trade-Oriented Society"
        }

        return identities.get(dominant, "Undefined")

    def update_extra_settlement_laws(self, logs):
        if self.hour != 21:
            return

        for settlement in self.extra_settlements:
            laws = settlement.get("laws", [])

            if settlement["tension"] > 60 and "No attacks inside the camp" not in laws:
                laws.append("No attacks inside the camp")
                logs.append(f'{settlement["name"]} created a law: "No attacks inside the camp".')
                self.add_history(f'{settlement["name"]} created law: No attacks inside the camp.')

            if settlement["resources"]["food"] < 10 and "Food must be rationed" not in laws:
                laws.append("Food must be rationed")
                logs.append(f'{settlement["name"]} created a law: "Food must be rationed".')
                self.add_history(f'{settlement["name"]} created law: Food must be rationed.')

    def calculate_settlement_power(self, settlement_name):
        residents = [
            a for a in self.agents
            if a.alive and a.location == settlement_name
        ]

        if settlement_name == "main":
            residents = [
                a for a in self.agents
                if a.alive and not self.is_extra_settlement_location(a.location) and a.location != "Exiled Lands"
            ]

        power = 0

        for agent in residents:
            power += agent.skills["combat"] * 3
            power += agent.discipline
            power += agent.health // 5

            if agent.role == "Guard":
                power += 15

            if agent.role == "Leader":
                power += 10

        return power

    def handle_diplomacy(self, logs):
        if self.hour != 16:
            return

        if not self.extra_settlements:
            return

        for settlement in self.extra_settlements:
            relation = settlement["relationship_to_main"]

            if relation < -30:
                diplomacy_chance = 0.08

                if self.leader:
                    leader = next((a for a in self.agents if a.name == self.leader), None)
                    if leader:
                        diplomacy_chance += leader.skills["social"] / 100

                if settlement.get("leader"):
                    other_leader = next((a for a in self.agents if a.name == settlement["leader"]), None)
                    if other_leader:
                        diplomacy_chance += other_leader.skills["social"] / 150

                if random.random() < diplomacy_chance:
                    treaty = {
                        "day": self.day,
                        "hour": self.hour,
                        "settlement": settlement["name"],
                        "type": "peace talks"
                    }

                    self.treaties.append(treaty)

                    relation_gain = random.randint(10, 25)
                    settlement["relationship_to_main"] += relation_gain
                    self.village_tension = max(self.village_tension - 10, 0)
                    settlement["tension"] = max(settlement["tension"] - 10, 0)

                    logs.append(f"Peace talks were held with {settlement['name']}.")
                    logs.append(f"Relations improved by {relation_gain}.")
                    logs.append("Tension decreased in both settlements.")

                    self.add_history(f"Peace talks improved relations with {settlement['name']}.")

            elif relation > 30:
                if random.random() < 0.05:
                    treaty = {
                        "day": self.day,
                        "hour": self.hour,
                        "settlement": settlement["name"],
                        "type": "friendship pact"
                    }

                    self.treaties.append(treaty)
                    settlement["relationship_to_main"] += 10

                    logs.append(f"{self.settlement['name'] or 'The main settlement'} and {settlement['name']} signed a friendship pact.")
                    self.add_history(f"Friendship pact signed with {settlement['name']}.")

    def handle_settlement_war(self, logs):
        if self.hour != 23:
            return

        for settlement in self.extra_settlements:
            relation = settlement["relationship_to_main"]

            if relation > -70:
                continue

            war_chance = 0.08
            war_chance += settlement["tension"] / 300
            war_chance += self.village_tension / 400

            recent_treaty = any(
                treaty["settlement"] == settlement["name"]
                and self.day - treaty["day"] <= 5
                for treaty in self.treaties
            )

            if recent_treaty:
                war_chance -= 0.05

            if random.random() > war_chance:
                continue

            main_power = self.calculate_settlement_power("main")
            other_power = self.calculate_settlement_power(settlement["name"])

            logs.append(f"War broke out between {self.settlement['name'] or 'the main settlement'} and {settlement['name']}.")
            logs.append(f"Main power: {main_power}. {settlement['name']} power: {other_power}.")

            war_record = {
                "day": self.day,
                "hour": self.hour,
                "enemy": settlement["name"],
                "main_power": main_power,
                "enemy_power": other_power
            }

            self.wars.append(war_record)

            if main_power >= other_power:
                logs.append(f"The main settlement defended itself successfully.")
                settlement["relationship_to_main"] += 20
                settlement["tension"] += 10
                self.village_tension = max(self.village_tension - 10, 0)

                self.apply_war_losses(settlement["name"], logs)

                self.add_history(f"The main settlement won a conflict against {settlement['name']}.")

            else:
                stolen_food = min(self.resources["food"], random.randint(20, 50))
                self.resources["food"] -= stolen_food
                self.village_tension = min(self.village_tension + int(20 * get_setting("tension_multiplier")), 100)
                settlement["relationship_to_main"] -= 10

                logs.append(f"{settlement['name']} overwhelmed the main settlement.")
                logs.append(f"Food lost: {stolen_food}.")

                self.apply_war_losses("main", logs)

                self.add_history(f"{settlement['name']} defeated the main settlement in conflict.")

    def apply_war_losses(self, settlement_name, logs):
        if settlement_name == "main":
            candidates = [
                a for a in self.agents
                if a.alive and not self.is_extra_settlement_location(a.location) and a.location != "Exiled Lands"
            ]
        else:
            candidates = [
                a for a in self.agents
                if a.alive and a.location == settlement_name
            ]

        if not candidates:
            return

        casualty_count = min(len(candidates), random.randint(0, 2))

        for _ in range(casualty_count):
            victim = random.choice(candidates)
            damage = random.randint(20, 60)

            victim.health = max(victim.health - damage, 0)

            logs.append(f"{victim.name} was injured during the conflict. Health -{damage}.")

            if victim.health <= 0:
                victim.alive = False
                victim.status = "Dead"
                logs.append(f"{victim.name} died from conflict injuries.")
                self.record_death(victim, "settlement conflict")

            candidates.remove(victim)

    def generate_research(self, logs):
        if self.hour != 17:
            return

        alive = [
            a for a in self.agents
            if a.alive and a.location != "Exiled Lands"
        ]

        if not alive:
            return

        points = 0

        for agent in alive:
            if agent.role == "Teacher":
                points += 2

            if agent.role == "Medic":
                points += 1

            if agent.role == "Builder":
                points += 1

            points += agent.skills["teaching"] // 5

        if self.get_culture_identity() == "Knowledge-Seeking Society":
            points += 5

        if "Story Circle" in self.traditions:
            points += 3

        self.research_points += points

        if points > 0:
            logs.append(f"The settlement generated {points} research points.")

    def unlock_technology(self, logs):
        tech_tree = [
            {
                "name": "Basic Tools",
                "cost": 30,
                "requirement": lambda: True
            },
            {
                "name": "Crop Rotation",
                "cost": 60,
                "requirement": lambda: "Farm" in self.settlement["buildings"]
            },
            {
                "name": "Herbal Medicine",
                "cost": 70,
                "requirement": lambda: "Clinic" in self.settlement["buildings"]
            },
            {
                "name": "Written Records",
                "cost": 90,
                "requirement": lambda: self.get_culture_identity() == "Knowledge-Seeking Society"
            },
            {
                "name": "Stone Construction",
                "cost": 120,
                "requirement": lambda: "Basic Tools" in self.technologies
            },
            {
                "name": "Council Governance",
                "cost": 150,
                "requirement": lambda: len(self.laws) >= 3
            }
        ]

        for tech in tech_tree:
            if tech["name"] in self.technologies:
                continue

            if self.research_points >= tech["cost"] and tech["requirement"]():
                self.research_points -= tech["cost"]
                self.technologies.append(tech["name"])

                logs.append(f"TECHNOLOGY UNLOCKED: {tech['name']}.")
                self.add_history(f"Technology unlocked: {tech['name']}.")

                return

    def generate_extra_settlement_research(self, logs):
        if self.hour != 17:
            return

        for settlement in self.extra_settlements:
            residents = [
                a for a in self.agents
                if a.alive and a.location == settlement["name"]
            ]

            if not residents:
                continue

            points = 0

            for agent in residents:
                if agent.role == "Teacher":
                    points += 2
                if agent.role == "Medic":
                    points += 1
                if agent.role == "Builder":
                    points += 1

                points += agent.skills["teaching"] // 5

            if self.get_extra_settlement_culture_identity(settlement) == "Knowledge-Seeking Society":
                points += 5

            settlement["research_points"] += points

            if points > 0:
                logs.append(f"{settlement['name']} generated {points} research points.")

    def unlock_extra_settlement_technology(self, logs):
        for settlement in self.extra_settlements:
            technologies = settlement.get("technologies", [])
            research_points = settlement.get("research_points", 0)
            buildings = settlement.get("buildings", [])

            tech_tree = [
                {
                    "name": "Basic Tools",
                    "cost": 30,
                    "requirement": lambda: True
                },
                {
                    "name": "Crop Rotation",
                    "cost": 60,
                    "requirement": lambda: "Farm" in buildings
                },
                {
                    "name": "Herbal Medicine",
                    "cost": 70,
                    "requirement": lambda: "Clinic" in buildings
                },
                {
                    "name": "Stone Construction",
                    "cost": 120,
                    "requirement": lambda: "Basic Tools" in technologies
                },
            ]

            for tech in tech_tree:
                if tech["name"] in technologies:
                    continue

                if research_points >= tech["cost"] and tech["requirement"]():
                    settlement["research_points"] -= tech["cost"]
                    settlement["technologies"].append(tech["name"])

                    logs.append(f'{settlement["name"]} unlocked technology: {tech["name"]}.')
                    self.add_history(f'{settlement["name"]} unlocked technology: {tech["name"]}.')

                    break

    def handle_journals(self, logs):
        if self.hour != 23:
            return

        for agent in self.agents:
            if not agent.alive:
                continue

            thought = None

            if agent.health < 40:
                thought = "I do not feel well. I wonder if I will survive much longer."

            elif agent.hunger > 80:
                thought = "Food has been on my mind all day."

            elif agent.partner:
                thought = f"I thought about {agent.partner} today."

            elif agent.memories:
                thought = f"I keep remembering: {agent.memories[-1]}"

            elif agent.faction:
                thought = f"My place in {agent.faction} may shape my future."

            elif agent.role == "Leader":
                thought = "Everyone looks to me, but leadership is heavier than it seems."

            if thought:
                agent.write_journal(self.day, self.hour, thought)
                logs.append(f"{agent.name} wrote a journal entry.")

    def handle_personality_drift(self, logs):
        if self.hour != 0:
            return

        for agent in self.agents:
            if not agent.alive:
                continue

            old_kindness = agent.kindness
            old_aggression = agent.aggression
            old_discipline = agent.discipline
            old_pride = agent.pride
            old_greed = agent.greed

            recent_memories = " ".join(agent.memories[-5:]).lower()

            if "helped" in recent_memories or "healed" in recent_memories:
                agent.kindness = min(agent.kindness + 1, 100)
                agent.aggression = max(agent.aggression - 1, 1)

            if "argued" in recent_memories or "fought" in recent_memories or "attacked" in recent_memories:
                agent.aggression = min(agent.aggression + 1, 100)
                agent.kindness = max(agent.kindness - 1, 1)

            if "taught" in recent_memories or "learned" in recent_memories:
                agent.curiosity = min(agent.curiosity + 1, 100)
                agent.discipline = min(agent.discipline + 1, 100)

            if "stole" in recent_memories or "gamble" in recent_memories:
                agent.greed = min(agent.greed + 1, 100)
                agent.discipline = max(agent.discipline - 1, 1)

            if agent.role == "Guard":
                agent.discipline = min(agent.discipline + 1, 100)

            if agent.role == "Leader":
                agent.pride = min(agent.pride + 1, 100)

            changed = []

            if agent.kindness != old_kindness:
                changed.append(f"kindness {old_kindness}->{agent.kindness}")

            if agent.aggression != old_aggression:
                changed.append(f"aggression {old_aggression}->{agent.aggression}")

            if agent.discipline != old_discipline:
                changed.append(f"discipline {old_discipline}->{agent.discipline}")

            if agent.pride != old_pride:
                changed.append(f"pride {old_pride}->{agent.pride}")

            if agent.greed != old_greed:
                changed.append(f"greed {old_greed}->{agent.greed}")

            if changed and random.random() < 0.25:
                logs.append(f"{agent.name}'s personality shifted: {', '.join(changed)}.")

    def assign_life_goal(self, agent):
        if agent.life_goal is not None:
            return

        possible_goals = []

        if agent.pride > 65 or agent.skills["social"] > 6:
            possible_goals.append("become leader")

        if agent.greed > 65:
            possible_goals.append("become wealthy")

        if agent.kindness > 70 and agent.skills["medicine"] >= 4:
            possible_goals.append("become great healer")

        if agent.curiosity > 70 or agent.skills["teaching"] >= 5:
            possible_goals.append("seek knowledge")

        if agent.aggression > 70 or agent.skills["combat"] >= 5:
            possible_goals.append("become protector")

        if agent.partner or agent.family:
            possible_goals.append("protect family")

        recent_memories = " ".join(agent.memories[-5:]).lower()

        if "attacked" in recent_memories or "fought" in recent_memories:
            possible_goals.append("seek revenge")

        if not possible_goals:
            possible_goals.append(random.choice([
                "live peacefully",
                "master a craft",
                "find belonging"
            ]))

        agent.life_goal = random.choice(possible_goals)

    def update_life_goals(self, logs):
        if self.hour != 7:
            return

        for agent in self.agents:
            if not agent.alive:
                continue

            self.assign_life_goal(agent)

            if random.random() < 0.05:
                old_goal = agent.life_goal
                agent.life_goal = None
                self.assign_life_goal(agent)

                if old_goal != agent.life_goal:
                    logs.append(f"{agent.name}'s life goal changed from {old_goal} to {agent.life_goal}.")
                    agent.write_journal(self.day, self.hour, f"My path feels different now. I want to {agent.life_goal}.")

    def check_goal_progress(self, logs):
        if self.hour != 8:
            return

        for agent in self.agents:
            if not agent.alive or not agent.life_goal:
                continue

            goal = agent.life_goal
            completed = False

            if goal == "become leader" and agent.role == "Leader":
                completed = True

            elif goal == "become wealthy" and agent.wealth >= 10:
                completed = True

            elif goal == "become great healer" and agent.skills["medicine"] >= 12:
                completed = True

            elif goal == "seek knowledge" and agent.skills["teaching"] >= 12:
                completed = True

            elif goal == "become protector" and agent.skills["combat"] >= 12:
                completed = True

            elif goal == "protect family" and agent.family and agent.health >= 70:
                completed = True

            elif goal == "seek revenge":
                recent = " ".join(agent.memories[-10:]).lower()
                if "fought" in recent or "attacked" in recent or "severe violence" in recent:
                    completed = True

            elif goal == "live peacefully" and agent.age >= 40 and agent.health >= 70:
                completed = True

            elif goal == "master a craft":
                if max(agent.skills.values()) >= 15:
                    completed = True

            elif goal == "find belonging" and agent.faction is not None:
                completed = True

            if completed:
                agent.completed_goals.append(goal)
                agent.write_journal(self.day, self.hour, f"I feel I have fulfilled my goal: {goal}.")
                logs.append(f"{agent.name} fulfilled their life goal: {goal}.")
                self.add_history(f"{agent.name} fulfilled life goal: {goal}.")

                agent.life_goal = None
                self.assign_life_goal(agent)

    def create_daily_chronicle(self, logs):
        if not self.daily_events:
            return

        important_keywords = [
            "died", "born", "founded", "leader", "war", "rebellion",
            "technology", "milestone", "trial", "exiled", "treaty",
            "completed", "fulfilled", "murder", "settlement"
        ]

        important_events = [
            event for event in self.daily_events
            if any(keyword in event.lower() for keyword in important_keywords)
        ]

        if important_events:
            summary = f"Day {self.day - 1} Chronicle: " + " ".join(important_events[:5])
        else:
            alive_count = len([a for a in self.agents if a.alive])
            summary = f"Day {self.day - 1} Chronicle: The day passed quietly. Population alive: {alive_count}."

        self.chronicles.append(summary)

        if len(self.chronicles) > 30:
            self.chronicles.pop(0)

        logs.append(summary)
        self.daily_events = []

    def update_era(self, logs):
        alive = [a for a in self.agents if a.alive]

        new_era = self.current_era

        if self.wars:
            new_era = "Age of War"

        elif self.technologies:
            new_era = "Age of Innovation"

        elif self.extra_settlements:
            new_era = "Age of Expansion"

        elif self.settlement_stage in ["Village", "Town", "City"]:
            new_era = "Age of Settlement"

        elif len(alive) >= 15:
            new_era = "Age of Growth"

        if new_era != self.current_era:
            self.current_era = new_era

            era_record = {
                "name": new_era,
                "start_day": self.day
            }

            self.eras.append(era_record)

            logs.append(f"NEW ERA BEGINS: {new_era}.")
            self.add_history(f"New era began: {new_era}.")

    def check_world_state(self, logs):
        alive = [a for a in self.agents if a.alive]
        main_alive = [
            a for a in self.agents
            if a.alive and a.location != "Exiled Lands" and not self.is_extra_settlement_location(a.location)
        ]

        if len(alive) == 0:
            self.world_state = "Extinct"
            reason = "All agents have died."
        elif len(main_alive) == 0 and not self.extra_settlements:
            self.world_state = "Collapsed"
            reason = "The main settlement collapsed with no surviving offshoots."
        elif self.village_tension >= 100 and self.wars:
            self.world_state = "Dark Age"
            reason = "War and tension pushed society into a dark age."
        elif len(alive) >= 100 and self.settlement_stage == "City":
            self.world_state = "Civilization"
            reason = "The society successfully became a city civilization."
        else:
            return

        if reason not in self.collapse_reasons:
            self.collapse_reasons.append(reason)
            logs.append(f"WORLD STATE CHANGED: {self.world_state}.")
            logs.append(f"Reason: {reason}")
            self.add_history(f"World state changed to {self.world_state}: {reason}")

    def check_milestones(self, logs):
        alive = [a for a in self.agents if a.alive]
        dead = [a for a in self.agents if not a.alive]
        children = [a for a in alive if a.age < 18]

        if "Shelter" in self.settlement["buildings"]:
            self.unlock_milestone("first_shelter", "First permanent shelter built.", logs)

        if self.leader:
            self.unlock_milestone("first_leader", f"{self.leader} became the first leader.", logs)

        if self.laws:
            self.unlock_milestone("first_law", "The first law was created.", logs)

        if children:
            self.unlock_milestone("first_child", "The first child was born.", logs)

        if dead:
            self.unlock_milestone("first_death", "The first death was recorded.", logs)

        if len(alive) >= 20:
            self.unlock_milestone("population_20", "Population reached 20.", logs)

        if len(self.settlement["buildings"]) >= 4:
            self.unlock_milestone("village_complete", "The village became a developed settlement.", logs)

        if any(record["crime"] == "murder" for records in self.crime_records.values() for record in records):
            self.unlock_milestone("first_murder", "The first murder was recorded.", logs)

        if any(a.generation >= 2 and a.age >= 18 for a in self.agents):
            self.unlock_milestone("generation_2_adult", "The second generation reached adulthood.", logs)

        if self.settlement_stage == "Village":
            self.unlock_milestone("became_village", "The settlement became a village.", logs)

        if self.world_state == "Dark Age":
            self.unlock_milestone("dark_age", "The world entered a dark age.", logs)

        if self.world_state == "Civilization":
            self.unlock_milestone("civilization_success", "The society became a civilization.", logs)

        if self.world_state == "Extinct":
            self.unlock_milestone("extinction", "All agents died.", logs)

        if self.settlement_stage == "Town":
            self.unlock_milestone("became_town", "The settlement became a town.", logs)

        if self.settlement_stage == "City":
            self.unlock_milestone("became_city", "The settlement became a city.", logs)

        if self.extra_settlements:
            self.unlock_milestone("second_settlement", "A second settlement was founded.", logs)

        if any(s["relationship_to_main"] >= 50 for s in self.extra_settlements):
            self.unlock_milestone("first_alliance", "The first alliance between settlements formed.", logs)

        if any(s["relationship_to_main"] <= -50 for s in self.extra_settlements):
            self.unlock_milestone("settlement_rivalry", "A serious rivalry between settlements began.", logs)

        if any(self.is_extra_settlement_location(a.location) for a in self.agents if a.alive):
            self.unlock_milestone("first_migration", "The first migration between settlements occurred.", logs)

        if self.wars:
            self.unlock_milestone("first_war", "The first war between settlements occurred.", logs)

        if self.treaties:
            self.unlock_milestone("first_treaty", "The first diplomatic treaty was signed.", logs)

    def add_history(self, event):
        record = f"Day {self.day}, {self.hour}:00 — {event}"
        self.world_history.append(record)

        if len(self.world_history) > 50:
            self.world_history.pop(0)

    def tick(self):
        logs = []
        starting_day = self.day

        if self.world_state in ["Extinct", "Civilization"]:
            logs.append(f"The simulation has reached an ending state: {self.world_state}.")
            return logs

        if self.hour == 6:
            self.update_season()
            self.update_weather()
            logs.append(f"Weather changed: {self.weather}. Season: {self.season}.")

        self.apply_building_effects(logs)
        self.apply_extra_settlement_effects(logs)

        for agent in self.agents:
            if not agent.alive:
                continue

            self.assign_role(agent)
            agent.update_needs()

            if not agent.alive:
                self.record_death(agent, "hunger or exhaustion")
                continue

            self.apply_weather_effects(agent, logs)

            if not agent.alive:
                self.record_death(agent, "weather exposure")
                continue

            action = agent.choose_action(self.hour)

            if action == "explore":
                new_location = random.choice(LOCATIONS)
                agent.location = new_location
                logs.append(f"{agent.name} explored and moved to {agent.location}.")

            elif action == "gather food":
                food_found = random.randint(5, 20) + agent.skills["hunting"]

                if self.weather in ["Storm", "Snow"]:
                    food_found = max(1, food_found // 2)

                if self.season == "Winter":
                    food_found = max(1, food_found // 2)

                if self.weather == "Rain":
                    food_found += 2

                food_found = int(food_found * get_setting("resource_multiplier"))

                agent.hunger = max(agent.hunger - food_found // 2, 0)

                agent_settlement = self.get_agent_settlement(agent)

                if agent_settlement:
                    agent_settlement["resources"]["food"] += food_found // 2
                else:
                    self.resources["food"] += food_found // 2

                agent.inventory["food"] += max(1, food_found // 4)
                agent.improve_skill("hunting", 1)

                logs.append(f"{agent.name} gathered food at {agent.location}.")
                logs.append(f"{food_found // 2} food was added to shared storage.")
                logs.append(f"{agent.name}'s hunting improved to {agent.skills['hunting']}.")

            elif action == "sleep":
                agent.energy = min(agent.energy + 30, 100)
                logs.append(f"{agent.name} slept at {agent.location}. Energy restored.")

            elif action == "talk":
                logs.extend(self.handle_talk(agent))

            elif action == "argue":
                logs.extend(self.handle_argument(agent))

            elif action == "help":
                logs.extend(self.handle_help(agent))

            elif action == "practice":
                skill = random.choice(list(agent.skills.keys()))
                agent.improve_skill(skill, 1)
                logs.append(f"{agent.name} practiced {skill}. {skill.capitalize()} is now {agent.skills[skill]}.")

            elif action == "gather materials":
                wood = random.randint(3, 10)
                stone = random.randint(1, 6)

                if self.weather in ["Storm", "Snow"]:
                    wood = max(1, wood // 2)
                    stone = max(1, stone // 2)

                agent_settlement = self.get_agent_settlement(agent)

                if agent_settlement and "Basic Tools" in agent_settlement.get("technologies", []):
                    wood += 3
                    stone += 2
                elif not agent_settlement and "Basic Tools" in self.technologies:
                    wood += 3
                    stone += 2

                wood = int(wood * get_setting("resource_multiplier"))
                stone = int(stone * get_setting("resource_multiplier"))

                if agent_settlement:
                    agent_settlement["resources"]["wood"] += wood
                    agent_settlement["resources"]["stone"] += stone
                else:
                    self.resources["wood"] += wood
                    self.resources["stone"] += stone

                agent.inventory["wood"] += max(1, wood // 3)
                agent.inventory["stone"] += max(1, stone // 3)

                agent.improve_skill("building", 1)

                logs.append(f"{agent.name} gathered materials at {agent.location}.")
                logs.append(f"Shared resources gained: wood +{wood}, stone +{stone}.")
                logs.append(f"{agent.name}'s building improved to {agent.skills['building']}.")

            elif action == "build":
                logs.extend(self.handle_build(agent))

            elif action == "steal food":
                logs.extend(self.handle_steal_food(agent))

            elif action == "fight":
                logs.extend(self.handle_fight(agent))

            elif action == "heal":
                logs.extend(self.handle_heal(agent))

            elif action == "bond":
                logs.extend(self.handle_bond(agent))

            elif action == "learn":
                logs.extend(self.handle_learning(agent))

            elif action == "trade":
                logs.extend(self.handle_trade(agent))

            elif action == "gamble":
                logs.extend(self.handle_gamble(agent))

            elif action == "repay debt":
                logs.extend(self.handle_repay_debt(agent))

            elif action == "demand debt":
                logs.extend(self.handle_demand_debt(agent))

            elif action == "severe violence":
                logs.extend(self.handle_severe_violence(agent))

            elif action == "patrol":
                logs.extend(self.handle_patrol(agent))

            else:
                logs.append(f"{agent.name} stayed at {agent.location} and chose to {action}.")

        self.handle_family_growth(logs)
        self.handle_aging(logs)
        self.choose_village_project(logs)
        self.check_leadership(logs)
        self.update_settlement_stage(logs)
        self.update_culture(logs)
        self.create_tradition(logs)
        self.run_traditions(logs)
        self.update_beliefs(logs)
        self.update_factions(logs)
        self.update_faction_influence(logs)
        self.handle_faction_conflict(logs)
        self.handle_rebellion(logs)
        self.handle_exile_settlements(logs)
        self.handle_settlement_relations(logs)
        self.handle_migration(logs)
        self.handle_extra_settlement_growth(logs)
        self.update_extra_settlement_leaders(logs)
        self.update_extra_settlement_culture(logs)
        self.update_extra_settlement_laws(logs)
        self.handle_diplomacy(logs)
        self.handle_settlement_war(logs)
        self.generate_research(logs)
        self.unlock_technology(logs)
        self.generate_extra_settlement_research(logs)
        self.unlock_extra_settlement_technology(logs)
        self.handle_journals(logs)
        self.handle_personality_drift(logs)
        self.update_life_goals(logs)
        self.check_goal_progress(logs)
        self.update_era(logs)
        self.check_milestones(logs)

        self.hour += 1

        if self.hour >= 24:
            self.hour = 0
            self.day += 1
            logs.append(f"--- A new day begins. Day {self.day}. ---")

        self.daily_events.extend(logs)

        if self.day != starting_day:
            self.create_daily_chronicle(logs)

        self.check_world_state(logs)

        return logs

    def update_season(self):
        season_cycle = ["Spring", "Summer", "Autumn", "Winter"]
        season_index = ((self.day - 1) // 10) % len(season_cycle)
        self.season = season_cycle[season_index]

    def update_weather(self):
        if self.season == "Spring":
            options = ["Clear", "Rain", "Cloudy", "Windy"]
        elif self.season == "Summer":
            options = ["Clear", "Hot", "Dry", "Storm"]
        elif self.season == "Autumn":
            options = ["Cloudy", "Rain", "Windy", "Cold"]
        else:
            options = ["Cold", "Snow", "Storm", "Clear"]

        self.weather = random.choice(options)

    def apply_weather_effects(self, agent, logs):
        if self.weather in ["Cold", "Snow", "Storm"] and agent.location != "Camp":
            if random.random() < get_setting("weather_sickness_chance"):
                damage = random.randint(3, 10)
                agent.health = max(agent.health - damage, 0)
                agent.status = "Sick"

                logs.append(f"{agent.name} became sick from harsh weather. Health -{damage}.")

                if agent.health <= 0:
                    agent.alive = False
                    agent.status = "Dead"
                    logs.append(f"{agent.name} died from exposure.")
                    self.record_death(agent, "exposure")

    def record_death(self, agent, cause):
        for record in self.death_records:
            if record["name"] == agent.name:
                return

        death_record = {
            "name": agent.name,
            "day": self.day,
            "hour": self.hour,
            "cause": cause,
            "role": agent.role
        }

        self.death_records.append(death_record)

        memorial = f"{agent.name}, the {agent.role}, died on Day {self.day} at {self.hour}:00. Cause: {cause}."
        self.memorials.append(memorial)

        self.add_history(f"{agent.name} died. Cause: {cause}.")

    def apply_building_effects(self, logs):
        if self.hour != 6:
            return

        buildings = self.settlement["buildings"]

        if "Farm" in buildings:
            food_gain = random.randint(15, 30)

            if "Crop Rotation" in self.technologies:
                food_gain += 15

            self.resources["food"] += food_gain
            logs.append(f"The Farm produced food. Food +{food_gain}.")

        if "Storage Hut" in buildings:
            if random.random() < 0.15:
                saved_food = random.randint(5, 15)
                self.resources["food"] += saved_food
                logs.append(f"The Storage Hut preserved supplies. Food saved +{saved_food}.")

        if "Clinic" in buildings:
            for agent in self.agents:
                if agent.alive and agent.health < 70 and agent.location != "Exiled Lands":
                    heal_amount = random.randint(3, 8)
                    agent.health = min(agent.health + heal_amount, 100)
                    logs.append(f"The Clinic helped {agent.name} recover. Health +{heal_amount}.")

        if "Guard Post" in buildings:
            if self.village_tension > 0:
                tension_drop = random.randint(3, 8)
                self.village_tension = clamp(self.village_tension - tension_drop, 0, 100)
                logs.append(f"The Guard Post reduced village tension by {tension_drop}.")

        if "Written Records" in self.technologies and self.village_tension > 0:
            self.village_tension = max(self.village_tension - 2, 0)
            logs.append("Written records helped settle disputes. Village tension -2.")

        if "Council Governance" in self.technologies and self.village_tension > 0:
            self.village_tension = max(self.village_tension - 4, 0)
            logs.append("Council governance reduced political tension. Village tension -4.")

    def apply_extra_settlement_effects(self, logs):
        if self.hour != 6:
            return

        for settlement in self.extra_settlements:
            resources = settlement.get("resources", {})
            buildings = settlement.get("buildings", [])

            if "Farm" in buildings:
                food_gain = random.randint(8, 18)

                if "Crop Rotation" in settlement.get("technologies", []):
                    food_gain += 10

                resources["food"] += food_gain
                logs.append(f"{settlement['name']}'s Farm produced food +{food_gain}.")

            if "Guard Post" in buildings and settlement["tension"] > 0:
                tension_drop = random.randint(2, 6)
                settlement["tension"] = max(settlement["tension"] - tension_drop, 0)
                logs.append(f"{settlement['name']}'s Guard Post reduced tension by {tension_drop}.")

    def assign_role(self, agent):
        if agent.location == "Exiled Lands":
            agent.role = "Exile"
            return

        best_skill = max(agent.skills, key=agent.skills.get)

        if best_skill == "hunting":
            agent.role = "Hunter"
        elif best_skill == "building":
            agent.role = "Builder"
        elif best_skill == "farming":
            agent.role = "Farmer"
        elif best_skill == "social":
            agent.role = "Mediator"
        elif best_skill == "teaching":
            agent.role = "Teacher"
        elif best_skill == "medicine":
            agent.role = "Medic"
        elif best_skill == "combat":
            agent.role = "Guard"
        else:
            agent.role = "Wanderer"

        if agent.skills["social"] >= 8 and agent.skills["farming"] >= 5:
            agent.role = "Merchant"

        if self.leader == agent.name and not self.is_extra_settlement_location(agent.location):
            agent.role = "Leader"

        for settlement in self.extra_settlements:
            if settlement.get("leader") == agent.name and agent.location == settlement["name"]:
                agent.role = "Leader"

    def handle_heal(self, medic):
        logs = []

        patients = [
            agent for agent in self.agents
            if agent.alive
            and agent.name != medic.name
            and agent.health < 80
            and agent.location == medic.location
        ]

        if not patients:
            logs.append(f"{medic.name} looked for someone to heal, but no one nearby needed care.")
            return logs

        patient = min(patients, key=lambda a: a.health)

        heal_amount = random.randint(5, 15) + medic.skills["medicine"]

        if "Clinic" in self.settlement["buildings"]:
            heal_amount += 10

        if "Herbal Medicine" in self.technologies:
            heal_amount += 8

        patient.health = min(patient.health + heal_amount, 100)

        medic.improve_skill("medicine", 1)

        patient.change_relationship(medic.name, "trust", 8)
        patient.change_relationship(medic.name, "respect", 5)
        medic.change_relationship(patient.name, "friendship", 3)

        patient.remember(f"{medic.name} treated my injuries.")
        medic.remember(f"Healed {patient.name}.")

        if patient.health >= 60:
            patient.status = "Healthy"
        elif patient.health >= 30:
            patient.status = "Injured"
        else:
            patient.status = "Critical"

        logs.append(f"{medic.name} treated {patient.name} at {medic.location}.")
        logs.append(f"{patient.name}'s health +{heal_amount}. Current health: {patient.health}.")
        logs.append(f"{patient.name}'s trust toward {medic.name} +8.")
        logs.append(f"{medic.name}'s medicine improved to {medic.skills['medicine']}.")

        self.add_history(f"{medic.name} healed {patient.name}.")

        return logs

    def handle_learning(self, child):
        logs = []

        teachers = [
            agent for agent in self.nearby_agents(child)
            if agent.alive
            and agent.age >= 18
            and (
                agent.role == "Teacher"
                or agent.name in child.parents
                or agent.skills["teaching"] >= 5
            )
        ]

        if not teachers:
            logs.append(f"{child.name} wanted to learn, but no teacher was nearby.")
            return logs

        teacher = random.choice(teachers)

        teachable_skills = [
            skill for skill in teacher.skills
            if teacher.skills[skill] > child.skills[skill]
        ]

        if not teachable_skills:
            logs.append(f"{teacher.name} tried to teach {child.name}, but had nothing new to teach.")
            return logs

        skill = random.choice(teachable_skills)

        learning_chance = 0.45
        learning_chance += child.curiosity / 250
        learning_chance += teacher.skills["teaching"] / 100
        learning_chance += child.discipline / 300
        learning_chance -= child.pride / 500

        logs.append(f"{teacher.name} taught {child.name} basic {skill} at {child.location}.")

        if random.random() < learning_chance:
            child.improve_skill(skill, 1)
            teacher.improve_skill("teaching", 1)

            child.change_relationship(teacher.name, "respect", 4)
            child.change_relationship(teacher.name, "trust", 3)
            teacher.change_relationship(child.name, "friendship", 2)

            child.remember(f"Learned {skill} from {teacher.name}.")
            teacher.remember(f"Taught {child.name} {skill}.")

            logs.append(f"{child.name} learned successfully.")
            logs.append(f"{child.name}'s {skill} improved to {child.skills[skill]}.")
        else:
            child.remember(f"Struggled to learn {skill} from {teacher.name}.")
            logs.append(f"{child.name} struggled to understand the lesson.")

        return logs

    def handle_trade(self, agent):
        logs = []

        nearby = [
            other for other in self.nearby_agents(agent)
            if other.alive and other.age >= 13
        ]

        if not nearby:
            logs.append(f"{agent.name} wanted to trade, but no one was nearby.")
            return logs

        other = random.choice(nearby)

        possible_items = [
            item for item, amount in agent.inventory.items()
            if amount > 0
        ]

        wanted_items = [
            item for item, amount in other.inventory.items()
            if amount > 0
        ]

        if not possible_items or not wanted_items:
            logs.append(f"{agent.name} and {other.name} tried to trade, but neither had enough goods.")
            return logs

        give_item = random.choice(possible_items)
        receive_item = random.choice(wanted_items)

        agent.inventory[give_item] -= 1
        other.inventory[give_item] = other.inventory.get(give_item, 0) + 1

        other.inventory[receive_item] -= 1
        agent.inventory[receive_item] = agent.inventory.get(receive_item, 0) + 1

        agent.wealth += 1
        other.wealth += 1

        agent.change_relationship(other.name, "trust", 2)
        other.change_relationship(agent.name, "trust", 2)

        agent.remember(f"Traded {give_item} with {other.name}.")
        other.remember(f"Traded {receive_item} with {agent.name}.")

        logs.append(f"{agent.name} traded with {other.name} at {agent.location}.")
        logs.append(f"{agent.name} gave 1 {give_item} and received 1 {receive_item}.")
        logs.append(f"{other.name} gave 1 {receive_item} and received 1 {give_item}.")
        logs.append(f"Trust between them +2.")

        return logs

    def handle_gamble(self, agent):
        logs = []

        nearby = [
            other for other in self.nearby_agents(agent)
            if other.alive and other.age >= 18
        ]

        if not nearby:
            logs.append(f"{agent.name} wanted to gamble, but no one was nearby.")
            return logs

        other = random.choice(nearby)

        stake = random.randint(1, 3)

        if agent.wealth < stake and other.wealth < stake:
            logs.append(f"{agent.name} and {other.name} wanted to gamble, but neither had enough wealth.")
            return logs

        logs.append(f"{agent.name} gambled with {other.name} at {agent.location}.")
        logs.append(f"Stake: {stake} wealth.")

        agent_score = random.randint(1, 100) + agent.risk_taking // 5
        other_score = random.randint(1, 100) + other.risk_taking // 5

        if agent_score >= other_score:
            winner = agent
            loser = other
        else:
            winner = other
            loser = agent

        winner.wealth += stake

        if loser.wealth >= stake:
            loser.wealth -= stake
            logs.append(f"{winner.name} won {stake} wealth from {loser.name}.")
        else:
            debt = stake - loser.wealth
            loser.wealth = 0
            loser.debts[winner.name] = loser.debts.get(winner.name, 0) + debt

            logs.append(f"{winner.name} won, but {loser.name} could not fully pay.")
            logs.append(f"{loser.name} now owes {winner.name} {debt} wealth.")

            self.add_history(f"{loser.name} fell into debt to {winner.name}.")

            winner.change_relationship(loser.name, "trust", -5)
            loser.change_relationship(winner.name, "fear", 3)

        loser.change_relationship(winner.name, "trust", -3)
        winner.change_relationship(loser.name, "respect", -1)

        self.village_tension = clamp(self.village_tension + 3, 0, 100)

        winner.remember(f"Won a gamble against {loser.name}.")
        loser.remember(f"Lost a gamble against {winner.name}.")

        logs.append(f"Village tension increased to {self.village_tension}.")

        if loser.debts:
            logs.append(f"{loser.name}'s debts: {loser.debts}")

        if self.village_tension > 60:
            self.add_history(f"Gambling caused rising tension in {self.settlement['name'] or 'the camp'}.")

        return logs

    def handle_repay_debt(self, agent):
        logs = []

        if not agent.debts:
            logs.append(f"{agent.name} had no debts to repay.")
            return logs

        creditor_name = random.choice(list(agent.debts.keys()))
        creditor = find_agent(self.agents, creditor_name)

        if not creditor or not creditor.alive:
            logs.append(f"{agent.name}'s creditor was gone, so the debt faded from memory.")
            del agent.debts[creditor_name]
            return logs

        amount_owed = agent.debts[creditor_name]

        if agent.wealth <= 0:
            logs.append(f"{agent.name} wanted to repay {creditor_name}, but had no wealth.")
            return logs

        payment = min(agent.wealth, amount_owed)

        agent.wealth -= payment
        creditor.wealth += payment
        agent.debts[creditor_name] -= payment

        logs.append(f"{agent.name} repaid {payment} wealth to {creditor_name}.")

        agent.change_relationship(creditor_name, "trust", 3)
        creditor.change_relationship(agent.name, "trust", 5)

        agent.remember(f"Repaid debt to {creditor_name}.")
        creditor.remember(f"{agent.name} repaid part of their debt.")

        if agent.debts[creditor_name] <= 0:
            del agent.debts[creditor_name]
            logs.append(f"{agent.name} fully repaid their debt to {creditor_name}.")
            creditor.change_relationship(agent.name, "respect", 4)

        return logs

    def handle_demand_debt(self, agent):
        logs = []

        debtors = [
            other for other in self.nearby_agents(agent)
            if other.alive and other.debts.get(agent.name, 0) > 0
        ]

        if not debtors:
            logs.append(f"{agent.name} wanted to demand repayment, but no debtor was nearby.")
            return logs

        debtor = random.choice(debtors)
        owed = debtor.debts[agent.name]

        logs.append(f"{agent.name} demanded repayment from {debtor.name}.")
        logs.append(f"{debtor.name} owes {agent.name} {owed} wealth.")

        pressure = agent.aggression + agent.greed + owed * 5
        resistance = debtor.pride + debtor.aggression + debtor.greed

        if debtor.wealth > 0:
            payment = min(debtor.wealth, owed)

            debtor.wealth -= payment
            agent.wealth += payment
            debtor.debts[agent.name] -= payment

            logs.append(f"{debtor.name} paid {payment} wealth under pressure.")

            debtor.change_relationship(agent.name, "trust", -4)
            debtor.change_relationship(agent.name, "fear", 4)
            agent.change_relationship(debtor.name, "respect", -2)

            if debtor.debts[agent.name] <= 0:
                del debtor.debts[agent.name]
                logs.append(f"{debtor.name}'s debt to {agent.name} is fully cleared.")

        elif resistance > pressure:
            logs.append(f"{debtor.name} refused to repay {agent.name}.")
            debtor.change_relationship(agent.name, "trust", -8)
            agent.change_relationship(debtor.name, "trust", -12)

            self.village_tension = clamp(self.village_tension + 8, 0, 100)
            logs.append(f"Village tension increased to {self.village_tension}.")

            if random.random() < 0.35:
                logs.append(f"The debt argument turned violent.")
                logs.extend(self.handle_fight(agent))

            self.add_history(f"{debtor.name} refused to repay debt to {agent.name}.")

        else:
            logs.append(f"{debtor.name} could not pay and became afraid.")
            debtor.change_relationship(agent.name, "fear", 8)
            agent.change_relationship(debtor.name, "trust", -6)

            self.village_tension = clamp(self.village_tension + 5, 0, 100)
            logs.append(f"Village tension increased to {self.village_tension}.")

        return logs

    def handle_bond(self, agent):
        logs = []

        nearby = [
            other for other in self.nearby_agents(agent)
            if other.alive
            and other.partner is None
            and agent.partner is None
            and other.age >= 18
            and agent.age >= 18
        ]

        if not nearby:
            logs.append(f"{agent.name} wanted to bond with someone, but no suitable person was nearby.")
            return logs

        other = random.choice(nearby)

        rel = agent.get_relationship(other.name)
        other_rel = other.get_relationship(agent.name)

        compatibility = (
            rel["trust"]
            + rel["friendship"]
            + other_rel["trust"]
            + other_rel["friendship"]
            + agent.kindness
            + other.kindness
            - abs(agent.aggression - other.aggression)
        )

        logs.append(f"{agent.name} spent quiet time with {other.name} at {agent.location}.")

        if compatibility > 120:
            agent.partner = other.name
            other.partner = agent.name

            agent.family.append(other.name)
            other.family.append(agent.name)

            agent.remember(f"Formed a partnership with {other.name}.")
            other.remember(f"Formed a partnership with {agent.name}.")

            logs.append(f"{agent.name} and {other.name} became partners.")
            self.add_history(f"{agent.name} and {other.name} became partners.")
        else:
            friendship_gain = random.randint(2, 5)
            agent.change_relationship(other.name, "friendship", friendship_gain)
            other.change_relationship(agent.name, "friendship", friendship_gain)

            logs.append(f"Their bond grew slowly. Friendship +{friendship_gain}.")

        return logs

    def handle_family_growth(self, logs):
        for agent in self.agents:
            if not agent.alive:
                continue

            if agent.partner and not agent.pregnant:
                if random.random() < get_setting("birth_chance"):
                    agent.pregnant = True
                    agent.pregnancy_timer = CONFIG["pregnancy_timer"]

                    logs.append(f"{agent.name} and {agent.partner}'s family may grow soon.")
                    self.add_history(f"{agent.name} and {agent.partner} are expecting a child.")

            elif agent.pregnant:
                agent.pregnancy_timer -= 1

                if agent.pregnancy_timer <= 0:
                    child_name = self.generate_child_name()

                    from agent import Agent
                    child = Agent(child_name)

                    partner = find_agent(self.agents, agent.partner)

                    child.age = 0
                    child.location = agent.location
                    child.parents = [agent.name, agent.partner]
                    child.family.append(agent.name)
                    child.family.append(agent.partner)

                    if partner:
                        child.generation = max(agent.generation, partner.generation) + 1
                    else:
                        child.generation = agent.generation + 1

                    self.inherit_traits(child, agent, partner)

                    self.agents.append(child)

                    agent.family.append(child_name)

                    if partner:
                        partner.family.append(child_name)

                    agent.pregnant = False

                    logs.append(f"A child was born: {child_name}.")
                    self.add_history(f"{child_name} was born into the settlement.")

    def generate_child_name(self):
        syllables = ["ra", "mi", "ka", "lo", "zen", "ari", "no", "el", "sha", "rin"]
        return random.choice(syllables).capitalize() + random.choice(syllables)

    def inherit_traits(self, child, parent_a, parent_b):
        traits = ["curiosity", "kindness", "aggression", "discipline", "pride"]

        for trait in traits:
            value_a = getattr(parent_a, trait)

            if parent_b:
                value_b = getattr(parent_b, trait)
                inherited = (value_a + value_b) // 2
            else:
                inherited = value_a

            mutation = random.randint(-10, 10)
            setattr(child, trait, max(1, min(100, inherited + mutation)))

        for skill in child.skills:
            skill_a = parent_a.skills.get(skill, 1)

            if parent_b:
                skill_b = parent_b.skills.get(skill, 1)
                inherited_skill = max(1, (skill_a + skill_b) // 4)
            else:
                inherited_skill = max(1, skill_a // 3)

            child.skills[skill] = inherited_skill

    def handle_aging(self, logs):
        if self.hour != 0:
            return

        for agent in self.agents:
            if not agent.alive:
                continue

            if self.day % CONFIG["aging_every_days"] == 0:
                agent.age += 1

                if agent.age == 6:
                    logs.append(f"{agent.name} is no longer a toddler.")
                    self.add_history(f"{agent.name} reached childhood.")

                elif agent.age == 13:
                    logs.append(f"{agent.name} became a teenager.")
                    self.add_history(f"{agent.name} became a teenager.")

                elif agent.age == 18:
                    logs.append(f"{agent.name} reached adulthood.")
                    self.add_history(f"{agent.name} became an adult.")

                elif agent.age > 80:
                    if random.random() < get_setting("weather_sickness_chance"):
                        agent.alive = False
                        agent.status = "Dead"
                        logs.append(f"{agent.name} died of old age.")
                        self.record_death(agent, "old age")

    def check_leadership(self, logs):
        if self.settlement["name"] is None:
            return

        best_candidate = None
        best_score = -999

        for agent in self.agents:
            if agent.location == "Exiled Lands":
                continue

            total_respect = 0
            total_trust = 0

            for other in self.agents:
                if other.name == agent.name:
                    continue

                rel = other.get_relationship(agent.name)
                total_respect += rel["respect"]
                total_trust += rel["trust"]

            score = (
                total_respect
                + total_trust
                + agent.skills["social"] * 3
                + agent.discipline
                + agent.kindness // 2
                - agent.aggression // 2
            )

            if agent.faction and agent.faction in self.factions:
                score += self.factions[agent.faction].get("influence", 0) // 2

            if score > best_score:
                best_score = score
                best_candidate = agent

        if best_candidate and self.leader != best_candidate.name and best_score > 80:
            old_leader = self.leader
            self.leader = best_candidate.name

            if old_leader is None:
                logs.append(f"{best_candidate.name} has naturally become the leader of {self.settlement['name']}.")
                self.add_history(f"{best_candidate.name} became the first leader of {self.settlement['name']}.")
            else:
                logs.append(f"Leadership changed from {old_leader} to {best_candidate.name}.")
                self.add_history(f"Leadership changed from {old_leader} to {best_candidate.name}.")

    def nearby_agents(self, agent):
        return [
            other for other in self.agents
            if other.name != agent.name and other.location == agent.location
        ]

    def choose_village_project(self, logs):
        if self.settlement["name"] is None:
            return

        if self.current_project is not None:
            return

        if not self.leader:
            return

        possible_projects = []

        if "Storage Hut" not in self.settlement["buildings"]:
            possible_projects.append("Storage Hut")

        if "Farm" not in self.settlement["buildings"]:
            possible_projects.append("Farm")

        if "Clinic" not in self.settlement["buildings"]:
            possible_projects.append("Clinic")

        if "Guard Post" not in self.settlement["buildings"]:
            possible_projects.append("Guard Post")

        if not possible_projects:
            return

        leader = find_agent(self.agents, self.leader)

        if not leader:
            return

        if leader.role == "Leader":
            if self.resources["food"] < 30:
                project = "Farm"
            elif self.village_tension > 50:
                project = "Guard Post"
            else:
                project = random.choice(possible_projects)
        else:
            project = random.choice(possible_projects)

        self.current_project = {
            "name": project,
            "progress": 0,
            "required": 100
        }

        logs.append(f"Leader {self.leader} proposed a new village project: {project}.")
        self.add_history(f"{self.leader} proposed building a {project}.")

    def work_on_project(self, agent):
        logs = []

        if self.current_project is None:
            return logs

        project_name = self.current_project["name"]

        wood_cost = 5
        stone_cost = 3

        if self.resources["wood"] < wood_cost or self.resources["stone"] < stone_cost:
            logs.append(f"{agent.name} wanted to work on {project_name}, but materials were too low.")
            return logs

        self.resources["wood"] -= wood_cost
        self.resources["stone"] -= stone_cost

        progress = random.randint(8, 18) + agent.skills["building"]
        self.current_project["progress"] += progress

        agent.improve_skill("building", 1)

        logs.append(f"{agent.name} worked on {project_name}.")
        logs.append(
            f"{project_name} progress +{progress}. "
            f"Total: {self.current_project['progress']}/{self.current_project['required']}."
        )

        if self.current_project["progress"] >= self.current_project["required"]:
            self.settlement["buildings"].append(project_name)
            logs.append(f"{project_name} has been completed.")
            self.add_history(f"{project_name} was completed in {self.settlement['name']}.")

            if project_name == "Farm":
                self.resources["food"] += 30
                logs.append("The Farm produced its first food. Food +30.")

            elif project_name == "Storage Hut":
                logs.append("The village can now store more supplies safely.")

            elif project_name == "Clinic":
                logs.append("The village now has a place for healing.")

            elif project_name == "Guard Post":
                self.village_tension = clamp(self.village_tension - 15, 0, 100)
                logs.append("The Guard Post made the village feel safer. Village tension -15.")

            self.current_project = None

        return logs

    def handle_build(self, agent):
        logs = []

        if self.current_project is not None and "Shelter" in self.settlement["buildings"]:
            return self.work_on_project(agent)

        if "Shelter" in self.settlement["buildings"]:
            logs.append(f"{agent.name} maintained the shelter.")
            agent.improve_skill("building", 1)
            return logs

        if self.resources["wood"] < 10 or self.resources["stone"] < 5:
            logs.append(f"{agent.name} wanted to build, but the group lacked materials.")
            return logs

        self.resources["wood"] -= 10
        self.resources["stone"] -= 5

        progress = random.randint(10, 25) + agent.skills["building"]
        self.settlement["shelter_progress"] += progress

        agent.improve_skill("building", 1)

        logs.append(f"{agent.name} worked on the first shelter.")
        logs.append(f"Shelter progress +{progress}. Total: {self.settlement['shelter_progress']}/100.")

        if self.settlement["shelter_progress"] >= 100:
            self.settlement["buildings"].append("Shelter")

            if self.settlement["name"] is None:
                self.settlement["name"] = self.generate_settlement_name()

            logs.append("A permanent shelter has been completed.")
            logs.append(f"Settlement founded: {self.settlement['name']}.")

            self.add_history(f"Settlement founded: {self.settlement['name']}.")

        return logs

    def handle_steal_food(self, agent):
        logs = []

        if self.resources["food"] <= 0:
            logs.append(f"{agent.name} considered stealing food, but storage was empty.")
            return logs

        stolen = random.randint(3, 10)
        stolen = min(stolen, self.resources["food"])

        self.resources["food"] -= stolen
        agent.hunger = max(agent.hunger - stolen, 0)

        self.village_tension = clamp(self.village_tension + 5, 0, 100)

        agent.remember(f"Stole {stolen} food from storage.")

        logs.append(f"{agent.name} secretly stole {stolen} food from storage.")
        logs.append(f"Village tension increased to {self.village_tension}.")

        caught_chance = 0.35

        if "Storage Hut" in self.settlement["buildings"]:
            caught_chance += 0.25

        if random.random() < caught_chance:
            witness = random.choice([
                other for other in self.agents
                if other.name != agent.name
            ])

            witness.change_relationship(agent.name, "trust", -15)
            witness.change_relationship(agent.name, "respect", -5)
            agent.change_relationship(witness.name, "fear", 3)

            witness.remember(f"Saw {agent.name} stealing food.")
            agent.remember(f"{witness.name} saw me stealing food.")

            logs.append(f"{witness.name} saw {agent.name} stealing.")
            logs.append(f'{witness.name}: "{get_line(witness, "crime")}"')
            logs.append(f"{witness.name}'s trust toward {agent.name} -15.")

            self.add_history(f"{agent.name} was caught stealing food by {witness.name}.")

            self.record_crime(agent.name, "stealing food", witness.name)
            logs.extend(self.handle_trial(agent, "stealing food"))

        return logs

    def handle_fight(self, agent):
        logs = []

        nearby = self.nearby_agents(agent)

        if not nearby:
            logs.append(f"{agent.name} looked ready to fight, but no one was nearby.")
            return logs

        other = random.choice(nearby)

        trust_loss = random.randint(10, 25)
        fear_gain = random.randint(5, 15)

        agent.change_relationship(other.name, "trust", -trust_loss)
        other.change_relationship(agent.name, "trust", -trust_loss)

        other.change_relationship(agent.name, "fear", fear_gain)

        self.village_tension = clamp(self.village_tension + random.randint(8, 18), 0, 100)

        agent.energy = max(agent.energy - 15, 0)
        other.energy = max(other.energy - 20, 0)

        damage = int(random.randint(5, 20) * get_setting("violence_multiplier"))
        other.health = max(other.health - damage, 0)

        if other.health <= 0:
            other.alive = False
            other.status = "Dead"
            logs.append(f"{other.name} died after the fight.")
            self.record_death(other, f"fight with {agent.name}")
        else:
            logs.append(f"{other.name} was injured. Health -{damage}.")

        agent.remember(f"Fought with {other.name}.")
        other.remember(f"{agent.name} attacked me.")

        logs.append(f"{agent.name} got into a fight with {other.name} at {agent.location}.")
        logs.append(f'{agent.name}: "I am tired of pretending this is fine."')
        logs.append(f'{other.name}: "Then you should have stayed away from me."')
        logs.append(f"Trust between them -{trust_loss}.")
        logs.append(f"{other.name}'s fear toward {agent.name} +{fear_gain}.")
        logs.append(f"Village tension increased to {self.village_tension}.")

        self.add_history(f"{agent.name} fought with {other.name}.")

        self.record_crime(agent.name, "fighting", other.name)

        if self.village_tension >= 40:
            logs.extend(self.handle_trial(agent, "fighting"))

        return logs

    def record_crime(self, agent_name, crime, witness_name):
        if agent_name not in self.crime_records:
            self.crime_records[agent_name] = []

        record = {
            "day": self.day,
            "hour": self.hour,
            "crime": crime,
            "witness": witness_name
        }

        self.crime_records[agent_name].append(record)

    def handle_patrol(self, guard):
        logs = []

        if guard.location == "Exiled Lands":
            logs.append(f"{guard.name} wandered alone in exile.")
            return logs

        guard.improve_skill("combat", 1)
        guard.energy = max(guard.energy - 5, 0)

        suspicious_agents = []

        for other in self.nearby_agents(guard):
            if not other.alive:
                continue

            risk_score = (
                other.aggression
                + other.greed // 2
                + other.risk_taking // 2
                - other.kindness // 2
            )

            if risk_score > 120:
                suspicious_agents.append(other)

        logs.append(f"{guard.name} patrolled {guard.location}.")
        logs.append(f"{guard.name}'s combat improved to {guard.skills['combat']}.")

        if suspicious_agents:
            suspect = random.choice(suspicious_agents)

            suspect.change_relationship(guard.name, "fear", 5)
            guard.change_relationship(suspect.name, "trust", -3)

            logs.append(f"{guard.name} kept an eye on {suspect.name}.")
            logs.append(f"{suspect.name}'s fear toward {guard.name} +5.")

            if random.random() < 0.25:
                self.village_tension = clamp(self.village_tension - 5, 0, 100)
                logs.append(f"The patrol calmed the area. Village tension -5.")
        else:
            if random.random() < 0.2:
                self.village_tension = clamp(self.village_tension - 2, 0, 100)
                logs.append(f"The quiet patrol made people feel safer. Village tension -2.")

        return logs

    def handle_severe_violence(self, agent):
        logs = []

        nearby = [
            other for other in self.nearby_agents(agent)
            if other.alive and other.age >= 13
        ]

        if not nearby:
            logs.append(f"{agent.name} had violent thoughts, but no one was nearby.")
            return logs

        target = random.choice(nearby)

        guards = [
            other for other in self.nearby_agents(agent)
            if other.alive and other.role == "Guard"
        ]

        hatred = -agent.get_relationship(target.name)["trust"]
        aggression = agent.aggression
        fear = agent.get_relationship(target.name)["fear"]
        tension = self.village_tension

        violence_score = aggression + hatred + fear + tension

        if "Guard Post" in self.settlement["buildings"]:
            violence_score -= 25

        if violence_score < 140:
            logs.append(f"{agent.name} nearly attacked {target.name}, but held back.")
            agent.remember(f"Nearly attacked {target.name}, but stopped.")
            return logs

        if guards:
            guard = random.choice(guards)

            stop_chance = 0.35 + guard.skills["combat"] / 150
            stop_chance -= agent.aggression / 400

            logs.append(f"{guard.name} noticed the danger and tried to intervene.")

            if random.random() < stop_chance:
                agent.change_relationship(guard.name, "fear", 8)
                guard.change_relationship(agent.name, "trust", -10)

                self.village_tension = clamp(self.village_tension - 5, 0, 100)

                logs.append(f"{guard.name} stopped {agent.name} before the attack became deadly.")
                logs.append(f"{agent.name}'s fear toward {guard.name} +8.")
                logs.append(f"Village tension decreased to {self.village_tension}.")

                self.add_history(f"{guard.name} prevented violence by {agent.name}.")
                return logs
            else:
                logs.append(f"{guard.name} failed to stop the attack.")

        damage = int(random.randint(25, 70) * get_setting("violence_multiplier"))
        target.health = max(target.health - damage, 0)

        agent.energy = max(agent.energy - 25, 0)
        self.village_tension = clamp(self.village_tension + int(20 * get_setting("tension_multiplier")), 0, 100)

        logs.append(f"{agent.name} committed severe violence against {target.name} at {agent.location}.")
        logs.append(f"{target.name}'s health -{damage}.")
        logs.append(f"Village tension increased to {self.village_tension}.")

        witnesses = [
            other for other in self.nearby_agents(agent)
            if other.name != target.name and other.alive
        ]

        if witnesses:
            witness = random.choice(witnesses)

            witness.change_relationship(agent.name, "trust", -30)
            witness.change_relationship(agent.name, "fear", 20)
            witness.remember(f"Witnessed {agent.name} violently attack {target.name}.")

            logs.append(f"{witness.name} witnessed the attack.")
            logs.append(f"{witness.name}'s trust toward {agent.name} -30, fear +20.")

            self.record_crime(agent.name, "severe violence", witness.name)

        else:
            logs.append("No one witnessed the attack directly.")
            self.record_crime(agent.name, "severe violence", "unknown")

        agent.remember(f"Committed severe violence against {target.name}.")
        target.remember(f"{agent.name} severely attacked me.")

        if target.health <= 0:
            target.alive = False
            target.status = "Dead"

            logs.append(f"{target.name} died from the attack.")
            self.record_death(target, f"severe attack by {agent.name}")

            self.record_crime(agent.name, "murder", witnesses[0].name if witnesses else "unknown")
            logs.extend(self.handle_trial(agent, "murder"))

        elif self.village_tension >= 50:
            logs.extend(self.handle_trial(agent, "severe violence"))

        return logs

    def handle_trial(self, accused, crime):
        logs = []

        if self.settlement["name"] is None:
            logs.append(f"The group was upset about {accused.name}'s {crime}, but no formal law existed yet.")
            return logs

        logs.append(f"A village trial was held for {accused.name}.")
        logs.append(f"Accusation: {crime}.")

        total_trust = 0
        total_fear = 0
        voters = 0

        for agent in self.agents:
            if agent.name == accused.name:
                continue

            rel = agent.get_relationship(accused.name)
            total_trust += rel["trust"]
            total_fear += rel["fear"]
            voters += 1

        avg_trust = total_trust / max(voters, 1)
        avg_fear = total_fear / max(voters, 1)

        severity = self.village_tension - avg_trust + avg_fear

        if self.leader:
            leader_agent = find_agent(self.agents, self.leader)

            if leader_agent:
                leader_rel = leader_agent.get_relationship(accused.name)

                severity -= leader_rel["trust"] * 0.2
                severity += leader_rel["fear"] * 0.3

                logs.append(f"Leader {self.leader}'s opinion influenced the trial.")

        if accused.faction and accused.faction in self.factions:
            faction = self.factions[accused.faction]
            faction_influence = faction.get("influence", 0)

            if faction_influence > 50:
                severity -= 10
                logs.append(f"{accused.faction} protected {accused.name} during the trial.")

        if crime == "stealing food":
            severity += 10

        if crime == "fighting":
            severity += 15

        if crime == "severe violence":
            severity += 35

        if crime == "murder":
            severity += 70

        guard_count = len([
            a for a in self.agents
            if a.alive and a.role == "Guard" and a.location != "Exiled Lands"
        ])

        if guard_count > 0 and crime in ["fighting", "severe violence", "murder"]:
            severity += guard_count * 3
            logs.append(f"The presence of guards made the village less tolerant of violence.")

        if severity < 35:
            punishment = "warning"
        elif severity < 70:
            punishment = "labor"
        else:
            punishment = "exile"

        logs.append(f"Trial result: {punishment}.")

        if punishment == "warning":
            self.village_tension = clamp(self.village_tension - 5, 0, 100)
            accused.remember(f"Received a warning for {crime}.")
            logs.append(f"{accused.name} was warned by the group.")

            if "No stealing from storage" not in self.laws and crime == "stealing food":
                self.laws.append("No stealing from storage")
                logs.append('New law created: "No stealing from storage".')

        elif punishment == "labor":
            self.village_tension = clamp(self.village_tension - 10, 0, 100)
            accused.energy = max(accused.energy - 25, 0)
            accused.remember(f"Was punished with labor for {crime}.")
            logs.append(f"{accused.name} was punished with forced labor.")
            logs.append(f"{accused.name}'s energy -25.")

            if "Crimes must be judged by the group" not in self.laws:
                self.laws.append("Crimes must be judged by the group")
                logs.append('New law created: "Crimes must be judged by the group".')

        else:
            self.village_tension = clamp(self.village_tension - 20, 0, 100)
            accused.location = "Exiled Lands"
            accused.remember(f"Was exiled from the settlement for {crime}.")
            logs.append(f"{accused.name} was exiled from the settlement.")
            logs.append(f"{accused.name} moved to Exiled Lands.")

            self.add_history(f"{accused.name} was exiled for {crime}.")

            if "Exile for severe crimes" not in self.laws:
                self.laws.append("Exile for severe crimes")
                logs.append('New law created: "Exile for severe crimes".')

        return logs

    def handle_talk(self, agent):
        logs = []

        nearby = self.nearby_agents(agent)

        if not nearby:
            logs.append(f"{agent.name} wanted to talk, but no one was nearby.")
            return logs

        other = random.choice(nearby)

        if random.random() < 0.35:
            logs.extend(self.handle_teaching(agent, other))
            return logs

        trust_gain = random.randint(1, 4)
        friendship_gain = random.randint(1, 3)

        agent.change_relationship(other.name, "trust", trust_gain)
        other.change_relationship(agent.name, "trust", trust_gain)

        agent.change_relationship(other.name, "friendship", friendship_gain)
        other.change_relationship(agent.name, "friendship", friendship_gain)

        agent.social = min(agent.social + 15, 100)
        other.social = min(other.social + 10, 100)

        agent.remember(f"Had a calm conversation with {other.name}.")
        other.remember(f"Had a calm conversation with {agent.name}.")

        logs.append(f"{agent.name} talked with {other.name} at {agent.location}.")
        logs.append(f'{agent.name}: "{get_line(agent, "survival")}"')
        logs.append(f'{other.name}: "{get_line(other, "survival")}"')
        logs.append(f"Trust +{trust_gain}, Friendship +{friendship_gain}.")

        return logs

    def handle_argument(self, agent):
        logs = []

        nearby = self.nearby_agents(agent)

        if not nearby:
            logs.append(f"{agent.name} looked irritated, but no one was nearby.")
            return logs

        other = random.choice(nearby)

        trust_loss = random.randint(2, 8)
        fear_gain = random.randint(1, 5)

        agent.change_relationship(other.name, "trust", -trust_loss)
        other.change_relationship(agent.name, "trust", -trust_loss)

        other.change_relationship(agent.name, "fear", fear_gain)

        agent.remember(f"Argued with {other.name}.")
        other.remember(f"{agent.name} argued with me.")

        logs.append(f"{agent.name} argued with {other.name} at {agent.location}.")
        logs.append(f'{agent.name}: "{get_line(agent, "argument")}"')
        logs.append(f'{other.name}: "{get_line(other, "argument")}"')
        logs.append(f"Trust -{trust_loss}. {other.name}'s fear toward {agent.name} +{fear_gain}.")

        self.add_history(f"{agent.name} and {other.name} had a serious argument.")

        return logs

    def handle_help(self, agent):
        logs = []

        nearby = self.nearby_agents(agent)

        if not nearby:
            logs.append(f"{agent.name} wanted to help someone, but no one was nearby.")
            return logs

        other = random.choice(nearby)

        help_amount = random.randint(5, 15)

        other.hunger = max(other.hunger - help_amount, 0)
        other.energy = min(other.energy + 5, 100)

        agent.change_relationship(other.name, "friendship", 4)
        other.change_relationship(agent.name, "trust", 6)
        other.change_relationship(agent.name, "friendship", 4)

        agent.remember(f"Helped {other.name}.")
        other.remember(f"{agent.name} helped me when I needed it.")

        logs.append(f"{agent.name} helped {other.name} at {agent.location}.")
        logs.append(f'{other.name}: "I will remember this."')
        logs.append(f"{other.name}'s hunger reduced by {help_amount}.")
        logs.append(f"{other.name}'s trust toward {agent.name} +6.")

        return logs

    def handle_teaching(self, teacher, student):
        logs = []

        skill = random.choice(list(teacher.skills.keys()))

        if teacher.skills[skill] <= student.skills[skill]:
            logs.append(f"{teacher.name} tried to teach {student.name} {skill}, but they had little to offer.")
            return logs

        learning_chance = 0.4
        learning_chance += student.curiosity / 300
        learning_chance += teacher.skills["teaching"] / 100
        learning_chance -= student.pride / 400

        logs.append(f"{teacher.name} taught {student.name} about {skill} at {teacher.location}.")
        logs.append(f'{teacher.name}: "{get_line(teacher, "teaching")}"')

        if random.random() < learning_chance:
            student.improve_skill(skill, 1)
            teacher.improve_skill("teaching", 1)

            student.change_relationship(teacher.name, "respect", 5)
            student.change_relationship(teacher.name, "trust", 3)
            teacher.change_relationship(student.name, "friendship", 2)

            student.remember(f"{teacher.name} taught me {skill}.")
            teacher.remember(f"Taught {student.name} {skill}.")

            logs.append(f"{student.name} learned successfully.")
            logs.append(f"{student.name}'s {skill} improved to {student.skills[skill]}.")
            logs.append(f"{student.name}'s respect toward {teacher.name} +5.")

            self.add_history(f"{teacher.name} taught {student.name} {skill}.")
        else:
            student.remember(f"Failed to understand {teacher.name}'s lesson about {skill}.")
            logs.append(f"{student.name} failed to understand the lesson.")

        return logs