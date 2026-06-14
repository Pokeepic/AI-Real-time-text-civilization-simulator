import random
from config import CONFIG, get_setting, get_scenario, ACTIVE_SCENARIO
from error_handler import safe_execute
from history_tracker import record_world_snapshot

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
# Modular crime and justice systems
from systems.crime_system import (
    record_crime as record_crime_system,
    handle_steal_food as steal_food_system,
    handle_fight as fight_system,
    handle_argument as argument_system,
    handle_severe_violence as severe_violence_system,
    handle_trial as trial_system,
)
# Modular economy systems
from systems.economy_system import (
    handle_trade as trade_system,
    handle_gamble as gamble_system,
    handle_repay_debt as repay_debt_system,
    handle_demand_debt as demand_debt_system,
)
# Modular health systems
from systems.health_system import (
    handle_heal as heal_system,
    apply_weather_effects as weather_effects_system,
    record_death as record_death_system,
    check_world_state as world_state_system,
)
# Modular agent action systems
from systems.agent_action_system import (
    handle_talk as talk_system,
    handle_help as help_system,
    handle_bond as bond_system,
    handle_learning as learning_system,
    handle_patrol as patrol_system,
    handle_teaching as teaching_system,
    handle_explore as explore_system,
    handle_sleep as sleep_system,
    handle_visit_favorite_place as visit_favorite_place_system,
    handle_practice as practice_system,
    handle_gather_food as gather_food_system,
    handle_gather_materials as gather_materials_system,
    handle_build as build_system,
)
# Modular world systems
from systems.world_system import (
    update_season as update_season_system,
    update_weather as update_weather_system,
    generate_world_name as world_name_system,
    generate_settlement_name as settlement_name_system,
    generate_child_name as child_name_system,
    generate_surname as surname_system,
    notify as notify_system,
    notify_agent_event as notify_agent_event_system,
    notify_family_event as notify_family_event_system,
    add_history as add_history_system,
    create_daily_chronicle as daily_chronicle_system,
)
# Modular faction systems
from systems.faction_system import (
    update_factions as update_factions_system,
    update_faction_influence as faction_influence_system,
    handle_faction_conflict as faction_conflict_system,
    handle_rebellion as rebellion_system,
)
# Modular leadership systems
from systems.leadership_system import (
    check_leadership as leadership_system,
)
# Modular life goal systems
from systems.life_goal_system import (
    assign_life_goal as assign_life_goal_system,
    update_life_goals as update_life_goals_system,
    check_goal_progress as check_goal_progress_system,
)
# Modular personality systems
from systems.personality_system import (
    handle_journals as journals_system,
    handle_personality_drift as personality_drift_system,
)
# Modular resource systems
from systems.resource_system import (
    consume_daily_food as consume_daily_food_system,
    spoil_excess_food as spoil_excess_food_system,
    enforce_storage_capacity as storage_capacity_system,
    enforce_material_storage_capacity as material_storage_capacity_system,
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
        return world_name_system(self)

    def generate_settlement_name(self):
        return settlement_name_system(self)

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
        update_factions_system(self, logs)

    def update_faction_influence(self, logs):
        faction_influence_system(self, logs)

    def handle_faction_conflict(self, logs):
        faction_conflict_system(self, logs)

    def handle_rebellion(self, logs):
        rebellion_system(self, logs)

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
        journals_system(self, logs)

    def handle_personality_drift(self, logs):
        personality_drift_system(self, logs)

    def assign_life_goal(self, agent):
        assign_life_goal_system(self, agent)

    def update_life_goals(self, logs):
        update_life_goals_system(self, logs)

    def check_goal_progress(self, logs):
        check_goal_progress_system(self, logs)

    def create_daily_chronicle(self, logs):
        daily_chronicle_system(self, logs)

    def update_era(self, logs):
        update_era_system(self, logs)

    def check_world_state(self, logs):
        world_state_system(self, logs)

    def check_milestones(self, logs):
        check_milestones_system(self, logs)

    def add_history(self, event):
        add_history_system(self, event)
    
    def handle_explore(self, agent):
        return explore_system(self, agent)
    
    def handle_sleep(self, agent):
        return sleep_system(self, agent)
    
    def handle_visit_favorite_place(self, agent):
        return visit_favorite_place_system(self, agent)
    
    def handle_practice(self, agent):
        return practice_system(self, agent)
    
    def handle_gather_food(self, agent):
        return gather_food_system(self, agent)
    
    def handle_gather_materials(self, agent):
        return gather_materials_system(self, agent)

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
                logs.extend(self.handle_explore(agent))

            elif action == "gather food":
                logs.extend(self.handle_gather_food(agent))

            elif action == "sleep":
                logs.extend(self.handle_sleep(agent))

            elif action == "talk":
                logs.extend(self.handle_talk(agent))

            elif action == "argue":
                logs.extend(self.handle_argument(agent))

            elif action == "help":
                logs.extend(self.handle_help(agent))

            elif action == "practice":
                logs.extend(self.handle_practice(agent))

            elif action == "gather materials":
                logs.extend(self.handle_gather_materials(agent))

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
                logs.extend(self.handle_visit_favorite_place(agent))

            else:
                logs.append(f"{agent.name} stayed at {agent.location} and chose to {action}.")

        systems = [
        ("consume_daily_food", self.consume_daily_food),
        ("spoil_excess_food", self.spoil_excess_food),
        ("enforce_storage_capacity", self.enforce_storage_capacity),
        ("enforce_material_storage_capacity", self.enforce_material_storage_capacity),
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
            record_world_snapshot(self)
            logs.append(f"--- A new day begins. Day {self.day}. ---")

        self.daily_events.extend(logs)

        if self.day != starting_day:
            self.create_daily_chronicle(logs)

        self.check_world_state(logs)

        return logs

    def update_season(self):
        update_season_system(self)

    def update_weather(self):
        update_weather_system(self)

    def apply_weather_effects(self, agent, logs):
        weather_effects_system(self, agent, logs)

    def record_death(self, agent, cause, logs=None):
        record_death_system(self, agent, cause, logs)

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

    def handle_heal(self, agent):
        return heal_system(self, agent)

    def handle_learning(self, agent):
        return learning_system(self, agent)

    def handle_trade(self, agent):
        return trade_system(self, agent)

    def handle_gamble(self, agent):
        return gamble_system(self, agent)

    def handle_repay_debt(self, agent):
        return repay_debt_system(self, agent)

    def handle_demand_debt(self, agent):
        return demand_debt_system(self, agent)

    def handle_bond(self, agent):
        return bond_system(self, agent)

    def handle_family_growth(self, logs):
        family_growth_system(self, logs)

    def generate_child_name(self):
        return child_name_system(self)

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
        leadership_system(self, logs)

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
        return build_system(self, agent)

    def handle_steal_food(self, agent):
        return steal_food_system(self, agent)

    def handle_fight(self, agent):
        return fight_system(self, agent)

    def record_crime(self, criminal_name, crime, witness_name):
        record_crime_system(self, criminal_name, crime, witness_name)

    def handle_patrol(self, agent):
        return patrol_system(self, agent)

    def handle_severe_violence(self, agent):
        return severe_violence_system(self, agent)

    def handle_trial(self, accused, crime):
        return trial_system(self, accused, crime)

    def handle_talk(self, agent):
        return talk_system(self, agent)

    def handle_argument(self, agent):
        return argument_system(self, agent)

    def handle_help(self, agent):
        return help_system(self, agent)

    def handle_teaching(self, teacher, student, logs):
        teaching_system(self, teacher, student, logs)
    
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
        return surname_system(self)
    
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
        notify_system(self, message, category)

    def notify_agent_event(self, agent_name, message):
        notify_agent_event_system(self, agent_name, message)

    def notify_family_event(self, surname, message):
        notify_family_event_system(self, surname, message)
    
    def consume_daily_food(self, logs):
        consume_daily_food_system(self, logs)

    def spoil_excess_food(self, logs):
        spoil_excess_food_system(self, logs)
    
    def enforce_storage_capacity(self, logs):
        storage_capacity_system(self, logs)

    def enforce_material_storage_capacity(self, logs):
        material_storage_capacity_system(self, logs)