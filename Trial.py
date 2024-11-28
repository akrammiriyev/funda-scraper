from selenium import webdriver
from bs4 import BeautifulSoup
import re
import pandas as pd
import time

# Base URL for Funda
BASE_URL = "https://www.funda.nl/en/zoeken/koop/?selected_area=%5B%22nl%22%5D"

# Parameters
params = {
    'price_min': 300000,  # Minimum price
    'price_max': 800000,  # Maximum price
    'location': 'amsterdam',  # Location (city or region)
    'object_type': 'house',  # Type: 'house' or 'apartment'
    'plot_area_min': 50,  # Minimum plot area in m²
    'plot_area_max': 500,  # Maximum plot area in m²
    'living_area_min': 80,  # Minimum living area in m²
    'living_area_max': 200,  # Maximum living area in m²
    'bedroom_min':3,
    'bedroom_max':5,
    'Energy label':'A'
    

}

# Helper function to build URL
# def build_url(params):
#     url = BASE_URL + params['location'] + '/'
#     if params['house_type'] == 'apartment':
#         url += 'appartement/'
#     else:
#         url += 'huis/'

#     url += f'{params["price_min"]}-{params["price_max"]}/'
#     print(url)
#     return url
# Construct URL
base_url = "https://www.funda.nl/en/zoeken/koop?"
query_string = f"selected_area=%5B%22{params['location']}%22%5D&object_type=%5B%22{params['object_type']}%22%5D&price=%22{params['price_min']}-{params['price_max']}%22&floor_area=%22{params['living_area_min']}-{params['living_area_max']}%22&bedrooms=%22{params['bedroom_min']}-{params['bedroom_max']}%22&energy_label=%5B%22{params['Energy label']}%22%5D"
url = base_url + query_string
print(url)


# Initialize Selenium WebDriver (replace with the path to your downloaded ChromeDriver)
driver_path = '/chromedriver.exe'
driver = webdriver.Chrome(driver_path)

# Example Funda URL (update parameters as needed)
# url = "https://www.funda.nl/en/zoeken/koop?selected_area=%5B%22nl%22%5D&price=%22300000-800000%22&object_type=%5B%22house%22%5D&plot_area=%22-500%22"
driver.get(url)

# Wait for JavaScript to load the listings
time.sleep(5)  # Adjust as needed depending on your internet speed

# Parse the page source with BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Close the WebDriver
driver.quit()

# Main scraping function
def scrape_funda(params):
    # # url = build_url(params)
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36'
    # }
    # response = requests.get(url, headers=headers)
    # soup = BeautifulSoup(response.text, 'html.parser')
    

    # Lists to store data
    addresses, prices, details, areas, price_per_area = [], [], [], [], []

    # Check for correct structure based on common Funda structure
    for listing in soup.select('[data-test-id="search-result-item"]'): # search-result-item 11-Nov-2024.
        # Address
        address_elem = listing.select_one('[data-test-id="postal-code-city"]')
        if address_elem:
            address = address_elem.get_text(strip=True)
            addresses.append(address)
        else:
            continue  # Skip if address is not found

        # Price
        price_elem = listing.select_one('.price-sale')
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            price = int(re.sub(r'\D', '', price_text))  # Remove non-numeric characters and convert to int
            prices.append(price)
        else:
            prices.append(None)

        # Details
        detail_elem = listing.select_one('.search-result-kenmerken')
        detail_text = detail_elem.get_text(separator=", ", strip=True) if detail_elem else ""
        details.append(detail_text)

        # Extract living area from details if available
        area_match = re.search(r'(\d+)\s*m²', detail_text)
        if area_match:
            area = int(area_match.group(1))  # Get the numeric value of the area
            areas.append(area)
            price_per_area.append(price / area if area > 0 else None)
        else:
            areas.append(None)
            price_per_area.append(None)

    # Saving to a DataFrame
    df = pd.DataFrame({
        'Address': addresses,
        'Price': prices,
        'Details': details,
        'Living Area (m²)': areas,
        'Price per m²': price_per_area
    })
    # print(soup.prettify())
    # Save to CSV
    df.to_csv('results.csv', index=False)
    return df

# Run the scraping
data = scrape_funda(params)
# print(url)

print(data)
