
google_scraper_reviews_final.py"

# Google Scraper Documentation

## Overview of Different Scrapers

1. **google_scraper_reviews_final.py**
   - Basic review scraper
   - Focuses on ratings and review information
   - Output: `affiliate_network_reviews_YYYY-MM-DD.csv`
   - Core fields: position, review site, ratings, review counts, snippets

2. **google_scraper_companyinfo_final2.py**
   - Company information scraper
   - Focuses on additional search data
   - Output: `affiliate_network_companyinfo2.csv`
   - Core fields: videos, discussions, people also ask/search, sponsored content

3. **google_scraper_complete.py**
   - Combined comprehensive scraper
   - Includes all features from both scrapers above
   - Output: `affiliate_network_complete_YYYY-MM-DD.csv`
   - All fields from both scrapers combined

## Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

## Required Python Packages
```bash
pip install requests beautifulsoup4
```

## Configuration
All scripts search for the following affiliate networks:
- CJ (Commission Junction)
- ShareASale
- ClickBank
- Impact
- AWIN
- Rakuten Advertising
- Partnerize

Search terms used:
- "reviews"
- "ratings"
- " " (blank search)

## Data Fields by Scraper

### google_scraper_reviews_final.py
- position
- company
- search_term
- review_site
- title
- link
- snippet
- rating
- rating_threshold
- reviews
- rating2

### google_scraper_companyinfo_final2.py
- company
- search_term
- url
- people_also_search
- people_also_search_companies
- videos (title, channel, duration, date)
- people_also_ask
- discussions_forums (title, name, date)
- sponsored_info (company, url, title)

### google_scraper_complete.py
All fields from both scrapers above, plus:
- Combined review and company information
- Enhanced video tracking
- Full discussion forum details
- Complete sponsored content information

## Running the Scripts

### Basic Review Scraper
```bash
/usr/bin/python3 "/Users/sylking/Documents/VCode/trustpilot/google first page results/google_scraper_reviews_final.py"
```

### Company Info Scraper
```bash
/usr/bin/python3 "/Users/sylking/Documents/VCode/trustpilot/google first page results/google_scraper_companyinfo_final2.py"
```

### Complete Scraper
```bash
/usr/bin/python3 "/Users/sylking/Documents/VCode/trustpilot/google first page results/google_scraper_complete.py"
```

## Output Files

### Review Scraper
- Creates: `affiliate_network_reviews_YYYY-MM-DD.csv`
- Focus: Review metrics and ratings

### Company Info Scraper
- Creates: `affiliate_network_companyinfo2.csv`
- Focus: Additional search information and company details

### Complete Scraper
- Creates: `affiliate_network_complete_YYYY-MM-DD.csv`
- Focus: All available data combined

## Rate Limiting and Safety Features
- Random delays (1-3 seconds) between requests
- SSL warning suppression
- Error handling for missing elements
- Continues to next item if a search fails

## Implementation Notes

### Error Handling
- All scripts ignore urllib3 warnings
- Graceful handling of missing data fields
- Continues processing if individual elements aren't found

### Data Processing
- Reviews script: Focuses on numerical data extraction
- Company info script: Handles complex nested data
- Complete script: Combines both with enhanced structure

### Best Practices
- Consider implementing proxy rotation for production use
- Monitor Google's robots.txt and terms of service
- Adjust delay times based on your needs
- Back up data regularly

## Common Issues and Solutions

1. SSL Warnings
   - Handled automatically in the latest versions
   - Can be suppressed using provided warning filters

2. Rate Limiting
   - Adjust `time.sleep()` values if needed
   - Consider implementing proxy rotation

3. Missing Data
   - Scripts handle missing elements gracefully
   - Check CSV output for completeness

## Notes
- Google may block requests if too many are made in a short time
- Consider implementing a proxy solution for production use
- Results may vary based on Google's search algorithm updates
- Always respect robots.txt and terms of service

## Future Improvements
- Add proxy support
- Implement concurrent requests
- Add data validation
- Enhanced error reporting
- Support for additional search engines

