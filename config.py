# fetch_data/config.py
OUTPUT_DIR = "output"

CHO_TOT_PUBLIC_API_URL = "https://gateway.chotot.com/v1/public/ad-listing"

CITIES = {
    "hanoi": {
        "name": "Hà Nội",
        "region_v2": "12000",
        "category": "Bán nhà", # type = "s"
        "category_code": "1020",
        "limit": 100,
        "page": 5,
    },
    "hcm": {
        "name": "TP Hồ Chí Minh",
        "region_v2": "13000",
        "category": "Bán nhà", # type = "s"
        "category_code": "1020",
        "limit": 100,
        "page": 5,
    },
}
