from flask import Flask, request, jsonify, render_template
from blockchain import Blockchain  # Assuming the blockchain code is in blockchain.py

app = Flask(__name__)
blockchain = Blockchain()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_attendance', methods=['POST'])
def add_attendance():
    employee_id = request.form['employee_id']
    attendance_status = request.form['attendance_status']
    blockchain.add_block(employee_id, attendance_status)
    return jsonify({"message": "Attendance added successfully!"})

@app.route('/view_attendance')
def view_attendance():
    attendance_records = blockchain.get_all_attendance()
    return render_template('view_attendance.html', records=attendance_records)

@app.route('/validate')
def validate_blockchain():
    if blockchain.is_valid():
        return jsonify({"message": "Blockchain is valid"})
    else:
        return jsonify({"message": "Blockchain is invalid"})

if __name__ == '__main__':
    app.run(debug=True)
