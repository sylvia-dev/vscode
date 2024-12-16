import csv
import os
import random
import sys
import platform

def print_environment_info():
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Operating System: {platform.system()} {platform.release()}")
    print(f"Current working directory: {os.getcwd()}")

# List of all competitors
competitors = [
    "cj", "cj affiliate", "ShareASale", "ClickBank", "Impact", "AWIN",
    "Rakuten Advertising", "Partnerize"
]

# List of review sites
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

def generate_random_review():
    """Generate a random rating and vote count."""
    rating = f"{random.randint(1, 5)}/5"
    votes = random.randint(1, 1000)
    return rating, votes

def main():
    print_environment_info()

    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create CSV file in the same directory as the script
    csv_path = os.path.join(script_dir, 'competitor_ratings.csv')
    
    print(f"Attempting to create CSV file at: {csv_path}")

    try:
        with open(csv_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Competitor', 'Review Site', 'Rating', 'Votes'])

            # Iterate through competitors and review sites
            for competitor in competitors:
                for site in review_sites:
                    rating, votes = generate_random_review()
                    writer.writerow([competitor, site, rating, votes])
                    print(f"Generated data for {competitor} on {site}: Rating: {rating}, Votes: {votes}")

        print(f"CSV file created successfully at: {csv_path}")
    except Exception as e:
        print(f"An error occurred while creating the CSV file: {str(e)}")

    print("Script execution completed.")

if __name__ == "__main__":
    main()