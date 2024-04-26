import pytest
import app
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app import db, User, New_Event

# Prefix for test data
TEST_PREFIX = "test_"

# Fixture for setting up the database
@pytest.fixture(scope="session")
def setup_database():
    # Create all tables in the main database
    with app.app.app_context():
        db.create_all()
        yield  # Provide control back to the test function
        db.drop_all()

# Fixture for initializing the Selenium WebDriver
@pytest.fixture(scope="module")
def driver():
    driver = webdriver.Firefox()  # Use appropriate WebDriver
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

# Test case for registration and login
@pytest.mark.usefixtures("setup_database")
def test_registration_and_login(driver):

    driver.get("http://127.0.0.1:443")

    # Perform registration
    register_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, 'or create account'))
    )
    register_button.click()

    username_field = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "username"))
    )
    username_field.send_keys("test_user")

    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys("test_password")

    submit_button = driver.find_element(By.CSS_SELECTOR, ".btn-primary")
    submit_button.click()

    time.sleep(2)  # Wait for registration to complete

    # Perform login
    username_field = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "username"))
    )
    username_field.send_keys("test_user")

    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys("test_password")

    submit_button = driver.find_element(By.CSS_SELECTOR, ".btn-primary")
    submit_button.click()

    time.sleep(2)  # Wait for login to complete

    # Perform event addition
    add_event_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.buttons'))
    )
    add_event_button.click()

    title_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "title"))
    )
    title_input.send_keys("Test Event")

    start_time_input = driver.find_element(By.ID, "start_time")
    start_time_input.send_keys("4042-02-40T12:00")

    end_time_input = driver.find_element(By.ID, "end_time")
    end_time_input.send_keys("4042-02-40T13:00")
    
    time.sleep(4)

    submit_button = driver.find_element(By.CSS_SELECTOR, ".btn-primary")
    submit_button.click()

    time.sleep(2)  # Wait for event addition to complete

    # Verify event insertion into the database
    with app.app.app_context():
        assert New_Event.query.filter_by(title='Test Event').first() is not None

    assert "Calendar" in driver.title
    
    # Perform event editing
    edit_event_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href*="/edit_event"]'))
    )
    edit_event_button.click()

    time.sleep(2)  # Wait for the page to load

    title_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "title"))
    )
    title_input.clear()
    title_input.send_keys("Edited Event")

    submit_button = driver.find_element(By.CSS_SELECTOR, ".btn-primary")
    submit_button.click()

    time.sleep(2)  # Wait for event editing to complete

    # Verify event editing in the database
    with app.app.app_context():
        edited_event = New_Event.query.filter_by(title='Edited Event').first()
        assert edited_event is not None
        
    edit_event_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href*="/edit_event"]'))
    )
    edit_event_button.click()

    # Perform event deletion
    delete_event_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.btn-danger'))
    )
    delete_event_button.click()

    time.sleep(2)  # Wait for the confirmation dialog to appear

    #confirm_delete_button = driver.switch_to.alert
    #confirm_delete_button.accept()

    time.sleep(2)  # Wait for event deletion to complete

    # Verify event deletion from the database
    with app.app.app_context():
        assert New_Event.query.filter_by(title='Edited Event').first() is None

    # Perform logout
    logout_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//form[@action="/logout"]/button'))
    )
    logout_button.click()

    time.sleep(2)  # Wait for logout to complete

    assert "Splash Page" in driver.title