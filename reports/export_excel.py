import re
from typing import Dict

import pandas as pd
from openpyxl.styles import Alignment
from openpyxl.worksheet.worksheet import Worksheet


# =====================================================
# Excel-safe sheet name
# =====================================================
def clean_sheet_name(name: str) -> str:
    """
    Clean sheet name to satisfy Excel constraints:
    - Max 31 characters
    - Cannot contain: \\ / ? * [ ]
    """
    cleaned: str = re.sub(r"[\\\/\?\*\[\]]", "-", name)
    result: str = cleaned[:31]
    return result


# =====================================================
# Worksheet formatting
# =====================================================
def format_worksheet(ws: Worksheet) -> None:
    """
    Apply standard formatting to an Excel worksheet.
    """
    # Freeze header
    ws.freeze_panes = "A2"

    # Enable filters
    ws.auto_filter.ref = ws.dimensions

    # Center header row
    for cell in ws[1]:
        cell.alignment = Alignment(horizontal="center")

    # Auto column width (safe cap)
    for column in ws.columns:
        values = (str(cell.value) for cell in column if cell.value is not None)
        max_length = max((len(v) for v in values), default=10)
        ws.column_dimensions[column[0].column_letter].width = min(
            max_length + 2, 40
        )


# =====================================================
# Export Excel
# =====================================================
def export_excel(
    reports: Dict[str, pd.DataFrame],
    output_path: str,
) -> None:
    """
    Export multiple reports to a single Excel file.

    Parameters
    ----------
    reports : dict[str, DataFrame]
        Mapping of sheet name → DataFrame
    output_path : str
        Destination Excel file path
    """
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for sheet_name, df in reports.items():
            if df is None or df.empty:
                continue

            safe_name = clean_sheet_name(sheet_name)

            df.to_excel(
                writer,
                sheet_name=safe_name,
                index=False,
            )

            worksheet = writer.sheets[safe_name]
            format_worksheet(worksheet)

    print(f"📊 Excel report exported to: {output_path}")
