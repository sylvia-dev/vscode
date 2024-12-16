import csv
import os
import sys

def print_debug_info():
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script location: {__file__}")

# This dictionary will store the manually collected data
# Format: {(competitor, site): (rating, threshold, votes)}
COLLECTED_DATA = {
    ("cj", "www.trustradius.com"): (5, 10, 7)
}

def get_review_data(competitor, site):
    """
    Get collected review data if available, otherwise return None values.
    """
    return COLLECTED_DATA.get((competitor, site), (None, None, None))

def generate_reviews_to_csv(csv_file_path):
    print(f"Attempting to create CSV file at: {csv_file_path}")
    
    competitors = [
        "cj", "cj affiliate", "ShareASale", "ClickBank", "Impact", "AWIN",
        "Rakuten Advertising", "Partnerize"
    ]

    review_sites = [
        "www.trustpilot.com", "www.reddit.com", "www.authorityhacker.com", "www.g2.com",
        "www.trustradius.com", "www.gartner.com", "www.sitejabber.com", "www.affpaying.com",
        "www.weberlo.com", "medium.com", "www.linkedin.com", "www.traderscooter.com",
        "smartblogger.com", "www.clickbank.com", "www.consumeraffairs.com", "www.capterra.com",
        "www.crazyegg.com", "www.iaea.org", "apps.shopify.com", "www.glassdoor.com",
        "www.imdb.com", "www.getapp.com", "www.youtube.com", "afluencer.com",
        "www.yelp.com", "www.quora.com", "craigcampbellseo.com", "www.growann.com",
        "www.cuspera.com", "www.influencer-hero.com", "go.partnerize.com"
    ]

    try:
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Competitor', 'Review Site', 'Rating', 'Rating Threshold', 'Votes']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for competitor in competitors:
                for site in review_sites:
                    rating, threshold, votes = get_review_data(competitor, site)
                    writer.writerow({
                        'Competitor': competitor,
                        'Review Site': site,
                        'Rating': rating if rating is not None else '',
                        'Rating Threshold': threshold if threshold is not None else '',
                        'Votes': votes if votes is not None else ''
                    })
                    print(f"Data for {competitor} on {site}: Rating: {rating}/{threshold}, Votes: {votes}")

        print(f"CSV file has been created successfully at {csv_file_path}")
        print("Note: Empty fields indicate no data available.")
    except Exception as e:
        print(f"An error occurred while creating the CSV file: {str(e)}")

if __name__ == "__main__":
    print_debug_info()
    csv_file_path = os.path.join(os.path.dirname(__file__), 'competitor_ratings.csv')
    generate_reviews_to_csv(csv_file_path)
    print("Script execution completed.")