import math
import cv2
import mediapipe as mp
import numpy as np
import time
from ai_controller import KeyController

class SteeringWheel:
    def __init__(self):
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_hands = mp.solutions.hands
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.key_controller = KeyController()
        self.radius = 150
        
    def calculate_steering_points(self, co, xm, ym):
        """Calculate steering wheel points using simplified geometry"""
        try:
            # Calculate angle between hands
            dx = co[1][0] - co[0][0]
            dy = co[1][1] - co[0][1]
            angle = math.atan2(dy, dx)
            
            # Calculate steering wheel endpoints
            xa = xm + self.radius * math.cos(angle)
            ya = ym + self.radius * math.sin(angle)
            xb = xm - self.radius * math.cos(angle)
            yb = ym - self.radius * math.sin(angle)
            
            # Calculate perpendicular line for steering indicator
            perp_angle = angle + math.pi/2
            xap = xm + self.radius * math.cos(perp_angle)
            yap = ym + self.radius * math.sin(perp_angle)
            xbp = xm - self.radius * math.cos(perp_angle)
            ybp = ym - self.radius * math.sin(perp_angle)
            
            return (xa, ya, xb, yb, xap, yap, xbp, ybp)
        except Exception:
            return None

    def add_mirrored_text(self, image, text, x, y, font_scale=0.8, thickness=2):
        """Add text that appears correctly in mirrored view"""
        # Create a temporary image for the text
        text_size = cv2.getTextSize(text, self.font, font_scale, thickness)[0]
        text_image = np.zeros((text_size[1] + 10, text_size[0] + 10, 3), dtype=np.uint8)
        
        # Put text on temporary image
        cv2.putText(text_image, text, (5, text_size[1] + 5), self.font, font_scale, (0, 255, 0), thickness, cv2.LINE_AA)
        
        # Flip the text horizontally
        text_image = cv2.flip(text_image, 1)
        
        # Create mask for text
        mask = text_image.sum(axis=2) > 0
        
        # Calculate position to place text
        y_offset = y - text_size[1] // 2
        x_offset = x - text_size[0] // 2
        
        # Ensure coordinates are within image bounds
        y_start = max(y_offset, 0)
        y_end = min(y_offset + text_image.shape[0], image.shape[0])
        x_start = max(x_offset, 0)
        x_end = min(x_offset + text_image.shape[1], image.shape[1])
        
        # Place text on main image where mask is True
        image[y_start:y_end, x_start:x_end][mask[:(y_end-y_start), :(x_end-x_start)]] = \
            text_image[:(y_end-y_start), :(x_end-x_start)][mask[:(y_end-y_start), :(x_end-x_start)]]

    def process_frame(self, image, results):
        """Process a single frame and return the annotated image"""
        co = []
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks
                self.mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style())
                
                # Get wrist position
                wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
                coords = self.mp_drawing._normalized_to_pixel_coordinates(
                    wrist.x, wrist.y, image.shape[1], image.shape[0])
                if coords:
                    co.append(list(coords))

        # Process steering based on hand positions
        if len(co) == 2:
            xm, ym = (co[0][0] + co[1][0]) / 2, (co[0][1] + co[1][1]) / 2
            points = self.calculate_steering_points(co, xm, ym)
            
            if points:
                xa, ya, xb, yb, xap, yap, xbp, ybp = points
                
                # Draw steering wheel
                cv2.circle(image, (int(xm), int(ym)), self.radius, (195, 255, 62), 15)
                cv2.line(image, (int(xa), int(ya)), (int(xb), int(yb)), (195, 255, 62), 20)
                
                # Calculate angle for mirrored view
                # Flip the x-coordinates to account for mirroring
                mirrored_dx = (image.shape[1] - co[0][0]) - (image.shape[1] - co[1][0])
                mirrored_dy = co[1][1] - co[0][1]
                angle_deg = math.degrees(math.atan2(mirrored_dy, mirrored_dx))
                
                # Adjustable turning threshold
                TURN_THRESHOLD = 30
                if abs(angle_deg) > TURN_THRESHOLD:  # Turning threshold
                    if angle_deg > 0:  # Turn right
                        self.handle_right_turn(image, xap, yap, xm, ym)
                    else:  # Turn left
                        self.handle_left_turn(image, xbp, ybp, xm, ym)
                else:  # Keep straight
                    self.handle_straight(image, xap, yap, xbp, ybp, xm, ym)
                    
        elif len(co) == 1:
            self.handle_reverse(image)
            
        return image

    def handle_left_turn(self, image, xbp, ybp, xm, ym):
        print("Turn right")
        self.key_controller.release_key('s')
        self.key_controller.release_key('a')
        self.key_controller.release_key('w')
        self.key_controller.press_key('d')
        self.add_mirrored_text(image, "Turn right", 100, 50)
        cv2.line(image, (int(xbp), int(ybp)), (int(xm), int(ym)), (195, 255, 62), 20)

    def handle_right_turn(self, image, xap, yap, xm, ym):
        print("Turn left")
        self.key_controller.release_key('s')
        self.key_controller.release_key('d')
        self.key_controller.release_key('w')
        self.key_controller.press_key('a')
        self.add_mirrored_text(image, "Turn left", 100, 50)
        cv2.line(image, (int(xap), int(yap)), (int(xm), int(ym)), (195, 255, 62), 20)

    def handle_straight(self, image, xap, yap, xbp, ybp, xm, ym):
        print("Keep straight")
        self.key_controller.release_key('s')
        self.key_controller.release_key('a')
        self.key_controller.release_key('d')
        self.key_controller.press_key('w')
        self.add_mirrored_text(image, "Keep straight", 100, 50)
        if ybp > yap:
            cv2.line(image, (int(xbp), int(ybp)), (int(xm), int(ym)), (195, 255, 62), 20)
        else:
            cv2.line(image, (int(xap), int(yap)), (int(xm), int(ym)), (195, 255, 62), 20)

    def handle_reverse(self, image):
        print("Reverse")
        self.key_controller.release_key('a')
        self.key_controller.release_key('d')
        self.key_controller.release_key('w')
        self.key_controller.press_key('s')
        self.add_mirrored_text(image, "Reverse", 100, 50)

def main():
    # Initialize steering wheel and camera
    steering_wheel = SteeringWheel()
    cap = cv2.VideoCapture(0)
    
    # Optimize camera settings for M1
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    # Initialize MediaPipe Hands
    with steering_wheel.mp_hands.Hands(
        model_complexity=0,  # Use lightweight model for M1
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as hands:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            # Optimize image processing
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Process frame
            image = steering_wheel.process_frame(image, results)
            
            # Display result
            cv2.imshow('Hand Steering Control', cv2.flip(image, 1))
            
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()