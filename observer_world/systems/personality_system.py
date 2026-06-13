"""
Personality system for Observer World.
"""
import random

def handle_journals(sim, logs):
    if sim.hour != 23:
        return

    for agent in sim.agents:
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
            agent.write_journal(sim.day, sim.hour, thought + emotional_note)
            logs.append(f"{agent.name} wrote a journal entry.")

def handle_personality_drift(sim, logs):
    if sim.hour != 0:
        return

    for agent in sim.agents:
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