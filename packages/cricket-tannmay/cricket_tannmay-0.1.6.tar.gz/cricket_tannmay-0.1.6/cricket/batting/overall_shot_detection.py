import cv2
import mediapipe as mp
import numpy as np


class CricketShotClassifier:
    def __init__(self):
        """Initialize MediaPipe Pose model."""
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()

    def classify_shot(self, frame):
        """Classifies the shot in a single frame."""
        results = self.pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if results.pose_landmarks:
            key_points = self.extract_key_points(results.pose_landmarks)
            return self.analyze_key_points(key_points)
        return "unknown"

    def extract_key_points(self, landmarks):
        """Extracts key points from pose landmarks."""
        return np.array([[lm.x, lm.y, lm.z] for lm in landmarks.landmark]).flatten()

    def analyze_key_points(self, key_points):
        """Analyzes key points and classifies shot types."""
        left_wrist_y = key_points[15 * 3 + 1]
        right_wrist_y = key_points[16 * 3 + 1]
        shoulder_y = (key_points[11 * 3 + 1] + key_points[12 * 3 + 1]) / 2
        left_elbow_y = key_points[13 * 3 + 1]
        right_elbow_y = key_points[14 * 3 + 1]
        torso_y = (key_points[11 * 3 + 1] + key_points[12 * 3 + 1]) / 2
        hip_y = (key_points[23 * 3 + 1] + key_points[24 * 3 + 1]) / 2

        # Determine shot type and quality
        if right_wrist_y < shoulder_y and left_wrist_y < shoulder_y:
            return self.assess_shot("pull shot", left_wrist_y, right_wrist_y, 0.2)

        elif left_wrist_y > shoulder_y and right_wrist_y < torso_y and abs(left_elbow_y - right_elbow_y) < 0.1:
            return self.assess_shot("hook shot", left_wrist_y, right_wrist_y, 0.15)

        elif left_wrist_y > hip_y > right_wrist_y:
            return self.assess_shot("reverse sweep", left_wrist_y, right_wrist_y, 0.15)

        elif right_wrist_y > shoulder_y > left_wrist_y:
            return self.assess_shot("sweep shot", left_wrist_y, right_wrist_y, 0.1)

        elif abs(left_wrist_y - right_wrist_y) < 0.05:
            return self.assess_shot("defence", left_wrist_y, right_wrist_y, 0.1)

        elif right_wrist_y > shoulder_y and abs(left_wrist_y - right_wrist_y) < 0.1:
            return self.assess_shot("straight drive", left_wrist_y, right_wrist_y, 0.15)

        elif left_wrist_y > shoulder_y > right_wrist_y:
            return self.assess_shot("cover drive", left_wrist_y, right_wrist_y, 0.2)

        return "unknown"

    def assess_shot(self, shot_type, left_wrist, right_wrist, threshold):
        """Evaluates if the shot is good or bad."""
        difference = abs(left_wrist - right_wrist)
        return f"Good {shot_type}" if difference < threshold else f"Bad {shot_type}"

    def classify_entire_video(self, video_path:str):
        """Classifies all shots in a video and returns the most frequent one."""
        cap = cv2.VideoCapture(video_path)
        shot_count = {}

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Classify the shot in the current frame
            shot_type = self.classify_shot(frame)
            if shot_type != "unknown":
                shot_count[shot_type] = shot_count.get(shot_type, 0) + 1

        cap.release()

        # Get the most frequent shot type
        if shot_count:
            return max(shot_count, key=shot_count.get)
        return "No valid shots detected"

