import csv
from bs4 import BeautifulSoup
import os

def parse_html_to_csv(html_file_path, writer):
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    review_cards = soup.find_all('div', class_='x-track-in-viewport-initialized')

    for card in review_cards:
        review_data = {field: None for field in fieldnames}

        # Extract user information
        user_info = card.select_one('.inline-block .flex.ai-c')
        if user_info:
            name_element = user_info.select_one('a.link--header-color') or user_info.find(string=lambda text: isinstance(text, str) and text.strip(), recursive=False)
            review_data['username'] = name_element.text.strip() if name_element else None
        else:
            review_data['username'] = None

        user_details = card.select('.c-midnight-80.line-height-h6.fw-regular .mt-4th')
        review_data['title'] = user_details[0].text.strip() if len(user_details) > 0 else None
        
        if len(user_details) > 1:
            business_info = user_details[1].text.strip()

            # Handle cases where business info is in the title field
            if 'employees' in business_info:
                review_data['title'], size_info = review_data['title'].split('(') if '(' in review_data['title'] else (review_data['title'], '')
                review_data['business_size'] = size_info.strip().replace(')', '')

            # Apply business size conversion logic
            size_options = {
                '1-10': '1-10 employees',
                '11-50': '11-50 employees',
                '51-200': '51-200 employees',
                '201-500': '201-500 employees',
                '501-1000': '501-1000 employees',
                '1001-5000': '1001-5000 employees',
                '5001-10000': '5001-10000 employees',
                '10001+': '10001+ employees'
            }
            for key, value in size_options.items():
                if key in business_info:
                    review_data['business_size'] = value

            review_data['business_type'] = business_info.split('(')[0].strip() if '(' in business_info else business_info.strip()
        else:
            review_data['business_type'] = None
            review_data['business_size'] = None

        # Extract tags
        review_data['validated_user'] = 'Yes' if card.select_one('.tags--teal div[alt="Validated CJ Affiliate Reviewer"]') else 'No'
        review_data['verified_current_user'] = 'Yes' if card.select_one('.tags--teal div[alt="Verified Current User"]') else 'No'
        review_source = card.select_one('.tags--teal div[data-tooltip="id2dia-tooltip"]')
        review_data['review_source'] = review_source.text.strip() if review_source else None
        review_data['incentivized_review'] = 'Yes' if card.select_one('.tags--teal div[data-tooltip="hkte5a-tooltip"]') else 'No'

        # Extract date
        date_element = card.select_one('.x-current-review-date time')
        review_data['date'] = date_element['datetime'] if date_element else None

        # Extract rating
        stars_div = card.select_one('.stars')
        if stars_div:
            star_class = [cls for cls in stars_div['class'] if cls.startswith('stars-')][0]
            star_mapping = {
                'stars-0': 0, 'stars-1': 0.5, 'stars-2': 1, 'stars-3': 1.5, 'stars-4': 2,
                'stars-5': 2.5, 'stars-6': 3, 'stars-7': 3.5, 'stars-8': 4, 'stars-9': 4.5, 'stars-10': 5
            }
            review_data['rating'] = star_mapping.get(star_class, None)

        # Extract review title and content sections
        review_title = card.select_one('.l2[itemprop="name"]')
        review_data['review_title'] = review_title.text.strip() if review_title else None

        like_best = card.select_one('div:-soup-contains("What do you like best") ~ div p.formatted-text')
        review_data['like_best'] = like_best.text.strip() if like_best else None

        dislike = card.select_one('div:-soup-contains("What do you dislike") ~ div p.formatted-text')
        review_data['dislike'] = dislike.text.strip() if dislike else None

        benefits = card.select_one('div:-soup-contains("What problems is CJ Affiliate solving") ~ div p.formatted-text')
        review_data['benefits'] = benefits.text.strip() if benefits else None

        writer.writerow(review_data)

# Directory containing the HTML files
directory = '/Users/sylking/Documents/VCode/trustpilot/g2 awin/'

# Output CSV file path
csv_file_path = os.path.join(directory, 'g2_awin_reviews_combined.csv')

fieldnames = [
    'username', 'title', 'business_type', 'business_size', 'validated_user', 
    'verified_current_user', 'review_source', 'incentivized_review', 'date', 
    'rating', 'review_title', 'like_best', 'dislike', 'benefits'
]

with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Iterate through all text files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            html_file_path = os.path.join(directory, filename)
            print(f"Processing file: {filename}")
            parse_html_to_csv(html_file_path, writer)

print(f"CSV file has been created at {csv_file_path}")