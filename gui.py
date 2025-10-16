"""
Instagram DM Automation - Graphical User Interface
"""
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import threading
import queue
import sys
import io
from datetime import datetime
import os

from browser_manager import BrowserManager
from instagram_automation import InstagramAutomation
from csv_processor import CSVProcessor
from config import Config
import logging

class TextRedirector(io.StringIO):
    """Redirect text output to GUI"""
    def __init__(self, text_widget, tag="stdout"):
        super().__init__()
        self.text_widget = text_widget
        self.tag = tag

    def write(self, string):
        if string.strip():  # Only write non-empty strings
            self.text_widget.insert(tk.END, string, self.tag)
            self.text_widget.see(tk.END)
            self.text_widget.update_idletasks()

    def flush(self):
        pass

class InstagramDMGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram DM Automation - Undetectable Edition")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Set icon (if available)
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        
        # Variables
        self.csv_file_path = tk.StringVar(value="InstagramProfiles.csv")
        self.instagram_username = tk.StringVar(value=Config.INSTAGRAM_USERNAME)
        self.instagram_password = tk.StringVar(value=Config.INSTAGRAM_PASSWORD)
        self.message_text = tk.StringVar(value=Config.DEFAULT_MESSAGE)
        self.input_mode = tk.StringVar(value="file")  # "file" or "direct"
        
        # Automation state
        self.is_running = False
        self.automation_thread = None
        self.automation_instance = None
        self.browser_manager = None
        self.driver = None
        
        # Setup UI
        self.setup_styles()
        self.create_widgets()
        
        # Setup logging redirect
        self.setup_logging()
        
    def setup_styles(self):
        """Setup custom styles for widgets"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        bg_color = "#f0f0f0"
        accent_color = "#0084ff"
        
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground=accent_color)
        style.configure('Heading.TLabel', font=('Segoe UI', 11, 'bold'))
        style.configure('TButton', padding=6, font=('Segoe UI', 10))
        style.configure('Start.TButton', foreground='white', background='#4CAF50', font=('Segoe UI', 11, 'bold'))
        style.configure('Stop.TButton', foreground='white', background='#f44336', font=('Segoe UI', 11, 'bold'))
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Instagram DM Automation System", style='Title.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 10), sticky=tk.W)
        
        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Tab 1: Input
        input_frame = ttk.Frame(notebook, padding="10")
        notebook.add(input_frame, text="Input")
        self.create_input_tab(input_frame)
        
        # Tab 2: Settings
        settings_frame = ttk.Frame(notebook, padding="10")
        notebook.add(settings_frame, text="Settings")
        self.create_settings_tab(settings_frame)
        
        # Tab 3: Advanced
        advanced_frame = ttk.Frame(notebook, padding="10")
        notebook.add(advanced_frame, text="Advanced")
        self.create_advanced_tab(advanced_frame)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, pady=10, sticky=(tk.W, tk.E))
        
        self.start_button = ttk.Button(control_frame, text="▶ Start Automation", 
                                       command=self.start_automation, style='Start.TButton')
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="■ Stop", 
                                      command=self.stop_automation, state=tk.DISABLED, 
                                      style='Stop.TButton')
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="5")
        progress_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.StringVar(value="Ready to start...")
        progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        progress_label.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Statistics
        stats_frame = ttk.Frame(progress_frame)
        stats_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        self.stats_label = ttk.Label(stats_frame, text="Processed: 0 | Success: 0 | Failed: 0")
        self.stats_label.pack(side=tk.LEFT)
        
        # Log output
        log_frame = ttk.LabelFrame(main_frame, text="Log Output", padding="5")
        log_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, wrap=tk.WORD, 
                                                   font=('Consolas', 9), bg='#1e1e1e', 
                                                   fg='#d4d4d4', insertbackground='white')
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure text tags for colors
        self.log_text.tag_config("INFO", foreground="#4CAF50")
        self.log_text.tag_config("WARNING", foreground="#FFC107")
        self.log_text.tag_config("ERROR", foreground="#f44336")
        self.log_text.tag_config("SUCCESS", foreground="#00E676")
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
    def create_input_tab(self, parent):
        """Create input tab widgets"""
        parent.columnconfigure(1, weight=1)
        
        # Input mode selection
        mode_frame = ttk.LabelFrame(parent, text="Input Mode", padding="10")
        mode_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Radiobutton(mode_frame, text="Load from CSV File", variable=self.input_mode, 
                       value="file", command=self.on_mode_change).pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="Enter Usernames Directly", variable=self.input_mode, 
                       value="direct", command=self.on_mode_change).pack(anchor=tk.W)
        
        # CSV File input
        self.file_frame = ttk.LabelFrame(parent, text="CSV File Selection", padding="10")
        self.file_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        self.file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(self.file_frame, text="CSV File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.file_frame, textvariable=self.csv_file_path).grid(row=0, column=1, 
                                                                          sticky=(tk.W, tk.E), 
                                                                          padx=5, pady=5)
        ttk.Button(self.file_frame, text="Browse...", 
                  command=self.browse_csv).grid(row=0, column=2, pady=5)
        
        ttk.Label(self.file_frame, text="Format: CSV with 'username' column", 
                 foreground='gray').grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Direct input
        self.direct_frame = ttk.LabelFrame(parent, text="Direct Username Input", padding="10")
        self.direct_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        self.direct_frame.columnconfigure(0, weight=1)
        self.direct_frame.rowconfigure(1, weight=1)
        
        ttk.Label(self.direct_frame, text="Enter usernames (one per line):").grid(row=0, column=0, 
                                                                                   sticky=tk.W, pady=(0, 5))
        
        self.direct_input = scrolledtext.ScrolledText(self.direct_frame, height=10, wrap=tk.WORD,
                                                      font=('Consolas', 10))
        self.direct_input.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.direct_input.insert('1.0', 'cristiano\nleomessi\nselenagomez')
        
        parent.rowconfigure(2, weight=1)
        
        # Set initial state
        self.on_mode_change()
        
    def create_settings_tab(self, parent):
        """Create settings tab widgets"""
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(1, weight=1)  # Allow message frame to expand
        
        # Instagram credentials
        creds_frame = ttk.LabelFrame(parent, text="Instagram Credentials", padding="10")
        creds_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        creds_frame.columnconfigure(1, weight=1)
        
        ttk.Label(creds_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(creds_frame, textvariable=self.instagram_username).grid(row=0, column=1, 
                                                                           sticky=(tk.W, tk.E), 
                                                                           padx=5, pady=5)
        
        ttk.Label(creds_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(creds_frame, textvariable=self.instagram_password, 
                 show="*").grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Message settings
        message_frame = ttk.LabelFrame(parent, text="Message Settings", padding="10")
        message_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        message_frame.columnconfigure(1, weight=1)
        message_frame.rowconfigure(1, weight=1)
        
        ttk.Label(message_frame, text="Message:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Use ScrolledText for multi-line messages
        self.message_text_widget = scrolledtext.ScrolledText(message_frame, height=8, wrap=tk.WORD,
                                                             font=('Segoe UI', 10))
        self.message_text_widget.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), 
                                     padx=5, pady=5)
        
        # Load default message
        self.message_text_widget.insert('1.0', Config.DEFAULT_MESSAGE)
        
        # Timing settings
        timing_frame = ttk.LabelFrame(parent, text="Timing Settings", padding="10")
        timing_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        timing_frame.columnconfigure(1, weight=1)
        
        ttk.Label(timing_frame, text=f"Delay between messages: {Config.MIN_DELAY_BETWEEN_MESSAGES}-{Config.MAX_DELAY_BETWEEN_MESSAGES}s").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(timing_frame, text=f"Messages per session: {Config.MESSAGES_PER_SESSION}").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(timing_frame, text=f"Daily limit: {Config.DAILY_MESSAGE_LIMIT}").grid(row=2, column=0, sticky=tk.W, pady=2)
        
        ttk.Label(timing_frame, text="(Edit config.py to change these values)", 
                 foreground='gray').grid(row=3, column=0, sticky=tk.W, pady=5)
        
    def create_advanced_tab(self, parent):
        """Create advanced settings tab"""
        parent.columnconfigure(1, weight=1)
        
        # Browser settings
        browser_frame = ttk.LabelFrame(parent, text="Browser Settings", padding="10")
        browser_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.headless_var = tk.BooleanVar(value=Config.HEADLESS_MODE)
        ttk.Checkbutton(browser_frame, text="Run browser in headless mode (background)", 
                       variable=self.headless_var).pack(anchor=tk.W, pady=2)
        
        self.save_cookies_var = tk.BooleanVar(value=Config.SAVE_COOKIES)
        ttk.Checkbutton(browser_frame, text="Save session cookies", 
                       variable=self.save_cookies_var).pack(anchor=tk.W, pady=2)
        
        # Safety settings
        safety_frame = ttk.LabelFrame(parent, text="Safety Features", padding="10")
        safety_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.check_blocks_var = tk.BooleanVar(value=Config.CHECK_FOR_BLOCKS)
        ttk.Checkbutton(safety_frame, text="Check for account blocks/restrictions", 
                       variable=self.check_blocks_var).pack(anchor=tk.W, pady=2)
        
        self.random_actions_var = tk.BooleanVar(value=Config.ENABLE_RANDOM_ACTIONS)
        ttk.Checkbutton(safety_frame, text="Enable random human-like actions", 
                       variable=self.random_actions_var).pack(anchor=tk.W, pady=2)
        
        # Actions
        actions_frame = ttk.LabelFrame(parent, text="Actions", padding="10")
        actions_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(actions_frame, text="View Report", 
                  command=self.view_report).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(actions_frame, text="Export Last Run", 
                  command=self.export_last_run).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(actions_frame, text="Reset Progress", 
                  command=self.reset_progress).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(actions_frame, text="Open Log File", 
                  command=self.open_log_file).pack(side=tk.LEFT, padx=5, pady=5)
        
    def on_mode_change(self):
        """Handle input mode change"""
        if self.input_mode.get() == "file":
            # Enable file input, disable direct input
            for child in self.file_frame.winfo_children():
                child.configure(state=tk.NORMAL)
            self.direct_input.configure(state=tk.DISABLED)
        else:
            # Disable file input, enable direct input
            for child in self.file_frame.winfo_children():
                if isinstance(child, (ttk.Entry, ttk.Button)):
                    child.configure(state=tk.DISABLED)
            self.direct_input.configure(state=tk.NORMAL)
    
    def browse_csv(self):
        """Open file dialog to select CSV"""
        filename = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.csv_file_path.set(filename)
    
    def setup_logging(self):
        """Setup logging to GUI"""
        # Redirect stdout to log widget
        sys.stdout = TextRedirector(self.log_text, "stdout")
        
        # Setup logging
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        
        # Create handler for GUI
        class GUIHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
                
            def emit(self, record):
                msg = self.format(record)
                tag = record.levelname
                self.text_widget.insert(tk.END, msg + '\n', tag)
                self.text_widget.see(tk.END)
                self.text_widget.update_idletasks()
        
        gui_handler = GUIHandler(self.log_text)
        gui_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(gui_handler)
    
    def log(self, message, level="INFO"):
        """Log a message to the GUI"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n", level)
        self.log_text.see(tk.END)
        self.log_text.update_idletasks()
    
    def start_automation(self):
        """Start the automation in a separate thread"""
        # Validate inputs
        if self.input_mode.get() == "file":
            if not os.path.exists(self.csv_file_path.get()):
                messagebox.showerror("Error", "CSV file not found!")
                return
        else:
            usernames = self.direct_input.get('1.0', tk.END).strip()
            if not usernames:
                messagebox.showerror("Error", "Please enter at least one username!")
                return
        
        if not self.instagram_username.get() or not self.instagram_password.get():
            messagebox.showerror("Error", "Please enter Instagram credentials!")
            return
        
        # Start automation immediately (no confirmation popup)
        
        # Update UI state
        self.is_running = True
        self.start_button.configure(state=tk.DISABLED)
        self.stop_button.configure(state=tk.NORMAL)
        self.progress_bar.start(10)
        self.status_var.set("Running...")
        
        # Clear log
        self.log_text.delete('1.0', tk.END)
        
        # Start automation thread
        self.automation_thread = threading.Thread(target=self.run_automation, daemon=True)
        self.automation_thread.start()
    
    def stop_automation(self):
        """Stop the automation"""
        self.is_running = False
        if self.automation_instance:
            self.automation_instance.running = False
        self.log("Stopping automation...", "WARNING")
        self.status_var.set("Stopping...")
    
    def run_automation(self):
        """Run the automation (in separate thread)"""
        automation = None
        try:
            from main import InstagramDMAutomation
            
            # Create temporary CSV if using direct input
            if self.input_mode.get() == "direct":
                usernames = self.direct_input.get('1.0', tk.END).strip().split('\n')
                usernames = [u.strip() for u in usernames if u.strip()]
                
                # Write to temporary CSV
                import csv
                temp_csv = "temp_usernames.csv"
                with open(temp_csv, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['username'])
                    for username in usernames:
                        writer.writerow([username])
                
                csv_file = temp_csv
            else:
                csv_file = self.csv_file_path.get()
            
            # Update config with GUI values
            Config.INSTAGRAM_USERNAME = self.instagram_username.get()
            Config.INSTAGRAM_PASSWORD = self.instagram_password.get()
            Config.DEFAULT_MESSAGE = self.message_text_widget.get('1.0', tk.END).strip()
            Config.HEADLESS_MODE = self.headless_var.get()
            Config.SAVE_COOKIES = self.save_cookies_var.get()
            Config.CHECK_FOR_BLOCKS = self.check_blocks_var.get()
            Config.CSV_FILE = csv_file
            
            self.log("Starting Instagram DM Automation...", "INFO")
            self.progress_var.set("Initializing...")
            
            # Run automation (disable signal handler since we're in a thread)
            automation = InstagramDMAutomation(setup_signal_handler=False)
            automation.running = True  # Set to running
            self.automation_instance = automation  # Store for stop button
            
            # Load CSV
            automation.csv_processor = CSVProcessor(csv_file)
            if not automation.csv_processor.load_csv():
                self.log("Failed to load profiles", "ERROR")
                return
            
            profiles = automation.csv_processor.get_unprocessed_profiles()
            if not profiles:
                self.log("No unprocessed profiles found", "WARNING")
                return
            
            self.log(f"Found {len(profiles)} profiles to process", "INFO")
            self.progress_var.set(f"Processing {len(profiles)} profiles...")
            
            # Initialize browser
            if not automation.initialize_browser():
                self.log("Failed to initialize browser", "ERROR")
                return
            
            # Login
            if not automation.login_to_instagram():
                self.log("Login failed", "ERROR")
                return
            
            # Process profiles
            success_count = 0
            fail_count = 0
            
            for i, profile_url in enumerate(profiles):
                if not self.is_running:
                    self.log("Automation stopped by user", "WARNING")
                    break
                
                self.progress_var.set(f"Processing {i+1}/{len(profiles)}: {profile_url}")
                
                if automation.process_profile(profile_url):
                    success_count += 1
                    self.log(f"✓ Sent message to {profile_url}", "SUCCESS")
                else:
                    fail_count += 1
                    self.log(f"✗ Failed to message {profile_url}", "ERROR")
                
                # Update statistics
                self.stats_label.config(
                    text=f"Processed: {i+1} | Success: {success_count} | Failed: {fail_count}"
                )
                
                # Delay between profiles
                if i < len(profiles) - 1 and self.is_running:
                    import time
                    delay = automation.get_random_delay()
                    self.log(f"Waiting {delay:.0f}s before next message...", "INFO")
                    time.sleep(delay)
            
            # Print statistics
            automation.print_statistics()
            
            self.log("Automation completed!", "SUCCESS")
            self.progress_var.set("Completed!")
            
        except Exception as e:
            self.log(f"Error: {str(e)}", "ERROR")
            import traceback
            traceback.print_exc()
        finally:
            self.finish_automation()
    
    def finish_automation(self):
        """Clean up after automation finishes"""
        self.is_running = False
        self.automation_instance = None
        self.start_button.configure(state=tk.NORMAL)
        self.stop_button.configure(state=tk.DISABLED)
        self.progress_bar.stop()
        self.status_var.set("Ready")
        
        # Clean up temp file
        if os.path.exists("temp_usernames.csv"):
            try:
                os.remove("temp_usernames.csv")
            except:
                pass
    
    def view_report(self):
        """Open the message report"""
        report_file = "message_report.csv"
        if os.path.exists(report_file):
            import subprocess
            try:
                os.startfile(report_file)  # Windows
            except:
                try:
                    subprocess.call(['open', report_file])  # Mac
                except:
                    subprocess.call(['xdg-open', report_file])  # Linux
        else:
            messagebox.showinfo("Info", "No report file found. Run automation first.")
    
    def export_last_run(self):
        """Export successful and unsuccessful sends from the last run"""
        try:
            processor = CSVProcessor(Config.CSV_FILE)
            success_file, fail_file = processor.export_last_run_results()
            
            if success_file or fail_file:
                message = "Export complete!\n\n"
                if success_file:
                    message += f"✓ Successful sends: {success_file}\n"
                if fail_file:
                    message += f"✗ Unsuccessful sends: {fail_file}"
                messagebox.showinfo("Export Complete", message)
                
                # Open the folder containing the files
                import subprocess
                import os
                folder = os.path.dirname(os.path.abspath(success_file or fail_file))
                try:
                    os.startfile(folder)  # Windows
                except:
                    try:
                        subprocess.call(['open', folder])  # Mac
                    except:
                        subprocess.call(['xdg-open', folder])  # Linux
            else:
                messagebox.showinfo("Info", "No recent sends to export (last 24 hours)")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting files: {str(e)}")
    
    def reset_progress(self):
        """Reset the processed profiles"""
        response = messagebox.askyesno(
            "Reset Progress",
            "This will reset all processed profiles.\nAre you sure?",
            icon='warning'
        )
        if response:
            if os.path.exists("processed_profiles.json"):
                os.remove("processed_profiles.json")
            self.log("Progress reset", "INFO")
            messagebox.showinfo("Success", "Progress has been reset.")
    
    def open_log_file(self):
        """Open the log file"""
        log_file = Config.LOG_FILE
        if os.path.exists(log_file):
            import subprocess
            try:
                os.startfile(log_file)  # Windows
            except:
                try:
                    subprocess.call(['open', log_file])  # Mac
                except:
                    subprocess.call(['xdg-open', log_file])  # Linux
        else:
            messagebox.showinfo("Info", "No log file found yet.")

def main():
    """Main entry point for GUI"""
    root = tk.Tk()
    app = InstagramDMGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

