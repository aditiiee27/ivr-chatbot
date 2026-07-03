import sqlite3
from datetime import datetime
import config

def get_db_connection():
    """
    Establishes and returns a connection to the SQLite database.
    Enables sqlite3.Row formatting to allow accessing columns by name.
    """
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initializes the database by creating tables if they do not exist:
    - customers: holds details of registered customers.
    - chat_history: stores conversations linked by a session identifier.
    - feedback: saves ratings and text comments from users.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Create Customers Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Create Chat History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL, -- 'user' or 'assistant'
            content TEXT NOT NULL,
            audio_file TEXT, -- Filename of the spoken audio response, if any
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 3. Create Feedback Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            rating INTEGER NOT NULL,
            comments TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database tables initialized successfully.")

def save_customer(name, email, phone):
    """
    Saves new customer details. If the email or phone already exists,
    retrieves and returns the existing customer record.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if customer already exists by phone or email
        cursor.execute(
            "SELECT id FROM customers WHERE phone = ? OR email = ?", 
            (phone, email)
        )
        existing = cursor.fetchone()
        if existing:
            return existing['id']
            
        cursor.execute(
            "INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)",
            (name, email, phone)
        )
        conn.commit()
        customer_id = cursor.lastrowid
        return customer_id
    except sqlite3.Error as e:
        print(f"Database error while saving customer: {e}")
        return None
    finally:
        conn.close()

def get_customer_by_phone(phone):
    """
    Fetches a customer record by phone number.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE phone = ?", (phone,))
    customer = cursor.fetchone()
    conn.close()
    return dict(customer) if customer else None

def save_chat_message(session_id, role, content, audio_file=None):
    """
    Inserts a single message (from user or assistant) into the chat history.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO chat_history (session_id, role, content, audio_file) VALUES (?, ?, ?, ?)",
            (session_id, role, content, audio_file)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Database error while saving chat message: {e}")
        return None
    finally:
        conn.close()

def get_chat_history(session_id):
    """
    Retrieves all messages associated with a session ID, sorted chronologically.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content, audio_file, created_at FROM chat_history WHERE session_id = ? ORDER BY created_at ASC",
        (session_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_feedback(session_id, rating, comments):
    """
    Stores customer feedback rating and comments.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO feedback (session_id, rating, comments) VALUES (?, ?, ?)",
            (session_id, rating, comments)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Database error while saving feedback: {e}")
        return None
    finally:
        conn.close()
