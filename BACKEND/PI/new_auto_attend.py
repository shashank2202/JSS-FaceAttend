import cv2
import requests
import face_recognition
import time

# Configuration
EC2_API_URL = "http://13.49.154.188:5050/recognize-face"
marked_ids = set()
SEND_INTERVAL = 2  # Send request every 2 seconds max
last_sent_time = 0

# Initialize webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("? Could not open webcam.")
    exit()

print("? Webcam started. Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("? Failed to grab frame.")
        break

    # Resize for faster detection
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Detect face
    face_locations = face_recognition.face_locations(rgb_small_frame)

    if face_locations and (time.time() - last_sent_time > SEND_INTERVAL):
        print("? Face detected. Sending to server...")
        last_sent_time = time.time()

        try:
            # Encode the resized frame (not full frame) to JPEG in memory
            _, img_encoded = cv2.imencode(".jpg", frame)
            response = requests.post(
                EC2_API_URL,
                files={"file": ("frame.jpg", img_encoded.tobytes(), "image/jpeg")},
                timeout=5  # optional timeout to avoid blocking too long
            )

            if response.status_code == 200:
                result = response.json()
                student_id = result.get("student_id")

                if result.get("status") == "Match" and student_id:
                    if student_id in marked_ids:
                        print(f"?? Already marked: {student_id}")
                    else:
                        print(f"? Marked: {student_id} at {result.get('timestamp')}")
                        marked_ids.add(student_id)
                else:
                    print("?? Face not recognized.")
            else:
                print("? Server error:", response.status_code)

        except Exception as e:
            print("? Error sending request:", e)

    else:
        print("? No face detected or waiting to send next frame.")

    # Display webcam feed
    cv2.imshow("Webcam Feed", frame)

    # Use a short waitKey to allow real-time updates (wait ~30ms)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
