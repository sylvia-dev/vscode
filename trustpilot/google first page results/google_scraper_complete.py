import warnings
import urllib3
from urllib.parse import urlparse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import csv
import time
import random
import re
import os
from datetime import datetime

# Suppress the specific NotOpenSSLWarning
warnings.filterwarnings('ignore', category=urllib3.exceptions.NotOpenSSLWarning)

def create_session():
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def get_google_search_results(query):
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    if not is_valid_url(url):
        raise ValueError("Invalid URL generated")
        
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    session = create_session()
    try:
        response = session.get(url, headers=headers, verify=True, timeout=30)
        response.raise_for_status()
        return response.text, url
    except requests.exceptions.RequestException as e:
        print(f"Error fetching search results: {e}")
        raise
    finally:
        session.close()

def parse_search_results(html_content, company, search_term, url):
    soup = BeautifulSoup(html_content, 'html.parser')
    results = []
    position = 1

    # Regular search results with review information
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
                'url': url,
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

    # People also ask
    people_also_ask = []
    paa_section = soup.select('.wQiwMc.related-question-pair')
    for item in paa_section:
        question = item.select_one('.CSkcDe')
        if question:
            people_also_ask.append(question.text.strip())
    
    # Ensure we get up to 4 results
    people_also_ask = people_also_ask[:4]

    # Discussions and forums
    discussions_forums = []
    df_section = soup.select('.LJ7wUe.sjVJQd.NzpZMe')
    for item in df_section:
        title_elem = item.select_one('.zNWc4c .r0uZsf')
        name_elem = item.select_one('.R8BTeb.q8U8x.LJEGod')
        date_elem = item.select_one('.xuPcX.yUTMj.OSrXXb.al4kQ')
        
        if title_elem and name_elem and date_elem:
            discussions_forums.append({
                'title': title_elem.text.strip(),
                'name': name_elem.text.strip().replace('\xa0· \xa0', ''),
                'date': date_elem.text.strip()
            })

    # Sponsored information
    sponsored_info = []
    sponsored_section = soup.select('.vdQmEd.fP1Qef.xpd.EtOod.pkphOe')
    for item in sponsored_section:
        company_elem = item.select_one('.pKWwCd.yUTMj .OSrXXb')
        url_elem = item.select_one('.sVXRqc')
        title_elem = item.select_one('.CCgQ5.vCa9Yd.QfkTvb.N8QANc.Va3FIb.EE3Upf')
        
        if company_elem and url_elem and title_elem:
            sponsored_info.append({
                'company': company_elem.text.strip(),
                'url': url_elem.get('href', ''),
                'title': title_elem.text.strip()
            })

    # Add additional data to each result
    for result in results:
        result['people_also_search'] = people_also_search
        result['people_also_search_companies'] = people_also_search_companies
        result['videos'] = videos
        result['people_also_ask'] = people_also_ask
        result['discussions_forums'] = discussions_forums
        result['sponsored_info'] = sponsored_info

    return results

def save_to_csv(results, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'position', 'company', 'search_term', 'url', 'review_site', 'title', 
            'link', 'snippet', 'rating', 'rating_threshold', 'reviews', 'rating2',
            'people_also_search', 'people_also_search_companies',
            'videos', 'people_also_ask',
            'discussions_forums_title', 'discussions_forums_name', 'discussions_forums_date',
            'sponsored_company', 'sponsored_url', 'sponsored_title'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            # Prepare the row data
            row = {
                'position': result['position'],
                'company': result['company'],
                'search_term': result['search_term'],
                'url': result['url'],
                'review_site': result['review_site'],
                'title': result['title'],
                'link': result['link'],
                'snippet': result['snippet'],
                'rating': result['rating'],
                'rating_threshold': result['rating_threshold'],
                'reviews': result['reviews'],
                'rating2': result['rating2'],
                'people_also_search': ', '.join(result['people_also_search']),
                'people_also_search_companies': ', '.join(result['people_also_search_companies']),
                'videos': ', '.join([f"{v['title']} ({v['channel']}, {v['duration']}, {v['date']})" for v in result['videos']]),
                'people_also_ask': ', '.join(result['people_also_ask']),
                'discussions_forums_title': result['discussions_forums'][0]['title'] if result['discussions_forums'] else '',
                'discussions_forums_name': result['discussions_forums'][0]['name'] if result['discussions_forums'] else '',
                'discussions_forums_date': result['discussions_forums'][0]['date'] if result['discussions_forums'] else '',
                'sponsored_company': result['sponsored_info'][0]['company'] if result['sponsored_info'] else '',
                'sponsored_url': result['sponsored_info'][0]['url'] if result['sponsored_info'] else '',
                'sponsored_title': result['sponsored_info'][0]['title'] if result['sponsored_info'] else ''
            }
            writer.writerow(row)

def main():
    companies = ["cj", "cj affiliate", "ShareASale", "ClickBank", "Impact", "Impact Radius", "AWIN",
        "Rakuten Advertising", "Partnerize"]
    search_terms = ["reviews", "ratings", " "]
    
    all_results = []

    for company in companies:
        for search_term in search_terms:
            query = f"{company} {search_term}"
            html_content, url = get_google_search_results(query)
            
            results = parse_search_results(html_content, company, search_term, url)
            all_results.extend(results)
            
            time.sleep(random.uniform(1, 3))  # Add a random delay between requests

    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create filename with current date
    current_date = datetime.now().strftime('%Y-%m-%d')
    filename = f'affiliate_network_complete_{current_date}.csv'
    
    # Create the full path for the CSV file
    csv_path = os.path.join(script_dir, filename)
    
    save_to_csv(all_results, csv_path)

if __name__ == "__main__":
    main()