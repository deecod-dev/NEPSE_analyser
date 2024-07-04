import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd

# Set up the Selenium WebDriver (you may need to specify the path to your WebDriver)
driver = webdriver.Chrome()

# Function to extract table data
def extract_table_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the table
    table = soup.find('table', class_='table table-hover table-bordered table-striped mb-0')

    # Initialize a list to store the table data
    data = []

    # Process the table rows
    rows = table.find_all('tr')[1:]  # Skip the header row
    num_brokers = 3
    for i in range(int(len(rows) / 2)):
        row1 = rows[2 * i]
        row2 = rows[2 * i + 1]

        # for row-1
        cells = row1.find_all('td')
        date = cells[0].get_text(strip=True)
        stock_price = cells[1].get_text(strip=True)
        daily_gain = cells[2].get_text(strip=True)

        to_be_appended_in_df = [date, stock_price, daily_gain]
        # Process each broker cell
        for i in range(3, 3 + num_brokers):
            broker_info = cells[i].get_text(strip=True)
            if broker_info:
                match = re.match(r"(\d+)\s*\((\d+)\s*,\s*([\d.]+)\s*%\)", broker_info)
                if match:
                    broker_number, volume, percent = match.groups()
                    to_be_appended_in_df.extend([broker_number, volume, percent])

        # for row-2
        cells = row2.find_all('td')

        for i in range(0, num_brokers):
            broker_info = cells[i].get_text(strip=True)
            if broker_info:
                match = re.match(r"(\d+)\s*\((\d+)\s*,\s*([\d.]+)\s*%\)", broker_info)
                if match:
                    broker_number, volume, percent = match.groups()
                    to_be_appended_in_df.extend([broker_number, volume, percent])

        data.append(to_be_appended_in_df)

    return data

# URL of the page with the stock selector and table
url = 'https://nepsealpha.com/monthly-floorsheet'
driver.get(url)

# Wait for the stock selector to load
wait = WebDriverWait(driver, 10)
stock_selector_xpath = "//select[@class='form-control searchable select2-hidden-accessible']"
wait.until(EC.presence_of_element_located((By.XPATH, stock_selector_xpath)))

# Parse the page source with BeautifulSoup to get the full list of stocks
html_content = driver.page_source
soup = BeautifulSoup(html_content, 'html.parser')

# Find the stock selector and extract all stock options
stock_selector = soup.find('select', class_='form-control searchable select2-hidden-accessible')
stock_options = stock_selector.find_all('option')

# Extract stock symbols and names
stocks = []
for option in stock_options:
    symbol = option.get('value')
    name = option.get_text(strip=True)
    if symbol:
        stocks.append((symbol, name))

# Initialize a list to store data for df2
df2_data = []

# Iterate through each stock
for symbol, name in stocks:
    lower_name = name.lower()
    if ("promoter" in lower_name)  or ("%" in lower_name)or ("fund" in lower_name) or ("debenture" in lower_name) :
        continue
    
    print("Processing", symbol, "-", name)

    # Reload the page for each stock to ensure the content is correctly loaded
    driver.get(url)
    wait.until(EC.presence_of_element_located((By.XPATH, stock_selector_xpath)))
    
    # Use JavaScript to set the value of the dropdown and trigger the change event
    driver.execute_script(f"document.querySelector('select.form-control.searchable.select2-hidden-accessible').value='{symbol}';")
    driver.execute_script(f"document.querySelector('select.form-control.searchable.select2-hidden-accessible').dispatchEvent(new Event('change'));")

    # Wait and then click the search button
    search_button_xpath = "//button[contains(text(), 'Search')]"
    search_button = wait.until(EC.element_to_be_clickable((By.XPATH, search_button_xpath)))
    search_button.click()

    # Optional: wait for a short time before moving to the next stock
    time.sleep(10)  # Adjust as needed

    table_xpath = "//table[@class='table table-hover table-bordered table-striped mb-0']"
    wait.until(EC.presence_of_element_located((By.XPATH, table_xpath)))

    # Extract the table data
    html_content = driver.page_source
    table_data = extract_table_data(html_content)

    # Convert the data to a DataFrame
    df = pd.DataFrame(table_data, columns=[
        'Date', 'Stock Price', 'Daily Gain',
        'Buy-Broker1', 'Buy-Volume1', 'Buy-Percent1',
        'Buy-Broker2', 'Buy-Volume2', 'Buy-Percent2',
        'Buy-Broker3', 'Buy-Volume3', 'Buy-Percent3',
        'Sell-Broker1', 'Sell-Volume1', 'Sell-Percent1',
        'Sell-Broker2', 'Sell-Volume2', 'Sell-Percent2',
        'Sell-Broker3', 'Sell-Volume3', 'Sell-Percent3'
    ])

    # Calculate the volume for each day
    df['Volume'] = df['Buy-Volume1'].astype(int) / df['Buy-Percent1'].astype(float) * 100

    # Calculate the average volume
    avg_volume = df['Volume'].mean()

    # Get the latest day's volume
    latest_volume = df['Volume'].iloc[0]  # Assuming the latest day is the first row
    latest_volume2 = df['Volume'].iloc[1]  # Assuming the latest day is the first row
    latest_volume3 = df['Volume'].iloc[2]  # Assuming the latest day is the first row

    # Calculate volume ratio
    volume_ratio = latest_volume / avg_volume
    volume_ratio2 = latest_volume2 / avg_volume
    volume_ratio3 =  latest_volume3 / avg_volume

    # Add data to df2_data
    df2_data.append({
        'Stock Symbol': symbol,
        'Ratio': volume_ratio,
        'Ratio2': volume_ratio2,
        'Ratio3': volume_ratio3
    })

    # Optional: Save the DataFrame to a CSV file
    filename = name.replace("/", "")
    df.to_csv(f'{filename}_table_data.csv', index=False)

# Create df2
df2 = pd.DataFrame(df2_data)
df2_sorted = df2.sort_values(by='Ratio')

# Save df2 to a CSV file
df2_sorted.to_csv('all_stocks_volume_ratio_and_broker_holdings.csv', index=False)

# Close the WebDriver
driver.quit()
