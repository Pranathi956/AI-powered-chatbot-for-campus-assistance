from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import sqlite3
import os
from typing import Any, Text, Dict, List
from groq import Groq 

# ==========================================
# 1. GROQ CONFIGURATION
# ==========================================
# Replace "YOUR_GROQ_API_KEY" with your actual key
api_key_from_env = os.getenv("GROQ_API_KEY")
client = Groq(api_key="GROQ_API_KEY")

def get_gemini_response(prompt):
    """
    Database info unte dani polish chestundi, 
    lekapothe (out of context) campus chatbot ani polite ga chepthundi.
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are a dedicated College Campus Assistant. "
                        "If the user asks about exams, canteen, bus, or staff, use the provided info to help them. "
                        "If the user asks anything NOT related to the college (like general knowledge, movies, or sports stars), "
                        "politely explain that you are only a campus bot and suggest they ask about college-related topics."
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
# Path logic ni ila marchu
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DB ni 'database' folder lo 'college_db.db' ga fix chestunnam
DB_PATH = os.path.join(BASE_DIR, "..", "database", "college_db.db")

def get_db_connection():
    try:
        if not os.path.exists(DB_PATH):
            return None
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception:
        return None

# ==========================================
# 3. SMART RASA CUSTOM ACTION
# ==========================================
class ActionGeminiEnhancer(Action):
    def name(self) -> Text:
        return "action_gemini_enhancer"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_message = tracker.latest_message.get('text', '').lower()
        intent_name = tracker.latest_message.get('intent', {}).get('name')
        
        connection = get_db_connection()
        raw_info = ""

        if not connection:
            dispatcher.utter_message(text="❌ Database is not responding. Please check back later.")
            return []

        try:
            cursor = connection.cursor()

            # --- SEARCH LOGIC (Everything included) ---
            
            # 1. Exams
            if "exam" in user_message or "test" in user_message:
                cursor.execute("SELECT subject_name, date, time FROM exam")
                rows = cursor.fetchall()
                if rows: raw_info = "Exam Schedule: " + ", ".join([f"{r[0]} on {r[1]} at {r[2]}" for r in rows])

            # 2. Canteen
            elif any(x in user_message for x in ["canteen", "food", "menu"]):
                cursor.execute("SELECT item_name, price, availability FROM canteen")
                rows = cursor.fetchall()
                if rows: raw_info = "Canteen Menu: " + ", ".join([f"{r[0]} costs {r[1]} ({r[2]})" for r in rows])

            # 3. Transport/Bus
            elif any(x in user_message for x in ["bus", "transport", "route"]):
                cursor.execute("SELECT route_name, pickup_point, pickup_time FROM transport")
                rows = cursor.fetchall()
                if rows: raw_info = "Bus Routes: " + ", ".join([f"{r[0]} from {r[1]} at {r[2]}" for r in rows])

            # 4. Courses & Staff
            elif "course" in user_message or "subject" in user_message:
                cursor.execute("SELECT c.name, d.name FROM course c JOIN department d ON c.department_id = d.dept_id")
                rows = cursor.fetchall()
                if rows: raw_info = "Courses: " + ", ".join([f"{r[0]} ({r[1]})" for r in rows])

            elif any(x in user_message for x in ["gym", "library", "college timing"]):
                type_v = "Gym" if "gym" in user_message else ("Library" if "library" in user_message else "College")
                cursor.execute("SELECT time FROM timings WHERE type = ?", (type_v,))
                data = cursor.fetchone()
                if data: raw_info = f"The {type_v} timings are {data[0]}."

            # --- SMART AI ROUTING (Fixes your problem) ---
            
            if intent_name == "greet":
                prompt = "The student said hello. Give a friendly campus assistant greeting and ask how you can help."
            
            elif raw_info != "":
                # Data found in DB
                prompt = f"Using this college info: {raw_info}, answer the student's question: {user_message}"
            
            else:
                # NO data found (Out of context)
                prompt = (f"The student asked: '{user_message}'. This is NOT in our college database. "
                          "Politely tell them you only provide information about the campus (like exams, canteen, bus, etc.) "
                          "and you cannot answer other general questions.")

            # Get response from AI
            enhanced_res = get_gemini_response(prompt)
            
            if enhanced_res:
                dispatcher.utter_message(text=enhanced_res)
            else:
                dispatcher.utter_message(text=f"Database Info: {raw_info}" if raw_info else "I only handle campus-related queries.")

        except Exception as e:
            print(f"❌ Error: {e}")
            dispatcher.utter_message(text="An internal error occurred while processing data.")
        finally:
            if connection:
                connection.close()

        return []