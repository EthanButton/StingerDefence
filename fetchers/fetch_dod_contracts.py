import requests
import pandas as pd
from bs4 import BeautifulSoup

def fetch_dod_contracts():
    url = "https://www.defense.gov/News/Contracts/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("article", class_="contract")
    data = []

    for article in articles:
        title = article.find("h3").text.strip()
        date = article.find("time")["datetime"].split("T")[0]
        summary = article.find("div", class_="contract-content").text.strip()
        link = article.find("a")["href"]
        data.append({
            "date": date,
            "title": title,
            "summary": summary,
            "link": f"https://www.defense.gov{link}"
        })

    df = pd.DataFrame(data)
    import os
os.makedirs("data", exist_ok=True)
    df.to_csv("data/dod_contracts.csv", index=False)
