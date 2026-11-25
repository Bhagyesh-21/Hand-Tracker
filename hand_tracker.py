import cv2
import numpy as np
import os
import datetime

print("[1] Imports successful", flush=True)

# Create save folder
current_directory = os.getcwd()
save_folder = os.path.join(current_directory, "hand_recordings")
os.makedirs(save_folder, exist_ok=True)
print(f"[2] Save folder created: {save_folder}", flush=True)

# Initialize Camera
print("[3] Trying to open camera...", flush=True)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("[ERROR] Cannot open camera!", flush=True)
    exit()

print("[4] Camera opened successfully", flush=True)
print("[5] Starting hand detection (skin color method)...", flush=True)

is_recording = False
out = None
fourcc = cv2.VideoWriter_fourcc(*'XVID')

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    # Skin color detection
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_skin = np.array([0, 48, 0])
    upper_skin = np.array([20, 255, 255])
    mask = cv2.inRange(hsv, lower_skin, upper_skin)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    hand_detected = False
    for contour in contours:
        if cv2.contourArea(contour) > 5000:
            hand_detected = True
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            break

    # Recording logic
    if hand_detected and not is_recording:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"hand_{timestamp}.avi"
        full_path = os.path.join(save_folder, filename)
        out = cv2.VideoWriter(full_path, fourcc, 20.0, (frame.shape[1], frame.shape[0]))
        is_recording = True
        print(f"[START] Hand Detected! Saving: {filename}", flush=True)

    if is_recording:
        out.write(frame)

    if not hand_detected and is_recording:
        out.release()
        out = None
        is_recording = False
        print(f"[STOP] File Saved", flush=True)

    status = "HAND DETECTED" if hand_detected else "Monitoring"
    color = (0, 0, 255) if hand_detected else (0, 255, 0)
    cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    cv2.imshow("Hand Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        if is_recording:
            out.release()
        break

cap.release()
cv2.destroyAllWindows()
print("[INFO] Done!", flush=True)