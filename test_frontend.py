import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy import create_engine
from app import app, db, User, New_Event
import time

# Prefix for test data
TEST_PREFIX = "test_"

# Fixture for setting up the database
@pytest.fixture(scope="session")
def setup_database():
    # Create all tables in the main database
    with app.app_context():
        db.create_all()

    # Clean up test data before testing
    with app.test_request_context():
        # Delete events associated with test users first
        test_users = db.session.query(User).filter(User.username.startswith(TEST_PREFIX)).all()
        for user in test_users:
            db.session.query(New_Event).filter_by(user_id=user.id).delete()

        # Then delete the test users
        db.session.query(User).filter(User.username.startswith(TEST_PREFIX)).delete()
        db.session.commit()
    yield

    # Clean up test data after testing
    with app.app_context():
        db.session.query(User).filter(User.username.startswith(TEST_PREFIX)).delete()
        
# Fixture for initializing the Selenium WebDriver
@pytest.fixture(scope="module")
def driver():
    driver = webdriver.Firefox()  # Use appropriate WebDriver
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

# Test case for registration and login
# Test case for registration and login
def test_registration_and_login(driver, setup_database):
    driver.get("http://127.0.0.1:443")

    # Wait for register button to be clickable
    register_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn-primary'))
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
    time.sleep(5)  # Adding a short delay for demonstration purposes
    
    # Verify that the registration was successful by checking the title
    assert "Splash Page" in driver.title
    
    # Login
   
    # Wait for login fields to be visible
    username_field = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "username"))
    )
    username_field.send_keys("test_usernamee")

    # Fill password field
    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys("test_passworde")

    # Find and click submit button
    submit_button = driver.find_element(By.CSS_SELECTOR, ".btn-success")
    submit_button.click()

    # Wait for the calendar page to load
    WebDriverWait(driver, 10).until(
        EC.title_contains("Calendar")
    )

    # Verify that the calendar view is loaded
    assert "Calendar" in driver.title
    
    add_event_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.buttons'))
    )
    add_event_button.click()

    # Wait for the add_event page to load
    WebDriverWait(driver, 10).until(
        EC.title_contains("Add Event")
    )

    # Fill out the add event form
    title_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "title"))
    )
    title_input.send_keys("Test Event Title")

    start_time_input = driver.find_element(By.ID, "start_time")
    start_time_input.send_keys("3202-02-40T12:00")  # Example start time, adjust as needed

    end_time_input = driver.find_element(By.ID, "end_time")
    end_time_input.send_keys("3202-02-40T13:00")  # Example end time, adjust as needed
    time.sleep(5)
    # Submit the form
    submit_button = driver.find_element(By.CSS_SELECTOR, ".btn-primary")
    submit_button.click()

    # Wait for the page to load after submission
    WebDriverWait(driver, 10).until(
        EC.title_contains("Calendar")
    )
    time.sleep(5)

    # Verify that we are back on the calendar page after submitting the event
    assert "Calendar" in driver.title
    
    event_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'fc-event'))
    )
    event_element.click()

    WebDriverWait(driver, 10).until(
        EC.title_contains("Edit Event")
    )

    # Modify event title
    title_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "title"))
    )
    title_input.clear()
    title_input.send_keys("Modified Event Title")
    time.sleep(5)
    submit_button = driver.find_element(By.CSS_SELECTOR, ".btn-primary")
    submit_button.click()

    WebDriverWait(driver, 10).until(
        EC.title_contains("Calendar")
    )
    time.sleep(5)

    assert "Calendar" in driver.title