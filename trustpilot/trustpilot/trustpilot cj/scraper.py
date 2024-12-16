import requests
from bs4 import BeautifulSoup
import csv
import re  # Add this import for regular expressions
from datetime import datetime
import os

# Function to scrape a single review page
def scrape_page(page_url):
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    reviews = []
    
    # Find all review cards on the page
    review_cards = soup.find_all('div', class_='styles_cardWrapper__LcCPA')

    for card in review_cards:
        # Extracting each element using the CSS selectors
        username = card.select_one('.typography_heading-xxs__QKBS8').text.strip() if card.select_one('.typography_heading-xxs__QKBS8') else None
        how_many_reviews = re.sub(r'\s*reviews?', '', card.select_one('.typography_body-m__xgxZ_').text.strip()) if card.select_one('.typography_body-m__xgxZ_') else None
        location = card.select_one('.typography_body-m__xgxZ_.typography_appearance-subtle__8_H2l span').text.strip() if card.select_one('.typography_body-m__xgxZ_.typography_appearance-subtle__8_H2l span') else None
        date = card.select_one('.typography_body-m__xgxZ_ time').text.strip() if card.select_one('.typography_body-m__xgxZ_ time') else None
        rating = card.select_one('.star-rating_starRating__4rrcf img[alt]')['alt'].strip() if card.select_one('.star-rating_starRating__4rrcf img[alt]') else None
        rating_title = card.select_one('.typography_heading-s__f7029').text.strip() if card.select_one('.typography_heading-s__f7029') else None
        rating_description = card.select_one('.typography_body-l__KUYFJ').text.strip() if card.select_one('.typography_body-l__KUYFJ') else None
        date_of_experience = card.select_one('.typography_body-m__xgxZ_ .typography_weight-heavy__E1LTj + span').text.strip() if card.select_one('.typography_body-m__xgxZ_ .typography_weight-heavy__E1LTj + span') else None

        reviews.append({
            'username': username,
            'how_many_reviews': how_many_reviews,
            'location': location,
            'date': date,
            'rating': rating,
            'rating_title': rating_title,
            'rating_description': rating_description,
            'date_of_experience': date_of_experience
        })

    return reviews

# Function to scrape multiple pages
def scrape_all_pages(base_url, num_pages):
    all_reviews = []

    for page_num in range(1, num_pages + 1):
        page_url = f"{base_url}?page={page_num}"
        print(f"Scraping page {page_num}: {page_url}")
        reviews = scrape_page(page_url)
        all_reviews.extend(reviews)

    return all_reviews

# URL and number of pages to scrape
base_url = "https://www.trustpilot.com/review/www.cj.com"
num_pages = 9

# Scrape all pages
all_reviews = scrape_all_pages(base_url, num_pages)

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Generate filename with current date
current_date = datetime.now().strftime('%Y-%m-%d')
filename = f'trustpilot_reviews_{current_date}.csv'

# Create full path by joining script directory and filename
filepath = os.path.join(script_dir, filename)

# Write the results to a CSV file
with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['username', 'how_many_reviews', 'location', 'date', 'rating', 'rating_title', 'rating_description', 'date_of_experience']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for review in all_reviews:
        writer.writerow(review)

print(f"Scraping completed and data saved to {filepath}")

