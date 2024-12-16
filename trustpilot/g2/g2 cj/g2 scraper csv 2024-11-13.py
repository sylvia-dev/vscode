import csv
from bs4 import BeautifulSoup
from datetime import datetime
import os

def get_section_text(card, section_title):
    """Helper function to extract specific section text"""
    section = card.find('div', text=lambda t: t and section_title in t)
    if section:
        content_div = section.find_next('div')
        if content_div:
            formatted_text = content_div.find('p', class_='formatted-text')
            if formatted_text:
                return formatted_text.text.replace('Review collected by and hosted on G2.com.', '').strip()
    return None

def parse_html_to_csv(input_files, csv_file_path):
    # Get current date for filename
    current_date = datetime.now().strftime('%Y-%m-%d')
    base_name, ext = csv_file_path.rsplit('.', 1)
    csv_file_path = f"{base_name}_{current_date}.{ext}"

    # Set to store unique reviews
    seen_reviews = set()
    all_reviews = []

    fieldnames = [
        'username', 'title', 'business_type', 'business_size', 'validated_user', 
        'verified_current_user', 'review_source', 'incentivized_review', 'date', 
        'rating', 'review_title', 'like_best', 'dislike', 'benefits'
    ]

    # Process each input file
    for input_file in input_files:
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), input_file)
        print(f"Processing {input_file}...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()

            soup = BeautifulSoup(html_content, 'html.parser')
            review_cards = soup.find_all(['div', 'article'], class_=['paper paper--white paper--box mb-2 position-relative border-bottom', 'x-track-in-viewport-initialized'])
            
            for card in review_cards:
                review_data = {field: None for field in fieldnames}
                
                # Extract username
                user_name = card.select_one('.fw-semibold.mb-half.lh-100 a, .fw-semibold.mb-half.lh-100 div')
                if user_name:
                    review_data['username'] = user_name.text.strip()
                
                # Extract business info
                user_details = card.select('.c-midnight-80.line-height-h6.fw-regular .mt-4th')
                if user_details:
                    if len(user_details) > 0:
                        review_data['title'] = user_details[0].text.strip()
                    if len(user_details) > 1:
                        business_info = user_details[1].text.strip()
                        business_parts = business_info.split('(')
                        review_data['business_type'] = business_parts[0].strip()
                        if len(business_parts) > 1:
                            review_data['business_size'] = f"({business_parts[1].strip()}"

                # Extract validation tags
                review_data['validated_user'] = 'Yes' if card.select_one('.tag:-soup-contains("Validated Reviewer")') else 'No'
                review_data['verified_current_user'] = 'Yes' if card.select_one('.tag:-soup-contains("Verified Current User")') else 'No'
                
                # Extract review source and incentive info
                source_tag = card.select_one('.tag:-soup-contains("Review source:")')
                if source_tag:
                    review_data['review_source'] = source_tag.text.replace('Review source: ', '').strip()
                
                review_data['incentivized_review'] = 'Yes' if card.select_one('.tag:-soup-contains("Incentivized Review")') else 'No'

                # Extract date
                date_element = card.select_one('time[datetime]')
                if date_element:
                    review_data['date'] = date_element.get('datetime')

                # Extract rating
                stars_div = card.select_one('.stars')
                if stars_div:
                    star_classes = [cls for cls in stars_div['class'] if cls.startswith('stars-')]
                    if star_classes:
                        star_class = star_classes[0]
                        star_mapping = {
                            'stars-0': 0, 'stars-1': 0.5, 'stars-2': 1, 'stars-3': 1.5, 'stars-4': 2,
                            'stars-5': 2.5, 'stars-6': 3, 'stars-7': 3.5, 'stars-8': 4, 'stars-9': 4.5, 'stars-10': 5
                        }
                        review_data['rating'] = star_mapping.get(star_class)

                # Extract review title
                review_title = card.select_one('.m-0.l2, div[itemprop="name"]')
                if review_title:
                    review_data['review_title'] = review_title.text.strip().replace('"', '')

                # Extract review sections using the helper function
                review_data['like_best'] = get_section_text(card, "What do you like best")
                review_data['dislike'] = get_section_text(card, "What do you dislike")
                review_data['benefits'] = get_section_text(card, "What problems")

                # Create unique key for this review
                unique_key = (
                    review_data['username'],
                    review_data['date'],
                    review_data['review_title']
                )

                # Only add if we haven't seen this review before
                if unique_key not in seen_reviews:
                    seen_reviews.add(unique_key)
                    all_reviews.append(review_data)
            
            print(f"Completed processing {input_file}")
            
        except Exception as e:
            print(f"Error processing {input_file}: {str(e)}")
            continue

    # Write deduplicated reviews to CSV
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_reviews)

    print(f"CSV file has been created at {csv_file_path}")
    print(f"Total unique reviews: {len(all_reviews)}")

# Define input files
input_files = ["g2_1_20241113.txt", "g2_2_20241113.txt", "g2_3_20241113.txt"]

# Define output file
output_file = "cj_affiliate_reviews.csv"

# Get the current directory path
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_file_path = os.path.join(current_dir, output_file)

# Call the function
parse_html_to_csv(input_files, csv_file_path)