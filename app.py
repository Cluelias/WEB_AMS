import io
import os
import qrcode
import uuid
from flask import Flask, render_template, request, redirect, send_from_directory, jsonify
from flask_socketio import SocketIO
import sqlite3

app = Flask(__name__)
socketio = SocketIO(app)

ADMIN_ID = "admin123"
ADMIN_PASSWORD = "adminpassword"

clock_in_out_enabled = False

QR_CODES_DIR = "static/qrcodes"
os.makedirs(QR_CODES_DIR, exist_ok=True)

def init_db():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()

    c.execute(''' 
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            clock_in_time TEXT,
            clock_out_time TEXT
        )
    ''')

    c.execute("PRAGMA table_info(employees)")
    columns = [col[1] for col in c.fetchall()]
    if "uid" not in columns:
        c.execute('''
            CREATE TABLE employees_new (
                uid TEXT PRIMARY KEY,
                name TEXT,
                email TEXT
            )
        ''')

        c.execute('SELECT name, email FROM employees')
        rows = c.fetchall()
        for row in rows:
            uid = uuid.uuid4().hex[:8]
            c.execute('INSERT INTO employees_new (uid, name, email) VALUES (?, ?, ?)', (uid, row[0], row[1]))

        c.execute('DROP TABLE employees')
        c.execute('ALTER TABLE employees_new RENAME TO employees')

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
    elif user_type == "Employee":
        return redirect('/employee_dashboard')
    return "Invalid credentials"


@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')


@app.route('/manage_employees', methods=['GET', 'POST'])
def manage_employees():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        uid = uuid.uuid4().hex[:8]
        c.execute('INSERT INTO employees (uid, name, email) VALUES (?, ?, ?)', (uid, name, email))
        conn.commit()

        qr_data = f"employee:{uid}"
        qr_code_path = os.path.join(QR_CODES_DIR, f"{uid}.png")
        qr = qrcode.make(qr_data)
        qr.save(qr_code_path)

    c.execute('''
        SELECT e.uid, e.name, e.email,
               MAX(DATE(a.clock_in_time)) AS date,
               MAX(a.clock_in_time) AS clock_in_time,
               MAX(a.clock_out_time) AS clock_out_time
        FROM employees e
        LEFT JOIN attendance a ON e.uid = a.employee_id
        GROUP BY e.uid
    ''')
    employees = c.fetchall()
    conn.close()

    return render_template('manage_employees.html', employees=employees)


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
            c.execute('UPDATE attendance SET clock_out_time = datetime("now") WHERE employee_id = ?', (employee_id,))
            conn.commit()
            conn.close()
            return jsonify({"message": "Clocked out successfully."})
        else:
            c.execute('INSERT INTO attendance (employee_id, clock_in_time) VALUES (?, datetime("now"))', (employee_id,))
            conn.commit()
            conn.close()
            return jsonify({"message": "Clocked in successfully."})
    return jsonify({"message": "Invalid QR Code format."}), 400


@app.route('/download_qr_code/<uid>')
def download_qr_code(uid):
    qr_code_path = os.path.join(QR_CODES_DIR, f"{uid}.png")

    if os.path.exists(qr_code_path):
        return send_from_directory(os.path.abspath(QR_CODES_DIR), f"{uid}.png", as_attachment=True)
    else:
        return "QR code not found", 404


@socketio.on('connect')
def handle_connect():
    socketio.emit('clock_in_out_status', {'enabled': clock_in_out_enabled})

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)

