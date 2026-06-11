from config import ACTIVE_SCENARIO


def stabilize_agent(agent):
    defaults = {
        "age": 18,
        "partner": None,
        "family": [],
        "pregnant": False,
        "pregnancy_timer": 0,
        "parents": [],
        "generation": 1,
        "inventory": {"food": 0, "wood": 0, "stone": 0},
        "wealth": 0,
        "debts": {},
        "risk_taking": 50,
        "greed": 50,
        "health": 100,
        "alive": True,
        "status": "Healthy",
        "role": "Wanderer",
        "faction": None,
        "journal": [],
        "life_goal": None,
        "completed_goals": [],
    }

    for key, value in defaults.items():
        if not hasattr(agent, key):
            setattr(agent, key, value)

    if not hasattr(agent, "skills"):
        agent.skills = {}

    for skill in ["hunting", "building", "farming", "social", "teaching", "medicine", "combat"]:
        agent.skills.setdefault(skill, 1)


def stabilize_sim(sim):
    defaults = {
        "world_state": "Ongoing",
        "collapse_reasons": [],
        "scenario": ACTIVE_SCENARIO,
        "milestones": set(),
        "world_history": [],
        "eras": [{"name": "Age of Survival", "start_day": 1}],
        "current_era": "Age of Survival",
        "chronicles": [],
        "daily_events": [],
        "technologies": [],
        "research_points": 0,
        "treaties": [],
        "wars": [],
        "extra_settlements": [],
        "rebellions": [],
        "faction_conflicts": [],
        "factions": {},
        "traditions": [],
        "settlement_stage": "Camp",
        "leader": None,
        "current_project": None,
        "death_records": [],
        "memorials": [],
        "laws": [],
        "error_log": [],
        "crime_records": {},
        "village_tension": 0,
    }

    for key, value in defaults.items():
        if not hasattr(sim, key):
            setattr(sim, key, value)

    for agent in sim.agents:
        stabilize_agent(agent)