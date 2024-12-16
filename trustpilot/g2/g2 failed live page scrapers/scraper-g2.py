import requests
from bs4 import BeautifulSoup
import csv

# Function to scrape a single review page
def scrape_page(page_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(page_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    reviews = []

    # Find all review cards on the page
    review_cards = soup.find_all('div', class_='x-track-in-viewport-initialized')

    if not review_cards:
        print("No review cards found. Check if the selector is correct.")

    for card in review_cards:
        # Extracting each element using the CSS selectors and printing for verification
        username = card.select_one('.inline-block .flex.ai-c[itemprop="author"]')
        user_title = card.select_one('.c-midnight-80.line-height-h6.fw-regular div.mt-4th:first-child')
        user_business = card.select_one('.c-midnight-80.line-height-h6.fw-regular div.mt-4th:last-child')
        validated_user = card.select_one('.tags--teal div[alt="Validated CJ Affiliate Reviewer"]')
        verified_current_user = card.select_one('.tags--teal div[alt="Verified Current User"]')
        review_source = card.select_one('.tags--teal div[data-tooltip="id2dia-tooltip"]')
        incentivized_review = card.select_one('.tags--teal div[data-tooltip="hkte5a-tooltip"]')
        date = card.select_one('.x-current-review-date time')

        # Print the extracted elements to debug
        print(f"Username: {username.text.strip() if username else 'None'}")
        print(f"User Title: {user_title.text.strip() if user_title else 'None'}")
        print(f"User Business: {user_business.text.strip() if user_business else 'None'}")
        print(f"Validated User: {validated_user.text.strip() if validated_user else 'None'}")
        print(f"Verified Current User: {verified_current_user.text.strip() if verified_current_user else 'None'}")
        print(f"Review Source: {review_source.text.strip() if review_source else 'None'}")
        print(f"Incentivized Review: {incentivized_review.text.strip() if incentivized_review else 'None'}")
        print(f"Date: {date.text.strip() if date else 'None'}")

        reviews.append({
            'username': username.text.strip() if username else None,
            'user_title': user_title.text.strip() if user_title else None,
            'user_business': user_business.text.strip() if user_business else None,
            'validated_user': validated_user.text.strip() if validated_user else None,
            'verified_current_user': verified_current_user.text.strip() if verified_current_user else None,
            'review_source': review_source.text.strip() if review_source else None,
            'incentivized_review': incentivized_review.text.strip() if incentivized_review else None,
            'date': date.text.strip() if date else None
        })

    return reviews

# Function to scrape a single page
def scrape_single_page(base_url):
    all_reviews = scrape_page(base_url)
    return all_reviews

# URL to scrape
base_url = "https://www.g2.com/products/cj-affiliate/reviews"

# Scrape the page
all_reviews = scrape_single_page(base_url)

# Write the results to a CSV file
with open('g2_reviews.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['username', 'user_title', 'user_business', 'validated_user', 'verified_current_user', 'review_source', 'incentivized_review', 'date']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for review in all_reviews:
        writer.writerow(review)

print("Scraping completed and data saved to g2_reviews.csv")
