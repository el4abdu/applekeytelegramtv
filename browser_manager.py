import random
import re
import time
import os
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import HEADLESS, USER_AGENTS, REDEEM_URL, BUTTON_XPATH

class BrowserManager:
    def __init__(self, max_browsers=3):
        self.max_browsers = max_browsers
        self.browsers = []
        self.initialize_browsers()
    
    def initialize_browsers(self):
        """Initialize the browser instances"""
        for _ in range(self.max_browsers):
            browser = self.create_browser()
            if browser:
                self.browsers.append(browser)
    
    def create_browser(self):
        """Create a new browser instance with random user agent"""
        options = Options()
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
        
        # Install undetected-chromedriver
        try:
            os.system("pip install undetected-chromedriver")
            import undetected_chromedriver as uc
            
            driver = uc.Chrome(options=options)
            return driver
        except Exception as e:
            print(f"Error creating browser with undetected-chromedriver: {e}")
            
            # Try using Selenium Manager
            try:
                from selenium.webdriver.chrome.service import Service as ChromeService
                from selenium.webdriver.chrome.options import Options
                
                chrome_options = Options()
                for arg in options.arguments:
                    chrome_options.add_argument(arg)
                
                # Use selenium-manager to find proper driver
                driver = webdriver.Chrome(options=chrome_options)
                return driver
            except Exception as e2:
                print(f"Error creating browser with Selenium Manager: {e2}")
                
                # Try with a specific older Chrome version
                try:
                    # Try to downgrade Chrome and install matching driver
                    print("Attempting to install older Chrome version...")
                    os.system("sudo apt-get install -y wget gnupg")
                    os.system("wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -")
                    os.system("echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list")
                    os.system("sudo apt-get update")
                    os.system("sudo apt-get install -y google-chrome-stable=114.0.5735.198-1")
                    os.system("sudo apt-mark hold google-chrome-stable")
                    
                    # Now try again with the downgraded Chrome
                    driver = webdriver.Chrome(options=options)
                    return driver
                except Exception as e3:
                    print(f"Error after attempting Chrome downgrade: {e3}")
                    return None
    
    def extract_key_from_url(self, url):
        """Extract the Apple TV key from the URL"""
        match = re.search(r'code=([A-Z0-9]+)', url)
        if match:
            return match.group(1)
        return None
    
    def generate_key(self, browser_index=0):
        """Generate an Apple TV key using a specific browser"""
        if browser_index >= len(self.browsers):
            return None
        
        browser = self.browsers[browser_index]
        
        try:
            browser.get(REDEEM_URL)
            
            # Wait for the button to be clickable
            button = WebDriverWait(browser, 15).until(
                EC.element_to_be_clickable((By.XPATH, BUTTON_XPATH))
            )
            button.click()
            
            # Wait for URL to change
            WebDriverWait(browser, 15).until(
                lambda driver: "code=" in driver.current_url
            )
            
            # Extract key from URL
            key = self.extract_key_from_url(browser.current_url)
            
            # Clear cookies and cache
            browser.delete_all_cookies()
            browser.execute_script("window.localStorage.clear();")
            browser.execute_script("window.sessionStorage.clear();")
            
            return key
        
        except Exception as e:
            print(f"Error generating key with browser {browser_index}: {e}")
            # Recreate browser instance if there's an error
            new_browser = self.create_browser()
            if new_browser:
                self.browsers[browser_index] = new_browser
            return None
    
    def generate_keys(self, count=1):
        """Generate multiple keys using all available browsers"""
        keys = []
        browser_index = 0
        
        while len(keys) < count and len(self.browsers) > 0:
            key = self.generate_key(browser_index)
            if key:
                keys.append(key)
            
            # Move to next browser
            browser_index = (browser_index + 1) % len(self.browsers)
            
            # Small delay to prevent rate limiting
            time.sleep(1)
        
        return keys
    
    def close_all(self):
        """Close all browser instances"""
        for browser in self.browsers:
            try:
                browser.quit()
            except:
                pass
        self.browsers = [] 