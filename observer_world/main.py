import time
import keyboard

from rich.console import Console

from agent import Agent
from simulation import Simulation
from save_system import save_world, load_world
from archive import archive_logs
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
paused = False
speed = 2

while True:
    console.clear()

    console.print(f"\nDAY {sim.day} | HOUR {sim.hour}:00", style="bold green")
    console.print(
        "Controls: [P] Pause | [+] Faster | [-] Slower | [Q] Save & Quit",
        style="dim"
    )

    logs = sim.tick()

    archive_logs(sim, logs)

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

    if keyboard.is_pressed("p"):
        paused = not paused
        time.sleep(0.5)

    if keyboard.is_pressed("+"):
        speed = max(0.2, speed - 0.2)
        time.sleep(0.3)

    if keyboard.is_pressed("-"):
        speed += 0.2
        time.sleep(0.3)

    if keyboard.is_pressed("q"):
        save_world(sim)
        console.print("World saved. Exiting.", style="bold yellow")
        break

    if paused:
        console.print("\nPAUSED — Press P to resume.", style="bold red")
        time.sleep(0.5)
        continue

    time.sleep(speed)