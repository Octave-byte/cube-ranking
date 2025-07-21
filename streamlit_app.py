import streamlit as st
from api import fetch_player_by_id, fetch_competition_by_id
from pages.tabs import show_players_tab, show_competitions_tab

def handle_global_search():
    search = st.text_input("Search player or competition ID", placeholder="Enter personId or comp_id...")

    if search:
        player = fetch_player_by_id(search)
        if player:
            st.success(f"Found player: {search}")
            if st.button("Go to player page"):
                st.experimental_set_query_params(view="player", personId=search)
                st.rerun()
            return
        comp = fetch_competition_by_id(search)
        if comp:
            st.success(f"Found competition: {comp[0]['name']}")
            if st.button("Go to competition page"):
                st.experimental_set_query_params(view="competition", compId=search)
                st.rerun()
            return
        st.error("No match found.")

st.set_page_config(layout="wide")
st.title("Rubik's Cube Analytics Dashboard")

handle_global_search()

# URL Routing
params = st.query_params()
view = params.get("view", [None])[0]

if view == "player":
    from pages.player import show_player_page
    show_player_page(params.get("personId", [None])[0])
    st.stop()

elif view == "competition":
    from pages.competition import show_competition_page
    show_competition_page(params.get("compId", [None])[0])
    st.stop()

# Default Tabs View
tab1, tab2 = st.tabs(["Players", "Competitions"])
with tab1: show_players_tab()
with tab2: show_competitions_tab()
