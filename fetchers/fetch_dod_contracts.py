import os
import pandas as pd
import feedparser

def fetch_dod_contracts():
    # RSS feed URL for official DoD contract announcements
    url = "https://www.defense.gov/News/Contracts/?rss"

    # Parse the RSS feed
    feed = feedparser.parse(url)
    data = []

    for entry in feed.entries:
        data.append({
            "date": entry.get("published", ""),
            "title": entry.get("title", ""),
            "summary": entry.get("summary", "").strip(),
            "link": entry.get("link", "")
        })

    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    # Save to CSV
    df = pd.DataFrame(data)
    df.to_csv("data/dod_contracts.csv", index=False)

    print(f"✅ Saved {len(data)} DoD contract entries.")

if __name__ == "__main__":
    fetch_dod_contracts()
