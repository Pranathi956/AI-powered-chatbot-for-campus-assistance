from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import sqlite3
import os
from typing import Any, Text, Dict, List
from groq import Groq 
import sys
# Prathi print ventane kanipinchela chesthundhi
def print_flush(text):
    print(text)
    sys.stdout.flush()
# ==========================================
# 1. GROQ CONFIGURATION
# ==========================================
# FIX: Using the environment variable correctly
"""api_key_from_env = os.getenv("GROQ_API_KEY")"""
client = Groq(api_key="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")

def get_groq_response(prompt):
    """
    Database info unte dani polish chestundi, 
    lekapothe (out of context) campus chatbot ani polite ga chepthundi.
    """
    if not api_key_from_env:
        return "🤖 (Action Error: GROQ_API_KEY not found in Actions environment)"

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are a dedicated College Campus Assistant. "
                        "If the user asks about exams, canteen, bus, or staff, use the provided info to help them. "
                        "If the user asks anything NOT related to the college, "
                        "politely explain that you are only a campus bot."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"⚠️ Groq API Error: {e}")
        return None

# ==========================================
# 2. DATABASE CONFIGURATION
# ==========================================

BASE_DIR = os.getcwd() # ఇది నీ ప్రాజెక్ట్ రూట్ ఫోల్డర్ ని తీసుకుంటుంది
DB_PATH = os.path.join(BASE_DIR, "database", "college_db.db")
print(f"DEBUG: Looking for database at {DB_PATH}") 

def get_db_connection():
    try:
        if not os.path.exists(DB_PATH):
            print(f"❌ DB Path not found: {DB_PATH}")
            return None
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"❌ DB Connection Error: {e}")
        return None

# ==========================================
# 3. SMART RASA CUSTOM ACTION
# ==========================================
class ActionGroqEnhancer(Action):
    def name(self) -> Text:
        # Intent name should match your domain.yml
        return "action_gemini_enhancer" 

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_message = tracker.latest_message.get('text', '').lower()
        intent_name = tracker.latest_message.get('intent', {}).get('name')
        print(f"DEBUG: User message is {user_message}")
        print(f"DEBUG: Checking database at {DB_PATH}")
        print(f"DEBUG: DB exists? {os.path.exists(DB_PATH)}")
        connection = get_db_connection()
        raw_info = ""

        if not connection:
            dispatcher.utter_message(text="❌ Database is not responding.")
            return []

        try:
            cursor = connection.cursor()

            # --- SEARCH LOGIC ---
            if "exam" in user_message or "test" in user_message:
                cursor.execute("SELECT subject_name, date, time FROM exam")
                rows = cursor.fetchall()
                if rows: raw_info = "Exam Schedule: " + ", ".join([f"{r[0]} on {r[1]} at {r[2]}" for r in rows])

            elif any(x in user_message for x in ["canteen", "food", "menu"]):
                cursor.execute("SELECT item_name, price, availability FROM canteen")
                rows = cursor.fetchall()
                if rows: raw_info = "Canteen Menu: " + ", ".join([f"{r[0]} costs {r[1]} ({r[2]})" for r in rows])

            elif any(x in user_message for x in ["bus", "transport", "route"]):
                cursor.execute("SELECT route_name, pickup_point, pickup_time FROM transport")
                rows = cursor.fetchall()
                if rows: raw_info = "Bus Routes: " + ", ".join([f"{r[0]} from {r[1]} at {r[2]}" for r in rows])

            elif "course" in user_message or "subject" in user_message:
                cursor.execute("SELECT c.name, d.name FROM course c JOIN department d ON c.department_id = d.dept_id")
                rows = cursor.fetchall()
                if rows: raw_info = "Courses: " + ", ".join([f"{r[0]} ({r[1]})" for r in rows])

            elif any(x in user_message for x in ["gym", "library", "college timing"]):
                type_v = "Gym" if "gym" in user_message else ("Library" if "library" in user_message else "College")
                cursor.execute("SELECT time FROM timings WHERE type = ?", (type_v,))
                data = cursor.fetchone()
                if data: raw_info = f"The {type_v} timings are {data[0]}."

            # --- AI PROMPT ROUTING ---
            if intent_name == "greet":
                prompt = "The student said hello. Give a friendly campus greeting."
            elif raw_info != "":
                prompt = f"Using this college info: {raw_info}, answer: {user_message}"
            else:
                prompt = f"The student asked: '{user_message}'. Explain you are only a campus bot."

            enhanced_res = get_groq_response(prompt)
            
            if enhanced_res:
                dispatcher.utter_message(text=enhanced_res)
            else:
                dispatcher.utter_message(text=f"Info: {raw_info}" if raw_info else "I only handle campus-related queries.")

        except Exception as e:
            dispatcher.utter_message(text=f"❌ Action Error: {str(e)}")
            print(f"❌ CRITICAL ERROR: {e}")
            return []
        finally:
            if connection:
                connection.close()

        return []
