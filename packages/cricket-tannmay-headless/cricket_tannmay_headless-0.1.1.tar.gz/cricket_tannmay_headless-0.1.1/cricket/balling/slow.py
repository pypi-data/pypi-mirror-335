import cv2
import numpy as np


def detect_slow_ball(frame, prev_position, ball_color_hsv_range, time_elapsed):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_frame, ball_color_hsv_range[0], ball_color_hsv_range[1])
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        ball_contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(ball_contour) > 50:
            x, y, w, h = cv2.boundingRect(ball_contour)
            curr_position = (x + w // 2, y + h // 2)

            if prev_position:
                distance = np.linalg.norm(np.array(curr_position) - np.array(prev_position))
                speed = distance / time_elapsed
                if speed <= 5:
                    return "Slow Ball", curr_position
            return "Not a Slow Ball", curr_position
    return "No Ball Detected", None


def analyze_video(video_path:str, ball_color_hsv_range:list[tuple, tuple]):
    cap = cv2.VideoCapture(video_path)
    prev_position = None
    frame_idx = 0
    time_elapsed = 1
    analysis = {}

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            classification, prev_position = detect_slow_ball(frame, prev_position, ball_color_hsv_range, time_elapsed)
            analysis[frame_idx] = classification
            frame_idx += 1

    finally:
        cap.release()

    return analysis


def classify_entire_video(video_path:str, ball_color_hsv_range:list[tuple, tuple]):
    analysis = analyze_video(video_path, ball_color_hsv_range)

    slow_count = sum(1 for v in analysis.values() if v == "Slow Ball")
    not_slow_count = sum(1 for v in analysis.values() if v == "Not a Slow Ball")
    total_frames = len(analysis)

    if total_frames == 0:
        return "No Valid Frames Detected"

    if slow_count / total_frames >= 0.5:
        return "Good Slow Ball"
    elif not_slow_count / total_frames >= 0.5:
        return "Bad Slow Ball"
    else:
        return "Not a Slow Ball"
