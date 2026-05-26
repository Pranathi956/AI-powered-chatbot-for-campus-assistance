import sqlite3
import os

def setup_db():
    db_folder = 'database'
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)
    
    db_path = r"D:\Internship HCL\HCL Internship Project\database\college_db.db"
    conn = sqlite3.connect(db_path)    
    cursor = conn.cursor()

    # --- 1. TABLES CREATION (Prathi table cover chesanu) ---
    queries = [
        "CREATE TABLE IF NOT EXISTS department (dept_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)",
        "CREATE TABLE IF NOT EXISTS admin (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT UNIQUE, password TEXT)",
        "CREATE TABLE IF NOT EXISTS student (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT UNIQUE, password TEXT, contact TEXT, department_id INTEGER, FOREIGN KEY(department_id) REFERENCES department(dept_id))",
        "CREATE TABLE IF NOT EXISTS course (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, department_id INTEGER, FOREIGN KEY(department_id) REFERENCES department(dept_id))",
        "CREATE TABLE IF NOT EXISTS student_admin_chat (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, admin_id INTEGER, message_from TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)",
        "CREATE TABLE IF NOT EXISTS student_chatbot_chat (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, email TEXT, message TEXT, message_from TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)",
        "CREATE TABLE IF NOT EXISTS live_escalations (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, name TEXT, email TEXT, issue TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)",
        "CREATE TABLE IF NOT EXISTS timings (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, time TEXT)",
        "CREATE TABLE IF NOT EXISTS staff (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, designation TEXT, department_id INTEGER)",
        "CREATE TABLE IF NOT EXISTS holidays (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, date TEXT)",
        "CREATE TABLE IF NOT EXISTS exam (id INTEGER PRIMARY KEY AUTOINCREMENT, subject_name TEXT, date TEXT, time TEXT)",
        "CREATE TABLE IF NOT EXISTS canteen (id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT, price TEXT, availability TEXT)",
        "CREATE TABLE IF NOT EXISTS transport (id INTEGER PRIMARY KEY AUTOINCREMENT, route_name TEXT, pickup_point TEXT, pickup_time TEXT)",
        "CREATE TABLE IF NOT EXISTS hostel (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, warden_name TEXT, contact TEXT)",
        "CREATE TABLE IF NOT EXISTS sports (id INTEGER PRIMARY KEY AUTOINCREMENT, sport_name TEXT, coach TEXT, timings TEXT)"
    ]

    for q in queries:
        cursor.execute(q)

    # --- 2. DATA INSERTION (Chala ekkuva data) ---
    
    # Admin & Departments
    cursor.execute("INSERT OR IGNORE INTO admin (name, email, password) VALUES ('Main Admin', 'admin1@college.com', 'Admin@123')")
    depts = [('Computer Science and Engineering',), ('Electronics and Communication',), ('Information Technology',), ('Mechanical Engineering',)]
    cursor.executemany("INSERT OR IGNORE INTO department (name) VALUES (?)", depts)

    # Courses
    courses_data = [
        ('Python Programming', 1), ('Data Structures', 1), ('AI & ML', 1),
        ('Microprocessors', 2), ('Embedded Systems', 2), ('Cloud Computing', 3),
        ('Thermodynamics', 4), ('Robotics', 4)
    ]
    cursor.executemany("INSERT OR IGNORE INTO course (name, department_id) VALUES (?, ?)", courses_data)

    # Exams (Idi ippudu miss avvadhu!)
    exams_data = [
        ('Python Basics', '2026-06-10', '10:00 AM'),
        ('DBMS Advanced', '2026-06-12', '02:00 PM'),
        ('Network Security', '2026-06-15', '10:00 AM'),
        ('Digital Logic', '2026-06-18', '10:00 AM')
    ]
    cursor.executemany("INSERT OR IGNORE INTO exam (subject_name, date, time) VALUES (?, ?, ?)", exams_data)

    # Holidays
    holidays_data = [('Summer Break', 'May 20 - June 10'), ('Bakrid', 'June 16, 2026'), ('Independence Day', 'August 15, 2026')]
    cursor.executemany("INSERT OR IGNORE INTO holidays (name, date) VALUES (?, ?)", holidays_data)

    # Timings (Gym, Library, etc.)
    timings_data = [('Gym', '6 AM - 9 PM'), ('Library', '8 AM - 10 PM'), ('College', '9 AM - 4:30 PM'), ('Lab', '10 AM - 5 PM')]
    cursor.executemany("INSERT OR IGNORE INTO timings (type, time) VALUES (?, ?)", timings_data)

    # Canteen & Transport
    canteen_data = [('Coffee', '₹20', 'Available'), ('Biryani', '₹80', '1 PM - 2 PM'), ('Samosa', '₹15', 'Evening'), ('Juice', '₹30', 'Morning')]
    cursor.executemany("INSERT OR IGNORE INTO canteen (item_name, price, availability) VALUES (?, ?, ?)", canteen_data)
    
    bus_data = [('Route 101', 'KPHB', '7:20 AM'), ('Route 102', 'Uppal', '7:10 AM'), ('Route 103', 'LB Nagar', '7:00 AM')]
    cursor.executemany("INSERT OR IGNORE INTO transport (route_name, pickup_point, pickup_time) VALUES (?, ?, ?)", bus_data)

    # Hostel & Sports
    cursor.execute("INSERT OR IGNORE INTO hostel (type, warden_name, contact) VALUES ('Boys', 'Mr. Rajasekhar', '9848012345')")
    cursor.execute("INSERT OR IGNORE INTO hostel (type, warden_name, contact) VALUES ('Girls', 'Mrs. Lakshmi', '9848054321')")
    cursor.execute("INSERT OR IGNORE INTO sports (sport_name, coach, timings) VALUES ('Cricket', 'Mr. Anand', '4:30 PM - 6:30 PM')")

    conn.commit()
    conn.close()
    print("✅ Full Ultimate Database is Ready with ALL tables and data!")

if __name__ == "__main__":
    setup_db()