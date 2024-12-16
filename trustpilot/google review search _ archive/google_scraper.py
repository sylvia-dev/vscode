import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urlparse
import os

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

    # Extract "People also search for"
    people_also_search = [item.text for item in soup.select('div.AJLUJb > div')]

    # Extract related keywords (if available)
    related_keywords = [item.text for item in soup.select('div.s75CSd')]

    return search_results, people_also_search, related_keywords

def save_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

# Main execution
url = "https://www.google.com/search?q=cj+reviews"
results, also_search, keywords = scrape_google_search(url)

# Print results
print("Search Results:")
for result in results:
    print(result)

print("\nPeople also search for:")
print(also_search)

print("\nRelated Keywords:")
print(keywords)

# Get the directory of the current script
script_directory = os.path.dirname(os.path.abspath(__file__))

# Create the full path for the CSV file
csv_file_path = os.path.join(script_directory, 'search_results.csv')

# Save results to CSV
save_to_csv(results, csv_file_path)
print(f"\nResults saved to {csv_file_path}")