#!/usr/bin/env python3
"""
Daily LeetCode picker for Notion (updated for the 2025-09-03 data sources API).

Picks one random not-yet-completed problem from your Notion database,
clears any previous "Today" flag, and marks the chosen one as today's problem.

Setup:
  1. Create an internal integration and copy its token (starts with "ntn_").
  2. Open your database as a full page -> ••• -> Connections -> add the integration.
  3. Set environment variables NOTION_TOKEN and DATABASE_ID.
       - DATABASE_ID is the 32-char string in the database URL.
  4. Your database needs two checkbox properties named exactly:
       - "Today"      (the picker sets this)
       - "Completed"  (you check this when you finish a problem)
  5. Run:  pip install requests  &&  python daily_leetcode_2.py
"""

import os
import random
import sys
import requests

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DATABASE_ID = os.environ["DATABASE_ID"]

API = "https://api.notion.com/v1"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2025-09-03",   # <-- new data-sources API version
    "Content-Type": "application/json",
}


def get_data_source_id():
    """A database is now a container of one or more data sources.
    Look up the first data source's ID for this database."""
    r = requests.get(f"{API}/databases/{DATABASE_ID}", headers=HEADERS)
    r.raise_for_status()
    sources = r.json().get("data_sources", [])
    if not sources:
        print("No data sources found on this database.")
        sys.exit(1)
    return sources[0]["id"]


def query_all(data_source_id, filter_):
    """Return every page matching a filter, following pagination."""
    results, cursor = [], None
    while True:
        body = {"filter": filter_, "page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        r = requests.post(
            f"{API}/data_sources/{data_source_id}/query",
            headers=HEADERS,
            json=body,
        )
        r.raise_for_status()
        data = r.json()
        results.extend(data["results"])
        if not data.get("has_more"):
            return results
        cursor = data["next_cursor"]


def set_checkbox(page_id, name, value):
    r = requests.patch(
        f"{API}/pages/{page_id}",
        headers=HEADERS,
        json={"properties": {name: {"checkbox": value}}},
    )
    r.raise_for_status()


def title_of(page):
    prop = next(
        (v for v in page["properties"].values() if v["type"] == "title"), None
    )
    if prop and prop["title"]:
        return prop["title"][0]["plain_text"]
    return "(untitled)"


def main():
    ds = get_data_source_id()

    # 1. Clear yesterday's pick.
    for page in query_all(ds, {"property": "Today", "checkbox": {"equals": True}}):
        set_checkbox(page["id"], "Today", False)

    # 2. Gather all problems not yet completed.
    pool = query_all(ds, {"property": "Completed", "checkbox": {"equals": False}})
    if not pool:
        print("Nothing left -- you've completed every problem.")
        sys.exit(0)

    # 3. Pick one at random and flag it as today's problem.
    choice = random.choice(pool)
    set_checkbox(choice["id"], "Today", True)
    print(f"Today's problem: {title_of(choice)}")


if __name__ == "__main__":
    main()
