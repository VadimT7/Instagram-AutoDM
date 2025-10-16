"""
CSV file processor for Instagram profiles
"""
import pandas as pd
import os
from datetime import datetime
import json

class CSVProcessor:
    def __init__(self, csv_file="InstagramProfiles.csv"):
        self.csv_file = csv_file
        self.profiles_df = None
        self.processed_file = "processed_profiles.json"
        self.processed_profiles = self.load_processed_profiles()
        
    def load_csv(self):
        """Load CSV file with Instagram profile usernames or links"""
        try:
            if not os.path.exists(self.csv_file):
                raise FileNotFoundError(f"CSV file not found: {self.csv_file}")
            
            self.profiles_df = pd.read_csv(self.csv_file)
            
            # Check if 'username' or 'link' column exists
            if 'username' in self.profiles_df.columns:
                # Convert usernames to full Instagram URLs
                self.profiles_df['username'] = self.profiles_df['username'].str.strip()
                self.profiles_df = self.profiles_df[self.profiles_df['username'].notna()]
                
                # Remove any @ symbols if present
                self.profiles_df['username'] = self.profiles_df['username'].str.replace('@', '', regex=False)
                
                # Construct full URLs from usernames
                self.profiles_df['link'] = self.profiles_df['username'].apply(
                    lambda x: f"https://www.instagram.com/{x}/" if not x.startswith('http') else x
                )
                
                print(f"Loaded {len(self.profiles_df)} Instagram usernames and converted to URLs")
                
            elif 'link' in self.profiles_df.columns:
                # Original format - clean and validate links
                self.profiles_df['link'] = self.profiles_df['link'].str.strip()
                self.profiles_df = self.profiles_df[self.profiles_df['link'].notna()]
                
                # Ensure links are Instagram URLs
                instagram_pattern = r'(instagram\.com|instagr\.am)'
                valid_links = self.profiles_df['link'].str.contains(instagram_pattern, case=False, na=False)
                invalid_count = (~valid_links).sum()
                
                if invalid_count > 0:
                    print(f"Warning: {invalid_count} invalid Instagram URLs found and will be skipped")
                    self.profiles_df = self.profiles_df[valid_links]
                
                print(f"Loaded {len(self.profiles_df)} valid Instagram profiles")
            else:
                raise ValueError("CSV file must contain either a 'username' or 'link' column")
            
            return True
            
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return False
    
    def get_profiles(self):
        """Get list of profile links"""
        if self.profiles_df is None:
            if not self.load_csv():
                return []
        
        return self.profiles_df['link'].tolist()
    
    def get_unprocessed_profiles(self):
        """Get profiles that haven't been processed yet"""
        all_profiles = self.get_profiles()
        unprocessed = [p for p in all_profiles if p not in self.processed_profiles]
        return unprocessed
    
    def mark_profile_processed(self, profile_url, status="success", message=""):
        """Mark a profile as processed"""
        self.processed_profiles[profile_url] = {
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "message": message
        }
        self.save_processed_profiles()
    
    def load_processed_profiles(self):
        """Load previously processed profiles"""
        if os.path.exists(self.processed_file):
            try:
                with open(self.processed_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_processed_profiles(self):
        """Save processed profiles to file"""
        with open(self.processed_file, 'w') as f:
            json.dump(self.processed_profiles, f, indent=2)
    
    def get_statistics(self):
        """Get processing statistics"""
        total = len(self.get_profiles())
        processed = len(self.processed_profiles)
        successful = sum(1 for p in self.processed_profiles.values() if p['status'] == 'success')
        failed = sum(1 for p in self.processed_profiles.values() if p['status'] == 'failed')
        
        return {
            "total": total,
            "processed": processed,
            "remaining": total - processed,
            "successful": successful,
            "failed": failed
        }
    
    def reset_processed(self):
        """Reset processed profiles (use with caution)"""
        self.processed_profiles = {}
        if os.path.exists(self.processed_file):
            os.remove(self.processed_file)
        print("Processed profiles have been reset")
    
    def export_report(self, filename="message_report.csv"):
        """Export a report of all processed profiles"""
        if not self.processed_profiles:
            print("No processed profiles to export")
            return
        
        report_data = []
        for url, data in self.processed_profiles.items():
            report_data.append({
                "profile_url": url,
                "timestamp": data.get("timestamp", ""),
                "status": data.get("status", ""),
                "message": data.get("message", "")
            })
        
        df = pd.DataFrame(report_data)
        df.to_csv(filename, index=False)
        print(f"Report exported to {filename}")
    
    def export_last_run_results(self):
        """Export successful and unsuccessful sends from the last run as separate CSV files"""
        if not self.processed_profiles:
            print("No processed profiles to export")
            return None, None
        
        # Get the latest run timestamp (last 24 hours)
        from datetime import datetime, timedelta
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        successful = []
        unsuccessful = []
        
        for url, data in self.processed_profiles.items():
            try:
                timestamp = datetime.fromisoformat(data.get("timestamp", ""))
                if timestamp > cutoff_time:  # From recent run
                    username = url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]
                    
                    if data.get("status") == "success":
                        successful.append({
                            "username": username,
                            "profile_url": url,
                            "timestamp": data.get("timestamp", ""),
                            "message_sent": data.get("message", "")
                        })
                    else:
                        unsuccessful.append({
                            "username": username,
                            "profile_url": url,
                            "timestamp": data.get("timestamp", ""),
                            "error": data.get("message", "")
                        })
            except:
                continue
        
        # Export successful sends
        success_file = f"successful_sends_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        if successful:
            df_success = pd.DataFrame(successful)
            df_success.to_csv(success_file, index=False)
            print(f"✓ Successful sends exported to {success_file} ({len(successful)} profiles)")
        else:
            success_file = None
            print("No successful sends to export")
        
        # Export unsuccessful sends  
        fail_file = f"unsuccessful_sends_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        if unsuccessful:
            df_fail = pd.DataFrame(unsuccessful)
            df_fail.to_csv(fail_file, index=False)
            print(f"✗ Unsuccessful sends exported to {fail_file} ({len(unsuccessful)} profiles)")
        else:
            fail_file = None
            print("No unsuccessful sends to export")
        
        return success_file, fail_file
