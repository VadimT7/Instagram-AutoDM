"""
Main Instagram DM Automation System
"""
import sys
import time
import random
import logging
from datetime import datetime, timedelta
from colorama import init, Fore, Style
import signal
import json
import os

from browser_manager import BrowserManager
from instagram_automation import InstagramAutomation
from csv_processor import CSVProcessor
from config import Config

# Initialize colorama for colored output
init(autoreset=True)

class InstagramDMAutomation:
    def __init__(self, setup_signal_handler=True, step_filter=None, use_flow=False):
        self.setup_logging()
        self.browser_manager = None
        self.driver = None
        self.instagram = None
        self.csv_processor = CSVProcessor(Config.CSV_FILE)
        self.daily_message_count = 0
        self.session_message_count = 0
        self.last_reset_date = datetime.now().date()
        self.running = True
        self.step_filter = step_filter  # Filter for specific flow step
        self.use_flow = use_flow  # Use flow system with database
        self.db = self.csv_processor.db  # Database access
        
        # Setup signal handler for graceful shutdown (only in main thread)
        if setup_signal_handler:
            try:
                signal.signal(signal.SIGINT, self.signal_handler)
            except ValueError:
                # Signal only works in main thread, ignore if in background thread
                pass
        
    def setup_logging(self):
        """Setup logging configuration"""
        self.logger = logging.getLogger(__name__)
        
        # Only configure if not already configured
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            
            # File handler
            file_handler = logging.FileHandler(Config.LOG_FILE)
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            self.logger.addHandler(file_handler)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            self.logger.addHandler(console_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signal"""
        print(f"\n{Fore.YELLOW}Received shutdown signal. Cleaning up...{Style.RESET_ALL}")
        self.running = False
        self.cleanup()
        sys.exit(0)
    
    def print_banner(self):
        """Print application banner"""
        print(f"""
{Fore.CYAN}===============================================
     Instagram DM Automation System
           Undetectable Edition
==============================================={Style.RESET_ALL}
        """)
    
    def print_status(self, message, status="info"):
        """Print colored status messages"""
        colors = {
            "info": Fore.BLUE,
            "success": Fore.GREEN,
            "warning": Fore.YELLOW,
            "error": Fore.RED
        }
        color = colors.get(status, Fore.WHITE)
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{Fore.LIGHTBLACK_EX}[{timestamp}]{Style.RESET_ALL} {color}{message}{Style.RESET_ALL}")
    
    def initialize_browser(self):
        """Initialize browser with anti-detection features"""
        try:
            self.print_status("Initializing browser with anti-detection features...", "info")
            self.browser_manager = BrowserManager(headless=Config.HEADLESS_MODE)
            self.driver = self.browser_manager.create_driver()
            self.instagram = InstagramAutomation(self.driver, Config)
            self.print_status("Browser initialized successfully", "success")
            return True
        except Exception as e:
            self.print_status(f"Failed to initialize browser: {e}", "error")
            return False
    
    def login_to_instagram(self):
        """Login to Instagram"""
        try:
            # Try to use saved cookies first
            if Config.USE_SAVED_COOKIES and os.path.exists(Config.COOKIES_FILE):
                self.print_status("Attempting to use saved session...", "info")
                self.driver.get("https://www.instagram.com")
                time.sleep(3)
                
                if self.browser_manager.load_cookies(Config.COOKIES_FILE):
                    self.driver.refresh()
                    time.sleep(5)
                    
                    if self.instagram.is_logged_in():
                        self.print_status("Logged in using saved session", "success")
                        return True
            
            # Manual login
            self.print_status("Logging in to Instagram...", "info")
            
            if not Config.validate():
                username = input("Enter Instagram username: ")
                password = input("Enter Instagram password: ")
            else:
                username = Config.INSTAGRAM_USERNAME
                password = Config.INSTAGRAM_PASSWORD
            
            if self.instagram.login(username, password):
                self.print_status("Login successful", "success")
                
                # Save cookies for future sessions
                if Config.SAVE_COOKIES:
                    self.browser_manager.save_cookies(Config.COOKIES_FILE)
                    self.print_status("Session saved for future use", "info")
                
                return True
            else:
                self.print_status("Login failed", "error")
                return False
                
        except Exception as e:
            self.print_status(f"Login error: {e}", "error")
            return False
    
    def check_daily_limit(self):
        """Check and reset daily message limit"""
        current_date = datetime.now().date()
        
        # Reset counter if it's a new day
        if current_date > self.last_reset_date:
            self.daily_message_count = 0
            self.last_reset_date = current_date
            self.print_status("Daily message counter reset", "info")
        
        # Check if daily limit reached
        if self.daily_message_count >= Config.DAILY_MESSAGE_LIMIT:
            self.print_status(f"Daily message limit reached ({Config.DAILY_MESSAGE_LIMIT})", "warning")
            return False
        
        return True
    
    def get_random_delay(self):
        """Get random delay between messages with human-like variation"""
        base_delay = random.uniform(
            Config.MIN_DELAY_BETWEEN_MESSAGES,
            Config.MAX_DELAY_BETWEEN_MESSAGES
        )
        
        # Sometimes take longer breaks (20% chance)
        if random.random() < 0.2:
            base_delay *= random.uniform(1.5, 3)
        
        return base_delay
    
    def process_profile(self, profile_url, profile_data=None):
        """Process a single Instagram profile"""
        try:
            self.print_status(f"Processing: {profile_url}", "info")
            
            # Navigate to profile
            if not self.instagram.navigate_to_profile(profile_url):
                error_msg = "Failed to navigate to profile"
                self.print_status(error_msg, "error")
                self.csv_processor.mark_profile_processed(
                    profile_url, "failed", error_msg, 
                    error_type=self.csv_processor.categorize_error(error_msg)
                )
                return False
            
            # Random delay to seem natural
            time.sleep(random.uniform(2, 5))
            
            # Follow the profile first (only on first contact if enabled)
            if Config.ENABLE_FOLLOW and (not profile_data or profile_data.get('current_step', 0) <= 1):
                self.print_status("Attempting to follow profile...", "info")
                follow_result = self.instagram.follow_profile()
                
                if not follow_result and not Config.ENABLE_FOLLOW:
                    # Rate limit detected and following was disabled
                    self.print_status("Following disabled due to Instagram rate limit", "warning")
                
                # Random delay after following (or after skip)
                time.sleep(random.uniform(1, 3))
            elif not Config.ENABLE_FOLLOW:
                self.print_status("Following disabled - skipping to message", "info")
            
            # Click message button (on the profile, not sidebar)
            self.print_status("Looking for Message button on profile...", "info")
            if not self.instagram.click_message_button():
                error_msg = "Message button not found on profile"
                self.print_status(error_msg, "warning")
                self.instagram.handle_popups()
                self.csv_processor.mark_profile_processed(
                    profile_url, "failed", error_msg,
                    error_type=self.csv_processor.categorize_error(error_msg)
                )
                return False
            
            # Wait for message window to open
            time.sleep(random.uniform(3, 6))
            
            # Get message text based on flow step or default
            if self.use_flow and profile_data:
                # Get template for the current step
                current_step = profile_data.get('current_step', 0)
                next_step = current_step + 1 if current_step == 0 else current_step
                
                template = self.db.get_template_for_step(next_step)
                if template:
                    message_text = template['message_content']
                    self.print_status(f"Using template for step {next_step}", "info")
                else:
                    # Fall back to default
                    message_text = Config.DEFAULT_MESSAGE
                    self.print_status(f"No template for step {next_step}, using default", "warning")
            else:
                # Original behavior - use variations
                if random.random() < 0.3:  # 30% chance of variation
                    messages = Config.get_message_variations()
                    message_text = random.choice(messages)
                else:
                    message_text = Config.DEFAULT_MESSAGE
            
            # Send message
            if not self.instagram.send_message(message_text):
                error_msg = "Failed to send message - input field not found"
                self.print_status(error_msg, "error")
                self.csv_processor.mark_profile_processed(
                    profile_url, "failed", error_msg,
                    error_type=self.csv_processor.categorize_error(error_msg)
                )
                return False
            
            self.print_status(f"Message sent successfully!", "success")
            
            # Update database if using flow
            if self.use_flow and profile_data:
                profile_id = profile_data.get('id')
                if profile_id:
                    # Update to next step
                    current_step = profile_data.get('current_step', 0)
                    next_step = current_step + 1 if current_step == 0 else current_step
                    wait_days = template.get('wait_days_before_next', 3) if 'template' in locals() else 3
                    self.db.update_profile_step(profile_id, next_step, message_text, wait_days)
                    self.print_status(f"Profile updated to step {next_step}", "info")
            
            # Update counters
            self.daily_message_count += 1
            self.session_message_count += 1
            
            # Mark profile as processed
            self.csv_processor.mark_profile_processed(profile_url, "success", message_text)
            
            return True
            
        except Exception as e:
            error_msg = str(e)
            error_type = self.csv_processor.categorize_error(error_msg)
            self.logger.error(f"Error processing profile {profile_url}: {error_msg}")
            
            # Update database if using flow system
            if self.use_flow and profile_data:
                profile_id = profile_data.get('id')
                if profile_id:
                    self.db.update_profile_failure(profile_id, error_type, error_msg)
                    retry_count = profile_data.get('retry_count', 0) + 1
                    self.print_status(f"Profile failed (attempt {retry_count}/3): {error_type}", "warning")
            
            # Also update CSV processor for legacy compatibility
            self.csv_processor.mark_profile_processed(
                profile_url, "failed", error_msg,
                error_type=error_type
            )
            return False
    
    def take_session_break(self):
        """Take a break between sessions"""
        break_time = random.uniform(Config.SESSION_BREAK_MIN, Config.SESSION_BREAK_MAX)
        self.print_status(f"Taking session break for {break_time/60:.1f} minutes...", "warning")
        
        # Show countdown
        end_time = datetime.now() + timedelta(seconds=break_time)
        while datetime.now() < end_time and self.running:
            remaining = (end_time - datetime.now()).total_seconds()
            print(f"\rTime remaining: {remaining/60:.1f} minutes", end="", flush=True)
            time.sleep(10)
        
        print()  # New line after countdown
    
    def run_automation(self):
        """Main automation loop"""
        try:
            # Check if we're using flow system
            if self.use_flow and hasattr(self, 'db'):
                self.print_status(f"Using flow system with step filter: {self.step_filter}", "info")
                
                # Use database profiles for flow system
                profiles_data = self.db.get_profiles_by_step(self.step_filter)
                
                self.print_status(f"Database query returned {len(profiles_data)} profiles", "info")
                
                if not profiles_data:
                    self.print_status(f"No profiles found at step {self.step_filter}", "warning")
                    return
                
                # Count failed profiles for retry
                failed_count = sum(1 for p in profiles_data if p['status'] == 'failed')
                new_count = len(profiles_data) - failed_count
                
                if failed_count > 0:
                    self.print_status(f"Found {new_count} new profiles + {failed_count} failed profiles for retry", "info")
                else:
                    self.print_status(f"Found {len(profiles_data)} new profiles", "info")
                
                # Convert to format expected by automation
                profiles = []
                for profile_data in profiles_data:
                    profile_url = f"https://www.instagram.com/{profile_data['username']}/"
                    profiles.append((profile_url, profile_data))
                
                self.print_status(f"Processing {len(profiles)} profiles at step {self.step_filter}", "info")
            else:
                # Use CSV file (legacy mode)
                if not self.csv_processor.load_csv():
                    self.print_status("Failed to load CSV file", "error")
                    return
                
                # Get unprocessed profiles
                profiles = self.csv_processor.get_unprocessed_profiles()
                
                if not profiles:
                    self.print_status("No unprocessed profiles found", "warning")
                    return
                
                # Convert to format expected by automation
                profiles = [(profile_url, None) for profile_url in profiles]
            
            # Initialize browser and login
            if not self.initialize_browser():
                return
            
            if not self.login_to_instagram():
                return
            
            # Process profiles
            for i, profile_info in enumerate(profiles):
                if not self.running:
                    break
                
                # Extract profile URL and data
                if isinstance(profile_info, tuple):
                    profile_url, profile_data = profile_info
                else:
                    profile_url = profile_info
                    profile_data = None
                
                # Check daily limit
                if not self.check_daily_limit():
                    self.print_status("Daily limit reached. Please run again tomorrow.", "warning")
                    break
                
                # Check for account blocks
                if Config.CHECK_FOR_BLOCKS and self.instagram.check_for_blocks():
                    self.print_status("Account restriction detected. Stopping automation.", "error")
                    break
                
                # Process profile
                retry_info = ""
                if profile_data and profile_data.get('status') == 'failed':
                    retry_count = profile_data.get('retry_count', 0)
                    retry_info = f" (retry {retry_count + 1}/4)"
                
                self.print_status(f"Processing profile {i+1}/{len(profiles)}{retry_info}", "info")
                
                success = False
                for retry in range(Config.MAX_RETRIES):
                    if self.process_profile(profile_url, profile_data):
                        success = True
                        break
                    else:
                        if retry < Config.MAX_RETRIES - 1:
                            self.print_status(f"Retrying... ({retry+2}/{Config.MAX_RETRIES})", "warning")
                            time.sleep(Config.RETRY_DELAY)
                
                if not success:
                    self.print_status(f"Failed to process profile after {Config.MAX_RETRIES} attempts", "error")
                    self.print_status("Moving to next profile...", "info")
                
                # Check session limit
                if self.session_message_count >= Config.MESSAGES_PER_SESSION:
                    self.print_status(f"Session limit reached ({Config.MESSAGES_PER_SESSION} messages)", "info")
                    
                    # Take a break if more profiles remain
                    if i < len(profiles) - 1:
                        self.take_session_break()
                        self.session_message_count = 0
                
                # Random delay between messages
                if i < len(profiles) - 1:  # Don't delay after last profile
                    delay = self.get_random_delay()
                    self.print_status(f"Waiting {delay:.0f} seconds before next message...", "info")
                    time.sleep(delay)
            
            # Print final statistics
            self.print_statistics()
            
        except Exception as e:
            self.logger.error(f"Automation error: {e}")
            self.print_status(f"Automation error: {e}", "error")
        finally:
            self.cleanup()
    
    def print_statistics(self):
        """Print automation statistics"""
        stats = self.csv_processor.get_statistics()
        
        print(f"""
{Fore.CYAN}===============================================
           Automation Statistics
==============================================={Style.RESET_ALL}
{Fore.GREEN}[OK] Successful: {stats['successful']}{Style.RESET_ALL}
{Fore.RED}[X] Failed: {stats['failed']}{Style.RESET_ALL}
{Fore.YELLOW}[!] Remaining: {stats['remaining']}{Style.RESET_ALL}
{Fore.BLUE}[-] Total: {stats['total']}{Style.RESET_ALL}
        """)
        
        # Export report
        self.csv_processor.export_report()
        self.print_status("Report exported to message_report.csv", "success")
        
        # Export separate CSV files for successful and unsuccessful sends
        success_file, fail_file = self.csv_processor.export_last_run_results()
        if success_file:
            self.print_status(f"Successful sends exported to {success_file}", "success")
        if fail_file:
            self.print_status(f"Unsuccessful sends exported to {fail_file}", "warning")
        
        # Export detailed failure analysis report if there are failures
        if stats['failed'] > 0:
            print()  # Add spacing
            failure_reports = self.csv_processor.export_detailed_failure_report()
            if failure_reports:
                detailed_file, summary_file = failure_reports
                self.print_status("Detailed failure analysis completed", "success")
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.browser_manager:
                self.print_status("Closing browser...", "info")
                self.browser_manager.close()
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")

def main():
    """Main entry point"""
    automation = InstagramDMAutomation()
    automation.print_banner()
    
    print(f"{Fore.YELLOW}[!] DISCLAIMER:{Style.RESET_ALL}")
    print("This tool is for educational purposes only.")
    print("Using automation on Instagram may violate their Terms of Service.")
    print("Use at your own risk and ensure compliance with all applicable laws.\n")
    
    response = input("Do you want to continue? (yes/no): ").lower()
    
    if response == 'yes':
        automation.run_automation()
    else:
        print("Automation cancelled.")

if __name__ == "__main__":
    main()
