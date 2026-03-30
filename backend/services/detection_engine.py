import sqlite3
from datetime import datetime, timedelta
import json
import os

class DetectionEngine:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'security.db')
        self.failed_attempts = {}
        
    def check_brute_force(self, ip, username):
        """Check for brute force attempts (5 failures in 5 minutes)"""
        now = datetime.now()
        
        if ip not in self.failed_attempts:
            self.failed_attempts[ip] = []
        
        # Clean old attempts
        self.failed_attempts[ip] = [
            t for t in self.failed_attempts[ip] 
            if (now - t).seconds < 300
        ]
        
        # Check threshold
        if len(self.failed_attempts[ip]) >= 4:  # 4 previous + current = 5
            return True
            
        return False
    
    def analyze_login(self, ip, username, success):
        """Analyze login attempt and return alert if needed"""
        if not success:
            # Store failed attempt
            if ip not in self.failed_attempts:
                self.failed_attempts[ip] = []
            self.failed_attempts[ip].append(datetime.now())
            
            # Check if this triggers brute force
            if self.check_brute_force(ip, username):
                alert = {
                    'type': 'BRUTE_FORCE_ATTACK',
                    'severity': 'HIGH',
                    'description': f'Brute force attack detected from IP {ip} for user {username}',
                    'details': {
                        'ip': ip,
                        'username': username,
                        'attempts': len(self.failed_attempts[ip])
                    }
                }
                return alert
        else:
            # Clear failed attempts on successful login
            if ip in self.failed_attempts:
                self.failed_attempts[ip] = []
        
        return None
    
    def save_event(self, event_type, source_ip, user_id, action, status, details=None):
        """Save security event to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO security_events (event_type, source_ip, user_id, action, status, details)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (event_type, source_ip, user_id, action, status, json.dumps(details)))
        
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return event_id
    
    def save_alert(self, alert, event_id=None):
        """Save alert to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO alerts (alert_type, severity, description, event_id)
        VALUES (?, ?, ?, ?)
        ''', (alert['type'], alert['severity'], alert['description'], event_id))
        
        alert_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return alert_id
    
    def get_recent_alerts(self, limit=50):
        """Get recent alerts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM alerts 
        ORDER BY timestamp DESC 
        LIMIT ?
        ''', (limit,))
        
        alerts = []
        for row in cursor.fetchall():
            alerts.append({
                'id': row[0],
                'timestamp': row[1],
                'type': row[2],
                'severity': row[3],
                'description': row[4],
                'status': row[6]
            })
        
        conn.close()
        return alerts