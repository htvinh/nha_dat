import pandas as pd


def price_by_district(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["price_million_per_m2"] = pd.to_numeric(
        df["price_million_per_m2"], errors="coerce"
    )

    result = (
        df.dropna(subset=["area_name"])
        .groupby("area_name", as_index=False)
        .agg(
            listings=("link", "count"),
            avg_price=("price", "mean"),
            median_price=("price", "median"),
            avg_price_m2=("price_million_per_m2", "mean"),
            median_price_m2=("price_million_per_m2", "median"),
        )
        .rename(columns={"area_name": "district"})
    )

    return result


def price_m2_by_district_category(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["price_million_per_m2"] = pd.to_numeric(
        df["price_million_per_m2"], errors="coerce"
    )

    result = (
        df.dropna(subset=["area_name", "price_million_per_m2"])
        .groupby(["area_name", "category"], as_index=False)
        .agg(
            listings=("link", "count"),
            avg_price_m2=("price_million_per_m2", "mean"),
            median_price_m2=("price_million_per_m2", "median"),
        )
        .rename(columns={"area_name": "district"})
    )

    return result


def supply_by_district(df: pd.DataFrame) -> pd.DataFrame:
    pivot = pd.pivot_table(
        df.dropna(subset=["area_name"]),
        index="area_name",
        columns="category",
        values="link",
        aggfunc="count",
        fill_value=0,
    ).reset_index()

    category_columns = [c for c in pivot.columns if c != "area_name"]
    pivot["TOTAL"] = pivot[category_columns].sum(axis=1)

    pivot.rename(columns={"area_name": "district"}, inplace=True)

    return pivot
