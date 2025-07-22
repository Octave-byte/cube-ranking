import streamlit as st
from api import fetch_player_by_id, fetch_competition_by_id
from pages.tabs import show_players_tab, show_competitions_tab
import uuid

params = st.query_params
st.write("🔍 Current query params:", params)  # DEBUG line
view = params.get("view", [None])[0]

if view == "player":
    person_id = params.get("personId", [None])[0]
    st.write(f"Loading player page for: {person_id}")  # Debug line
    from pages.player import show_player_page
    show_player_page(person_id)
    st.stop()

elif view == "competition":
    comp_id = params.get("compId", [None])[0]
    st.write(f"Loading competition page for: {comp_id}")  # Debug line
    from pages.competition import show_competition_page
    show_competition_page(comp_id)
    st.stop()

# --- Only runs when view is not set ---
st.set_page_config(layout="wide")
st.title("Rubik's Cube Analytics Dashboard")


def handle_global_search():
    search = st.text_input("Search player or competition ID", placeholder="Enter personId or comp_id...")

    if search:
        player = fetch_player_by_id(search)
        if player:
            st.success(f"Found player: {search}")
            if st.button("Go to player page"):
                st.query_params.clear()
                #st.query_params.update({"view": "player", "personId": search})
                st.query_params.update({
                    "view": "player",
                    "personId": search,
                    "uuid": str(uuid.uuid4())  # 👈 force refresh
                })
                st.rerun()  # Ensure rerun occurs immediately
                st.write("⚠️ rerun should have triggered but you still see this?")  # this should never appear

            return
        comp = fetch_competition_by_id(search)
        if comp:
            st.success(f"Found competition: {comp[0]['name']}")
            if st.button("Go to competition page"):
                st.query_params.clear()
                st.query_params.update({"view": "competition", "compId": search})
                st.rerun()
                st.write("⚠️ rerun should have triggered but you still see this?")  # this should never appear

            return
        st.error("No match found.")

# Render search + tabs
handle_global_search()

# Default Tabs View
tab1, tab2 = st.tabs(["Players", "Competitions"])
with tab1: show_players_tab()
with tab2: show_competitions_tab()
