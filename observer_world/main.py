import time

from rich.console import Console

from agent import Agent
from simulation import Simulation
from save_system import save_world, load_world
from display import (
    show_agent_status,
    show_world_history,
    show_agent_details,
    show_resources,
    show_memorials,
)

console = Console()

names = [
    "Mira",
    "Kai",
    "Lena",
    "Rook",
    "Niko",
    "Aria",
    "Daren",
    "Nova",
    "Eli",
    "Zane"
]

sim = load_world()

if sim is None:
    agents = [Agent(name) for name in names]
    sim = Simulation(agents)
else:
    console.print("Loaded saved world.", style="bold yellow")
    agents = sim.agents

selected_agent_index = 0

while True:
    console.clear()

    console.print(f"\nDAY {sim.day} | HOUR {sim.hour}:00", style="bold green")

    logs = sim.tick()

    if sim.hour % 6 == 0:
        save_world(sim)
        logs.append("World autosaved.")

    console.print("\n[bold cyan]Recent Events[/bold cyan]")
    for log in logs[-12:]:
        console.print(log)

    console.print()
    show_agent_status(console, agents)

    console.print()
    show_resources(console, sim)

    console.print()
    show_world_history(console, sim)

    console.print()
    show_memorials(console, sim)

    console.print()
    show_agent_details(console, agents[selected_agent_index])

    selected_agent_index += 1

    if selected_agent_index >= len(agents):
        selected_agent_index = 0

    time.sleep(2)