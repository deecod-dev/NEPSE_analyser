from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import requests
import traceback
import telebot
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def time_sleep(t):
    for i in range(t):
        time.sleep(1)
        print(t-i)

def wait_until_next_minute():
    current_time = datetime.now()
    next_minute = (current_time + timedelta(minutes=1)).replace(second=0, microsecond=0)
    sleep_time = (next_minute - current_time).total_seconds()
    print(f"waiting for {sleep_time} seconds")
    time.sleep(sleep_time)
    
def scroll_to_bottom():
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Adjust the sleep time as needed
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def extract_table_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table', class_='table__lg')
    if table:
        rows = table.find_all('tr')
        extracted_data = []
        for row in rows[1:]:  # Skip the first row as it contains headers
            cells = row.find_all('td')
            if len(cells) >= 8:  # Ensure that there are enough cells in the row
                sn = cells[0].text.strip()
                contract_no = int(cells[1].text.strip())
                stock_symbol = cells[2].text.strip()
                buyer = cells[3].text.strip()
                seller = cells[4].text.strip()
                quantity = float(cells[5].text.strip().replace(',', ''))
                rate_rs = float(cells[6].text.strip().replace(',', ''))
                amount_rs = float(cells[7].text.strip().replace(',', ''))
                title = cells[2].get('title', '')  # Fetch title attribute from the third cell
                extracted_data.append([sn, contract_no, stock_symbol, buyer, seller, quantity, rate_rs, amount_rs, title])
        return extracted_data
    else:
        print("Table not found in HTML content.")
        return None

def write_to_csv(old_df, data, filename):
    df = pd.DataFrame(data, columns=['SN', 'Contract No.', 'Stock Symbol', 'Buyer', 'Seller', 'Quantity', 'Rate (Rs)', 'Amount (Rs)', 'Title'])
    df['Stock Symbol_Buyer'] = df['Stock Symbol'] + '_' + df['Buyer']
    df['Stock Symbol_Seller'] = df['Stock Symbol'] + '_' + df['Seller']
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename} with additional columns.")
    old_df = old_df._append(df, ignore_index=True)
    return old_df

def send_file_on_tg(filename, API_KEY, user):
    files = {"document": open(filename, 'rb')}
    resp = requests.post("https://api.telegram.org/bot" + API_KEY + "/sendDocument?chat_id=" + user, files=files)
    return resp


def check_success(df):
    symbol_buyer_freq = df['Stock Symbol'].value_counts()
    frequent_symbols = symbol_buyer_freq[symbol_buyer_freq > 25].index.tolist()

    for symbol in frequent_symbols:
        filtered_df = df[df['Stock Symbol'] == symbol]
        total_amount = filtered_df['Amount (Rs)'].sum()

        if total_amount > 5000000:
            string_to_return = f"Symbol {symbol} has total turnover {total_amount / 100000:.2f} lacs."

            filtered_df['trend'] = 0
            val = 0

            for i in range(len(filtered_df) - 2, -1, -1):
                if filtered_df.iloc[i]['Rate (Rs)'] > filtered_df.iloc[i + 1]['Rate (Rs)']:
                    # recent vs old
                    val = 1
                elif filtered_df.iloc[i]['Rate (Rs)'] < filtered_df.iloc[i + 1]['Rate (Rs)']:
                    val = -1
                filtered_df.at[filtered_df.index[i], 'trend'] = val

            filtered_df.to_csv(f"filtered_df_{symbol}.csv", index=False)

            increasing_volume = filtered_df[filtered_df['trend'] == 1]['Quantity'].sum()
            decreasing_volume = filtered_df[filtered_df['trend'] == -1]['Quantity'].sum()
            total_volume = filtered_df['Quantity'].sum()

            string_to_return += f"\nSymbol {symbol} has total volume ({total_volume})."

            if increasing_volume > decreasing_volume:
                string_to_return += f"\nSymbol {symbol} has net volume ({increasing_volume}) in increasing trend."
            else:
                string_to_return += f"\nSymbol {symbol} has net volume ({decreasing_volume}) in decreasing trend."

            bot.send_message(800851598, string_to_return)

API_KEY = ""
bot = telebot.TeleBot(API_KEY, parse_mode=None)
wait_time = 4


def find_button(driver, i):
    noErrFlag = False
    while not noErrFlag:
        try:
            button_element = driver.find_element(By.XPATH, f"//a/span[text()='{i}']")
            noErrFlag = True
        except Exception as e:
            print(f"Exception occurred: {e}")
            noErrFlag = False
            pass
    return button_element

if __name__ == '__main__':
    try:
        driver = webdriver.Chrome()

        class_link = "https://nepalstock.com/floor-sheet"
        driver.get(class_link)
        scroll_to_bottom()
        wait = WebDriverWait(driver, 10)
        table_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".table-striped")))

        dropdown_element = driver.find_element(By.CSS_SELECTOR, ".table__perpage select")
        dropdown = Select(dropdown_element)
        dropdown.select_by_value("500")

        last_contract_num = 0
        while True:
            
            # beginning of minute
            button_element = find_button(driver, i)
            print("Click the button")
            button_element.click()
            print("Wait until the page loads 500 rows")
            time.sleep(wait_time)
            html_content = driver.page_source
            extracted_data = extract_table_data(html_content=html_content)
            df = write_to_csv(pd.DataFrame(), extracted_data, "1th_table.csv")

            if last_contract_num != df['Contract No.'].iloc[0]:
                # coming here means , somethings changed in floorsheet
                last_contract_num = df['Contract No.'].iloc[0]
                for i in range(2, 16):
                    button_element = driver.find_element(By.XPATH, f"//a/span[text()='{i}']")
                    print("Click the button")
                    button_element.click()

                    print("Wait until the page loads 500 rows")
                    time.sleep(wait_time)

                    html_content = driver.page_source
                    extracted_data = extract_table_data(html_content=html_content)
                    if extracted_data:
                        new_df = pd.DataFrame(extracted_data, columns=['SN', 'Contract No.', 'Stock Symbol', 'Buyer', 'Seller', 'Quantity', 'Rate (Rs)', 'Amount (Rs)', 'Title'])
                        new_df['Stock Symbol_Buyer'] = new_df['Stock Symbol'] + '_' + new_df['Buyer']
                        new_df['Stock Symbol_Seller'] = new_df['Stock Symbol'] + '_' + new_df['Seller']
                        new_df.to_csv(f"{i}th_table.csv", index=False)
                        df = df._append(df, ignore_index=True)
                        if last_contract_num in new_df['Contract No.']:
                            break
                    

                check_success(df)
            print("Waiting for new page")
            wait_until_next_minute()


    except Exception as e2:
        e2 = traceback.format_exc(limit=None, chain=True)
        bot.send_message(800851598, f"Bot threw error!!\n```{e2}```")
        traceback.print_exc()
