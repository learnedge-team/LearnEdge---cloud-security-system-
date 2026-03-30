import requests
import time
import sys

def simulate_brute_force():
    """Simulate brute force attack"""
    url = "http://localhost:5000/api/login"
    
    # List of common passwords to try
    passwords = [
        "password123",
        "admin",
        "123456",
        "letmein",
        "password",
        "admin123",
        "root",
        "qwerty"
    ]
    
    print("=" * 60)
    print("🚨 Starting brute force simulation...")
    print("=" * 60)
    
    alert_triggered = False
    
    for i, password in enumerate(passwords, 1):
        payload = {
            "username": "admin",
            "password": password
        }
        
        try:
            response = requests.post(url, json=payload)
            print(f"Attempt {i}: Trying '{password}' - Status: {response.status_code}")
            
            if response.status_code == 401:
                data = response.json()
                if 'alert' in data:
                    print("\n" + "=" * 60)
                    print("⚠️  ALERT TRIGGERED!")
                    print("=" * 60)
                    print(f"Alert Type: {data['alert']['type']}")
                    print(f"Severity: {data['alert']['severity']}")
                    print(f"Description: {data['alert']['description']}")
                    print("\n✅ Brute force attack detected!")
                    alert_triggered = True
                    break
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(0.5)  # Small delay between attempts
    
    print("\n" + "=" * 60)
    if alert_triggered:
        print("Check the dashboard at http://localhost:5000 to see the alert!")
    else:
        print("No alert was triggered. Make sure the server is running.")
    print("=" * 60)

if __name__ == "__main__":
    simulate_brute_force()
