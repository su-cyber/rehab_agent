import cv2
import tkinter as tk
from tkinter import messagebox
from coach import Sense, Think, Act
import pyttsx3
import subprocess
import sys

def start_memory_game():
    """Function to start the memory game."""
    python_executable = sys.executable
    subprocess.Popen([python_executable, 'coach\memory_game.py'])  # Adjust path if needed

class ExerciseApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Exercise and Memory Game for Eleanor")
        self.exercise_choice = None
        self.engine = pyttsx3.init()

        # Create interface for selecting exercise type
        self.create_widgets()

    def create_widgets(self):
        # Create and place labels and buttons
        label = tk.Label(self.root, text="Choose your exercise or game:", font=('Helvetica', 18))
        label.pack(pady=20)

        arm_button = tk.Button(self.root, text="Arm Exercise", font=('Helvetica', 14), command=self.start_arm_exercise)
        arm_button.pack(pady=10)

        leg_button = tk.Button(self.root, text="Leg Exercise", font=('Helvetica', 14), command=self.start_leg_exercise)
        leg_button.pack(pady=10)

        sit_stand_button = tk.Button(self.root, text="Sit-Stand Exercise", font=('Helvetica', 14), command=self.start_sit_stand_exercise)
        sit_stand_button.pack(pady=10)

        memory_game_button = tk.Button(self.root, text="Memory Game", font=('Helvetica', 14), command=self.start_memory_game)
        memory_game_button.pack(pady=10)

    def start_arm_exercise(self):
        """Handle arm exercise selection and launch the exercise program."""
        self.exercise_choice = 'arm'
        messagebox.showinfo("Arm Exercise", "Starting Arm Exercise...")
        self.engine.say(f"You have selected the Arm exercise, Eleanor. Your task is to flex and extend your left arm repeatedly. You're going to do great!")
        self.engine.runAndWait()
        self.root.destroy()  # Close the Tkinter window
        self.run_exercise()

    def start_leg_exercise(self):
        """Handle leg exercise selection and launch the exercise program."""
        self.exercise_choice = 'leg'
        messagebox.showinfo("Leg Exercise", "Starting Leg Exercise...")
        self.engine.say(f"You have selected the Leg exercise, Eleanor. Your task is to flex and extend your left leg repeatedly. Keep up the good work!")
        self.engine.runAndWait()
        self.root.destroy()  # Close the Tkinter window
        self.run_exercise()

    def start_sit_stand_exercise(self):
        """Handle sit-stand exercise selection and launch the exercise program."""
        self.exercise_choice = 'sit-stand'
        messagebox.showinfo("Sit-Stand Exercise", "Starting Sit-Stand Exercise...")
        self.engine.say(f"You have selected the sit-stand exercise, Eleanor. Your task is to sit and stand from a chair repeatedly. Stay strong!")
        self.engine.runAndWait()
        self.root.destroy()  # Close the Tkinter window
        self.run_exercise()

    def start_memory_game(self):
        """Launch the memory game."""
        self.engine.say(f"You have selected the memory game, Eleanor. Let's have some fun!")
        self.engine.runAndWait()
        self.root.destroy()  # Close the current window
        start_memory_game()

    def run_exercise(self):
        """Launch the webcam and run the selected exercise (arm, leg, or sit-stand)."""
        # Initialize components
        sense = Sense.Sense()
        act = Act.Act()
        think = Think.Think(act, exercise_type=self.exercise_choice)

        # Initialize the webcam
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Unable to open the webcam.")
            return

        # Main loop to process video frames
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to grab frame from webcam.")
                break

            # Detect joints in the frame
            joints = sense.detect_joints(frame)
            if not joints or not joints.pose_landmarks:
                print("No joints detected, skipping frame.")
                continue

            landmarks = joints.pose_landmarks

            try:
                if self.exercise_choice == 'arm':
                    # Left arm joint coordinates
                    shoulder = sense.extract_joint_coordinates(landmarks, 'left_shoulder')
                    elbow = sense.extract_joint_coordinates(landmarks, 'left_elbow')
                    wrist = sense.extract_joint_coordinates(landmarks, 'left_wrist')

                    # Calculate elbow angle
                    elbow_angle_mvg = sense.calculate_angle(shoulder, elbow, wrist)
                    print(f"Elbow angle: {elbow_angle_mvg}")

                    # Update the state machine with the elbow angle
                    think.update_state(elbow_angle_mvg)

                elif self.exercise_choice == 'leg':
                    # Left leg joint coordinates
                    hip = sense.extract_joint_coordinates(landmarks, 'left_hip')
                    knee = sense.extract_joint_coordinates(landmarks, 'left_knee')
                    ankle = sense.extract_joint_coordinates(landmarks, 'left_ankle')

                    # Calculate knee angle
                    knee_angle_mvg = sense.calculate_angle(hip, knee, ankle)
                    print(f"Knee angle: {knee_angle_mvg}")

                    # Update the state machine with the knee angle
                    think.update_state(knee_angle_mvg)

                elif self.exercise_choice == 'sit-stand':
                    # Use both hip and knee angles to detect sit-stand motion
                    hip = sense.extract_joint_coordinates(landmarks, 'left_hip')
                    knee = sense.extract_joint_coordinates(landmarks, 'left_knee')
                    ankle = sense.extract_joint_coordinates(landmarks, 'left_ankle')

                    # Calculate hip and knee angles
                    hip_angle_mvg = sense.calculate_angle(hip, knee, ankle)
                    knee_angle_mvg = sense.calculate_angle(hip, knee, ankle)
                    print(f"Hip angle: {hip_angle_mvg}, Knee angle: {knee_angle_mvg}")

                    # Update the state machine based on the sit-stand angles
                    think.update_state_sit_stand(hip_angle_mvg, knee_angle_mvg)

                # Act: Provide feedback and visualize rocket progress based on the state
                decision = think.state
                act.provide_feedback(decision, frame, joints, elbow_angle_mvg if self.exercise_choice == 'arm' else knee_angle_mvg)
                act.visualize_rocket()

            except Exception as e:
                print(f"Error during processing: {e}")
                continue

            # Exit on 'q' key press
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        # Release resources
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    root = tk.Tk()
    app = ExerciseApp(root)
    root.mainloop()
