import warnings
import urllib3

# Suppress the specific NotOpenSSLWarning
warnings.filterwarnings('ignore', category=urllib3.exceptions.NotOpenSSLWarning)

import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import re
import os
from datetime import datetime

def get_google_search_results(query):
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    return response.text

def parse_search_results(html_content, company, search_term):
    soup = BeautifulSoup(html_content, 'html.parser')
    results = []
    position = 1

    for result in soup.select('.g'):
        title_element = result.select_one('.LC20lb')
        link_element = result.select_one('.yuRUbf a')
        snippet_element = result.select_one('.VwiC3b')
        rating_element = result.select_one('.fG8Fp .ChPIuf')
        rating2_element = result.select_one('.fG8Fp .z3HNkc')
        review_site_element = result.select_one('.VuuXrf')

        if title_element and link_element:
            title = title_element.text.strip()
            link = link_element['href']
            snippet = snippet_element.text.strip() if snippet_element else ""
            review_site = review_site_element.text.strip() if review_site_element else ""
            
            rating = ""
            rating_threshold = ""
            reviews = ""
            rating2 = ""
            
            if rating_element:
                rating_text = rating_element.text
                rating_match = re.search(r'Rating: (\d+(?:\.\d+)?)', rating_text)
                if rating_match:
                    rating = rating_match.group(1)
                
                threshold_match = re.search(r'out of (\d+)', rating_text)
                if threshold_match:
                    rating_threshold = threshold_match.group(1).rstrip(',')
                
                reviews_match = re.search(r'(\d+) reviews', rating_text)
                if reviews_match:
                    reviews = reviews_match.group(1)

            if rating2_element:
                rating2 = rating2_element.get('aria-label', '').replace(',', '')

            results.append({
                'position': position,
                'company': company,
                'search_term': search_term,
                'review_site': review_site,
                'title': title,
                'link': link,
                'snippet': snippet,
                'rating': rating,
                'rating_threshold': rating_threshold,
                'reviews': reviews,
                'rating2': rating2
            })
            position += 1

    return results

def save_to_csv(results, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['position', 'company', 'search_term', 'review_site', 'title', 'link', 'snippet', 'rating', 'rating_threshold', 'reviews', 'rating2']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)

def main():
    companies = ["cj", "cj affiliate", "ShareASale", "ClickBank", "Impact", "impact radius", "AWIN",
        "Rakuten Advertising", "Partnerize" ]
    search_terms = ["reviews", "ratings", " "]
    
    all_results = []

    for company in companies:
        for search_term in search_terms:
            query = f"{company} {search_term}"
            html_content = get_google_search_results(query)
            
            results = parse_search_results(html_content, company, search_term)
            
            all_results.extend(results)
            
            time.sleep(random.uniform(1, 3))  # Add a random delay between requests

    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create filename with current date
    current_date = datetime.now().strftime('%Y-%m-%d')
    filename = f'affiliate_network_reviews_{current_date}.csv'
    
    # Create the full path for the CSV file
    csv_path = os.path.join(script_dir, filename)
    
    save_to_csv(all_results, csv_path)

if __name__ == "__main__":
    main()