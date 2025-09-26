import sys
import os
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db
from login_window import LoginWindow

def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    print("Uncaught exception:", exc_type, exc_value)
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    
    # Show error message to user
    try:
        app = QApplication.instance()
        if app:
            QMessageBox.critical(None, "Unexpected Error", 
                               f"An unexpected error occurred:\n\n{str(exc_value)}\n\nPlease restart the application.")
    except:
        pass

def main():
    # Set global exception handler
    sys.excepthook = handle_exception
    
    # Initialize database
    print("🚀 Starting ID Card System...")
    print("📊 Initializing database...")
    
    try:
        init_db()
        print("✅ Database initialization completed")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        QMessageBox.critical(None, "Database Error", 
                           f"Failed to initialize database:\n\n{str(e)}")
        return 1
    
    # Create application
    app = QApplication(sys.argv)
    
    # Set application-wide style
    app.setStyleSheet("""
        * {
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QMessageBox {
            background: white;
        }
    """)
    
    try:
        # Create and show login window
        window = LoginWindow()
        window.show()
        
        print("✅ System ready! Login with: admin / admin123")
        
        return app.exec_()
        
    except Exception as e:
        print(f"❌ Application startup failed: {e}")
        QMessageBox.critical(None, "Startup Error", 
                           f"Failed to start application:\n\n{str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main())