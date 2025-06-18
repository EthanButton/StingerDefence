import os
import feedparser
import pandas as pd
from newspaper import Article
from time import sleep

COMPANIES = [
    "Lockheed Martin", "Raytheon", "Northrop Grumman", "General Dynamics",
    "L3Harris", "BAE Systems", "Airbus", "Boeing", "Thales", "Leonardo"
]

def summarize_article(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        article.nlp()
        return article.summary
    except Exception as e:
        print(f"❌ Could not summarize: {url} — {e}")
        return "Summary not available."

def fetch_news():
    news_items = []

    for company in COMPANIES:
        query = company.replace(" ", "+")
        url = f"https://news.google.com/rss/search?q={query}+defense"
        feed = feedparser.parse(url)

        for entry in feed.entries[:5]:
            summary = summarize_article(entry.link)
            news_items.append({
                "company": company,
                "title": entry.title,
                "link": entry.link,
                "published": entry.published,
                "summary": summary
            })
            sleep(1)  # avoid being rate-limited

    os.makedirs("data", exist_ok=True)
    df = pd.DataFrame(news_items)
    df.to_csv("data/defense_news.csv", index=False)
    print(f"✅ Saved {len(df)} news stories.")

if __name__ == "__main__":
    fetch_news()
