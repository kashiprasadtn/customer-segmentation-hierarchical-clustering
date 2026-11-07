"""Download the UCI Online Retail dataset and save it as data/OnlineRetail.csv.

Source: Chen, D. (2015). Online Retail [Dataset]. UCI Machine Learning Repository.
https://doi.org/10.24432/C5BW33  (licence: CC BY 4.0)

The UCI file is an Excel workbook (541,909 rows, 8 columns). This script writes the
7-column CSV layout used by the notebook (StockCode dropped, dates as dd-mm-YYYY HH:MM).

Usage (from the repository root):
    pip install -r requirements.txt
    python scripts/download_data.py
"""
import io
import sys
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

URL = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"
OUT = Path(__file__).resolve().parents[1] / "data" / "OnlineRetail.csv"


def convert(xlsx_bytes: bytes) -> pd.DataFrame:
    df = pd.read_excel(io.BytesIO(xlsx_bytes), dtype={"InvoiceNo": str, "StockCode": str})
    df = df.drop(columns=["StockCode"])
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"]).dt.strftime("%d-%m-%Y %H:%M")
    return df[["InvoiceNo", "Description", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID", "Country"]]


def main() -> None:
    if OUT.exists():
        print(f"{OUT} already exists - nothing to do.")
        return
    print(f"Downloading {URL} ...")
    with urllib.request.urlopen(URL, timeout=120) as resp:
        payload = resp.read()
    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        name = next(n for n in zf.namelist() if n.lower().endswith(".xlsx"))
        xlsx = zf.read(name)
    print(f"Converting {name} (this takes about a minute) ...")
    df = convert(xlsx)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False, encoding="cp1252", errors="replace")
    print(f"Saved {len(df):,} rows to {OUT}")
    if len(df) != 541909:
        print("Warning: expected 541,909 rows; the source file may have changed.", file=sys.stderr)


if __name__ == "__main__":
    main()
