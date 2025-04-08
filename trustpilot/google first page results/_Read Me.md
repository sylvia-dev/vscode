# Google Scraper Documentation

## Overview
This collection of Python scripts scrapes Google search results for various affiliate networks, focusing on reviews, ratings, and company information. The scripts are designed to gather comprehensive data about affiliate networks' online presence and reputation.

## Available Scrapers

### 1. Basic Review Scraper (`google_scraper_reviews_final.py`)
- **Purpose**: Extracts basic review and rating information
- **Output File**: `affiliate_network_reviews_YYYY-MM-DD.csv`
- **Key Fields**:
  - Position in search results
  - Review site information
  - Ratings and review counts
  - Search result snippets

### 2. Company Information Scraper (`google_scraper_companyinfo_final2.py`)
- **Purpose**: Gathers additional company-related search data
- **Output File**: `affiliate_network_companyinfo2.csv`
- **Key Fields**:
  - Video content
  - Discussion forums
  - "People also ask" questions
  - Sponsored content

### 3. Complete Scraper (`google_scraper_complete.py`)
- **Purpose**: Comprehensive data collection combining all features
- **Output File**: `affiliate_network_complete_YYYY-MM-DD.csv`
- **Features**: All data from both basic and company information scrapers

## Setup and Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Required Packages
```bash
pip install requests beautifulsoup4
```

### Configuration
The scripts search for the following affiliate networks:
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

## Data Fields

### Review Scraper Fields
| Field | Description |
|-------|-------------|
| position | Search result position |
| company | Affiliate network name |
| search_term | Search query used |
| review_site | Source of the review |
| title | Search result title |
| link | URL of the result |
| snippet | Search result description |
| rating | Numerical rating |
| rating_threshold | Rating scale (e.g., out of 5) |
| reviews | Number of reviews |
| rating2 | Additional rating metric |

### Company Info Scraper Fields
| Field | Description |
|-------|-------------|
| people_also_search | Related search terms |
| people_also_search_companies | Related companies |
| videos | Video content details |
| people_also_ask | Related questions |
| discussions_forums | Forum discussions |
| sponsored_info | Sponsored content details |

## Usage

### Running the Scripts

1. **Basic Review Scraper**:
```bash
python "google_scraper_reviews_final.py"
```

2. **Company Info Scraper**:
```bash
python "google_scraper_companyinfo_final2.py"
```

3. **Complete Scraper**:
```bash
python "google_scraper_complete.py"
```

## Output Files

### File Naming Convention
- Review Scraper: `affiliate_network_reviews_YYYY-MM-DD.csv`
- Company Info: `affiliate_network_companyinfo2.csv`
- Complete Scraper: `affiliate_network_complete_YYYY-MM-DD.csv`

## Technical Details

### Rate Limiting
- Random delays (1-3 seconds) between requests
- Configurable through `time.sleep()` values

### Error Handling
- SSL warning suppression
- Graceful handling of missing elements
- Continues processing if individual elements fail

### Data Processing
- Reviews: Focuses on numerical data extraction
- Company info: Handles complex nested data
- Complete: Combines both with enhanced structure

## Best Practices

### Production Use
- Implement proxy rotation for large-scale scraping
- Monitor Google's robots.txt and terms of service
- Adjust delay times based on your needs
- Regular data backups recommended

### Common Issues and Solutions

1. **SSL Warnings**
   - Handled automatically in latest versions
   - Can be suppressed using provided warning filters

2. **Rate Limiting**
   - Adjust `time.sleep()` values if needed
   - Consider implementing proxy rotation

3. **Missing Data**
   - Scripts handle missing elements gracefully
   - Check CSV output for completeness

## Future Improvements
- [ ] Add proxy support
- [ ] Implement concurrent requests
- [ ] Add data validation
- [ ] Enhanced error reporting
- [ ] Support for additional search engines

## Notes
- Google may block requests if too many are made in a short time
- Consider implementing a proxy solution for production use
- Results may vary based on Google's search algorithm updates
- Always respect robots.txt and terms of service

## Contributing
Feel free to submit issues and enhancement requests!

