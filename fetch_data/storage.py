import os
import pandas as pd
from openpyxl.styles import Alignment

# =====================================================
# FIXED COLUMN ORDER (RAW + NORMALIZED)
# =====================================================
COLUMN_ORDER = [
    # ===== identity =====
    "city",
    "category",
    "category_code",

    # ===== content =====
    "title",

    # ===== raw =====
    "price_string",
    "price",
    "price_million_per_m2",
    "area",

    # ===== location (SEPARATE, NO JOIN) =====
    "ward_name",
    "area_name",

    # ===== meta =====
    "crawl_time",

    # ===== key =====
    "link",
]

# =====================================================
# FIXED COLUMN WIDTHS
# =====================================================
COLUMN_WIDTHS = {
    # identity
    "city": 14,
    "category": 22,
    "category_code": 14,

    # content
    "title": 100,

    # raw
    "price_string": 15,
    "price": 15,
    "price_million_per_m2": 18,
    "area": 12,

    # location
    "ward_name": 24,
    "area_name": 24,
    "region_name": 24,

    # meta
    "crawl_time": 20,

    # key
    "link": 200,
}

# =====================================================
# SAVE FUNCTION
# =====================================================
def save_city_data(data, city_key, output_dir):
    """
    Save crawled city data to CSV and formatted Excel.

    Returns:
        df, path_xlsx, path_csv
    """
    os.makedirs(output_dir, exist_ok=True)
    df = pd.DataFrame(data)

    path_xlsx = None
    path_csv = None

    if not df.empty:
        # ======================
        # CLEAN
        # ======================
        if "link" in df.columns:
            df = df.dropna(subset=["link"])
            df = df.drop_duplicates(subset=["link"])

        # ======================
        # APPLY FIXED ORDER (SAFE)
        # ======================
        ordered_cols = [c for c in COLUMN_ORDER if c in df.columns]
        remaining_cols = [c for c in df.columns if c not in ordered_cols]
        df = df[ordered_cols + remaining_cols]

        # ======================
        # PATHS
        # ======================
        path_xlsx = os.path.join(output_dir, f"{city_key}.xlsx")
        path_csv = path_xlsx.replace(".xlsx", ".csv")

        # ======================
        # SAVE CSV
        # ======================
        df.to_csv(path_csv, index=False)

        # ======================
        # SAVE EXCEL (FORMATTED)
        # ======================
        with pd.ExcelWriter(path_xlsx, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name=city_key)
            ws = writer.sheets[city_key]

            # Freeze header
            ws.freeze_panes = "A2"

            # Enable filter
            ws.auto_filter.ref = ws.dimensions

            # Center header
            for cell in ws[1]:
                cell.alignment = Alignment(horizontal="center")

            # Fixed widths
            for idx, col in enumerate(df.columns, start=1):
                ws.column_dimensions[
                    ws.cell(row=1, column=idx).column_letter
                ].width = COLUMN_WIDTHS.get(col, 18)

    return df, path_xlsx, path_csv
