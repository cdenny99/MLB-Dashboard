import requests
import pandas as pd
from io import StringIO
from pandas.errors import ParserError

# Four splits to pull
SPLITS = [
    ("bat", 13, 17, "hitters_vs_lhp.csv"),
    ("bat", 14, 17, "hitters_vs_rhp.csv"),
    ("pit", 13, 6,  "pitchers_vs_lhb.csv"),
    ("pit", 14, 6,  "pitchers_vs_rhb.csv"),
]

BASE_URL = "https://www.fangraphs.com/leaders/major-league"

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
        "qual":      1,
        "csv":       1,
    }
    r = requests.get(BASE_URL, params=params)
    r.raise_for_status()
    text = r.text

    # Try CSV first
    try:
        df = pd.read_csv(StringIO(text))
    except ParserError:
        # Fallback: pick the first HTML table (the data grid)
        tables = pd.read_html(text)
        if not tables:
            raise RuntimeError(f"No tables found in HTML for {out_path}")
        df = tables[0]

    # Finally save
    df.to_csv(f"data/{out_path}", index=False)
    print(f"✔ Saved {out_path} ({df.shape[0]} rows)")

if __name__ == "__main__":
    for stat, month, sortcol, fname in SPLITS:
        fetch_and_save(stat, month, sortcol, fname)


