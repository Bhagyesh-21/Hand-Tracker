import cv2
import os
import datetime

# 1. Show where the script is running from (Base Folder)
current_directory = os.getcwd()
print(f"[FOLDER] Script is running in: {current_directory}")

# 2. Define where to save videos
save_folder = os.path.join(current_directory, "recordings")
os.makedirs(save_folder, exist_ok=True)

print(f"[SAVE] Videos will be saved in: {save_folder}")
print("-" * 30)

# Initialize Camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Cannot open camera")
    exit()

# Motion Detection Variables
prev_frame = None
is_recording = False
out = None
min_area = 500

print("[STATUS] Monitoring... Wave your hand to trigger recording.")
print("[INFO] Press 'q' to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Preprocess
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # Motion Logic
    if prev_frame is None:
        prev_frame = gray
        continue

    frame_delta = cv2.absdiff(prev_frame, gray)
    _, thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)
    thresh = cv2.dilate(thresh, None, iterations=2)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    motion_detected = False
    for contour in contours:
        if cv2.contourArea(contour) > min_area:
            motion_detected = True
            break

    # RECORDING LOGIC
    if motion_detected and not is_recording:
        # START RECORDING
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"motion_{timestamp}.avi"
        full_path = os.path.join(save_folder, filename)
        
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(full_path, fourcc, 20.0, (frame.shape[1], frame.shape[0]))
        
        is_recording = True
        print(f"[START] Motion Detected! Saving to: {full_path}")

    if is_recording:
        out.write(frame)

    if not motion_detected and is_recording:
        # STOP RECORDING
        out.release()
        out = None
        is_recording = False
        print(f"[STOP] Motion Stopped. File Saved.")

    prev_frame = gray

    # Display
    status = "Recording..." if is_recording else "Monitoring"
    cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("Security Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        if is_recording:
            out.release()
        break

cap.release()
cv2.destroyAllWindows()