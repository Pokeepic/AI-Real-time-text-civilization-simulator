import random

from observer_world.world import LOCATIONS


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

            logs.append(
                f"{agent.name} | {agent.location} | {action}"
            )

        self.hour += 1

        if self.hour >= 24:
            self.hour = 0
            self.day += 1

        return logs