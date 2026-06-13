"""
Life goal system for Observer World.
"""

import random


def assign_life_goal(sim, agent):
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

def update_life_goals(sim, logs):
    if sim.hour != 7:
        return

    for agent in sim.agents:
        if not agent.alive:
            continue

        sim.assign_life_goal(agent)

        if random.random() < 0.05:
            old_goal = agent.life_goal
            agent.life_goal = None
            sim.assign_life_goal(agent)

            if old_goal != agent.life_goal:
                logs.append(f"{agent.name}'s life goal changed from {old_goal} to {agent.life_goal}.")
                agent.write_journal(
                    sim.day,
                    sim.hour,
                    f"My path feels different now. I want to {agent.life_goal}."
                )

def check_goal_progress(sim, logs):
    if sim.hour != 8:
        return

    for agent in sim.agents:
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
            agent.write_journal(sim.day, sim.hour, f"I feel I have fulfilled my goal: {goal}.")
            logs.append(f"{agent.name} fulfilled their life goal: {goal}.")
            sim.add_history(f"{agent.name} fulfilled life goal: {goal}.")

            agent.life_goal = None
            sim.assign_life_goal(agent)