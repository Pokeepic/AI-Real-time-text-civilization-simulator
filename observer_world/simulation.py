import random

from world import LOCATIONS


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

        self.settlement = {
            "name": None,
            "buildings": [],
            "shelter_progress": 0
        }
        
        self.village_tension = 0
        self.laws = []
        self.crime_records = {}
        self.leader = None
        self.weather = "Clear"
        self.season = "Spring"
        self.death_records = []
        self.memorials = []

    def add_history(self, event):
        record = f"Day {self.day}, {self.hour}:00 — {event}"
        self.world_history.append(record)

        if len(self.world_history) > 50:
            self.world_history.pop(0)

    def tick(self):
        logs = []

        if self.hour == 6:
            self.update_season()
            self.update_weather()
            logs.append(f"Weather changed: {self.weather}. Season: {self.season}.")

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

                agent.hunger = max(agent.hunger - food_found // 2, 0)
                self.resources["food"] += food_found // 2
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

                self.resources["wood"] += wood
                self.resources["stone"] += stone

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

            else:
                logs.append(f"{agent.name} stayed at {agent.location} and chose to {action}.")

        self.handle_family_growth(logs)
        self.handle_aging(logs)
        self.check_leadership(logs)

        self.hour += 1

        if self.hour >= 24:
            self.hour = 0
            self.day += 1
            logs.append(f"--- A new day begins. Day {self.day}. ---")

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
            if random.random() < 0.08:
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
        else:
            agent.role = "Wanderer"

        if self.leader == agent.name:
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
                if random.random() < 0.01:
                    agent.pregnant = True
                    agent.pregnancy_timer = 5

                    logs.append(f"{agent.name} and {agent.partner}'s family may grow soon.")
                    self.add_history(f"{agent.name} and {agent.partner} are expecting a child.")

            elif agent.pregnant:
                agent.pregnancy_timer -= 1

                if agent.pregnancy_timer <= 0:
                    child_name = self.generate_child_name()

                    from agent import Agent
                    child = Agent(child_name)

                    partner = next((a for a in self.agents if a.name == agent.partner), None)

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

            if self.day % 5 == 0:
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
                    if random.random() < 0.08:
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

    def handle_build(self, agent):
        logs = []

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
                self.settlement["name"] = "First Hearth"

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

        self.village_tension += 5

        agent.remember(f"Stole {stolen} food from storage.")

        logs.append(f"{agent.name} secretly stole {stolen} food from storage.")
        logs.append(f"Village tension increased to {self.village_tension}.")

        caught_chance = 0.35

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

        self.village_tension += random.randint(8, 18)

        agent.energy = max(agent.energy - 15, 0)
        other.energy = max(other.energy - 20, 0)

        damage = random.randint(5, 20)
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
            leader_agent = next((a for a in self.agents if a.name == self.leader), None)

            if leader_agent:
                leader_rel = leader_agent.get_relationship(accused.name)

                severity -= leader_rel["trust"] * 0.2
                severity += leader_rel["fear"] * 0.3

                logs.append(f"Leader {self.leader}'s opinion influenced the trial.")

        if crime == "stealing food":
            severity += 10

        if crime == "fighting":
            severity += 15

        if severity < 35:
            punishment = "warning"
        elif severity < 70:
            punishment = "labor"
        else:
            punishment = "exile"

        logs.append(f"Trial result: {punishment}.")

        if punishment == "warning":
            self.village_tension = max(self.village_tension - 5, 0)
            accused.remember(f"Received a warning for {crime}.")
            logs.append(f"{accused.name} was warned by the group.")

            if "No stealing from storage" not in self.laws and crime == "stealing food":
                self.laws.append("No stealing from storage")
                logs.append('New law created: "No stealing from storage".')

        elif punishment == "labor":
            self.village_tension = max(self.village_tension - 10, 0)
            accused.energy = max(accused.energy - 25, 0)
            accused.remember(f"Was punished with labor for {crime}.")
            logs.append(f"{accused.name} was punished with forced labor.")
            logs.append(f"{accused.name}'s energy -25.")

            if "Crimes must be judged by the group" not in self.laws:
                self.laws.append("Crimes must be judged by the group")
                logs.append('New law created: "Crimes must be judged by the group".')

        else:
            self.village_tension = max(self.village_tension - 20, 0)
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
        logs.append(f'{agent.name}: "We should understand this place better."')
        logs.append(f'{other.name}: "Then we should share what we learn."')
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
        logs.append(f'{agent.name}: "You are slowing everyone down."')
        logs.append(f'{other.name}: "Say that again and see what happens."')
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