import requests
import json
import os
from datetime import datetime, timedelta

USERNAME = "Ayush-5787"
API_URL = "https://api.github.com/graphql"

QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            count
            level
          }
        }
      }
    }
  }
}
"""

def fetch_data():
    print(f"Fetching live data for {USERNAME}...")
    
    today = datetime.utcnow()
    start_date = today - timedelta(days=365)
    
    payload = {
        "query": QUERY,
        "variables": {
            "login": USERNAME,
            "from": start_date.isoformat(),
            "to": today.isoformat()
        }
    }
    
    headers = {"Content-Type": "application/json"}
    
    # Check if Token exists (provided by GitHub Actions)
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
        print("✅ Using GitHub Token for authentication.")
    else:
        print("⚠️ No Token found. Trying unauthenticated request (may hit rate limit).")
        
    try:
        resp = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        
        data = resp.json()
        
        if "errors" in data:
            print(f"❌ API Error: {data['errors']}")
            return False
            
        collection = data["data"]["user"]["contributionsCollection"]
        calendar = collection["contributionCalendar"]
        
        total = calendar["totalContributions"]
        weeks = calendar["weeks"]
        
        days_list = []
        for week in weeks:
            for day in week["contributionDays"]:
                days_list.append({
                    "date": day["date"],
                    "count": day["count"],
                    "level": day["level"]
                })
                
        output = {
            "days": days_list,
            "stats": {
                "total": total,
                "last_updated": datetime.now().isoformat()
            }
        }
        
        os.makedirs("data", exist_ok=True)
        filepath = "data/contributions.json"
        with open(filepath, "w") as f:
            json.dump(output, f, indent=2)
            
        print(f"✅ Success! Found {total} contributions.")
        return True
        
    except Exception as e:
        print(f"❌ Failed to fetch data: {e}")
        return False

if __name__ == "__main__":
    fetch_data()