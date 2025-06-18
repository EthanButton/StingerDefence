import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
import sys

def fetch_dod_contracts():
    url = "https://www.defense.gov/News/Contracts/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Updated logic for current site layout
    articles = soup.select("main article")  # More reliable than old class

    sys.stdout.write(f"📦 Found {len(articles)} contract articles.\n")
    sys.stdout.flush()

    data = []
    for article in articles:
        try:
            title = article.find("h3").get_text(strip=True)
            date = article.find("time")["datetime"].split("T")[0]
            summary = article.find("div", class_="contract-content").get_text(strip=True)
            link_tag = article.find("a")
            link = f"https://www.defense.gov{link_tag['href']}" if link_tag else url
            data.append({
                "date": date,
                "title": title,
                "summary": summary,
                "link": link
            })
        except Exception as e:
            continue  # Skip any malformed entries

    # Save to CSV
    os.makedirs("data", exist_ok=True)
    df = pd.DataFrame(data)
    df.to_csv("data/dod_contracts.csv", index=False)

if __name__ == "__main__":
    fetch_dod_contracts()
    print("✅ Scraper completed successfully.")
