import os
import requests
import pandas as pd
from bs4 import BeautifulSoup

def fetch_dod_contracts():
    url = "https://www.defense.gov/News/Contracts/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # raise error if site is down

    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("article", class_="contract")

    data = []
    for article in articles:
        try:
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
        except Exception as e:
            print(f"⚠️ Skipped a contract due to parsing error: {e}")

    os.makedirs("data", exist_ok=True)
    df = pd.DataFrame(data)
    df.to_csv("data/dod_contracts.csv", index=False)
    print(f"✅ Saved {len(data)} DoD contract entries.")

if __name__ == "__main__":
    fetch_dod_contracts()
