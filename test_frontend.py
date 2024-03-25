import time  # Import time module for sleep
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

@pytest.fixture(scope="module")
def driver():
    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

def test_register(driver):
    driver.get("http://127.0.0.1:443")
    
    # Wait for register button to be clickable
    register_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-primary"))
    )
    register_button.click()

    # Wait for username field to be visible
    username_field = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "username"))
    )
    username_field.send_keys("test_usernamee")

    # Find and fill password field
    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys("test_passworde")

    # Find and click submit button
    submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
    submit_button.click()

    # Wait for the registration process to complete and splash page to load
    time.sleep(2)  # Adding a short delay for demonstration purposes
    
    # Verify that the registration was successful by checking the title
    assert "Splash Page" in driver.title