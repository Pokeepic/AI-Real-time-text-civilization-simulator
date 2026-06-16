from agent import Agent
from simulation import Simulation
from config import CONFIG
from stability import stabilize_sim
from name_generator import generate_unique_name, generate_founder_age
from collections import Counter
from export_data import export_agents_csv, export_relationships_csv
from archive import export_story_summary, export_chronicles, export_history_snapshots, export_history_snapshots_csv
import random
TEST_TICKS = 1000
TEST_SEEDS = [7, 42, 99]

def run_test(seed):
    random.seed(seed)

    starting_population = CONFIG.get("starting_population", len(CONFIG["starting_names"]))
    print(f"Starting population target: {starting_population}")

    existing_names = set()
    agents = []

    for _ in range(starting_population):
        name = generate_unique_name(existing_names)
        existing_names.add(name)

        agent = Agent(name)
        agent.age = generate_founder_age()

        agents.append(agent)
    sim = Simulation(agents)
    stabilize_sim(sim)

    print(f"Running {TEST_TICKS} tick test...")
    print(f"Random seed: {seed}")
    result_file = f"test_results_seed_{seed}.txt"

    for i in range(TEST_TICKS):
        current_tick = i
        logs = sim.tick()

        if i % 100 == 0:
            print(f"Tick {i}/{TEST_TICKS} completed...")

        if getattr(sim, "error_log", []):
            print("Errors detected:")
            print(f"Failed at tick: {current_tick}")

            with open(result_file, "w", encoding="utf-8") as file:
                file.write("OBSERVER WORLD TEST RESULTS\n")
                file.write("===========================\n\n")
                file.write("Status: FAILED\n\n")
                file.write("Errors:\n")
                file.write(f"Random Seed: {seed}\n")
                file.write(f"Failed Tick: {current_tick}\n\n")

                for error in sim.error_log:
                    print(error)
                    file.write(f"- {error}\n")

            print(f"Failed test results saved to {result_file}.")
            return False
    print(f"Total agents: {len(sim.agents)}")
    print(f"Alive agents: {len([a for a in sim.agents if a.alive])}")
    print(f"Deaths recorded: {len(sim.death_records)}")
    death_causes = Counter(
        record.get("cause", "Unknown")
        for record in sim.death_records
    )

    print("Death causes:")
    for cause, count in death_causes.most_common():
        print(f"- {cause}: {count}")
    accounted_for = (
        len([a for a in sim.agents if a.alive])
        + len(sim.death_records)
    )

    alive_agents = [a for a in sim.agents if a.alive]

    if alive_agents:
        avg_health = sum(a.health for a in alive_agents) / len(alive_agents)
        avg_hunger = sum(a.hunger for a in alive_agents) / len(alive_agents)
        avg_energy = sum(a.energy for a in alive_agents) / len(alive_agents)

        critical_hunger = len([a for a in alive_agents if a.hunger >= 85])
        critical_energy = len([a for a in alive_agents if a.energy <= 15])

        food = sim.resources.get("food", 0)
        food_per_person = food / max(1, len(alive_agents))

        print("Survival audit:")
        print(f"- Food: {food}")
        print(f"- Food per person: {food_per_person:.2f}")
        print(f"- Average health: {avg_health:.1f}")
        print(f"- Average hunger: {avg_hunger:.1f}")
        print(f"- Average energy: {avg_energy:.1f}")
        print(f"- Critical hunger agents: {critical_hunger}")
        print(f"- Critical energy agents: {critical_energy}")

    all_ages = [getattr(a, "age", 0) for a in sim.agents]
    alive_ages = [getattr(a, "age", 0) for a in sim.agents if a.alive]

    if all_ages:
        print("Age audit:")
        print(f"- Youngest age: {min(all_ages)}")
        print(f"- Oldest age: {max(all_ages)}")
        print(f"- Average age: {sum(all_ages) / len(all_ages):.1f}")

        print(f"- Children under 13: {len([age for age in alive_ages if age < 13])}")
        print(f"- Adults 18-44: {len([age for age in alive_ages if 18 <= age <= 44])}")
        print(f"- Older adults 45-59: {len([age for age in alive_ages if 45 <= age <= 59])}")
        print(f"- Elders 60-74: {len([age for age in alive_ages if 60 <= age <= 74])}")
        print(f"- Very old 75+: {len([age for age in alive_ages if age >= 75])}")

    missing = len(sim.agents) - accounted_for

    print(f"Accounted for: {accounted_for}")
    print(f"Missing agents: {missing}")
    print(f"Notifications: {len(sim.notifications)}")
    print(f"Chronicles: {len(sim.chronicles)}")
    print(f"Milestones: {len(sim.milestones)}")
    print(f"World state: {sim.world_state}")
    print(f"Day: {sim.day}, Hour: {sim.hour}")
    print(f"Population: {len([a for a in sim.agents if a.alive])}")
    dead_agents = [a for a in sim.agents if not a.alive]
    recorded_death_names = set(record["name"] for record in sim.death_records)

    unrecorded_dead = [
        a.name for a in dead_agents
        if a.name not in recorded_death_names
    ]

    print(f"Dead agents total: {len(dead_agents)}")
    print(f"Unrecorded dead agents: {len(unrecorded_dead)}")

    if unrecorded_dead:
        print("First 20 unrecorded dead:")
        print(unrecorded_dead[:20])

    print("Testing exports...")

    export_agents_csv(sim)
    export_relationships_csv(sim)
    export_history_snapshots(sim)
    export_history_snapshots_csv(sim)
    export_story_summary(sim)
    export_chronicles(sim)

    print("Exports completed successfully.")
    with open(result_file, "w", encoding="utf-8") as file:
        file.write("OBSERVER WORLD TEST RESULTS\n")
        file.write("===========================\n\n")
        file.write("Status: PASSED\n")
        file.write(f"Day: {sim.day}\n")
        file.write(f"Hour: {sim.hour}\n")
        file.write(f"Total agents: {len(sim.agents)}\n")
        file.write(f"Alive agents: {len([a for a in sim.agents if a.alive])}\n")
        file.write(f"Deaths recorded: {len(sim.death_records)}\n")
        file.write("Death causes:\n")
        for cause, count in death_causes.most_common():
            file.write(f"- {cause}: {count}\n")
        file.write(f"Accounted for: {accounted_for}\n")
        file.write(f"Missing agents: {missing}\n")
        file.write(f"Notifications: {len(sim.notifications)}\n")
        file.write(f"Chronicles: {len(sim.chronicles)}\n")
        file.write(f"Milestones: {len(sim.milestones)}\n")
        file.write(f"World state: {sim.world_state}\n")
        file.write(f"Random Seed: {seed}\n")
        file.write("Survival audit:\n")
        file.write(f"- Food: {food}\n")
        file.write(f"- Food per person: {food_per_person:.2f}\n")
        file.write(f"- Average health: {avg_health:.1f}\n")
        file.write(f"- Average hunger: {avg_hunger:.1f}\n")
        file.write(f"- Average energy: {avg_energy:.1f}\n")
        file.write(f"- Critical hunger agents: {critical_hunger}\n")
        file.write(f"- Critical energy agents: {critical_energy}\n")

    print(f"Test results saved to {result_file}.")
    return True


if __name__ == "__main__":
    passed_seeds = []
    failed_seeds = []

    for seed in TEST_SEEDS:
        print(f"\n=== Running seed {seed} ===")
        passed = run_test(seed)

        if passed:
            passed_seeds.append(seed)
        else:
            failed_seeds.append(seed)

    with open("test_summary.txt", "w", encoding="utf-8") as file:
        file.write("OBSERVER WORLD MULTI-SEED TEST SUMMARY\n")
        file.write("======================================\n\n")
        file.write(f"Ticks per seed: {TEST_TICKS}\n")
        file.write(f"Seeds tested: {TEST_SEEDS}\n")
        file.write(f"Passed seeds: {passed_seeds}\n")
        file.write(f"Failed seeds: {failed_seeds}\n")

    print("\nAll seed tests completed.")
    print("Summary saved to test_summary.txt.")