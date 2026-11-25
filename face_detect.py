import cv2

print("Loading OpenCV Face Detector...")

# 1. Load OpenCV's built-in face detection "brain" (Haar Cascade)
# This file is already on your computer because you installed opencv-python!
cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(cascade_path)

# 2. Open the camera (the code we know works!)
cap = cv2.VideoCapture(0)

print("Camera ON! Look at the lens. Press 'q' to quit.")

while True:
    success, frame = cap.read()
    if not success:
        break
    
    # Flip the frame so it acts like a mirror
    frame = cv2.flip(frame, 1)

    # 3. OpenCV's face detector requires the image to be Black & White (Grayscale)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 4. Detect the faces!
    # scaleFactor and minNeighbors help filter out false positives
    faces = face_cascade.detectMultiScale(
        gray_frame, 
        scaleFactor=1.1, 
        minNeighbors=5, 
        minSize=(30, 30)
    )

    # 5. Draw a blue rectangle around any face it finds
    for (x, y, w, h) in faces:
        # cv2.rectangle(image, top_left_corner, bottom_right_corner, color(B,G,R), thickness)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 3)

    # 6. Show the window
    cv2.imshow("OpenCV Basic Face Detection", frame)

    # 7. Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up
cap.release()
cv2.destroyAllWindows()
print("Program closed gracefully.")