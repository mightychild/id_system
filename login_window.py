from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QApplication,
                             QFrame, QHBoxLayout)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon
import os

from database import authenticate_user
from config import DEPARTMENT_NAME

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("University ID Card System - Login")
        self.setFixedSize(900, 700)
        
        # Center window on screen
        self.center_window()
        
        # Set modern gradient background
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #667eea, stop: 1 #764ba2);
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(0)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Main login container
        login_container = QFrame()
        login_container.setFixedSize(800, 600)
        login_container.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.3);
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            }
        """)
        
        container_layout = QHBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Left side - University branding
        left_panel = self.create_left_panel()
        container_layout.addWidget(left_panel)
        
        # Right side - Login form
        right_panel = self.create_right_panel()
        container_layout.addWidget(right_panel)
        
        login_container.setLayout(container_layout)
        layout.addWidget(login_container)
        
        central_widget.setLayout(layout)
        
        # Set focus to username field
        QTimer.singleShot(100, self.username_input.setFocus)
    
    def create_left_panel(self):
        """Create the left panel with university branding"""
        panel = QFrame()
        panel.setFixedWidth(400)
        panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #3498db, stop: 1 #2980b9);
                border-top-left-radius: 20px;
                border-bottom-left-radius: 20px;
                border-right: 2px solid rgba(255, 255, 255, 0.1);
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 60, 40, 60)
        layout.setSpacing(30)
        layout.setAlignment(Qt.AlignCenter)
        
        # University Logo
        logo_label = QLabel()
        self.load_university_logo(logo_label)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("margin-bottom: 20px;")
        layout.addWidget(logo_label)
        
        # Welcome message
        welcome_title = QLabel("Welcome to")
        welcome_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                text-align: center;
            }
        """)
        welcome_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome_title)
        
        # System name
        system_name = QLabel("ID Card System")
        system_name.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 32px;
                font-weight: bold;
                text-align: center;
            }
        """)
        system_name.setAlignment(Qt.AlignCenter)
        layout.addWidget(system_name)
        
        # Department name
        dept_label = QLabel(DEPARTMENT_NAME)
        dept_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 16px;
                text-align: center;
                margin-top: 10px;
            }
        """)
        dept_label.setAlignment(Qt.AlignCenter)
        dept_label.setWordWrap(True)
        layout.addWidget(dept_label)
        
        # Features list
        features_frame = QFrame()
        features_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 20px;
                margin-top: 30px;
            }
        """)
        
        features_layout = QVBoxLayout()
        features = [
            "🎯 Student ID Card Generation",
            "📊 Digital Management System",
            "🔒 Secure Authentication",
            "🖨️ Professional Printing",
            "📱 QR Code Integration"
        ]
        
        for feature in features:
            feature_label = QLabel(feature)
            feature_label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 14px;
                    padding: 5px;
                }
            """)
            features_layout.addWidget(feature_label)
        
        features_frame.setLayout(features_layout)
        layout.addWidget(features_frame)
        
        layout.addStretch()
        
        # Footer
        footer_label = QLabel("Secure • Efficient • Professional")
        footer_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.7);
                font-size: 12px;
                text-align: center;
                margin-top: 20px;
            }
        """)
        footer_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer_label)
        
        panel.setLayout(layout)
        return panel
    
    def create_right_panel(self):
        """Create the right panel with login form"""
        panel = QFrame()
        panel.setFixedWidth(400)
        panel.setStyleSheet("""
            QFrame {
                background: white;
                border-top-right-radius: 20px;
                border-bottom-right-radius: 20px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 80, 50, 60)
        layout.setSpacing(25)
        
        # Login title
        login_title = QLabel("Administrator Login")
        login_title.setStyleSheet("""
            QLabel {
                font-size: 25px;
                font-weight: bold;
                color: #2c3e50;
                text-align: center;
                margin-bottom: 10px;
            }
        """)
        login_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(login_title)
        
        # Login subtitle
        login_subtitle = QLabel("Access the ID Card Management System")
        login_subtitle.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #7f8c8d;
                text-align: center;
                margin-bottom: 30px;
            }
        """)
        login_subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(login_subtitle)
        
        # Username field
        username_layout = QVBoxLayout()
        username_label = QLabel("Username")
        username_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 2px;
            }
        """)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setFixedHeight(65)
        self.username_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                padding: 0 15px;
                font-size: 14px;
                background: white;
                margin-bottom: 30px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background: #f8f9fa;
            }
        """)
        
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)
        
        # Password field
        password_layout = QVBoxLayout()
        password_label = QLabel("Password")
        password_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                margin-top: -20px;
            }
        """)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(65)
        self.password_input.setStyleSheet(self.username_input.styleSheet())
        
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)
        
        # Login button
        self.login_btn = QPushButton("Login to Dashboard")
        self.login_btn.setFixedHeight(55)
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #3498db, stop: 1 #2980b9);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #2980b9, stop: 1 #2471a3);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #2471a3, stop: 1 #1b4f72);
            }
        """)
        self.login_btn.clicked.connect(self.handle_login)
        layout.addWidget(self.login_btn)
        
        # Demo credentials
        # demo_label = QLabel("Demo Credentials: admin / admin123")
        # demo_label.setStyleSheet("""
        #     QLabel {
        #         color: #95a5a6;
        #         font-size: 12px;
        #         text-align: center;
        #         margin-top: 15px;
        #         padding: 10px;
        #         background: #f8f9fa;
        #         border-radius: 5px;
        #     }
        # """)
        # demo_label.setAlignment(Qt.AlignCenter)
        # layout.addWidget(demo_label)
        
        # Forgot password
        forgot_label = QLabel("<a href='#' style='color: #3498db; text-decoration: none;'>Forgot Password?</a>")
        forgot_label.setAlignment(Qt.AlignCenter)
        forgot_label.setStyleSheet("font-size: 12px; margin-top: 10px;")
        forgot_label.setOpenExternalLinks(False)
        # forgot_label.linkActivated.connect(self.show_forgot_password)  # Implement if needed
        layout.addWidget(forgot_label)
        
        layout.addStretch()
        
        # Footer
        footer_label = QLabel("© 2025 University ID System. All rights reserved.")
        footer_label.setStyleSheet("""
            QLabel {
                color: #bdc3c7;
                font-size: 10px;
                text-align: center;
                margin-top: 20px;
            }
        """)
        footer_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer_label)
        
        panel.setLayout(layout)
        return panel
    
    def load_university_logo(self, logo_label):
        """Load university logo for left panel"""
        logo_paths = [
            "assets/university_logo.jpeg",
            "assets/university_logo.jpg",
            "assets/logo.jpeg",
            "assets/logo.jpg",
            "university_logo.jpeg",
            "university_logo.jpg"
        ]
        
        logo_loaded = False
        for logo_path in logo_paths:
            if os.path.exists(logo_path):
                try:
                    pixmap = QPixmap(logo_path)
                    if not pixmap.isNull():
                        # Scale logo for display
                        scaled_pixmap = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        logo_label.setPixmap(scaled_pixmap)
                        logo_loaded = True
                        break
                except Exception as e:
                    print(f"Error loading logo: {e}")
        
        if not logo_loaded:
            # Fallback to icon
            logo_label.setText("🎓")
            logo_label.setStyleSheet("""
                QLabel {
                    font-size: 64px;
                    margin: 20px;
                }
            """)
    
    def center_window(self):
        """Center the window on screen"""
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())
    
    def handle_login(self):
        """Handle login attempt"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            self.shake_window()
            QMessageBox.warning(self, "Login Error", "Please enter both username and password")
            return
        
        # Disable login button during attempt
        self.login_btn.setEnabled(False)
        self.login_btn.setText("Authenticating...")
        
        # Simulate network delay for better UX
        QApplication.processEvents()
        
        user_data = authenticate_user(username, password)
        
        if user_data:
            self.login_success()
        else:
            self.login_failed()
        
        # Re-enable login button
        self.login_btn.setEnabled(True)
        self.login_btn.setText("🚀 Login to Dashboard")
    
    def login_success(self):
        """Handle successful login"""
        from admin_dashboard import AdminDashboard
        self.dashboard = AdminDashboard({'username': self.username_input.text(), 'full_name': 'Administrator'})
        self.dashboard.show()
        self.close()
    
    def login_failed(self):
        """Handle failed login"""
        self.shake_window()
        QMessageBox.critical(self, "Login Failed", 
                           "Invalid username or password.\n\n"
                           "Please check your credentials and try again.")
        self.password_input.clear()
        self.password_input.setFocus()
    
    def shake_window(self):
        """Add shake animation for invalid login"""
        animation = QPropertyAnimation(self, b"geometry")
        animation.setDuration(100)
        animation.setLoopCount(2)
        animation.setEasingCurve(QEasingCurve.OutInBounce)
        
        original_geometry = self.geometry()
        animation.setStartValue(QRect(original_geometry.x() - 10, original_geometry.y(), 
                                    original_geometry.width(), original_geometry.height()))
        animation.setEndValue(original_geometry)
        
        animation.start()
    
    def keyPressEvent(self, event):
        """Handle Enter key for login"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.handle_login()
        else:
            super().keyPressEvent(event)