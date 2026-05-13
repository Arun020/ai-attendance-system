import face_recognition
import numpy as np
import joblib


def load_trained_model(model_path):

    print("Loading trained model...")

    model_data = joblib.load(model_path)

    known_encodings = model_data["encodings"]
    known_names = model_data["names"]

    print("Model loaded successfully.")

    return known_encodings, known_names


def recognize_face(
    known_encodings,
    known_names,
    face_encoding,
    tolerance=0.45
):

    matches = face_recognition.compare_faces(
        known_encodings,
        face_encoding,
        tolerance=tolerance
    )

    face_distances = face_recognition.face_distance(
        known_encodings,
        face_encoding
    )

    name = "Unknown"

    if len(face_distances) > 0:

        best_match_index = np.argmin(
            face_distances
        )

        if matches[best_match_index]:

            name = known_names[
                best_match_index
            ]

    return name