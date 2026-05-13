import cv2
import os
import sys
import time

# -----------------------------
# GET NAME FROM ARG
# -----------------------------
if len(sys.argv) < 2:
    print("No name provided")
    exit()

name = sys.argv[1]


# -----------------------------
# PATH SETUP
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

save_path = os.path.join(BASE_DIR, "data", "faces", name)
os.makedirs(save_path, exist_ok=True)


# -----------------------------
# CAMERA (FIXED WINDOWS ISSUE)
# -----------------------------
cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cam.set(3, 640)
cam.set(4, 480)


# -----------------------------
# FACE DETECTOR
# -----------------------------
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


# -----------------------------
# GUIDED CAPTURE SETTINGS
# -----------------------------
instructions = [
    "Look Straight",
    "Turn Left",
    "Turn Right",
    "Look Up",
    "Look Down"
]

instruction_index = 0
images_per_step = 4

count = 0
max_images = len(instructions) * images_per_step

last_capture_time = time.time()

print(f"\nStarting guided face capture for: {name}\n")


# -----------------------------
# MAIN LOOP
# -----------------------------
while True:

    ret, frame = cam.read()
    if not ret:
        print("Camera error")
        break

    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    current_instruction = instructions[instruction_index]

    # -----------------------------
    # UI OVERLAY (GUIDANCE TEXT)
    # -----------------------------
    cv2.putText(frame,
                "AI FACE REGISTRATION MODE",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2)

    cv2.putText(frame,
                f"Instruction: {current_instruction}",
                (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 255),
                2)

    cv2.putText(frame,
                f"Progress: {count}/{max_images}",
                (20, 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2)

    cv2.putText(frame,
                "Press Q to quit",
                (20, 150),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2)

    # -----------------------------
    # FACE DETECTION + CAPTURE
    # -----------------------------
    for (x, y, w, h) in faces:

        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        if time.time() - last_capture_time > 1:

            face = frame[y:y+h, x:x+w]

            img_path = os.path.join(save_path, f"{count}.jpg")
            cv2.imwrite(img_path, face)

            count += 1
            last_capture_time = time.time()

            print(f"Captured image {count}")

            # move instruction step
            if count % images_per_step == 0 and instruction_index < len(instructions) - 1:
                instruction_index += 1

        break

    # show window
    cv2.imshow("Guided Face Capture", frame)

    # stop conditions
    if count >= max_images:
        break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cam.release()
cv2.destroyAllWindows()

print(f"\nFace capture completed for: {name}")