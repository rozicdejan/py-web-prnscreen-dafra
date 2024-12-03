import yaml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import schedule
import time
from datetime import datetime
import os

# Load configuration from config.yml
def load_config(file="config.yml"):
    with open(file, "r") as f:
        return yaml.safe_load(f)

# Retry mechanism
def take_screenshot_with_retry(config, max_retries, delay):
    for attempt in range(max_retries):
        try:
            take_screenshot(config)
            print(f"Screenshot taken successfully on attempt {attempt + 1}.")
            break  # Exit loop if successful
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Max retries reached. Skipping for now.")

# Main function to take a screenshot
def take_screenshot(config):
    try:
        # Setup WebDriver
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run in headless mode (no browser UI)
        options.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # Open the website
        driver.get(config["login"]["url"])

        # Locate username and password fields
        username = driver.find_element(By.NAME, "userLoginName")
        password = driver.find_element(By.NAME, "userLoginPass")

        # Locate login button
        login_button = driver.find_element(By.XPATH, "//input[@type='submit' and @value='Prijava']")

        # Input credentials
        username.send_keys(config["login"]["username"])
        password.send_keys(config["login"]["password"])
        login_button.click()

        # Wait for the page to load
        time.sleep(5)

        # Create screenshot directory if it doesn't exist
        screenshot_dir = config["screenshot"]["directory"]
        os.makedirs(screenshot_dir, exist_ok=True)

        # Take a screenshot
        timestamp = datetime.now().strftime("%Y-%d-%m_%H-%M-%S")
        screenshot_path = os.path.join(screenshot_dir, f"screenshot_{timestamp}.png")
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved as {screenshot_path}")

    except Exception as e:
        raise Exception(f"Failed to take screenshot: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    # Load the configuration
    config = load_config()

    # Test screenshot immediately
    take_screenshot_with_retry(config, config["retries"]["max_retries"], config["retries"]["delay"])

    # Schedule the task
    schedule.every().day.at(config["schedule"]["time"]).do(
        lambda: take_screenshot_with_retry(config, config["retries"]["max_retries"], config["retries"]["delay"])
    )

    print("Scheduler is running. Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(1)
