import requests
from bs4 import BeautifulSoup
import json
import os
import datetime

USERNAME = "Ayush-5787"
URL = f"https://github.com/users/{USERNAME}/contributions"

def fetch_data():
    print(f"Fetching contributions for {USERNAME}...")
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        resp = requests.get(URL, headers=headers, timeout=10)
        print(f"HTTP Status Code: {resp.status_code}")
        
        if resp.status_code != 200:
            print("❌ Failed to fetch data.")
            return False
            
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Try multiple selectors for robustness
        cells = soup.select(".ContributionCalendar-day[data-date]")
        if not cells:
            cells = soup.select("[data-date]")
            
        if not cells:
            print("⚠️ No contribution cells found. Saving empty data.")
            output = {"days": [], "stats": {"total": 0}}
            os.makedirs("data", exist_ok=True)
            with open("data/contributions.json", "w") as f:
                json.dump(output, f, indent=2)
            return True

        days = []
        total_contributions = 0
        
        for cell in cells:
            date_str = cell.get("data-date")
            label = cell.get("aria-label", "")
            count = 0
            if "contribution" in label.lower():
                parts = label.split()
                for p in parts:
                    if p.isdigit():
                        count = int(p)
                        break
            
            level = 0
            if count > 0: level = 1
            if count >= 3: level = 2
            if count >= 5: level = 3
            if count >= 10: level = 4
            
            days.append({"date": date_str, "count": count, "level": level})
            total_contributions += count

        stats = {
            "total": total_contributions,
            "last_updated": datetime.datetime.now().isoformat()
        }
        
        output = {"days": days, "stats": stats}
        
        os.makedirs("data", exist_ok=True)
        filepath = "data/contributions.json"
        with open(filepath, "w") as f:
            json.dump(output, f, indent=2)
            
        print(f"✅ Successfully saved {filepath} ({total_contributions} contributions)")
        return True
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        return False

if __name__ == "__main__":
    fetch_data()