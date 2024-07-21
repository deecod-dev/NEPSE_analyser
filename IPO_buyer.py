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





BASE_PRICE = 880
MAX_QUANTITY = "1000"
WAIT_TIME = 0.1

# Initialize WebDriver (Assuming you are using Chrome)
driver = webdriver.Chrome()

try:
    # Load the initial webpage
    driver.get("https://tms58.nepsetms.com.np/tms/me/memberclientorderentry")
    
    # Wait for 20 seconds to allow manual login
    done = input("Done? (Press Enter if done)")

    # Reload the webpage to ensure proper loading post-login
    driver.get("https://tms58.nepsetms.com.np/tms/me/memberclientorderentry")
    
    # Wait for manual setting of stock symbol and quantity
    done = input("Entered script and quantity and pressed toggle? (Press Enter if done)")

    # Locate the quantity input box
    quantity_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input.form-control.form-control-sm.form-qty"))
    )
    print("Quantity input box located")
    quantity_input.clear()
    quantity_input.send_keys("10")

    # Locate the price input box
    price_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input.form-control.form-control-sm.form-price"))
    )
    print("Price input box located")
    price_input.clear()
    price_input.send_keys(str(BASE_PRICE))

    # Define a more specific selector for the BUY button
    buy_button_selector = "button.btn.btn-sm.btn-primary[type='submit']"
    noErrFlag = False
    while not noErrFlag:
        try:
            print("Trying to locate BUY button")
            buy_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, buy_button_selector))
            )
            print("BUY button found and clickable")
            noErrFlag = True
        except Exception as e:
            print(f"Exception occurred: {e}")
            noErrFlag = False
            pass

    assert noErrFlag == True
    print("Buy Button located")

    # =----------------------------------------------------------------------
    def bruteforce_price(price, volume):
        # Continuously enter the price and press the buy button every WAIT_TIME seconds
        while True:
            print("Calling enter_price_and_buy")
            print("Entering volume")
            quantity_input.clear()
            quantity_input.send_keys(volume)
            
            print("Entering price")
            price_input.clear()
            price_input.send_keys(price)
            
            print("Clicking BUY button")
            buy_button.click()

            # Check if the button is disabled, indicating a successful trade
            if buy_button.get_attribute('disabled'):
                return "SUCCESS"

            time.sleep(WAIT_TIME)

    # Perform the buying process with increasing prices
    for i in range(1, 6):
        TRADE_PRICE = BASE_PRICE * ((1.02) ** i)
        TRADE_PRICE = str(round(TRADE_PRICE, 1))
        if i == 5:
            bruteforce_price(TRADE_PRICE, MAX_QUANTITY)
        else:
            bruteforce_price(TRADE_PRICE, "10")

finally:
    driver.quit()
