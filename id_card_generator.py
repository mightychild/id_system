import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from database import get_student_by_id, mark_id_card_generated
from config import GENERATED_CARDS_DIR, STUDENT_PHOTOS_DIR, LOGO_PATHS

class IDCardGenerator:
    def __init__(self):
        # Standard ID card dimensions in portrait orientation
        self.card_width = 440   # ID Card width
        self.card_height = 935  # ID Card height
        self.photo_size = 140   # Photo size
        self.qr_size = 90       # QR code size
        self.logo_size = (50, 50)
        
    def generate_id_card(self, student_data, output_path):
        """Generate realistic ID card with front and back"""
        try:
            # Create front of the card
            front_card = self.generate_front_side(student_data)
            
            # Create back of the card
            back_card = self.generate_back_side(student_data)
            
            # Use the taller height between front and back
            final_height = max(front_card.height, back_card.height)
            
            # Resize both cards to have same height
            front_card_resized = front_card.resize((self.card_width, final_height), Image.LANCZOS)
            back_card_resized = back_card.resize((self.card_width, final_height), Image.LANCZOS)
            
            # Combine front and back into one image
            combined_width = self.card_width * 2 + 20
            combined_image = Image.new('RGB', (combined_width, final_height), color=(240, 240, 240))
            combined_image.paste(front_card_resized, (0, 0))
            combined_image.paste(back_card_resized, (self.card_width + 20, 0))
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save the combined card
            combined_image.save(output_path, 'PNG', quality=95)
            
            # Also save front only for printing
            front_only_path = output_path.replace('.png', '_front.png')
            front_card_resized.save(front_only_path, 'PNG', quality=95)
            
            
            # Mark as generated in database
            mark_id_card_generated(student_data['student_id'], output_path, 
                                 self.generate_qr_data(student_data))
            
            return True, output_path
            
        except Exception as e:
            print(f"Error generating ID card: {e}")
            import traceback
            traceback.print_exc()
            return False, str(e)
    
    def generate_front_side(self, student_data):
        """Generate the front side of the ID card in PORTRAIT orientation"""
        # Calculate dynamic height based on content
        content_height = self.calculate_front_height(student_data)
        card = Image.new('RGB', (self.card_width, content_height), color=(255, 255, 255))
        draw = ImageDraw.Draw(card)
        
        # Load fonts with sizes adjusted for new dimensions
        try:
            university_font = ImageFont.truetype("arialbd.ttf", 20)
            title_font = ImageFont.truetype("arialbd.ttf", 16)
            name_font = ImageFont.truetype("arialbd.ttf", 18)
            info_font = ImageFont.truetype("arial.ttf", 13)
            small_font = ImageFont.truetype("arial.ttf", 10)
        except:
            university_font = ImageFont.load_default()
            title_font = ImageFont.load_default()
            name_font = ImageFont.load_default()
            info_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Draw background
        self.draw_portrait_front_background(draw, content_height)
        
        # Add university logo
        self.draw_university_logo(card)
        
        # Add university header
        self.draw_portrait_university_header(draw, university_font, title_font)
        
        # Add student photo - FIXED PHOTO LOADING
        photo_loaded = self.draw_portrait_student_photo(card, student_data)
        
        # Add student information
        self.draw_portrait_student_info(draw, student_data, name_font, info_font)
        
        # Add footer
        self.draw_portrait_front_footer(draw, small_font, content_height)
        
        return card
    
    def calculate_front_height(self, student_data):
        """Calculate height based on content"""
        base_height = 500
        program = student_data.get('program', '')
        
        # Add extra height for long program names
        if len(program) > 25:
            base_height += 20
        if len(program) > 40:
            base_height += 20
            
        return min(base_height, 650)
    
    def generate_back_side(self, student_data):
        """Generate the back side in PORTRAIT orientation"""
        content_height = self.calculate_back_height()
        card = Image.new('RGB', (self.card_width, content_height), color=(255, 255, 255))
        draw = ImageDraw.Draw(card)
        
        try:
            title_font = ImageFont.truetype("arialbd.ttf", 16)
            content_font = ImageFont.truetype("arial.ttf", 11)
            small_font = ImageFont.truetype("arial.ttf", 9)
        except:
            title_font = ImageFont.load_default()
            content_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Draw back background
        self.draw_portrait_back_background(draw, content_height)
        
        # Add header
        draw.rectangle([0, 0, self.card_width, 45], fill=(41, 128, 185))
        draw.text((self.card_width//2, 22), "FEDERAL UNIVERSITY DUTSE", 
                 fill=(255, 255, 255), font=title_font, anchor="mm")
        
        # Add QR code
        qr_data = self.generate_qr_data(student_data)
        self.draw_portrait_qr_code(card, qr_data)
        
        # Add informational text
        self.draw_portrait_back_text(draw, content_font, student_data)
        
        # Add contact information
        self.draw_portrait_contact_info(draw, small_font, content_height)
        
        return card
    
    def calculate_back_height(self):
        """Calculate back side height"""
        return 550
    
    def draw_portrait_front_background(self, draw, height):
        """Draw background for portrait orientation"""
        # University color header
        draw.rectangle([0, 0, self.card_width, 75], fill=(41, 128, 185))
        
        # Subtle pattern
        for y in range(75, height, 4):
            shade = 245 if y % 8 == 0 else 250
            draw.line([(0, y), (self.card_width, y)], fill=(shade, shade, shade))
    
    def draw_university_logo(self, card):
        """Draw university logo"""
        try:
            logo_image = None
            for logo_path in LOGO_PATHS:
                if os.path.exists(logo_path):
                    try:
                        logo_image = Image.open(logo_path)
                        break
                    except Exception as e:
                        print(f"Error opening logo {logo_path}: {e}")
                        continue
            
            if logo_image:
                # Resize logo
                logo_image = logo_image.resize(self.logo_size, Image.LANCZOS)
                
                # Convert to RGB if needed
                if logo_image.mode != 'RGB':
                    logo_image = logo_image.convert('RGB')
                
                # Position logo at top left with margin
                logo_position = (15, 12)
                card.paste(logo_image, logo_position)
                return True
            else:
                self.draw_logo_placeholder(card)
                return False
                
        except Exception as e:
            print(f"Error loading university logo: {e}")
            self.draw_logo_placeholder(card)
            return False
    
    def draw_logo_placeholder(self, card):
        """Draw logo placeholder"""
        draw = ImageDraw.Draw(card)
        logo_x, logo_y = 15, 12
        logo_width, logo_height = self.logo_size
        
        # Draw logo background
        draw.rectangle([logo_x, logo_y, logo_x + logo_width, logo_y + logo_height], 
                      fill=(255, 255, 255), outline=(200, 200, 200), width=2)
        
        # Draw university initials
        try:
            font = ImageFont.truetype("arialbd.ttf", 14)
        except:
            font = ImageFont.load_default()
            
        draw.text((logo_x + logo_width//2, logo_y + logo_height//2), "FUD", 
                 fill=(41, 128, 185), font=font, anchor="mm")
    
    def draw_portrait_university_header(self, draw, university_font, title_font):
        """Draw university header for portrait orientation"""
        # University name - centered with logo consideration
        draw.text((self.card_width//2, 25), "FEDERAL UNIVERSITY DUTSE", 
                 fill=(255, 255, 255), font=university_font, anchor="mm")
        
        # Department name
        from config import DEPARTMENT_NAME
        # Truncate if too long for portrait width
        dept_name = DEPARTMENT_NAME
        if len(dept_name) > 20:
            dept_name = dept_name[:20] + "..."
        draw.text((self.card_width//2, 48), dept_name, 
                 fill=(255, 255, 255), font=title_font, anchor="mm")
        
        # Card title
        draw.text((self.card_width//2, 70), "STUDENT ID CARD", 
                 fill=(255, 255, 255), font=title_font, anchor="mm")
    
    def draw_portrait_student_photo(self, card, student_data):
        """Draw student photo for portrait orientation - FIXED PHOTO LOADING"""
        # Center the photo horizontally
        photo_x = (self.card_width - self.photo_size) // 2
        photo_y = 95  # Position below header
        
        draw = ImageDraw.Draw(card)
        
        # Photo frame
        draw.rounded_rectangle([photo_x, photo_y, photo_x+self.photo_size, photo_y+self.photo_size], 
                             radius=8, outline=(80, 80, 80), width=2, fill=(250, 250, 250))
        
        # Try to load actual student photo 
        photo_path = student_data.get('photo_path')
        if photo_path:
            # Handle both original and safe filenames
            if '/' in student_data['student_id'] and '/' in photo_path:
                safe_student_id = student_data['student_id'].replace('/', '_')
                photo_path = photo_path.replace(student_data['student_id'], safe_student_id)
            
            full_photo_path = os.path.join(STUDENT_PHOTOS_DIR, photo_path)
            print(f"DEBUG: Looking for student photo at: {full_photo_path}")
            print(f"DEBUG: Photo exists: {os.path.exists(full_photo_path)}")
            
            if os.path.exists(full_photo_path):
                try:
                    photo = Image.open(full_photo_path)
                    print(f"DEBUG: Photo loaded: {photo.size}, mode: {photo.mode}")
                    
                    if photo.mode in ('RGBA', 'LA', 'P'):
                        photo = photo.convert('RGB')
                        print("DEBUG: Converted photo to RGB")
                    
                    # Resize photo to fit the frame
                    photo = photo.resize((self.photo_size-6, self.photo_size-6), Image.LANCZOS)
                    
                    # Paste the photo onto the card
                    card.paste(photo, (photo_x+3, photo_y+3))
                    print("DEBUG: Student photo added successfully")
                    return True
                    
                except Exception as e:
                    print(f"DEBUG: Error loading student photo: {e}")
                    # Fall through to placeholder if photo loading fails
        
        # If no photo or error loading, add placeholder text
        print("DEBUG: Using photo placeholder")
        self.draw_portrait_photo_placeholder(draw, photo_x, photo_y)
        return False
    
    def draw_portrait_photo_placeholder(self, draw, x, y):
        """Draw photo placeholder for portrait"""
        center_x = x + self.photo_size // 2
        center_y = y + self.photo_size // 2
        
        draw.text((center_x, center_y - 8), "STUDENT", 
                 fill=(150, 150, 150), font=ImageFont.load_default(), anchor="mm")
        draw.text((center_x, center_y + 8), "PHOTO", 
                 fill=(150, 150, 150), font=ImageFont.load_default(), anchor="mm")
    
    def draw_portrait_student_info(self, draw, student_data, name_font, info_font):
        """Draw student information filling 90% of portrait width"""
        # Use 90% of card width for content
        content_width = int(self.card_width * 0.9)
        content_start_x = (self.card_width - content_width) // 2
        start_y = 150 + self.photo_size + 20
        
        # Student Name - LARGE AND CENTERED
        name = student_data['full_name'].upper()
        draw.text((self.card_width//2, start_y), name, 
                 fill=(0, 0, 0), font=name_font, anchor="mm")
        
        # Student ID - CENTERED
        draw.text((self.card_width//2, start_y + 30), f"ID: {student_data['student_id']}", 
                 fill=(50, 50, 50), font=info_font, anchor="mm")
        
        # Department - CENTERED
        draw.text((self.card_width//2, start_y + 55), f"Department: {student_data['department']}", 
                 fill=(50, 50, 50), font=info_font, anchor="mm")
        
        # Program - CENTERED (with wrapping if needed)
        program = student_data.get('program', 'N/A')
        program_lines = self.wrap_text(program, info_font, content_width - 20)
        for i, line in enumerate(program_lines):
            prefix = "Program: " if i == 0 else "         "
            draw.text((self.card_width//2, start_y + 80 + (i * 20)), f"{prefix}{line}", 
                     fill=(50, 50, 50), font=info_font, anchor="mm")
        
        # Valid Until - CENTERED
        graduation = student_data.get('graduation_date', 'N/A')
        y_pos = start_y + 80 + (len(program_lines) * 20) + 10
        draw.text((self.card_width//2, y_pos), f"Valid Until: {graduation}", 
                 fill=(50, 50, 50), font=info_font, anchor="mm")
    
    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within max width"""
        words = text.split()
        if not words:
            return [text]
            
        lines = []
        current_line = words[0]
        
        for word in words[1:]:
            test_line = current_line + " " + word
            # Width estimation
            test_width = len(test_line) * 7  
            if test_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        
        lines.append(current_line)
        return lines
    
    def draw_portrait_front_footer(self, draw, font, height):
        """Draw front footer for portrait"""
        # Signature area
        line_length = 100
        line_start = (self.card_width - line_length) // 2
        signature_y = height - 45
        
        draw.line([(line_start, signature_y), (line_start + line_length, signature_y)], 
                 fill=(100, 100, 100), width=2)
        draw.text((self.card_width//2, signature_y + 12), "Registrar's Signature", 
                 fill=(100, 100, 100), font=font, anchor="mm")
        
        # Issue date
        issued_date = datetime.now().strftime('%m/%Y')
        draw.text((self.card_width//2, height - 20), f"Issued: {issued_date}", 
                 fill=(150, 150, 150), font=font, anchor="mm")
    
    def draw_portrait_back_background(self, draw, height):
        """Draw background for portrait back side"""
        draw.rectangle([0, 0, self.card_width, height], fill=(245, 250, 255))
    
    def draw_portrait_qr_code(self, card, qr_data):
        """Draw QR code on portrait back"""
        try:
            qr = qrcode.QRCode(
                version=2,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=4,
                border=2,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            qr_image = qr.make_image(fill_color="black", back_color="white")
            qr_image = qr_image.resize((self.qr_size, self.qr_size))
            
            # Center QR code horizontally
            qr_x = (self.card_width - self.qr_size) // 2
            qr_y = 70  # Below header
            
            card.paste(qr_image, (qr_x, qr_y))
            
            # QR code label
            draw = ImageDraw.Draw(card)
            draw.text((self.card_width // 2, qr_y + self.qr_size + 10), "SCAN TO VERIFY", 
                     fill=(41, 128, 185), font=ImageFont.load_default(), anchor="mm")
                     
        except Exception as e:
            print(f"Error generating QR code: {e}")
    
    def draw_portrait_back_text(self, draw, font, student_data):
        """Draw informational text on portrait back"""
        text_start_y = 70 + self.qr_size + 30
        
        lines = [
            "OFFICIAL ID CARD",
            "FEDERAL UNIVERSITY DUTSE",
            "",
            "Property of Federal University Dutse",
            "Must be carried on campus",
            "",
            f"Student: {student_data['full_name']}",
            f"ID: {student_data['student_id']}",
            "",
            "If found, return to:",
            "Registry Department",
            "FUD, Dutse",
            "",
            "Non-transferable",
            "Valid with official stamp"
        ]
        
        for i, line in enumerate(lines):
            draw.text((self.card_width // 2, text_start_y + (i * 18)), 
                     line, fill=(40, 40, 40), font=font, anchor="mm")
    
    def draw_portrait_contact_info(self, draw, font, height):
        """Draw contact information on portrait back"""
        draw.text((self.card_width // 2, height - 20), 
                 "www.fud.edu.ng | 080-1234-5678", 
                 fill=(100, 100, 100), font=font, anchor="mm")
    
    def generate_qr_data(self, student_data):
        """Generate QR code data string"""
        qr_data = f"""
FEDERAL UNIVERSITY DUTSE
ID CARD

Name: {student_data['full_name']}
ID: {student_data['student_id']}
Department: {student_data['department']}
Program: {student_data.get('program', 'N/A')}
Valid: {student_data.get('graduation_date', 'N/A')}
        """.strip()
        return qr_data

def generate_student_id_card(student_id):
    """Generate ID card for a specific student"""
    student_data = get_student_by_id(student_id)
    if not student_data:
        return None, "Student not found"
    
    from database import get_student_id_card_path
    existing_path = get_student_id_card_path(student_id)
    if existing_path and os.path.exists(existing_path):
        return existing_path, "ID card already exists"
    
    generator = IDCardGenerator()
    output_filename = f"{student_id}_id_card.png"
    output_path = os.path.join(GENERATED_CARDS_DIR, output_filename)
    
    print(f"Generating ID card for {student_data['full_name']}...")
    success, result = generator.generate_id_card(student_data, output_path)
    if success:
        print(f"ID card generated successfully: {output_path}")
        return output_path, "ID card generated successfully"
    else:
        print(f"Failed to generate ID card: {result}")
        return None, f"Failed to generate ID card: {result}"

def batch_generate_id_cards():
    """Generate ID cards for all students"""
    from database import get_all_students
    students = get_all_students()
    results = []
    
    for student in students:
        output_path, message = generate_student_id_card(student['student_id'])
        results.append({
            'student_id': student['student_id'],
            'name': student['full_name'],
            'success': output_path is not None,
            'message': message,
            'file_path': output_path
        })
    
    return results

def get_all_generated_id_cards():
    """Get all generated ID cards with student information"""
    from database import get_all_students
    students = get_all_students()
    
    id_cards = []
    for student in students:
        if student.get('id_card_generated') and student.get('id_card_path'):
            if os.path.exists(student['id_card_path']):
                id_cards.append({
                    'student_id': student['student_id'],
                    'full_name': student['full_name'],
                    'program': student.get('program', 'N/A'),
                    'id_card_path': student['id_card_path'],
                    'generated_date': student.get('id_card_generated_date', 'Unknown'),
                    'has_photo': bool(student.get('photo_path'))
                })
    
    return sorted(id_cards, key=lambda x: x['full_name'])