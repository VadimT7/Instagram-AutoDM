"""
Instagram automation module for sending messages
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
from human_behavior import HumanBehavior
import logging

class InstagramAutomation:
    def __init__(self, driver, config):
        self.driver = driver
        self.config = config
        self.human = HumanBehavior(driver)
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://www.instagram.com"
        
    def login(self, username, password):
        """Login to Instagram with human-like behavior"""
        try:
            self.logger.info("Navigating to Instagram login page...")
            self.driver.get(self.base_url)
            self.human.random_delay(3, 5)
            
            # Check if already logged in (quick check, no long wait)
            try:
                if self.is_logged_in(wait_time=3):
                    self.logger.info("Already logged in")
                    return True
            except:
                pass
            
            # Wait for login form
            wait = WebDriverWait(self.driver, 20)
            
            self.logger.info("Looking for username field...")
            # Find and fill username
            username_input = wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            
            # Clear field first
            username_input.clear()
            self.human.random_delay(0.3, 0.5)
            
            self.logger.info(f"Entering username: {username}")
            self.human.human_type(username_input, username)
            self.human.random_delay(1, 2)
            
            # Find and fill password
            self.logger.info("Looking for password field...")
            password_input = wait.until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            
            # Clear field first
            password_input.clear()
            self.human.random_delay(0.3, 0.5)
            
            self.logger.info("Entering password...")
            self.human.human_type(password_input, password)
            self.human.random_delay(1, 2)
            
            # Click login button - try multiple selectors
            self.logger.info("Looking for login button...")
            login_button = None
            
            button_selectors = [
                "//button[@type='submit']",
                "//button[contains(text(), 'Log in') or contains(text(), 'Log In')]",
                "//div[@role='button' and contains(text(), 'Log in')]",
                "//button[contains(@class, 'sqdOP')]"  # Instagram's login button class
            ]
            
            for selector in button_selectors:
                try:
                    login_button = wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    if login_button:
                        self.logger.info(f"Found login button with selector: {selector}")
                        break
                except:
                    continue
            
            if not login_button:
                self.logger.error("Could not find login button")
                return False
            
            # Make sure button is visible and clickable
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", login_button)
            self.human.random_delay(0.5, 1)
            
            self.logger.info("Clicking login button...")
            try:
                self.human.human_click(login_button)
            except Exception as e:
                self.logger.warning(f"Human click failed: {e}, using JavaScript click")
                # Fallback to JavaScript click
                self.driver.execute_script("arguments[0].click();", login_button)
                self.human.random_delay(0.3, 0.6)
            
            # Wait for login to complete - give it more time
            self.logger.info("Waiting for login to complete...")
            self.human.random_delay(8, 12)
            
            # Check for security challenges
            try:
                if "challenge" in self.driver.current_url or "checkpoint" in self.driver.current_url:
                    self.logger.warning("⚠ Instagram security challenge detected!")
                    self.logger.warning("Please complete the verification manually in the browser.")
                    self.logger.warning("Waiting 60 seconds for manual verification...")
                    time.sleep(60)
            except:
                pass
            
            # Handle common popups after login
            self.logger.info("Checking for post-login popups...")
            popup_handled = False
            
            # Try to handle "Save Your Login Info?" prompt
            try:
                wait_short = WebDriverWait(self.driver, 5)
                not_now_button = wait_short.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now') or contains(text(), 'Not now')]"))
                )
                self.logger.info("Found 'Save Login Info' popup, dismissing...")
                not_now_button.click()
                self.human.random_delay(2, 3)
                popup_handled = True
            except:
                pass
            
            # Try to handle "Turn on Notifications" prompt
            try:
                wait_short = WebDriverWait(self.driver, 5)
                not_now_button = wait_short.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now') or contains(text(), 'Not now')]"))
                )
                self.logger.info("Found 'Notifications' popup, dismissing...")
                not_now_button.click()
                self.human.random_delay(2, 3)
                popup_handled = True
            except:
                pass
            
            # Verify login
            self.logger.info("Verifying login status...")
            if self.is_logged_in(wait_time=20):
                self.logger.info("✓ Login successful!")
                return True
            else:
                self.logger.error("✗ Login verification failed - checking current URL and page state")
                self.logger.error(f"Current URL: {self.driver.current_url}")
                
                # Take screenshot for debugging
                try:
                    self.driver.save_screenshot("login_failed_debug.png")
                    self.logger.info("Screenshot saved to login_failed_debug.png")
                except:
                    pass
                
                return False
                
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return False
    
    def is_logged_in(self, wait_time=15):
        """Check if user is logged in"""
        try:
            # First quick check - if on login page, definitely not logged in
            current_url = self.driver.current_url
            if '/accounts/login' in current_url or current_url == 'https://www.instagram.com/':
                # Check if login form exists
                try:
                    login_form = self.driver.find_element(By.NAME, "username")
                    if login_form:
                        return False  # Login form present = not logged in
                except:
                    pass
            
            wait = WebDriverWait(self.driver, wait_time)
            
            # Multiple indicators that user is logged in
            login_indicators = [
                (By.XPATH, "//svg[@aria-label='Home']"),
                (By.XPATH, "//a[@href='/'][@aria-label='Home']"),
                (By.XPATH, "//a[contains(@href, '/direct/inbox')]"),
                (By.XPATH, "//svg[@aria-label='New post']"),
                (By.XPATH, "//span[contains(text(), 'Search')]"),
                (By.XPATH, "//a[@href='#']//span[text()='Home']")
            ]
            
            for locator_type, locator_value in login_indicators:
                try:
                    element = wait.until(
                        EC.presence_of_element_located((locator_type, locator_value))
                    )
                    if element:
                        self.logger.info(f"Login verified: found element {locator_value}")
                        return True
                except:
                    continue
            
            # If no indicator found, check URL
            if '/accounts/login' not in self.driver.current_url:
                self.logger.info("Login verified: not on login page")
                return True
                
            return False
        except Exception as e:
            self.logger.error(f"Error checking login status: {e}")
            return False
    
    def navigate_to_profile(self, profile_url):
        """Navigate to a user profile"""
        try:
            self.logger.info(f"Navigating to profile: {profile_url}")
            
            # Random delay before navigation
            self.human.wait_between_actions()
            
            self.driver.get(profile_url)
            self.human.random_delay(3, 5)
            
            # Check if profile loaded
            wait = WebDriverWait(self.driver, 15)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "header")))
            
            # Random scroll to appear natural
            if random.random() < 0.6:
                self.human.random_scroll()
                self.human.random_delay(1, 3)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error navigating to profile: {e}")
            return False
    
    def check_rate_limit_popup(self):
        """Check for and handle Instagram rate limit popup"""
        try:
            # Look for "Try again later" popup
            popup_texts = [
                "Try again later",
                "Try Again Later",
                "We limit how often you can do certain things",
                "too many requests"
            ]
            
            for text in popup_texts:
                elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
                if elements:
                    self.logger.warning("⚠️ Instagram rate limit detected!")
                    
                    # Try to click "OK" button to dismiss
                    try:
                        ok_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'OK') or contains(text(), 'Ok')]")
                        ok_button.click()
                        self.logger.info("Dismissed rate limit popup")
                        time.sleep(2)
                    except:
                        pass
                    
                    return True
            
            return False
            
        except Exception as e:
            return False
    
    def follow_profile(self):
        """Follow the profile if not already following - bulletproof method"""
        try:
            # Check if following is enabled in config
            if not self.config.ENABLE_FOLLOW:
                self.logger.info("Following disabled in config - skipping")
                return False
            
            # Wait for page to load
            time.sleep(2)
            self.logger.info("Looking for Follow button...")
            
            # First find the button
            follow_button = self.driver.execute_script("""
                var elements = document.querySelectorAll('*');
                for (var elem of elements) {
                    var text = elem.textContent.trim();
                    if (text === 'Follow' && elem.offsetWidth > 0 && elem.offsetHeight > 0) {
                        // Check if it's a button-like element
                        var tagName = elem.tagName.toLowerCase();
                        var role = elem.getAttribute('role');
                        if (tagName === 'button' || tagName === 'div' || role === 'button') {
                            // Check it's not "Following" or "Follow Back"
                            if (!elem.textContent.includes('Following') && !elem.textContent.includes('Back')) {
                                var rect = elem.getBoundingClientRect();
                                if (rect.top > 100) {  // Below header
                                    return elem;
                                }
                            }
                        }
                    }
                }
                return null;
            """)
            
            if not follow_button:
                self.logger.info("Follow button not found - may already be following")
                return False
            
            # Scroll into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", follow_button)
            time.sleep(0.5)  # Wait for scroll
            
            # Check if the button is actually clickable
            is_enabled = self.driver.execute_script("return !arguments[0].disabled && arguments[0].offsetParent !== null;", follow_button)
            if not is_enabled:
                self.logger.warning("Follow button found but not clickable")
                return False
            
            # Try multiple click methods
            try:
                # Method 1: Use Action Chains
                from selenium.webdriver.common.action_chains import ActionChains
                actions = ActionChains(self.driver)
                actions.move_to_element(follow_button).click().perform()
                self.logger.info("✓ Clicked Follow button with ActionChains")
            except Exception as e:
                self.logger.debug(f"ActionChains failed: {e}")
                # Method 2: JavaScript clicks with multiple event types
                self.driver.execute_script("""
                    var elem = arguments[0];
                    
                    // Regular click
                    elem.click();
                    
                    // MouseEvent click
                    var clickEvent = new MouseEvent('click', {
                        view: window,
                        bubbles: true,
                        cancelable: true,
                        buttons: 1
                    });
                    elem.dispatchEvent(clickEvent);
                    
                    // Pointer events
                    var pointerDown = new PointerEvent('pointerdown', {
                        bubbles: true,
                        cancelable: true,
                        view: window,
                        button: 0,
                        buttons: 1
                    });
                    var pointerUp = new PointerEvent('pointerup', {
                        bubbles: true,
                        cancelable: true,
                        view: window,
                        button: 0,
                        buttons: 0
                    });
                    elem.dispatchEvent(pointerDown);
                    elem.dispatchEvent(pointerUp);
                """, follow_button)
                self.logger.info("✓ Clicked Follow button with JavaScript")
            
            # Wait and check for rate limit popup
            self.human.random_delay(2, 3)
            
            # Check if Instagram blocked the follow action
            if self.check_rate_limit_popup():
                self.logger.warning("⚠️ Instagram follow rate limit reached - disabling follows for this session")
                # Disable following for the rest of the session
                self.config.ENABLE_FOLLOW = False
                return False
            
            return True
                
        except Exception as e:
            self.logger.warning(f"Error following profile: {e}")
            # Check for rate limit popup even on error
            self.check_rate_limit_popup()
            return False
    
    def click_message_button(self):
        """Find and click the Message button on the profile page - bulletproof method"""
        try:
            # Wait for page to fully load
            time.sleep(3)
            self.logger.info("Looking for Message button...")
            
            # First find the button
            message_button = self.driver.execute_script("""
                var elements = document.querySelectorAll('*');
                for (var elem of elements) {
                    // Check for exact "Message" text
                    if (elem.textContent.trim() === 'Message' && 
                        elem.offsetWidth > 0 && elem.offsetHeight > 0) {
                        // Check if it's a clickable element
                        var tagName = elem.tagName.toLowerCase();
                        var role = elem.getAttribute('role');
                        if (tagName === 'button' || tagName === 'div' || role === 'button') {
                            // Check position (not in header/nav)
                            var rect = elem.getBoundingClientRect();
                            if (rect.top > 100) {  // Below header
                                return elem;
                            }
                        }
                    }
                }
                return null;
            """)
            
            if not message_button:
                self.logger.error("Message button not found on profile")
                return False
            
            # Scroll into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", message_button)
            time.sleep(0.5)  # Wait for scroll
            
            # Check if the button is actually clickable
            is_enabled = self.driver.execute_script("return !arguments[0].disabled && arguments[0].offsetParent !== null;", message_button)
            if not is_enabled:
                self.logger.warning("Message button found but not clickable")
                return False
            
            # Now try multiple click methods
            try:
                # Method 1: Use Action Chains with forced click
                from selenium.webdriver.common.action_chains import ActionChains
                actions = ActionChains(self.driver)
                actions.move_to_element(message_button).click().perform()
                self.logger.info("✓ Clicked Message button with ActionChains")
            except Exception as e:
                self.logger.debug(f"ActionChains failed: {e}")
                # Method 2: JavaScript clicks with multiple event types
                self.driver.execute_script("""
                    var elem = arguments[0];
                    
                    // Regular click
                    elem.click();
                    
                    // MouseEvent click
                    var clickEvent = new MouseEvent('click', {
                        view: window,
                        bubbles: true,
                        cancelable: true,
                        buttons: 1
                    });
                    elem.dispatchEvent(clickEvent);
                    
                    // Pointer events
                    var pointerDown = new PointerEvent('pointerdown', {
                        bubbles: true,
                        cancelable: true,
                        view: window,
                        button: 0,
                        buttons: 1
                    });
                    var pointerUp = new PointerEvent('pointerup', {
                        bubbles: true,
                        cancelable: true,
                        view: window,
                        button: 0,
                        buttons: 0
                    });
                    elem.dispatchEvent(pointerDown);
                    elem.dispatchEvent(pointerUp);
                    
                    // Touch events for mobile simulation
                    if (window.TouchEvent) {
                        var touch = new Touch({
                            identifier: Date.now(),
                            target: elem,
                            clientX: elem.getBoundingClientRect().left + 10,
                            clientY: elem.getBoundingClientRect().top + 10,
                            screenX: elem.getBoundingClientRect().left + 10,
                            screenY: elem.getBoundingClientRect().top + 10,
                            pageX: elem.getBoundingClientRect().left + 10,
                            pageY: elem.getBoundingClientRect().top + 10,
                        });
                        var touchStart = new TouchEvent('touchstart', {
                            cancelable: true,
                            bubbles: true,
                            touches: [touch],
                            targetTouches: [touch],
                            changedTouches: [touch]
                        });
                        var touchEnd = new TouchEvent('touchend', {
                            cancelable: true,
                            bubbles: true,
                            touches: [],
                            targetTouches: [],
                            changedTouches: [touch]
                        });
                        elem.dispatchEvent(touchStart);
                        elem.dispatchEvent(touchEnd);
                    }
                """, message_button)
                self.logger.info("✓ Clicked Message button with JavaScript")
            
            # Wait for navigation/modal
            time.sleep(2)
            return True
            
        except Exception as e:
            self.logger.error(f"Error clicking message button: {e}")
            return False
    
    def send_message(self, message_text):
        """Send a message in the chat window"""
        try:
            wait = WebDriverWait(self.driver, 15)
            
            # Wait for message input field
            self.human.random_delay(2, 4)
            
            # Try different selectors for the message input
            input_selectors = [
                "//textarea[@placeholder='Message...']",
                "//textarea[contains(@placeholder, 'Message')]",
                "//div[@role='textbox']",
                "//div[@contenteditable='true']"
            ]
            
            message_input = None
            for selector in input_selectors:
                try:
                    message_input = wait.until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    if message_input:
                        break
                except:
                    continue
            
            if not message_input:
                self.logger.error("Message input field not found")
                return False
            
            # Click on the input field
            try:
                self.human.human_click(message_input)
            except:
                message_input.click()
            self.human.random_delay(0.5, 1)
            
            # Type the message with human-like behavior
            self.human.human_type(message_input, message_text)
            
            # Random delay before sending
            self.human.random_delay(1, 3)
            
            # Find and click send button
            send_selectors = [
                "//button[contains(text(), 'Send')]",
                "//button[@type='button'][contains(., 'Send')]",
                "//div[contains(@aria-label, 'Send')]",
                "//button[contains(@aria-label, 'Send')]"
            ]
            
            send_button = None
            for selector in send_selectors:
                try:
                    send_button = self.driver.find_element(By.XPATH, selector)
                    if send_button:
                        self.logger.info(f"Found send button with: {selector}")
                        break
                except:
                    continue
            
            if send_button:
                try:
                    self.human.human_click(send_button)
                except Exception as e:
                    self.logger.warning(f"Human click on send failed: {e}, using JavaScript")
                    self.driver.execute_script("arguments[0].click();", send_button)
            else:
                # Try pressing Enter if send button not found
                self.logger.info("Send button not found, using Enter key")
                from selenium.webdriver.common.keys import Keys
                message_input.send_keys(Keys.RETURN)
            
            self.logger.info(f"Message sent: {message_text[:50]}...")
            
            # Check for rate limit popup after sending
            time.sleep(2)
            if self.check_rate_limit_popup():
                self.logger.warning("⚠️ Instagram message rate limit detected after send")
                return True  # Message was sent, but we're now rate limited
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            # Check for rate limit even on error
            self.check_rate_limit_popup()
            return False
    
    def check_for_blocks(self):
        """Check if account is blocked or rate limited"""
        try:
            # Check for common block/restriction messages
            block_indicators = [
                "Try Again Later",
                "We restrict certain activity",
                "Action Blocked",
                "temporarily blocked",
                "Please wait a few minutes"
            ]
            
            page_source = self.driver.page_source
            for indicator in block_indicators:
                if indicator.lower() in page_source.lower():
                    self.logger.warning(f"Possible restriction detected: {indicator}")
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking for blocks: {e}")
            return False
    
    def handle_popups(self):
        """Handle any popups that might appear"""
        try:
            # Common popup dismissal buttons
            popup_selectors = [
                "//button[contains(text(), 'Not Now')]",
                "//button[contains(text(), 'Cancel')]",
                "//button[contains(text(), 'OK')]",
                "//button[@aria-label='Close']"
            ]
            
            for selector in popup_selectors:
                try:
                    popup_button = self.driver.find_element(By.XPATH, selector)
                    if popup_button.is_displayed():
                        self.human.human_click(popup_button)
                        self.human.random_delay(1, 2)
                        return True
                except:
                    continue
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Error handling popups: {e}")
            return False
