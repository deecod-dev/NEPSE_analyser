from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def time_sleep(t):
    for i in range(t):
        time.sleep(1)
        print(t - i)

PRICE = "766"

# Initialize WebDriver (Assuming you are using Chrome)
driver = webdriver.Chrome()

try:
    # Load the initial webpage
    driver.get("https://tms58.nepsetms.com.np/tms/me/memberclientorderentry")
    
    # Wait for 20 seconds to allow manual login
    done = input("Done? (Press Enter if done)")

    # Reload the webpage to ensure proper loading post-login
    driver.get("https://tms58.nepsetms.com.np/tms/me/memberclientorderentry")
    
    # Wait for 25 seconds to allow manual setting of stock symbol and quantity
    done = input("Entered script and quantity and pressed toggle? (Press Enter if done)")

    # Locate the price input box and the sell button
    price_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input.form-control.form-control-sm.form-price"))
    )
    print("Price input box located")
    price_input.clear()
    price_input.send_keys(PRICE)

    # Define a more specific selector for the SELL button
    sell_button_selector = "button.btn.btn-sm.btn-danger[type='submit']"

    noErrFlag = False
    while not noErrFlag:
        try:
            print("Trying to locate sell button")
            sell_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, sell_button_selector))
            )
            print("sell button found and clickable")
            noErrFlag = True
        except Exception as e:
            print(f"Exception occurred: {e}")
            noErrFlag = False
            pass

    # Function to enter the price and click the sell button
    def enter_price_and_sell():
        print("Entering price")
        price_input.clear()
        price_input.send_keys(PRICE)
        print("Clicking sell button")
        sell_button.click()

    # Continuously enter the price and press the sell button every 10 seconds
    while True:
        print("Calling enter_price_and_sell")
        enter_price_and_sell()
        time.sleep(0.1)

finally:
    driver.quit()