import joblib
import face_recognition


def load_trained_model(path):

    try:
        data = joblib.load(path)
        return data["encodings"], data["names"]

    except Exception as e:
        print("Model loading failed:", e)
        return [], []


def recognize_face(encodings, names, face_encoding):

    if len(encodings) == 0:
        return "Unknown"

    matches = face_recognition.compare_faces(encodings, face_encoding, tolerance=0.5)
    distances = face_recognition.face_distance(encodings, face_encoding)

    best = distances.argmin()

    if matches[best]:
        return names[best]

    return "Unknown"