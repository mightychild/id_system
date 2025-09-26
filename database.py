import sqlite3
import os
import shutil
from config import DATABASE_PATH, STUDENT_PHOTOS_DIR

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def check_and_migrate_schema():
    """Check current schema and migrate if needed"""
    conn = get_db_connection()
    try:
        # Check if users table has is_active column
        cursor = conn.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        migrations = []
        
        # Migration 1: Add is_active to users table
        if 'is_active' not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1")
            migrations.append("Added is_active column to users table")
        
        # Check students table structure
        cursor = conn.execute("PRAGMA table_info(students)")
        student_columns = [column[1] for column in cursor.fetchall()]
        
        # Migration 2: Add id_card_path to students table if missing
        if 'id_card_path' not in student_columns:
            conn.execute("ALTER TABLE students ADD COLUMN id_card_path TEXT")
            migrations.append("Added id_card_path column to students table")
        
        if migrations:
            conn.commit()
            print("Database migrations applied:")
            for migration in migrations:
                print(f"  ✓ {migration}")
        
        return True
        
    except Exception as e:
        print(f"Schema migration error: {e}")
        return False
    finally:
        conn.close()

def init_db():
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    os.makedirs(STUDENT_PHOTOS_DIR, exist_ok=True)
    
    conn = get_db_connection()
    try:
        # Users table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                user_type TEXT NOT NULL,
                full_name TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Enhanced Students table with ID card path storage
        conn.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                department TEXT NOT NULL,
                program TEXT,
                email TEXT,
                phone TEXT,
                date_of_birth TEXT,
                gender TEXT,
                enrollment_date TEXT,
                graduation_date TEXT,
                photo_path TEXT,
                id_card_generated BOOLEAN DEFAULT 0,
                id_card_path TEXT,
                id_card_generated_date TEXT,
                qr_code_data TEXT,
                date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        
        # Create default admin user if not exists
        cursor = conn.execute("SELECT id FROM users WHERE username = 'admin'")
        if cursor.fetchone() is None:
            conn.execute(
                "INSERT INTO users (username, password_hash, user_type, full_name) VALUES (?, ?, ?, ?)",
                ('admin', 'admin123', 'admin', 'System Administrator')
            )
            print("Default admin user created: admin / admin123")
        
        # Create sample student if none exist
        cursor = conn.execute("SELECT COUNT(*) as count FROM students")
        if cursor.fetchone()['count'] == 0:
            conn.execute('''
                INSERT INTO students 
                (student_id, full_name, department, program, email, phone, date_of_birth, gender, enrollment_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                'SE2024001', 'John Doe', 'Software Engineering', 
                'BSc Software Engineering', 'john.doe@university.edu',
                '+1234567890', '2000-01-15', 'Male', '2024-09-01'
            ))
            print("Sample student created: SE2024001")
        
        conn.commit()
        print("Database initialized successfully.")
        
        # Apply any necessary migrations
        check_and_migrate_schema()
        
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

def get_all_students():
    conn = get_db_connection()
    try:
        cursor = conn.execute('''
            SELECT * FROM students 
            ORDER BY student_id
        ''')
        return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error getting all students: {e}")
        return []
    finally:
        conn.close()

def get_student_by_id(student_id):
    conn = get_db_connection()
    try:
        cursor = conn.execute('SELECT * FROM students WHERE student_id = ?', (student_id,))
        result = cursor.fetchone()
        return dict(result) if result else None
    except Exception as e:
        print(f"Error getting student by ID: {e}")
        return None
    finally:
        conn.close()

def get_student_count():
    conn = get_db_connection()
    try:
        cursor = conn.execute("SELECT COUNT(*) as count FROM students")
        return cursor.fetchone()['count']
    except Exception as e:
        print(f"Error getting student count: {e}")
        return 0
    finally:
        conn.close()

def add_student(student_data):
    """Add new student with photo debugging"""
    conn = get_db_connection()
    try:
        print(f"DEBUG: Adding student to database: {student_data['student_id']}")
        print(f"DEBUG: Photo path being saved: {student_data.get('photo_path')}")
        
        conn.execute('''
            INSERT INTO students 
            (student_id, full_name, department, program, email, phone, 
             date_of_birth, gender, enrollment_date, graduation_date, photo_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            student_data['student_id'],
            student_data['full_name'],
            student_data['department'],
            student_data.get('program', ''),
            student_data.get('email', ''),
            student_data.get('phone', ''),
            student_data.get('date_of_birth', ''),
            student_data.get('gender', ''),
            student_data.get('enrollment_date', ''),
            student_data.get('graduation_date', ''),
            student_data.get('photo_path', '')  # This should now contain the filename
        ))
        conn.commit()
        
        # Verify the student was added
        cursor = conn.execute("SELECT photo_path FROM students WHERE student_id = ?", 
                            (student_data['student_id'],))
        result = cursor.fetchone()
        print(f"DEBUG: Student added. Photo path in database: {result['photo_path'] if result else 'None'}")
        
        return True
        
    except sqlite3.IntegrityError:
        print(f"ERROR: Student with ID {student_data['student_id']} already exists")
        return False
    except Exception as e:
        print(f"ERROR adding student: {e}")
        return False
    finally:
        conn.close()

def update_student(student_id, student_data):
    conn = get_db_connection()
    try:
        conn.execute('''
            UPDATE students SET 
            full_name = ?, department = ?, program = ?, email = ?, phone = ?,
            date_of_birth = ?, gender = ?, enrollment_date = ?, graduation_date = ?,
            photo_path = ?, last_updated = CURRENT_TIMESTAMP
            WHERE student_id = ?
        ''', (
            student_data['full_name'],
            student_data['department'],
            student_data.get('program', ''),
            student_data.get('email', ''),
            student_data.get('phone', ''),
            student_data.get('date_of_birth', ''),
            student_data.get('gender', ''),
            student_data.get('enrollment_date', ''),
            student_data.get('graduation_date', ''),
            student_data.get('photo_path', ''),
            student_id
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating student: {e}")
        return False
    finally:
        conn.close()

def delete_student(student_id):
    conn = get_db_connection()
    try:
        # First get student data to delete associated files
        student = get_student_by_id(student_id)
        if student:
            # Delete photo if exists
            if student.get('photo_path'):
                photo_path = os.path.join(STUDENT_PHOTOS_DIR, student['photo_path'])
                if os.path.exists(photo_path):
                    os.remove(photo_path)
            
            # Delete ID card if exists
            if student.get('id_card_path'):
                id_card_path = student['id_card_path']
                if os.path.exists(id_card_path):
                    os.remove(id_card_path)
        
        conn.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting student: {e}")
        return False
    finally:
        conn.close()

def save_student_photo(student_id, source_photo_path):
    """Save student photo and return the filename"""
    try:
        if not os.path.exists(source_photo_path):
            return None
        
        # Create filename from student_id
        file_ext = os.path.splitext(source_photo_path)[1].lower()
        filename = f"{student_id}{file_ext}"
        dest_path = os.path.join(STUDENT_PHOTOS_DIR, filename)
        
        # Copy photo to student photos directory
        shutil.copy2(source_photo_path, dest_path)
        return filename
    except Exception as e:
        print(f"Error saving photo: {e}")
        return None
    
def get_student_photo_path(student_id):
    """Get the photo path for a student, handling special characters in ID"""
    conn = get_db_connection()
    try:
        cursor = conn.execute('SELECT photo_path FROM students WHERE student_id = ?', (student_id,))
        result = cursor.fetchone()
        if result and result['photo_path']:
            photo_path = result['photo_path']
            # If the student ID contains slashes, handle the filename conversion
            if '/' in student_id and '/' in photo_path:
                safe_student_id = student_id.replace('/', '_')
                photo_path = photo_path.replace(student_id, safe_student_id)
            return photo_path
        return None
    except Exception as e:
        print(f"Error getting student photo path: {e}")
        return None
    finally:
        conn.close()

def mark_id_card_generated(student_id, id_card_path, qr_data):
    """Mark ID card as generated and store the file path"""
    conn = get_db_connection()
    try:
        conn.execute('''
            UPDATE students SET 
            id_card_generated = 1, 
            id_card_path = ?,
            id_card_generated_date = CURRENT_TIMESTAMP,
            qr_code_data = ?
            WHERE student_id = ?
        ''', (id_card_path, qr_data, student_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error marking ID card generated: {e}")
        return False
    finally:
        conn.close()

def get_student_id_card_path(student_id):
    """Get the path to a student's ID card if it exists"""
    conn = get_db_connection()
    try:
        cursor = conn.execute('SELECT id_card_path FROM students WHERE student_id = ?', (student_id,))
        result = cursor.fetchone()
        return result['id_card_path'] if result and result['id_card_path'] else None
    except Exception as e:
        print(f"Error getting ID card path: {e}")
        return None
    finally:
        conn.close()

def get_all_generated_id_cards():
    """Get all generated ID cards with student information for gallery"""
    conn = get_db_connection()
    try:
        cursor = conn.execute('''
            SELECT student_id, full_name, program, photo_path, 
                   id_card_path, id_card_generated_date 
            FROM students 
            WHERE id_card_generated = 1 AND id_card_path IS NOT NULL
            ORDER BY full_name
        ''')
        
        id_cards = []
        for row in cursor.fetchall():
            card_data = dict(row)
            if os.path.exists(card_data['id_card_path']):
                card_data['has_photo'] = bool(card_data.get('photo_path'))
                id_cards.append(card_data)
        
        return id_cards
    except Exception as e:
        print(f"Error getting generated ID cards: {e}")
        return []
    finally:
        conn.close()

def authenticate_user(username, password):
    """Authenticate user with plain text password (for demo)"""
    conn = get_db_connection()
    try:
        # Try the new schema first (with is_active column)
        try:
            cursor = conn.execute(
                "SELECT * FROM users WHERE username = ? AND password_hash = ? AND is_active = 1",
                (username, password)
            )
        except sqlite3.OperationalError:
            # Fallback to old schema (without is_active column)
            cursor = conn.execute(
                "SELECT * FROM users WHERE username = ? AND password_hash = ?",
                (username, password)
            )
        
        user = cursor.fetchone()
        return dict(user) if user else None
    except Exception as e:
        print(f"Authentication error: {e}")
        return None
    finally:
        conn.close()