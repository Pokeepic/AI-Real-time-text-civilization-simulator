from agent import Agent
from simulation import Simulation
from config import CONFIG


required_methods = [
    "update_season",
    "update_weather",
    "generate_world_name",
    "generate_settlement_name",
    "generate_child_name",
    "generate_surname",
    "notify",
    "notify_agent_event",
    "notify_family_event",
    "add_history",
    "create_daily_chronicle",
    "handle_family_growth",
    "handle_aging",
    "handle_family_reunions",
    "handle_sibling_interactions",
    "handle_parent_child_bonds",
    "deepen_partner_bonds",
    "handle_mourning",
    "update_family_reputation",
    "apply_family_reputation_effects",
    "record_family_alliance",
    "record_family_rivalry",
    "apply_family_rivalry_effects",
    "check_social_changes",
    "spread_gossip",
    "update_emotional_states",
    "update_crushes",
    "handle_confessions",
    "handle_rejection_recovery",
    "get_memory_line",
    "get_relationship_line",
]


agents = [Agent(name) for name in CONFIG["starting_names"]]
sim = Simulation(agents)

missing = []

for method in required_methods:
    if not hasattr(sim, method):
        missing.append(method)

if missing:
    print("Missing wrapper methods:")
    for method in missing:
        print("-", method)
else:
    print("All required wrapper methods exist.")