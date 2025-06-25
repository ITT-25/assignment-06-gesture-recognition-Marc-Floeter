import cv2
import mediapipe as mp
from pynput.mouse import Controller, Button

SHOW_CAM = True
DRAWING_THRESHOLD = 30 # Max Abstand Zeigefinger zu Daumen zum Auslösen des Malens in px
DEBUG = True # Anzeige von Prints, Landmarks etc.

NUM_HANDS = 1
DETECTION_CONFIDENCE = 0.7
TRACKING_CONFIDENCE = 0.7


class HandDetection:

    def __init__(self, num_hands=1, detection_confidence=0.7, tracking_confidence=0.7, drawing_threshold=30, show_cam=True, debug=False):
        self.detector = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=num_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )
        self.cap = cv2.VideoCapture(0)
        self.show_cam = show_cam
        self.running = False

        self.drawing = False
        self.drawing_threshold = drawing_threshold

        self.mouse = Controller()
        self.screen_w = 1920
        self.screen_h = 1080

        self.debug = debug


    def run(self):
        self.running = True
        while self.running:
            success, frame = self.cap.read()
            if not success:
                continue
            
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            success, data = self.detect(frame_rgb, frame.shape)
            if success:
                for handedness, (coords, landmark_data) in data.items():

                    if len(coords) >= 9:
                            index_tip = coords[8] # Zeigefingerspitze Koordinaten 
                            thumb_tip = coords[4] # Daumenspitze Koordinaten
                            dx = index_tip[0] - thumb_tip[0]
                            dy = index_tip[1] - thumb_tip[1]
                            distance = (dx ** 2 + dy ** 2) ** 0.5 # Abstand Zeigefinger - Daumen

                            # Handpossition in Kamera auf Bildschirmgröße übertragen
                            mapped_x, mapped_y = self.map_to_screen(index_tip[0], index_tip[1], frame.shape)
                            self.mouse.position = (mapped_x, mapped_y) # Mausposition setzen

                            # Zeigefinger berührt Daumen -> Mausklick -> Zeichnen aktiviert
                            if distance < self.drawing_threshold:
                                if not self.drawing:
                                    print("Zeichnen aktiviert")
                                self.mouse.press(Button.left)
                            else:
                                if self.drawing:
                                    print("Zeichnen deaktiviert")
                                self.mouse.release(Button.left)

                    # Debug-Anzeigen 
                    if self.debug:
                        print(f"{handedness} hand detected. Index fingertip: {coords[8]}")
                        self.draw_landmarks(frame, landmark_data)
                        cv2.circle(frame, coords[8], 10, (0, 255, 0), -1)  # Zeigefingerspitze in grün
                        cv2.putText(frame, f"Drawing: {self.drawing}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0) if self.drawing else (0, 0, 255), 2)
            
            # Kamerabild zeigen (falls gewollt)
            if self.show_cam:
                cv2.imshow("Handkamera", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    self.running = False
                    self.cap.release()
                    cv2.destroyAllWindows()


    def detect(self, img_rgb, shape):
        hand_data = {}
        h, w, _ = shape
        detections = self.detector.process(img_rgb)

        success = detections.multi_hand_landmarks and detections.multi_handedness
        if not success:
            return False, hand_data

        for hand_landmarks, handedness in zip(detections.multi_hand_landmarks, detections.multi_handedness):
            handedness_label = handedness.classification[0].label
            coords = []

            for lm in hand_landmarks.landmark:
                x_px = int(lm.x * w)
                y_px = int(lm.y * h)
                coords.append((x_px, y_px))

            hand_data[handedness_label] = (coords, hand_landmarks)

        return True, hand_data


    def draw_landmarks(self, img, landmarks):
        mp.solutions.drawing_utils.draw_landmarks(
            img, landmarks, mp.solutions.hands.HAND_CONNECTIONS
        )


    # Handposition im Kamerabild auf Bildschirmgröße übertragen
    def map_to_screen(self, x, y, frame_shape):
        frame_h, frame_w, _ = frame_shape
        mapped_x = int((x / frame_w) * self.screen_w)
        mapped_y = int((y / frame_h) * self.screen_h)
        return mapped_x, mapped_y


if __name__ == "__main__":
    detector = HandDetection(NUM_HANDS, DETECTION_CONFIDENCE, TRACKING_CONFIDENCE, DRAWING_THRESHOLD, SHOW_CAM, DEBUG)
    detector.run()