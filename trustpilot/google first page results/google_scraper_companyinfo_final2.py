import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import warnings
import os

warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")

def get_google_search_results(query):
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    return response.text, url

def parse_search_results(html_content, company, search_term, url):
    soup = BeautifulSoup(html_content, 'html.parser')
    
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

    return {
        'company': company,
        'search_term': search_term,
        'url': url,
        'people_also_search': people_also_search,
        'people_also_search_companies': people_also_search_companies,
        'videos': videos,
        'people_also_ask': people_also_ask,
        'discussions_forums': discussions_forums,
        'sponsored_info': sponsored_info
    }

def save_to_csv(results, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['company', 'search_term', 'url', 'people_also_search', 'people_also_search_companies', 'videos', 
                      'people_also_ask', 'discussions_forums_title', 'discussions_forums_name', 'discussions_forums_date',
                      'sponsored_company', 'sponsored_url', 'sponsored_title']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            row = {
                'company': result['company'],
                'search_term': result['search_term'],
                'url': result['url'],
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
    companies = ["cj", "cj affiliate", "ShareASale", "ClickBank", "Impact", "AWIN",
        "Rakuten Advertising", "Partnerize" ]
    search_terms = ["reviews", "ratings", " "]
    
    all_results = []

    for company in companies:
        for search_term in search_terms:
            query = f"{company} {search_term}"
            html_content, url = get_google_search_results(query)
            
            result = parse_search_results(html_content, company, search_term, url)
            all_results.append(result)
            
            time.sleep(random.uniform(1, 3))  # Add a random delay between requests

    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create the full path for the CSV file
    csv_path = os.path.join(script_dir, 'affiliate_network_companyinfo2.csv')
    
    save_to_csv(all_results, csv_path)

if __name__ == "__main__":
    main()