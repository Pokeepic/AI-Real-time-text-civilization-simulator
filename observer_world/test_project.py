from agent import Agent
from simulation import Simulation
from config import CONFIG
from stability import stabilize_sim
from export_data import export_agents_csv, export_relationships_csv
from archive import export_story_summary, export_chronicles
import random
TEST_TICKS = 1000
TEST_SEEDS = [42, 99, 123, 7, 202, 999]

def run_test(seed):
    random.seed(seed)

    agents = [Agent(name) for name in CONFIG["starting_names"]]
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

            print("Failed test results saved to test_results.txt.")
            return False
    print(f"Total agents: {len(sim.agents)}")
    print(f"Alive agents: {len([a for a in sim.agents if a.alive])}")
    print(f"Deaths recorded: {len(sim.death_records)}")
    print(f"Notifications: {len(sim.notifications)}")
    print(f"Chronicles: {len(sim.chronicles)}")
    print(f"Milestones: {len(sim.milestones)}")
    print(f"World state: {sim.world_state}")
    print(f"Day: {sim.day}, Hour: {sim.hour}")
    print(f"Population: {len([a for a in sim.agents if a.alive])}")
    print("Testing exports...")

    export_agents_csv(sim)
    export_relationships_csv(sim)
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
        file.write(f"Notifications: {len(sim.notifications)}\n")
        file.write(f"Chronicles: {len(sim.chronicles)}\n")
        file.write(f"Milestones: {len(sim.milestones)}\n")
        file.write(f"World state: {sim.world_state}\n")
        file.write(f"Random Seed: {seed}\n")

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