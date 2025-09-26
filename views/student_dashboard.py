from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QMessageBox, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap

from config import DEPARTMENT_NAME

class StudentDashboard(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle(f"ID Card System - Student Dashboard")
        
        # Set window size
        self.setGeometry(100, 100, 1000, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # Welcome message
        welcome_label = QLabel(f"Welcome, {self.user_data['full_name']}!")
        welcome_label.setFont(QFont("Arial", 20, QFont.Bold))
        welcome_label.setAlignment(Qt.AlignCenter)
        
        # Department info
        dept_label = QLabel(DEPARTMENT_NAME)
        dept_label.setFont(QFont("Arial", 14))
        dept_label.setAlignment(Qt.AlignCenter)
        
        # Student info
        info_label = QLabel(f"Student ID: {self.user_data.get('student_id', 'N/A')}")
        info_label.setFont(QFont("Arial", 12))
        info_label.setAlignment(Qt.AlignCenter)
        
        # Placeholder for future features
        placeholder = QLabel("Student Dashboard - Features coming soon...\n\n"
                           "• View My ID Card\n• Update Profile\n• Request New ID Card")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("""
            background-color: #f0f0f0;
            border: 2px dashed #ccc;
            border-radius: 10px;
            padding: 20px;
            margin: 20px;
        """)
        
        # Logout button
        logout_btn = QPushButton("Logout")
        logout_btn.setFixedSize(100, 40)
        logout_btn.clicked.connect(self.logout)
        
        layout.addWidget(welcome_label)
        layout.addWidget(dept_label)
        layout.addWidget(info_label)
        layout.addWidget(placeholder)
        layout.addWidget(logout_btn)
        
        central_widget.setLayout(layout)
    
    def logout(self):
        """Handle logout."""
        reply = QMessageBox.question(self, "Logout", "Are you sure you want to logout?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            from login_window import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.show()
            self.close()