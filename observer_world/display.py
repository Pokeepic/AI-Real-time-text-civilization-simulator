from rich.table import Table
from rich.panel import Panel


def show_agent_status(console, agents):
    table = Table(title="AI Status")

    table.add_column("Name")
    table.add_column("Role")
    table.add_column("Location")
    table.add_column("Age")
    table.add_column("Gen")
    table.add_column("Hunger")
    table.add_column("Energy")
    table.add_column("Social")
    table.add_column("Health")
    table.add_column("Status")
    table.add_column("Best Skill")

    for agent in agents:
        best_skill = max(agent.skills, key=agent.skills.get)

        table.add_row(
            agent.name,
            agent.role,
            agent.location,
            str(agent.age),
            str(agent.generation),
            str(agent.hunger),
            str(agent.energy),
            str(agent.social),
            str(agent.health),
            agent.status,
            f"{best_skill} ({agent.skills[best_skill]})"
        )

    console.print(table)


def show_world_history(console, sim):
    if not sim.world_history:
        return

    recent_history = "\n".join(sim.world_history[-5:])
    console.print(Panel(recent_history, title="Recent World History"))


def show_agent_details(console, agent):
    memories = "\n".join(agent.memories[-5:]) if agent.memories else "No memories yet."

    journal_text = "\n".join(agent.journal[-5:]) if agent.journal else "No journal entries yet."

    relationships = []

    for name, rel in agent.relationships.items():
        relationships.append(
            f"{name}: trust {rel['trust']}, friendship {rel['friendship']}, "
            f"respect {rel['respect']}, fear {rel['fear']}"
        )

    relationship_text = "\n".join(relationships) if relationships else "No relationships yet."

    skills_text = "\n".join([
        f"{skill}: {value}"
        for skill, value in agent.skills.items()
    ])

    text = f"""
Partner: {agent.partner or 'None'}
Family: {', '.join(agent.family) if agent.family else 'None'}
Faction: {agent.faction or 'None'}
Life Goal: {agent.life_goal or 'None'}
Completed Goals: {', '.join(agent.completed_goals[-5:]) if agent.completed_goals else 'None'}
Inventory: {agent.inventory}
Wealth: {agent.wealth}
Debts: {agent.debts if agent.debts else 'None'}

Personality:
Curiosity: {agent.curiosity}
Kindness: {agent.kindness}
Aggression: {agent.aggression}
Discipline: {agent.discipline}
Pride: {agent.pride}
Greed: {agent.greed}
Risk Taking: {agent.risk_taking}

Skills:
{skills_text}

Recent Memories:
{memories}

Journal:
{journal_text}

Relationships:
{relationship_text}
"""

    console.print(Panel(text, title=f"{agent.name} Details"))


def show_resources(console, sim):
    text = f"""
Season: {sim.season}
Weather: {sim.weather}

Food: {sim.resources['food']}
Wood: {sim.resources['wood']}
Stone: {sim.resources['stone']}

World: {sim.world_name}
World State: {sim.world_state}

Settlement: {sim.settlement['name'] or 'None'}
Stage: {sim.settlement_stage}
Era: {sim.current_era}
Collapse Reasons: {', '.join(sim.collapse_reasons) if sim.collapse_reasons else 'None'}
Culture: {sim.get_culture_identity()}
Traditions: {', '.join(sim.traditions) if sim.traditions else 'None'}
Belief: {sim.get_belief_identity()}
Leader: {sim.leader or 'None'}
Buildings: {', '.join(sim.settlement['buildings']) if sim.settlement['buildings'] else 'None'}
Shelter Progress: {sim.settlement['shelter_progress']}/100
Current Project: {sim.current_project['name'] + ' ' + str(sim.current_project['progress']) + '/' + str(sim.current_project['required']) if sim.current_project else 'None'}

Village Tension: {sim.village_tension}
Laws: {', '.join(sim.laws) if sim.laws else 'None'}
Research Points: {sim.research_points}
Technologies: {', '.join(sim.technologies) if sim.technologies else 'None'}
Culture Scores: {sim.culture}
Belief Scores: {sim.beliefs}
"""
    console.print(Panel(text, title="World Resources"))


def show_memorials(console, sim):
    if not sim.memorials:
        return

    recent_memorials = "\n".join(sim.memorials[-5:])
    console.print(Panel(recent_memorials, title="Memorials"))


def show_statistics(console, sim):
    alive = [a for a in sim.agents if a.alive]
    dead = [a for a in sim.agents if not a.alive]
    adults = [a for a in alive if a.age >= 18]
    children = [a for a in alive if a.age < 18]

    total_crimes = sum(len(records) for records in sim.crime_records.values())
    highest_generation = max([a.generation for a in sim.agents], default=1)

    role_counts = {}

    for agent in alive:
        role_counts[agent.role] = role_counts.get(agent.role, 0) + 1

    role_text = ", ".join(
        f"{role}: {count}" for role, count in role_counts.items()
    ) if role_counts else "None"

    text = f"""
Population Alive: {len(alive)}
Dead: {len(dead)}
Adults: {len(adults)}
Children: {len(children)}
Total Born: {max(0, len(sim.agents) - 10)}

Highest Generation: {highest_generation}

Total Crimes Recorded: {total_crimes}
Faction Conflicts: {len(sim.faction_conflicts)}
Rebellions: {len(sim.rebellions)}
Wars: {len(sim.wars)}
Treaties: {len(sim.treaties)}
Laws Created: {len(sim.laws)}
Buildings Built: {len(sim.settlement['buildings'])}

Roles: {role_text}
"""

    console.print(Panel(text, title="Civilization Statistics"))


def show_milestones(console, sim):
    if not sim.milestones:
        return

    text = "\n".join(sorted(sim.milestones))
    console.print(Panel(text, title="Milestones"))


def show_factions(console, sim):
    if not sim.factions:
        return

    lines = []

    for name, data in sim.factions.items():
        members = ", ".join(data["members"]) if data["members"] else "No active members"
        influence = data.get("influence", 0)
        lines.append(f"{name} ({data['reason']}) | Influence: {influence} | Members: {members}")

    console.print(Panel("\n".join(lines), title="Factions"))


def show_extra_settlements(console, sim):
    if not sim.extra_settlements:
        return

    lines = []

    for settlement in sim.extra_settlements:
        resources = settlement.get("resources", {})
        buildings = settlement.get("buildings", [])
        culture_identity = sim.get_extra_settlement_culture_identity(settlement)
        laws = settlement.get("laws", [])
        techs = settlement.get("technologies", [])
        research = settlement.get("research_points", 0)

        lines.append(
            f"{settlement['name']} | Founder: {settlement['founder']} | Leader: {settlement.get('leader', 'None')} | "
            f"Population: {settlement['population']} | Stage: {settlement['stage']} | "
            f"Relation to Main: {settlement['relationship_to_main']}\n"
            f"Culture: {culture_identity} | Laws: {', '.join(laws) if laws else 'None'}\n"
            f"Research: {research} | Techs: {', '.join(techs) if techs else 'None'}\n"
            f"Resources: food {resources.get('food', 0)}, wood {resources.get('wood', 0)}, stone {resources.get('stone', 0)} | "
            f"Buildings: {', '.join(buildings) if buildings else 'None'}"
        )

    console.print(Panel("\n\n".join(lines), title="Other Settlements"))


def show_location_population(console, sim):
    counts = {}

    for agent in sim.agents:
        if not agent.alive:
            continue

        counts[agent.location] = counts.get(agent.location, 0) + 1

    if not counts:
        return

    lines = []

    for location, count in sorted(counts.items()):
        lines.append(f"{location}: {count}")

    console.print(Panel("\n".join(lines), title="Population by Location"))


def show_chronicles(console, sim):
    if not sim.chronicles:
        return

    recent = "\n\n".join(sim.chronicles[-3:])
    console.print(Panel(recent, title="Daily Chronicles"))


def show_eras(console, sim):
    if not sim.eras:
        return

    lines = [
        f"{era['name']} — started Day {era['start_day']}"
        for era in sim.eras[-5:]
    ]

    console.print(Panel("\n".join(lines), title="Eras"))