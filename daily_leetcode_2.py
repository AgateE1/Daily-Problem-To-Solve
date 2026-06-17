#!/usr/bin/env python3
"""
Daily LeetCode picker for Notion.

Picks one random not-yet-completed problem from your Notion database,
clears any previous "Today" flag, and marks the chosen one as today's problem.

Setup:
  1. Create an internal integration at https://www.notion.so/my-integrations
     and copy its token (starts with "ntn_" or "secret_").
  2. Share your LeetCode database with that integration:
     open the database -> ••• menu -> Connections -> add your integration.
  3. Set environment variables NOTION_TOKEN and DATABASE_ID.
       - DATABASE_ID is the 32-char string in the database URL.
  4. Your database needs two checkbox properties named exactly:
       - "Today"      (the picker sets this)
       - "Completed"  (you check this when you finish a problem)
  5. Run:  pip install requests  &&  python daily_leetcode.py
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
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


def query_all(filter_):
    """Return every page matching a filter, following pagination."""
    results, cursor = [], None
    while True:
        body = {"filter": filter_, "page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        r = requests.post(
            f"{API}/databases/{DATABASE_ID}/query", headers=HEADERS, json=body
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
    # 1. Clear yesterday's pick.
    for page in query_all({"property": "Today", "checkbox": {"equals": True}}):
        set_checkbox(page["id"], "Today", False)

    # 2. Gather all problems not yet completed.
    pool = query_all({"property": "Completed", "checkbox": {"equals": False}})
    if not pool:
        print("Nothing left -- you've completed every problem.")
        sys.exit(0)

    # 3. Pick one at random and flag it as today's problem.
    choice = random.choice(pool)
    set_checkbox(choice["id"], "Today", True)
    print(f"Today's problem: {title_of(choice)}")


if __name__ == "__main__":
    main()
