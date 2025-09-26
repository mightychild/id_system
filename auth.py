import sqlite3
from config import DATABASE_PATH

def get_db_connection():
    """Local db connection to avoid circular imports"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def authenticate_user(username, password, user_type="admin"):
    """Authentication with schema fallback"""
    conn = get_db_connection()
    try:
        # Try new schema first (with is_active column)
        try:
            cursor = conn.execute(
                "SELECT * FROM users WHERE username = ? AND user_type = ? AND is_active = 1",
                (username, user_type)
            )
        except sqlite3.OperationalError:
            # Fallback to old schema (without is_active column)
            cursor = conn.execute(
                "SELECT * FROM users WHERE username = ? AND user_type = ?",
                (username, user_type)
            )
        
        user = cursor.fetchone()
        
        if user:
            # Simple password check (plain text for now)
            if user['password_hash'] == password:
                return dict(user)
        return None
    except Exception as e:
        print(f"Authentication error: {e}")
        return None
    finally:
        conn.close()