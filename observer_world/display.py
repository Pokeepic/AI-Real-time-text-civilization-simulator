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
Inventory: {agent.inventory}
Wealth: {agent.wealth}

Skills:
{skills_text}

Recent Memories:
{memories}

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

Settlement: {sim.settlement['name'] or 'None'}
Leader: {sim.leader or 'None'}
Buildings: {', '.join(sim.settlement['buildings']) if sim.settlement['buildings'] else 'None'}
Shelter Progress: {sim.settlement['shelter_progress']}/100

Village Tension: {sim.village_tension}
Laws: {', '.join(sim.laws) if sim.laws else 'None'}
"""
    console.print(Panel(text, title="World Resources"))


def show_memorials(console, sim):
    if not sim.memorials:
        return

    recent_memorials = "\n".join(sim.memorials[-5:])
    console.print(Panel(recent_memorials, title="Memorials"))