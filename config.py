"""
Configuration settings for Instagram automation
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Instagram credentials (use environment variables for security)
    INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME", "")
    INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD", "")
    
    # Message settings
    DEFAULT_MESSAGE = """Hey,
Love the cars in your line-up - awesome machines! 

A close friend told me about your rental company. 
I just checked your Instagram and, man, you're losing money without a site that generates you bookings.  

So, I created a live website w/ your cars for you. I can send you the link and, if you like it, we can work together. If no, no problem.

Reply "yes" to this message if you want to see your new luxurious website, tailored just to your rental company."""
    
    # Timing settings (in seconds) - optimized for speed
    MIN_DELAY_BETWEEN_MESSAGES = 15  # Minimum delay between messages (faster)
    MAX_DELAY_BETWEEN_MESSAGES = 45  # Maximum delay between messages (faster)
    
    # Session settings - increased throughput
    MESSAGES_PER_SESSION = 20  # Max messages to send per session (doubled)
    SESSION_BREAK_MIN = 300  # Minimum break between sessions (5 minutes)
    SESSION_BREAK_MAX = 600  # Maximum break between sessions (10 minutes)
    
    # Daily limits (to avoid detection) - increased for production
    DAILY_MESSAGE_LIMIT = 200  # Increased daily limit
    
    # Browser settings
    HEADLESS_MODE = False  # Set to True to run browser in background (default for server deployment)
    
    # Retry settings
    MAX_RETRIES = 2  # Total attempts = 2 (1 initial + 1 retry)
    RETRY_DELAY = 30  # Delay before retrying failed profile (seconds)
    
    # Anti-detection settings
    ENABLE_RANDOM_ACTIONS = True  # Enable random human-like actions
    RANDOM_ACTION_PROBABILITY = 0.3  # Probability of random actions
    
    # File paths
    CSV_FILE = "InstagramProfiles.csv"
    LOG_FILE = "instagram_automation.log"
    COOKIES_FILE = "instagram_cookies.json"
    
    # Feature flags
    SAVE_COOKIES = False  # Save cookies for session persistence (DISABLED - fresh login each time)
    USE_SAVED_COOKIES = False  # Try to use saved cookies for login (DISABLED - fresh login each time)
    CHECK_FOR_BLOCKS = True  # Check for account blocks/restrictions
    
    # Advanced settings
    PAGE_LOAD_TIMEOUT = 30
    ELEMENT_WAIT_TIMEOUT = 15
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.INSTAGRAM_USERNAME or not cls.INSTAGRAM_PASSWORD:
            print("Warning: Instagram credentials not set in environment variables")
            print("Please create a .env file with INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD")
            return False
        return True
    
    @classmethod
    def get_message_variations(cls):
        """Get message variations for more natural messaging"""
        # Return only the main message, no fallbacks
        return [cls.DEFAULT_MESSAGE]
