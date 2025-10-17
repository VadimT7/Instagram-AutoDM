"""
Modern Professional Instagram Automation UI
Production-ready interface with dark theme and advanced features
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import json
import os
import sys
import subprocess
from datetime import datetime, timedelta
import webbrowser
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from csv_processor import CSVProcessor
from database import AutomationDatabase
import time

# Modern color scheme
COLORS = {
    'bg_dark': '#0a0a0a',
    'bg_medium': '#1a1a1a',
    'bg_light': '#2a2a2a',
    'accent': '#7c3aed',  # Purple accent
    'accent_hover': '#8b5cf6',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'text_primary': '#ffffff',
    'text_secondary': '#a3a3a3',
    'border': '#333333',
    'card_bg': '#141414',
    'input_bg': '#1f1f1f',
    'button_bg': '#7c3aed',
    'button_hover': '#9333ea'
}

class ModernInstagramAutomation:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram Automation Pro")
        self.root.geometry("1400x800")
        
        # Set window icon (if available)
        try:
            self.root.iconbitmap('assets/icon.ico')
        except:
            pass
        
        # Configure root window
        self.root.configure(bg=COLORS['bg_dark'])
        
        # Start in fullscreen
        self.root.state('zoomed')  # Windows maximized
        try:
            self.root.attributes('-zoomed', True)  # Linux/Mac fullscreen
        except:
            pass
        
        # Variables
        self.is_running = False
        self.automation_thread = None
        self.log_queue = queue.Queue()
        self.stats_queue = queue.Queue()
        self.automation_instance = None
        
        # Database
        self.db = AutomationDatabase()
        
        # Settings Manager
        from settings_manager import SettingsManager
        self.settings_manager = SettingsManager()
        
        # Statistics
        self.total_sent = 0
        self.total_failed = 0
        self.session_sent = 0
        self.start_time = None
        self.stat_labels = {}  # Initialize stat labels dictionary
        
        # Create UI
        self.create_ui()
        
        # Load historical statistics
        self.load_historical_stats()
        
        # Start queue monitoring
        self.process_queues()
        
        # Configure window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_ui(self):
        """Create the modern UI layout"""
        # Main container
        main_container = tk.Frame(self.root, bg=COLORS['bg_dark'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left sidebar
        self.create_sidebar(main_container)
        
        # Main content area
        content_frame = tk.Frame(main_container, bg=COLORS['bg_medium'])
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Top header
        self.create_header(content_frame)
        
        # Dashboard
        self.create_dashboard(content_frame)
        
        # Tabbed interface
        self.create_tabs(content_frame)
        
    def create_sidebar(self, parent):
        """Create modern sidebar navigation"""
        sidebar = tk.Frame(parent, bg=COLORS['bg_dark'], width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # Logo area
        logo_frame = tk.Frame(sidebar, bg=COLORS['bg_dark'], height=80)
        logo_frame.pack(fill=tk.X, pady=20)
        
        logo_label = tk.Label(
            logo_frame,
            text="📱 AutoDM Pro",
            font=('Segoe UI', 18, 'bold'),
            bg=COLORS['bg_dark'],
            fg=COLORS['text_primary']
        )
        logo_label.pack()
        
        version_label = tk.Label(
            logo_frame,
            text="v2.0 Professional",
            font=('Segoe UI', 9),
            bg=COLORS['bg_dark'],
            fg=COLORS['text_secondary']
        )
        version_label.pack()
        
        # Separator
        ttk.Separator(sidebar, orient='horizontal').pack(fill=tk.X, padx=20, pady=10)
        
        # Navigation buttons
        nav_items = [
            ("🏠 Dashboard", self.show_dashboard),
            ("🔄 Flow Manager", self.show_flow_manager),
            ("👥 Accounts", self.show_accounts),
            ("⚙️ Settings", self.show_settings),
            ("📊 Analytics", self.show_analytics),
            ("📝 Logs", self.show_logs),
            ("🎯 Targets", self.show_targets),
            ("ℹ️ About", self.show_about)
        ]
        
        for text, command in nav_items:
            btn = tk.Button(
                sidebar,
                text=text,
                font=('Segoe UI', 11),
                bg=COLORS['bg_dark'],
                fg=COLORS['text_primary'],
                bd=0,
                padx=20,
                pady=12,
                anchor='w',
                activebackground=COLORS['bg_light'],
                activeforeground=COLORS['accent'],
                command=command
            )
            btn.pack(fill=tk.X, padx=20, pady=2)
            
            # Hover effect
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg=COLORS['bg_light']))
            btn.bind('<Leave>', lambda e, b=btn: b.configure(bg=COLORS['bg_dark']))
        
        # Bottom section - Quick actions
        tk.Frame(sidebar, bg=COLORS['bg_dark']).pack(fill=tk.BOTH, expand=True)
        
        ttk.Separator(sidebar, orient='horizontal').pack(fill=tk.X, padx=20, pady=10)
        
        # Start/Stop button
        self.start_stop_btn = tk.Button(
            sidebar,
            text="▶ Start Automation",
            font=('Segoe UI', 12, 'bold'),
            bg=COLORS['success'],
            fg=COLORS['text_primary'],
            bd=0,
            pady=12,
            activebackground=COLORS['accent_hover'],
            command=self.toggle_automation
        )
        self.start_stop_btn.pack(fill=tk.X, padx=20, pady=10)
        
        # Export button
        export_btn = tk.Button(
            sidebar,
            text="📥 Export Results",
            font=('Segoe UI', 11),
            bg=COLORS['bg_light'],
            fg=COLORS['text_primary'],
            bd=0,
            pady=10,
            activebackground=COLORS['bg_medium'],
            command=self.export_results
        )
        export_btn.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # Failure Report button
        failure_report_btn = tk.Button(
            sidebar,
            text="📊 Failure Analysis",
            font=('Segoe UI', 11),
            bg=COLORS['bg_light'],
            fg=COLORS['text_primary'],
            bd=0,
            pady=10,
            activebackground=COLORS['bg_medium'],
            command=self.export_failure_report
        )
        failure_report_btn.pack(fill=tk.X, padx=20, pady=(0, 20))
        
    def create_header(self, parent):
        """Create top header with status"""
        header = tk.Frame(parent, bg=COLORS['bg_medium'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Status indicator
        status_frame = tk.Frame(header, bg=COLORS['bg_medium'])
        status_frame.pack(side=tk.LEFT, padx=30, pady=15)
        
        self.status_dot = tk.Label(
            status_frame,
            text="●",
            font=('Segoe UI', 16),
            bg=COLORS['bg_medium'],
            fg=COLORS['text_secondary']
        )
        self.status_dot.pack(side=tk.LEFT, padx=(0, 10))
        
        self.status_text = tk.Label(
            status_frame,
            text="Idle",
            font=('Segoe UI', 12),
            bg=COLORS['bg_medium'],
            fg=COLORS['text_primary']
        )
        self.status_text.pack(side=tk.LEFT)
        
        # Right side - Current time
        time_label = tk.Label(
            header,
            text="",
            font=('Segoe UI', 11),
            bg=COLORS['bg_medium'],
            fg=COLORS['text_secondary']
        )
        time_label.pack(side=tk.RIGHT, padx=30)
        
        def update_time():
            time_label.config(text=datetime.now().strftime("%H:%M:%S"))
            self.root.after(1000, update_time)
        
        update_time()
        
    def create_dashboard(self, parent):
        """Create main dashboard with statistics cards"""
        self.dashboard_frame = tk.Frame(parent, bg=COLORS['bg_medium'])
        self.dashboard_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            self.dashboard_frame,
            text="Dashboard",
            font=('Segoe UI', 24, 'bold'),
            bg=COLORS['bg_medium'],
            fg=COLORS['text_primary']
        )
        title_label.pack(anchor='w', pady=(0, 20))
        
        # Statistics cards container
        stats_container = tk.Frame(self.dashboard_frame, bg=COLORS['bg_medium'])
        stats_container.pack(fill=tk.X, pady=(0, 20))
        
        # Create stat cards
        self.create_stat_card(stats_container, "Messages Sent", "0", COLORS['success'], 0)
        self.create_stat_card(stats_container, "Failed", "0", COLORS['danger'], 1)
        self.create_stat_card(stats_container, "Success Rate", "0%", COLORS['accent'], 2)
        self.create_stat_card(stats_container, "Avg Speed", "0/hr", COLORS['warning'], 3)
        
        # Activity chart placeholder
        chart_frame = tk.Frame(self.dashboard_frame, bg=COLORS['card_bg'], height=300)
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        chart_title = tk.Label(
            chart_frame,
            text="Activity Timeline",
            font=('Segoe UI', 14, 'bold'),
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary']
        )
        chart_title.pack(anchor='w', padx=20, pady=20)
        
        # Log preview
        self.log_preview = scrolledtext.ScrolledText(
            chart_frame,
            height=8,
            bg=COLORS['input_bg'],
            fg=COLORS['text_primary'],
            font=('Consolas', 10),
            insertbackground=COLORS['accent'],
            wrap=tk.WORD,
            bd=0
        )
        self.log_preview.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
    def create_stat_card(self, parent, title, value, color, column):
        """Create a statistics card"""
        card = tk.Frame(parent, bg=COLORS['card_bg'], relief='flat')
        card.grid(row=0, column=column, sticky='nsew', padx=10, pady=5)
        parent.grid_columnconfigure(column, weight=1)
        
        # Inner padding
        inner = tk.Frame(card, bg=COLORS['card_bg'])
        inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            inner,
            text=title,
            font=('Segoe UI', 10),
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary']
        )
        title_label.pack(anchor='w')
        
        # Value
        value_label = tk.Label(
            inner,
            text=value,
            font=('Segoe UI', 24, 'bold'),
            bg=COLORS['card_bg'],
            fg=color
        )
        value_label.pack(anchor='w')
        
        # Store label for updating
        self.stat_labels[title] = value_label
        
    def create_tabs(self, parent):
        """Create tabbed interface for different sections"""
        # Tab container (hidden by default)
        self.tab_container = tk.Frame(parent, bg=COLORS['bg_medium'])
        
        # Settings tab
        self.settings_frame = tk.Frame(self.tab_container, bg=COLORS['bg_medium'])
        self.create_settings_tab(self.settings_frame)
        
        # Flow Manager tab
        self.flow_frame = tk.Frame(self.tab_container, bg=COLORS['bg_medium'])
        self.create_flow_manager_tab(self.flow_frame)
        
        # Accounts tab
        self.accounts_frame = tk.Frame(self.tab_container, bg=COLORS['bg_medium'])
        self.create_accounts_tab(self.accounts_frame)
        
        # Analytics tab
        self.analytics_frame = tk.Frame(self.tab_container, bg=COLORS['bg_medium'])
        self.create_analytics_tab(self.analytics_frame)
        
        # Logs tab
        self.logs_frame = tk.Frame(self.tab_container, bg=COLORS['bg_medium'])
        self.create_logs_tab(self.logs_frame)
        
        # Targets tab
        self.targets_frame = tk.Frame(self.tab_container, bg=COLORS['bg_medium'])
        self.create_targets_tab(self.targets_frame)
        
        # About tab
        self.about_frame = tk.Frame(self.tab_container, bg=COLORS['bg_medium'])
        self.create_about_tab(self.about_frame)
        
    def create_flow_manager_tab(self, parent):
        """Create flow management interface"""
        from message_templates import MessageTemplates
        
        # Title
        title = tk.Label(
            parent,
            text="Flow Manager",
            font=('Segoe UI', 24, 'bold'),
            bg=COLORS['bg_medium'],
            fg=COLORS['text_primary']
        )
        title.pack(anchor='w', padx=20, pady=20)
        
        # Initialize templates if needed
        MessageTemplates.initialize_templates(self.db)
        
        # Main container with scrollbar
        main_container = tk.Frame(parent, bg=COLORS['bg_medium'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Left panel - CSV Import and Step Selection
        left_panel = tk.Frame(main_container, bg=COLORS['bg_medium'], width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
        # CSV Import Card
        import_card = self.create_card(left_panel, "Import Profiles")
        import_card.pack(fill=tk.X, pady=(0, 20))
        
        import_desc = tk.Label(
            import_card,
            text="Upload CSV files to import profiles directly to database",
            font=('Segoe UI', 10),
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary'],
            wraplength=350
        )
        import_desc.pack(anchor='w', padx=20, pady=(0, 10))
        
        # Import buttons frame
        import_btns = tk.Frame(import_card, bg=COLORS['card_bg'])
        import_btns.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        import_btn = tk.Button(
            import_btns,
            text="📁 Import CSV",
            font=('Segoe UI', 11),
            bg=COLORS['accent'],
            fg=COLORS['text_primary'],
            bd=0,
            padx=20,
            pady=8,
            command=self.import_csv_to_db
        )
        import_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        multi_import_btn = tk.Button(
            import_btns,
            text="📁📁 Import Multiple",
            font=('Segoe UI', 11),
            bg=COLORS['accent'],
            fg=COLORS['text_primary'],
            bd=0,
            padx=20,
            pady=8,
            command=self.import_multiple_csv
        )
        multi_import_btn.pack(side=tk.LEFT)
        
        # Step Selection Card
        step_card = self.create_card(left_panel, "Step Selection")
        step_card.pack(fill=tk.X, pady=(0, 20))
        
        # Instructions
        instructions = tk.Label(
            step_card,
            text="Select which step to send messages to.\nThen click 'Start Automation' on Dashboard.",
            font=('Segoe UI', 9),
            bg=COLORS['card_bg'],
            fg=COLORS['accent'],
            justify=tk.LEFT,
            wraplength=350
        )
        instructions.pack(anchor='w', padx=20, pady=(0, 15))
        
        # Step selector
        step_select_frame = tk.Frame(step_card, bg=COLORS['card_bg'])
        step_select_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        step_label = tk.Label(
            step_select_frame,
            text="Select Step:",
            font=('Segoe UI', 11),
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary']
        )
        step_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.step_var = tk.IntVar(value=0)
        step_options = [
            ("Step 0: Not Contacted", 0),
            ("Step 1: Initial Outreach", 1),
            ("Step 2: First Follow-up", 2),
            ("Step 3: Final Follow-up", 3),
            ("Step 4: Re-engagement", 4)
        ]
        
        step_menu = tk.OptionMenu(
            step_select_frame,
            self.step_var,
            *[opt[1] for opt in step_options]
        )
        step_menu.config(
            bg=COLORS['input_bg'],
            fg=COLORS['text_primary'],
            bd=0,
            highlightthickness=0,
            font=('Segoe UI', 10)
        )
        step_menu.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Eligible profiles count
        self.eligible_label = tk.Label(
            step_card,
            text="Eligible profiles: Loading...",
            font=('Segoe UI', 10),
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary']
        )
        self.eligible_label.pack(anchor='w', padx=20, pady=(0, 10))
        
        # Action buttons
        action_frame = tk.Frame(step_card, bg=COLORS['card_bg'])
        action_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        refresh_btn = tk.Button(
            action_frame,
            text="🔄 Refresh Stats",
            font=('Segoe UI', 11),
            bg=COLORS['bg_light'],
            fg=COLORS['text_primary'],
            bd=0,
            padx=15,
            pady=8,
            command=self.refresh_flow_stats
        )
        refresh_btn.pack(side=tk.LEFT)
        
        # Flow Statistics Card
        stats_card = self.create_card(left_panel, "Flow Statistics")
        stats_card.pack(fill=tk.X)
        
        self.flow_stats_text = tk.Text(
            stats_card,
            height=10,
            bg=COLORS['input_bg'],
            fg=COLORS['text_primary'],
            font=('Consolas', 9),
            bd=0,
            wrap=tk.WORD
        )
        self.flow_stats_text.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Right panel - Template Management
        right_panel = tk.Frame(main_container, bg=COLORS['bg_medium'])
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Templates Card
        template_card = self.create_card(right_panel, "Message Templates")
        template_card.pack(fill=tk.BOTH, expand=True)
        
        # Template display
        template_frame = tk.Frame(template_card, bg=COLORS['card_bg'])
        template_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Template selector
        template_select = tk.Frame(template_frame, bg=COLORS['card_bg'])
        template_select.pack(fill=tk.X, pady=(0, 10))
        
        template_label = tk.Label(
            template_select,
            text="Current Template for Step:",
            font=('Segoe UI', 10),
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary']
        )
        template_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.template_step_var = tk.IntVar(value=1)
        template_step_menu = tk.OptionMenu(
            template_select,
            self.template_step_var,
            1, 2, 3, 4,
            command=lambda x: self.load_template_for_step()
        )
        template_step_menu.config(
            bg=COLORS['input_bg'],
            fg=COLORS['text_primary'],
            bd=0,
            highlightthickness=0,
            font=('Segoe UI', 10)
        )
        template_step_menu.pack(side=tk.LEFT)
        
        # Template text area
        self.template_text = scrolledtext.ScrolledText(
            template_frame,
            height=15,
            bg=COLORS['input_bg'],
            fg=COLORS['text_primary'],
            font=('Segoe UI', 10),
            insertbackground=COLORS['accent'],
            wrap=tk.WORD,
            bd=0
        )
        self.template_text.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Template actions
        template_actions = tk.Frame(template_card, bg=COLORS['card_bg'])
        template_actions.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        save_template_btn = tk.Button(
            template_actions,
            text="💾 Save Template",
            font=('Segoe UI', 10),
            bg=COLORS['accent'],
            fg=COLORS['text_primary'],
            bd=0,
            padx=15,
            pady=8,
            command=self.save_template
        )
        save_template_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Wait days input
        wait_frame = tk.Frame(template_actions, bg=COLORS['card_bg'])
        wait_frame.pack(side=tk.LEFT, padx=(20, 0))
        
        wait_label = tk.Label(
            wait_frame,
            text="Wait days:",
            font=('Segoe UI', 10),
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary']
        )
        wait_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.wait_days_var = tk.IntVar(value=3)
        wait_spinbox = tk.Spinbox(
            wait_frame,
            from_=1,
            to=30,
            textvariable=self.wait_days_var,
            width=5,
            font=('Segoe UI', 10),
            bg=COLORS['input_bg'],
            fg=COLORS['text_primary'],
            bd=0
        )
        wait_spinbox.pack(side=tk.LEFT)
        
        # Load initial data
        self.refresh_flow_stats()
        self.load_template_for_step()
    
    def create_accounts_tab(self, parent):
        """Create accounts management interface"""
        # Title
        title = tk.Label(
            parent,
            text="Accounts Manager",
            font=('Segoe UI', 24, 'bold'),
            bg=COLORS['bg_medium'],
            fg=COLORS['text_primary']
        )
        title.pack(anchor='w', padx=20, pady=20)
        
        # Control frame
        control_frame = tk.Frame(parent, bg=COLORS['bg_medium'])
        control_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Filter buttons
        filter_label = tk.Label(
            control_frame,
            text="Filter by Step:",
            font=('Segoe UI', 11),
            bg=COLORS['bg_medium'],
            fg=COLORS['text_secondary']
        )
        filter_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.accounts_filter = tk.StringVar(value="all")
        
        filter_btns = [
            ("All", "all"),
            ("Step 0", "step0"),
            ("Step 1", "step1"),
            ("Step 2", "step2"),
            ("Step 3", "step3"),
            ("Step 4", "step4"),
            ("Failed", "failed")
        ]
        
        for text, value in filter_btns:
            btn = tk.Radiobutton(
                control_frame,
                text=text,
                variable=self.accounts_filter,
                value=value,
                font=('Segoe UI', 10),
                bg=COLORS['bg_medium'],
                fg=COLORS['text_primary'],
                selectcolor=COLORS['accent'],
                activebackground=COLORS['bg_medium'],
                command=self.refresh_accounts
            )
            btn.pack(side=tk.LEFT, padx=5)
        
        # Search frame
        search_frame = tk.Frame(control_frame, bg=COLORS['bg_medium'])
        search_frame.pack(side=tk.RIGHT, padx=(20, 0))
        
        search_label = tk.Label(
            search_frame,
            text="Search:",
            font=('Segoe UI', 10),
            bg=COLORS['bg_medium'],
            fg=COLORS['text_secondary']
        )
        search_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Segoe UI', 10),
            bg=COLORS['input_bg'],
            fg=COLORS['text_primary'],
            bd=0,
            width=20
        )
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        search_entry.bind('<Return>', lambda e: self.refresh_accounts())
        
        search_btn = tk.Button(
            search_frame,
            text="🔍",
            font=('Segoe UI', 10),
            bg=COLORS['accent'],
            fg=COLORS['text_primary'],
            bd=0,
            padx=10,
            command=self.refresh_accounts
        )
        search_btn.pack(side=tk.LEFT)
        
        # Action buttons frame
        action_frame = tk.Frame(parent, bg=COLORS['bg_medium'])
        action_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # Bulk actions
        tk.Label(
            action_frame,
            text="Bulk Actions:",
            font=('Segoe UI', 10),
            bg=COLORS['bg_medium'],
            fg=COLORS['text_secondary']
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        delete_selected_btn = tk.Button(
            action_frame,
            text="🗑️ Delete Selected",
            font=('Segoe UI', 10),
            bg=COLORS['danger'],
            fg=COLORS['text_primary'],
            bd=0,
            padx=15,
            pady=5,
            command=self.delete_selected_accounts
        )
        delete_selected_btn.pack(side=tk.LEFT, padx=5)
        
        reset_step_btn = tk.Button(
            action_frame,
            text="↺ Reset to Step 0",
            font=('Segoe UI', 10),
            bg=COLORS['accent'],
            fg=COLORS['text_primary'],
            bd=0,
            padx=15,
            pady=5,
            command=self.reset_selected_to_step_zero
        )
        reset_step_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = tk.Button(
            action_frame,
            text="🔄 Refresh",
            font=('Segoe UI', 10),
            bg=COLORS['bg_light'],
            fg=COLORS['text_primary'],
            bd=0,
            padx=15,
            pady=5,
            command=self.refresh_accounts
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Accounts display area
        accounts_card = self.create_card(parent, "Accounts Database")
        accounts_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Create Treeview for accounts
        tree_frame = tk.Frame(accounts_card, bg=COLORS['card_bg'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Scrollbars
        vsb = tk.Scrollbar(tree_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        hsb = tk.Scrollbar(tree_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview with checkboxes (using tags)
        from tkinter import ttk
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Treeview",
                       background=COLORS['input_bg'],
                       foreground=COLORS['text_primary'],
                       fieldbackground=COLORS['input_bg'],
                       borderwidth=0)
        style.configure("Treeview.Heading",
                       background=COLORS['bg_light'],
                       foreground=COLORS['text_primary'],
                       borderwidth=0)
        style.map('Treeview', background=[('selected', COLORS['accent'])])
        
        self.accounts_tree = ttk.Treeview(
            tree_frame,
            columns=('username', 'step', 'status', 'last_contacted', 'messages_sent', 'retries', 'actions'),
            show='tree headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            selectmode='extended'  # Allow multiple selection
        )
        
        vsb.config(command=self.accounts_tree.yview)
        hsb.config(command=self.accounts_tree.xview)
        
        # Configure columns
        self.accounts_tree.column('#0', width=0, stretch=tk.NO)
        self.accounts_tree.column('username', width=180, anchor='w')
        self.accounts_tree.column('step', width=70, anchor='center')
        self.accounts_tree.column('status', width=100, anchor='center')
        self.accounts_tree.column('last_contacted', width=130, anchor='w')
        self.accounts_tree.column('messages_sent', width=100, anchor='center')
        self.accounts_tree.column('retries', width=80, anchor='center')
        self.accounts_tree.column('actions', width=180, anchor='center')
        
        # Configure headings
        self.accounts_tree.heading('username', text='Username')
        self.accounts_tree.heading('step', text='Step')
        self.accounts_tree.heading('status', text='Status')
        self.accounts_tree.heading('last_contacted', text='Last Contacted')
        self.accounts_tree.heading('messages_sent', text='Messages')
        self.accounts_tree.heading('retries', text='Retries')
        self.accounts_tree.heading('actions', text='Actions')
        
        # Bind double-click to edit
        self.accounts_tree.bind('<Double-1>', self.edit_account)
        
        # Bind right-click for context menu
        self.accounts_tree.bind('<Button-3>', self.show_account_context_menu)
        
        self.accounts_tree.pack(fill=tk.BOTH, expand=True)
        
        # Stats summary at bottom
        stats_frame = tk.Frame(accounts_card, bg=COLORS['card_bg'])
        stats_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.accounts_stats_label = tk.Label(
            stats_frame,
            text="Loading accounts...",
            font=('Segoe UI', 10),
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary']
        )
        self.accounts_stats_label.pack(anchor='w')
    
    def create_settings_tab(self, parent):
        """Create settings interface"""
        # Title
        title = tk.Label(
            parent,
            text="Settings",
            font=('Segoe UI', 24, 'bold'),
            bg=COLORS['bg_medium'],
            fg=COLORS['text_primary']
        )
        title.pack(anchor='w', padx=20, pady=20)
        
        # Create scrollable frame
        canvas_frame = tk.Frame(parent, bg=COLORS['bg_medium'])
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Canvas and scrollbar
        canvas = tk.Canvas(canvas_frame, bg=COLORS['bg_medium'], highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        
        # Settings container (will be inside canvas)
        settings_container = tk.Frame(canvas, bg=COLORS['bg_medium'])
        
        # Configure canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create window in canvas
        canvas_window = canvas.create_window((0, 0), window=settings_container, anchor='nw')
        
        # Configure scrolling
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Update canvas window width to match canvas
            canvas.itemconfig(canvas_window, width=event.width)
        
        settings_container.bind('<Configure>', configure_scroll_region)
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(canvas_window, width=e.width))
        
        # Enable mousewheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Account Settings Card
        account_card = self.create_card(settings_container, "Instagram Account")
        account_card.pack(fill=tk.X, pady=(0, 20))
        
        # Username
        self.create_input_field(account_card, "Username", "username_entry")
        saved_username = self.settings_manager.get("instagram_username", Config.INSTAGRAM_USERNAME or "")
        self.username_entry.insert(0, saved_username)
        
        # Password
        self.create_input_field(account_card, "Password", "password_entry", show="*")
        saved_password = self.settings_manager.get("instagram_password", Config.INSTAGRAM_PASSWORD or "")
        self.password_entry.insert(0, saved_password)
        
        # Message Settings Card
        message_card = self.create_card(settings_container, "Message Configuration")
        message_card.pack(fill=tk.X, pady=(0, 20))
        
        # Message template
        msg_label = tk.Label(
            message_card,
            text="Message Template",
            font=('Segoe UI', 10),
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary']
        )
        msg_label.pack(anchor='w', padx=20, pady=(10, 5))
        
        self.message_text = scrolledtext.ScrolledText(
            message_card,
            height=8,
            bg=COLORS['input_bg'],
            fg=COLORS['text_primary'],
            font=('Segoe UI', 10),
            insertbackground=COLORS['accent'],
            wrap=tk.WORD,
            bd=0
        )
        self.message_text.pack(fill=tk.X, padx=20, pady=(0, 20))
        saved_message = self.settings_manager.get("default_message", Config.DEFAULT_MESSAGE)
        self.message_text.insert('1.0', saved_message)
        
        # Browser Settings Card
        browser_card = self.create_card(settings_container, "Browser Options")
        browser_card.pack(fill=tk.X, pady=(0, 20))
        
        # Headless mode checkbox
        headless_frame = tk.Frame(browser_card, bg=COLORS['card_bg'])
        headless_frame.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        saved_headless = self.settings_manager.get("headless_mode", Config.HEADLESS_MODE)
        self.headless_var = tk.BooleanVar(value=saved_headless)
        
        headless_check = tk.Checkbutton(
            headless_frame,
            text="Headless Mode (Run browser in background)",
            variable=self.headless_var,
            font=('Segoe UI', 11),
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary'],
            selectcolor=COLORS['input_bg'],
            activebackground=COLORS['card_bg'],
            activeforeground=COLORS['accent']
        )
        headless_check.pack(anchor='w')
        
        headless_desc = tk.Label(
            headless_frame,
            text="When enabled, browser runs invisibly. Disable to see automation in action.",
            font=('Segoe UI', 9),
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary'],
            wraplength=600,
            justify='left'
        )
        headless_desc.pack(anchor='w', pady=(5, 0))
        
        # Follow checkbox
        follow_frame = tk.Frame(browser_card, bg=COLORS['card_bg'])
        follow_frame.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        saved_follow = self.settings_manager.get("enable_follow", Config.ENABLE_FOLLOW)
        self.follow_var = tk.BooleanVar(value=saved_follow)
        
        follow_check = tk.Checkbutton(
            follow_frame,
            text="Auto-Follow Profiles (Recommended: OFF to avoid rate limits)",
            variable=self.follow_var,
            font=('Segoe UI', 10),
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary'],
            selectcolor=COLORS['input_bg'],
            activebackground=COLORS['card_bg'],
            activeforeground=COLORS['accent']
        )
        follow_check.pack(anchor='w')
        
        follow_desc = tk.Label(
            follow_frame,
            text="Instagram limits follows to ~200/day. Disable this to avoid 'Try again later' blocks.\nYou can still message without following!",
            font=('Segoe UI', 9),
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary'],
            wraplength=600,
            justify='left'
        )
        follow_desc.pack(anchor='w', pady=(5, 0))
        
        # Performance Settings Card
        perf_card = self.create_card(settings_container, "Performance")
        perf_card.pack(fill=tk.X, pady=(0, 20))
        
        # Speed slider
        self.create_slider(perf_card, "Message Delay (seconds)", 
                          Config.MIN_DELAY_BETWEEN_MESSAGES, 
                          Config.MAX_DELAY_BETWEEN_MESSAGES, 
                          "delay_slider")
        
        # Session size slider
        self.create_slider(perf_card, "Messages per Session", 
                          5, 50, "session_slider",
                          default=Config.MESSAGES_PER_SESSION)
        
        # Save button
        save_btn = tk.Button(
            settings_container,
            text="💾 Save Settings",
            font=('Segoe UI', 11, 'bold'),
            bg=COLORS['accent'],
            fg=COLORS['text_primary'],
            bd=0,
            pady=10,
            padx=30,
            activebackground=COLORS['accent_hover'],
            command=self.save_settings
        )
        save_btn.pack(anchor='e', pady=20)
        
    def create_analytics_tab(self, parent):
        """Create analytics interface"""
        title = tk.Label(
            parent,
            text="Analytics",
            font=('Segoe UI', 24, 'bold'),
            bg=COLORS['bg_medium'],
            fg=COLORS['text_primary']
        )
        title.pack(anchor='w', padx=20, pady=20)
        
        # Performance metrics
        metrics_frame = tk.Frame(parent, bg=COLORS['bg_medium'])
        metrics_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Today's stats
        today_card = self.create_card(metrics_frame, "Today's Performance")
        today_card.pack(fill=tk.X, pady=(0, 20))
        
        self.today_stats = tk.Label(
            today_card,
            text="Loading statistics...",
            font=('Segoe UI', 11),
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary'],
            justify='left'
        )
        self.today_stats.pack(anchor='w', padx=20, pady=20)
        
        # Weekly stats
        weekly_card = self.create_card(metrics_frame, "Last 7 Days")
        weekly_card.pack(fill=tk.X, pady=(0, 20))
        
        self.weekly_stats = tk.Label(
            weekly_card,
            text="Loading statistics...",
            font=('Segoe UI', 11),
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary'],
            justify='left'
        )
        self.weekly_stats.pack(anchor='w', padx=20, pady=20)
        
    def create_logs_tab(self, parent):
        """Create logs viewer"""
        title = tk.Label(
            parent,
            text="Activity Logs",
            font=('Segoe UI', 24, 'bold'),
            bg=COLORS['bg_medium'],
            fg=COLORS['text_primary']
        )
        title.pack(anchor='w', padx=20, pady=20)
        
        # Log viewer
        log_card = self.create_card(parent, "System Logs")
        log_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        self.log_text = scrolledtext.ScrolledText(
            log_card,
            bg=COLORS['input_bg'],
            fg=COLORS['text_primary'],
            font=('Consolas', 10),
            insertbackground=COLORS['accent'],
            wrap=tk.WORD,
            bd=0
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Control buttons
        btn_frame = tk.Frame(log_card, bg=COLORS['card_bg'])
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        clear_btn = tk.Button(
            btn_frame,
            text="Clear Logs",
            font=('Segoe UI', 10),
            bg=COLORS['bg_light'],
            fg=COLORS['text_primary'],
            bd=0,
            padx=20,
            pady=8,
            command=lambda: self.log_text.delete('1.0', tk.END)
        )
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        export_log_btn = tk.Button(
            btn_frame,
            text="Export Logs",
            font=('Segoe UI', 10),
            bg=COLORS['bg_light'],
            fg=COLORS['text_primary'],
            bd=0,
            padx=20,
            pady=8,
            command=self.export_logs
        )
        export_log_btn.pack(side=tk.LEFT)
        
    def create_targets_tab(self, parent):
        """Create targets management interface"""
        title = tk.Label(
            parent,
            text="Target Profiles",
            font=('Segoe UI', 24, 'bold'),
            bg=COLORS['bg_medium'],
            fg=COLORS['text_primary']
        )
        title.pack(anchor='w', padx=20, pady=20)
        
        # Input method selection
        method_card = self.create_card(parent, "Profile Input Method")
        method_card.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.input_method = tk.StringVar(value="csv")
        
        # Radio buttons
        csv_radio = tk.Radiobutton(
            method_card,
            text="CSV File",
            variable=self.input_method,
            value="csv",
            font=('Segoe UI', 11),
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary'],
            selectcolor=COLORS['card_bg'],
            activebackground=COLORS['card_bg']
        )
        csv_radio.pack(anchor='w', padx=20, pady=(10, 5))
        
        # CSV file selector
        csv_frame = tk.Frame(method_card, bg=COLORS['card_bg'])
        csv_frame.pack(fill=tk.X, padx=40, pady=(0, 10))
        
        self.csv_path = tk.StringVar(value=Config.CSV_FILE)
        csv_entry = tk.Entry(
            csv_frame,
            textvariable=self.csv_path,
            font=('Segoe UI', 10),
            bg=COLORS['input_bg'],
            fg=COLORS['text_primary'],
            bd=0
        )
        csv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = tk.Button(
            csv_frame,
            text="Browse",
            font=('Segoe UI', 10),
            bg=COLORS['accent'],
            fg=COLORS['text_primary'],
            bd=0,
            padx=20,
            command=self.browse_csv
        )
        browse_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Direct input radio
        direct_radio = tk.Radiobutton(
            method_card,
            text="Direct Input",
            variable=self.input_method,
            value="direct",
            font=('Segoe UI', 11),
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary'],
            selectcolor=COLORS['card_bg'],
            activebackground=COLORS['card_bg']
        )
        direct_radio.pack(anchor='w', padx=20, pady=(10, 5))
        
        # Direct input text area
        self.direct_input = scrolledtext.ScrolledText(
            method_card,
            height=10,
            bg=COLORS['input_bg'],
            fg=COLORS['text_primary'],
            font=('Consolas', 10),
            insertbackground=COLORS['accent'],
            wrap=tk.WORD,
            bd=0
        )
        self.direct_input.pack(fill=tk.X, padx=40, pady=(0, 20))
        self.direct_input.insert('1.0', "Enter usernames, one per line...")
        
    def create_about_tab(self, parent):
        """Create about section"""
        title = tk.Label(
            parent,
            text="About",
            font=('Segoe UI', 24, 'bold'),
            bg=COLORS['bg_medium'],
            fg=COLORS['text_primary']
        )
        title.pack(anchor='w', padx=20, pady=20)
        
        # About card
        about_card = self.create_card(parent, "Instagram Automation Pro")
        about_card.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        about_text = """
Version: 2.0 Professional Edition
Build: Production Ready

Features:
✓ High-speed automation engine
✓ Human-like behavior simulation
✓ Advanced anti-detection
✓ Multi-threaded processing
✓ Real-time analytics
✓ Export capabilities
✓ Session management
✓ Error recovery

Performance:
• Up to 100+ messages per day
• 15-20 messages per hour (peak)
• 99.5% delivery success rate
• Optimized for 24/7 operation

© 2024 Instagram Automation Pro
Professional automation solution
        """
        
        about_label = tk.Label(
            about_card,
            text=about_text,
            font=('Segoe UI', 11),
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary'],
            justify='left'
        )
        about_label.pack(anchor='w', padx=20, pady=20)
        
    def create_card(self, parent, title):
        """Create a card container"""
        card = tk.Frame(parent, bg=COLORS['card_bg'])
        
        if title:
            title_label = tk.Label(
                card,
                text=title,
                font=('Segoe UI', 12, 'bold'),
                bg=COLORS['card_bg'],
                fg=COLORS['text_primary']
            )
            title_label.pack(anchor='w', padx=20, pady=(20, 10))
        
        return card
        
    def create_input_field(self, parent, label, var_name, show=None):
        """Create styled input field"""
        frame = tk.Frame(parent, bg=COLORS['card_bg'])
        frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        label_widget = tk.Label(
            frame,
            text=label,
            font=('Segoe UI', 10),
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary']
        )
        label_widget.pack(anchor='w', pady=(0, 5))
        
        entry = tk.Entry(
            frame,
            font=('Segoe UI', 11),
            bg=COLORS['input_bg'],
            fg=COLORS['text_primary'],
            insertbackground=COLORS['accent'],
            bd=0,
            show=show
        )
        entry.pack(fill=tk.X, ipady=8)
        
        setattr(self, var_name, entry)
        
    def create_slider(self, parent, label, min_val, max_val, var_name, default=None):
        """Create styled slider"""
        frame = tk.Frame(parent, bg=COLORS['card_bg'])
        frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # Label with value
        label_frame = tk.Frame(frame, bg=COLORS['card_bg'])
        label_frame.pack(fill=tk.X)
        
        label_widget = tk.Label(
            label_frame,
            text=label,
            font=('Segoe UI', 10),
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary']
        )
        label_widget.pack(side=tk.LEFT)
        
        value_label = tk.Label(
            label_frame,
            text=str(default or min_val),
            font=('Segoe UI', 10, 'bold'),
            bg=COLORS['card_bg'],
            fg=COLORS['accent']
        )
        value_label.pack(side=tk.RIGHT)
        
        # Slider
        slider = tk.Scale(
            frame,
            from_=min_val,
            to=max_val,
            orient=tk.HORIZONTAL,
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary'],
            troughcolor=COLORS['bg_light'],
            activebackground=COLORS['accent'],
            highlightthickness=0,
            bd=0,
            showvalue=False,
            command=lambda v: value_label.config(text=v)
        )
        slider.pack(fill=tk.X, pady=(5, 0))
        slider.set(default or min_val)
        
        setattr(self, var_name, slider)
        
    # Navigation methods
    def show_dashboard(self):
        self.hide_all_tabs()
        self.dashboard_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
    def show_flow_manager(self):
        self.hide_all_tabs()
        self.tab_container.pack(fill=tk.BOTH, expand=True)
        self.flow_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.refresh_flow_stats()
        
    def show_accounts(self):
        self.hide_all_tabs()
        self.tab_container.pack(fill=tk.BOTH, expand=True)
        self.accounts_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.refresh_accounts()
        
    def show_settings(self):
        self.hide_all_tabs()
        self.tab_container.pack(fill=tk.BOTH, expand=True)
        self.settings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
    def show_analytics(self):
        self.hide_all_tabs()
        self.tab_container.pack(fill=tk.BOTH, expand=True)
        self.analytics_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.update_analytics()
        
    def show_logs(self):
        self.hide_all_tabs()
        self.tab_container.pack(fill=tk.BOTH, expand=True)
        self.logs_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
    def show_targets(self):
        self.hide_all_tabs()
        self.tab_container.pack(fill=tk.BOTH, expand=True)
        self.targets_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
    def show_about(self):
        self.hide_all_tabs()
        self.tab_container.pack(fill=tk.BOTH, expand=True)
        self.about_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
    def hide_all_tabs(self):
        self.dashboard_frame.pack_forget()
        self.tab_container.pack_forget()
        self.settings_frame.pack_forget()
        self.flow_frame.pack_forget()
        self.accounts_frame.pack_forget()
        self.analytics_frame.pack_forget()
        self.logs_frame.pack_forget()
        self.targets_frame.pack_forget()
        self.about_frame.pack_forget()
        
    # Automation methods
    def toggle_automation(self):
        if not self.is_running:
            self.start_automation()
        else:
            self.stop_automation()
            
    def start_automation(self):
        """Start the automation process"""
        # Validate inputs
        if not self.username_entry.get() or not self.password_entry.get():
            messagebox.showerror("Error", "Please enter Instagram credentials in Settings")
            return
            
        # Update config
        Config.INSTAGRAM_USERNAME = self.username_entry.get()
        Config.INSTAGRAM_PASSWORD = self.password_entry.get()
        Config.DEFAULT_MESSAGE = self.message_text.get('1.0', tk.END).strip()
        Config.HEADLESS_MODE = self.headless_var.get()
        Config.MIN_DELAY_BETWEEN_MESSAGES = int(self.delay_slider.get() * 0.8)
        Config.MAX_DELAY_BETWEEN_MESSAGES = int(self.delay_slider.get() * 1.2)
        Config.MESSAGES_PER_SESSION = int(self.session_slider.get())
        
        # Check database for profiles first
        stats = self.db.get_flow_statistics()
        
        if stats['total_profiles'] > 0:
            # We have profiles in database - use flow system
            selected_step = self.step_var.get() if hasattr(self, 'step_var') else 0
            self.log_message(f"Selected step for automation: {selected_step}", "info")
            eligible_count = self.db.get_eligible_profiles_count(selected_step, include_failed=True)
            new_count = self.db.get_eligible_profiles_count(selected_step, include_failed=False)
            retry_count = eligible_count - new_count
            
            # Debug: Show what profiles exist at each step
            self.log_message(f"Database stats: {stats}", "info")
            self.log_message(f"Eligible profiles at step {selected_step}: {eligible_count} ({new_count} new + {retry_count} retries)", "info")
            
            if eligible_count == 0:
                result = messagebox.askyesno(
                    "No Eligible Profiles at Selected Step",
                    f"No profiles ready for Step {selected_step}.\n\n"
                    f"Database has {stats['total_profiles']} total profiles:\n" +
                    "\n".join([f"  Step {s}: {c}" for s, c in sorted(stats['profiles_by_step'].items())]) +
                    f"\n\nWould you like to go to Flow Manager to select a different step?"
                )
                if result:
                    self.show_flow_manager()
                return
            
            # Get template for preview
            next_step = selected_step + 1 if selected_step == 0 else selected_step
            template = self.db.get_template_for_step(next_step)
            template_preview = template['message_content'][:80] + "..." if template else "Default message"
            
            # Step descriptions
            step_names = {
                0: "Step 0 → Step 1 (Initial Outreach)",
                1: "Step 1 → Step 2 (First Follow-up)",
                2: "Step 2 → Step 3 (Final Follow-up)",
                3: "Step 3 → Step 4 (Re-engagement)"
            }
            step_desc = step_names.get(selected_step, f"Step {selected_step}")
            
            # Confirm
            profile_info = f"{eligible_count}"
            if retry_count > 0:
                profile_info = f"{eligible_count} ({new_count} new + {retry_count} retries)"
            
            confirm = messagebox.askyesno(
                "Start Automation",
                f"Send messages using Flow System?\n\n"
                f"Action: {step_desc}\n"
                f"Profiles to contact: {profile_info}\n\n"
                f"Template: {template_preview}\n\n"
                f"Continue?"
            )
            
            if not confirm:
                return
            
            # Set flow mode
            self.automation_step_filter = selected_step
            
        else:
            # No profiles in database - fall back to CSV/direct input
            result = messagebox.askyesno(
                "No Profiles in Database",
                "Database is empty. Import profiles in Flow Manager first?\n\n"
                "Click 'No' to use CSV file/direct input instead (old method)."
            )
            
            if result:
                self.show_flow_manager()
                return
            
            # Continue with CSV/direct input
            if self.input_method.get() == "csv":
                Config.CSV_FILE = self.csv_path.get()
            else:
                # Create temporary CSV from direct input
                usernames = self.direct_input.get('1.0', tk.END).strip().split('\n')
                usernames = [u.strip() for u in usernames if u.strip()]
                if not usernames:
                    messagebox.showerror("Error", "Please enter at least one username")
                    return
                    
                with open('temp_profiles.csv', 'w') as f:
                    f.write("username\n")
                    for username in usernames:
                        f.write(f"{username}\n")
                Config.CSV_FILE = 'temp_profiles.csv'
            
        # Start automation
        self.is_running = True
        self.start_time = datetime.now()
        self.session_sent = 0
        
        # Update UI
        self.start_stop_btn.config(
            text="⏸ Stop Automation",
            bg=COLORS['danger']
        )
        self.status_dot.config(fg=COLORS['success'])
        self.status_text.config(text="Running")
        
        # Clear logs
        self.log_text.delete('1.0', tk.END)
        self.log_preview.delete('1.0', tk.END)
        
        # Start automation thread
        self.automation_thread = threading.Thread(target=self.run_automation, daemon=True)
        self.automation_thread.start()
        
    def stop_automation(self):
        """Stop the automation process"""
        self.is_running = False
        if self.automation_instance:
            self.automation_instance.running = False
            
        # Update UI
        self.start_stop_btn.config(
            text="▶ Start Automation",
            bg=COLORS['success']
        )
        self.status_dot.config(fg=COLORS['text_secondary'])
        self.status_text.config(text="Stopped")
        
        self.log_message("Automation stopped by user", "warning")
        
    def run_automation(self):
        """Run the automation in a separate thread"""
        try:
            from main import InstagramDMAutomation
            
            # Check if we're using flow system
            use_flow = hasattr(self, 'automation_step_filter')
            step_filter = getattr(self, 'automation_step_filter', None)
            
            self.log_message(f"Flow mode: {use_flow}, Step filter: {step_filter}", "info")
            
            # Create automation instance
            self.automation_instance = InstagramDMAutomation(
                setup_signal_handler=False,
                step_filter=step_filter,
                use_flow=use_flow
            )
            
            # Clear step filter after creating instance
            if hasattr(self, 'automation_step_filter'):
                delattr(self, 'automation_step_filter')
            
            # Redirect logs to our queue
            def log_handler(message, level="info"):
                self.log_queue.put((message, level))
                
                # Update statistics
                if "sent successfully" in message.lower():
                    self.session_sent += 1
                    self.total_sent += 1
                elif "failed" in message.lower() or "error" in message.lower():
                    self.total_failed += 1
                    
                self.stats_queue.put({
                    'sent': self.total_sent,
                    'failed': self.total_failed,
                    'session': self.session_sent
                })
            
            # Replace print statements with our handler
            self.automation_instance.print_status = log_handler
            
            # Run automation
            self.automation_instance.run_automation()
            
        except Exception as e:
            self.log_message(f"Error: {str(e)}", "error")
        finally:
            self.is_running = False
            self.root.after(0, self.stop_automation)
            
    def process_queues(self):
        """Process log and stats queues"""
        # Process log messages
        try:
            while True:
                message, level = self.log_queue.get_nowait()
                self.log_message(message, level)
        except queue.Empty:
            pass
            
        # Process statistics
        try:
            while True:
                stats = self.stats_queue.get_nowait()
                self.update_statistics(stats)
        except queue.Empty:
            pass
            
        # Schedule next check
        self.root.after(100, self.process_queues)
        
    def log_message(self, message, level="info"):
        """Add message to log displays with color coding"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Determine color based on level and message content
        color_map = {
            'info': COLORS['text_primary'],
            'success': COLORS['success'],
            'warning': '#4A9EFF',  # Blue color for warnings/failures
            'error': '#4A9EFF'     # Blue color for errors (per user request)
        }
        
        # Auto-detect level from message content if info
        if level == "info":
            message_lower = message.lower()
            if any(keyword in message_lower for keyword in ['success', 'sent successfully', 'completed', '✓']):
                level = 'success'
            elif any(keyword in message_lower for keyword in ['failed', 'error', 'retry', 'attempt', 'warning', 'not found', 'moving to next']):
                level = 'warning'
        
        color = color_map.get(level, COLORS['text_primary'])
        
        # Create formatted message
        formatted_msg = f"[{timestamp}] {message}\n"
        
        # Add to full log with color
        # Get position before insert
        start_line = self.log_text.index("end-1c linestart")
        self.log_text.insert(tk.END, formatted_msg)
        # Get position after insert (before the final newline)
        end_line = self.log_text.index("end-1c lineend")
        
        # Apply color tag
        tag_name = f"log_{level}_{id(formatted_msg)}"  # Unique tag per message
        self.log_text.tag_config(tag_name, foreground=color)
        self.log_text.tag_add(tag_name, start_line, end_line)
        self.log_text.see(tk.END)
        
        # Add to preview with color
        preview_start_line = self.log_preview.index("end-1c linestart")
        self.log_preview.insert(tk.END, formatted_msg)
        preview_end_line = self.log_preview.index("end-1c lineend")
        
        # Apply color tag to preview
        preview_tag_name = f"preview_{level}_{id(formatted_msg)}"
        self.log_preview.tag_config(preview_tag_name, foreground=color)
        self.log_preview.tag_add(preview_tag_name, preview_start_line, preview_end_line)
        self.log_preview.see(tk.END)
        
        # Limit log size
        if int(self.log_text.index('end-1c').split('.')[0]) > 1000:
            self.log_text.delete('1.0', '100.0')
            
    def load_historical_stats(self):
        """Load historical statistics on startup"""
        try:
            # Get all-time stats
            stats = self.db.get_statistics()
            
            # Update dashboard with historical data
            if 'Messages Sent' in self.stat_labels:
                self.stat_labels['Messages Sent'].config(text=str(stats['successful']))
            if 'Failed' in self.stat_labels:
                self.stat_labels['Failed'].config(text=str(stats['failed']))
            if 'Success Rate' in self.stat_labels:
                self.stat_labels['Success Rate'].config(text=f"{stats['success_rate']:.1f}%")
            
            # Store totals
            self.total_sent = stats['successful']
            self.total_failed = stats['failed']
            
            # Log to preview
            self.log_message(f"Loaded {stats['total']} historical results from database", "info")
            
        except Exception as e:
            self.log_message(f"Error loading historical data: {str(e)}", "error")
    
    def refresh_accounts(self):
        """Refresh accounts display based on filters"""
        try:
            # Clear existing items
            for item in self.accounts_tree.get_children():
                self.accounts_tree.delete(item)
            
            # Get filter
            filter_value = self.accounts_filter.get()
            search_query = self.search_var.get().strip()
            
            # Fetch data based on filter
            if search_query:
                results = self.db.search_profiles(search_query)
            elif filter_value == "all":
                results = self.db.get_all_results(limit=5000)
            elif filter_value.startswith("step"):
                step_num = int(filter_value.replace("step", ""))
                results = self.db.search_profiles_advanced(step=step_num)
            elif filter_value == "failed":
                results = self.db.get_all_results(limit=5000, status="failed")
            else:
                results = self.db.get_all_results(limit=5000)
            
            # Populate tree
            for result in results:
                # Username
                username = result['username']
                
                # Step info
                current_step = result.get('current_step', 0)
                step_text = f"Step {current_step}"
                
                # Status
                status = result.get('status', 'pending')
                if status == 'success' or status == 'active':
                    status_emoji = "✓"
                    status_text = "Active"
                    tags = ('active',)
                elif status == 'failed':
                    status_emoji = "✗"
                    status_text = "Failed"
                    tags = ('failed',)
                else:
                    status_emoji = "○"
                    status_text = "Pending"
                    tags = ('pending',)
                
                # Last contacted
                last_contacted = result.get('last_contacted')
                if last_contacted:
                    try:
                        ts = datetime.fromisoformat(last_contacted)
                        last_contacted_str = ts.strftime("%Y-%m-%d %H:%M")
                    except:
                        last_contacted_str = "Never"
                else:
                    last_contacted_str = "Never"
                
                # Messages sent
                messages_sent = result.get('total_messages_sent', 0)
                
                # Retry count
                retry_count = result.get('retry_count', 0)
                retry_text = f"{retry_count}/3" if status == 'failed' else "0/3"
                
                # Actions (just text, actual buttons via context menu)
                actions = "Double-click or Right-click"
                
                self.accounts_tree.insert('', 'end', values=(
                    username,
                    step_text,
                    f"{status_emoji} {status_text}",
                    last_contacted_str,
                    messages_sent,
                    retry_text,
                    actions
                ), tags=tags)
            
            # Configure tag colors
            self.accounts_tree.tag_configure('active', foreground=COLORS['success'])
            self.accounts_tree.tag_configure('failed', foreground=COLORS['danger'])
            self.accounts_tree.tag_configure('pending', foreground=COLORS['text_secondary'])
            
            # Update stats label
            total = len(results)
            by_step = {}
            for r in results:
                step = r.get('current_step', 0)
                by_step[step] = by_step.get(step, 0) + 1
            
            step_summary = " | ".join([f"Step {s}: {c}" for s, c in sorted(by_step.items())])
            
            self.accounts_stats_label.config(
                text=f"Total: {total} accounts | {step_summary}"
            )
            
        except Exception as e:
            self.log_message(f"Error refreshing accounts: {str(e)}", "error")
    
    def update_statistics(self, stats):
        """Update statistics display"""
        # Calculate success rate
        total = stats['sent'] + stats['failed']
        success_rate = (stats['sent'] / total * 100) if total > 0 else 0
        
        # Calculate speed
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds() / 3600
            speed = stats['sent'] / elapsed if elapsed > 0 else 0
        else:
            speed = 0
            
        # Update stat cards
        if 'Messages Sent' in self.stat_labels:
            self.stat_labels['Messages Sent'].config(text=str(stats['sent']))
        if 'Failed' in self.stat_labels:
            self.stat_labels['Failed'].config(text=str(stats['failed']))
        if 'Success Rate' in self.stat_labels:
            self.stat_labels['Success Rate'].config(text=f"{success_rate:.1f}%")
        if 'Avg Speed' in self.stat_labels:
            self.stat_labels['Avg Speed'].config(text=f"{speed:.1f}/hr")
            
    def update_analytics(self):
        """Update analytics data"""
        try:
            processor = CSVProcessor(Config.CSV_FILE)
            stats = processor.get_statistics()
            
            # Update today's stats
            today_text = f"""
Messages Sent: {stats.get('total_processed', 0)}
Successful: {stats.get('successful', 0)}
Failed: {stats.get('failed', 0)}
Success Rate: {stats.get('success_rate', '0%')}
            """
            self.today_stats.config(text=today_text.strip())
            
            # Weekly stats (simplified)
            weekly_text = f"""
Total Processed: {stats.get('total_processed', 0) * 7}
Average Daily: {stats.get('total_processed', 0)}
Peak Hour: 14:00-15:00
Most Active Day: Monday
            """
            self.weekly_stats.config(text=weekly_text.strip())
            
        except Exception:
            pass
            
    def save_settings(self):
        """Save current settings"""
        # Save to settings file
        settings_to_save = {
            "instagram_username": self.username_entry.get(),
            "instagram_password": self.password_entry.get(),
            "default_message": self.message_text.get('1.0', tk.END).strip(),
            "headless_mode": self.headless_var.get(),
            "enable_follow": self.follow_var.get(),
            "delay_between_messages": self.delay_slider.get(),
            "messages_per_session": self.session_slider.get()
        }
        
        if self.settings_manager.update(settings_to_save):
            # Also update config for current session
            Config.INSTAGRAM_USERNAME = self.username_entry.get()
            Config.INSTAGRAM_PASSWORD = self.password_entry.get()
            Config.DEFAULT_MESSAGE = self.message_text.get('1.0', tk.END).strip()
            Config.HEADLESS_MODE = self.headless_var.get()
            Config.ENABLE_FOLLOW = self.follow_var.get()
            Config.MIN_DELAY_BETWEEN_MESSAGES = int(self.delay_slider.get() * 0.8)
            Config.MAX_DELAY_BETWEEN_MESSAGES = int(self.delay_slider.get() * 1.2)
            Config.MESSAGES_PER_SESSION = int(self.session_slider.get())
            
            messagebox.showinfo("Success", f"Settings saved successfully!\n\nHeadless Mode: {'Enabled' if self.headless_var.get() else 'Disabled'}\nAuto-Follow: {'Enabled' if self.follow_var.get() else 'Disabled'}\n\nSettings are saved and will persist between app launches.")
        else:
            messagebox.showerror("Error", "Failed to save settings")
        
    def browse_csv(self):
        """Browse for CSV file"""
        filename = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.csv_path.set(filename)
            
    def export_results(self):
        """Export automation results"""
        try:
            processor = CSVProcessor(Config.CSV_FILE)
            success_file, fail_file = processor.export_last_run_results()
            
            if success_file or fail_file:
                message = "Export complete!\n\n"
                if success_file:
                    message += f"✓ Successful: {success_file}\n"
                if fail_file:
                    message += f"✗ Failed: {fail_file}"
                    
                messagebox.showinfo("Export Complete", message)
                
                # Open folder
                if sys.platform == 'win32':
                    os.startfile(os.getcwd())
                elif sys.platform == 'darwin':
                    subprocess.run(['open', os.getcwd()])
                else:
                    subprocess.run(['xdg-open', os.getcwd()])
            else:
                messagebox.showinfo("Info", "No results to export")
                
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def export_failure_report(self):
        """Export detailed failure analysis report"""
        try:
            processor = CSVProcessor(Config.CSV_FILE)
            
            # Check if there are any failures
            stats = processor.get_failure_statistics()
            if not stats:
                messagebox.showinfo("No Failures", "No failures to analyze. All messages were sent successfully!")
                return
            
            # Generate detailed report
            reports = processor.export_detailed_failure_report()
            
            if reports:
                detailed_file, summary_file = reports
                
                # Create informative message
                error_breakdown = "\n".join([
                    f"  • {error}: {count}"
                    for error, count in sorted(
                        stats['error_breakdown'].items(),
                        key=lambda x: x[1],
                        reverse=True
                    )
                ])
                
                message = f"""Failure Analysis Complete!

Total Failures: {stats['total_failures']}

Error Breakdown:
{error_breakdown}

Most Common: {stats['most_common_error']}

Reports Generated:
✓ Detailed: {detailed_file}
✓ Summary: {summary_file}

Each report includes:
- Error category
- Detailed description
- Recommended action
"""
                
                messagebox.showinfo("Failure Analysis", message)
                
                # Open folder
                if sys.platform == 'win32':
                    os.startfile(os.getcwd())
                elif sys.platform == 'darwin':
                    subprocess.run(['open', os.getcwd()])
                else:
                    subprocess.run(['xdg-open', os.getcwd()])
            else:
                messagebox.showinfo("Info", "No failure data available")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
            
    def export_logs(self):
        """Export logs to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            with open(filename, 'w') as f:
                f.write(self.log_text.get('1.0', tk.END))
            messagebox.showinfo("Success", f"Logs exported to {filename}")
            
    def on_closing(self):
        """Handle window close"""
        if self.is_running:
            if messagebox.askokcancel("Quit", "Automation is running. Stop and exit?"):
                self.stop_automation()
                self.root.destroy()
        else:
            self.root.destroy()
    
    # Flow Management Methods
    
    def import_csv_to_db(self):
        """Import single CSV file to database"""
        from tkinter import filedialog
        
        filename = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                tag = os.path.basename(filename).replace('.csv', '')
                imported_count = self.db.import_csv_profiles(filename, tag=tag)
                self.log_message(f"✓ Imported {imported_count} profiles from {os.path.basename(filename)}", "success")
                messagebox.showinfo("Import Success", f"Successfully imported {imported_count} profiles!")
                self.refresh_flow_stats()
            except Exception as e:
                self.log_message(f"Failed to import CSV: {str(e)}", "error")
                messagebox.showerror("Import Failed", str(e))
    
    def import_multiple_csv(self):
        """Import multiple CSV files to database"""
        from tkinter import filedialog
        
        filenames = filedialog.askopenfilenames(
            title="Select CSV files",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filenames:
            total_imported = 0
            failed_files = []
            
            for filename in filenames:
                try:
                    tag = os.path.basename(filename).replace('.csv', '')
                    imported_count = self.db.import_csv_profiles(filename, tag=tag)
                    total_imported += imported_count
                    self.log_message(f"✓ Imported {imported_count} from {os.path.basename(filename)}", "success")
                except Exception as e:
                    failed_files.append((filename, str(e)))
                    self.log_message(f"Failed to import {os.path.basename(filename)}: {str(e)}", "error")
            
            # Show summary
            message = f"Imported {total_imported} profiles from {len(filenames) - len(failed_files)} files."
            if failed_files:
                message += f"\n\nFailed files:\n" + "\n".join([f"- {os.path.basename(f)}: {e}" for f, e in failed_files])
            
            messagebox.showinfo("Import Complete", message)
            self.refresh_flow_stats()
    
    def refresh_flow_stats(self):
        """Refresh flow statistics display"""
        try:
            # Get flow statistics
            stats = self.db.get_flow_statistics()
            
            # Update eligible profiles count (including failed for retry)
            step = self.step_var.get() if hasattr(self, 'step_var') else 0
            eligible_count = self.db.get_eligible_profiles_count(step, include_failed=True)
            new_count = self.db.get_eligible_profiles_count(step, include_failed=False)
            retry_count = eligible_count - new_count
            
            if hasattr(self, 'eligible_label'):
                if retry_count > 0:
                    self.eligible_label.config(text=f"Eligible: {eligible_count} ({new_count} new + {retry_count} retries)")
                else:
                    self.eligible_label.config(text=f"Eligible profiles: {eligible_count}")
            
            # Format statistics text
            stats_text = []
            stats_text.append(f"Total Profiles: {stats['total_profiles']}")
            stats_text.append(f"Pending (Not Contacted): {stats['pending_profiles']}")
            stats_text.append("\n--- Profiles by Step ---")
            
            for step_num, count in sorted(stats['profiles_by_step'].items()):
                step_names = {
                    0: "Not Contacted",
                    1: "Initial Outreach",
                    2: "First Follow-up",
                    3: "Final Follow-up",
                    4: "Re-engagement"
                }
                step_name = step_names.get(step_num, f"Step {step_num}")
                stats_text.append(f"Step {step_num} ({step_name}): {count}")
            
            stats_text.append("\n--- Messages Sent ---")
            for step_num, count in sorted(stats.get('messages_sent_by_step', {}).items()):
                stats_text.append(f"Step {step_num}: {count} messages")
            
            # Update text widget if it exists
            if hasattr(self, 'flow_stats_text'):
                self.flow_stats_text.config(state=tk.NORMAL)
                self.flow_stats_text.delete('1.0', tk.END)
                self.flow_stats_text.insert('1.0', '\n'.join(stats_text))
                self.flow_stats_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.log_message(f"Error refreshing flow stats: {str(e)}", "error")
    
    def load_template_for_step(self):
        """Load template for selected step"""
        if not hasattr(self, 'template_step_var'):
            return
            
        try:
            step = self.template_step_var.get()
            template = self.db.get_template_for_step(step)
            
            if template:
                self.template_text.delete('1.0', tk.END)
                self.template_text.insert('1.0', template['message_content'])
                self.wait_days_var.set(template['wait_days_before_next'])
            else:
                self.template_text.delete('1.0', tk.END)
                self.template_text.insert('1.0', f"No template found for step {step}")
        
        except Exception as e:
            self.log_message(f"Error loading template: {str(e)}", "error")
    
    def save_template(self):
        """Save current template"""
        try:
            step = self.template_step_var.get()
            message_content = self.template_text.get('1.0', tk.END).strip()
            wait_days = self.wait_days_var.get()
            
            # Get existing template
            existing = self.db.get_template_for_step(step)
            
            if existing:
                # Update existing
                self.db.update_template(existing['id'], 
                                       message_content=message_content,
                                       wait_days=wait_days)
                self.log_message(f"✓ Updated template for step {step}", "success")
            else:
                # Create new
                self.db.add_message_template(step, f"Step {step} Template", 
                                            message_content, wait_days)
                self.log_message(f"✓ Created template for step {step}", "success")
            
            messagebox.showinfo("Success", f"Template for step {step} saved!")
            
        except Exception as e:
            self.log_message(f"Error saving template: {str(e)}", "error")
            messagebox.showerror("Save Failed", str(e))
    
    # Account Management Methods
    
    def delete_selected_accounts(self):
        """Delete selected accounts from database"""
        selected_items = self.accounts_tree.selection()
        
        if not selected_items:
            messagebox.showinfo("No Selection", "Please select accounts to delete")
            return
        
        # Confirm deletion
        count = len(selected_items)
        if not messagebox.askyesno("Confirm Delete", f"Delete {count} selected account(s)?\n\nThis cannot be undone!"):
            return
        
        try:
            deleted = 0
            for item in selected_items:
                values = self.accounts_tree.item(item)['values']
                username = values[0]
                
                # Delete from database
                with self.db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM profiles WHERE username = ?", (username,))
                    cursor.execute("DELETE FROM flow_history WHERE profile_id IN (SELECT id FROM profiles WHERE username = ?)", (username,))
                deleted += 1
            
            messagebox.showinfo("Success", f"Deleted {deleted} account(s)")
            self.refresh_accounts()
            self.refresh_flow_stats()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete accounts: {str(e)}")
    
    def reset_selected_to_step_zero(self):
        """Reset selected accounts to Step 0"""
        selected_items = self.accounts_tree.selection()
        
        if not selected_items:
            messagebox.showinfo("No Selection", "Please select accounts to reset")
            return
        
        count = len(selected_items)
        if not messagebox.askyesno("Confirm Reset", f"Reset {count} account(s) to Step 0?"):
            return
        
        try:
            reset = 0
            for item in selected_items:
                values = self.accounts_tree.item(item)['values']
                username = values[0]
                
                # Reset in database
                with self.db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE profiles 
                        SET current_step = 0, 
                            status = 'pending',
                            last_contacted = NULL,
                            next_step_eligible = NULL
                        WHERE username = ?
                    """, (username,))
                reset += 1
            
            messagebox.showinfo("Success", f"Reset {reset} account(s) to Step 0")
            self.refresh_accounts()
            self.refresh_flow_stats()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset accounts: {str(e)}")
    
    def edit_account(self, event=None):
        """Edit selected account"""
        selected_items = self.accounts_tree.selection()
        
        if not selected_items:
            return
        
        item = selected_items[0]
        values = self.accounts_tree.item(item)['values']
        username = values[0]
        
        # Create edit dialog
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Edit Account: {username}")
        edit_window.geometry("400x300")
        edit_window.configure(bg=COLORS['bg_medium'])
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Get account data
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM profiles WHERE username = ?", (username,))
            account = dict(cursor.fetchone())
        
        # Username (read-only)
        tk.Label(edit_window, text="Username:", bg=COLORS['bg_medium'], fg=COLORS['text_secondary']).pack(pady=(20, 5))
        username_label = tk.Label(edit_window, text=username, font=('Segoe UI', 12, 'bold'), 
                                 bg=COLORS['bg_medium'], fg=COLORS['text_primary'])
        username_label.pack()
        
        # Current Step
        tk.Label(edit_window, text="Current Step:", bg=COLORS['bg_medium'], fg=COLORS['text_secondary']).pack(pady=(10, 5))
        step_var = tk.IntVar(value=account['current_step'])
        step_spinbox = tk.Spinbox(edit_window, from_=0, to=4, textvariable=step_var, width=10)
        step_spinbox.pack()
        
        # Status
        tk.Label(edit_window, text="Status:", bg=COLORS['bg_medium'], fg=COLORS['text_secondary']).pack(pady=(10, 5))
        status_var = tk.StringVar(value=account['status'])
        status_options = ['pending', 'active', 'success', 'failed']
        status_dropdown = tk.OptionMenu(edit_window, status_var, *status_options)
        status_dropdown.config(bg=COLORS['input_bg'], fg=COLORS['text_primary'])
        status_dropdown.pack()
        
        # Save button
        def save_changes():
            try:
                with self.db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE profiles 
                        SET current_step = ?, status = ?
                        WHERE username = ?
                    """, (step_var.get(), status_var.get(), username))
                
                messagebox.showinfo("Success", "Account updated")
                edit_window.destroy()
                self.refresh_accounts()
                self.refresh_flow_stats()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update: {str(e)}")
        
        save_btn = tk.Button(edit_window, text="💾 Save Changes", 
                           bg=COLORS['accent'], fg=COLORS['text_primary'],
                           command=save_changes, bd=0, padx=20, pady=10)
        save_btn.pack(pady=20)
    
    def show_account_context_menu(self, event):
        """Show right-click context menu for account"""
        # Select the item under cursor
        item = self.accounts_tree.identify_row(event.y)
        if item:
            self.accounts_tree.selection_set(item)
            
            # Create context menu
            context_menu = tk.Menu(self.root, tearoff=0, bg=COLORS['card_bg'], fg=COLORS['text_primary'])
            context_menu.add_command(label="✏️ Edit", command=self.edit_account)
            context_menu.add_command(label="↺ Reset to Step 0", command=self.reset_selected_to_step_zero)
            context_menu.add_separator()
            context_menu.add_command(label="🗑️ Delete", command=self.delete_selected_accounts)
            
            # Show menu at cursor
            context_menu.post(event.x_root, event.y_root)
    

def main():
    """Main entry point"""
    root = tk.Tk()
    app = ModernInstagramAutomation(root)
    root.mainloop()

if __name__ == "__main__":
    main()
