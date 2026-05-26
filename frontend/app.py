import eventlet
eventlet.monkey_patch()

from flask import Flask, request, render_template, redirect, url_for, session, jsonify, json
from flask_socketio import SocketIO, emit, join_room
import sqlite3
import os
from dotenv import load_dotenv
from datetime import datetime, date
import traceback
import uuid
import re
import requests
import google.generativeai as genai

app = Flask(__name__)
load_dotenv()
socketio = SocketIO(app)

app.secret_key = os.getenv('SECRET_KEY', 'default_dev_key')


# ───── Gemini AI Configuration ─────
genai.configure(api_key="")

def generate_gemini_reply(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print("Gemini Error:", str(e))
        return "🤖 Sorry, I couldn't fetch a response from Gemini right now."

# ───── Database Connection (SQLite) ─────
# ───── Database Connection (SQLite) ─────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Database 'database' folder lo undi kabatti path ila undali
DB_PATH = os.path.join(BASE_DIR, 'database', 'college_db.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ───── Routes ─────

@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/student_chat_admin', methods=['GET'])
def student_chat_admin():
    if 'student' not in session:
        return redirect(url_for('login'))

    student_email = session['student']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM student WHERE email=?", (student_email,))
    row = cur.fetchone()
    student_id = row['id'] if row else None
    cur.close()
    conn.close()

    return render_template('student_chat_admin.html', student_id=student_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('homepage.html')

    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if role == 'admin':
        cursor.execute("SELECT * FROM admin WHERE email = ? AND password = ?", (email, password))
        admin = cursor.fetchone()

        if admin:
            session['admin'] = email
            cursor.close()
            conn.close()
            return redirect(url_for('dashboard'))
        else:
            cursor.close()
            conn.close()
            return render_template('homepage.html', error="❌ Invalid Admin Credentials")

    elif role == 'student':
        cursor.execute("SELECT id FROM student WHERE email = ? AND password = ?", (email, password))
        student = cursor.fetchone()

        if student:
            session['student'] = email
            session['student_id'] = student['id']
            session['email'] = email
            cursor.close()
            conn.close()
            return redirect(url_for('chatbot'))
        else:
            cursor.close()
            conn.close()
            return render_template('homepage.html', error="❌ Invalid Student Credentials")

    else:
        cursor.close()
        conn.close()
        return render_template('homepage.html', error="❌ Invalid Role")
    
@app.route('/view_escalation/<int:escalation_id>')
def view_escalation(escalation_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT student_id, issue FROM live_escalations WHERE id = ?", (escalation_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return "Invalid escalation ID", 404

    student_id = row['student_id']
    issue = row['issue']

    cursor.execute("SELECT message, message_from, timestamp FROM student_admin_chat WHERE student_id = ? ORDER BY timestamp", (student_id,))
    chat_data = cursor.fetchall()
    conn.close()

    return render_template('student_chat_admin.html', student_id=student_id, issue=issue, chat_data=chat_data, role="student")

@app.route('/view_escalation_data')
def view_escalation_data():
    if 'student_id' not in session:
        return jsonify([])

    student_id = session['student_id']
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT message, message_from FROM student_admin_chat WHERE student_id = ? ORDER BY timestamp", (student_id,))
    chat_data = cursor.fetchall()
    conn.close()

    return jsonify([
        {
            "message": row["message"],
            "sender": row["message_from"]
        } for row in chat_data
    ])

@app.route('/view_escalation_messages/<int:student_id>')
def view_escalation_messages(student_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
      SELECT message, message_from FROM student_admin_chat 
      WHERE student_id=? ORDER BY timestamp
    """, (student_id,))
    msgs = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(messages=[dict(m) for m in msgs])

@app.route('/send_admin_chat', methods=['POST'])
def send_admin_chat():
    data = request.get_json()
    student_id = data['student_id']
    msg = data['message']
    msg_from = data['message_from']
    conn = get_db_connection()
    cur = conn.cursor()
    # SQLite uses CURRENT_TIMESTAMP by default if setup correctly, or we can pass datetime.now()
    cur.execute("""
      INSERT INTO student_admin_chat (student_id, admin_id, message_from, message, timestamp) 
      VALUES (?, 1, ?, ?, ?)
    """, (student_id, msg_from, msg, datetime.now()))
    conn.commit()
    cur.close()
    conn.close()
    return "OK", 200

@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    contact = request.form.get('contact')
    dept_input = request.form.get('department', '').strip().lower()
    email = request.form.get('email')
    password = request.form.get('password')

    if not all([name, contact, dept_input, email, password]):
        return "❌ All fields are required.", 400

    dept_map = {
        'cse': 'Computer Science and Engineering',
        'ece': 'Electronics and Communication Engineering',
        'eee': 'Electrical and Electronics Engineering',
        'mech': 'Mechanical Engineering',
        'civil': 'Civil Engineering',
        'it': 'Information Technology',
        'bme': 'Biomedical Engineering',
        'chemical': 'Chemical Engineering'
    }

    department = dept_map.get(dept_input, dept_input.title())

    if not email.endswith("@college.com"):
        return "❌ Email must end with @college.com", 400

    if not re.match(r'^(?=.*[A-Z])(?=.*[@$!%*?&]).{6,}$', password):
        return "❌ Password must be 6+ chars with 1 capital & 1 special character.", 400

    if not re.match(r'^\d{10}$', contact):
        return "❌ Contact must be 10 digits.", 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT dept_id FROM department WHERE LOWER(name) = ?", (department.lower(),))
        dept = cursor.fetchone()
        if not dept:
            return "❌ Invalid department.", 400
        department_id = dept['dept_id']

        cursor.execute("SELECT id FROM student WHERE email = ?", (email,))
        if cursor.fetchone():
            return "⚠️ Account already exists with this email.", 400

        cursor.execute("""
            INSERT INTO student (name, contact, email, password, department_id)
            VALUES (?, ?, ?, ?, ?)
        """, (name, contact, email, password, department_id))
        conn.commit()
        return "✅ Account created successfully!", 200

    except Exception as e:
        return f"❌ Registration failed: {e}", 500
    finally:
        cursor.close()
        conn.close()

@app.route('/chatbot')
def chatbot():
    if 'student' not in session:
        return redirect(url_for('login'))

    email = session['student']
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.id, s.name, s.contact, s.email, d.name as dept_name
        FROM student s
        JOIN department d ON s.department_id = d.dept_id
        WHERE s.email = ?
    """, (email,))

    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        return render_template(
            'chatbot.html',
            student_id=result['id'],
            student_email=result['email'],
            student_name=result['name'],
            student_phone=result['contact'],
            student_dept=result['dept_name']
        )
    else:
        return "❌ Student not found.", 404

@app.route('/save_chat', methods=['POST'])
def save_chat():
    data = request.get_json()
    student_id = data.get('student_id')
    sender = data.get('message_from')
    message = data.get('message')

    if not student_id or not sender or not message:
        return "Missing required fields", 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT email FROM student WHERE id = ?", (student_id,))
        result = cursor.fetchone()
        email = result['email'] if result else None

        cursor.execute(
            """
            INSERT INTO student_chatbot_chat (student_id, email, message_from, message, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (student_id, email, sender, message, datetime.now())
        )
        conn.commit()
        return "Message saved", 200
    except Exception as e:
        print("❌ Error saving message:", e)
        return "Database error", 500
    finally:
        cursor.close()
        conn.close()

@app.route('/save_chat_session', methods=['POST'])
def save_chat_session():
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        session_data = data.get('session_data')
        session_title = data.get('session_title', 'Untitled')

        if not student_id or not session_data:
            return "❌ Missing data", 400

        folder = 'chat_logs'
        os.makedirs(folder, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        filename = f"chat_{student_id}_{timestamp}_{unique_id}.json"
        filepath = os.path.join(folder, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(session_data)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chat_session_logs (student_id, session_title, file_name, file_path, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (student_id, session_title, filename, filepath, datetime.now()))
        conn.commit()
        conn.close()

        return jsonify({"success": True, "file_path": filepath}), 200

    except Exception as e:
        traceback.print_exc()
        return f"❌ Internal Error: {e}", 500

@app.route('/get_sessions/<int:student_id>')
def get_sessions(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT session_title, file_path FROM chat_session_logs WHERE student_id = ? ORDER BY created_at DESC", (student_id,))
    sessions = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"sessions": [dict(s) for s in sessions]})

@app.route('/load_session')
def load_session():
    path = request.args.get('path')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            return jsonify({"session": json.loads(content)})
    except Exception as e:
        return jsonify({"session": []}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('homepage'))

@app.route('/submit_escalation', methods=['POST'])
def submit_escalation():
    if 'student_id' not in session or 'email' not in session:
        return redirect(url_for('login'))

    student_id = session['student_id']
    email = session['email']
    name = request.form.get('name')
    issue = request.form.get('issue')
    ts = datetime.now()

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO live_escalations (student_id, name, email, issue, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (student_id, name, email, issue, ts))
        conn.commit()
    except Exception as e:
        print("Error:", e)
        return "❌ Database Error.", 400
    finally:
        cursor.close()
        conn.close()

    return render_template("chat_socket.html", student_id=student_id, issue=issue, role='admin')

@app.route('/dashboard')
def dashboard():
    if 'admin' not in session:
        return redirect(url_for('login'))

    admin_email = session['admin']
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM admin WHERE email = ?", (admin_email,))
    admin_row = cursor.fetchone()
    admin_name = admin_row['name'] if admin_row else 'Admin'

    # SQLite uses date('now') for current date comparison
    cursor.execute("""
        SELECT DISTINCT s.id, s.email
        FROM student_admin_chat c
        JOIN student s ON s.id = c.student_id
        WHERE date(c.timestamp) = date('now')
        ORDER BY c.timestamp DESC
    """)
    today_students = cursor.fetchall()

    cursor.execute("SELECT COUNT(DISTINCT student_id) AS total FROM student_chatbot_chat")
    total_bot_users = cursor.fetchone()['total'] or 1

    cursor.execute("SELECT COUNT(DISTINCT student_id) AS failures FROM student_admin_chat")
    failures = cursor.fetchone()['failures'] or 0

    cursor.execute("SELECT COUNT(*) AS count FROM live_escalations")
    live_requests_count = cursor.fetchone()['count'] or 0

    failure_percentage = round((failures / total_bot_users) * 100, 2)
    handled_percentage = 100 - failure_percentage

    cursor.close()
    conn.close()

    return render_template(
        'dashboard.html',
        admin_name=admin_name,
        admin_email=admin_email,
        today_students=today_students,
        total_admin_chats=failures,
        live_requests_count=live_requests_count,
        failure_percentage=failure_percentage,
        handled_percentage=handled_percentage
    )

@app.route('/chat_history_students')
def chat_history_students():
    if 'admin' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT s.name, s.email
        FROM student_chatbot_chat c
        JOIN student s ON s.email = c.email
        ORDER BY c.timestamp DESC
    """)
    students = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('chat_history.html', students=students)

@app.route('/totalcharts')
def totalcharts():
    if 'admin' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT s.id, s.name FROM student_admin_chat c JOIN student s ON c.student_id = s.id")
    students = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('totalcharts.html', students=students)

@app.route('/view_chat/<email>')
def view_chat(email):
    if 'admin' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM student WHERE email = ?", (email,))
    student = cursor.fetchone()

    if not student:
        conn.close()
        return f"No student found with email: {email}"

    student_id = student['id']
    student_name = student['name']

    cursor.execute("""
        SELECT message_from AS sender, message, timestamp 
        FROM student_chatbot_chat
        WHERE student_id = ?
        ORDER BY timestamp
    """, (student_id,))
    chats = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'student_chat_detail.html',
        student_id=student_id,
        student_name=student_name,
        chats=chats
    )

@app.route('/admin_chat/<int:student_id>')
def admin_chat_detail(student_id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    source = request.args.get('source', 'dashboard')
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM student WHERE id = ?", (student_id,))
    student = cursor.fetchone()
    student_name = student['name'] if student else f"Student {student_id}"

    cursor.execute("""
        SELECT message_from AS sender, message, timestamp 
        FROM student_admin_chat 
        WHERE student_id = ? 
        ORDER BY timestamp
    """, (student_id,))
    chat_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "admin_chat_detail.html",
        student_id=student_id,
        student_name=student_name,
        chat_data=chat_data,
        source=source
    )

@app.route('/view_bot_chat/<int:student_id>')
def view_bot_chat(student_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT message_from AS sender, message 
        FROM student_chatbot_chat 
        WHERE student_id = ? 
        ORDER BY timestamp
    """, (student_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/view_chatbot_data')
def view_chatbot_data():
    if 'student_id' not in session:
        return jsonify([])

    student_id = session['student_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT message, message_from FROM student_chatbot_chat WHERE student_id = ? ORDER BY timestamp", (student_id,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify([
        {
            "message": row["message"],
            "sender": row["message_from"].lower()
        } for row in data
    ])

@socketio.on('join_room')
def handle_join(data):
    room = data['room']
    join_room(room)
    print(f"✅ User joined room: {room}")

@socketio.on('send_message')
def handle_send_message(data):
    student_id = int(data['student_id'])
    message = data['message']
    message_from = data['message_from']

    emit('receive_message', {
        'student_id': student_id,
        'message': message,
        'message_from': message_from
    }, room=f"room_{student_id}")

@app.route("/rasa_webhook", methods=["POST"])
def rasa_webhook():
    data = request.get_json()
    user_message = data.get("message")

    try:
        # app.py lo rasa_url line ni ila marchu
        rasa_url = "http://127.0.0.1:5005/webhooks/rest/webhook" 
# '0.0.0.0' badulu '127.0.0.1' try chey, internal communication ki safe.
        payload = {"sender": "student_user", "message": user_message}
        headers = {"Content-Type": "application/json"}

        rasa_response = requests.post(rasa_url, json=payload, headers=headers)
        messages = rasa_response.json()

        return jsonify({"responses": messages})
    except Exception as e:
        print("❌ Error contacting Rasa:", e)
        return jsonify({
            "responses": [{
            "text": f"❌ Could not connect to Rasa: {str(e)}"
            }]
        }), 500

import os
# ... pyna code antha same ...
if __name__ == "__main__":
    # Railway iche port ni pick chestundi, lekapothe 8000
    port = int(os.environ.get("PORT", 8000)) 
    app.run(host='0.0.0.0', port=port)