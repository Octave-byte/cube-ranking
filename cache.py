import streamlit as st
from api import fetch_latest_players, fetch_latest_competitions

@st.cache_data(ttl=3600)
def get_cached_players():
    return fetch_latest_players()

@st.cache_data(ttl=3600)
def get_cached_competitions():
    return fetch_latest_competitions()
