import streamlit as st


def render(sim):
    st.subheader("Simulation Errors")

    error_log = getattr(sim, "error_log", [])

    if error_log:
        for error in error_log[-50:]:
            st.error(error)
    else:
        st.success("No errors detected.")