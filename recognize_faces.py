import os
import face_recognition
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Пути ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWN_FACES_DIR = os.path.join(BASE_DIR, 'known_faces')
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'face-recognition-credentials.json')

# --- Google Sheets ---
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)

# --- Доступ к Google Таблице ---
spreadsheet_id = '1AaJxPoR0eUdFvOiq73wTCZFmVKD4KnSfOBo8BCkwrV8'
sheet_name = 'учет посещаемости май'
worksheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)

# --- Загрузка известных лиц ---
print("Загружаем известные лица...")
known_face_encodings = []
known_face_names = []

for filename in os.listdir(KNOWN_FACES_DIR):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        image_path = os.path.join(KNOWN_FACES_DIR, filename)
        image = face_recognition.load_image_file(image_path)
        encoding = face_recognition.face_encodings(image)
        if encoding:
            known_face_encodings.append(encoding[0])
            name = os.path.splitext(filename)[0]
            known_face_names.append(name)

# --- Распознавание лиц на одном фото ---
def recognize_and_return_names(photo_path):
    print(f"📸 Обработка: {photo_path}")
    recognized_names = []

    image = face_recognition.load_image_file(photo_path)
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
        name = "Неизвестный"

        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]
            if name not in recognized_names:
                recognized_names.append(name)

    print("✅ Распознаны:", recognized_names)
    return recognized_names
def write_names_to_sheet(names):
    if not names:
        return

    # Определим следующую свободную строку
    next_row = len(worksheet.get_all_values()) + 1

    for name in names:
        worksheet.update_acell(f'D{next_row}', name)
        next_row += 1
