import cv2
import numpy as np
import mediapipe as mp


class CricketBallAnalyzer:
    def __init__(self, video_path, lower_hsv, upper_hsv, pitch_length=22):
        self.video_path = video_path
        self.lower_hsv = lower_hsv
        self.upper_hsv = upper_hsv
        self.pitch_length = pitch_length
        self.prev_ball_position = None

    def detect_ball(self, frame):
        """
        Detects the ball in the frame based on a given HSV color range.
        """
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_frame, self.lower_hsv, self.upper_hsv)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            ball_contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(ball_contour) > 50:
                x, y, w, h = cv2.boundingRect(ball_contour)
                center = (x + w // 2, y + h // 2)
                return center, (x, y, w, h)
        return None, None

    def calculate_ball_speed(self, prev_position, curr_position, time_elapsed):
        """
        Calculates the ball speed based on movement between frames.
        """
        if prev_position and curr_position:
            distance = np.linalg.norm(np.array(curr_position) - np.array(prev_position))
            return distance / time_elapsed
        return 0

    def classify_ball_type(self, speed, trajectory, ball_position):
        """
        Classifies the ball type based on speed, trajectory, and landing position.
        """
        if ball_position <= self.pitch_length * 0.15:
            return "Yorker"
        elif speed > 10 and trajectory == 'straight':
            return "Fast Ball"
        elif speed <= 10 and trajectory == 'straight':
            return "Slow Ball"
        elif trajectory == 'spin':
            return "Spin Ball"
        return "Unknown"

    def analyze_video(self):
        cap = cv2.VideoCapture(self.video_path)
        ball_type = "Unknown"

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            ball_position, _ = self.detect_ball(frame)

            if self.prev_ball_position and ball_position:
                time_elapsed = 1 / cap.get(cv2.CAP_PROP_FPS)
                speed = self.calculate_ball_speed(self.prev_ball_position, ball_position, time_elapsed)
                trajectory = 'straight'  # Placeholder for advanced tracking
                ball_type = self.classify_ball_type(speed, trajectory, ball_position[1])

            self.prev_ball_position = ball_position

        cap.release()
        return ball_type


# Define HSV range for red cricket ball
lower_hsv = np.array([0, 70, 50])
upper_hsv = np.array([10, 255, 255])
