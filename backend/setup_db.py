import sqlite3
import os

# Create data directory if not exists
os.makedirs('../data', exist_ok=True)

# Connect to database
conn = sqlite3.connect('../data/security.db')
cursor = conn.cursor()

# Create security events table
cursor.execute('''
CREATE TABLE IF NOT EXISTS security_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    event_type TEXT NOT NULL,
    source_ip TEXT,
    user_id TEXT,
    action TEXT,
    status TEXT,
    details TEXT
)
''')

# Create alerts table
cursor.execute('''
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    alert_type TEXT NOT NULL,
    severity TEXT,
    description TEXT,
    event_id INTEGER,
    status TEXT DEFAULT 'NEW'
)
''')

# Create users table for admin
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'admin'
)
''')

# Insert default admin user (password: admin123)
cursor.execute('''
INSERT OR IGNORE INTO users (username, password, role)
VALUES ('admin', 'admin123', 'admin')
''')

conn.commit()
conn.close()

print("Database setup completed!")