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
    url = "https://www.rotoballer.com/starting-pitcher-dfs-matchups-streamers-tool"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    # Find the table with the most rows (the main matchups grid)
    tables = soup.find_all("table")
    if not tables:
        raise RuntimeError("No tables found on Rotoballer page")
    table = max(tables, key=lambda t: len(t.find_all("tr")))

    # Parse header
    thead = table.find("thead")
    cols = [th.get_text(strip=True) for th in thead.find_all("th")]

    # Parse all body rows
    tbody = table.find("tbody")
    data = []
    for tr in tbody.find_all("tr"):
        row = [td.get_text(strip=True) for td in tr.find_all("td")]
        if row:
            data.append(row)

    return pd.DataFrame(data, columns=cols)

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


