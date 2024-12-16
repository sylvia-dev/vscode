"""
Dec 2 2024 - not getting all the results for the dates... use other script

TRUSTPILOT REVIEW SCRAPER
-------------------------

This script scrapes reviews from Trustpilot within a specified date range.

DATE RANGE CONFIGURATION:
------------------------
To set a date range, modify these lines in the main() function:

    start_date = datetime.strptime('2024-01-01', '%Y-%m-%d')  # Start date
    end_date = datetime.now()                                 # End date (current date)

OPTIONS:
1. To scrape ALL reviews (no start date):
   - Comment out or remove the start_date check in the scrape_page() function
   - Look for the line: if review_date < start_date:

2. To scrape from a specific start date:
   - Use format: 'YYYY-MM-DD'
   - Example: '2024-01-01' for January 1st, 2024

3. To set a specific end date instead of current date:
   - Replace datetime.now() with:
   - datetime.strptime('YYYY-MM-DD', '%Y-%m-%d')
   - Example: datetime.strptime('2024-03-01', '%Y-%m-%d')

EXAMPLE CONFIGURATIONS:
----------------------
# Scrape all reviews:
    Comment out these lines in scrape_page():
    # if review_date < start_date:
    #     should_continue = False
    #     break

# Scrape from specific date:
    start_date = datetime.strptime('2024-01-01', '%Y-%m-%d')
    end_date = datetime.now()

# Scrape specific date range:
    start_date = datetime.strptime('2024-01-01', '%Y-%m-%d')
    end_date = datetime.strptime('2024-03-01', '%Y-%m-%d')

OUTPUT:
-------
The script creates a CSV file with the following naming convention:
- With date range: trustpilot_reviews_[start_date]_to_[end_date].csv
- Without date range: trustpilot_reviews_[end_date].csv
"""


import requests
from bs4 import BeautifulSoup
import csv
import re
from datetime import datetime
import os

def parse_date(date_str):
    """Convert Trustpilot date format to datetime object"""
    try:
        # Handle different date formats
        if 'hours ago' in date_str or 'minutes ago' in date_str:
            return datetime.now()
        elif 'day ago' in date_str or 'days ago' in date_str:
            days = int(re.search(r'(\d+)', date_str).group(1))
            return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            # Parse standard date format
            return datetime.strptime(date_str, '%b %d, %Y')
    except Exception as e:
        print(f"Error parsing date: {date_str}")
        return None

def scrape_all_pages(base_url, start_date, end_date):
    all_reviews = []
    total_pages = 9  # Set fixed number of pages
    
    for page_num in range(1, total_pages + 1):
        page_url = f"{base_url}?page={page_num}&sort=recency"
        print(f"Scraping page {page_num} of {total_pages}: {page_url}")
        
        page_reviews = scrape_page(page_url, start_date, end_date)
        print(f"Found {len(page_reviews)} reviews within date range on page {page_num}")
        all_reviews.extend(page_reviews)
        print(f"Total reviews collected so far: {len(all_reviews)}")
        
    return all_reviews

def scrape_page(page_url, start_date, end_date):
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    reviews = []
    review_cards = soup.find_all('div', class_='styles_cardWrapper__LcCPA')
    print(f"Found {len(review_cards)} total reviews on this page")
    
    for card in review_cards:
        date_str = card.select_one('.typography_body-m__xgxZ_ time').text.strip() if card.select_one('.typography_body-m__xgxZ_ time') else None
        print(f"Processing review with date: {date_str}")
        review_date = parse_date(date_str) if date_str else None
        
        # Skip if date parsing failed
        if not review_date:
            continue
            
        # Apply date filtering
        if review_date < start_date or review_date > end_date:
            print(f"Skipping review from {date_str} - outside date range")
            continue

        username = card.select_one('.typography_heading-xxs__QKBS8').text.strip() if card.select_one('.typography_heading-xxs__QKBS8') else None
        how_many_reviews = re.sub(r'\s*reviews?', '', card.select_one('.typography_body-m__xgxZ_').text.strip()) if card.select_one('.typography_body-m__xgxZ_') else None
        location = card.select_one('.typography_body-m__xgxZ_.typography_appearance-subtle__8_H2l span').text.strip() if card.select_one('.typography_body-m__xgxZ_.typography_appearance-subtle__8_H2l span') else None
        rating = card.select_one('.star-rating_starRating__4rrcf img[alt]')['alt'].strip() if card.select_one('.star-rating_starRating__4rrcf img[alt]') else None
        rating_title = card.select_one('.typography_heading-s__f7029').text.strip() if card.select_one('.typography_heading-s__f7029') else None
        rating_description = card.select_one('.typography_body-l__KUYFJ').text.strip() if card.select_one('.typography_body-l__KUYFJ') else None
        date_of_experience = card.select_one('.typography_body-m__xgxZ_ .typography_weight-heavy__E1LTj + span').text.strip() if card.select_one('.typography_body-m__xgxZ_ .typography_weight-heavy__E1LTj + span') else None

        reviews.append({
            'username': username,
            'how_many_reviews': how_many_reviews,
            'location': location,
            'date': date_str,
            'rating': rating,
            'rating_title': rating_title,
            'rating_description': rating_description,
            'date_of_experience': date_of_experience,
            'parsed_date': review_date
        })

    return reviews

def main():
    # URL to scrape
    base_url = "https://www.trustpilot.com/review/www.cj.com"
    
    # Define date range (format: YYYY-MM-DD)
    # To change the start date, modify the date string '2024-01-01' 
    # To remove start date, comment out start date line
    start_date = datetime.strptime('2024-11-22', '%Y-%m-%d')
    end_date = datetime.now()
    
    # Scrape reviews within date range
    all_reviews = scrape_all_pages(base_url, start_date, end_date)
    
    # Sort reviews by date to find actual date range
    if all_reviews:
        # Sort reviews by parsed_date
        sorted_reviews = sorted(all_reviews, key=lambda x: x['parsed_date'])
        actual_start_date = sorted_reviews[0]['parsed_date']
        actual_end_date = sorted_reviews[-1]['parsed_date']
        
        # Generate filename with actual date range
        filename = f'trustpilot_reviews_{actual_start_date.strftime("%Y%m%d")}_to_{actual_end_date.strftime("%Y%m%d")}.csv'
    else:
        # Fallback if no reviews found
        filename = f'trustpilot_reviews_no_results_{datetime.now().strftime("%Y%m%d")}.csv'
    
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    
    # Write results to CSV (excluding the parsed_date field)
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['username', 'how_many_reviews', 'location', 'date', 'rating', 'rating_title', 'rating_description', 'date_of_experience']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for review in all_reviews:
            # Create a copy of the review dict without the parsed_date field
            review_data = {k: v for k, v in review.items() if k != 'parsed_date'}
            writer.writerow(review_data)
    
    print(f"Scraping completed. Found {len(all_reviews)} reviews.")
    if all_reviews:
        print(f"Date range of scraped reviews: {actual_start_date.strftime('%Y-%m-%d')} to {actual_end_date.strftime('%Y-%m-%d')}")
    print(f"Data saved to {filepath}")

if __name__ == "__main__":
    main()