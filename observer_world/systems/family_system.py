import random
from agent import Agent

def handle_family_reunions(sim, logs):
    if sim.hour != 19:
        return

    for agent in sim.agents:
        if not agent.alive:
            continue

        family_nearby = [
            other for other in sim.nearby_agents(agent)
            if other.name in agent.family and other.alive
        ]

        if len(family_nearby) < 1:
            continue

        if random.random() > 0.15:
            continue

        relative = random.choice(family_nearby)

        agent.change_relationship(relative.name, "friendship", 3)
        agent.change_relationship(relative.name, "trust", 2)

        relative.change_relationship(agent.name, "friendship", 3)
        relative.change_relationship(agent.name, "trust", 2)

        agent.add_bond(relative.name, "family reunion")
        relative.add_bond(agent.name, "family reunion")

        agent.set_emotion("Connected")
        relative.set_emotion("Connected")

        logs.append(f"{agent.name} shared a quiet family moment with {relative.name}.")

def handle_sibling_interactions(sim, logs):
    if sim.hour != 16:
        return

    for agent in sim.agents:
        if not agent.alive:
            continue

        siblings_nearby = [
            other for other in sim.nearby_agents(agent)
            if other.alive and agent.is_sibling_of(other)
        ]

        if not siblings_nearby:
            continue

        sibling = random.choice(siblings_nearby)

        if random.random() < 0.6:
            agent.change_relationship(sibling.name, "friendship", 2)
            sibling.change_relationship(agent.name, "friendship", 2)

            agent.add_bond(sibling.name, "sibling bond")
            sibling.add_bond(agent.name, "sibling bond")

            logs.append(f"{agent.name} spent time with their sibling {sibling.name}.")
        else:
            agent.change_relationship(sibling.name, "trust", -1)
            sibling.change_relationship(agent.name, "trust", -1)

            agent.add_grudge(sibling.name, "sibling argument")
            sibling.add_grudge(agent.name, "sibling argument")

            logs.append(f"{agent.name} had a small sibling argument with {sibling.name}.")

def handle_parent_child_bonds(sim, logs):
    if sim.hour != 17:
        return

    for parent in sim.agents:
        if not parent.alive:
            continue

        children_nearby = [
            child for child in sim.nearby_agents(parent)
            if child.alive and parent.name in child.parents
        ]

        if not children_nearby:
            continue

        child = random.choice(children_nearby)

        parent.change_relationship(child.name, "friendship", 3)
        parent.change_relationship(child.name, "trust", 3)
        child.change_relationship(parent.name, "trust", 4)
        child.change_relationship(parent.name, "respect", 2)

        parent.add_bond(child.name, "parental bond")
        child.add_bond(parent.name, "parental care")

        parent.set_emotion("Connected")
        child.set_emotion("Connected")

        if random.random() < 0.25:
            logs.append(f"{parent.name} spent time caring for {child.name}.")

def deepen_partner_bonds(sim, logs):
    if sim.hour != 20:
        return

    for agent in sim.agents:
        if not agent.alive:
            continue

        if not agent.partner:
            continue

        partner = next((a for a in sim.agents if a.name == agent.partner), None)

        if not partner or not partner.alive:
            continue

        if partner.location != agent.location:
            continue

        agent.change_relationship(partner.name, "trust", 1)
        agent.change_relationship(partner.name, "friendship", 1)
        partner.change_relationship(agent.name, "trust", 1)
        partner.change_relationship(agent.name, "friendship", 1)

        agent.add_bond(partner.name, "spent time together")
        partner.add_bond(agent.name, "spent time together")

        if random.random() < 0.25:
            logs.append(f"{agent.name} and {partner.name}'s bond deepened.")

def handle_mourning(sim, dead_agent, logs):
    for agent in sim.agents:
        if not agent.alive:
            continue

        if agent.name == dead_agent.name:
            continue

        should_mourn = False
        reason = None
        grief_power = 0

        if dead_agent.name == agent.partner:
            should_mourn = True
            reason = "partner"
            grief_power = 30

        elif dead_agent.name in agent.family:
            should_mourn = True
            reason = "family"
            grief_power = 25

        elif dead_agent.name in agent.parents:
            should_mourn = True
            reason = "parent"
            grief_power = 28

        elif agent.name in dead_agent.parents:
            should_mourn = True
            reason = "child"
            grief_power = 35

        elif dead_agent.name in agent.bonds:
            should_mourn = True
            reason = "bond"
            grief_power = 18

        elif agent.get_best_friend() == dead_agent.name:
            should_mourn = True
            reason = "close friend"
            grief_power = 20

        if should_mourn:
            agent.social = max(agent.social - grief_power, 0)
            agent.energy = max(agent.energy - grief_power // 2, 0)

            if grief_power >= 30:
                agent.set_emotion("Suffering")
            else:
                agent.set_emotion("Lonely")

            agent.remember(f"Mourned the death of {dead_agent.name}.")
            agent.write_journal(
                sim.day,
                sim.hour,
                f"I mourned {dead_agent.name}. They were my {reason}."
            )

            logs.append(f"{agent.name} deeply mourned the death of {dead_agent.name}. Reason: {reason}.")

def handle_family_growth(sim, logs):
    for agent in sim.agents:
        if not agent.alive:
            continue

        if agent.partner and not agent.pregnant:
            if random.random() < get_birth_chance(sim):
                agent.pregnant = True
                agent.pregnancy_timer = get_pregnancy_timer(sim)

                logs.append(f"{agent.name} and {agent.partner}'s family may grow soon.")
                sim.add_history(f"{agent.name} and {agent.partner} are expecting a child.")

        elif agent.pregnant:
            agent.pregnancy_timer -= 1

            if agent.pregnancy_timer <= 0:
                child_name = sim.generate_child_name()
                child = Agent(child_name)

                partner = next((a for a in sim.agents if a.name == agent.partner), None)

                child.age = 0
                child.location = agent.location
                child.parents = [agent.name, agent.partner]
                child.family.append(agent.name)
                child.family.append(agent.partner)

                if partner:
                    child.generation = max(agent.generation, partner.generation) + 1
                else:
                    child.generation = agent.generation + 1

                if agent.surname:
                    child.surname = agent.surname
                elif partner and partner.surname:
                    child.surname = partner.surname
                else:
                    new_surname = sim.generate_surname()
                    agent.surname = new_surname
                    if partner:
                        partner.surname = new_surname
                    child.surname = new_surname

                sim.inherit_traits(child, agent, partner)

                sim.agents.append(child)

                agent.family.append(child_name)

                if partner:
                    partner.family.append(child_name)

                agent.pregnant = False

                logs.append(f"A child was born: {child.get_full_name()}.")
                sim.add_history(f"{child.get_full_name()} was born into the settlement.")

                sim.notify(f"{child.get_full_name()} was born.", "Birth")
                sim.notify_family_event(child.surname, f"{child.get_full_name()} was born.")

                sim.notify_agent_event(
                    agent.name,
                    f"became a parent to {child.get_full_name()}."
                )

                if partner:
                    sim.notify_agent_event(
                        partner.name,
                        f"became a parent to {child.get_full_name()}."
                    )

def get_birth_chance(sim):
    try:
        from config import get_setting
        return get_setting("birth_chance")
    except Exception:
        return 0.01


def get_pregnancy_timer(sim):
    try:
        from config import CONFIG
        return CONFIG["pregnancy_timer"]
    except Exception:
        return 5

def handle_aging(sim, logs):
    if sim.hour != 0:
        return

    aging_days = get_aging_every_days()

    for agent in sim.agents:
        if not agent.alive:
            continue

        if sim.day % aging_days == 0:
            agent.age += 1

            if agent.age == 6:
                logs.append(f"{agent.name} is no longer a toddler.")
                sim.add_history(f"{agent.name} reached childhood.")

            elif agent.age == 13:
                logs.append(f"{agent.name} became a teenager.")
                sim.add_history(f"{agent.name} became a teenager.")

            elif agent.age == 18:
                logs.append(f"{agent.name} reached adulthood.")
                sim.add_history(f"{agent.name} became an adult.")

            elif agent.age > 80:
                if random.random() < 0.08:
                    agent.alive = False
                    agent.status = "Dead"
                    logs.append(f"{agent.name} died of old age.")
                    sim.record_death(agent, "old age", logs)

def get_aging_every_days():
    try:
        from config import CONFIG
        return CONFIG["aging_every_days"]
    except Exception:
        return 5

def update_family_reputation(sim, logs):
    if sim.hour != 21:
        return

    reputation = {}

    for agent in sim.agents:
        surname = getattr(agent, "surname", None)

        if not surname:
            continue

        reputation.setdefault(surname, 0)

        reputation[surname] += agent.get_social_score()
        reputation[surname] += agent.wealth
        reputation[surname] += agent.skills.get("social", 0)

        if agent.role == "Leader":
            reputation[surname] += 20

        if agent.role == "Guard":
            reputation[surname] += 5

        if agent.role == "Exile":
            reputation[surname] -= 10

        if agent.get_rival():
            reputation[surname] -= 3

    sim.family_reputation = reputation

def apply_family_reputation_effects(sim, logs):
    if sim.hour != 22:
        return

    if not sim.family_reputation:
        return

    for agent in sim.agents:
        if not agent.alive:
            continue

        if not agent.surname:
            continue

        reputation = sim.family_reputation.get(agent.surname, 0)

        nearby = sim.nearby_agents(agent)

        if not nearby:
            continue

        for other in nearby:
            if not other.alive:
                continue

            if reputation >= 50:
                other.change_relationship(agent.name, "respect", 1)

                if random.random() < 0.05:
                    logs.append(f"{other.name} showed respect toward {agent.name}'s family name.")

            elif reputation <= -30:
                other.change_relationship(agent.name, "trust", -1)

                if random.random() < 0.05:
                    logs.append(f"{other.name} distrusted {agent.name} because of their family reputation.")

def record_family_alliance(sim, agent_a, agent_b, reason):
    surname_a = getattr(agent_a, "surname", None)
    surname_b = getattr(agent_b, "surname", None)

    if not surname_a or not surname_b:
        return

    if surname_a == surname_b:
        return

    key = tuple(sorted([surname_a, surname_b]))

    if key not in sim.family_alliances:
        sim.family_alliances[key] = {
            "score": 0,
            "reasons": []
        }

    sim.family_alliances[key]["score"] += 1
    sim.family_alliances[key]["reasons"].append(reason)

    if len(sim.family_alliances[key]["reasons"]) > 10:
        sim.family_alliances[key]["reasons"].pop(0)

def record_family_rivalry(sim, agent_a, agent_b, reason):
    surname_a = getattr(agent_a, "surname", None)
    surname_b = getattr(agent_b, "surname", None)

    if not surname_a or not surname_b:
        return

    if surname_a == surname_b:
        return

    key = tuple(sorted([surname_a, surname_b]))

    if key not in sim.family_rivalries:
        sim.family_rivalries[key] = {
            "score": 0,
            "reasons": []
        }

    sim.family_rivalries[key]["score"] += 1
    sim.family_rivalries[key]["reasons"].append(reason)

    if len(sim.family_rivalries[key]["reasons"]) > 10:
        sim.family_rivalries[key]["reasons"].pop(0)

def apply_family_rivalry_effects(sim, logs):
    if sim.hour != 18:
        return

    if not sim.family_rivalries:
        return

    for families, data in sim.family_rivalries.items():
        score = data.get("score", 0)

        if score < 3:
            continue

        family_a, family_b = families

        members_a = [
            a for a in sim.agents
            if a.alive and getattr(a, "surname", None) == family_a
        ]

        members_b = [
            a for a in sim.agents
            if a.alive and getattr(a, "surname", None) == family_b
        ]

        for member_a in members_a:
            for member_b in members_b:
                if member_a.location != member_b.location:
                    continue

                member_a.change_relationship(member_b.name, "trust", -1)
                member_b.change_relationship(member_a.name, "trust", -1)

                if random.random() < 0.05:
                    logs.append(
                        f"Old family rivalry caused tension between {member_a.name} and {member_b.name}."
                    )