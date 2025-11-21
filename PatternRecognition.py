import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision
import time

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = vision.GestureRecognizer
GestureRecognizerOptions = vision.GestureRecognizerOptions
VisionRunningMode = mp.tasks.vision.RunningMode


class ModeHandler:
    def __init__(self):
        self.mode = 0

    def print_result(self, result, output_image, timestamp_ms):

        if result.gestures:
            top_gesture = result.gestures[0][0]
            confidence = top_gesture.score
            name = top_gesture.category_name

            print(f"Gesture: {name} ({confidence:.2f}) at {timestamp_ms} ms, mode: {self.mode}")

            if name == "Thumb_Up" and confidence >= 0.5:
                self.mode = 1
            elif name == "Thumb_Down" and confidence >= 0.5:
                self.mode = 2
            elif name == "Open_palm" and confidence >= 0.5:
                self.mode = 3
            elif name == "Closed_Palm" and confidence >= 0.5:
                self.mode = 4
        
        else:
            print(f"No gesture detected at {timestamp_ms} ms")

        # Print mode state
        match self.mode:
            case 1:
                print("Mode: Love")
            case 2:
                print("Mode: Aggression")
            case 3:
                print("Mode: Curious")
            case 4:
                print("Mode: Fear")
            case _:
                print("Mode: Part B")  # default mode

handler = ModeHandler()

options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path='gesture_recognizer.task'),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=handler.print_result   # <=== callback method
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

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        timestamp_ms = int(time.time() * 1000)

        recognizer.recognize_async(mp_image, timestamp_ms)

        cv2.imshow("Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()