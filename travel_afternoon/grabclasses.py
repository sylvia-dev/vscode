import requests
from bs4 import BeautifulSoup

# Fetch webpage
url = 'https://www.cj.com/events/private/travelafternoon_24'
response = requests.get(url)
html_content = response.text

# Parse HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Extract classes from HTML elements
all_classes = []
for tag in soup.find_all(True):
    if 'class' in tag.attrs:
        classes = tag['class']
        all_classes.extend(classes)

# Remove duplicate classes
unique_classes = list(set(all_classes))

# Print the unique classes found
print("Unique classes found on the webpage:")
for class_name in unique_classes:
    print(class_name)
