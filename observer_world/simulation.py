import random

from world import LOCATIONS
from dialogue import get_line
from config import CONFIG, get_setting, get_scenario, ACTIVE_SCENARIO
from utils import find_agent, clamp
from error_handler import safe_execute
# Modular family systems
from systems.family_system import (
    handle_family_reunions as family_reunions_system,
    handle_sibling_interactions as sibling_interactions_system,
    handle_parent_child_bonds as parent_child_bonds_system,
    deepen_partner_bonds as deepen_partner_bonds_system,
    handle_mourning as mourning_system,
    handle_family_growth as family_growth_system,
    handle_aging as aging_system,
    update_family_reputation as family_reputation_system,
    apply_family_reputation_effects as family_reputation_effects_system,
    record_family_alliance as family_alliance_system,
    record_family_rivalry as family_rivalry_system,
    apply_family_rivalry_effects as family_rivalry_effects_system,
)
# Modular social systems
from systems.social_system import (
    check_social_changes as social_changes_system,
    spread_gossip as gossip_system,
    update_emotional_states as emotional_states_system,
    update_crushes as crushes_system,
    handle_confessions as confessions_system,
    handle_rejection_recovery as rejection_recovery_system,
    get_memory_line as memory_line_system,
    get_relationship_line as relationship_line_system,
)
# Modular settlement systems
from systems.settlement_system import (
    update_settlement_stage as settlement_stage_system,
    choose_village_project as village_project_system,
    work_on_project as work_on_project_system,
    apply_building_effects as building_effects_system,
    apply_extra_settlement_effects as extra_settlement_effects_system,
    handle_extra_settlement_growth as extra_settlement_growth_system,
    update_extra_settlement_leaders as extra_settlement_leaders_system,
    update_extra_settlement_culture as extra_settlement_culture_system,
    update_extra_settlement_laws as extra_settlement_laws_system,
    handle_exile_settlements as exile_settlements_system,
    handle_settlement_relations as settlement_relations_system,
    handle_migration as migration_system,
    handle_diplomacy as diplomacy_system,
    calculate_settlement_power as settlement_power_system,
    handle_settlement_war as settlement_war_system,
    apply_war_losses as war_losses_system,
)
# Modular technology systems
from systems.technology_system import (
    generate_research as generate_research_system,
    unlock_technology as unlock_technology_system,
    generate_extra_settlement_research as extra_research_system,
    unlock_extra_settlement_technology as extra_technology_system,
)
# Modular culture systems
from systems.culture_system import (
    update_culture as culture_update_system,
    get_culture_identity as culture_identity_system,
    create_tradition as create_tradition_system,
    run_traditions as run_traditions_system,
    update_beliefs as update_beliefs_system,
    get_belief_identity as belief_identity_system,
    update_era as update_era_system,
    unlock_milestone as unlock_milestone_system,
    check_milestones as check_milestones_system,
)

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
        self.family_reputation = {}
        self.family_rivalries = {}
        self.family_alliances = {}
        self.notifications = []
        self.watchlist = []
        self.family_watchlist = []
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
        unlock_milestone_system(self, key, text, logs)

    def update_settlement_stage(self, logs):
        settlement_stage_system(self, logs)

    def update_culture(self, logs):
        culture_update_system(self, logs)

    def get_culture_identity(self):
        return culture_identity_system(self)

    def create_tradition(self, logs):
        create_tradition_system(self, logs)

    def run_traditions(self, logs):
        run_traditions_system(self, logs)

    def update_beliefs(self, logs):
        update_beliefs_system(self, logs)

    def get_belief_identity(self):
        return belief_identity_system(self)

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
        exile_settlements_system(self, logs)

    def get_agent_settlement(self, agent):
        return self.get_extra_settlement_by_name(agent.location)

    def handle_settlement_relations(self, logs):
        settlement_relations_system(self, logs)

    def handle_migration(self, logs):
        migration_system(self, logs)

    def handle_extra_settlement_growth(self, logs):
        extra_settlement_growth_system(self, logs)

    def update_extra_settlement_leaders(self, logs):
        extra_settlement_leaders_system(self, logs)

    def update_extra_settlement_culture(self, logs):
        extra_settlement_culture_system(self, logs)

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
        extra_settlement_laws_system(self, logs)

    def calculate_settlement_power(self, settlement_name):
        return settlement_power_system(self, settlement_name)

    def handle_diplomacy(self, logs):
        diplomacy_system(self, logs)

    def handle_settlement_war(self, logs):
        settlement_war_system(self, logs)

    def apply_war_losses(self, settlement_name, logs):
        war_losses_system(self, settlement_name, logs)

    def generate_research(self, logs):
        generate_research_system(self, logs)

    def unlock_technology(self, logs):
        unlock_technology_system(self, logs)

    def generate_extra_settlement_research(self, logs):
        extra_research_system(self, logs)

    def unlock_extra_settlement_technology(self, logs):
        extra_technology_system(self, logs)

    def handle_journals(self, logs):
        if self.hour != 23:
            return

        for agent in self.agents:
            if not agent.alive:
                continue

            thought = None

            best_friend = agent.get_best_friend()
            rival = agent.get_rival()
            favorite_place = agent.get_favorite_place()

            recent_memories = " ".join(agent.memories[-5:]).lower()

            if "mourned the death" in recent_memories:
                thought = "Someone important is gone. The world feels quieter now."

            elif agent.health < 40:
                thought = "I do not feel well. I wonder if I will survive much longer."

            elif agent.hunger > 80:
                thought = "Food has been on my mind all day."

            elif agent.partner:
                thought = f"I thought about {agent.partner} today. I hope we can keep our family safe."

            elif best_friend:
                thought = f"I am grateful for {best_friend}. Trust is rare here."

            elif rival:
                thought = f"I cannot stop thinking about {rival}. Some wounds do not close easily."

            elif favorite_place:
                thought = f"I feel drawn to {favorite_place}. Something about that place stays with me."

            elif agent.memories:
                thought = f"I keep remembering: {agent.memories[-1]}"

            elif agent.faction:
                thought = f"My place in {agent.faction} may shape my future."

            elif agent.role == "Leader":
                thought = "Everyone looks to me, but leadership is heavier than it seems."

            if thought:
                emotional_note = f" Emotion: {agent.emotional_state}."
                agent.write_journal(self.day, self.hour, thought + emotional_note)
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
            if "mourned the death" in recent_memories:
                agent.kindness = min(agent.kindness + 1, 100)
                agent.social = max(agent.social - 2, 0)

                if agent.aggression > 50:
                    agent.aggression = max(agent.aggression - 1, 1)

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
        update_era_system(self, logs)

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
        check_milestones_system(self, logs)

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
                self.record_death(agent, "hunger or exhaustion", logs)
                continue

            self.apply_weather_effects(agent, logs)

            if not agent.alive:
                self.record_death(agent, "weather exposure", logs)
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

            elif action == "visit favorite place":
                favorite = agent.get_favorite_place()

                if favorite:
                    agent.location = favorite
                    agent.social = min(agent.social + 5, 100)
                    agent.energy = max(agent.energy - 2, 0)

                    logs.append(f"{agent.name} visited their favorite place: {favorite}.")
                else:
                    logs.append(f"{agent.name} wanted to visit a favorite place, but had none.")

            else:
                logs.append(f"{agent.name} stayed at {agent.location} and chose to {action}.")

        systems = [
        ("handle_family_growth", self.handle_family_growth),
        ("handle_aging", self.handle_aging),
        ("choose_village_project", self.choose_village_project),
        ("check_leadership", self.check_leadership),
        ("update_settlement_stage", self.update_settlement_stage),
        ("update_culture", self.update_culture),
        ("create_tradition", self.create_tradition),
        ("run_traditions", self.run_traditions),
        ("update_beliefs", self.update_beliefs),
        ("update_factions", self.update_factions),
        ("update_faction_influence", self.update_faction_influence),
        ("handle_faction_conflict", self.handle_faction_conflict),
        ("handle_rebellion", self.handle_rebellion),
        ("handle_exile_settlements", self.handle_exile_settlements),
        ("handle_settlement_relations", self.handle_settlement_relations),
        ("handle_migration", self.handle_migration),
        ("handle_extra_settlement_growth", self.handle_extra_settlement_growth),
        ("update_extra_settlement_leaders", self.update_extra_settlement_leaders),
        ("update_extra_settlement_culture", self.update_extra_settlement_culture),
        ("update_extra_settlement_laws", self.update_extra_settlement_laws),
        ("handle_diplomacy", self.handle_diplomacy),
        ("handle_settlement_war", self.handle_settlement_war),
        ("generate_research", self.generate_research),
        ("unlock_technology", self.unlock_technology),
        ("generate_extra_settlement_research", self.generate_extra_settlement_research),
        ("unlock_extra_settlement_technology", self.unlock_extra_settlement_technology),
        ("update_emotional_states", self.update_emotional_states),
        ("update_crushes", self.update_crushes),
        ("handle_confessions", self.handle_confessions),
        ("handle_rejection_recovery", self.handle_rejection_recovery),
        ("deepen_partner_bonds", self.deepen_partner_bonds),
        ("handle_family_reunions", self.handle_family_reunions),
        ("handle_sibling_interactions", self.handle_sibling_interactions),
        ("handle_parent_child_bonds", self.handle_parent_child_bonds),
        ("update_family_reputation", self.update_family_reputation),
        ("handle_journals", self.handle_journals),
        ("handle_personality_drift", self.handle_personality_drift),
        ("update_life_goals", self.update_life_goals),
        ("check_goal_progress", self.check_goal_progress),
        ("update_era", self.update_era),
        ("check_social_changes", self.check_social_changes),
        ("spread_gossip", self.spread_gossip),
        ("apply_family_reputation_effects", self.apply_family_reputation_effects),
        ("apply_family_rivalry_effects", self.apply_family_rivalry_effects),
        ("check_milestones", self.check_milestones),
    ]

        for name, system in systems:
            safe_execute(self, logs, name, system)

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
                    self.record_death(agent, "exposure", logs)

    def record_death(self, agent, cause, logs=None):
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
        self.notify(f"{agent.name} died. Cause: {cause}.", "Death")
        self.notify(f"{agent.name} died ({cause}).", "Death")
        self.notify_agent_event(
            agent.name,
            f"died ({cause})."
        )
        self.notify_family_event(
            agent.surname,
            f"{agent.get_full_name()} died."
        )

        mourning_logs = []
        self.handle_mourning(agent, mourning_logs)

        for mourning_log in mourning_logs:
            self.add_history(mourning_log)

        if logs is not None:
            logs.extend(mourning_logs)

    def apply_building_effects(self, logs):
        building_effects_system(self, logs)

    def apply_extra_settlement_effects(self, logs):
        extra_settlement_effects_system(self, logs)

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

        bonded_patients = [
            patient for patient in patients
            if patient.name in medic.family
            or patient.name in medic.bonds
        ]

        if bonded_patients:
            patient = min(bonded_patients, key=lambda a: a.health)
        else:
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

        patient.add_bond(medic.name, "healed me")
        medic.add_bond(patient.name, "treated them")

        self.record_family_alliance(medic, patient, "healing")

        medic.set_emotion("Connected")
        patient.set_emotion("Connected")

        medic.add_location_affinity(medic.location, 2)
        patient.add_location_affinity(patient.location, 2)

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
        family_growth_system(self, logs)

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
        aging_system(self, logs)

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
                self.notify(f"{best_candidate.name} became leader of {self.settlement['name']}.", "Leadership")
                self.add_history(f"{best_candidate.name} became the first leader of {self.settlement['name']}.")
                self.notify_agent_event(
                    best_candidate.name,
                    "became leader."
                )
                self.notify_family_event(
                    best_candidate.surname,
                    f"{best_candidate.get_full_name()} became leader."
                )
            else:
                logs.append(f"Leadership changed from {old_leader} to {best_candidate.name}.")
                self.notify(f"Leadership changed from {old_leader} to {best_candidate.name}.", "Leadership")
                self.add_history(f"Leadership changed from {old_leader} to {best_candidate.name}.")
                self.notify_agent_event(
                    best_candidate.name,
                    "became leader."
                )
                self.notify_family_event(
                    best_candidate.surname,
                    f"{best_candidate.get_full_name()} became leader."
                )
    def nearby_agents(self, agent):
        return [
            other for other in self.agents
            if other.name != agent.name and other.location == agent.location
        ]

    def choose_village_project(self, logs):
        village_project_system(self, logs)

    def work_on_project(self, agent):
        return work_on_project_system(self, agent)

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

            witness.add_grudge(agent.name, "caught stealing food")

            self.record_family_rivalry(agent, witness, "stealing accusation")

            witness.set_emotion("Troubled")
            agent.set_emotion("Desperate")

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

        grudge_targets = [
            other for other in nearby
            if other.name in agent.grudges
        ]

        if grudge_targets:
            other = random.choice(grudge_targets)
        else:
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
            self.record_death(other, f"fight with {agent.name}", logs)
        else:
            logs.append(f"{other.name} was injured. Health -{damage}.")

        agent.remember(f"Fought with {other.name}.")
        other.remember(f"{agent.name} attacked me.")

        agent.add_grudge(other.name, "fight")
        other.add_grudge(agent.name, "fight")

        self.record_family_rivalry(agent, other, "fight")

        agent.set_emotion("Troubled")
        other.set_emotion("Suffering")

        agent.add_location_affinity(agent.location, -1)
        other.add_location_affinity(other.location, -1)

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

        self.record_family_rivalry(agent, target, "severe violence")

        agent.set_emotion("Troubled")
        target.set_emotion("Suffering")

        if target.health <= 0:
            target.alive = False
            target.status = "Dead"

            logs.append(f"{target.name} died from the attack.")
            self.record_death(target, f"severe attack by {agent.name}", logs)

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

        preferred_targets = [
            other for other in nearby
            if other.name == agent.crush
            or other.name in agent.bonds
            or other.name in agent.family
            or other.age < 18
        ]

        if preferred_targets:
            other = random.choice(preferred_targets)
        else:
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

        agent.add_location_affinity(agent.location, 1)
        other.add_location_affinity(other.location, 1)

        logs.append(f"{agent.name} talked with {other.name} at {agent.location}.")
        agent_relationship_line = self.get_relationship_line(agent, other)
        other_relationship_line = self.get_relationship_line(other, agent)

        agent_memory_line = self.get_memory_line(agent)
        other_memory_line = self.get_memory_line(other)

        if agent_relationship_line and random.random() < 0.5:
            logs.append(f'{agent.name}: "{agent_relationship_line}"')
        elif agent_memory_line and random.random() < 0.35:
            logs.append(f'{agent.name}: "{agent_memory_line}"')
        else:
            logs.append(f'{agent.name}: "{get_line(agent, "survival")}"')

        if other_relationship_line and random.random() < 0.5:
            logs.append(f'{other.name}: "{other_relationship_line}"')
        elif other_memory_line and random.random() < 0.35:
            logs.append(f'{other.name}: "{other_memory_line}"')
        else:
            logs.append(f'{other.name}: "{get_line(other, "survival")}"')

        return logs

    def handle_argument(self, agent):
        logs = []

        nearby = self.nearby_agents(agent)

        if not nearby:
            logs.append(f"{agent.name} looked irritated, but no one was nearby.")
            return logs

        grudge_targets = [
            other for other in nearby
            if other.name in agent.grudges
        ]

        if grudge_targets:
            other = random.choice(grudge_targets)
        else:
            other = random.choice(nearby)

        trust_loss = random.randint(2, 8)
        fear_gain = random.randint(1, 5)

        agent.change_relationship(other.name, "trust", -trust_loss)
        other.change_relationship(agent.name, "trust", -trust_loss)

        other.change_relationship(agent.name, "fear", fear_gain)

        agent.remember(f"Argued with {other.name}.")
        other.remember(f"{agent.name} argued with me.")

        agent.add_grudge(other.name, "argument")
        other.add_grudge(agent.name, "argument")

        self.record_family_rivalry(agent, other, "argument")

        agent.set_emotion("Troubled")
        other.set_emotion("Troubled")

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

        bond_targets = [
            other for other in nearby
            if other.name in agent.family
            or other.name in agent.bonds
            or other.name == agent.crush
        ]

        if bond_targets:
            other = random.choice(bond_targets)
        else:
            other = random.choice(nearby)

        help_amount = random.randint(5, 15)

        other.hunger = max(other.hunger - help_amount, 0)
        other.energy = min(other.energy + 5, 100)

        agent.change_relationship(other.name, "friendship", 4)
        other.change_relationship(agent.name, "trust", 6)
        other.change_relationship(agent.name, "friendship", 4)

        agent.remember(f"Helped {other.name}.")
        other.remember(f"{agent.name} helped me when I needed it.")

        other.add_bond(agent.name, "helped me")
        agent.add_bond(other.name, "helped them")

        self.record_family_alliance(agent, other, "help")

        agent.set_emotion("Connected")
        other.set_emotion("Connected")

        agent.add_location_affinity(agent.location, 2)
        other.add_location_affinity(other.location, 2)

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

            student.add_bond(teacher.name, "taught me")
            teacher.add_bond(student.name, "learned from me")

            self.record_family_alliance(teacher, student, "teaching")

            teacher.set_emotion("Connected")
            student.set_emotion("Connected")

            logs.append(f"{student.name} learned successfully.")
            logs.append(f"{student.name}'s {skill} improved to {student.skills[skill]}.")
            logs.append(f"{student.name}'s respect toward {teacher.name} +5.")

            self.add_history(f"{teacher.name} taught {student.name} {skill}.")
        else:
            student.remember(f"Failed to understand {teacher.name}'s lesson about {skill}.")
            logs.append(f"{student.name} failed to understand the lesson.")

        return logs
    
    def check_social_changes(self, logs):
        social_changes_system(self, logs)

    def handle_mourning(self, dead_agent, logs):
        mourning_system(self, dead_agent, logs)

    def spread_gossip(self, logs):
        gossip_system(self, logs)

    def get_memory_line(self, agent):
        return memory_line_system(self, agent)
    
    def get_relationship_line(self, speaker, listener):
        return relationship_line_system(self, speaker, listener)
    
    def update_emotional_states(self, logs):
        emotional_states_system(self, logs)

    def update_crushes(self, logs):
        crushes_system(self, logs)
    
    def handle_confessions(self, logs):
        confessions_system(self, logs)
    
    def handle_rejection_recovery(self, logs):
        rejection_recovery_system(self, logs)
    
    def deepen_partner_bonds(self, logs):
        deepen_partner_bonds_system(self, logs)
    
    def handle_family_reunions(self, logs):
        family_reunions_system(self, logs)

    def handle_sibling_interactions(self, logs):
        sibling_interactions_system(self, logs)

    def handle_parent_child_bonds(self, logs):
        parent_child_bonds_system(self, logs)

    def generate_surname(self):
        roots = ["Hearth", "River", "Stone", "Ash", "Moon", "Sun", "Vale", "Wolf", "Oak", "Storm"]
        endings = ["born", "field", "watch", "wood", "crest", "ward", "line", "keeper"]

        return random.choice(roots) + random.choice(endings)
    
    def update_family_reputation(self, logs):
        family_reputation_system(self, logs)

    def apply_family_reputation_effects(self, logs):
        family_reputation_effects_system(self, logs)

    def record_family_rivalry(self, agent_a, agent_b, reason):
        family_rivalry_system(self, agent_a, agent_b, reason)

    def apply_family_rivalry_effects(self, logs):
        family_rivalry_effects_system(self, logs)

    def record_family_alliance(self, agent_a, agent_b, reason):
        family_alliance_system(self, agent_a, agent_b, reason)

    def notify(self, message, category="General"):
        self.notifications.append({
            "day": self.day,
            "hour": self.hour,
            "category": category,
            "message": message,
        })

        if len(self.notifications) > 100:
            self.notifications.pop(0)

    def notify_agent_event(self, agent_name, message):
        if agent_name in self.watchlist:
            self.notify(
                f"[WATCHLIST] {agent_name}: {message}",
                "Watchlist"
            )

    def notify_family_event(self, surname, message):
        if surname and surname in self.family_watchlist:
            self.notify(
                f"[{surname.upper()}] {message}",
                "Family Watchlist"
            )