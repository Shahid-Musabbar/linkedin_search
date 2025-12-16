import requests
import json
import os
from datetime import date
from typing import List, Dict
from dotenv import load_dotenv  
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

USAGE_FILE = "google_cse_usage.json"
DAILY_LIMIT = 100


def _check_and_increment_usage():
    today = date.today().isoformat()

    if os.path.exists(USAGE_FILE):
        with open(USAGE_FILE, "r") as f:
            usage = json.load(f)
    else:
        usage = {}

    # Reset count if new day
    if usage.get("date") != today:
        usage = {"date": today, "count": 0}

    if usage["count"] >= DAILY_LIMIT:
        raise RuntimeError(
            "Daily Google Custom Search API limit (100) reached. "
            "Try again tomorrow."
        )

    usage["count"] += 1

    with open(USAGE_FILE, "w") as f:
        json.dump(usage, f)


def search_linkedin_company(company_name: str, num_results: int = 5) -> List[Dict]:
    """
    Searches Google for LinkedIn company pages using:
    site:linkedin.com/company <company_name>

    Enforces a hard limit of 100 API calls per day.
    """

    _check_and_increment_usage()  # 🔐 protect quota

    query = f"site:linkedin.com/company {company_name}"

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": query,
        "num": min(num_results, 10)
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()

    results = []
    for item in data.get("items", []):
        results.append({
            "title": item.get("title"),
            "link": item.get("link"),
            "snippet": item.get("snippet")
        })

    return results
