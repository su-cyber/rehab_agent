import cv2
import mediapipe as mp
import math
import numpy as np

# Sense Component: Detect joints using the camera
class Sense:

    def __init__(self):
        # Initialize the Mediapipe Pose object to track joints
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose.Pose(static_image_mode=False, model_complexity=1)


        # Moving average filter for smoother angles
        self.angle_window = [-1] * 10  # Smoother tracking
        self.previous_angle = -1

    def detect_joints(self, frame):
        # Ensure the frame is in RGB as required by Mediapipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.mp_pose.process(frame_rgb)
        return results if results.pose_landmarks else None

    def calculate_angle(self, joint1, joint2, joint3):
        """
        Calculates the angle between three joints.
        """
        vector1 = [joint1[0] - joint2[0], joint1[1] - joint2[1]]
        vector2 = [joint3[0] - joint2[0], joint3[1] - joint2[1]]

        dot_product = vector1[0] * vector2[0] + vector1[1] * vector2[1]
        magnitude1 = math.sqrt(vector1[0] ** 2 + vector1[1] ** 2)
        magnitude2 = math.sqrt(vector2[0] ** 2 + vector2[1] ** 2)

        angle = math.acos(dot_product / (magnitude1 * magnitude2 + 1e-7))  # Avoid divide by zero

        # Get a moving average for smoother tracking
        self.angle_window.pop(0)
        self.angle_window.append(math.degrees(angle))
        return np.mean(self.angle_window)

    def extract_joint_coordinates(self, landmarks, joint):
        joint_index_map = {
            'left_shoulder': mp.solutions.pose.PoseLandmark.LEFT_SHOULDER,
            'left_elbow': mp.solutions.pose.PoseLandmark.LEFT_ELBOW,
            'left_wrist': mp.solutions.pose.PoseLandmark.LEFT_WRIST,
            'left_hip': mp.solutions.pose.PoseLandmark.LEFT_HIP,
            'left_knee': mp.solutions.pose.PoseLandmark.LEFT_KNEE,
            'left_ankle': mp.solutions.pose.PoseLandmark.LEFT_ANKLE
        }
        joint_index = joint_index_map[joint]
        landmark = landmarks.landmark[joint_index]

        return landmark.x, landmark.y

    def extract_hip_angle(self, landmarks):
        left_hip = self.extract_joint_coordinates(landmarks, 'left_hip')
        left_shoulder = self.extract_joint_coordinates(landmarks, 'left_shoulder')
        left_knee = self.extract_joint_coordinates(landmarks, 'left_knee')
        return self.calculate_angle(left_shoulder, left_hip, left_knee)

    def extract_knee_angle(self, landmarks):
        left_hip = self.extract_joint_coordinates(landmarks, 'left_hip')
        left_knee = self.extract_joint_coordinates(landmarks, 'left_knee')
        left_ankle = self.extract_joint_coordinates(landmarks, 'left_ankle')
        return self.calculate_angle(left_hip, left_knee, left_ankle)
