import streamlit as st
import pandas as pd
import requests
from io import StringIO
from bs4 import BeautifulSoup

@st.cache_data(ttl=3600)
def load_lineups():
    import requests
    import pandas as pd

    # 1) Grab today’s games
    today = pd.Timestamp.today().strftime("%Y-%m-%d")
    sched_url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}"
    games = requests.get(sched_url).json()["dates"][0]["games"]

    rows = []
    for g in games:
        pk = g["gamePk"]
        # ← use /api/v1/game/, *not* v1.1
        box_url = f"https://statsapi.mlb.com/api/v1/game/{pk}/boxscore"
        resp = requests.get(box_url)
        resp.raise_for_status()
        data = resp.json()

        # now this should exist
        teams = data.get("teams")
        if not teams:
            raise RuntimeError(f"boxscore JSON for game {pk} missing 'teams' – keys = {list(data)}")

        for side in ["away", "home"]:
            team = teams[side]
            tm_name = team["team"]["name"]
            # battingOrder is keyed by string IDs, so coerce to str
            for batter_id, order in team["battingOrder"].items():
                p = team["players"][f"ID{batter_id}"]["person"]
                rows.append({
                    "Team":     tm_name,
                    "Slot":     order,
                    "Player":   p["fullName"],
                    "Position": team["players"][f"ID{batter_id}"]["position"]["abbreviation"],
                    "GamePk":   pk
                })

    return pd.DataFrame(rows).sort_values(["GamePk", "Slot"]).reset_index(drop=True) 

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


