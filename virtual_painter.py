# -*- coding: utf-8 -*-
import cv2
import numpy as np

# 1. Initialize Camera
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Cannot open camera!")
    exit()

print("Virtual Painter Started!")
print("Press 'q' to Quit | Press 'c' to Clear Canvas")

# 2. Read first frame to get dimensions
ret, frame = cap.read()
if not ret:
    print("ERROR: Cannot read frame!")
    exit()

# 3. Create COLOR canvas (3 channels for BGR)
height, width = frame.shape[:2]
canvas = np.zeros((height, width, 3), dtype=np.uint8)

prev_point = None

# 4. Color Range (BLUE)
lower_blue = np.array([100, 50, 50])
upper_blue = np.array([130, 255, 255])

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # 5. Convert to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # 6. Create Mask (used internally, not displayed)
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    # 7. Find Contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        c = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        center = (int(x), int(y))
        
        if radius > 10:
            # Draw circle on frame to show detection
            cv2.circle(frame, center, int(radius), (0, 255, 255), 2)
            
            if prev_point:
                # Draw GREEN line on canvas
                cv2.line(canvas, prev_point, center, (0, 255, 0), 5)
            
            prev_point = center
    
    # 8. Combine frame and canvas
    result = cv2.addWeighted(frame, 0.7, canvas, 0.3, 0)
    
    # 9. Show ONLY the color window
    cv2.imshow('Virtual Painter', result)
    
    # 10. Controls
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('c'):
        canvas = np.zeros((height, width, 3), dtype=np.uint8)
        prev_point = None
        print("Canvas Cleared!")

cap.release()
cv2.destroyAllWindows()