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

    def add_history(self, event):
        record = f"Day {self.day}, {self.hour}:00 — {event}"
        self.world_history.append(record)

        if len(self.world_history) > 50:
            self.world_history.pop(0)

    def tick(self):
        logs = []

        for agent in self.agents:
            agent.update_needs()
            action = agent.choose_action()

            if action == "explore":
                new_location = random.choice(LOCATIONS)
                agent.location = new_location
                logs.append(f"{agent.name} explored and moved to {agent.location}.")

            elif action == "gather food":
                food_found = random.randint(5, 20) + agent.skills["hunting"]
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

            else:
                logs.append(f"{agent.name} stayed at {agent.location} and chose to {action}.")

        self.check_leadership(logs)

        self.hour += 1

        if self.hour >= 24:
            self.hour = 0
            self.day += 1
            logs.append(f"--- A new day begins. Day {self.day}. ---")

        return logs

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