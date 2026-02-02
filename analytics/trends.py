import pandas as pd

def trend_7_days(df: pd.DataFrame):
    if df.empty or "crawl_time" not in df.columns:
        return pd.DataFrame()

    df = df.copy()

    # ✅ FORCE datetime
    df["crawl_time"] = pd.to_datetime(
        df["crawl_time"],
        errors="coerce"
    )

    # Drop invalid rows
    df = df.dropna(subset=["crawl_time"])

    # Extract date
    df["date"] = df["crawl_time"].dt.date

    # Keep last 7 days
    max_date = df["date"].max()
    if max_date is None:
        return pd.DataFrame()

    start_date = max_date - pd.Timedelta(days=6)

    df_7d = df[df["date"] >= start_date]

    # Count listings per day
    trend = (
        df_7d
        .groupby("date")
        .size()
        .reset_index(name="listing_count")
        .sort_values("date")
    )

    return trend
