
import os
import sys
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


import requests
from datetime import datetime, UTC
from typing import List, Dict, Any

from fetch_data.storage import save_city_data
import config 


# =====================================================
# API CONFIG
# =====================================================
URL = config.CHO_TOT_PUBLIC_API_URL

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


# =====================================================
# HELPERS
# =====================================================
def get_str(value: Any) -> str:
    """
    Safe string extractor.
    """
    return value if isinstance(value, str) else ""


# =====================================================
# FETCH
# =====================================================
def fetch_ads(
    city_key: str,
    city_config: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Fetch real estate ads from NhaTot API and normalize to storage schema.
    """
    params = {
        "region_v2": city_config["region_v2"],
        "cg": city_config["category_code"],
        "limit": city_config.get("limit", 200),
        "page": city_config.get("page", 2),
    }

    response = requests.get(
        URL,
        params=params,
        headers=HEADERS,
        timeout=15,
    )
    response.raise_for_status()

    payload = response.json()
    ads = payload.get("ads", [])

    crawl_time = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")

    results: List[Dict[str, Any]] = []

    for ad in ads:
        type_sell_or_rent = ad.get("type")
        if type_sell_or_rent != "s":
            continue

        area = ad.get("area") or ad.get("land_area")

        ward_name = get_str(ad.get("ward_name_v3") or ad.get("ward_name"))
        area_name = get_str(ad.get("area_name"))
        region_name = get_str(ad.get("region_name_v3") or ad.get("region_name"))

        item: Dict[str, Any] = {
            # ======================
            # identity
            # ======================
            "city": city_config["name"],
            "category": city_config["category"],
            "category_code": city_config["category_code"],

            # ======================
            # content
            # ======================
            "title": ad.get("subject"),

            # ======================
            # raw
            # ======================
            "price": ad.get("price"),
            "price_string": ad.get("price_string"), 
            "price_million_per_m2": ad.get("price_million_per_m2"),
            "area": area,


            # ======================
            # location (SEPARATE – NO JOIN)
            # ======================
            "ward_name": ward_name,
            "area_name": area_name,

            # ======================
            # meta
            # ======================
            "crawl_time": crawl_time,

            # ======================
            # key
            # ======================
            "link": f"https://www.nhatot.com/{ad.get('list_id')}",
        }

        results.append(item)

    return results


# =====================================================
# CRAWL CITY
# =====================================================
def crawl_city(city_key: str, city_config: Dict[str, Any]) -> None:
    """
    Fetch and persist data for one city.
    """
    print(f"🚀 Crawling {city_config['name']}")

    data = fetch_ads(city_key, city_config)

    df, path_xlsx, path_csv = save_city_data(
        data=data,
        city_key=city_key,
        output_dir=config.OUTPUT_DIR,
    )

    print(f"✅ {city_config['name']}: {len(df)} listings")

    if path_xlsx:
        print(f"📊 Excel saved: {path_xlsx}")
    if path_csv:
        print(f"📄 CSV saved: {path_csv}")


# =====================================================
# MAIN
# =====================================================
def get_data() -> None:
    """
    Crawl all configured cities.
    """
    for city_key, city_config in config.CITIES.items():
        crawl_city(city_key, city_config)


if __name__ == "__main__":
    get_data()
