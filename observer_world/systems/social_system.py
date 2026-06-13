import random

def check_social_changes(sim, logs):
    if sim.hour != 20:
        return

    for agent in sim.agents:
        if not agent.alive:
            continue

        current_best_friend = agent.get_best_friend()
        current_rival = agent.get_rival()

        if current_best_friend and current_best_friend != agent.known_best_friend:
            agent.known_best_friend = current_best_friend
            logs.append(f"{agent.name} now considers {current_best_friend} a close friend.")
            sim.add_history(f"{agent.name} became close friends with {current_best_friend}.")

        if current_rival and current_rival != agent.known_rival:
            agent.known_rival = current_rival
            logs.append(f"{agent.name} now sees {current_rival} as a rival.")
            sim.add_history(f"{agent.name} became rivals with {current_rival}.")

def spread_gossip(sim, logs):
    if sim.hour != 19:
        return

    recent_history = sim.world_history[-10:]

    gossip_topics = [
        event for event in recent_history
        if any(word in event.lower() for word in [
            "died", "crime", "trial", "leader", "war",
            "rebellion", "murder", "exiled", "born"
        ])
    ]

    if not gossip_topics:
        return

    for agent in sim.agents:
        if not agent.alive:
            continue

        nearby = sim.nearby_agents(agent)

        if not nearby:
            continue

        listener = random.choice(nearby)
        topic = random.choice(gossip_topics)

        agent.add_gossip(topic)
        listener.add_gossip(topic)

        agent.change_relationship(listener.name, "friendship", 1)
        listener.change_relationship(agent.name, "trust", 1)

        topic_lower = topic.lower()

        if "murder" in topic_lower or "severe violence" in topic_lower:
            listener.social = max(listener.social - 3, 0)

        if "exiled" in topic_lower or "crime" in topic_lower or "trial" in topic_lower:
            listener.discipline = min(listener.discipline + 1, 100)

        if "leader" in topic_lower:
            if sim.leader:
                listener.change_relationship(sim.leader, "respect", 1)

        if "born" in topic_lower:
            listener.kindness = min(listener.kindness + 1, 100)

        if "died" in topic_lower:
            listener.social = max(listener.social - 2, 0)

        logs.append(f"{agent.name} shared gossip with {listener.name}.")
        logs.append(f'Gossip: "{topic}"')

def update_emotional_states(sim, logs):
    for agent in sim.agents:
        agent.update_emotional_state()

def update_crushes(sim, logs):
    for agent in sim.agents:
        if not agent.alive:
            continue

        previous = agent.crush

        agent.update_crush()

        if agent.crush and agent.crush != previous:
            logs.append(f"{agent.name} seems to have developed feelings for {agent.crush}.")
            agent.remember(f"I think I may have feelings for {agent.crush}.")

def handle_confessions(sim, logs):
    if sim.hour != 18:
        return

    for agent in sim.agents:
        if not agent.alive:
            continue

        if agent.age < 18:
            continue

        if agent.partner:
            continue

        if not agent.crush:
            continue

        crush = next((a for a in sim.agents if a.name == agent.crush), None)

        if not crush or not crush.alive:
            continue

        if crush.partner:
            continue

        if crush.location != agent.location:
            continue

        rel = agent.get_relationship(crush.name)
        crush_rel = crush.get_relationship(agent.name)

        confession_score = (
            rel.get("trust", 0)
            + rel.get("friendship", 0)
            + crush_rel.get("trust", 0)
            + crush_rel.get("friendship", 0)
            + agent.kindness
            - agent.pride // 2
        )

        if confession_score < 120:
            continue

        logs.append(f"{agent.name} confessed their feelings to {crush.name}.")

        acceptance_score = (
            crush_rel.get("trust", 0)
            + crush_rel.get("friendship", 0)
            + crush.kindness
            - crush.pride // 2
        )

        if crush.crush == agent.name:
            acceptance_score += 40

        if acceptance_score >= 100:
            agent.partner = crush.name
            crush.partner = agent.name

            agent.family.append(crush.name)
            crush.family.append(agent.name)

            agent.crush = None
            crush.crush = None

            agent.set_emotion("Connected")
            crush.set_emotion("Connected")

            agent.add_bond(crush.name, "accepted my confession")
            crush.add_bond(agent.name, "became my partner")

            agent.remember(f"Became partners with {crush.name}.")
            crush.remember(f"Became partners with {agent.name}.")

            logs.append(f"{crush.name} accepted. {agent.name} and {crush.name} became partners.")

            sim.notify(f"{agent.name} and {crush.name} became partners.", "Relationship")

            sim.notify_agent_event(agent.name, f"became partners with {crush.name}.")
            sim.notify_agent_event(crush.name, f"became partners with {agent.name}.")

            sim.notify_family_event(
                agent.surname,
                f"{agent.get_full_name()} became partners with {crush.get_full_name()}."
            )

            sim.notify_family_event(
                crush.surname,
                f"{crush.get_full_name()} became partners with {agent.get_full_name()}."
            )

            sim.record_family_alliance(agent, crush, "partnership")

            sim.add_history(f"{agent.name} and {crush.name} became partners after a confession.")

        else:
            agent.change_relationship(crush.name, "trust", -5)
            agent.change_relationship(crush.name, "friendship", -3)

            agent.set_emotion("Lonely")
            agent.remember(f"{crush.name} rejected my confession.")
            agent.add_grudge(crush.name, "rejected confession")

            logs.append(f"{crush.name} rejected {agent.name}'s confession.")
            sim.notify(f"{crush.name} rejected {agent.name}'s confession.", "Relationship")

def handle_rejection_recovery(sim, logs):
    if sim.hour != 9:
        return

    for agent in sim.agents:
        if not agent.alive:
            continue

        recent_memories = " ".join(agent.memories[-8:]).lower()

        if "rejected my confession" not in recent_memories:
            continue

        if agent.emotional_state != "Lonely":
            continue

        recovery_chance = 0.15
        recovery_chance += agent.discipline / 300
        recovery_chance += agent.kindness / 400

        if agent.get_best_friend():
            recovery_chance += 0.15

        if random.random() < recovery_chance:
            agent.set_emotion("Stable")
            agent.remember("I started to recover from rejection.")
            agent.write_journal(
                sim.day,
                sim.hour,
                "Rejection still hurts, but I feel like I can move forward."
            )

            logs.append(f"{agent.name} began recovering from rejection.")

def get_memory_line(sim, agent):
    if not agent.memories:
        return None

    memory = random.choice(agent.memories[-5:])

    return f"I still remember this: {memory}"


def get_relationship_line(sim, speaker, listener):
    if listener.name == speaker.partner:
        return random.choice([
            "I feel safer when you are near.",
            "We have survived so much together.",
            "I was thinking about our family today."
        ])

    if listener.name in speaker.family:
        return random.choice([
            "Family should look after each other.",
            "I worry about you more than I say.",
            "Whatever happens, you are still family."
        ])

    if listener.name == speaker.get_best_friend():
        return random.choice([
            "I trust you more than most people here.",
            "You have always been there when it mattered.",
            "Talking with you makes this place feel less lonely."
        ])

    if listener.name == speaker.get_rival():
        return random.choice([
            "I have not forgotten what happened between us.",
            "Do not pretend everything is fine.",
            "I still do not trust you."
        ])

    return None