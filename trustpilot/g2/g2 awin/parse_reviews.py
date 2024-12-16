import csv
from bs4 import BeautifulSoup
import os
import re

def categorize_business_size(size_text):
    if not size_text:
        return None
    if "50 or fewer" in size_text or "Small-Business" in size_text:
        return "Small Business (50 or fewer emp.)"
    elif "51-1000" in size_text or "Mid-Market" in size_text:
        return "Mid-Market (51-1000 emp.)"
    elif "1000" in size_text or "Enterprise" in size_text:
        return "Enterprise (>1000 emp.)"
    return None

def clean_title(title):
    # Remove any business size information from the title
    clean = re.sub(r'\(.*?emp\.?\)', '', title).strip()
    clean = re.sub(r'Small-Business|Mid-Market|Enterprise', '', clean).strip()
    return clean

def parse_html_to_csv(html_file_path, writer):
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    
    review_cards = soup.find_all('div', attrs={'data-track-in-viewport-options': True})

    print(f"Found {len(review_cards)} review cards in {html_file_path}")

    for index, card in enumerate(review_cards, 1):
        review_data = {field: None for field in fieldnames}

        try:
            # Extract user information
            user_info = card.select_one('.inline-block .flex.ai-c')
            if user_info:
                name_element = user_info.select_one('a.link--header-color') or user_info.find(string=lambda text: isinstance(text, str) and text.strip(), recursive=False)
                review_data['username'] = name_element.text.strip() if name_element else None

            # Extract title and business size information
            user_details = card.select('.c-midnight-80.line-height-h6.fw-regular .mt-4th')
            if user_details:
                full_title = ' '.join(detail.text.strip() for detail in user_details)
                review_data['title'] = clean_title(full_title)
            
            # Extract business size
            business_size_element = card.select_one('.c-midnight-80.line-height-h6.fw-regular')
            if business_size_element:
                business_size_text = business_size_element.text
                review_data['business_size'] = categorize_business_size(business_size_text)

            # Extract tags
            review_data['validated_user'] = 'Yes' if card.select_one('div[alt="Validated G2.com Reviewer"]') else 'No'
            review_data['verified_current_user'] = 'Yes' if card.select_one('div[alt="Validated G2.com Screenshot"]') else 'No'
            review_source = card.select_one('.tag:-soup-contains("Review source")')
            review_data['review_source'] = review_source.text.split(': ')[-1] if review_source else None

            # Extract date
            date_element = card.select_one('.x-current-review-date time')
            review_data['date'] = date_element['datetime'] if date_element else None

            # Extract rating
            stars_div = card.select_one('.stars')
            if stars_div:
                star_class = [cls for cls in stars_div['class'] if cls.startswith('stars-')][0]
                review_data['rating'] = int(star_class.split('-')[-1]) / 2

            # Extract review title and content sections
            review_title = card.select_one('.l2[itemprop="name"]')
            review_data['review_title'] = review_title.text.strip() if review_title else None

            like_best = card.select_one('div:-soup-contains("What do you like best") ~ div p.formatted-text')
            review_data['like_best'] = like_best.text.strip() if like_best else None

            dislike = card.select_one('div:-soup-contains("What do you dislike") ~ div p.formatted-text')
            review_data['dislike'] = dislike.text.strip() if dislike else None

            benefits = card.select_one('div:-soup-contains("What problems is G2 solving") ~ div p.formatted-text')
            review_data['benefits'] = benefits.text.strip() if benefits else None

            writer.writerow(review_data)
        except Exception as e:
            print(f"Error processing review {index} in {html_file_path}: {str(e)}")

# Directory containing the HTML files
directory = '/Users/sylking/Documents/VCode/trustpilot/g2 awin/'

# Output CSV file path
csv_file_path = os.path.join(directory, 'g2_reviews_combined.csv')

fieldnames = [
    'username', 'title', 'business_size', 'validated_user', 
    'verified_current_user', 'review_source', 'date', 
    'rating', 'review_title', 'like_best', 'dislike', 'benefits'
]

total_reviews = 0

with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Iterate through all text files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            html_file_path = os.path.join(directory, filename)
            print(f"\nProcessing file: {filename}")
            parse_html_to_csv(html_file_path, writer)
            
            # Count the number of reviews in this file
            with open(html_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                soup = BeautifulSoup(content, 'html.parser')
                reviews_count = len(soup.find_all('div', attrs={'data-track-in-viewport-options': True}))
                total_reviews += reviews_count
                print(f"Reviews found in {filename}: {reviews_count}")

print(f"\nTotal reviews processed: {total_reviews}")
print(f"CSV file has been created at {csv_file_path}")