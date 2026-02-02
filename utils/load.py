import pandas as pd

def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    df["crawl_time"] = pd.to_datetime(df["crawl_time"], errors="coerce")

    numeric_cols = [
        "price",
        "price_million_per_m2",
        "area"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["price", "area"])

    return df
