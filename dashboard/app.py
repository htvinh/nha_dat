import streamlit as st
import pandas as pd
import os
import sys
import traceback

# Fix import path – same fix that made main.py work
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import from your working main.py & config
from fetch_data.fetch_data import crawl_city, get_data
from config import CITIES

# Your original modules for reports
from analytics.metrics import (
    price_by_district,
    price_m2_by_district_category,
    supply_by_district
)
from analytics.trends import trend_7_days
from analytics.deals import detect_deals
from reports.export_excel import export_excel
from reports.export_docx import export_docx

# Constants
OUTPUT_DIR = "output"
REPORTS_DIR = "output_reports"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# ────────────────────────────────────────────────────────────────
# STREAMLIT INTERFACE
# ────────────────────────────────────────────────────────────────
st.set_page_config(layout="wide")
st.title("🏘️ Bất Động Sản - Robot")

# Sidebar
city_key = st.sidebar.selectbox(
    "Chọn thành phố",
    list(CITIES.keys()),
    format_func=lambda x: CITIES[x]["name"]
)

#mode = st.sidebar.radio(
#    "Chế độ chạy",
#    ["Chỉ thành phố được chọn", "Toàn bộ thành phố"]
#)

mode = "Chỉ thành phố được chọn"

if st.sidebar.button("🧹 Clear session & retry"):
    st.session_state.clear()
    st.rerun()

# Main button
if st.sidebar.button("🚀 Tìm kiếm"):
    with st.spinner("Đang thu thập dữ liệu... Vui lòng chờ"):
        try:
            if mode == "Toàn bộ các thành phố":
                #st.info("Chạy toàn bộ quy trình ...")
                get_data()
                st.success("Hoàn tất thu thập tất cả thành phố!")
                st.info(f"Kết quả lưu tại: **{os.path.abspath(OUTPUT_DIR)}**")
                st.info("Các file ví dụ: hanoi.xlsx, hanoi.csv, ...")

            else:
                # Reuse crawl_city from main.py
                city_config = CITIES[city_key]
                st.info(f"Thu thập dữ liệu chỉ cho: **{city_config['name']}**")

                crawl_city(city_key, city_config)

                st.success(f"Thu thập xong cho {city_config['name']}")
                #st.info(f"Kết quả lưu tại:")
                #st.info(f"• **{os.path.abspath(os.path.join(OUTPUT_DIR, f'{city_key}.xlsx'))}**")
                #st.info(f"• **{os.path.abspath(os.path.join(OUTPUT_DIR, f'{city_key}.csv'))}**")

            # ── Try to load latest data for display (optional) ──
            latest_file = os.path.join(OUTPUT_DIR, f"{city_key}.xlsx")
            if os.path.exists(latest_file) and mode != "Toàn bộ các thành phố":
                try:
                    df = pd.read_excel(latest_file)
                    st.session_state.df = df
                    st.session_state.data_excel = latest_file
                    st.session_state.data_csv = latest_file.replace(".xlsx", ".csv")
                except:
                    st.warning("Không đọc được file kết quả để hiển thị")

        except Exception as e:
            st.error("Có lỗi xảy ra khi chạy scraper")
            with st.expander("Chi tiết lỗi"):
                pass
                st.code(str(e))
                st.code(traceback.format_exc())

# ────────────────────────────────────────────────────────────────
# DATA VIEW & REPORTS (your original logic)
# ────────────────────────────────────────────────────────────────
if "df" in st.session_state:
    df = st.session_state.df

    st.subheader("📋 Dữ liệu đã thu thập")
    st.dataframe(df, use_container_width=True)

    st.subheader("⬇️ Tải xuống dữ liệu")
    if "data_excel" in st.session_state:
        with open(st.session_state.data_excel, "rb") as f:
            st.download_button(
                "Download Excel",
                f.read(),
                file_name=os.path.basename(st.session_state.data_excel),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # Reports section
    st.subheader("📊 Báo cáo")

    with st.spinner("Đang tạo báo cáo..."):
        try:
            reports = {
                "Giá trung bình & median theo quận": price_by_district(df),
                "Giá/m² theo quận + loại": price_m2_by_district_category(df),
                "Nguồn cung theo quận": supply_by_district(df),
                "Xu hướng 7 ngày": trend_7_days(df),
                "Tin giá tốt": detect_deals(df)
            }

            excel_report = os.path.join(REPORTS_DIR, f"{city_key}_report.xlsx")
            docx_report = os.path.join(REPORTS_DIR, f"{city_key}_deals.docx")

            
            export_excel(reports, excel_report)
            export_docx(df, reports["Tin giá tốt"], docx_report)

            st.session_state.report_excel = excel_report
            st.session_state.report_docx = docx_report
            st.success("✅ Báo cáo đã được tạo!")

        except Exception as report_error:
            st.error("Lỗi khi tạo báo cáo")
            st.code(str(report_error))

    if "report_excel" in st.session_state:
        st.subheader("⬇️ Download Báo cáo")

        with open(st.session_state.report_excel, "rb") as f:
            st.download_button(
                "Download Excel Báo cáo phân tích",
                f.read(),
                file_name=os.path.basename(st.session_state.report_excel),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        with open(st.session_state.report_docx, "rb") as f:
            st.download_button(
                "Download DOCX Báo cáo Tin giá tốt",
                f.read(),
                file_name=os.path.basename(st.session_state.report_docx),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

else:
    st.info("👈 Chọn thành phố và nhấn **Tìm kiếm**")
    #st.caption("Dữ liệu sẽ được lấy trực tiếp từ logic của main.py")