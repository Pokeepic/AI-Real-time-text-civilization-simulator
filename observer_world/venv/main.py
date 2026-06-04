import time

from rich.console import Console

from agent import Agent
from simulation import Simulation

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

agents = [Agent(name) for name in names]

sim = Simulation(agents)

while True:

    console.clear()

    console.print(
        f"\nDAY {sim.day} | HOUR {sim.hour}:00\n",
        style="bold green"
    )

    logs = sim.tick()

    for log in logs:
        console.print(log)

    time.sleep(1)