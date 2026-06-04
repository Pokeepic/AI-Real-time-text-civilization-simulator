import time
import threading

from rich.console import Console

from agent import Agent
from simulation import Simulation
from display import (
    show_agent_status,
    show_world_history,
    show_agent_details,
    show_resources,
    show_memorials,
    show_statistics,
)
from save_system import save_world, load_world
from archive import archive_logs

console = Console()

names = [
    "Mira", "Kai", "Lena", "Rook", "Niko",
    "Aria", "Daren", "Nova", "Eli", "Zane"
]

sim = load_world()

if sim is None:
    agents = [Agent(name) for name in names]
    sim = Simulation(agents)
else:
    console.print("Loaded saved world.", style="bold yellow")

paused = False
running = True
speed = 2
selected_agent_index = 0
inspect_agent_name = None


def command_listener():
    global paused, running, speed, inspect_agent_name

    while running:
        command = input().strip()

        if command == "pause":
            paused = True

        elif command == "resume":
            paused = False

        elif command.startswith("speed "):
            try:
                speed = float(command.split(" ")[1])
            except ValueError:
                pass

        elif command.startswith("inspect "):
            inspect_agent_name = command.replace("inspect ", "").strip()

        elif command == "clear inspect":
            inspect_agent_name = None

        elif command == "quit":
            save_world(sim)
            running = False


threading.Thread(target=command_listener, daemon=True).start()


while running:
    console.clear()

    console.print(f"\nDAY {sim.day} | HOUR {sim.hour}:00", style="bold green")
    console.print(
        "Commands: pause | resume | speed 1 | inspect Mira | clear inspect | quit",
        style="dim"
    )

    if paused:
        console.print("\nPAUSED", style="bold red")
        time.sleep(0.5)
        continue

    logs = sim.tick()
    archive_logs(sim, logs)

    if sim.hour % 6 == 0:
        save_world(sim)
        logs.append("World autosaved.")

    console.print("\n[bold cyan]Recent Events[/bold cyan]")
    for log in logs[-12:]:
        console.print(log)

    console.print()
    show_agent_status(console, sim.agents)

    console.print()
    show_resources(console, sim)

    console.print()
    show_statistics(console, sim)

    console.print()
    show_world_history(console, sim)

    console.print()
    show_memorials(console, sim)

    console.print()

    if inspect_agent_name:
        found = next(
            (agent for agent in sim.agents if agent.name.lower() == inspect_agent_name.lower()),
            None
        )

        if found:
            show_agent_details(console, found)
        else:
            console.print(f"No agent named {inspect_agent_name}.", style="bold red")
    else:
        show_agent_details(console, sim.agents[selected_agent_index])
        selected_agent_index = (selected_agent_index + 1) % len(sim.agents)

    time.sleep(speed)

console.print("World saved. Exiting.", style="bold yellow")