import os
import sqlite3
import uuid
from datetime import datetime
import pytz
import qrcode
from flask import Flask, render_template, request, redirect, send_from_directory, jsonify
from flask_socketio import SocketIO
from flask_socketio import SocketIO, emit

app = Flask(__name__, static_folder='static')

socketio = SocketIO(app)

# Hardcoded credentials
ADMIN_ID = "admin123"
ADMIN_PASSWORD = "adminpassword"
EMPLOYEE_ID = "employee123"
EMPLOYEE_PASSWORD = "employeepassword"

clock_in_out_enabled = False

QR_CODES_DIR = "static/qrcodes"
os.makedirs(QR_CODES_DIR, exist_ok=True)

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()

    # Create attendance table
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            clock_in_time TEXT,
            clock_out_time TEXT,
            date TEXT  -- Added date column
        )
    ''')

    # Create or migrate employees table
    c.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            uid TEXT PRIMARY KEY,
            name TEXT,
            email TEXT,
            password TEXT
        )
    ''')
    # Create leave_requests table
    c.execute('''
           CREATE TABLE IF NOT EXISTS leave_requests (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT,
               leave_type TEXT,
               start_date TEXT,
               end_date TEXT,
               reason TEXT,
               additional_notes TEXT,
               attachment_path TEXT,
               status TEXT DEFAULT 'Pending'
           )
       ''')
    conn.commit()
    conn.close()


init_db()

@app.route('/')
def home():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    user_type = request.form.get('user_type')
    user_id = request.form.get('id')
    password = request.form.get('password')

    if user_type == "Admin" and user_id == ADMIN_ID and password == ADMIN_PASSWORD:
        return redirect('/admin_dashboard')
    elif user_type == "Employee" and user_id == EMPLOYEE_ID and password == EMPLOYEE_PASSWORD:
        return redirect('/employee_dashboard')
    return "Invalid credentials"


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        employee_id = request.form.get('id')
        password = request.form.get('password')

        if employee_id == EMPLOYEE_ID and password == EMPLOYEE_PASSWORD:
            return redirect('/employee_dashboard')
        return "Invalid signup credentials"
    return render_template('signup.html')


@app.route('/employee_dashboard')
def employee_dashboard():
    employee_name = EMPLOYEE_ID
    return render_template('employee_dashboard.html', name=employee_name)


@app.route('/request_leave')
def request_leave():
    return render_template('request_leave.html')

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/submit_leave_request', methods=['POST'])
def submit_leave_request():
    name = request.form.get('name', 'Anonymous')
    leave_type = request.form['leave_type']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    reason = request.form['reason']
    additional_notes = request.form.get('additional_notes', '')

    attachment = request.files.get('attachment')
    attachment_path = ''
    if attachment and attachment.filename:
        filename = f"{uuid.uuid4().hex}_{attachment.filename}"
        attachment_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        attachment.save(attachment_path)

    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()

    # Insert leave request into the database
    c.execute('''
        INSERT INTO leave_requests (name, leave_type, start_date, end_date, reason, additional_notes, attachment_path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, leave_type, start_date, end_date, reason, additional_notes, attachment_path))

    conn.commit()
    conn.close()

    return redirect('/employee_dashboard')

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/manage_leave_requests')
def manage_leave_requests():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()

    # Fetch all leave requests
    c.execute('SELECT * FROM leave_requests')
    leave_requests = c.fetchall()
    conn.close()

    return render_template('manage_leave_requests.html', leave_requests=leave_requests)

@app.route('/clear_leave_requests', methods=['POST'])
def clear_leave_requests():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()

    c.execute('DELETE FROM leave_requests')
    conn.commit()
    conn.close()

    return redirect('/manage_leave_requests')


@app.route('/update_leave_status', methods=['POST'])
def update_leave_status():
    request_id = request.form['request_id']
    status = request.form['status']

    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()

    # Update leave request status
    c.execute('''
        UPDATE leave_requests
        SET status = ?
        WHERE id = ?
    ''', (status, request_id))
    conn.commit()

    c.execute('SELECT * FROM leave_requests WHERE id = ?', (request_id,))
    leave_request = c.fetchone()
    conn.close()

    socketio.emit('leave_status_update', {
        'id': leave_request[0],
        'name': leave_request[1],
        'leave_type': leave_request[2],
        'start_date': leave_request[3],
        'end_date': leave_request[4],
        'reason': leave_request[5],
        'notes': leave_request[6],
        'attachment_path': leave_request[7],
        'status': leave_request[8]
    })

    return redirect('/manage_leave_requests')


@app.route('/view_attachment/<path:filename>')
def view_attachment(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/manage_employees', methods=['GET', 'POST'])
def manage_employees():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        uid = uuid.uuid4().hex[:8]
        c.execute('INSERT INTO employees (uid, name, email) VALUES (?, ?, ?)',
                  (uid, name, email))
        conn.commit()

        qr_data = f"employee:{uid}"
        qr_code_path = os.path.join(QR_CODES_DIR, f"{uid}.png")
        qr = qrcode.make(qr_data)
        qr.save(qr_code_path)

    c.execute('''
        SELECT e.uid, e.name, e.email,
               MAX(a.date) AS date,  -- Only the date column
               MAX(a.clock_in_time) AS clock_in_time,
               MAX(a.clock_out_time) AS clock_out_time
        FROM employees e
        LEFT JOIN attendance a ON e.uid = a.employee_id
        GROUP BY e.uid
    ''')

    employees = c.fetchall()
    conn.close()

    return render_template('manage_employees.html', employees=employees)

def get_philippine_time():
    tz = pytz.timezone('Asia/Manila')
    return datetime.now(tz).strftime('%I:%M:%S %p')

def get_philippine_date():
    tz = pytz.timezone('Asia/Manila')
    return datetime.now(tz).strftime('%d/%m/%Y')

@app.route('/delete_employee/<uid>', methods=['POST'])
def delete_employee(uid):
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute('DELETE FROM employees WHERE uid = ?', (uid,))
    conn.commit()
    conn.close()

    qr_code_path = os.path.join(QR_CODES_DIR, f"{uid}.png")
    if os.path.exists(qr_code_path):
        os.remove(qr_code_path)

    return redirect('/manage_employees')


@app.route('/toggle_clock_in_out', methods=['POST'])
def toggle_clock_in_out():
    global clock_in_out_enabled
    data = request.get_json()
    clock_in_out_enabled = data.get('enable', False)
    socketio.emit('clock_in_out_status', {'enabled': clock_in_out_enabled})
    return jsonify({'enabled': clock_in_out_enabled})

@app.route('/download_qr_code/<uid>')
def download_qr_code(uid):
    qr_code_path = os.path.join(QR_CODES_DIR, f"{uid}.png")

    if os.path.exists(qr_code_path):
        return send_from_directory(os.path.abspath(QR_CODES_DIR), f"{uid}.png", as_attachment=True)
    else:
        return "QR code not found", 404
@app.route('/clock_in_out', methods=['POST'])
def clock_in_out():
    if not clock_in_out_enabled:
        return jsonify({"message": "Clock-in/out is disabled."}), 403

    data = request.get_json()
    qr_data = data.get('employee_qr_data')

    if qr_data and qr_data.startswith("employee:"):
        employee_id = qr_data.split(":")[1]
        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()
        c.execute('SELECT uid FROM employees WHERE uid = ?', (employee_id,))
        if not c.fetchone():
            conn.close()
            return jsonify({"message": "Invalid Employee QR Code."}), 400

        c.execute('SELECT id FROM attendance WHERE employee_id = ? AND clock_out_time IS NULL', (employee_id,))
        if c.fetchone():
            # Clock out
            c.execute('''
                UPDATE attendance
                SET clock_out_time = ?
                WHERE employee_id = ? AND clock_out_time IS NULL
            ''', (get_philippine_time(), employee_id))
            conn.commit()
            conn.close()
            return jsonify({"message": "Clocked out successfully."})
        else:
            c.execute('''
                INSERT INTO attendance (employee_id, clock_in_time, date)
                VALUES (?, ?, ?)
            ''', (employee_id, get_philippine_time(), get_philippine_date()))
            conn.commit()
            conn.close()
            return jsonify({"message": "Clocked in successfully."})

    return jsonify({"message": "Invalid QR Code."}), 400

@socketio.on('leave_status_update', namespace='/')
def handle_leave_status_update(data):
    print(f"Leave status updated for {data['employee_name']} - Request ID: {data['request_id']}, Status: {data['status']}")

if __name__ == "__main__":
    socketio.run(app, debug=True)
