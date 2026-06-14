import streamlit as st

from save_system import save_world


def render(sim):
    st.subheader("Agent Watchlist")

    selected_watch = st.multiselect(
        "Choose agents to follow",
        sorted(a.name for a in sim.agents),
        default=sim.watchlist
    )

    sim.watchlist = selected_watch
    save_world(sim)

    st.write("Currently watching:")

    if sim.watchlist:
        st.write(sim.watchlist)
    else:
        st.info("No agents selected.")