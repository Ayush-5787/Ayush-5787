import requests
import json
import os
from datetime import datetime, timedelta

USERNAME = "Ayush-5787"
API_URL = "https://api.github.com/graphql"

# Query to get contributions for the last 365 days
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
    print(f"Fetching live data for {USERNAME} via GitHub API...")
    
    # Calculate date range: Today back to 365 days ago
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
        
        # Flatten weeks into a list of days
        days_list = []
        for week in weeks:
            for day in week["contributionDays"]:
                days_list.append({
                    "date": day["date"],
                    "count": day["count"],
                    "level": day["level"] # Level is already 0-4 from API!
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