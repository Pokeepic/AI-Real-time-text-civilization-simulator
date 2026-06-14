import streamlit as st


def render(sim):
    st.subheader("World History")

    for event in sim.world_history[-80:]:
        st.write(event)

    st.subheader("Milestones")
    st.write(list(sim.milestones))

    st.subheader("Eras")
    st.json(sim.eras)

    st.subheader("Death Records")
    st.json(sim.death_records)

    st.subheader("Wars")
    st.json(sim.wars)

    st.subheader("Treaties")
    st.json(sim.treaties)

    st.subheader("Rebellions")
    st.json(sim.rebellions)