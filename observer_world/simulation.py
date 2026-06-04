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

            else:
                logs.append(f"{agent.name} stayed at {agent.location} and chose to {action}.")

        self.hour += 1

        if self.hour >= 24:
            self.hour = 0
            self.day += 1
            logs.append(f"--- A new day begins. Day {self.day}. ---")

        return logs

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