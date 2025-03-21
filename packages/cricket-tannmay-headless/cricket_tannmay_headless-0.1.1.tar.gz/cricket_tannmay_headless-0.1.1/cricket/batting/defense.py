import cv2
import mediapipe as mp
from cricket.utils import calculate_angle

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose


# Function to classify frame based on defense shot logic
def classify_frame(landmarks):
    # Extracting key points: Shoulder, Elbow, Wrist for both arms
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

    # Calculate arm angles
    left_arm_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
    right_arm_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)

    # Defense shot logic:
    if 160 <= left_arm_angle <= 180 or 160 <= right_arm_angle <= 180:
        return "Good Defense"
    elif 130 <= left_arm_angle < 160 or 130 <= right_arm_angle < 160:
        return "Bad Defense"  # Arm not extended enough
    else:
        return "Not a Defense Shot"  # Arm posture not suitable for defense


# Analyze video to classify frames
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


# Classify the entire video based on frame results
def classify_entire_video(video_path:str):
    analysis = analyze_video(video_path)

    # Count occurrences of each classification
    good_defense_count = sum(1 for v in analysis.values() if v == "Good Defense")
    bad_defense_count = sum(1 for v in analysis.values() if v == "Bad Defense")
    not_defense_count = sum(1 for v in analysis.values() if v == "Not a Defense Shot")

    total_frames = len(analysis)

    # Final classification logic
    if total_frames == 0:
        return "No Valid Frames Detected"

    if good_defense_count / total_frames >= 0.5:
        return "Good Defense"

    elif bad_defense_count / total_frames >= 0.5:
        return "Bad Defense"

    else:
        return "Not a Defense Shot"
