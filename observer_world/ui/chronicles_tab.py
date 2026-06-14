import streamlit as st


def render(sim):
    st.subheader("Daily Chronicles")

    for chronicle in sim.chronicles[-30:]:
        st.write(chronicle)