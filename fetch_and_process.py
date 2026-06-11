import json
import sqlite3
import requests
import sys
from datetime import datetime

# Configuration
DB_FILE = "enrollment.db"
API_URL = "https://api.mock-university.edu/v1/enrollment" # Simulated API
NODE_ALERT_URL = "http://localhost:3000/api/alert"

def process_batch(records):
    """
    Processes a batch of course records, updates the DB, 
    and returns a list of courses where seats just became available.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    alerts = []

    try:
        cursor.execute("BEGIN TRANSACTION;")
        
        for record in records:
            c_id = record['course_id']
            c_name = record['course_name']
            total = record['total_seats']
            current_available = record['unassigned_seats']

            # Check previous state to detect a real-time change
            cursor.execute("SELECT unassigned_seats FROM courses WHERE course_id = ?", (c_id,))
            row = cursor.fetchone()

            if row is None:
                # First time seeing this course, insert it
                cursor.execute(
                    "INSERT INTO courses (course_id, course_name, total_seats, unassigned_seats) VALUES (?, ?, ?, ?)",
                    (c_id, c_name, total, current_available)
                )
            else:
                prev_available = row[0]
                
                # If available seats increased, trigger a real-time alert event
                if current_available > prev_available:
                    alerts.append({
                        "course_id": c_id,
                        "course_name": c_name,
                        "previous_seats": prev_available,
                        "new_seats": current_available,
                        "timestamp": datetime.utcnow().isoformat()
                    })

                # Update the record
                cursor.execute(
                    "UPDATE courses SET unassigned_seats = ?, last_updated = CURRENT_TIMESTAMP WHERE course_id = ?",
                    (current_available, c_id)
                )
                
                # Log the delta change
                if prev_available != current_available:
                    cursor.execute(
                        "INSERT INTO enrollment_logs (course_id, previous_seats, new_seats) VALUES (?, ?, ?)",
                        (c_id, prev_available, current_available)
                    )

        conn.commit()
        return alerts
    except Exception as e:
        conn.rollback()
        print(f"[-] Database Transaction Error: {e}", file=sys.stderr)
        return []
    finally:
        conn.close()

def dispatch_alerts(alerts):
    """Pushes alerts to the JavaScript real-time Node.js server"""
    for alert in alerts:
        try:
            response = requests.post(NODE_ALERT_URL, json=alert, timeout=2)
            if response.status_code == 200:
                print(f"[+] Alert broadcasted out for {alert['course_id']}")
        except requests.exceptions.RequestException:
            print(f"[-] Failed to dispatch alert hook to JavaScript server for {alert['course_id']}", file=sys.stderr)

if __name__ == "__main__":
    print(f"[{datetime.now()}] Python engine parsing API buffer payload...")
    
    # Reading mock JSON from standard input stream (piped from Bash)
    try:
        input_data = sys.stdin.read()
        payload = json.loads(input_data)
        
        detected_alerts = process_batch(payload.get("records", []))
        if detected_alerts:
            print(f"[!] Found {len(detected_alerts)} seat status changes. Dispatching real-time notifications...")
            dispatch_alerts(detected_alerts)
        else:
            print("[+] Processing complete. No seat availability changes detected.")
            
    except Exception as e:
        print(f"[-] Execution failure: {e}", file=sys.stderr)
        sys.exit(1)
