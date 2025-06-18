import os
import requests
import pandas as pd
from bs4 import BeautifulSoup

def fetch_dod_contracts():
    url = "https://www.defense.gov/News/Contracts/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("article", class_="contract")
    print(f"Found {len(articles)} contract articles.")
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

    # Ensure the data folder exists
    os.makedirs("data", exist_ok=True)

    # Save to CSV
    df = pd.DataFrame(data)
    df.to_csv("data/dod_contracts.csv", index=False)

if __name__ == "__main__":
    fetch_dod_contracts()
