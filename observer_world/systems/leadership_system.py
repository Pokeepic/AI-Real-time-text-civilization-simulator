"""
Leadership system for Observer World.
"""


def check_leadership(sim, logs):
    if sim.settlement["name"] is None:
        return

    best_candidate = None
    best_score = -999

    for agent in sim.agents:
        if agent.location == "Exiled Lands":
            continue

        total_respect = 0
        total_trust = 0

        for other in sim.agents:
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

        if agent.faction and agent.faction in sim.factions:
            score += sim.factions[agent.faction].get("influence", 0) // 2

        if score > best_score:
            best_score = score
            best_candidate = agent

    if best_candidate and sim.leader != best_candidate.name and best_score > 80:
        old_leader = sim.leader
        sim.leader = best_candidate.name

        if old_leader is None:
            logs.append(f"{best_candidate.name} has naturally become the leader of {sim.settlement['name']}.")
            sim.notify(f"{best_candidate.name} became leader of {sim.settlement['name']}.", "Leadership")
            sim.add_history(f"{best_candidate.name} became the first leader of {sim.settlement['name']}.")
        else:
            logs.append(f"Leadership changed from {old_leader} to {best_candidate.name}.")
            sim.notify(f"Leadership changed from {old_leader} to {best_candidate.name}.", "Leadership")
            sim.add_history(f"Leadership changed from {old_leader} to {best_candidate.name}.")

        sim.notify_agent_event(best_candidate.name, "became leader.")
        sim.notify_family_event(
            best_candidate.surname,
            f"{best_candidate.get_full_name()} became leader."
        )