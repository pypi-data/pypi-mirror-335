import cv2
import numpy as np


def detect_spin(frame, prev_position, ball_color_hsv_range):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_frame, ball_color_hsv_range[0], ball_color_hsv_range[1])
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        ball_contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(ball_contour) > 50:
            x, y, w, h = cv2.boundingRect(ball_contour)
            curr_position = (x + w // 2, y + h // 2)

            if prev_position:
                change_x = abs(curr_position[0] - prev_position[0])
                change_y = abs(curr_position[1] - prev_position[1])

                # If the ball moves significantly sideways but not too fast vertically, it's a spin ball
                if change_x > change_y and change_x > 5:
                    return "Spin Ball", curr_position
            return "Not a Spin Ball", curr_position
    return "No Ball Detected", None


def analyze_video(video_path:str, ball_color_hsv_range:list[tuple, tuple]):
    cap = cv2.VideoCapture(video_path)
    prev_position = None
    frame_idx = 0
    analysis = {}

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            classification, prev_position = detect_spin(frame, prev_position, ball_color_hsv_range)
            analysis[frame_idx] = classification
            frame_idx += 1

    finally:
        cap.release()

    return analysis


def classify_entire_video(video_path:str, ball_color_hsv_range:list[tuple, tuple]):
    analysis = analyze_video(video_path, ball_color_hsv_range)

    spin_count = sum(1 for v in analysis.values() if v == "Spin Ball")
    not_spin_count = sum(1 for v in analysis.values() if v == "Not a Spin Ball")
    total_frames = len(analysis)

    if total_frames == 0:
        return "No Valid Frames Detected"

    if spin_count / total_frames >= 0.5:
        return "Good Spin Ball"
    elif not_spin_count / total_frames >= 0.5:
        return "Bad Spin Ball"
    else:
        return "Not a Spin Ball"
