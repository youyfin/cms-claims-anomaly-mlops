from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


def build_provider_features(cleaned_csv: Path, sqlite_db: Path, sql_file: Path, output_csv: Path) -> pd.DataFrame:
    '''
    Build provider features from the cleaned claims data using SQL.
    data(clean_csv) -> db(sqlite_db) -> sql(sql_file) -> save features(output_csv)
    '''
    df = pd.read_csv(cleaned_csv)
    sqlite_db.parent.mkdir(parents=True, exist_ok=True)
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(sqlite_db) as conn:
        df.to_sql("inpatient_claims", conn, if_exists="replace", index=False)          # pd.DataFrame -> SQL table (= inpatient_claims table in sqlite_db )
        sql = sql_file.read_text(encoding="utf-8")                                     # read SQL script
        conn.executescript(sql)                                                        # execute SQL script
        features = pd.read_sql_query("SELECT * FROM provider_features", conn)          # SQL query -> pd.DataFrame

    features.to_csv(output_csv, index=False)
    return features
