import requests

# URL of the webpage to scrape
url = 'https://www.cj.com/events/private/travelafternoon_24'

# Send a GET request to the URL
response = requests.get(url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Save the HTML content to a file
    with open('webpage.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("Webpage content saved successfully as 'webpage.html'")
else:
    print("Failed to retrieve webpage. Status code:", response.status_code)
