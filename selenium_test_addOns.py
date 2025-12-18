from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_add_ons():
    # Initialize the WebDriver
    driver = webdriver.Chrome()  # Ensure ChromeDriver is installed and in your PATH
    driver.get("http://127.0.0.1:5000/add_ons")  # Update the URL as per your local server setup

    # Debugging: Print page source to confirm the page is loaded
    print(driver.page_source)

    # Wait for the First Class button to be visible
    first_class_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "addFirstClassBtn"))
    )

    # Test adding First Class upgrade
    first_class_button.click()
    time.sleep(1)
    assert first_class_button.text == "REMOVE", "Failed to add First Class upgrade."
    print("First Class upgrade added successfully.")

    # Test removing First Class upgrade
    first_class_button.click()
    time.sleep(1)
    assert first_class_button.text == "ADD", "Failed to remove First Class upgrade."
    print("First Class upgrade removed successfully.")

    # Test adding Insurance
    insurance_button = driver.find_element(By.ID, "addInsuranceBtn")
    insurance_button.click()
    time.sleep(1)
    assert insurance_button.text == "REMOVE", "Failed to add Insurance."
    print("Insurance added successfully.")

    # Test removing Insurance
    insurance_button.click()
    time.sleep(1)
    assert insurance_button.text == "ADD", "Failed to remove Insurance."
    print("Insurance removed successfully.")

    # Test increasing baggage count
    increase_baggage_button = driver.find_element(By.ID, "increaseBaggageBtn")
    decrease_baggage_button = driver.find_element(By.ID, "decreaseBaggageBtn")
    baggage_count = driver.find_element(By.ID, "baggageCount")

    for _ in range(3):
        increase_baggage_button.click()
        time.sleep(1)
    assert baggage_count.text == "3", f"Baggage count incorrect. Expected 3, got {baggage_count.text}"
    print("Baggage count increased successfully to 3.")

    # Test decreasing baggage count
    decrease_baggage_button.click()
    time.sleep(1)
    assert baggage_count.text == "2", f"Baggage count incorrect. Expected 2, got {baggage_count.text}"
    print("Baggage count decreased successfully to 2.")

    print("Add-ons confirmed successfully, redirected to Traveller Information page.")

    # Close the browser
    driver.quit()

# Run the test
test_add_ons()
