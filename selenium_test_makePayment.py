from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def test_select_and_make_payment():
    #initialize driver (chrome)
    driver = webdriver.Chrome()

    #link used is make_payment but it redirects to home page because we do not have a flight selected (check app.py)
    #we have to select flight before it goes to the make payment page.
    driver.get("http://127.0.0.1:5000/make_payment")

    try:
        from_location_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "from_location"))
        )
        to_location_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "to_location"))
        )

        from_location_input.send_keys("Toronto")
        time.sleep(1)  # Wait for the input
        to_location_input.send_keys("Vancouver")
        time.sleep(1)  # Wait for the input

        submit_input = WebDriverWait(driver, 1).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/form/button"))
        )
        submit_input.click() #click on button to move to next page

        #display flights page
        WebDriverWait(driver, 1).until(
            EC.url_contains("/display_flights")
        )

        #button to select flight
        select_flight_button = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/table/tbody/tr[3]/td[1]/input"))) 
        #button to confirm selection and move to next page
        submit_flight = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/button")))

        #click to select flight and then wait for 1 second and then submit selection
        select_flight_button.click() 
        time.sleep(1)
        submit_flight.click()


        # Redirect to the Make Payments page directly
        driver.get("http://127.0.0.1:5000/make_payment")

        #confirm reditrection
        WebDriverWait(driver, 2).until(EC.url_contains("/make_payment"))


        #check the review page and click on icon to look at the contents, click icon again to put it back up
        review_trip = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/details[1]/summary/span")))
        time.sleep(1)
        review_trip.click()
        time.sleep(3)
        review_trip.click()

        #click on icon for drop down to input payment information
        payment_info = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/details[2]/summary/span")))
        time.sleep(1)
        payment_info.click()

        #check for card details locations and input the details
        card_number_input = driver.find_element(By.ID, "card-number")
        expiry_input = driver.find_element(By.ID, "expiry")
        cvv_input = driver.find_element(By.ID, "cvv")

        card_number_input.send_keys("123456789124567")
        time.sleep(2)
        expiry_input.send_keys("2026/12/24")
        time.sleep(1)
        cvv_input.send_keys("123")
        time.sleep(2)

        #look for where it shows total cost and print it as output
        total_cost = driver.find_element(By.ID, "totalCost").text
        print(f"Total Cost: {total_cost}")

        #confirm details and pay
        confirm_button = driver.find_element(By.XPATH, "/html/body/form/div/button")
        confirm_button.click()


    finally:
        #Wait 3 seconds to see result before closing the browser
        time.sleep(3) 
        driver.quit()


if __name__ == "__main__":
    test_select_and_make_payment()
