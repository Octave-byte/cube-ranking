import requests

SUPABASE_URL = "https://<your-project>.supabase.co"
SUPABASE_KEY = "your-api-key"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

def fetch_latest_players():
    url = f"{SUPABASE_URL}/rest/v1/latest_player_metrics?select=*&order=rank90avg.asc"
    return requests.get(url, headers=HEADERS).json()

def fetch_latest_competitions():
    url = f"{SUPABASE_URL}/rest/v1/latest_competition_ranking?select=*&order=rank90avg_avg.asc"
    return requests.get(url, headers=HEADERS).json()

def fetch_player_by_id(person_id):
    url = f"{SUPABASE_URL}/rest/v1/player_metrics?personId=eq.{person_id}&select=personId&limit=1"
    return requests.get(url, headers=HEADERS).json()

def fetch_competition_by_id(comp_id):
    url = f"{SUPABASE_URL}/rest/v1/competitions?comp_id=eq.{comp_id}&select=comp_id,name&limit=1"
    return requests.get(url, headers=HEADERS).json()
