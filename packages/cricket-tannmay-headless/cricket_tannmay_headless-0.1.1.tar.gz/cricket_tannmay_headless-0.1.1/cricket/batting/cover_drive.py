import cv2
import mediapipe as mp
from cricket.utils import calculate_angle

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose


# Modified classify_frame function with "Bad Cover Drive"
def classify_frame(landmarks):
    left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y]
    left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].x,
                  landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].y]
    left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST].x,
                  landmarks[mp_pose.PoseLandmark.LEFT_WRIST].y]

    right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x,
                      landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y]
    right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].x,
                   landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].y]
    right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].x,
                   landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].y]

    left_arm_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
    right_arm_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)

    # Defining cover drive angles for the bat and posture
    if 100 <= left_arm_angle <= 130 or 100 <= right_arm_angle <= 130:
        bat_position = "Cover"
    else:
        bat_position = "Not Cover"

    ball_position = "Cover"  # Assume ball is in a cover drive position

    if bat_position == "Cover" and ball_position == "Cover":
        return "Good Cover Drive"
    elif bat_position == "Not Cover" and ball_position == "Cover":
        return "Bad Cover Drive"
    else:
        return "Not a Cover Drive"


# Analyze video to get frame-by-frame classifications
def analyze_video(video_path:str):
    analysis = {}
    cap = cv2.VideoCapture(video_path)
    pose = mp_pose.Pose()
    frame_idx = 0

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)

            if results.pose_landmarks:
                shot_classification = classify_frame(results.pose_landmarks.landmark)
                analysis[frame_idx] = shot_classification

            frame_idx += 1

    finally:
        cap.release()

    return analysis


# New function to classify the entire video based on frame-by-frame results
def classify_entire_video(video_path:str):
    analysis = analyze_video(video_path)

    # Count the occurrences of each classification
    good_drive_count = sum(1 for v in analysis.values() if v == "Good Cover Drive")
    bad_drive_count = sum(1 for v in analysis.values() if v == "Bad Cover Drive")
    not_cover_drive_count = sum(1 for v in analysis.values() if v == "Not a Cover Drive")

    total_frames = len(analysis)

    # Final classification logic
    if total_frames == 0:
        return "No Valid Frames Detected"

    if good_drive_count / total_frames >= 0.5:
        return "Good Cover Drive"

    elif bad_drive_count / total_frames >= 0.5:
        return "Bad Cover Drive"

    else:
        return "Not a Cover Drive"
