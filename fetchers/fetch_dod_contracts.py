import os
import pandas as pd
import feedparser
import sys

def fetch_dod_contracts():
    url = "https://www.defense.gov/News/Contracts/?rss"
    feed = feedparser.parse(url)

    sys.stdout.write(f"📡 RSS Feed status: {feed.get('status', 'unknown')}\n")
    sys.stdout.write(f"📰 Entries found in RSS feed: {len(feed.entries)}\n")

    data = []
    for entry in feed.entries:
        data.append({
            "date": entry.get("published", ""),
            "title": entry.get("title", ""),
            "summary": entry.get("summary", "").strip(),
            "link": entry.get("link", "")
        })

    os.makedirs("data", exist_ok=True)
    df = pd.DataFrame(data)
    df.to_csv("data/dod_contracts.csv", index=False)

    print(f"✅ Saved {len(data)} DoD contract entries.")

if __name__ == "__main__":
    fetch_dod_contracts()
