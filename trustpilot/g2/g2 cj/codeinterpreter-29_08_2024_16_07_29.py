import csv
from bs4 import BeautifulSoup

def parse_html_to_csv(html_file_path, csv_file_path):
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    review_cards = soup.find_all('div', class_='x-track-in-viewport-initialized')

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'username', 'title', 'business_type', 'business_size', 'validated_user', 
            'verified_current_user', 'review_source', 'incentivized_review', 'date', 
            'rating', 'review_title', 'like_best', 'dislike', 'benefits'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

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
                business_info = user_details[1].text.strip().split('(')
                review_data['business_type'] = business_info[0].strip()
                review_data['business_size'] = f"({business_info[1]}" if len(business_info) > 1 else None
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

            like_best = card.select_one('div:contains("What do you like best") ~ div p.formatted-text')
            review_data['like_best'] = like_best.text.strip() if like_best else None

            dislike = card.select_one('div:contains("What do you dislike") ~ div p.formatted-text')
            review_data['dislike'] = dislike.text.strip() if dislike else None

            benefits = card.select_one('div:contains("What problems is CJ Affiliate solving") ~ div p.formatted-text')
            review_data['benefits'] = benefits.text.strip() if benefits else None

            writer.writerow(review_data)

    print(f"CSV file has been created at {csv_file_path}")

# Use the function
html_file_path = 'g2 html.txt'  # The downloaded HTML file
csv_file_path = 'g2_reviews.csv'  # The output CSV file

parse_html_to_csv(html_file_path, csv_file_path)
