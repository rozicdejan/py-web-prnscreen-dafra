import yaml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import schedule
import time
from datetime import datetime
import os
import psutil  # To monitor system and container resources

# Load configuration from config.yml
def load_config(file="config.yml"):
    try:
        print(f"[{datetime.now()}] Loading configuration from {file}")
        with open(file, "r") as f:
            config = yaml.safe_load(f)
            print(f"[{datetime.now()}] Configuration loaded successfully")
            return config
    except Exception as e:
        print(f"[{datetime.now()}] Failed to load configuration: {e}")
        raise

# Log Docker container information
def log_docker_info():
    try:
        print(f"[{datetime.now()}] Logging Docker container environment and resource info")
        print(f"[{datetime.now()}] Environment Variables:")
        for key, value in os.environ.items():
            print(f"  {key} = {value}")

        # Resource usage stats
        memory_info = psutil.virtual_memory()
        cpu_usage = psutil.cpu_percent(interval=1)
        print(f"[{datetime.now()}] Resource Usage:")
        print(f"  Total Memory: {memory_info.total / (1024 ** 2):.2f} MB")
        print(f"  Available Memory: {memory_info.available / (1024 ** 2):.2f} MB")
        print(f"  Used Memory: {memory_info.used / (1024 ** 2):.2f} MB")
        print(f"  Memory Usage Percentage: {memory_info.percent}%")
        print(f"  CPU Usage: {cpu_usage}%")

        print(f"[{datetime.now()}] Docker-specific information logged (if running in a container).")
    except Exception as e:
        print(f"[{datetime.now()}] Error logging Docker information: {e}")

# Retry mechanism
def take_screenshot_with_retry(config, max_retries, delay):
    print(f"[{datetime.now()}] Starting screenshot task with max retries: {max_retries}, delay: {delay}s")
    for attempt in range(max_retries):
        try:
            print(f"[{datetime.now()}] Attempt {attempt + 1} to take screenshot")
            take_screenshot(config)
            print(f"[{datetime.now()}] Screenshot taken successfully on attempt {attempt + 1}")
            break  # Exit loop if successful
        except Exception as e:
            print(f"[{datetime.now()}] Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"[{datetime.now()}] Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"[{datetime.now()}] Max retries reached. Skipping for now.")

# Main function to take a screenshot
def take_screenshot(config):
    driver = None  # Initialize driver to None
    try:
        print(f"[{datetime.now()}] Setting up WebDriver")
        # Setup WebDriver
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run in headless mode
        options.add_argument("--no-sandbox")  # Disable the sandbox (necessary in Docker)
        options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
        options.add_argument("--disable-gpu")  # Disable GPU (not needed in headless mode)
        options.add_argument("--disable-extensions")  # Disable extensions
        options.add_argument("--remote-debugging-port=9222")  # Enable remote debugging
        options.add_argument("--window-size=1920,1080")  # Set a specific window size
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        print(f"[{datetime.now()}] WebDriver setup complete")

        # Open the website
        url = config["login"]["url"]
        print(f"[{datetime.now()}] Navigating to URL: {url}")
        driver.get(url)

        # Locate username and password fields
        print(f"[{datetime.now()}] Locating username and password fields")
        username = driver.find_element(By.NAME, "userLoginName")
        password = driver.find_element(By.NAME, "userLoginPass")

        # Locate login button
        print(f"[{datetime.now()}] Locating login button")
        login_button = driver.find_element(By.XPATH, "//input[@type='submit' and @value='Prijava']")

        # Input credentials
        print(f"[{datetime.now()}] Entering login credentials")
        username.send_keys(config["login"]["username"])
        password.send_keys(config["login"]["password"])
        login_button.click()

        # Wait for the page to load
        print(f"[{datetime.now()}] Waiting for the page to load")
        time.sleep(5)

        # Create screenshot directory if it doesn't exist
        screenshot_dir = config["screenshot"]["directory"]
        print(f"[{datetime.now()}] Ensuring screenshot directory exists: {screenshot_dir}")
        os.makedirs(screenshot_dir, exist_ok=True)

        # Take a screenshot
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        screenshot_path = os.path.join(screenshot_dir, f"screenshot_{timestamp}.png")
        print(f"[{datetime.now()}] Taking screenshot")
        driver.save_screenshot(screenshot_path)
        print(f"[{datetime.now()}] Screenshot saved as {screenshot_path}")

    except Exception as e:
        print(f"[{datetime.now()}] An error occurred while taking screenshot: {e}")
        raise  # Re-raise the exception for retry handling
    finally:
        if driver is not None:
            print(f"[{datetime.now()}] Quitting WebDriver")
            driver.quit()  # Ensure the driver is quit properly

if __name__ == "__main__":
    print(f"[{datetime.now()}] Script started")
    
    # Log Docker environment and resource info
    log_docker_info()

    # Load the configuration
    config = load_config()

    # Test screenshot immediately
    print(f"[{datetime.now()}] Testing screenshot functionality")
    take_screenshot_with_retry(config, config["retries"]["max_retries"], config["retries"]["delay"])

    # Schedule the task
    schedule_time = config["schedule"]["time"]
    print(f"[{datetime.now()}] Scheduling task at {schedule_time}")
    schedule.every().day.at(schedule_time).do(
        lambda: take_screenshot_with_retry(config, config["retries"]["max_retries"], config["retries"]["delay"])
    )

    print(f"[{datetime.now()}] Scheduler is running. Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(1)
