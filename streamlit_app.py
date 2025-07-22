import streamlit as st
from api import fetch_player_by_id, fetch_competition_by_id
from pages.tabs import show_players_tab, show_competitions_tab

st.set_page_config(layout="wide")

# Initialize session state
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'main'
if 'selected_person_id' not in st.session_state:
    st.session_state.selected_person_id = None
if 'selected_comp_id' not in st.session_state:
    st.session_state.selected_comp_id = None

# Navigation functions
def go_to_main():
    st.session_state.current_view = 'main'
    st.session_state.selected_person_id = None
    st.session_state.selected_comp_id = None

def go_to_player(person_id):
    st.session_state.current_view = 'player'
    st.session_state.selected_person_id = person_id
    st.session_state.selected_comp_id = None

def go_to_competition(comp_id):
    st.session_state.current_view = 'competition'
    st.session_state.selected_comp_id = comp_id
    st.session_state.selected_person_id = None

# Handle different views
if st.session_state.current_view == 'player':
    from pages.players import show_player_page
    show_player_page(st.session_state.selected_person_id)

elif st.session_state.current_view == 'competition':
    from pages.competitions import show_competition_page
    show_competition_page(st.session_state.selected_comp_id)

else:
    # Main view
    st.title("Rubik's Cube Analytics Dashboard")
    
    def handle_global_search():
        search = st.text_input("Search player or competition ID", placeholder="Enter personId or comp_id...")
        
        if search:
            player = fetch_player_by_id(search)
            if player:
                st.success(f"Found player: {search}")
                if st.button("Go to player page", type="primary"):
                    go_to_player(search)
                    st.rerun()
                return
                
            comp = fetch_competition_by_id(search)
            if comp:
                st.success(f"Found competition: {comp[0]['name']}")
                if st.button("Go to competition page", type="primary"):
                    go_to_competition(search)
                    st.rerun()
                return
                
            st.error("No match found.")
    
    # Render search + tabs
    handle_global_search()
    
    # Default Tabs View
    tab1, tab2 = st.tabs(["Players", "Competitions"])
    with tab1: 
        show_players_tab()
    with tab2: 
        show_competitions_tab()