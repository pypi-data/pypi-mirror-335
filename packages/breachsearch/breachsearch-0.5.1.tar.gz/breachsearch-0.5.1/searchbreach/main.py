import requests
import json
import argparse

def search_breach(data):
    url = "https://breachsearch.site/search"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://breachsearch.site",
        "Referer": "https://breachsearch.site/",
    }
    data = {"query": data}

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        try:
            json_data = response.json()
            if "grouped_data" in json_data:
                for group in json_data["grouped_data"]:
                    db_name = group.get("db", "Unknown Database")
                    print(f"\nData leak from: {db_name}\n")
                    if "data" in group:
                        for entry in group["data"]:
                            for key, value in entry.items():
                                print(f"{key}: {value}")
                            print("\n")
            else:
                print("No data found for the given input.")
        except json.JSONDecodeError:
            print("Invalid JSON response received.")
    else:
        print(f"Request failed with status code: {response.status_code}")

def main():
    parser = argparse.ArgumentParser(description="Check if an email, domain, phone number, or keyword is in a data breach.")
    parser.add_argument("data", help="Enter an email, domain, phone number (with country code), or keyword to check.")
    args = parser.parse_args()

    search_breach(args.data)

if __name__ == "__main__":
    main()
