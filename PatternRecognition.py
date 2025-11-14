import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision
import time

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = vision.GestureRecognizer
GestureRecognizerOptions = vision.GestureRecognizerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

def print_result(result, output_image, timestamp_ms):
    if result.gestures:
        top_gesture = result.gestures[0][0]
        confidence = top_gesture.score
        print(f"Gesture: {top_gesture.category_name} ({confidence:.2f}) at {timestamp_ms} ms")
    else:
        print(f"No gesture detected at {timestamp_ms} ms")

options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path='gesture_recognizer.task'),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result
)

with GestureRecognizer.create_from_options(options) as recognizer:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert to mediapipe recognisable
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        timestamp_ms = int(time.time() * 1000)
        recognizer.recognize_async(mp_image, timestamp_ms)   

        # Output of video
        cv2.imshow("Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()