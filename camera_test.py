import cv2

# 1. Open the default camera 
# (If this fails, try changing 0 to 1 in case Windows assigned a different ID to your webcam)
cap = cv2.VideoCapture(0)

# Note: If the code hangs here, uncomment the line below and use it instead:
# cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

print("Attempting to open the webcam... Press 'q' on your keyboard to quit.")

while True:
    # 2. Grab a frame from the camera
    success, frame = cap.read()
    
    # If it can't read a frame, print an error and stop
    if not success:
        print("Error: Could not read frame. Is the camera being used by another app?")
        break

    # 3. Show the frame in a window
    cv2.imshow("OpenCV Camera Test", frame)

    # 4. Wait for the 'q' key to be pressed to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 5. Clean up and close everything
cap.release()
cv2.destroyAllWindows()
print("Camera closed successfully.")