"""
Browser manager with anti-detection features
"""
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from fake_useragent import UserAgent
import random
import os

class BrowserManager:
    def __init__(self, headless=False):
        self.headless = headless
        self.driver = None
        
    def create_driver(self):
        """Create undetected Chrome driver with anti-detection features"""
        
        # Use undetected-chromedriver
        options = uc.ChromeOptions()
        
        # Anti-detection arguments (basic set for compatibility)
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Randomize window size
        width = random.randint(1200, 1920)
        height = random.randint(800, 1080)
        options.add_argument(f'--window-size={width},{height}')
        
        # Language and locale
        languages = ['en-US', 'en-GB', 'en-CA', 'en-AU']
        options.add_argument(f'--lang={random.choice(languages)}')
        
        # Add preferences to avoid detection
        prefs = {
            'credentials_enable_service': False,
            'profile.password_manager_enabled': False,
            'profile.default_content_setting_values.notifications': 2
        }
        options.add_experimental_option('prefs', prefs)
        
        if self.headless:
            options.add_argument('--headless=new')  # New headless mode
            
        try:
            # Create driver with undetected-chromedriver
            self.driver = uc.Chrome(options=options)
            
            # Execute CDP commands to mask webdriver
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    // Override webdriver property
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    
                    // Override chrome property
                    window.chrome = {
                        runtime: {},
                        loadTimes: function() {},
                        csi: function() {},
                        app: {}
                    };
                    
                    // Override permissions
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters)
                    );
                    
                    // Override plugins
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    
                    // Override languages
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en']
                    });
                    
                    // Track mouse position for human-like movement
                    window.mouseX = 0;
                    window.mouseY = 0;
                    document.addEventListener('mousemove', (e) => {
                        window.mouseX = e.clientX;
                        window.mouseY = e.clientY;
                    });
                '''
            })
            
            # Set realistic timeouts
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(30)
            
            return self.driver
            
        except Exception as e:
            print(f"Error creating driver: {e}")
            raise
            
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            
    def clear_cookies(self):
        """Clear all cookies"""
        if self.driver:
            self.driver.delete_all_cookies()
            
    def save_cookies(self, filename='cookies.json'):
        """Save cookies for session persistence"""
        import json
        cookies = self.driver.get_cookies()
        with open(filename, 'w') as f:
            json.dump(cookies, f)
            
    def load_cookies(self, filename='cookies.json'):
        """Load cookies from file"""
        import json
        import os
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                cookies = json.load(f)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
                return True
        return False
