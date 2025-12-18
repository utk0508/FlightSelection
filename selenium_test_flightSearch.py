from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Path to chrome driver
CHROME_DRIVER_PATH = "./chromedriver"

#Create Service instance
service = Service(executable_path=CHROME_DRIVER_PATH)

#Create webdriver instance
driver = webdriver.Chrome(service=service)

#Test: Open search page/home page and search for flight
def test_search_flights():
    #Make sure application is running
    driver.get("http://127.0.0.1:5000")

    try:
        from_location_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "from_location"))
        )
        to_location_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "to_location"))
        )

        #Input flight search, using Toronto and Vancouver
        print("Choosing flight starting location and destination.")
        from_location_input.send_keys("Toronto")
        time.sleep(1)  #Wait 1 second to see result
        to_location_input.send_keys("Vancouver")
        time.sleep(1)  #Wait 1 second to see result

        #Press search button
        print("Searching for flights by selecting search button.")
        to_location_input.send_keys(Keys.RETURN)
        time.sleep(1)  #Wait 1 second to see result

        #Make sure page was redirected to display flights page 
        WebDriverWait(driver, 20).until(
            EC.url_contains("/display_flights")
        )

        #Check if no flights are found
        no_flights_message = driver.find_elements(By.XPATH, "//p[text()='No flights found.']")
        if no_flights_message:
            print("No flights found.")
            return  #Exit if no flights are found

        #Check if flight rows are present in the table
        flights = driver.find_elements(By.TAG_NAME, "tr")
        if len(flights) > 1:  
            print(f"Test passed: {len(flights) - 1} flights found.") #-1 to account for header
        else:
            print("No flights found.")
            return

    except Exception as e:
        print(f"Test failed: {e}")
        raise  

    finally:
        time.sleep(3)  #Wait 3 seconds to see result before closing the browser
        driver.quit()

if __name__ == "__main__":
    test_search_flights()


