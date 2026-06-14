import streamlit as st


def render(sim):
    st.subheader("World Timeline")

    timeline_sources = []

    for event in getattr(sim, "world_history", []):
        timeline_sources.append({
            "Source": "History",
            "Event": event
        })

    for chronicle in getattr(sim, "chronicles", []):
        timeline_sources.append({
            "Source": "Chronicle",
            "Event": chronicle
        })

    for notification in getattr(sim, "notifications", []):
        if isinstance(notification, dict):
            timeline_sources.append({
                "Source": notification.get("category", "Notification"),
                "Event": f"Day {notification.get('day')}, Hour {notification.get('hour')}:00 — {notification.get('message')}"
            })

    source_options = sorted(set(item["Source"] for item in timeline_sources))

    selected_sources = st.multiselect(
        "Filter timeline sources",
        source_options,
        default=source_options
    )

    search_timeline = st.text_input("Search timeline")

    filtered_timeline = [
        item for item in timeline_sources
        if item["Source"] in selected_sources
    ]

    if search_timeline:
        filtered_timeline = [
            item for item in filtered_timeline
            if search_timeline.lower() in item["Event"].lower()
        ]

    if filtered_timeline:
        for item in filtered_timeline[-100:]:
            st.write(f"**[{item['Source']}]** {item['Event']}")
    else:
        st.info("No timeline events match your filters.")