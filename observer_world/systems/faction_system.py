"""
Faction system for Observer World.
"""
import random
from config import get_setting


def update_factions(sim, logs):
    if sim.hour != 19:
        return

    if sim.settlement["name"] is None:
        return

    alive = [
        a for a in sim.agents
        if a.alive and a.location != "Exiled Lands" and a.age >= 13
    ]

    if len(alive) < 6:
        return

    possible_factions = []

    if sim.leader:
        possible_factions.append(("Leader Loyalists", "loyalty"))

    if sim.get_belief_identity() != "None":
        possible_factions.append(("Faith Circle", "belief"))

    if sim.village_tension > 60:
        possible_factions.append(("Reform Seekers", "tension"))

    if any(a.wealth >= 5 for a in alive):
        possible_factions.append(("Trade Guild", "wealth"))

    if any(a.role == "Guard" for a in alive):
        possible_factions.append(("Watch Order", "guard"))

    for faction_name, reason in possible_factions:
        if faction_name not in sim.factions:
            sim.factions[faction_name] = {
                "reason": reason,
                "members": []
            }

            logs.append(f"New faction formed: {faction_name}.")
            sim.add_history(f"Faction formed: {faction_name}.")

    for agent in alive:
        chosen_faction = None

        if sim.leader:
            rel = agent.get_relationship(sim.leader)

            if rel["trust"] > 20 or rel["respect"] > 20:
                chosen_faction = "Leader Loyalists"

        if agent.role == "Guard" and "Watch Order" in sim.factions:
            chosen_faction = "Watch Order"

        if agent.wealth >= 5 and "Trade Guild" in sim.factions:
            chosen_faction = "Trade Guild"

        if sim.get_belief_identity() != "None" and agent.kindness > 50:
            chosen_faction = "Faith Circle"

        if sim.village_tension > 60 and agent.aggression > 50:
            chosen_faction = "Reform Seekers"

        agent.faction = chosen_faction

    for faction in sim.factions.values():
        faction["members"] = []

    for agent in alive:
        if agent.faction and agent.faction in sim.factions:
            sim.factions[agent.faction]["members"].append(agent.name)

def update_faction_influence(sim, logs):
    if sim.hour != 20:
        return

    if not sim.factions:
        return

    for faction_name, data in sim.factions.items():
        members = data["members"]

        if not members:
            data["influence"] = 0
            continue

        influence = len(members) * 5

        for member_name in members:
            member = next((a for a in sim.agents if a.name == member_name), None)

            if not member:
                continue

            influence += member.wealth
            influence += member.skills["social"]
            influence += member.skills["combat"] // 2

            if member.role == "Leader":
                influence += 15

            if member.role == "Guard":
                influence += 8

            if member.role == "Merchant":
                influence += 6

        data["influence"] = influence

        if influence >= 40:
            logs.append(f"{faction_name} has become influential.")

        if influence >= 70:
            logs.append(f"{faction_name} is now a major power in the settlement.")

def handle_faction_conflict(sim, logs):
    if sim.hour != 21:
        return

    if len(sim.factions) < 2:
        return

    active_factions = [
        (name, data) for name, data in sim.factions.items()
        if data.get("members")
    ]

    if len(active_factions) < 2:
        return

    faction_a, data_a = random.choice(active_factions)
    faction_b, data_b = random.choice([
        item for item in active_factions
        if item[0] != faction_a
    ])

    influence_gap = abs(data_a.get("influence", 0) - data_b.get("influence", 0))

    conflict_chance = 0.05
    conflict_chance += sim.village_tension / 300

    if data_a["reason"] != data_b["reason"]:
        conflict_chance += 0.05

    if random.random() > conflict_chance:
        return

    conflict = {
        "day": sim.day,
        "hour": sim.hour,
        "factions": [faction_a, faction_b],
        "reason": "influence dispute"
    }

    sim.faction_conflicts.append(conflict)

    sim.village_tension = min(
        sim.village_tension + int(10 * get_setting("tension_multiplier")),
        100
    )

    logs.append(f"Faction conflict erupted between {faction_a} and {faction_b}.")
    logs.append(f"Village tension increased to {sim.village_tension}.")

    if influence_gap > 30:
        stronger = faction_a if data_a.get("influence", 0) > data_b.get("influence", 0) else faction_b
        logs.append(f"{stronger} dominated the dispute through influence.")
    else:
        logs.append("Neither faction gained clear control from the dispute.")

    sim.add_history(f"Faction conflict: {faction_a} vs {faction_b}.")

def handle_rebellion(sim, logs):
    if sim.hour != 22:
        return

    if not sim.leader:
        return

    if sim.village_tension < 70:
        return

    rebel_factions = [
        (name, data) for name, data in sim.factions.items()
        if data.get("members")
        and name != "Leader Loyalists"
        and data.get("influence", 0) >= 50
    ]

    if not rebel_factions:
        return

    faction_name, faction_data = random.choice(rebel_factions)

    leader = next((a for a in sim.agents if a.name == sim.leader), None)

    if not leader:
        return

    rebellion_power = faction_data.get("influence", 0) + sim.village_tension

    loyalist_power = 0

    if "Leader Loyalists" in sim.factions:
        loyalist_power += sim.factions["Leader Loyalists"].get("influence", 0)

    loyalist_power += leader.skills["social"] * 3
    loyalist_power += leader.skills["combat"] * 2
    loyalist_power += leader.discipline

    logs.append(f"Rebellion began against leader {sim.leader}.")
    logs.append(f"Rebel faction: {faction_name}.")

    rebellion_record = {
        "day": sim.day,
        "hour": sim.hour,
        "against": sim.leader,
        "faction": faction_name
    }

    sim.rebellions.append(rebellion_record)

    if rebellion_power > loyalist_power:
        old_leader = sim.leader

        possible_new_leaders = [
            a for a in sim.agents
            if a.name in faction_data["members"] and a.alive
        ]

        if possible_new_leaders:
            new_leader = max(
                possible_new_leaders,
                key=lambda a: a.skills["social"] + a.skills["combat"] + a.discipline
            )

            sim.leader = new_leader.name
            new_leader.role = "Leader"

            leader.change_relationship(new_leader.name, "trust", -30)
            new_leader.change_relationship(leader.name, "trust", -30)

            sim.village_tension = max(sim.village_tension - 25, 0)

            logs.append("The rebellion succeeded.")
            logs.append(f"{old_leader} was overthrown.")
            logs.append(f"{new_leader.name} became the new leader.")

            sim.notify(f"{old_leader} was overthrown. {new_leader.name} became leader.", "Leadership")
            sim.add_history(f"{old_leader} was overthrown by {new_leader.name} of {faction_name}.")
        else:
            logs.append("The rebellion succeeded, but no clear leader emerged.")
            sim.leader = None
            sim.village_tension = min(sim.village_tension + 10, 100)

    else:
        sim.village_tension = max(sim.village_tension - 10, 0)

        logs.append("The rebellion failed.")
        logs.append(f"{sim.leader} remained in power.")

        for member_name in faction_data["members"]:
            rebel = next((a for a in sim.agents if a.name == member_name), None)

            if rebel and rebel.alive:
                rebel.change_relationship(sim.leader, "fear", 10)
                rebel.change_relationship(sim.leader, "trust", -10)

        sim.add_history(f"A rebellion by {faction_name} against {sim.leader} failed.")