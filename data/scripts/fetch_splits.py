import requests
import pandas as pd
from io import StringIO

# Configuration for the four splits we need
SPLITS = [
    # stat, side, month, sortcol, output filename
    ("bat", "vs_lhp", 13, 17, "hitters_vs_lhp.csv"),
    ("bat", "vs_rhp", 14, 17, "hitters_vs_rhp.csv"),
    ("pit", "vs_lhb", 13, 6,  "pitchers_vs_lhb.csv"),
    ("pit", "vs_rhb", 14, 6,  "pitchers_vs_rhb.csv"),
]

API_URL = "https://cdn.fangraphs.com/api/leaders/export"

def fetch_and_save(stat, month, sortcol, out_path):
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
    resp = requests.get(API_URL, params=params)
    resp.raise_for_status()
    df = pd.read_csv(StringIO(resp.text))
    df.to_csv(f"data/{out_path}", index=False)
    print(f"Saved {out_path}, shape={df.shape}")

if __name__ == "__main__":
    for stat, side, month, sortcol, fname in SPLITS:
        fetch_and_save(stat, month, sortcol, fname)

