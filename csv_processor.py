"""
CSV file processor for Instagram profiles
"""
import pandas as pd
import os
from datetime import datetime
import json
from database import AutomationDatabase

class CSVProcessor:
    def __init__(self, csv_file="InstagramProfiles.csv"):
        self.csv_file = csv_file
        self.profiles_df = None
        self.processed_file = "processed_profiles.json"
        self.processed_profiles = self.load_processed_profiles()
        self.db = AutomationDatabase()  # Initialize database
        
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
    
    def mark_profile_processed(self, profile_url, status="success", message="", error_type=None):
        """Mark a profile as processed with detailed error tracking"""
        timestamp = datetime.now()
        
        # Save to JSON (legacy support)
        self.processed_profiles[profile_url] = {
            "timestamp": timestamp.isoformat(),
            "status": status,
            "message": message,
            "error_type": error_type if status == "failed" else None
        }
        self.save_processed_profiles()
        
        # Also save to database
        username = profile_url.split('/')[-2] if profile_url.endswith('/') else profile_url.split('/')[-1]
        self.db.add_profile_result(
            username=username,
            profile_url=profile_url,
            status=status,
            message_sent=message if status == "success" else None,
            error_type=error_type,
            error_details=message if status == "failed" else None,
            timestamp=timestamp
        )
        
        # Update daily stats
        self.db.update_daily_stats()
    
    def categorize_error(self, error_message):
        """Categorize error based on error message"""
        error_message_lower = error_message.lower()
        
        if "login" in error_message_lower or "credentials" in error_message_lower:
            return "Login Failed"
        elif "message button" in error_message_lower or "button not found" in error_message_lower:
            return "Message Button Not Found"
        elif "follow button" in error_message_lower:
            return "Follow Button Not Found"
        elif "navigate" in error_message_lower or "navigation" in error_message_lower:
            return "Navigation Error"
        elif "message input" in error_message_lower or "text field" in error_message_lower:
            return "Message Input Field Not Found"
        elif "private" in error_message_lower:
            return "Private Account"
        elif "block" in error_message_lower or "restricted" in error_message_lower:
            return "Account Blocked/Restricted"
        elif "timeout" in error_message_lower:
            return "Timeout Error"
        elif "network" in error_message_lower or "connection" in error_message_lower:
            return "Network Error"
        elif "move target out of bounds" in error_message_lower:
            return "Element Interaction Error"
        else:
            return "Other Error"
    
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
                        error_msg = data.get("message", "")
                        error_type = data.get("error_type") or self.categorize_error(error_msg)
                        unsuccessful.append({
                            "username": username,
                            "profile_url": url,
                            "timestamp": data.get("timestamp", ""),
                            "error_type": error_type,
                            "error_details": error_msg
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
    
    def export_detailed_failure_report(self, filename=None):
        """Export a comprehensive failure report with error analysis and categorization"""
        if not self.processed_profiles:
            print("No processed profiles to analyze")
            return None
        
        # Collect all failures
        failures = []
        error_counts = {}
        
        for url, data in self.processed_profiles.items():
            if data.get("status") == "failed":
                username = url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]
                error_msg = data.get("message", "Unknown error")
                error_type = data.get("error_type") or self.categorize_error(error_msg)
                
                # Count error types
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
                
                # Parse timestamp
                try:
                    timestamp = datetime.fromisoformat(data.get("timestamp", ""))
                    date_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    date_str = data.get("timestamp", "")
                
                failures.append({
                    "username": username,
                    "profile_url": url,
                    "date_time": date_str,
                    "error_category": error_type,
                    "error_description": error_msg,
                    "recommended_action": self.get_recommended_action(error_type)
                })
        
        if not failures:
            print("No failures to report")
            return None
        
        # Generate filename if not provided
        if filename is None:
            filename = f"failure_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Create DataFrame with sorted data
        df = pd.DataFrame(failures)
        df = df.sort_values(by=['error_category', 'date_time'], ascending=[True, False])
        
        # Export main report
        df.to_csv(filename, index=False)
        
        # Generate summary report
        summary_filename = filename.replace('.csv', '_summary.csv')
        summary_data = [
            {"error_category": category, "count": count, "percentage": f"{count/len(failures)*100:.1f}%"}
            for category, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        ]
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_csv(summary_filename, index=False)
        
        # Print statistics
        print(f"\n{'='*60}")
        print(f"FAILURE ANALYSIS REPORT")
        print(f"{'='*60}")
        print(f"Total Failures: {len(failures)}")
        print(f"\nError Breakdown:")
        for category, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = count/len(failures)*100
            print(f"  • {category}: {count} ({percentage:.1f}%)")
        print(f"\n{'='*60}")
        print(f"✓ Detailed report: {filename}")
        print(f"✓ Summary report: {summary_filename}")
        print(f"{'='*60}\n")
        
        return filename, summary_filename
    
    def get_recommended_action(self, error_type):
        """Get recommended action for each error type"""
        recommendations = {
            "Login Failed": "Check Instagram credentials in settings. May need to verify account from phone/email.",
            "Message Button Not Found": "Profile may be private or has disabled messaging. Try following first or skip.",
            "Follow Button Not Found": "Profile may have restricted actions. Try refreshing or skip.",
            "Navigation Error": "Connection issue or Instagram layout changed. Check internet connection.",
            "Message Input Field Not Found": "Chat window didn't load properly. Increase delays or retry.",
            "Private Account": "Account is private and has not accepted follow request. Skip or manual follow required.",
            "Account Blocked/Restricted": "Your account may be temporarily restricted. Wait 24-48 hours and reduce frequency.",
            "Timeout Error": "Page took too long to load. Check internet connection or increase timeout settings.",
            "Network Error": "Connection lost during operation. Check internet stability.",
            "Element Interaction Error": "Browser element issue. May need to update Chrome or undetected-chromedriver.",
            "Other Error": "Unexpected error. Check logs for details or contact support."
        }
        return recommendations.get(error_type, "Review error details and check logs for more information.")
    
    def get_failure_statistics(self):
        """Get detailed failure statistics"""
        total_failures = sum(1 for p in self.processed_profiles.values() if p['status'] == 'failed')
        
        if total_failures == 0:
            return None
        
        error_counts = {}
        for data in self.processed_profiles.values():
            if data.get("status") == "failed":
                error_msg = data.get("message", "Unknown error")
                error_type = data.get("error_type") or self.categorize_error(error_msg)
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        return {
            "total_failures": total_failures,
            "error_breakdown": error_counts,
            "most_common_error": max(error_counts.items(), key=lambda x: x[1])[0] if error_counts else None
        }
