"""
Human-like behavior simulation for browser automation
"""
import random
import time
import numpy as np
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import pyautogui

class HumanBehavior:
    def __init__(self, driver):
        self.driver = driver
        
    def random_delay(self, min_seconds=1, max_seconds=3):
        """Generate random delay with normal distribution"""
        mean = (min_seconds + max_seconds) / 2
        std = (max_seconds - min_seconds) / 4
        delay = np.random.normal(mean, std)
        delay = max(min_seconds, min(max_seconds, delay))  # Clamp to range
        time.sleep(delay)
        
    def typing_delay(self):
        """Simulate human typing speed"""
        # Average typing speed: 40 WPM = ~200 chars/min = ~3.3 chars/sec
        # So ~0.3 sec per char with variation
        return random.uniform(0.1, 0.4)
    
    def human_type(self, element, text):
        """Type text with human-like speed and occasional mistakes, supporting multi-line"""
        element.click()
        self.random_delay(0.5, 1)
        
        # Handle multi-line text properly
        lines = text.split('\n')
        
        for line_idx, line in enumerate(lines):
            # Type each line
            for char in line:
                # Occasionally make typos and correct them (5% chance)
                if random.random() < 0.05 and char.isalpha():
                    wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                    element.send_keys(wrong_char)
                    time.sleep(self.typing_delay())
                    element.send_keys(Keys.BACKSPACE)
                    time.sleep(self.typing_delay() * 0.5)
                
                element.send_keys(char)
                time.sleep(self.typing_delay())
                
                # Occasional pauses (10% chance)
                if random.random() < 0.1:
                    self.random_delay(0.5, 2)
            
            # Add line break if not the last line
            if line_idx < len(lines) - 1:
                element.send_keys(Keys.RETURN)
                self.random_delay(0.2, 0.5)  # Brief pause after line break
    
    def human_click(self, element):
        """Click with human-like behavior"""
        try:
            # Scroll element into view first
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            self.random_delay(0.3, 0.6)
            
            # Simple move and click with small random offset
            actions = ActionChains(self.driver)
            
            # Get element size to ensure offset is within bounds
            size = element.size
            max_offset_x = min(5, size['width'] // 4)
            max_offset_y = min(5, size['height'] // 4)
            
            x_offset = random.randint(-max_offset_x, max_offset_x)
            y_offset = random.randint(-max_offset_y, max_offset_y)
            
            actions.move_to_element_with_offset(element, x_offset, y_offset)
            self.random_delay(0.1, 0.3)
            actions.click()
            actions.perform()
        except Exception as e:
            # Fallback to simple click if move fails
            self.random_delay(0.2, 0.4)
            element.click()
        
    def move_to_element_human(self, element):
        """Move mouse to element with human-like curve"""
        actions = ActionChains(self.driver)
        
        # Get current position
        current = self.driver.execute_script("""
            return {x: window.mouseX || 0, y: window.mouseY || 0};
        """)
        
        # Get element position
        location = element.location_once_scrolled_into_view
        size = element.size
        target_x = location['x'] + size['width'] / 2
        target_y = location['y'] + size['height'] / 2
        
        # Create bezier curve path
        steps = random.randint(10, 20)
        for i in range(steps):
            progress = (i + 1) / steps
            # Add some curve to the movement
            curve = random.uniform(-20, 20) * (1 - abs(2 * progress - 1))
            x = current['x'] + (target_x - current['x']) * progress + curve
            y = current['y'] + (target_y - current['y']) * progress + curve
            
            actions.move_by_offset(x - current['x'], y - current['y'])
            current = {'x': x, 'y': y}
            
        actions.perform()
        
    def random_scroll(self):
        """Perform random scroll action"""
        scroll_amount = random.randint(100, 500)
        direction = random.choice([-1, 1])
        
        self.driver.execute_script(f"window.scrollBy(0, {scroll_amount * direction})")
        self.random_delay(0.5, 1.5)
        
    def random_mouse_movement(self):
        """Random mouse movements to appear human"""
        actions = ActionChains(self.driver)
        
        for _ in range(random.randint(1, 3)):
            x = random.randint(-100, 100)
            y = random.randint(-100, 100)
            actions.move_by_offset(x, y)
            
        actions.perform()
        
    def wait_between_actions(self):
        """Wait between major actions with variation"""
        base_wait = random.uniform(3, 8)
        
        # Sometimes take longer breaks (20% chance)
        if random.random() < 0.2:
            base_wait *= random.uniform(2, 4)
            
        time.sleep(base_wait)
        
        # Occasionally do random actions
        if random.random() < 0.3:
            self.random_mouse_movement()
        if random.random() < 0.2:
            self.random_scroll()
