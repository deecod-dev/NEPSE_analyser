from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from bs4 import BeautifulSoup
import csv
import os
import time
import telebot
import traceback
import subprocess
from selenium.common.exceptions import TimeoutException



# command = "pip install -r _req.txt"
# try:
#     # subprocess.check_call(command, shell=True)
#     print("Requirements installed successfully.")
# except subprocess.CalledProcessError:
#     print("Error installing requirements.")



bot = telebot.TeleBot(API_KEY, parse_mode=None)
num_pages = 4

wait_time = 4


def time_sleep(t):
    for i in range(t):
        time.sleep(1)
        print(t-i)


def scroll_to_bottom():
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Adjust the sleep time as needed
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def extract_table_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table', {'id': 'buyer-table'})
    if table:
        rows = table.find_all('tr')
        table_data = []
        for row in rows:
            cells = row.find_all(['td'])
            # cells = [ele.text.strip() for ele in cells]
            if len(cells) >= 5:  # Ensure that there are enough cells in the row
                try:
                    Symbol = cells[0].text.strip()
                    t1 = extract_tuple(cells[1].text.strip())
                    t2 = extract_tuple(cells[2].text.strip())
                    t3 = extract_tuple(cells[3].text.strip())

                    table_data.append([Symbol]+t1+t2+t3)
                except:
                    pass
    return table_data


def write_to_csv(data, filename):
    df = pd.DataFrame(data, columns=['Symbol', 'broker1', 'volume1', 'percent1', 'broker2', 'volume2', 'percent2', 'broker3', 'volume3', 'percent3'])
    df = df.sort_values(by='percent1', ascending=False)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename} .")
    return df


def extract_tuple(input_string):
    # Define the regex pattern
    pattern = r"(\d+)\s*\n\s*\((\d+)\s*,\s*\n\s*([\d\.]+)\s*%\)"
    
    # Search for the pattern in the input string
    match = re.search(pattern, input_string)
    
    try:
        # Extract the variables from the match
        broker_id = int(match.group(1))
        volume = int(match.group(2))
        percent = float(match.group(3))

        return [broker_id, volume, percent]
    except:
        return [None, None, None]


# def check_success(df):
#     symbol_buyer_freq = df['Stock Symbol_Buyer'].value_counts()

#     # Filter 'Stock Symbol_Buyer' with frequency > 50
#     frequent_symbols = symbol_buyer_freq[symbol_buyer_freq > 50].index.tolist()

#     # Filter DataFrame to include only rows with 'Stock Symbol_Buyer' in frequent_symbols
#     filtered_df = df[df['Stock Symbol_Buyer'].isin(frequent_symbols)]

#     filtered_df.reset_index(drop=True, inplace=True)

#     # Iterate over each row and clean 'Amount (Rs)' values
#     for i in range(filtered_df.shape[0]):
#         filtered_df.at[i, 'Amount (Rs)'] = float(filtered_df.at[i, 'Amount (Rs)'].replace(',', ''))



#     # Group by 'Stock Symbol_Buyer' and sum the 'Amount (Rs)'
#     total_amounts = filtered_df.groupby('Stock Symbol_Buyer')['Amount (Rs)'].sum()

#     success_symbols = total_amounts[total_amounts > 5000000].index.tolist()

#     # If there are any success symbols, print "Success" along with those symbols
#     if success_symbols:
#         print("Success:")
#         for symbol in success_symbols:
#             print(symbol)
#         bot.send_message(
#             800851598, str(success_symbols))
#     else:
#         print("No success found.")


# Set up Chrome WebDriver
# Replace with the path to your chromedriver executable
try:
    chrome_driver_path = "_chromedriver_64.exe"

    chrome_options = Options()
    webdriver_service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)


    # Open the URL in the Chrome browser
    class_link = "https://nepsealpha.com/floorsheet-analysis"
    driver.get(class_link)
    scroll_to_bottom()
    wait = WebDriverWait(driver, 1000)
    pagination_element = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".dataTables_paginate.paging_simple_numbers"))
    )
    # .................................................

    # Wait until the dropdown is present
    wait = WebDriverWait(driver, 10)
    dropdown = wait.until(EC.presence_of_element_located((By.NAME, 'buyer-table_length')))
    
    # Create a Select object
    select = Select(dropdown)
    
    # Select the option with value "100"
    select.select_by_value('100')
    
    print("Option '100' selected successfully.")
    total_data = []
    # .................................................
    for i in range(1, num_pages+1):  # Loop through buttons 1 to 4
        print(f'clicking button-{i}')
        button_xpath = f"//a[@class='paginate_button ' and text()='{i}']"
        if i!=1:
            try:
                # Wait until the button is clickable
                button = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
                button.click()
                print(f"Button {i} clicked successfully.")
                time.sleep(1)
            except TimeoutException:
                print(f"Button {i} not found within the time limit.")
            except Exception as e:
                print(f"An error occurred while clicking button {i}: {e}")

        html_content = driver.page_source

        extracted_data = extract_table_data(html_content=html_content) 
        total_data.extend(extracted_data)
        time_sleep(wait_time)

    write_to_csv(total_data, "table_data")



except Exception as e2:
    e2 = traceback.format_exc(limit=None, chain=True)
    bot.send_message(
        800851598, f"Phase2_bulk_download threw error!!\n```{e2}```")
    traceback.print_exc()