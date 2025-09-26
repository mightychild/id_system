from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QLineEdit, QDialog,
                             QFrame, QScrollArea, QProgressBar, QProgressDialog,
                             QTabWidget, QTextEdit, QFileDialog, QSplitter, QApplication)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPalette, QColor
import os
import logging
from datetime import datetime

from database import get_all_students, get_student_count, add_student, delete_student
from id_card_generator import generate_student_id_card, batch_generate_id_cards
from id_card_gallery import IDCardGallery
from config import DEPARTMENT_NAME, GENERATED_CARDS_DIR

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class IDGenerationThread(QThread):
    """Thread for background ID generation"""
    progress_signal = pyqtSignal(int, str)
    finished_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)

    def __init__(self, student_ids, batch_mode=False):
        super().__init__()
        self.student_ids = student_ids
        self.batch_mode = batch_mode

    def run(self):
        try:
            results = []
            total = len(self.student_ids)
            
            for i, student_id in enumerate(self.student_ids):
                output_path, message = generate_student_id_card(student_id)
                success = output_path is not None
                
                results.append({
                    'student_id': student_id,
                    'success': success,
                    'message': message,
                    'file_path': output_path
                })
                
                progress = int((i + 1) / total * 100)
                self.progress_signal.emit(progress, f"Processing {student_id}...")
            
            self.finished_signal.emit(results)
            
        except Exception as e:
            self.error_signal.emit(f"Generation error: {str(e)}")

class AdminDashboard(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.generation_thread = None
        self.current_students = []
        self.init_ui()
        self.setup_auto_refresh()
        
    def init_ui(self):
        self.setWindowTitle(f"ID Card System • {DEPARTMENT_NAME}")
        self.setGeometry(100, 100, 1400, 800)
        self.setMinimumSize(1200, 700)
        
        # Clean styling
        self.setStyleSheet("""
            QMainWindow {
                background: #f8f9fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background: white;
            }
            QTabBar::tab {
                background: #e9ecef;
                border: 1px solid #dee2e6;
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background: #3498db;
                color: white;
                border-bottom: 2px solid #2980b9;
            }
            QTabBar::tab:hover:!selected {
                background: #dae0e5;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Simplified Sidebar
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Main content with tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                margin-top: 10px;
            }
        """)
        
        # Create only essential tabs
        self.dashboard_tab = self.create_dashboard_tab()
        self.students_tab = self.create_students_tab()
        self.generator_tab = self.create_generator_tab()
        self.gallery_tab = self.create_gallery_tab()
        
        self.tab_widget.addTab(self.dashboard_tab, "📊 Dashboard")
        self.tab_widget.addTab(self.students_tab, "👥 Students")
        self.tab_widget.addTab(self.generator_tab, "🆔 ID Generator")
        self.tab_widget.addTab(self.gallery_tab, "🖼️ ID Gallery")
        
        main_layout.addWidget(self.tab_widget)
        central_widget.setLayout(main_layout)
        
        # Load initial data
        QTimer.singleShot(100, self.refresh_dashboard)
    
    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #2b5876, stop: 1 #4e4376);
                border-right: 2px solid #1e3c72;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setFixedHeight(150)
        header.setStyleSheet("""
            QFrame {
                background: rgba(0, 0, 0, 0.15);
                border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            }
        """)
        
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(20, 20, 20, 20)
        
        user_icon = QLabel("👨‍💼")
        user_icon.setStyleSheet("font-size: 40px; color: white;")
        user_icon.setAlignment(Qt.AlignCenter)
        
        user_name = QLabel(self.user_data['full_name'])
        user_name.setStyleSheet("""
            color: white; 
            font-size: 18px; 
            font-weight: bold; 
            text-align: center;
            margin: 5px 0px;
        """)
        user_name.setWordWrap(True)
        
        user_role = QLabel("Administrator")
        user_role.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9); 
            font-size: 12px; 
            text-align: center;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 4px 8px;
        """)
        
        header_layout.addWidget(user_icon)
        header_layout.addWidget(user_name)
        header_layout.addWidget(user_role)
        header.setLayout(header_layout)
        
        # Navigation - Only essential items
        nav_layout = QVBoxLayout()
        nav_layout.setContentsMargins(15, 20, 15, 20)
        nav_layout.setSpacing(8)
        
        menu_items = [
            ("📊 Dashboard", self.show_dashboard, "#3498db"),
            ("👥 Student Management", self.show_students, "#27ae60"),
            ("🆔 ID Card Generator", self.show_generator, "#e67e22"),
            ("🖼️ ID Card Gallery", self.show_gallery, "#9b59b6"),
        ]
        
        for text, callback, color in menu_items:
            btn = QPushButton(text)
            btn.setFixedHeight(50)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    text-align: left;
                    padding-left: 20px;
                    font-size: 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background: rgba(255, 255, 255, 0.15);
                    border-left: 4px solid {color};
                    padding-left: 16px;
                }}
            """)
            btn.clicked.connect(callback)
            nav_layout.addWidget(btn)
        
        nav_layout.addStretch()
        
        # Simple status
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background: rgba(0, 0, 0, 0.2);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        
        status_layout = QVBoxLayout()
        status_layout.setContentsMargins(15, 10, 15, 10)
        
        status_title = QLabel("System Status")
        status_title.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")
        
        status_online = QLabel("🟢 Online")
        status_online.setStyleSheet("color: #2ecc71; font-size: 11px;")
        
        students_count = QLabel(f"Students: {get_student_count()}")
        students_count.setStyleSheet("color: rgba(255, 255, 255, 0.9); font-size: 11px;")
        
        status_layout.addWidget(status_title)
        status_layout.addWidget(status_online)
        status_layout.addWidget(students_count)
        status_frame.setLayout(status_layout)
        
        # Logout button
        logout_btn = QPushButton("🚪 Logout System")
        logout_btn.setFixedHeight(45)
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet("""
            QPushButton {
                background: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                margin: 10px;
            }
            QPushButton:hover {
                background: #c0392b;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        
        layout.addWidget(header)
        layout.addLayout(nav_layout)
        layout.addWidget(status_frame)
        layout.addWidget(logout_btn)
        layout.addSpacing(10)
        
        sidebar.setLayout(layout)
        return sidebar

    def create_dashboard_tab(self):
        """Simplified dashboard without analytics or recent activity"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Header
        header_layout = QHBoxLayout()
        
        welcome_section = QVBoxLayout()
        welcome_title = QLabel("ID Card System Dashboard")
        welcome_title.setStyleSheet("font-size: 32px; font-weight: bold; color: #2c3e50;")
        
        welcome_sub = QLabel(f"Managing {DEPARTMENT_NAME}")
        welcome_sub.setStyleSheet("font-size: 16px; color: #7f8c8d;")
        
        welcome_section.addWidget(welcome_title)
        welcome_section.addWidget(welcome_sub)
        
        header_layout.addLayout(welcome_section)
        header_layout.addStretch()
        
        # Quick actions
        quick_actions = QHBoxLayout()
        quick_actions.setSpacing(10)
        
        actions = [
            ("🆔 Generate All", self.generate_all_ids, "#27ae60"),
            ("➕ Add Student", self.show_add_student_dialog, "#3498db"),
            ("📊 Refresh", self.refresh_dashboard, "#9b59b6"),
        ]
        
        for text, callback, color in actions:
            btn = QPushButton(text)
            btn.setFixedHeight(40)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {color};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    padding: 0 15px;
                }}
                QPushButton:hover {{
                    background: {self.darken_color(color)};
                }}
            """)
            btn.clicked.connect(callback)
            quick_actions.addWidget(btn)
        
        header_layout.addLayout(quick_actions)
        layout.addLayout(header_layout)
        
        # Stats cards (removed system uptime)
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(20)
        layout.addLayout(self.stats_layout)
        
        # Removed recent activity section entirely
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_students_tab(self):
        """Students management tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Student Management")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Search and actions
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search students by name, ID, or program...")
        self.search_input.setFixedHeight(45)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 0 15px;
                font-size: 14px;
                background: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        self.search_input.textChanged.connect(self.search_students)
        
        add_btn = QPushButton("➕ Add New Student")
        add_btn.setFixedHeight(45)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #219a52;
            }
        """)
        add_btn.clicked.connect(self.show_add_student_dialog)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        layout.addLayout(search_layout)
        
        # Students table
        self.students_table = QTableWidget()
        self.students_table.setColumnCount(6)
        self.students_table.setHorizontalHeaderLabels([
            "Student ID", "Full Name", "Program", "Email", "ID Generated", "Actions"
        ])
        
        # Enhanced table styling
        self.students_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background: #3498db;
                color: white;
                font-weight: bold;
                padding: 12px 8px;
                border: none;
                font-size: 12px;
            }
        """)
        
        header = self.students_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        self.students_table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                alternate-background-color: #f8f9fa;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
                font-size: 12px;
            }
            QTableWidget::item:selected {
                background: #3498db;
                color: white;
            }
        """)
        
        self.students_table.setAlternatingRowColors(True)
        self.students_table.setSortingEnabled(True)
        layout.addWidget(self.students_table)
        
        widget.setLayout(layout)
        return widget

    def create_generator_tab(self):
        """ID Card Generator tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        title = QLabel("ID Card Generator")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)
        
        # Generation options
        options_layout = QVBoxLayout()
        options_layout.setSpacing(15)
        
        # Single generation
        single_group = QFrame()
        single_group.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        
        single_layout = QVBoxLayout()
        single_title = QLabel("Generate Single ID Card")
        single_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        
        single_desc = QLabel("Select a student from the Students tab and click the ID button to generate their card individually.")
        single_desc.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        single_desc.setWordWrap(True)
        
        single_layout.addWidget(single_title)
        single_layout.addWidget(single_desc)
        single_group.setLayout(single_layout)
        
        # Batch generation
        batch_group = QFrame()
        batch_group.setStyleSheet(single_group.styleSheet())
        
        batch_layout = QVBoxLayout()
        batch_title = QLabel("🔄 Batch ID Card Generation")
        batch_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        
        batch_desc = QLabel("Generate ID cards for all students at once. This may take several minutes for large datasets.")
        batch_desc.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        batch_desc.setWordWrap(True)
        
        batch_btn = QPushButton("Generate All ID Cards")
        batch_btn.setFixedHeight(45)
        batch_btn.setCursor(Qt.PointingHandCursor)
        batch_btn.setStyleSheet("""
            QPushButton {
                background: #e67e22;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background: #d35400;
            }
        """)
        batch_btn.clicked.connect(self.generate_all_ids)
        
        self.batch_progress = QProgressBar()
        self.batch_progress.setVisible(False)
        
        batch_layout.addWidget(batch_title)
        batch_layout.addWidget(batch_desc)
        batch_layout.addWidget(batch_btn)
        batch_layout.addWidget(self.batch_progress)
        batch_group.setLayout(batch_layout)
        
        options_layout.addWidget(single_group)
        options_layout.addWidget(batch_group)
        options_layout.addStretch()
        
        widget.setLayout(options_layout)
        return widget

    def create_gallery_tab(self):
        """ID Card Gallery tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create and add gallery widget
        self.gallery_widget = IDCardGallery()
        layout.addWidget(self.gallery_widget)
        
        widget.setLayout(layout)
        return widget

    def update_stats_cards(self):
        """Update stats cards - removed system uptime"""
        # Clear existing cards
        for i in reversed(range(self.stats_layout.count())):
            item = self.stats_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
        
        total_students = get_student_count()
        
        # Only essential stats
        stats_data = [
            ("Total Students", total_students, "#3498db", "👥"),
            ("ID Cards Generated", total_students, "#27ae60", "🆔"),
            ("Pending Generation", 0, "#e67e22", "⏳"),
        ]
        
        for title, value, color, icon in stats_data:
            card = self.create_stat_card(title, value, color, icon)
            self.stats_layout.addWidget(card)

    def create_stat_card(self, title, value, color, icon):
        """Create stat card"""
        frame = QFrame()
        frame.setFixedHeight(120)
        frame.setMinimumWidth(200)
        frame.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                border-left: 4px solid {color};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Header
        header_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px;")
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #7f8c8d;")
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Value
        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {color};")
        
        layout.addLayout(header_layout)
        layout.addWidget(value_label)
        frame.setLayout(layout)
        
        return frame

    def refresh_dashboard(self):
        """Refresh dashboard - removed activity log"""
        try:
            # Update stats cards
            self.update_stats_cards()
            
            # Refresh students table if visible
            if self.tab_widget.currentIndex() == 1:  # Students tab
                self.load_students_data()
                
        except Exception as e:
            logging.error(f"Dashboard refresh error: {e}")

    def load_students_data(self):
        """Load students data into table"""
        try:
            self.current_students = get_all_students()
            self.students_table.setRowCount(len(self.current_students))
            
            for row, student in enumerate(self.current_students):
                # Student ID
                self.students_table.setItem(row, 0, QTableWidgetItem(student['student_id']))
                
                # Full Name
                self.students_table.setItem(row, 1, QTableWidgetItem(student['full_name']))
                
                # Program
                self.students_table.setItem(row, 2, QTableWidgetItem(student.get('program', 'N/A')))
                
                # Email
                self.students_table.setItem(row, 3, QTableWidgetItem(student.get('email', 'N/A')))
                
                # ID Generated
                status_item = QTableWidgetItem("Yes" if student.get('id_card_generated') else "No")
                self.students_table.setItem(row, 4, status_item)
                
                # Action buttons
                action_widget = self.create_action_buttons(student)
                self.students_table.setCellWidget(row, 5, action_widget)
                
        except Exception as e:
            logging.error(f"Error loading students data: {e}")
            QMessageBox.critical(self, "Database Error", f"Failed to load students: {str(e)}")

    def create_action_buttons(self, student):
        """Create action buttons for student row"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(3)
        
        # View ID Card button (only if generated)
        if student.get('id_card_generated'):
            view_card_btn = QPushButton("👁️")
            view_card_btn.setFixedSize(28, 28)
            view_card_btn.setCursor(Qt.PointingHandCursor)
            view_card_btn.setToolTip("View ID Card")
            view_card_btn.setStyleSheet("""
                QPushButton {
                    background: #9b59b6;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background: #8e44ad;
                }
            """)
            view_card_btn.clicked.connect(lambda: self.view_id_card(student))
            layout.addWidget(view_card_btn)
        
        # Generate ID button
        gen_btn = QPushButton("🆔")
        gen_btn.setFixedSize(28, 28)
        gen_btn.setCursor(Qt.PointingHandCursor)
        gen_btn.setToolTip("Generate ID Card")
        gen_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 10px;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        gen_btn.clicked.connect(lambda: self.generate_single_id_for_student(student))
        
        # View Student button
        view_btn = QPushButton("📋")
        view_btn.setFixedSize(28, 28)
        view_btn.setCursor(Qt.PointingHandCursor)
        view_btn.setToolTip("View Student Details")
        view_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 10px;
            }
            QPushButton:hover {
                background: #219a52;
            }
        """)
        view_btn.clicked.connect(lambda: self.view_student_details(student))
        
        # Delete button
        del_btn = QPushButton("🗑️")
        del_btn.setFixedSize(28, 28)
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setToolTip("Delete Student")
        del_btn.setStyleSheet("""
            QPushButton {
                background: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 10px;
            }
            QPushButton:hover {
                background: #c0392b;
            }
        """)
        del_btn.clicked.connect(lambda: self.delete_student(student['student_id']))
        
        # Add buttons in logical order
        if student.get('id_card_generated'):
            layout.addWidget(view_card_btn)
        layout.addWidget(gen_btn)
        layout.addWidget(view_btn)
        layout.addWidget(del_btn)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget

    def search_students(self):
        """Search students functionality"""
        search_text = self.search_input.text().lower()
        
        if not search_text:
            self.load_students_data()
            return
        
        filtered = [
            s for s in self.current_students 
            if (search_text in s['student_id'].lower() or 
                search_text in s['full_name'].lower() or 
                search_text in s.get('program', '').lower() or
                search_text in s.get('email', '').lower())
        ]
        
        self.students_table.setRowCount(len(filtered))
        for row, student in enumerate(filtered):
            self.students_table.setItem(row, 0, QTableWidgetItem(student['student_id']))
            self.students_table.setItem(row, 1, QTableWidgetItem(student['full_name']))
            self.students_table.setItem(row, 2, QTableWidgetItem(student.get('program', 'N/A')))
            self.students_table.setItem(row, 3, QTableWidgetItem(student.get('email', 'N/A')))
            
            status_item = QTableWidgetItem("Yes" if student.get('id_card_generated') else "No")
            self.students_table.setItem(row, 4, status_item)
            
            action_widget = self.create_action_buttons(student)
            self.students_table.setCellWidget(row, 5, action_widget)

    def generate_single_id_for_student(self, student):
        """Generate ID card for a single student"""
        try:
            output_path, message = generate_student_id_card(student['student_id'])
            
            if output_path:
                # Show success with file location
                reply = QMessageBox.information(
                    self, 
                    "ID Card Generated", 
                    f"Successfully generated ID card for {student['full_name']}!\n\n"
                    f"File saved to: {output_path}\n\n"
                    f"Would you like to open the containing folder?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    os.startfile(os.path.dirname(output_path))
                
                self.log_activity(f"Generated ID card for {student['student_id']}")
                self.refresh_dashboard()
            else:
                QMessageBox.critical(self, "Generation Failed", 
                                   f"Failed to generate ID card: {message}")
                
        except Exception as e:
            logging.error(f"ID generation error for {student['student_id']}: {e}")
            QMessageBox.critical(self, "Error", f"Generation failed: {str(e)}")

    def view_id_card(self, student):
        """View generated ID card for a student"""
        from database import get_student_id_card_path
        
        card_path = get_student_id_card_path(student['student_id'])
        
        if not card_path or not os.path.exists(card_path):
            QMessageBox.information(self, "No ID Card", 
                                  f"No ID card found for {student['full_name']}.\n"
                                  f"Please generate one first.")
            return
        
        # Create ID card viewer dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"ID Card - {student['full_name']}")
        dialog.setFixedSize(900, 650)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel(f"ID Card for {student['full_name']} ({student['student_id']})")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # ID Card Image
        image_label = QLabel()
        pixmap = QPixmap(card_path)
        scaled_pixmap = pixmap.scaled(800, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image_label.setPixmap(scaled_pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setStyleSheet("border: 2px solid #ddd; padding: 10px; background: white;")
        layout.addWidget(image_label)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        print_btn = QPushButton("🖨️ Print ID Card")
        print_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        print_btn.clicked.connect(lambda: self.print_id_card(card_path))
        
        open_btn = QPushButton("📁 Open Folder")
        open_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #219a52;
            }
        """)
        open_btn.clicked.connect(lambda: os.startfile(os.path.dirname(card_path)))
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #7f8c8d;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        
        button_layout.addWidget(print_btn)
        button_layout.addWidget(open_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.exec_()

    def print_id_card(self, card_path):
        """Print the ID card"""
        try:
            # For Windows
            os.startfile(card_path, "print")
            QMessageBox.information(self, "Print", "ID card sent to printer!")
        except Exception as e:
            QMessageBox.information(self, "Print", f"Open the file manually to print: {card_path}")

    def generate_all_ids(self):
        """Batch generate ID cards for all students"""
        try:
            students = get_all_students()
            if not students:
                QMessageBox.warning(self, "No Students", "No students found in database.")
                return
            
            reply = QMessageBox.question(
                self, 
                "Confirm Batch Generation",
                f"This will generate ID cards for all {len(students)} students.\n"
                "This may take several minutes. Continue?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Create progress dialog
                progress_dialog = QProgressDialog("Generating ID Cards...", "Cancel", 0, len(students), self)
                progress_dialog.setWindowTitle("Batch ID Generation")
                progress_dialog.setWindowModality(Qt.WindowModal)
                progress_dialog.show()
                
                # Generate IDs
                student_ids = [s['student_id'] for s in students]
                success_count = 0
                
                for i, student_id in enumerate(student_ids):
                    if progress_dialog.wasCanceled():
                        break
                        
                    output_path, message = generate_student_id_card(student_id)
                    if output_path:
                        success_count += 1
                    
                    progress_dialog.setValue(i + 1)
                    progress_dialog.setLabelText(f"Generating ID for {student_id}... ({i+1}/{len(students)})")
                    QApplication.processEvents()  # Keep UI responsive
                
                progress_dialog.close()
                
                # Show results
                QMessageBox.information(
                    self,
                    "Batch Generation Complete",
                    f"Successfully generated {success_count} out of {len(students)} ID cards.\n\n"
                    f"Files saved to: {GENERATED_CARDS_DIR}"
                )
                
                self.log_activity(f"Batch generated {success_count} ID cards")
                self.refresh_dashboard()
                
        except Exception as e:
            logging.error(f"Batch generation error: {e}")
            QMessageBox.critical(self, "Batch Error", f"Batch generation failed: {str(e)}")

    def show_add_student_dialog(self):
        """Show add student dialog"""
        from registration_form import StudentRegistrationDialog
        dialog = StudentRegistrationDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_dashboard()
            self.log_activity("Added new student")

    def view_student_details(self, student):
        """View student details dialog"""
        details = f"""
        <h3>Student Details</h3>
        <table style="width: 100%; border-collapse: collapse;">
            <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><b>Student ID:</b></td><td style="padding: 8px; border-bottom: 1px solid #eee;">{student['student_id']}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><b>Full Name:</b></td><td style="padding: 8px; border-bottom: 1px solid #eee;">{student['full_name']}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><b>Program:</b></td><td style="padding: 8px; border-bottom: 1px solid #eee;">{student.get('program', 'N/A')}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><b>Email:</b></td><td style="padding: 8px; border-bottom: 1px solid #eee;">{student.get('email', 'N/A')}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><b>ID Generated:</b></td><td style="padding: 8px; border-bottom: 1px solid #eee;">{'✅ Yes' if student.get('id_card_generated') else '❌ No'}</td></tr>
        </table>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Student Details")
        msg.setTextFormat(Qt.RichText)
        msg.setText(details)
        msg.exec_()

    def delete_student(self, student_id):
        """Delete student with confirmation"""
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion",
            f"Are you sure you want to delete student {student_id}?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if delete_student(student_id):
                    QMessageBox.information(self, "Success", "Student deleted successfully!")
                    self.log_activity(f"Deleted student {student_id}")
                    self.refresh_dashboard()
                else:
                    QMessageBox.critical(self, "Error", "Failed to delete student")
            except Exception as e:
                logging.error(f"Delete student error: {e}")
                QMessageBox.critical(self, "Error", f"Deletion failed: {str(e)}")

    def log_activity(self, message):
        """Log system activity"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        logging.info(log_entry)

    def setup_auto_refresh(self):
        """Setup automatic refresh timer"""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_dashboard)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds

    def darken_color(self, color):
        """Darken a hex color for hover effects"""
        darker_colors = {
            "#3498db": "#2980b9",
            "#27ae60": "#219a52",
            "#e67e22": "#d35400",
            "#9b59b6": "#8e44ad"
        }
        return darker_colors.get(color, color)

    def show_dashboard(self):
        self.tab_widget.setCurrentIndex(0)
        self.refresh_dashboard()

    def show_students(self):
        self.tab_widget.setCurrentIndex(1)
        self.load_students_data()

    def show_generator(self):
        self.tab_widget.setCurrentIndex(2)

    def show_gallery(self):
        """Show ID Card Gallery"""
        self.tab_widget.setCurrentIndex(3)
        if hasattr(self, 'gallery_widget'):
            self.gallery_widget.load_id_cards()

    def logout(self):
        reply = QMessageBox.question(
            self, 
            "Confirm Logout",
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            from login_window import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.show()
            self.close()

    def closeEvent(self, event):
        """Handle application close"""
        if self.generation_thread and self.generation_thread.isRunning():
            self.generation_thread.terminate()
            self.generation_thread.wait()
        
        logging.info("Admin dashboard closed")
        event.accept()