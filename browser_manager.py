import random
import re
import time
import os
import logging
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import HEADLESS, USER_AGENTS, REDEEM_URL, BUTTON_XPATH

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class BrowserManager:
    def __init__(self, max_browsers=3):
        self.max_browsers = max_browsers
        self.browsers = []
        logger.info(f"Initializing BrowserManager with {max_browsers} browsers")
        self.initialize_browsers()
    
    def initialize_browsers(self):
        """Initialize the browser instances"""
        for i in range(self.max_browsers):
            logger.info(f"Creating browser {i+1}/{self.max_browsers}")
            browser = self.create_browser()
            if browser:
                self.browsers.append(browser)
        
        logger.info(f"Successfully initialized {len(self.browsers)} browsers")
    
    def update_chrome(self):
        """Update Chrome to the latest version"""
        try:
            logger.info("Updating Chrome to the latest version")
            os.system("sudo apt-get update")
            os.system("sudo apt-get install -y google-chrome-stable")
            return True
        except Exception as e:
            logger.error(f"Error updating Chrome: {e}")
            return False
    
    def create_browser(self):
        """Create a new browser instance with random user agent"""
        options = ChromeOptions()
        if HEADLESS:
            options.add_argument("--headless=new")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-notifications")
        options.add_argument("--incognito")
        options.add_argument("--disable-cookies")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Try different approaches to create a browser
        for attempt in range(3):
            try:
                logger.info(f"Browser creation attempt {attempt+1}/3")
                
                if attempt == 0:
                    # First try: Use undetected-chromedriver
                    logger.info("Attempting to create browser with undetected-chromedriver")
                    try:
                        import undetected_chromedriver as uc
                    except ImportError:
                        os.system("pip install -U undetected-chromedriver")
                        import undetected_chromedriver as uc
                    
                    driver = uc.Chrome(options=options)
                    logger.info("Successfully created browser with undetected-chromedriver")
                    return driver
                
                elif attempt == 1:
                    # Second try: Use Selenium Manager
                    logger.info("Attempting to create browser with Selenium Manager")
                    chrome_options = ChromeOptions()
                    for arg in options.arguments:
                        chrome_options.add_argument(arg)
                    
                    driver = webdriver.Chrome(options=chrome_options)
                    logger.info("Successfully created browser with Selenium Manager")
                    return driver
                
                else:
                    # Third try: Use a simple approach
                    logger.info("Attempting to create browser with basic Chrome")
                    driver = webdriver.Chrome()
                    logger.info("Successfully created browser with basic Chrome")
                    return driver
            
            except Exception as e:
                logger.error(f"Error in browser creation attempt {attempt+1}: {e}")
        
        logger.error("All browser creation attempts failed")
        return None
    
    def extract_key_from_url(self, url):
        """Extract the Apple TV key from the URL"""
        match = re.search(r'code=([A-Z0-9]+)', url)
        if match:
            key = match.group(1)
            logger.info(f"Extracted key from URL: {key}")
            return key
        logger.warning(f"Could not extract key from URL: {url}")
        return None
    
    def generate_key(self, browser_index=0):
        """Generate an Apple TV key using a specific browser"""
        if browser_index >= len(self.browsers):
            logger.error(f"Invalid browser index: {browser_index}, max index: {len(self.browsers)-1}")
            return None
        
        browser = self.browsers[browser_index]
        logger.info(f"Generating key with browser {browser_index}")
        
        # Set a timeout for the entire key generation process
        start_time = time.time()
        timeout = 60  # 60 seconds timeout
        
        try:
            logger.info(f"Navigating to {REDEEM_URL}")
            browser.get(REDEEM_URL)
            
            # Take screenshot for debugging
            try:
                screenshot_path = f"browser_{browser_index}_before_click.png"
                browser.save_screenshot(screenshot_path)
                logger.info(f"Saved screenshot to {screenshot_path}")
            except Exception as e:
                logger.error(f"Error saving screenshot: {e}")
            
            # Wait for the button to be clickable
            logger.info(f"Waiting for button to be clickable: {BUTTON_XPATH}")
            button = WebDriverWait(browser, 20).until(
                EC.element_to_be_clickable((By.XPATH, BUTTON_XPATH))
            )
            logger.info("Button found, clicking")
            button.click()
            
            # Wait for URL to change
            logger.info("Waiting for URL to change")
            WebDriverWait(browser, 20).until(
                lambda driver: "code=" in driver.current_url
            )
            
            # Extract key from URL
            logger.info(f"URL changed to: {browser.current_url}")
            key = self.extract_key_from_url(browser.current_url)
            
            # Clear cookies and cache
            logger.info("Clearing cookies and cache")
            browser.delete_all_cookies()
            browser.execute_script("window.localStorage.clear();")
            browser.execute_script("window.sessionStorage.clear();")
            
            return key
        
        except Exception as e:
            logger.error(f"Error generating key with browser {browser_index}: {e}")
            
            # Take screenshot for debugging
            try:
                screenshot_path = f"browser_{browser_index}_error.png"
                browser.save_screenshot(screenshot_path)
                logger.info(f"Saved error screenshot to {screenshot_path}")
            except Exception as e:
                logger.error(f"Error saving error screenshot: {e}")
            
            # Check if timeout occurred
            if time.time() - start_time > timeout:
                logger.error(f"Key generation timed out after {timeout} seconds")
            
            # Recreate browser instance if there's an error
            logger.info(f"Recreating browser {browser_index}")
            try:
                browser.quit()
            except:
                pass
            
            new_browser = self.create_browser()
            if new_browser:
                self.browsers[browser_index] = new_browser
            return None
    
    def generate_keys(self, count=1):
        """Generate multiple keys using all available browsers"""
        keys = []
        browser_index = 0
        
        logger.info(f"Generating {count} keys with {len(self.browsers)} browsers")
        
        if len(self.browsers) == 0:
            logger.error("No browsers available for key generation")
            # Try to initialize browsers again
            logger.info("Attempting to reinitialize browsers")
            self.initialize_browsers()
            if len(self.browsers) == 0:
                return keys
        
        # Set a timeout for the entire key generation process
        start_time = time.time()
        timeout = 300  # 5 minutes timeout
        
        while len(keys) < count and len(self.browsers) > 0:
            # Check if timeout occurred
            if time.time() - start_time > timeout:
                logger.error(f"Key generation batch timed out after {timeout} seconds")
                break
            
            key = self.generate_key(browser_index)
            if key:
                logger.info(f"Successfully generated key: {key}")
                keys.append(key)
            else:
                logger.warning(f"Failed to generate key with browser {browser_index}")
            
            # Move to next browser
            browser_index = (browser_index + 1) % len(self.browsers)
            
            # Small delay to prevent rate limiting
            time.sleep(2)
        
        logger.info(f"Generated {len(keys)} keys")
        return keys
    
    def close_all(self):
        """Close all browser instances"""
        logger.info(f"Closing {len(self.browsers)} browsers")
        for i, browser in enumerate(self.browsers):
            try:
                logger.info(f"Closing browser {i}")
                browser.quit()
            except Exception as e:
                logger.error(f"Error closing browser {i}: {e}")
        self.browsers = []
        logger.info("All browsers closed") 