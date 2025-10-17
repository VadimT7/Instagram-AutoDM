"""
Settings Manager - Persistent storage for application settings
"""
import json
import os
from pathlib import Path


class SettingsManager:
    def __init__(self, settings_file="app_settings.json"):
        self.settings_file = settings_file
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Load settings from file"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
                return self.get_default_settings()
        return self.get_default_settings()
    
    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get_default_settings(self):
        """Get default settings"""
        return {
            "instagram_username": "",
            "instagram_password": "",
            "default_message": "Hey,\n\nLove the cars in your line-up - awesome machines!\n\nA close friend told me about your rental company.\nI just checked your Instagram and, man, you're losing money without a site that generates you bookings.\n\nSo, I created a live website w/ your cars for you. I can send you the link and, if you like it, we can work together. If no, no problem.\n\nIf you want to see it, reply with \"Yes\" and I will send you your new luxurious website, tailored just to your rental company.",
            "headless_mode": True,
            "enable_follow": False,
            "delay_between_messages": 30,
            "messages_per_session": 20,
            "daily_message_limit": 200,
            "last_csv_path": ""
        }
    
    def get(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """Set a setting value"""
        self.settings[key] = value
        return self.save_settings()
    
    def update(self, settings_dict):
        """Update multiple settings at once"""
        self.settings.update(settings_dict)
        return self.save_settings()

