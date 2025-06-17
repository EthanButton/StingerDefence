import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

def fetch_dod_contracts():
    url = "https://www.defense.gov/News/Contracts/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("article")

    contracts = []
    for article in articles[:10]:  # limit for demo
        title = article.find("h4").get_text(strip=True)
        link = article.find("a")["href"]
        summary = article.find("p").get_text(strip=True)
        contracts.append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "title": title,
            "summary": summary,
            "link": "https://www.defense.gov" + link
        })

    df = pd.DataFrame(contracts)

    # Ensure data folder exists
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/dod_contracts.csv", index=False)
