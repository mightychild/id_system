import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
DATABASE_PATH = os.path.join(DATA_DIR, 'id_card_system.db')
STUDENT_PHOTOS_DIR = os.path.join(DATA_DIR, 'student_photos')
GENERATED_CARDS_DIR = os.path.join(DATA_DIR, 'generated_cards')

# Create directories if they don't exist
for directory in [DATA_DIR, STUDENT_PHOTOS_DIR, GENERATED_CARDS_DIR, ASSETS_DIR]:
    os.makedirs(directory, exist_ok=True)

# University information
UNIVERSITY_NAME = "FEDERAL UNIVERSITY DUTSE"
DEPARTMENT_NAME = "Software Engineering Department"

# Logo paths
LOGO_PATHS = [
    os.path.join(ASSETS_DIR, 'university_logo.jpeg'),
    os.path.join(ASSETS_DIR, 'logo.png'),
    os.path.join(BASE_DIR, 'university_logo.jpeg'),
    os.path.join(BASE_DIR, 'logo.png')
]