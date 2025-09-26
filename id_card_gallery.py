from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QFrame, QMessageBox,
                             QGridLayout, QDialog, QLineEdit, QComboBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon
import os
from datetime import datetime

from id_card_generator import get_all_generated_id_cards, generate_student_id_card
from database import get_all_students
from config import GENERATED_CARDS_DIR

class IDCardGallery(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.id_cards = []
        self.current_filter = "all"
        self.init_ui()
        self.load_id_cards()
        
    def init_ui(self):
        self.setMinimumSize(1000, 700)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("ID Card Gallery")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        filter_label = QLabel("Filter:")
        filter_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All ID Cards", "With Photos", "Without Photos"])
        self.filter_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                min-width: 150px;
            }
        """)
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        refresh_btn.clicked.connect(self.load_id_cards)
        
        generate_all_btn = QPushButton("🎨 Generate Missing IDs")
        generate_all_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #219a52;
            }
        """)
        generate_all_btn.clicked.connect(self.generate_missing_ids)
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addStretch()
        filter_layout.addWidget(refresh_btn)
        filter_layout.addWidget(generate_all_btn)
        
        # Stats
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: #7f8c8d; font-size: 14px;")
        
        layout.addLayout(header_layout)
        layout.addLayout(filter_layout)
        layout.addWidget(self.stats_label)
        
        # Scroll area for ID cards
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.cards_container = QWidget()
        self.cards_layout = QGridLayout()
        self.cards_layout.setSpacing(20)
        self.cards_layout.setAlignment(Qt.AlignTop)
        
        self.cards_container.setLayout(self.cards_layout)
        self.scroll_area.setWidget(self.cards_container)
        
        layout.addWidget(self.scroll_area)
        self.setLayout(layout)
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_id_cards)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def load_id_cards(self):
        """Load all generated ID cards"""
        self.id_cards = get_all_generated_id_cards()
        self.display_id_cards()
        self.update_stats()
    
    def display_id_cards(self):
        """Display ID cards in the gallery"""
        # Clear existing cards
        for i in reversed(range(self.cards_layout.count())):
            item = self.cards_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
        
        # Filter cards based on current selection
        filtered_cards = self.filter_cards(self.id_cards)
        
        # Display cards in grid
        row, col = 0, 0
        max_cols = 3  # 3 cards per row
        
        for card_data in filtered_cards:
            card_widget = self.create_id_card_widget(card_data)
            self.cards_layout.addWidget(card_widget, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Add stretch to push cards to top
        self.cards_layout.setRowStretch(row + 1, 1)
    
    def filter_cards(self, cards):
        """Filter cards based on current selection"""
        filter_text = self.filter_combo.currentText()
        
        if filter_text == "With Photos":
            return [card for card in cards if card['has_photo']]
        elif filter_text == "Without Photos":
            return [card for card in cards if not card['has_photo']]
        else:  # "All ID Cards"
            return cards
    
    def apply_filter(self):
        """Apply current filter to displayed cards"""
        self.display_id_cards()
        self.update_stats()
    
    def create_id_card_widget(self, card_data):
        """Create a widget for displaying an ID card"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 15px;
            }
            QFrame:hover {
                border: 2px solid #3498db;
                background: #f8f9fa;
            }
        """)
        frame.setFixedSize(300, 400)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignTop)
        
        # Student info
        name_label = QLabel(card_data['full_name'])
        name_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)
        
        id_label = QLabel(f"ID: {card_data['student_id']}")
        id_label.setStyleSheet("color: #7f8c8d; font-size: 14px;")
        id_label.setAlignment(Qt.AlignCenter)
        
        program_label = QLabel(card_data['program'])
        program_label.setStyleSheet("color: #95a5a6; font-size: 12px;")
        program_label.setAlignment(Qt.AlignCenter)
        program_label.setWordWrap(True)
        
        # ID Card preview
        preview_label = QLabel()
        preview_label.setAlignment(Qt.AlignCenter)
        preview_label.setFixedSize(250, 160)
        preview_label.setStyleSheet("""
            QLabel {
                background: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
            }
        """)
        
        # Load and scale ID card image for preview
        try:
            pixmap = QPixmap(card_data['id_card_path'])
            scaled_pixmap = pixmap.scaled(240, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            preview_label.setPixmap(scaled_pixmap)
            preview_label.setToolTip("Click to view full size")
        except Exception as e:
            preview_label.setText("Preview\nNot Available")
            preview_label.setStyleSheet("color: #95a5a6; font-size: 12px; background: #f8f9fa;")
        
        # Photo indicator
        photo_indicator = QLabel("📷 Has Photo" if card_data['has_photo'] else "❌ No Photo")
        photo_indicator.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        photo_indicator.setAlignment(Qt.AlignCenter)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        view_btn = QPushButton("👁️ View")
        view_btn.setFixedSize(70, 30)
        view_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        view_btn.clicked.connect(lambda: self.view_id_card(card_data))
        
        print_btn = QPushButton("🖨️ Print")
        print_btn.setFixedSize(70, 30)
        print_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #219a52;
            }
        """)
        print_btn.clicked.connect(lambda: self.print_id_card(card_data))
        
        regenerate_btn = QPushButton("🔄 Regenerate")
        regenerate_btn.setFixedSize(90, 30)
        regenerate_btn.setStyleSheet("""
            QPushButton {
                background: #e67e22;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #d35400;
            }
        """)
        regenerate_btn.clicked.connect(lambda: self.regenerate_id_card(card_data))
        
        button_layout.addWidget(view_btn)
        button_layout.addWidget(print_btn)
        button_layout.addWidget(regenerate_btn)
        
        layout.addWidget(name_label)
        layout.addWidget(id_label)
        layout.addWidget(program_label)
        layout.addWidget(preview_label)
        layout.addWidget(photo_indicator)
        layout.addLayout(button_layout)
        
        frame.setLayout(layout)
        return frame
    
    def view_id_card(self, card_data):
        """View ID card in full size"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout
        from PyQt5.QtGui import QPixmap
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"ID Card - {card_data['full_name']}")
        dialog.setFixedSize(900, 650)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel(f"ID Card for {card_data['full_name']} ({card_data['student_id']})")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # ID Card Image
        image_label = QLabel()
        pixmap = QPixmap(card_data['id_card_path'])
        scaled_pixmap = pixmap.scaled(800, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image_label.setPixmap(scaled_pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setStyleSheet("border: 2px solid #ddd; padding: 10px; background: white;")
        layout.addWidget(image_label)
        
        # Info
        info_label = QLabel(
            f"Generated: {card_data['generated_date']} | "
            f"Has Photo: {'Yes' if card_data['has_photo'] else 'No'}"
        )
        info_label.setStyleSheet("color: #7f8c8d; margin: 10px;")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def print_id_card(self, card_data):
        """Print the ID card"""
        try:
            # For Windows
            os.startfile(card_data['id_card_path'], "print")
            QMessageBox.information(self, "Print", f"ID card for {card_data['full_name']} sent to printer!")
        except Exception as e:
            QMessageBox.information(self, "Print", 
                                  f"Open the file manually to print:\n{card_data['id_card_path']}")
    
    def regenerate_id_card(self, card_data):
        """Regenerate ID card for a student"""
        reply = QMessageBox.question(
            self, 
            "Regenerate ID Card",
            f"Regenerate ID card for {card_data['full_name']}?\n\n"
            "This will overwrite the existing ID card.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            output_path, message = generate_student_id_card(card_data['student_id'])
            if output_path:
                QMessageBox.information(self, "Success", 
                                      f"✅ ID card regenerated for {card_data['full_name']}!")
                self.load_id_cards()
            else:
                QMessageBox.critical(self, "Error", 
                                   f"Failed to regenerate ID card: {message}")
    
    def generate_missing_ids(self):
        """Generate ID cards for students who don't have them"""
        students = get_all_students()
        missing_ids = [s for s in students if not s.get('id_card_generated')]
        
        if not missing_ids:
            QMessageBox.information(self, "No Missing IDs", 
                                  "All students already have ID cards generated!")
            return
        
        reply = QMessageBox.question(
            self,
            "Generate Missing IDs",
            f"Generate ID cards for {len(missing_ids)} students without IDs?\n\n"
            "This may take several minutes.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success_count = 0
            for student in missing_ids:
                output_path, message = generate_student_id_card(student['student_id'])
                if output_path:
                    success_count += 1
            
            QMessageBox.information(
                self,
                "Generation Complete",
                f"✅ Generated {success_count} out of {len(missing_ids)} missing ID cards!"
            )
            self.load_id_cards()
    
    def update_stats(self):
        """Update statistics label"""
        total = len(self.id_cards)
        with_photos = len([c for c in self.id_cards if c['has_photo']])
        without_photos = total - with_photos
        
        self.stats_label.setText(
            f"Showing {len(self.filter_cards(self.id_cards))} ID cards | "
            f"Total: {total} | With Photos: {with_photos} | Without Photos: {without_photos}"
        )