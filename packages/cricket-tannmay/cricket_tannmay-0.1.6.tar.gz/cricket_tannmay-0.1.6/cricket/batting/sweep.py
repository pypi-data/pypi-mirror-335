import cv2
import mediapipe as mp
from cricket.utils import calculate_angle

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose


# Function to classify a frame based on pose landmarks
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

    # Additional conditions for identifying a sweep shot
    torso_angle = calculate_angle(left_shoulder, right_shoulder,
                                  [landmarks[mp_pose.PoseLandmark.LEFT_HIP].x,
                                   landmarks[mp_pose.PoseLandmark.LEFT_HIP].y])

    # Conditions for Good Sweep, Bad Sweep, and Not a Sweep
    if 70 <= left_arm_angle <= 110 or 70 <= right_arm_angle <= 110:
        if 20 <= torso_angle <= 50:
            return "Good Sweep"
        else:
            return "Bad Sweep"
    else:
        return "Not a Sweep"


# Function to analyze the entire video and return per-frame classifications
def analyze_video(video_path:str):
    analysis = {}  # Dictionary to store frame-by-frame classification
    cap = cv2.VideoCapture(video_path)
    pose = mp_pose.Pose()
    frame_idx = 0

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Convert the frame to RGB for MediaPipe processing
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)

            if results.pose_landmarks:
                # Classify the current frame and store in the dictionary
                shot_classification = classify_frame(results.pose_landmarks.landmark)
                analysis[frame_idx] = shot_classification

            frame_idx += 1  # Increment the frame index

    finally:
        cap.release()  # Ensure the video capture is released

    return analysis


def classify_entire_video(video_path:str):
    analysis = analyze_video(video_path)

    # Count the occurrences of each classification
    good_sweep_count = sum(1 for v in analysis.values() if v == "Good Sweep")
    bad_sweep_count = sum(1 for v in analysis.values() if v == "Bad Sweep")
    not_sweep_count = sum(1 for v in analysis.values() if v == "Not a Sweep")

    total_frames = len(analysis)

    # Final classification logic
    if total_frames == 0:
        return "No Valid Frames Detected"

    if good_sweep_count / total_frames >= 0.5:
        return "Good Sweep Detected"
    elif bad_sweep_count / total_frames >= 0.5:
        return "Bad Sweep Detected"
    else:
        return "Not a Sweep"
