import os
import face_recognition
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FACES_DIR = os.path.join(BASE_DIR, "data", "faces")
MODEL_PATH = os.path.join(BASE_DIR, "models", "face_encodings.pkl")

os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

encodings = []
names = []

print("Training model...")

for person in os.listdir(FACES_DIR):

    person_path = os.path.join(FACES_DIR, person)

    if not os.path.isdir(person_path):
        continue

    for img in os.listdir(person_path):

        path = os.path.join(person_path, img)

        try:
            image = face_recognition.load_image_file(path)
            enc = face_recognition.face_encodings(image)

            if len(enc) > 0:
                encodings.append(enc[0])
                names.append(person)

        except:
            pass


joblib.dump(
    {"encodings": encodings, "names": names},
    MODEL_PATH
)

print("Model trained & saved")