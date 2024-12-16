import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urlparse, quote_plus
import os
import time

def scrape_google_search(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    search_results = []
    position = 1

    for result in soup.select('div.g'):
        title = result.select_one('h3')
        link = result.select_one('a')
        snippet = result.select_one('div.VwiC3b')
        
        if title and link:
            site_name = urlparse(link['href']).netloc
            search_results.append({
                'Position': position,
                'Title': title.text,
                'URL': link['href'],
                'Site Name': site_name,
                'Snippet': snippet.text if snippet else 'N/A'
            })
            position += 1

    people_also_search = [item.text for item in soup.select('div.AJLUJb > div')]
    related_keywords = [item.text for item in soup.select('div.s75CSd')]

    return search_results, people_also_search, related_keywords

def save_to_csv(all_data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Company', 'Position', 'Title', 'URL', 'Site Name', 'Snippet'])
        
        for company, data in all_data.items():
            writer.writerow([company])  # Write company name as a header
            for result in data['results']:
                writer.writerow([company] + [result[key] for key in ['Position', 'Title', 'URL', 'Site Name', 'Snippet']])
            writer.writerow([])  # Empty row for separation
            
            writer.writerow(['People also search for'])
            for item in data['also_search']:
                writer.writerow([item])
            writer.writerow([])
            
            writer.writerow(['Related Keywords'])
            for item in data['keywords']:
                writer.writerow([item])
            writer.writerow([])
            writer.writerow([])  # Double empty row for better separation between companies

# List of companies
companies = [
    "cj",
    "cj affiliate",
    "ShareASale",
    "ClickBank",
    "Impact",
    "AWIN",
    "Rakuten Advertising",
    "Partnerize"
]

# Main execution
all_data = {}
base_url = "https://www.google.com/search?q={0}+reviews"

for company in companies:
    print(f"Scraping data for {company}...")
    url = base_url.format(quote_plus(company))
    results, also_search, keywords = scrape_google_search(url)
    all_data[company] = {
        'results': results,
        'also_search': also_search,
        'keywords': keywords
    }
    time.sleep(2)  # Add a delay to avoid overwhelming the server

# Get the directory of the current script
script_directory = os.path.dirname(os.path.abspath(__file__))

# Create the full path for the CSV file
csv_file_path = os.path.join(script_directory, 'all_companies_search_results.csv')

# Save results to CSV
save_to_csv(all_data, csv_file_path)
print(f"\nResults for all companies saved to {csv_file_path}")