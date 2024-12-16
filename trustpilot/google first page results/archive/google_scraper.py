import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import warnings
import re
import os
import urllib3

# Suppress the SSL warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")

def get_google_search_results(query):
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers, verify=False)  # Added verify=False to ignore SSL certificate
    return response.text

def parse_search_results(html_content, company, search_term):
    soup = BeautifulSoup(html_content, 'html.parser')
    results = []
    position = 1

    for result in soup.select('.g'):
        title_element = result.select_one('.LC20lb')
        link_element = result.select_one('.yuRUbf a')
        snippet_element = result.select_one('.VwiC3b')
        rating_element = result.select_one('.fG8Fp .ChPIuf')
        rating2_element = result.select_one('.fG8Fp .z3HNkc')
        review_site_element = result.select_one('.VuuXrf')

        if title_element and link_element:
            title = title_element.text.strip()
            link = link_element['href']
            snippet = snippet_element.text.strip() if snippet_element else ""
            review_site = review_site_element.text.strip() if review_site_element else ""
            
            rating = ""
            rating_threshold = ""
            reviews = ""
            rating2 = ""
            
            if rating_element:
                rating_text = rating_element.text
                rating_match = re.search(r'Rating: (\d+(?:\.\d+)?)', rating_text)
                if rating_match:
                    rating = rating_match.group(1)
                
                threshold_match = re.search(r'out of (\d+)', rating_text)
                if threshold_match:
                    rating_threshold = threshold_match.group(1).rstrip(',')
                
                reviews_match = re.search(r'(\d+) reviews', rating_text)
                if reviews_match:
                    reviews = reviews_match.group(1)

            if rating2_element:
                rating2 = rating2_element.get('aria-label', '').replace(',', '')

            results.append({
                'position': position,
                'company': company,
                'search_term': search_term,
                'review_site': review_site,
                'title': title,
                'link': link,
                'snippet': snippet,
                'rating': rating,
                'rating_threshold': rating_threshold,
                'reviews': reviews,
                'rating2': rating2
            })
            position += 1

    # Videos
    videos = []
    video_section = soup.select('.X4T0U')
    for video in video_section:
        title_elem = video.select_one('.y05Tsc')
        channel_elem = video.select_one('.Sg4azc')
        duration_elem = video.select_one('.c8rnLc')
        date_elem = video.select_one('.OwbDmd')
        link_elem = video.select_one('a.xMqpbd[href^="https://www.youtube.com/watch"]')
        
        if title_elem and channel_elem and duration_elem and date_elem and link_elem:
            title = title_elem.text.strip()
            channel = channel_elem.text.strip().split('·')[0].strip()
            duration = duration_elem.text.strip()
            date = date_elem.text.strip()
            link = link_elem['href']
            
            videos.append({
                'title': title,
                'channel': channel,
                'duration': duration,
                'date': date,
                'link': link
            })

    # People also search
    people_also_search = []
    pas_section = soup.select_one('.AJLUJb')
    if pas_section:
        pas_items = pas_section.select('.oatEtb')
        people_also_search = [item.text.strip() for item in pas_items if item.text.strip()]

    # People also search for companies
    people_also_search_companies = []
    pasc_elements = soup.select('.f3LoEf.OSrXXb')
    for elem in pasc_elements:
        company_name = elem.text.strip()
        if company_name:
            people_also_search_companies.append(company_name)

    print(f"People also search for companies: {people_also_search_companies}")

    # Check for alternative selectors
    alt_selectors = ['.oIk2Cb .f3LoEf', '.kfsfbe .f3LoEf', '.XRVJtc .f3LoEf']
    for selector in alt_selectors:
        alt_elements = soup.select(selector)
        print(f"Number of {selector} elements found: {len(alt_elements)}")
        for elem in alt_elements:
            print(f"Text content of {selector}: {elem.text.strip()}")

    # People also ask
    people_also_ask = []
    paa_section = soup.select('.wQiwMc.related-question-pair')
    for item in paa_section:
        question = item.select_one('.CSkcDe')
        if question:
            people_also_ask.append(question.text.strip())
            
    # Ensure we get up to 4 results
    people_also_ask = people_also_ask[:4]        

    return results, people_also_search, people_also_search_companies, videos, people_also_ask

def save_to_csv(results, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['position', 'company', 'search_term', 'review_site', 'title', 'link', 'snippet', 'rating', 'rating_threshold', 'reviews', 'rating2', 'people_also_search', 'people_also_search_companies', 'videos', 'people_also_ask']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)

def main():
    companies = ["cj"]
   # companies = ["cj", "cj affiliate", "ShareASale", "ClickBank", "Impact", "AWIN", "Rakuten Advertising", "Partnerize"]
   # search_terms = ["reviews", "ratings", "vs cj"]
    search_terms = ["reviews"]
    
    all_results = []
    all_people_also_search = set()
    all_people_also_search_companies = set()
    all_videos = []
    all_people_also_ask = set()

    for company in companies:
        for search_term in search_terms:
            query = f"{company} {search_term}"
            print(f"Searching for: {query}")
            html_content = get_google_search_results(query)
            
            results, pas, pasc, videos, paa = parse_search_results(html_content, company, search_term)
            
            all_results.extend(results)
            all_people_also_search.update(pas)
            all_people_also_search_companies.update(pasc)
            all_videos.extend(videos)
            all_people_also_ask.update(paa)
            
            print(f"People also search companies found in this query: {pasc}")
            
            time.sleep(random.uniform(1, 3))  # Add a random delay between requests

    print(f"All people also search companies: {all_people_also_search_companies}")

    # Add the additional data to each result
    for result in all_results:
        result['people_also_search'] = ', '.join(all_people_also_search)
        result['people_also_search_companies'] = ', '.join(all_people_also_search_companies)
        result['videos'] = ', '.join([f"{v['title']} ({v['channel']}, {v['duration']}, {v['date']})" for v in all_videos])
        result['people_also_ask'] = ', '.join(all_people_also_ask)

    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create the full path for the CSV file
    csv_path = os.path.join(script_dir, 'affiliate_network_reviews.csv')
    
    save_to_csv(all_results, csv_path)

if __name__ == "__main__":
    main()