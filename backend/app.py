from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import json
from datetime import datetime
import os
import sqlite3
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.detection_engine import DetectionEngine

# --- Path setup ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
LOG_DIR = os.path.join(BASE_DIR, '..', 'logs')
DB_PATH = os.path.join(DATA_DIR, 'security.db')

# Ensure required directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)


def init_db():
    """Initialize the database tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

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

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'admin'
    )
    ''')

    cursor.execute('''
    INSERT OR IGNORE INTO users (username, password, role)
    VALUES ('admin', 'admin123', 'admin')
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully.")


# Initialize DB on module load (important for Render cold starts)
init_db()

app = Flask(__name__, static_folder='../frontend/public', static_url_path='')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize detection engine
detector = DetectionEngine()

@app.route('/')
def serve_dashboard():
    """Serve the dashboard"""
    return send_from_directory('../frontend/public', 'index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/login', methods=['POST'])
def login():
    """Simulate login endpoint for testing"""
    data = request.get_json()
    username = data.get('username', 'unknown')
    ip = request.remote_addr
    
    # In real system, you'd check credentials
    # Here we're simulating failed login for demonstration
    success = False
    
    # Check password (simulate)
    if data.get('password') == 'correct_password':
        success = True
    
    # Log the event
    event_id = detector.save_event(
        event_type='LOGIN_ATTEMPT',
        source_ip=ip,
        user_id=username,
        action='login',
        status='SUCCESS' if success else 'FAILED',
        details={'password_attempt': data.get('password', '')[:3] + '***'}
    )
    
    # Analyze for threats
    alert = detector.analyze_login(ip, username, success)
    
    if alert:
        # Save alert to database
        alert_id = detector.save_alert(alert, event_id)
        
        # Emit real-time alert via WebSocket
        alert['id'] = alert_id
        alert['timestamp'] = datetime.now().isoformat()
        socketio.emit('new_alert', alert)
        
        # Log to file
        log_path = os.path.join(LOG_DIR, 'alerts.log')
        with open(log_path, 'a') as f:
            f.write(json.dumps(alert) + '\n')
        
        return jsonify({
            'status': 'failed',
            'message': 'Login failed',
            'alert': alert
        }), 401
    
    if success:
        return jsonify({'status': 'success', 'message': 'Login successful'})
    else:
        return jsonify({'status': 'failed', 'message': 'Invalid credentials'}), 401

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get all alerts"""
    limit = request.args.get('limit', 50, type=int)
    alerts = detector.get_recent_alerts(limit)
    return jsonify(alerts)

@app.route('/api/alerts/<int:alert_id>/resolve', methods=['PUT'])
def resolve_alert(alert_id):
    """Mark alert as resolved"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    UPDATE alerts 
    SET status = 'RESOLVED' 
    WHERE id = ?
    ''', (alert_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success', 'message': 'Alert resolved'})

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get security events"""
    limit = request.args.get('limit', 100, type=int)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT * FROM security_events 
    ORDER BY timestamp DESC 
    LIMIT ?
    ''', (limit,))
    
    events = []
    for row in cursor.fetchall():
        events.append({
            'id': row[0],
            'timestamp': row[1],
            'event_type': row[2],
            'source_ip': row[3],
            'user_id': row[4],
            'action': row[5],
            'status': row[6],
            'details': row[7]
        })
    
    conn.close()
    return jsonify(events)

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('connected', {'message': 'Connected to security system'})

if __name__ == '__main__':
    print("=" * 50)
    print("Starting Security Detection System...")
    print("=" * 50)
    print("Dashboard available at: http://localhost:5000")
    print("API endpoints:")
    print("  - GET  /api/health")
    print("  - POST /api/login")
    print("  - GET  /api/alerts")
    print("  - GET  /api/events")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)