import streamlit as st


def render(sim):
    st.subheader("Main Settlement")

    st.json({
        "world": getattr(sim, "world_name", "Unknown"),
        "settlement": sim.settlement,
        "stage": getattr(sim, "settlement_stage", "Camp"),
        "leader": getattr(sim, "leader", None),
        "resources": sim.resources,
        "village_tension": sim.village_tension,
        "culture": sim.get_culture_identity(),
        "belief": sim.get_belief_identity(),
        "laws": sim.laws,
        "traditions": sim.traditions,
        "technologies": sim.technologies,
        "research_points": sim.research_points,
        "current_project": sim.current_project,
    })

    st.subheader("Other Settlements")
    st.json(sim.extra_settlements)

    st.subheader("Factions")
    st.json(sim.factions)