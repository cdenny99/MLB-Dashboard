import streamlit as st
import pandas as pd
import requests
from io import StringIO
from bs4 import BeautifulSoup

@st.cache_data(ttl=3600)
def load_lineups():
    import requests, pandas as pd

    today = pd.Timestamp.today().strftime("%Y-%m-%d")
    sched = requests.get(
        f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}"
    ).json()["dates"][0]["games"]

    rows = []
    for g in sched:
        pk     = g["gamePk"]
        box    = requests.get(f"https://statsapi.mlb.com/api/v1/game/{pk}/boxscore")
        teams  = box.json().get("teams", {})
        for side in ("away", "home"):
            team = teams.get(side, {})
            tm   = team.get("team", {}).get("name", side)

            # Use the 'batters' list (IDs in lineup order)
            for slot, batter_id in enumerate(team.get("batters", []), start=1):
                player_key   = f"ID{batter_id}"
                person       = team["players"][player_key]["person"]
                position     = team["players"][player_key]["position"]["abbreviation"]
                rows.append({
                    "GamePk":  pk,
                    "Team":    tm,
                    "Slot":    slot,
                    "Player":  person["fullName"],
                    "Position":position
                })

    return pd.DataFrame(rows).sort_values(["GamePk","Slot"]).reset_index(drop=True)

@st.cache_data(ttl=3600)
def load_sps():
    url = "https://www.rotoballer.com/starting-pitcher-dfs-matchups-streamers-tool"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    r = requests.get(url, headers=headers)
    return pd.read_html(r.text)[0]

@st.cache_data(ttl=3600)
def load_fg_split(stat: str, month: int, sortcol: int) -> pd.DataFrame:
    url = "https://cdn.fangraphs.com/api/leaders/export"
    params = {
        "pos":       "all",
        "stats":     stat,
        "lg":        "all",
        "ind":       0,
        "type":      8,
        "month":     month,
        "season1":   2024,
        "season":    2025,
        "sortcol":   sortcol,
        "sortdir":   "default",
        "pageitems": 2000000000,
        "qual":      1
    }
    r = requests.get(url, params=params)
    df = pd.read_csv(StringIO(r.text))
    return df

st.title("⚾️ MLB Morning Snapshot")
st.subheader("Today's Lineups")
st.dataframe(load_lineups())
st.subheader("Probable SPs")
st.dataframe(load_sps())
col1, col2 = st.columns(2)
with col1:
    st.markdown("#### Hitters vs LHP")
    st.dataframe(load_fg_split("bat", 13, 17).head(20))
with col2:
    st.markdown("#### Hitters vs RHP")
    st.dataframe(load_fg_split("bat", 14, 17).head(20))
col3, col4 = st.columns(2)
with col3:
    st.markdown("#### Pitchers vs LHB")
    st.dataframe(load_fg_split("pit", 13, 6).head(20))
with col4:
    st.markdown("#### Pitchers vs RHB")


