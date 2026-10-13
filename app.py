from flask import Flask, render_template, request, jsonify
import sqlite3
import os
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'pulseops-secure-secret'

DB_PATH = '/app/data/pulseops.db'
os.makedirs('/app/data', exist_ok=True)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Monitors Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS monitors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        url TEXT NOT NULL,
        status TEXT NOT NULL,
        response_time INTEGER NOT NULL,
        uptime_percentage REAL NOT NULL,
        environment TEXT NOT NULL,
        check_interval TEXT NOT NULL,
        last_checked DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 2. Incidents Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        monitor_name TEXT NOT NULL,
        title TEXT NOT NULL,
        severity TEXT NOT NULL,
        status TEXT NOT NULL,
        duration TEXT NOT NULL,
        start_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    # 3. Alert Rules Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS alert_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        condition_rule TEXT NOT NULL,
        channels TEXT NOT NULL,
        enabled INTEGER DEFAULT 1
    )''')

    conn.commit()
    
    # Seed Data if empty
    cursor.execute("SELECT COUNT(*) FROM monitors")
    if cursor.fetchone()[0] == 0:
        sample_monitors = [
            ('Campus Search Gateway', 'https://search.cit.edu.in', 'Online', 142, 99.98, 'Production', '30s'),
            ('Gitlab CI Runner', 'https://git.cit.edu.in', 'Online', 215, 99.85, 'Production', '1m'),
            ('Student Portal API', 'https://api.student.cit.edu.in', 'Degraded', 840, 98.40, 'Production', '30s'),
            ('Library Staging Node', 'https://staging-lib.cit.edu.in', 'Offline', 0, 94.20, 'Staging', '5m'),
            ('Exam Microservice', 'https://exams.cit.edu.in', 'Online', 95, 99.99, 'Production', '30s')
        ]
        cursor.executemany("INSERT INTO monitors (name, url, status, response_time, uptime_percentage, environment, check_interval) VALUES (?, ?, ?, ?, ?, ?, ?)", sample_monitors)
        
        sample_incidents = [
            ('Student Portal API', 'Response time exceeded 800ms threshold', 'Warning', 'Open', '12m'),
            ('Library Staging Node', 'HTTP 504 Gateway Timeout / Unreachable', 'Critical', 'Acknowledged', '46m')
        ]
        cursor.executemany("INSERT INTO incidents (monitor_name, title, severity, status, duration) VALUES (?, ?, ?, ?, ?)", sample_incidents)

        sample_rules = [
            ('High Latency Warning', 'Response time > 500ms for 2 consecutive checks', 'Email, Webhook', 1),
            ('Total Outage Alert', 'Website status changes to Offline', 'Slack, SMS, Email', 1)
        ]
        cursor.executemany("INSERT INTO alert_rules (name, condition_rule, channels, enabled) VALUES (?, ?, ?, ?)", sample_rules)
        conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/monitors', methods=['GET', 'POST'])
def handle_monitors():
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        name = data.get('name')
        url = data.get('url')
        environment = data.get('environment', 'Production')
        check_interval = data.get('interval', '30s')
        
        status, response_time = 'Online', 120
        try:
            start = datetime.now()
            res = requests.get(url, timeout=5)
            end = datetime.now()
            response_time = int((end - start).total_seconds() * 1000)
            if res.status_code != 200:
                status = 'Degraded'
        except:
            status = 'Offline'
            response_time = 0

        cursor.execute("INSERT INTO monitors (name, url, status, response_time, uptime_percentage, environment, check_interval) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (name, url, status, response_time, 100.0, environment, check_interval))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Monitor registered successfully'})

    cursor.execute("SELECT * FROM monitors ORDER BY id DESC")
    monitors = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(monitors)

@app.route('/api/monitors/<int:mon_id>/delete', methods=['DELETE'])
def delete_monitor(mon_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM monitors WHERE id = ?", (mon_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/incidents', methods=['GET'])
def get_incidents():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM incidents ORDER BY id DESC")
    incidents = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(incidents)

@app.route('/api/alert-rules', methods=['GET'])
def get_alert_rules():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM alert_rules")
    rules = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(rules)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)