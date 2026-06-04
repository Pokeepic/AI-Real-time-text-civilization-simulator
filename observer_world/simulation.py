import random

from world import LOCATIONS


class Simulation:
    def __init__(self, agents):
        self.agents = agents
        self.day = 1
        self.hour = 8

    def tick(self):
        logs = []

        for agent in self.agents:
            agent.update_needs()
            action = agent.choose_action()

            if action == "explore":
                new_location = random.choice(LOCATIONS)
                agent.location = new_location
                logs.append(f"{agent.name} moved to {agent.location}.")

            elif action == "gather food":
                food_found = random.randint(5, 20)
                agent.hunger = max(agent.hunger - food_found, 0)
                logs.append(f"{agent.name} gathered food at {agent.location}. Hunger -{food_found}.")

            elif action == "sleep":
                agent.energy = min(agent.energy + 30, 100)
                logs.append(f"{agent.name} slept at {agent.location}. Energy restored.")

            elif action == "talk":
                logs.extend(self.handle_talk(agent))

            else:
                logs.append(f"{agent.name} stayed at {agent.location} and chose to {action}.")

        self.hour += 1

        if self.hour >= 24:
            self.hour = 0
            self.day += 1

        return logs

    def handle_talk(self, agent):
        logs = []

        nearby_agents = [
            other for other in self.agents
            if other.name != agent.name and other.location == agent.location
        ]

        if not nearby_agents:
            logs.append(f"{agent.name} wanted to talk, but no one was nearby.")
            return logs

        other = random.choice(nearby_agents)

        conversation_type = self.choose_conversation(agent, other)

        if conversation_type == "friendly":
            trust_gain = random.randint(1, 5)
            agent.change_trust(other.name, trust_gain)
            other.change_trust(agent.name, trust_gain)

            agent.social = min(agent.social + 15, 100)
            other.social = min(other.social + 10, 100)

            memory_a = f"Had a friendly talk with {other.name}."
            memory_b = f"Had a friendly talk with {agent.name}."

            agent.remember(memory_a)
            other.remember(memory_b)

            logs.append(f"{agent.name} talked with {other.name} at {agent.location}.")
            logs.append(f'{agent.name}: "We should work together if we want to survive."')
            logs.append(f'{other.name}: "I agree. Alone, this place feels too large."')
            logs.append(f"Trust increased between {agent.name} and {other.name} by {trust_gain}.")

        elif conversation_type == "argument":
            trust_loss = random.randint(1, 7)
            agent.change_trust(other.name, -trust_loss)
            other.change_trust(agent.name, -trust_loss)

            memory_a = f"Argued with {other.name}."
            memory_b = f"Argued with {agent.name}."

            agent.remember(memory_a)
            other.remember(memory_b)

            logs.append(f"{agent.name} argued with {other.name} at {agent.location}.")
            logs.append(f'{agent.name}: "You never listen when it matters."')
            logs.append(f'{other.name}: "And you think shouting makes you right?"')
            logs.append(f"Trust decreased between {agent.name} and {other.name} by {trust_loss}.")

        return logs

    def choose_conversation(self, agent, other):
        aggression_average = (agent.aggression + other.aggression) / 2
        kindness_average = (agent.kindness + other.kindness) / 2

        if aggression_average > kindness_average and random.random() < 0.5:
            return "argument"

        return "friendly"