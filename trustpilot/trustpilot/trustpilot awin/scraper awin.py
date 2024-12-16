import requests
from bs4 import BeautifulSoup
import csv
import re
import os

def scrape_page(page_url):
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    reviews = []
    
    review_cards = soup.find_all('div', class_='styles_cardWrapper__LcCPA')

    for card in review_cards:
        username = card.select_one('.typography_heading-xxs__QKBS8').text.strip() if card.select_one('.typography_heading-xxs__QKBS8') else None
        how_many_reviews = re.sub(r'\s*reviews?', '', card.select_one('.typography_body-m__xgxZ_').text.strip()) if card.select_one('.typography_body-m__xgxZ_') else None
        location = card.select_one('.typography_body-m__xgxZ_.typography_appearance-subtle__8_H2l span').text.strip() if card.select_one('.typography_body-m__xgxZ_.typography_appearance-subtle__8_H2l span') else None
        date = card.select_one('.typography_body-m__xgxZ_ time').text.strip() if card.select_one('.typography_body-m__xgxZ_ time') else None
        rating = card.select_one('.star-rating_starRating__4rrcf img[alt]')['alt'].strip() if card.select_one('.star-rating_starRating__4rrcf img[alt]') else None
        rating_title = card.select_one('.typography_heading-s__f7029').text.strip() if card.select_one('.typography_heading-s__f7029') else None
        rating_description = card.select_one('.typography_body-l__KUYFJ').text.strip() if card.select_one('.typography_body-l__KUYFJ') else None
        
        # Updated selector for date of experience
        date_of_experience_elem = card.select_one('p[data-service-review-date-of-experience-typography="true"]')
        date_of_experience = date_of_experience_elem.contents[-1].strip() if date_of_experience_elem else None

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

def scrape_all_pages(base_url, num_pages):
    all_reviews = []
    total_reviews = 0

    for page_num in range(1, num_pages + 1):
        page_url = f"{base_url}?page={page_num}"
        print(f"Scraping page {page_num}: {page_url}")
        reviews = scrape_page(page_url)
        all_reviews.extend(reviews)
        
        print(f"Found {len(reviews)} reviews on page {page_num}")
        total_reviews += len(reviews)

    print(f"Total reviews scraped: {total_reviews}")
    return all_reviews

script_dir = '/Users/sylking/Documents/VCode/trustpilot/trustpilot awin'
output_csv = os.path.join(script_dir, 'trustpilot_reviews_awin.csv')
base_url = "https://www.trustpilot.com/review/awin.com"
num_pages = 29

all_reviews = scrape_all_pages(base_url, num_pages)

with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['username', 'how_many_reviews', 'location', 'date', 'rating', 'rating_title', 'rating_description', 'date_of_experience']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for review in all_reviews:
        writer.writerow(review)

print(f"Scraping completed and data saved to {output_csv}")
print(f"Total reviews in CSV: {len(all_reviews)}")