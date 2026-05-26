import pymysql
from create import create_database

# Step 1: Create the database
create_database("college_db")

# Step 2: Connect to the database
connection = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="college_db",
    port=3306
)
cursor = connection.cursor()

# ───── Table 1: department ─────
def create_department_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS department (
            dept_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) UNIQUE
        )
    """)
    print("✅ department table created.")

# ───── Table 2: staff ─────
def create_staff_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staff (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100) UNIQUE,
            designation VARCHAR(100),
            department_id INT,
            FOREIGN KEY (department_id) REFERENCES department(dept_id)
        )
    """)
    print("✅ staff table created.")

# ───── Table 3: course ─────
def create_course_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS course (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) UNIQUE,
            department_id INT,
            FOREIGN KEY (department_id) REFERENCES department(dept_id)
        )
    """)
    print("✅ course table created.")

# ───── Table 4: timings ─────
def create_timings_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS timings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            type VARCHAR(50) UNIQUE,
            time VARCHAR(100)
        )
    """)
    print("✅ timings table created.")

# ───── Table 5: exam ─────
def create_exam_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exam (
            id INT AUTO_INCREMENT PRIMARY KEY,
            subject_name VARCHAR(100),
            date DATE,
            time TIME
        )
    """)
    print("✅ exam table created.")

# ───── Table 6: student ─────
def create_student_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100) UNIQUE, -- Should end with '@college.com'
            password VARCHAR(50) NOT NULL,
            contact VARCHAR(15),
            department_id INT,
            FOREIGN KEY (department_id) REFERENCES department(dept_id)
        )
    """)
    print("✅ student table created.")

# ───── Table 7: admin ─────
def create_admin_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100) UNIQUE,
            password VARCHAR(100)
        )
    """)
    print("✅ admin table created with name, email, and password.")

# ───── Table 8: events ─────
def create_events_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INT AUTO_INCREMENT PRIMARY KEY,
            event_name VARCHAR(100) UNIQUE,
            description TEXT,
            location VARCHAR(100),
            date DATE,
            time TIME,
            organizer VARCHAR(100)
        )
    """)
    print("✅ events table created.")

# ───── Table 9: student_admin_chat ─────
def create_student_admin_chat_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_admin_chat (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            admin_id INT,
            message_from ENUM('student', 'admin') NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES student(id),
            FOREIGN KEY (admin_id) REFERENCES admin(id)
        )
    """)
    print("✅ student_admin_chat table created.")

def create_student_chatbot_chat_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_chatbot_chat (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            email VARCHAR(100) NOT NULL, -- Should match @college.com
            message TEXT NOT NULL,
            message_from ENUM('student', 'bot') NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES student(id)
        )
    """)
    print("✅ student_chatbot_chat table created with email column.")

# ───── Table 10: live_escalations ─────
def create_live_escalations_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS live_escalations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT,
            name VARCHAR(100),
            email VARCHAR(100),
            issue TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE
        )
    """)
    print("✅ live_escalations table created.")

# ───── Table 11: chat_session_logs ─────
def chat_session_logs():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_session_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            session_title VARCHAR(255),
            file_name VARCHAR(255),
            file_path TEXT,
            created_at DATETIME,
            FOREIGN KEY (student_id) REFERENCES student(id)
        )
    """)
    print("✅ chat_session_logs table created.")

# ───── Table 12: holidays ─────
def create_holidays_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS holidays (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            date DATE,
            description TEXT
        )
    """)
    print("✅ holidays table created.")

def create_locations_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            building VARCHAR(50),
            floor VARCHAR(20),
            UNIQUE KEY unique_location (name, building, floor)
        )
    """)
    print("✅ locations table created with UNIQUE constraint.")

def create_hostels_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hostels (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL Unique,
            description TEXT,
            floor VARCHAR(20),
            capacity INT
        )
    """)
    print("✅ hostels table created.")

# Step 3: Create all tables
def create_all_tables():
    create_department_table()
    create_staff_table()
    create_course_table()
    create_timings_table()
    create_exam_table()
    create_student_table()
    create_admin_table()
    create_events_table()
    create_student_admin_chat_table()
    create_live_escalations_table()
    chat_session_logs()
    create_student_chatbot_chat_table()
    create_holidays_table()
    create_locations_table()
    create_hostels_table()

# Step 4: Execute and close
create_all_tables()
connection.commit()
cursor.close()
connection.close()
print("🔒 All tables created and connection closed.")
