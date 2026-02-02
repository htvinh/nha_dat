import pandas as pd


def detect_deals(df: pd.DataFrame, threshold: float = 0.75) -> pd.DataFrame:
    """
    Detect good real-estate deals by comparing price per m2
    against district median (area_name).
    """
    working_df = df.copy()

    # ----------------------
    # Filter valid rows
    # ----------------------
    working_df = working_df.dropna(
        subset=["area_name", "price_million_per_m2"]
    )

    # ----------------------
    # Median price per m2 by district
    # ----------------------
    median_price_map = (
        working_df
        .groupby("area_name")["price_million_per_m2"]
        .median()
    )

    # ----------------------
    # Deal score
    # ----------------------
    working_df["deal_score"] = (
        working_df["price_million_per_m2"]
        / working_df["area_name"].map(median_price_map)
    )

    # Remove invalid scores (safety)
    working_df = working_df.dropna(subset=["deal_score"])

    # ----------------------
    # Filter good deals
    # ----------------------
    deals = working_df[working_df["deal_score"] < threshold]

    result = (
        deals[
            [
                "title",
                "area_name",
                "price",
                "price_million_per_m2",
                "area",
                "deal_score",
                "link",
            ]
        ]
        .sort_values("deal_score")
        .reset_index(drop=True)
    )

    return result
