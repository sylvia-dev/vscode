from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
chrome_options.add_argument("accept-language=en-US,en;q=0.9")

# Use these options when initializing the driver
driver = webdriver.Chrome(options=chrome_options)

# Function to scrape a single review page
def scrape_page(page_url):
    driver.get(page_url)

    try:
        # Wait for the reviews to load by waiting for a specific element to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.x-track-in-viewport-initialized'))
        )

        # Once the page is fully loaded, get the page source and parse it
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        reviews = []

        # Find all review cards on the page
        review_cards = soup.find_all('div', class_='x-track-in-viewport-initialized')

        if not review_cards:
            print("No review cards found. Check if the selector is correct.")
            return []

        for card in review_cards:
            username = card.select_one('.inline-block .flex.ai-c[itemprop="author"]')
            username = username.text.strip() if username else None
            
            user_title = card.select_one('.c-midnight-80.line-height-h6.fw-regular div.mt-4th:first-child')
            user_title = user_title.text.strip() if user_title else None
            
            user_business = card.select_one('.c-midnight-80.line-height-h6.fw-regular div.mt-4th:last-child')
            user_business = user_business.text.strip() if user_business else None
            
            validated_user = card.select_one('.tags--teal div[alt="Validated CJ Affiliate Reviewer"]')
            validated_user = validated_user.text.strip() if validated_user else None
            
            verified_current_user = card.select_one('.tags--teal div[alt="Verified Current User"]')
            verified_current_user = verified_current_user.text.strip() if verified_current_user else None
            
            review_source = card.select_one('.tags--teal div[data-tooltip="id2dia-tooltip"]')
            review_source = review_source.text.strip() if review_source else None
            
            incentivized_review = card.select_one('.tags--teal div[data-tooltip="hkte5a-tooltip"]')
            incentivized_review = incentivized_review.text.strip() if incentivized_review else None
            
            date = card.select_one('.x-current-review-date time')
            date = date.text.strip() if date else None

            reviews.append({
                'username': username,
                'user_title': user_title,
                'user_business': user_business,
                'validated_user': validated_user,
                'verified_current_user': verified_current_user,
                'review_source': review_source,
                'incentivized_review': incentivized_review,
                'date': date
            })

        return reviews

    except Exception as e:
        print(f"Error while scraping: {e}")
        return []

# URL to scrape
base_url = "https://www.g2.com/products/cj-affiliate/reviews"

# Scrape the page
all_reviews = scrape_page(base_url)

# Write the results to a CSV file
with open('g2_reviews.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['username', 'user_title', 'user_business', 'validated_user', 'verified_current_user', 'review_source', 'incentivized_review', 'date']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for review in all_reviews:
        writer.writerow(review)

print(f"Scraping completed. {len(all_reviews)} reviews saved to g2_reviews.csv")

# Close the WebDriver
driver.quit()