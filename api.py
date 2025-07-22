import requests
import streamlit as st

SUPABASE_URL = 'https://bvkfmjbkamxntyclcymu.supabase.co'

SUPABASE_KEY = st.secrets["API_KEY"]

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def fetch_latest_players():
    url = f"{SUPABASE_URL}/rest/v1/latest_player_metrics?select=*&order=rank365avg.desc&limit=10000"
    return requests.get(url, headers=HEADERS).json()

def fetch_latest_competitions():
    url = f"{SUPABASE_URL}/rest/v1/latest_competition_ranking?select=*&order=rank365avg_avg.desc&limit=10000"
    return requests.get(url, headers=HEADERS).json()

def fetch_player_by_id(person_id):
    url = f"{SUPABASE_URL}/rest/v1/player_metrics?personId=eq.{person_id}&select=personId&limit=1"
    return requests.get(url, headers=HEADERS).json()

def fetch_competition_by_id(comp_id):
    url = f"{SUPABASE_URL}/rest/v1/competitions?comp_id=eq.{comp_id}&select=comp_id,name&limit=1"
    return requests.get(url, headers=HEADERS).json()
