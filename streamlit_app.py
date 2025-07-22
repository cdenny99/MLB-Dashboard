import streamlit as st
import pandas as pd

@st.cache_data(ttl=3600)
def load_fg_split(stat_side: str) -> pd.DataFrame:
    # stat_side should match the filename suffix, e.g. "hitters_vs_lhp"
    path = f"data/{stat_side}.csv"
    return pd.read_csv(path)

# ...

# In your layout:
st.subheader("Hitters vs LHP")
st.dataframe(load_fg_split("hitters_vs_lhp").head(20))

st.subheader("Hitters vs RHP")
st.dataframe(load_fg_split("hitters_vs_rhp").head(20))

st.subheader("Pitchers vs LHH")
st.dataframe(load_fg_split("pitchers_vs_lhh").head(20))

st.subheader("Pitchers vs RHH")
st.dataframe(load_fg_split("pitchers_vs_rhh").head(20))

