import requests
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup

@st.cache_data(ttl=3600)
def load_lineups():
    csv_url = "https://baseballmonster.com/Lineups.aspx?csv=1"
    # pandas can read it straight
    df = pd.read_csv(csv_url)
    # optionally rename columns to match downstream merges
    # df.rename(columns={"Team Name": "Team", "Player Name": "Player", …}, inplace=True)
    return df

@st.cache_data(ttl=3600)
def load_sps():
    today = pd.Timestamp.today().strftime("%Y-%m-%d")
    sched_url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}"
    sched = requests.get(sched_url).json().get("dates", [])

    if not sched:
        return pd.DataFrame([], columns=["Team","Pitcher","GamePk"])

    games = sched[0]["games"]
    rows = []
    for g in games:
        pk   = g["gamePk"]
        for side in ("away","home"):
            team_info = g["teams"][side]
            team_name = team_info["team"]["name"]
            prob      = team_info.get("probablePitcher")
            if prob:
                rows.append({
                    "GamePk":  pk,
                    "Team":    team_name,
                    "Pitcher": prob["person"]["fullName"]
                })

    return pd.DataFrame(rows)

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


