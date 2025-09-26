from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QComboBox,
                             QFormLayout, QGroupBox, QFileDialog, QDateEdit,
                             QTextEdit, QScrollArea, QWidget, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QPixmap, QImage
import os
import shutil

from config import STUDENT_PHOTOS_DIR
from database import add_student, update_student, get_student_by_id

class StudentRegistrationDialog(QDialog):
    def __init__(self, parent=None, student_id=None):
        super().__init__(parent)
        self.student_id = student_id  # None for new student, ID for editing
        self.photo_path = None
        self.init_ui()
        
        if student_id:
            self.load_student_data()
    
    def init_ui(self):
        title = "Edit Student" if self.student_id else "Register New Student"
        self.setWindowTitle(title)
        self.setMinimumSize(500, 400)
        self.resize(700, 600)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; padding: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Scroll content widget
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.setSpacing(15)
        scroll_layout.setContentsMargins(15, 15, 15, 15)
        
        # Personal Information Section
        personal_group = self.create_personal_info_section()
        scroll_layout.addWidget(personal_group)
        
        # Academic Information Section
        academic_group = self.create_academic_info_section()
        scroll_layout.addWidget(academic_group)
        
        # Photo Section
        photo_group = self.create_photo_section()
        scroll_layout.addWidget(photo_group)
        
        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        
        # Make scroll area expandable
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(scroll_area)
        
        # Fixed buttons section at bottom (always visible)
        buttons_group = self.create_buttons_section()
        main_layout.addWidget(buttons_group)
        
        self.setLayout(main_layout)
        
        # Style
        self.setStyleSheet("""
            QDialog {
                background: #f8f9fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: #2c3e50;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
    
    def create_personal_info_section(self):
        group = QGroupBox("Personal Information")
        layout = QFormLayout()
        layout.setLabelAlignment(Qt.AlignRight)
        layout.setSpacing(8)
        layout.setContentsMargins(15, 20, 15, 15)
        
        # Student ID
        self.student_id_input = QLineEdit()
        self.student_id_input.setPlaceholderText("e.g., SE2024001")
        self.student_id_input.setMinimumHeight(35)
        if self.student_id:
            self.student_id_input.setText(self.student_id)
            self.student_id_input.setEnabled(False)
        
        # Full Name
        self.full_name_input = QLineEdit()
        self.full_name_input.setPlaceholderText("Enter full name")
        self.full_name_input.setMinimumHeight(35)
        
        # Date of Birth
        self.dob_input = QDateEdit()
        self.dob_input.setDate(QDate(2000, 1, 1))
        self.dob_input.setCalendarPopup(True)
        self.dob_input.setMinimumHeight(35)
        
        # Gender
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Male", "Female", "Other"])
        self.gender_input.setMinimumHeight(35)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("student@university.edu")
        self.email_input.setMinimumHeight(35)
        
        # Phone
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("+1234567890")
        self.phone_input.setMinimumHeight(35)
        
        layout.addRow("Student ID:*", self.student_id_input)
        layout.addRow("Full Name:*", self.full_name_input)
        layout.addRow("Date of Birth:", self.dob_input)
        layout.addRow("Gender:", self.gender_input)
        layout.addRow("Email:*", self.email_input)
        layout.addRow("Phone:", self.phone_input)
        
        group.setLayout(layout)
        return group
    
    def create_academic_info_section(self):
        group = QGroupBox("Academic Information")
        layout = QFormLayout()
        layout.setLabelAlignment(Qt.AlignRight)
        layout.setSpacing(8)
        layout.setContentsMargins(15, 20, 15, 15)
        
        # Department (fixed for Software Engineering)
        self.department_input = QComboBox()
        self.department_input.addItems(["Software Engineering"])
        self.department_input.setMinimumHeight(35)
        self.department_input.setEnabled(False)
        
        # Program
        self.program_input = QComboBox()
        self.program_input.addItems([
            "BSc Software Engineering",
            "MSc Software Engineering", 
            "PhD Software Engineering",
            "Software Engineering Diploma"
        ])
        self.program_input.setMinimumHeight(35)
        
        # Enrollment Date
        self.enrollment_input = QDateEdit()
        self.enrollment_input.setDate(QDate.currentDate())
        self.enrollment_input.setCalendarPopup(True)
        self.enrollment_input.setMinimumHeight(35)
        
        # Expected Graduation
        self.graduation_input = QDateEdit()
        future_date = QDate.currentDate().addYears(4)
        self.graduation_input.setDate(future_date)
        self.graduation_input.setCalendarPopup(True)
        self.graduation_input.setMinimumHeight(35)
        
        layout.addRow("Department:*", self.department_input)
        layout.addRow("Program:*", self.program_input)
        layout.addRow("Enrollment Date:*", self.enrollment_input)
        layout.addRow("Expected Graduation:", self.graduation_input)
        
        group.setLayout(layout)
        return group
    
    def create_photo_section(self):
        group = QGroupBox("Student Photo")
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 20, 15, 15)
        
        # Photo preview
        self.photo_label = QLabel()
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.photo_label.setMinimumHeight(150)
        self.photo_label.setMaximumHeight(200)
        self.photo_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 2px dashed #dee2e6;
                border-radius: 10px;
                color: #6c757d;
                padding: 10px;
            }
        """)
        self.photo_label.setText("No photo selected\n\nClick 'Browse Photo' to upload")
        
        # Photo buttons
        buttons_layout = QHBoxLayout()
        
        browse_btn = QPushButton("📷 Browse Photo")
        browse_btn.setMinimumHeight(35)
        browse_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        browse_btn.clicked.connect(self.browse_photo)
        
        clear_btn = QPushButton("🗑️ Clear Photo")
        clear_btn.setMinimumHeight(35)
        clear_btn.setStyleSheet("""
            QPushButton {
                background: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #c0392b;
            }
        """)
        clear_btn.clicked.connect(self.clear_photo)
        
        buttons_layout.addWidget(browse_btn)
        buttons_layout.addWidget(clear_btn)
        buttons_layout.addStretch()
        
        # Photo requirements
        requirements = QLabel(
            "📋 Photo Requirements:\n"
            "• Recent passport-sized photo (2x2 inches)\n"
            "• Clear front view of face\n" 
            "• Plain background\n"
            "• Formal attire preferred"
        )
        requirements.setStyleSheet("color: #6c757d; font-size: 11px; padding: 10px; background: #f1f2f6; border-radius: 5px;")
        
        layout.addWidget(self.photo_label)
        layout.addLayout(buttons_layout)
        layout.addWidget(requirements)
        
        group.setLayout(layout)
        return group
    
    def create_buttons_section(self):
        button_frame = QFrame()
        button_frame.setFixedHeight(70)
        button_frame.setStyleSheet("background: #2c3e50; border-radius: 8px;")
        
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Cancel button
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setFixedSize(120, 40)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #7f8c8d;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        # Save button
        save_text = "💾 Update Student" if self.student_id else "✅ Register Student"
        self.save_btn = QPushButton(save_text)
        self.save_btn.setFixedSize(150, 45)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #219a52;
            }
        """)
        self.save_btn.clicked.connect(self.save_student)
        
        layout.addStretch()
        layout.addWidget(cancel_btn)
        layout.addWidget(self.save_btn)
        
        button_frame.setLayout(layout)
        return button_frame
    
    def browse_photo(self):
        """Browse and validate photo"""
        print("DEBUG: Browse photo button clicked")
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Student Photo", "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)"
        )
        
        if file_path:
            print(f"DEBUG: File selected: {file_path}")
            print(f"DEBUG: File exists: {os.path.exists(file_path)}")
            
            try:
                # Validate the image
                try:
                    from PIL import Image
                    img = Image.open(file_path)
                    img.verify()
                    img = Image.open(file_path)  # Reopen for processing
                    print(f"DEBUG: Image validated - Size: {img.size}, Mode: {img.mode}")
                    
                except ImportError:
                    print("DEBUG: PIL not available, using basic validation")
                except Exception as img_error:
                    QMessageBox.warning(self, "Invalid Image", 
                                      "The selected file is not a valid image.\n\n"
                                      "Please select a valid JPG, PNG, or other image file.")
                    print(f"DEBUG: Image validation failed: {img_error}")
                    return
                
                # Load and display preview
                pixmap = QPixmap(file_path)
                if pixmap.isNull():
                    QMessageBox.warning(self, "Invalid Image", "The selected file is not a valid image.")
                    print("DEBUG: QPixmap failed to load image")
                    return
                
                # Scale image for preview
                scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.photo_label.setPixmap(scaled_pixmap)
                self.photo_path = file_path  # Store the path
                
                print(f"DEBUG: Photo preview set successfully. Photo path stored: {self.photo_path}")
                print(f"DEBUG: Photo path variable type: {type(self.photo_path)}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
                print(f"DEBUG: Exception in browse_photo: {e}")
        else:
            print("DEBUG: No file selected")
    
    def clear_photo(self):
        """Clear the selected photo"""
        print("DEBUG: Clearing photo")
        self.photo_label.clear()
        self.photo_label.setText("No photo selected\n\nClick 'Browse Photo' to upload")
        self.photo_path = None
        print("DEBUG: Photo cleared")
    
    def load_student_data(self):
        """Load existing student data for editing"""
        student = get_student_by_id(self.student_id)
        if not student:
            QMessageBox.critical(self, "Error", "Student not found!")
            self.reject()
            return
        
        # Fill form with existing data
        self.full_name_input.setText(student.get('full_name', ''))
        self.email_input.setText(student.get('email', ''))
        self.phone_input.setText(student.get('phone', ''))
        
        # Set dates
        if student.get('date_of_birth'):
            dob = QDate.fromString(student['date_of_birth'], 'yyyy-MM-dd')
            self.dob_input.setDate(dob)
        
        if student.get('enrollment_date'):
            enrollment = QDate.fromString(student['enrollment_date'], 'yyyy-MM-dd')
            self.enrollment_input.setDate(enrollment)
        
        if student.get('graduation_date'):
            graduation = QDate.fromString(student['graduation_date'], 'yyyy-MM-dd')
            self.graduation_input.setDate(graduation)
        
        # Set gender and program
        gender = student.get('gender', '')
        if gender in ["Male", "Female", "Other"]:
            self.gender_input.setCurrentText(gender)
        
        program = student.get('program', '')
        if program:
            index = self.program_input.findText(program)
            if index >= 0:
                self.program_input.setCurrentIndex(index)
        
        # Load photo if exists
        photo_path = student.get('photo_path')
        if photo_path:
            # Handle both original and safe filenames
            if '/' in self.student_id and '/' in photo_path:
                # Convert to safe filename for lookup
                safe_student_id = self.student_id.replace('/', '_')
                photo_path = photo_path.replace(self.student_id, safe_student_id)
            
            full_photo_path = os.path.join(STUDENT_PHOTOS_DIR, photo_path)
            if os.path.exists(full_photo_path):
                pixmap = QPixmap(full_photo_path)
                scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.photo_label.setPixmap(scaled_pixmap)
                self.photo_path = full_photo_path
                print(f"DEBUG: Loaded existing photo: {full_photo_path}")
            else:
                print(f"DEBUG: Photo path in database but file not found: {full_photo_path}")
    
    def validate_form(self):
        """Validate the form data"""
        required_fields = [
            (self.student_id_input.text().strip(), "Student ID"),
            (self.full_name_input.text().strip(), "Full Name"),
            (self.email_input.text().strip(), "Email Address"),
        ]
        
        for field_value, field_name in required_fields:
            if not field_value:
                QMessageBox.warning(self, "Validation Error", f"{field_name} is required.")
                return False
        
        # Validate email format
        email = self.email_input.text().strip()
        if "@" not in email or "." not in email:
            QMessageBox.warning(self, "Validation Error", "Please enter a valid email address.")
            return False
        
        # Validate student ID format for new students
        if not self.student_id:
            student_id = self.student_id_input.text().strip()
            if len(student_id) < 3:
                QMessageBox.warning(self, "Validation Error", "Student ID must be at least 3 characters long.")
                return False
        
        return True
    
    def save_student(self):
        """Save student data to database - FIXED PHOTO SAVING"""
        print("DEBUG: Save student button clicked")
        
        if not self.validate_form():
            return
        
        try:
            # Prepare student data
            student_data = {
                'student_id': self.student_id_input.text().strip(),
                'full_name': self.full_name_input.text().strip(),
                'department': self.department_input.currentText(),
                'program': self.program_input.currentText(),
                'email': self.email_input.text().strip(),
                'phone': self.phone_input.text().strip(),
                'date_of_birth': self.dob_input.date().toString("yyyy-MM-dd"),
                'gender': self.gender_input.currentText(),
                'enrollment_date': self.enrollment_input.date().toString("yyyy-MM-dd"),
                'graduation_date': self.graduation_input.date().toString("yyyy-MM-dd"),
            }
            
            print(f"DEBUG: Starting to save student {student_data['student_id']}")
            print(f"DEBUG: Photo path available: {self.photo_path is not None}")
            print(f"DEBUG: Photo path value: {self.photo_path}")
            
            # Handle photo - FIXED: Check if photo_path is set and file exists
            photo_saved = False
            if self.photo_path and os.path.exists(self.photo_path):
                print(f"DEBUG: Photo found at: {self.photo_path}")
                print(f"DEBUG: Photo file exists: {os.path.exists(self.photo_path)}")
                
                # Save the photo and get the filename
                photo_filename = self.save_student_photo(student_data['student_id'], self.photo_path)
                
                if photo_filename:
                    student_data['photo_path'] = photo_filename
                    photo_saved = True
                    print(f"DEBUG: Photo saved successfully as: {photo_filename}")
                else:
                    print("DEBUG: Failed to save photo")
                    student_data['photo_path'] = None
            else:
                print("DEBUG: No photo selected or photo file doesn't exist")
                if self.photo_path:
                    print(f"DEBUG: Photo path was set but file doesn't exist: {self.photo_path}")
                    print(f"DEBUG: File exists check: {os.path.exists(self.photo_path)}")
                student_data['photo_path'] = None
            
            # Save to database
            if self.student_id:
                # Update existing student
                success = update_student(self.student_id, student_data)
                action = "updated"
            else:
                # Add new student
                success = add_student(student_data)
                action = "registered"
            
            if success:
                # Show appropriate success message
                if photo_saved:
                    message = f"✅ Student {action} successfully!\n\nName: {student_data['full_name']}\nStudent ID: {student_data['student_id']}\nPhoto: ✅ Saved successfully"
                else:
                    message = f"✅ Student {action} successfully!\n\nName: {student_data['full_name']}\nStudent ID: {student_data['student_id']}\nPhoto: ⚠️ No photo saved"
                
                QMessageBox.information(self, "Success", message)
                print(f"DEBUG: Student {action} successfully")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", f"Failed to {action} student.")
                print(f"DEBUG: Failed to {action} student")
                
        except Exception as e:
            print(f"ERROR in save_student: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Database Error", f"Failed to save student: {str(e)}")
    
    def save_student_photo(self, student_id, source_photo_path):
        """Save student photo with proper error handling - FIXED SLASH ISSUE"""
        print(f"DEBUG: Attempting to save photo for {student_id}")
        print(f"DEBUG: Source path: {source_photo_path}")
        print(f"DEBUG: Source path exists: {os.path.exists(source_photo_path)}")
        
        try:
            # Validate source path
            if not source_photo_path or not os.path.exists(source_photo_path):
                print(f"ERROR: Source photo doesn't exist: {source_photo_path}")
                return None
            
            # Validate it's an image file using PIL if available
            try:
                from PIL import Image
                with Image.open(source_photo_path) as img:
                    img.verify()
                img = Image.open(source_photo_path)  # Reopen for processing
                print(f"DEBUG: Image validated - Size: {img.size}, Mode: {img.mode}")
                
            except ImportError:
                print("DEBUG: PIL not available, skipping advanced validation")
            except Exception as img_error:
                print(f"ERROR: Invalid image file: {img_error}")
                QMessageBox.warning(self, "Invalid Image", 
                                  "The selected file is not a valid image file.\n\n"
                                  "Please select a JPG, PNG, or other image file.")
                return None
            
            # Get file extension
            _, file_ext = os.path.splitext(source_photo_path)
            if not file_ext:
                file_ext = '.jpg'
            
            # Create safe filename by replacing invalid characters (FIX FOR SLASHES)
            safe_student_id = student_id.replace('/', '_').replace('\\', '_').replace(':', '_')
            filename = f"{safe_student_id}{file_ext.lower()}"
            dest_path = os.path.join(STUDENT_PHOTOS_DIR, filename)
            
            print(f"DEBUG: Safe student ID: {safe_student_id}")
            print(f"DEBUG: Destination path: {dest_path}")
            
            # Ensure directory exists
            os.makedirs(STUDENT_PHOTOS_DIR, exist_ok=True)
            print(f"DEBUG: Directory ensured: {STUDENT_PHOTOS_DIR}")
            print(f"DEBUG: STUDENT_PHOTOS_DIR exists: {os.path.exists(STUDENT_PHOTOS_DIR)}")
            
            # Copy the file
            try:
                shutil.copy2(source_photo_path, dest_path)
                print(f"DEBUG: File copied successfully from {source_photo_path} to {dest_path}")
                print(f"DEBUG: Destination file exists: {os.path.exists(dest_path)}")
                
                # Verify the copy worked
                if os.path.exists(dest_path):
                    print(f"DEBUG: Destination file size: {os.path.getsize(dest_path)} bytes")
                    
                    # Verify the copied file is readable
                    try:
                        if 'Image' in globals():  # If PIL is available
                            with Image.open(dest_path) as verify_img:
                                verify_img.verify()
                            print("DEBUG: Copied photo verified as valid image")
                        return filename
                    except Exception as verify_error:
                        print(f"ERROR: Copied photo is invalid: {verify_error}")
                        # Clean up the invalid file
                        if os.path.exists(dest_path):
                            os.remove(dest_path)
                        return None
                else:
                    print("ERROR: File copy failed - destination file doesn't exist")
                    return None
                    
            except Exception as copy_error:
                print(f"ERROR copying file: {copy_error}")
                print(f"DEBUG: Destination directory: {os.path.dirname(dest_path)}")
                print(f"DEBUG: Directory exists: {os.path.exists(os.path.dirname(dest_path))}")
                print(f"DEBUG: Directory writable: {os.access(os.path.dirname(dest_path), os.W_OK)}")
                return None
            
        except Exception as e:
            print(f"ERROR saving photo: {e}")
            import traceback
            traceback.print_exc()
            return None