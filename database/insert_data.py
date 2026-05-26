import pymysql

# Connect to the existing database
connection = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="college_db",
    port=3306
)
cursor = connection.cursor()

# ───── Insert Departments ─────
def insert_departments():
    departments = [
        'Computer Science and Engineering',
        'Electronics and Communication Engineering',
        'Electrical and Electronics Engineering',
        'Mechanical Engineering',
        'Civil Engineering',
        'Information Technology',
        'Biomedical Engineering',
        'Chemical Engineering'
    ]
    for name in departments:
        cursor.execute("INSERT IGNORE INTO department (name) VALUES (%s)", (name,))
    print("✅ Departments inserted.")

# ───── Insert Staff ─────
def insert_staff():
    staff_members = [
        ('Dr. A. Kumar', 'kumar@college.com', 'Professor', 1),
        ('Ms. B. Sharma', 'sharma@college.com', 'Assistant Professor', 1),
        ('Dr. C. Iyer', 'iyer@college.com', 'HOD', 2),
        ('Mr. D. Patel', 'patel@college.com', 'Associate Professor', 2),
        ('Ms. E. Rao', 'rao@college.com', 'Lecturer', 3),
        ('Dr. F. Verma', 'verma@college.com', 'Professor', 4),
        ('Mr. G. Singh', 'singh@college.com', 'Lab Assistant', 5),
        ('Ms. H. Das', 'das@college.com', 'Assistant Professor', 6),
        ('Dr. I. George', 'george@college.com', 'HOD', 7),
        ('Mr. J. Khan', 'khan@college.com', 'Lecturer', 8)
    ]
    for name, email, designation, dept_id in staff_members:
        cursor.execute("""
            INSERT IGNORE INTO staff (name, email, designation, department_id)
            VALUES (%s, %s, %s, %s)
        """, (name, email, designation, dept_id))
    print("✅ Staff inserted.")

# ───── Insert Courses ─────
def insert_courses():
    courses = [
        # dept_id 1 - CSE
        ('Data Structures and Algorithms', 1),
        ('Operating Systems', 1),
        ('Database Management Systems', 1),
        ('Computer Networks', 1),
        ('Artificial Intelligence', 1),
        # dept_id 2 - ECE
        ('Digital Electronics', 2),
        ('Signals and Systems', 2),
        ('VLSI Design', 2),
        ('Embedded Systems', 2),
        ('Communication Systems', 2),
        # dept_id 3 - EEE
        ('Power Systems', 3),
        ('Control Systems', 3),
        ('Electrical Machines', 3),
        ('Power Electronics', 3),
        ('Switchgear and Protection', 3),
        # dept_id 4 - MECH
        ('Thermodynamics', 4),
        ('Fluid Mechanics', 4),
        ('Heat Transfer', 4),
        ('Manufacturing Technology', 4),
        ('Machine Design', 4),
        # dept_id 5 - CIVIL
        ('Structural Analysis', 5),
        ('Construction Materials', 5),
        ('Environmental Engineering', 5),
        ('Surveying', 5),
        ('Transportation Engineering', 5),
        # dept_id 6 - IT
        ('Web Technologies', 6),
        ('Software Engineering', 6),
        ('Cyber Security', 6),
        ('Cloud Computing', 6),
        ('Big Data Analytics', 6),
        # dept_id 7 - BME
        ('Biomedical Instrumentation', 7),
        ('Medical Imaging', 7),
        ('Biomaterials', 7),
        ('Human Anatomy and Physiology', 7),
        ('Rehabilitation Engineering', 7),
        # dept_id 8 - Chemical
        ('Chemical Reaction Engineering', 8),
        ('Fluid Mechanics for Chemical Engineers', 8),
        ('Process Dynamics and Control', 8),
        ('Heat Transfer Operations', 8),
        ('Mass Transfer', 8)
    ]
    for name, dept_id in courses:
        cursor.execute("INSERT IGNORE INTO course (name, department_id) VALUES (%s, %s)", (name, dept_id))
    print("✅ Courses inserted.")

# ───── Insert Timings ─────
def insert_timings():
    timings = [
        ('College', '9:00 AM to 4:00 PM'),
        ('Lunch', '12:30 PM to 1:30 PM'),
        ('Library', '03:00 PM to 05:00 PM'),
        ('Gym', '5 AM to 7 AM and 7 PM to 9 PM')
    ]
    for type_, time in timings:
        cursor.execute("INSERT IGNORE INTO timings (type, time) VALUES (%s, %s)", (type_, time))
    print("✅ Timings inserted.")

# ───── Insert Students ─────
def insert_students():
    students = [
        ('Nikhil Reddy', 'student1@college.com', 'pass123', '9876543210', 1),
        ('Ananya Rao', 'student2@college.com', 'pass456', '9123456780', 2)
    ]
    for name, email, password, contact, dept_id in students:
        cursor.execute("""
            INSERT IGNORE INTO student (name, email, password, contact, department_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, email, password, contact, dept_id))
    print("✅ Students inserted.")

# ───── Insert Admins ─────
def insert_admins():
    admins = [
        ('Admin One', 'admin1@college.com', 'adminpass'),
        ('Admin Two', 'admin2@college.com', 'adminpass2')
    ]
    cursor.executemany("""
        INSERT IGNORE INTO admin (name, email, password)
        VALUES (%s, %s, %s)
    """, admins)
    print("✅ Admins inserted.")


# ───── Insert Holidays ─────
def insert_holidays():
    holidays = [
        ('Independence Day', '2025-08-15', 'National holiday'),
        ('Republic Day', '2026-01-26', 'National holiday'),
        ('Pongal', '2025-01-14', 'Regional festival'),
    ]
    for name, date, desc in holidays:
        cursor.execute("INSERT IGNORE INTO holidays (name, date, description) VALUES (%s, %s, %s)", (name, date, desc))
    print("✅ Holidays inserted.")

# ───── Insert Events ─────
def insert_events():
    events = [
        ('Tech Fest 2025', 'National level technical event', 'Main Auditorium', '2025-09-10', '10:00:00', 'Dr. A. Kumar'),
        ('Sports Day', 'Annual sports meet', 'Grounds', '2025-12-01', '09:00:00', 'Sports Committee')
    ]
    for name, desc, location, date, time, organizer in events:
        cursor.execute("""
            INSERT IGNORE INTO events (event_name, description, location, date, time, organizer)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, desc, location, date, time, organizer))
    print("✅ Events inserted.")

# ───── Insert Exams ─────
def insert_exams():
    exams = [
        ('Data Structures and Algorithms', '2025-07-15', '10:00:00'),
        ('Digital Electronics', '2025-07-17', '02:00:00')
    ]
    cursor.executemany("""
        INSERT IGNORE INTO exam (subject_name, date, time)
        VALUES (%s, %s, %s)
    """, exams)
    print("✅ Exams inserted.")

# ───── Insert Chatbot Chat ─────
def insert_student_chatbot_chat():
    data = [
        (1, 'student1@college.com', "What is my exam date?", "student", "2025-07-11 10:05:00"),
        (1, 'student1@college.com', "Your exam is on 15th July.", "bot", "2025-07-11 10:05:01"),
        (2, 'student2@college.com', "Where is the library?", "student", "2025-07-11 10:10:00"),
        (2, 'student2@college.com', "The library is in Block B.", "bot", "2025-07-11 10:10:01")
    ]
    cursor.executemany("""
        INSERT INTO student_chatbot_chat (student_id, email, message, message_from, timestamp)
        VALUES (%s, %s, %s, %s, %s)
    """, data)
    print("✅ student_chatbot_chat inserted.")

# ───── Insert Admin-Student Chat ─────
def insert_student_admin_chat():
    data = [
        (1, 1, 'student', 'I can’t register for the elective course.'),
        (1, 1, 'admin', 'Which course do you want to register?'),
        (2, 1, 'student', 'Can I get my hall ticket?'),
        (2, 1, 'admin', "Check the student portal under 'Exams'.")
    ]
    cursor.executemany("""
        INSERT INTO student_admin_chat (student_id, admin_id, message_from, message)
        VALUES (%s, %s, %s, %s)
    """, data)
    print("✅ student_admin_chat inserted.")

# ───── Insert Session Logs ─────
def insert_chat_session_logs():
    logs = [
        (1, "Library Chat", "library.txt", "/sessions/library.txt", "2025-07-11 10:15:00"),
        (2, "Exam Info", "exam.txt", "/sessions/exam.txt", "2025-07-11 10:20:00")
    ]
    cursor.executemany("""
        INSERT INTO chat_session_logs (student_id, session_title, file_name, file_path, created_at)
        VALUES (%s, %s, %s, %s, %s)
    """, logs)
    print("✅ chat_session_logs inserted.")

def insert_locations():
    locations = [
        ('Canteen', 'Central food court', 'Block A', 'Ground'),
        ('Gym', 'Fitness and wellness center', 'Block B', '1st'),
        ('Library', 'Main campus library', 'Block C', '2nd'),
        ('Auditorium', 'Event and seminar hall', 'Block D', 'Ground'),
        ('Lab 1', 'Computer Science Lab', 'Block E', '3rd'),
        ('CSE Department', 'Computer Science & Engineering Department Office', 'Block F', '2nd'),
        ('ECE Department', 'Electronics and Communication Engineering Department', 'Block G', '3rd'),
        ('EEE Department', 'Electrical and Electronics Engineering Department', 'Block H', '1st'),
        ('Mechanical Department', 'Mechanical Engineering Department', 'Block I', '2nd'),
        ('Civil Department', 'Civil Engineering Department', 'Block J', 'Ground'),
        ('Finance Department', 'Finance and Accounts Office', 'Admin Block', '1st'),
        ('Admissions Office', 'Student Admission and Enquiry Center', 'Admin Block', 'Ground'),
    ]

    for name, description, building, floor in locations:
        cursor.execute("""
            INSERT IGNORE INTO locations (name, description, building, floor)
            VALUES (%s, %s, %s, %s)
        """, (name, description, building, floor))

    print("✅ Locations inserted (duplicates ignored).")

def insert_hostels_data():
    hostels = [
        ("Vedhavathi", "Boys hostel", "Ground to 20th", 700),
        ("Ganga", "Boys hostel", "Ground to 21st", 500),
        ("Yamuna", "Girls hostel", "Ground to 7th", 550),
        ("Kaveri", "Girls hostel", "Ground to 7th", 450),
        ("Krishna", "Girls hostel", "Ground to 7th", 500)
    ]

    for name, desc, floor, cap in hostels:
        cursor.execute("""
            INSERT IGNORE INTO hostels (name, description, floor, capacity)
            VALUES (%s, %s, %s, %s)
        """, (name, desc, floor, cap))

    print("✅ Hostel data inserted (duplicates skipped).")

# ───── Run All Insert Functions ─────
insert_departments()
insert_staff()
insert_courses()
insert_timings()
insert_students()
insert_admins()
insert_holidays()
insert_events()
insert_exams()
insert_student_chatbot_chat()
insert_student_admin_chat()
insert_chat_session_logs()

# ───── Final Commit & Close ─────
connection.commit()
cursor.close()
connection.close()
print("🔒 All data inserted and connection closed.")
