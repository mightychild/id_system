from PyQt5.QtWidgets import QSplashScreen, QApplication, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont, QMovie
import sys
import os

class LoadingScreen(QSplashScreen):
    def __init__(self):
        # Create a simple splash screen with university logo
        pixmap = QPixmap(600, 400)
        pixmap.fill(Qt.white)
        
        super().__init__(pixmap)
        
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setEnabled(False)
        
        # Center on screen
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.move(screen_geometry.center() - self.rect().center())
        
        self.init_ui()
        
    def init_ui(self):
        # Main layout
        main_widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        # University Logo
        self.logo_label = QLabel()
        self.load_university_logo()
        self.logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo_label)
        
        # Loading text
        loading_label = QLabel("Starting ID Card System")
        loading_label.setAlignment(Qt.AlignCenter)
        loading_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                margin: 10px;
            }
        """)
        layout.addWidget(loading_label)
        
        # Progress text
        self.status_label = QLabel("Initializing database...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #7f8c8d;
                margin: 5px;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Loading animation (simple dots)
        self.animation_label = QLabel("●")
        self.animation_label.setAlignment(Qt.AlignCenter)
        self.animation_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #3498db;
                margin: 10px;
            }
        """)
        layout.addWidget(self.animation_label)
        
        # Version info
        version_label = QLabel("Version 2.0 • Professional Edition")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #95a5a6;
                margin-top: 20px;
            }
        """)
        layout.addWidget(version_label)
        
        main_widget.setLayout(layout)
        self.setWidget(main_widget)
        
        # Start animation
        self.animation_counter = 0
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_loading)
        self.animation_timer.start(500)  # Update every 500ms

        
    def load_university_logo(self):
        """Load university logo with fallback"""
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
                        # Scale logo to appropriate size
                        scaled_pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.logo_label.setPixmap(scaled_pixmap)
                        logo_loaded = True
                        break
                except Exception as e:
                    print(f"Error loading logo: {e}")
        
        if not logo_loaded:
            # Create a text-based logo fallback
            self.logo_label.setText("🎓 UNIVERSITY")
            self.logo_label.setStyleSheet("""
                QLabel {
                    font-size: 32px;
                    font-weight: bold;
                    color: #3498db;
                    margin: 20px;
                }
            """)
    
    def animate_loading(self):
        """Animate loading dots"""
        dots = ["●", "●●", "●●●", "●●●●"]
        self.animation_label.setText(dots[self.animation_counter])
        self.animation_counter = (self.animation_counter + 1) % len(dots)
    
    def update_status(self, message):
        """Update the status message"""
        self.status_label.setText(message)
        QApplication.processEvents()  # Force UI update
    
    def finish_loading(self, main_window):
        """Finish loading and show main window"""
        self.animation_timer.stop()
        self.finish(main_window)

class StartupManager:
    def __init__(self):
        self.splash = LoadingScreen()
        self.splash.show()
        
        # Simulate startup process
        QTimer.singleShot(100, self.initialize_system)
    
    def initialize_system(self):
        """Initialize system components with progress updates"""
        try:
            self.splash.update_status("Loading database...")
            QApplication.processEvents()
            
            # Initialize database
            from database import init_db
            init_db()
            
            self.splash.update_status("Loading configuration...")
            QApplication.processEvents()
            
            # Import other modules
            from config import DEPARTMENT_NAME
            
            self.splash.update_status("Starting application...")
            QApplication.processEvents()
            
            # Small delay to show completion
            QTimer.singleShot(500, self.show_login)
            
        except Exception as e:
            self.splash.update_status(f"Error: {str(e)}")
            QTimer.singleShot(2000, self.quit_app)
    
    def show_login(self):
        """Show login window"""
        from login_window import LoginWindow
        self.login_window = LoginWindow()
        self.splash.finish_loading(self.login_window)
        self.login_window.show()
    
    def quit_app(self):
        """Quit application on error"""
        QApplication.quit()