import os
import feedparser
import pandas as pd

COMPANIES = [
    "Lockheed Martin", "Raytheon", "Northrop Grumman", "General Dynamics",
    "L3Harris", "BAE Systems", "Airbus", "Boeing", "Thales", "Leonardo", "Huntington Ingalls", "Textron", "Leidos", "Mercury Systems", "Kratos", "Curtiss-Wright", "CACI International", "Oshkosh", "Rheinmetall", "Saab", "Kongsberg Gruppen", "Dassault Aviation", "Hensoldt AG", "Elbit Systems", "Babcock International", "Serco Group", "Rolls-Royce Holdings", "QinetiQ Group", "MTU Aero Engines"
]

def fetch_news():
    news_items = []

    for company in COMPANIES:
        query = company.replace(" ", "+")
        url = f"https://news.google.com/rss/search?q={query}+defense"

        feed = feedparser.parse(url)

        for entry in feed.entries[:5]:
            news_items.append({
                "company": company,
                "title": entry.title,
                "link": entry.link,
                "published": entry.published
            })

    os.makedirs("data", exist_ok=True)
    df = pd.DataFrame(news_items)
    df.to_csv("data/defense_news.csv", index=False)
    print(f"✅ Saved {len(df)} news stories.")

if __name__ == "__main__":
    fetch_news()
