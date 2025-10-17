"""
SQLite Database Manager for Instagram Automation
Persists all results and provides historical tracking
"""

import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

class AutomationDatabase:
    def __init__(self, db_path="automation_history.db"):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database with required tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Profiles table - stores all processed profiles with flow tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    profile_url TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL,
                    message_sent TEXT,
                    error_type TEXT,
                    error_details TEXT,
                    timestamp DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    current_step INTEGER DEFAULT 0,
                    last_contacted DATETIME,
                    next_step_eligible DATETIME,
                    total_messages_sent INTEGER DEFAULT 0,
                    retry_count INTEGER DEFAULT 0,
                    last_retry DATETIME,
                    imported_from TEXT,
                    tags TEXT
                )
            """)
            
            # Sessions table - tracks automation runs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME,
                    total_processed INTEGER DEFAULT 0,
                    successful INTEGER DEFAULT 0,
                    failed INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'running',
                    notes TEXT
                )
            """)
            
            # Statistics table - daily aggregated stats
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL UNIQUE,
                    total_sent INTEGER DEFAULT 0,
                    total_failed INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0.0,
                    most_common_error TEXT
                )
            """)
            
            # Message templates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS message_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    step_number INTEGER NOT NULL,
                    template_name TEXT NOT NULL,
                    message_content TEXT NOT NULL,
                    wait_days_before_next INTEGER DEFAULT 3,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Flow history table - tracks each message sent in the flow
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS flow_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id INTEGER NOT NULL,
                    step_number INTEGER NOT NULL,
                    message_sent TEXT,
                    sent_at DATETIME NOT NULL,
                    response_received BOOLEAN DEFAULT 0,
                    FOREIGN KEY (profile_id) REFERENCES profiles(id)
                )
            """)
            
            # Imported CSV tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS csv_imports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    total_profiles INTEGER,
                    imported_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    import_tag TEXT
                )
            """)
            
            # Add columns if they don't exist (for migration from old schema)
            # Check if we need to migrate
            cursor.execute("PRAGMA table_info(profiles)")
            existing_columns = {row[1] for row in cursor.fetchall()}
            
            if 'current_step' not in existing_columns:
                cursor.execute("ALTER TABLE profiles ADD COLUMN current_step INTEGER DEFAULT 0")
            if 'last_contacted' not in existing_columns:
                cursor.execute("ALTER TABLE profiles ADD COLUMN last_contacted DATETIME")
            if 'next_step_eligible' not in existing_columns:
                cursor.execute("ALTER TABLE profiles ADD COLUMN next_step_eligible DATETIME")
            if 'total_messages_sent' not in existing_columns:
                cursor.execute("ALTER TABLE profiles ADD COLUMN total_messages_sent INTEGER DEFAULT 0")
            if 'imported_from' not in existing_columns:
                cursor.execute("ALTER TABLE profiles ADD COLUMN imported_from TEXT")
            if 'tags' not in existing_columns:
                cursor.execute("ALTER TABLE profiles ADD COLUMN tags TEXT")
            if 'retry_count' not in existing_columns:
                cursor.execute("ALTER TABLE profiles ADD COLUMN retry_count INTEGER DEFAULT 0")
            if 'last_retry' not in existing_columns:
                cursor.execute("ALTER TABLE profiles ADD COLUMN last_retry DATETIME")
            
            # Create indexes for performance (after ensuring columns exist)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_profiles_timestamp 
                ON profiles(timestamp)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_profiles_status 
                ON profiles(status)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_profiles_step 
                ON profiles(current_step)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_start_time 
                ON sessions(start_time)
            """)
    
    def add_profile_result(self, username, profile_url, status, message_sent=None,
                          error_type=None, error_details=None, timestamp=None):
        """Add or update a profile result"""
        if timestamp is None:
            timestamp = datetime.now()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if profile already exists
            cursor.execute("SELECT id FROM profiles WHERE profile_url = ?", (profile_url,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record
                cursor.execute("""
                    UPDATE profiles 
                    SET username = ?, status = ?, message_sent = ?, 
                        error_type = ?, error_details = ?, timestamp = ?
                    WHERE profile_url = ?
                """, (username, status, message_sent, error_type, error_details, 
                      timestamp, profile_url))
            else:
                # Insert new record
                cursor.execute("""
                    INSERT INTO profiles 
                    (username, profile_url, status, message_sent, error_type, 
                     error_details, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (username, profile_url, status, message_sent, error_type,
                      error_details, timestamp))
    
    def start_session(self, notes=None):
        """Start a new automation session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sessions (start_time, notes)
                VALUES (?, ?)
            """, (datetime.now(), notes))
            return cursor.lastrowid
    
    def end_session(self, session_id, total_processed, successful, failed):
        """End an automation session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE sessions 
                SET end_time = ?, total_processed = ?, successful = ?, 
                    failed = ?, status = 'completed'
                WHERE id = ?
            """, (datetime.now(), total_processed, successful, failed, session_id))
    
    def update_daily_stats(self, date=None):
        """Update daily statistics"""
        if date is None:
            date = datetime.now().date()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Calculate stats for the day
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
                FROM profiles
                WHERE DATE(timestamp) = ?
            """, (date,))
            
            row = cursor.fetchone()
            total = row['total'] or 0
            successful = row['successful'] or 0
            failed = row['failed'] or 0
            success_rate = (successful / total * 100) if total > 0 else 0
            
            # Get most common error
            cursor.execute("""
                SELECT error_type, COUNT(*) as count
                FROM profiles
                WHERE DATE(timestamp) = ? AND status = 'failed'
                GROUP BY error_type
                ORDER BY count DESC
                LIMIT 1
            """, (date,))
            
            error_row = cursor.fetchone()
            most_common_error = error_row['error_type'] if error_row else None
            
            # Insert or update daily stats
            cursor.execute("""
                INSERT INTO daily_stats 
                (date, total_sent, total_failed, success_rate, most_common_error)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(date) DO UPDATE SET
                    total_sent = excluded.total_sent,
                    total_failed = excluded.total_failed,
                    success_rate = excluded.success_rate,
                    most_common_error = excluded.most_common_error
            """, (date, successful, failed, success_rate, most_common_error))
    
    def get_all_results(self, limit=None, status=None):
        """Get all profile results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM profiles"
            params = []
            
            if status:
                query += " WHERE status = ?"
                params.append(status)
            
            query += " ORDER BY timestamp DESC"
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_recent_results(self, days=7):
        """Get results from last N days"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM profiles
                WHERE timestamp >= datetime('now', '-' || ? || ' days')
                ORDER BY timestamp DESC
            """, (days,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_statistics(self, days=None):
        """Get overall statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            time_filter = ""
            params = []
            if days:
                time_filter = "WHERE timestamp >= datetime('now', '-' || ? || ' days')"
                params.append(days)
            
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
                FROM profiles
                {time_filter}
            """, params)
            
            row = cursor.fetchone()
            total = row['total'] or 0
            successful = row['successful'] or 0
            failed = row['failed'] or 0
            
            return {
                'total': total,
                'successful': successful,
                'failed': failed,
                'success_rate': (successful / total * 100) if total > 0 else 0
            }
    
    def get_error_breakdown(self, days=None):
        """Get breakdown of errors by type"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            time_filter = ""
            params = []
            if days:
                time_filter = "AND timestamp >= datetime('now', '-' || ? || ' days')"
                params.append(days)
            
            cursor.execute(f"""
                SELECT error_type, COUNT(*) as count
                FROM profiles
                WHERE status = 'failed' {time_filter}
                GROUP BY error_type
                ORDER BY count DESC
            """, params)
            
            return {row['error_type']: row['count'] for row in cursor.fetchall()}
    
    def get_sessions(self, limit=10):
        """Get recent sessions"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM sessions
                ORDER BY start_time DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_daily_stats(self, days=30):
        """Get daily statistics for charting"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM daily_stats
                WHERE date >= date('now', '-' || ? || ' days')
                ORDER BY date DESC
            """, (days,))
            return [dict(row) for row in cursor.fetchall()]
    
    def search_profiles(self, username_query):
        """Search for profiles by username"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM profiles
                WHERE username LIKE ?
                ORDER BY timestamp DESC
            """, (f'%{username_query}%',))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_total_sent_all_time(self):
        """Get total messages sent ever"""
        stats = self.get_statistics()
        return stats['successful']
    
    def export_to_csv(self, filename, status=None, days=None):
        """Export database results to CSV"""
        import pandas as pd
        
        with self.get_connection() as conn:
            query = "SELECT * FROM profiles"
            conditions = []
            params = []
            
            if status:
                conditions.append("status = ?")
                params.append(status)
            
            if days:
                conditions.append("timestamp >= datetime('now', '-' || ? || ' days')")
                params.append(days)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY timestamp DESC"
            
            df = pd.read_sql_query(query, conn, params=params)
            df.to_csv(filename, index=False)
            return filename
    
    def clear_old_data(self, days=90):
        """Clear data older than N days (for maintenance)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM profiles
                WHERE timestamp < datetime('now', '-' || ? || ' days')
            """, (days,))
            deleted = cursor.rowcount
            return deleted
    
    def backup_database(self, backup_path=None):
        """Create a backup of the database"""
        import shutil
        
        if backup_path is None:
            backup_path = f"{self.db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        shutil.copy2(self.db_path, backup_path)
        return backup_path
    
    # Flow Management Methods
    
    def import_csv_profiles(self, csv_file, tag=None):
        """Import profiles from CSV directly into database"""
        import pandas as pd
        from datetime import datetime
        
        try:
            df = pd.read_csv(csv_file)
            imported_count = 0
            
            # Track the import
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO csv_imports (filename, total_profiles, import_tag)
                    VALUES (?, ?, ?)
                """, (csv_file, len(df), tag))
                import_id = cursor.lastrowid
            
            # Process each row
            for _, row in df.iterrows():
                username = None
                profile_url = None
                
                if 'username' in df.columns:
                    username = str(row['username']).strip().replace('@', '')
                    profile_url = f"https://www.instagram.com/{username}/"
                elif 'link' in df.columns:
                    profile_url = row['link']
                    username = profile_url.split('/')[-2] if profile_url.endswith('/') else profile_url.split('/')[-1]
                
                if username and profile_url:
                    self.add_profile_for_flow(
                        username=username,
                        profile_url=profile_url,
                        imported_from=csv_file,
                        tags=tag
                    )
                    imported_count += 1
            
            return imported_count
        
        except Exception as e:
            raise Exception(f"Error importing CSV: {str(e)}")
    
    def add_profile_for_flow(self, username, profile_url, imported_from=None, tags=None):
        """Add a profile to the database for flow management"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if profile exists
            cursor.execute("SELECT id, current_step FROM profiles WHERE profile_url = ?", (profile_url,))
            existing = cursor.fetchone()
            
            if not existing:
                # Insert new profile
                cursor.execute("""
                    INSERT INTO profiles 
                    (username, profile_url, status, current_step, timestamp, 
                     imported_from, tags, total_messages_sent)
                    VALUES (?, ?, 'pending', 0, ?, ?, ?, 0)
                """, (username, profile_url, datetime.now(), imported_from, tags))
                return cursor.lastrowid
            else:
                # Update existing profile
                cursor.execute("""
                    UPDATE profiles 
                    SET imported_from = ?, tags = ?
                    WHERE profile_url = ?
                """, (imported_from, tags, profile_url))
                return existing['id']
    
    def get_profiles_by_step(self, step_number, limit=None, include_failed=True, max_retries=None):
        """Get profiles at a specific step in the flow, including failed accounts for retry"""
        from config import Config
        
        if max_retries is None:
            max_retries = Config.MAX_DATABASE_RETRIES
            
        cooldown_minutes = Config.RETRY_COOLDOWN_MINUTES
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if include_failed:
                # Include both pending/active profiles and failed profiles eligible for retry
                query = """
                    SELECT * FROM profiles 
                    WHERE current_step = ? 
                    AND (
                        (status IN ('pending', 'active', 'success') 
                         AND (next_step_eligible IS NULL OR next_step_eligible <= datetime('now')))
                        OR 
                        (status = 'failed' 
                         AND retry_count < ? 
                         AND (last_retry IS NULL OR last_retry <= datetime('now', '-{} minutes')))
                    )
                    ORDER BY 
                        CASE 
                            WHEN status = 'failed' THEN 1  -- Prioritize failed accounts for retry
                            ELSE 2 
                        END,
                        last_contacted ASC
                """.format(cooldown_minutes)
                cursor.execute(query, (step_number, max_retries))
            else:
                # Original logic - only pending/active profiles
                query = """
                    SELECT * FROM profiles 
                    WHERE current_step = ? 
                    AND (next_step_eligible IS NULL OR next_step_eligible <= datetime('now'))
                    ORDER BY last_contacted ASC
                """
                cursor.execute(query, (step_number,))
            
            results = [dict(row) for row in cursor.fetchall()]
            
            if limit:
                results = results[:limit]
            
            return results
    
    def update_profile_step(self, profile_id, new_step, message_sent, wait_days=3):
        """Update profile's current step after sending a message"""
        from datetime import datetime, timedelta
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            next_eligible = datetime.now() + timedelta(days=wait_days)
            
            cursor.execute("""
                UPDATE profiles 
                SET current_step = ?, 
                    last_contacted = ?, 
                    next_step_eligible = ?,
                    total_messages_sent = total_messages_sent + 1,
                    status = 'active',
                    retry_count = 0  -- Reset retry count on success
                WHERE id = ?
            """, (new_step, datetime.now(), next_eligible, profile_id))
            
            # Add to flow history
            cursor.execute("""
                INSERT INTO flow_history 
                (profile_id, step_number, message_sent, sent_at)
                VALUES (?, ?, ?, ?)
            """, (profile_id, new_step, message_sent, datetime.now()))
    
    def update_profile_failure(self, profile_id, error_type, error_details):
        """Update profile with failure information and increment retry count"""
        from datetime import datetime
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE profiles 
                SET status = 'failed',
                    error_type = ?,
                    error_details = ?,
                    last_retry = datetime('now'),
                    retry_count = retry_count + 1
                WHERE id = ?
            """, (error_type, error_details, profile_id))
    
    # Template Management
    
    def add_message_template(self, step_number, template_name, message_content, wait_days=3):
        """Add a message template for a specific step"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO message_templates 
                (step_number, template_name, message_content, wait_days_before_next)
                VALUES (?, ?, ?, ?)
            """, (step_number, template_name, message_content, wait_days))
            return cursor.lastrowid
    
    def get_template_for_step(self, step_number):
        """Get the active template for a specific step"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM message_templates 
                WHERE step_number = ? AND is_active = 1
                ORDER BY created_at DESC
                LIMIT 1
            """, (step_number,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_templates(self):
        """Get all message templates"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM message_templates 
                WHERE is_active = 1
                ORDER BY step_number, created_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def update_template(self, template_id, message_content=None, wait_days=None, is_active=None):
        """Update a message template"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if message_content is not None:
                updates.append("message_content = ?")
                params.append(message_content)
            
            if wait_days is not None:
                updates.append("wait_days_before_next = ?")
                params.append(wait_days)
            
            if is_active is not None:
                updates.append("is_active = ?")
                params.append(is_active)
            
            if updates:
                params.append(template_id)
                cursor.execute(f"""
                    UPDATE message_templates 
                    SET {', '.join(updates)}
                    WHERE id = ?
                """, params)
    
    # Flow Statistics
    
    def get_flow_statistics(self):
        """Get statistics about the flow"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get profiles by step
            cursor.execute("""
                SELECT current_step, COUNT(*) as count 
                FROM profiles 
                GROUP BY current_step 
                ORDER BY current_step
            """)
            
            step_counts = {row['current_step']: row['count'] for row in cursor.fetchall()}
            
            # Get total messages sent per step
            cursor.execute("""
                SELECT step_number, COUNT(*) as count 
                FROM flow_history 
                GROUP BY step_number 
                ORDER BY step_number
            """)
            
            messages_per_step = {row['step_number']: row['count'] for row in cursor.fetchall()}
            
            # Get pending profiles (step 0, never contacted)
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM profiles 
                WHERE current_step = 0 AND last_contacted IS NULL
            """)
            
            pending_count = cursor.fetchone()['count']
            
            return {
                'profiles_by_step': step_counts,
                'messages_sent_by_step': messages_per_step,
                'pending_profiles': pending_count,
                'total_profiles': sum(step_counts.values())
            }
    
    def get_eligible_profiles_count(self, step_number, include_failed=True, max_retries=None):
        """Get count of profiles eligible for a specific step, including failed accounts for retry"""
        from config import Config
        
        if max_retries is None:
            max_retries = Config.MAX_DATABASE_RETRIES
            
        cooldown_minutes = Config.RETRY_COOLDOWN_MINUTES
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if include_failed:
                cursor.execute("""
                    SELECT COUNT(*) as count 
                    FROM profiles 
                    WHERE current_step = ? 
                    AND (
                        (status IN ('pending', 'active', 'success') 
                         AND (next_step_eligible IS NULL OR next_step_eligible <= datetime('now')))
                        OR 
                        (status = 'failed' 
                         AND retry_count < ? 
                         AND (last_retry IS NULL OR last_retry <= datetime('now', '-{} minutes')))
                    )
                """.format(cooldown_minutes), (step_number, max_retries))
            else:
                cursor.execute("""
                    SELECT COUNT(*) as count 
                    FROM profiles 
                    WHERE current_step = ? 
                    AND (next_step_eligible IS NULL OR next_step_eligible <= datetime('now'))
                """, (step_number,))
            
            return cursor.fetchone()['count']
    
    def search_profiles_advanced(self, username=None, step=None, tags=None, status=None):
        """Advanced search with multiple filters"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM profiles WHERE 1=1"
            params = []
            
            if username:
                query += " AND username LIKE ?"
                params.append(f'%{username}%')
            
            if step is not None:
                query += " AND current_step = ?"
                params.append(step)
            
            if tags:
                query += " AND tags LIKE ?"
                params.append(f'%{tags}%')
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            query += " ORDER BY timestamp DESC LIMIT 1000"
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

