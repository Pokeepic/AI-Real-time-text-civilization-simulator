import streamlit as st
import os
import zipfile
import streamlit as st

from save_system import save_world
from export_data import export_agents_csv, export_relationships_csv
from archive import export_story_summary, export_chronicles, export_history_snapshots, export_history_snapshots_csv


def render(sim, app_version, safe_version):
    st.write(f"**App Version:** {app_version}")
    st.subheader("Temporary Controls")

    st.write("""
    This is the temporary observer dashboard.

    Use:
    - **Advance 1 Hour** for careful observation.
    - **Run 6 Hours** for short progress.
    - **Run 1 Day** to quickly grow the world.
    - **Run 7 Days** to quickly simulate a longer period.
    - **Save** to store the current world.
    - **Reset World** to start over.

    True real-time mode can be built later using a FastAPI backend + web dashboard.
    """)

    st.divider()

    st.subheader("Export Files")
    if st.button("Export Everything"):
        export_story_summary(sim)
        export_chronicles(sim)
        export_history_snapshots(sim)
        export_agents_csv(sim)
        export_relationships_csv(sim)
        save_world(sim)

        st.success("Exported story summary, chronicles, agents CSV, relationships CSV, and saved world.")
    
    if st.button("Create Backup ZIP"):
        export_story_summary(sim)
        export_chronicles(sim)
        export_agents_csv(sim)
        export_relationships_csv(sim)
        save_world(sim)

        os.makedirs("exports", exist_ok=True)

        safe_version = app_version.replace(" ", "_").replace(".", "_")
        zip_path = f"exports/observer_world_backup_{safe_version}.zip"

        files_to_zip = [
            "logs/story_summary.txt",
            "logs/chronicles.txt",
            "logs/world_history.txt",
            "exports/agents.csv",
            "exports/relationships.csv",
            "saves/world_save.pkl",
            "logs/history_snapshots.txt",
            "logs/history_snapshots.csv",
        ]

        with zipfile.ZipFile(zip_path, "w") as zipf:
            for file_path in files_to_zip:
                if os.path.exists(file_path):
                    zipf.write(file_path)

        st.success("Backup ZIP created.")
    
    st.divider()

    st.subheader("Backup Info")

    backup_path = "exports/observer_world_backup.zip"

    if os.path.exists(backup_path):
        backup_size = os.path.getsize(backup_path) / 1024

        st.success("Backup ZIP exists.")
        st.write(f"**File:** {backup_path}")
        st.write(f"**Size:** {backup_size:.2f} KB")
    else:
        st.warning("No backup ZIP created yet.")

    if st.button("Export Story Summary"):
        path = export_story_summary(sim)
        st.success(f"Story summary exported to {path}")

    st.divider()

    st.subheader("Download Files")

    download_files = [
        {
            "label": "Download Story Summary",
            "path": "logs/story_summary.txt",
            "file_name": "story_summary.txt",
            "mime": "text/plain",
        },
        {
            "label": "Download Chronicles",
            "path": "logs/chronicles.txt",
            "file_name": "chronicles.txt",
            "mime": "text/plain",
        },
        {
            "label": "Download Full World History",
            "path": "logs/world_history.txt",
            "file_name": "world_history.txt",
            "mime": "text/plain",
        },
        {
            "label": "Download Agents CSV",
            "path": "exports/agents.csv",
            "file_name": "agents.csv",
            "mime": "text/csv",
        },
        {
            "label": "Download Relationships CSV",
            "path": "exports/relationships.csv",
            "file_name": "relationships.csv",
            "mime": "text/csv",
        },
        {
            "label": "Download Full Backup ZIP",
            "path": f"exports/observer_world_backup_{safe_version}.zip",
            "file_name": f"observer_world_backup_{safe_version}.zip",
            "mime": "application/zip",
        },
        {
            "label": "Download History Snapshots",
            "path": "logs/history_snapshots.txt",
            "file_name": "history_snapshots.txt",
            "mime": "text/plain",
        },
        {
            "label": "Download History Snapshots CSV",
            "path": "logs/history_snapshots.csv",
            "file_name": "history_snapshots.csv",
            "mime": "text/csv",
        },
    ]

    for item in download_files:
        if os.path.exists(item["path"]):
            with open(item["path"], "rb") as file:
                st.download_button(
                    label=item["label"],
                    data=file,
                    file_name=item["file_name"],
                    mime=item["mime"],
                    key=f"download_{item['file_name']}"
                )
        else:
            st.caption(f"{item['file_name']} not created yet.")
    
    st.divider()

    st.subheader("Clean Up")

    cleanup_col1, cleanup_col2 = st.columns(2)

    with cleanup_col1:
        if st.button("Clear Dashboard Logs"):
            st.session_state.logs = []
            st.success("Dashboard logs cleared.")
            st.rerun()

    with cleanup_col2:
        if st.button("Clear Notifications"):
            sim.notifications = []
            save_world(sim)
            st.success("Notifications cleared.")
            st.rerun()
    
    st.divider()

    st.subheader("Delete Exported Files")
    confirm_delete_files = st.checkbox("Confirm Delete Exported Files")

    delete_col1, delete_col2 = st.columns(2)

    with delete_col1:
        if st.button("Delete Log Files"):
            if confirm_delete_files:
                log_files = [
                    "logs/story_summary.txt",
                    "logs/chronicles.txt",
                    "logs/world_history.txt",
                ]

                for file_path in log_files:
                    if os.path.exists(file_path):
                        os.remove(file_path)

                st.success("Log files deleted.")
                st.rerun()
            else:
                st.warning("Please tick 'Confirm Delete Exported Files' first.")

    with delete_col2:
        if st.button("Delete Export Files"):
            if confirm_delete_files:
                export_files = [
                    "exports/agents.csv",
                    "exports/relationships.csv",
                    "exports/observer_world_backup.zip",
                ]

                for file_path in export_files:
                    if os.path.exists(file_path):
                        os.remove(file_path)

                st.success("Export files deleted.")
                st.rerun()
            else:
                st.warning("Please tick 'Confirm Delete Exported Files' first.")