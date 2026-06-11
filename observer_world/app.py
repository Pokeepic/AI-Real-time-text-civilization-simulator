import streamlit as st
from save_system import load_world, save_world
from simulation import Simulation
from agent import Agent
from config import CONFIG

st.set_page_config(page_title="Observer World", layout="wide")

st.title("Observer World")

sim = load_world()

if sim is None:
    agents = [Agent(name) for name in CONFIG["starting_names"]]
    sim = Simulation(agents)

if st.button("Advance 1 Hour"):
    logs = sim.tick()
    save_world(sim)
else:
    logs = []

col1, col2, col3 = st.columns(3)

col1.metric("Day", sim.day)
col2.metric("Hour", f"{sim.hour}:00")
col3.metric("Population", len([a for a in sim.agents if a.alive]))

st.subheader("Recent Events")
for log in logs[-20:]:
    st.write(log)

st.subheader("Agents")
st.dataframe([
    {
        "Name": a.name,
        "Age": a.age,
        "Role": a.role,
        "Location": a.location,
        "Health": a.health,
        "Status": a.status,
        "Wealth": a.wealth,
        "Goal": a.life_goal,
    }
    for a in sim.agents
])