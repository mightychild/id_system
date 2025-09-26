
import os
import sys

print("=== DEBUG: Checking Current Directory ===")
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Current directory: {current_dir}")
print(f"Python path: {sys.path}")
print("\n=== Files in directory ===")

files = os.listdir(current_dir)
for file in files:
    print(f"📄 {file}")

print(f"\n=== Looking for login_window ===")
py_files = [f for f in files if f.endswith('.py')]
print("Python files found:", py_files)

# Check if login_window.py exists
login_window_exists = 'login_window.py' in files
print(f"login_window.py exists: {login_window_exists}")

if login_window_exists:
    print("\n=== Testing import ===")
    try:
        # Add current directory to path explicitly
        sys.path.insert(0, current_dir)
        from login_window import LoginWindow
        print("✅ SUCCESS: login_window imported successfully!")
    except ImportError as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
else:
    print("\n❌ login_window.py not found in directory!")
