import json
import requests

def scrape_data():
    # Your scraping logic here
    data = {"message": "Scraping completed successfully!"}
    with open('job_data.json', 'w') as f:
        json.dump(data, f)

if __name__ == "__main__":
    scrape_data()
    print("Scraping finished. Data saved to job_data.json.")
