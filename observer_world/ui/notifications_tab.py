import streamlit as st


def render(sim):
    st.subheader("Notifications")

    notifications = getattr(sim, "notifications", [])

    category_filter = st.selectbox(
        "Filter by category",
        ["All"] + sorted(list(set(
            n.get("category", "General") if isinstance(n, dict) else "General"
            for n in notifications
        )))
    )

    filtered_notifications = notifications

    if category_filter != "All":
        filtered_notifications = [
            n for n in notifications
            if isinstance(n, dict)
            and n.get("category", "General") == category_filter
        ]

    if filtered_notifications:
        for notification in reversed(filtered_notifications[-50:]):
            if isinstance(notification, dict):
                st.info(
                    f"Day {notification.get('day')}, Hour {notification.get('hour')}:00 "
                    f"[{notification.get('category')}] {notification.get('message')}"
                )
            else:
                st.info(notification)
    else:
        st.info("No notifications yet.")