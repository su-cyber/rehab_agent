import mediapipe as mp
import cv2
import numpy as np
import random
import pyttsx3

class Act:

    def __init__(self):
        # Rocket launch progress and state tracking
        self.rep_count = 0
        self.max_reps = 10  # Launch after 10 repetitions
        self.rocket_ready = False  # Track if the rocket is ready for launch
        self.rocket_launched = False
        self.engine = pyttsx3.init()

        # Rocket visuals
        self.rocket_position = 400  # Initial vertical position (ground)
        self.rocket_speed = 10  # Speed of ascent when launching
        self.launch_flames = False  # Display flames when rocket is launching

        self.motivational_phrases = ['Ignition set!', 'Rocket is heating up!', 'Almost ready to launch!', 'Countdown starting soon!']

    def handle_rep_increase(self):
        """
        Increase the repetition count and update the rocket's state.
        """
        if not self.rocket_launched:
            self.rep_count += 1
            if self.rep_count >= self.max_reps:
                self.launch_rocket()
            else:
                self.display_progress()
                text = random.choice(self.motivational_phrases)
                self.engine.say(f"{self.rep_count} reps: {text}")
                self.engine.runAndWait()

    def display_progress(self):
        """
        Show the rocket heating up and preparing for launch as the reps increase.
        """
        if self.rep_count >= self.max_reps - 3:
            # Show countdown effect as rocket approaches launch
            self.engine.say(f"Countdown: {self.max_reps - self.rep_count}")
            self.engine.runAndWait()

    def launch_rocket(self):
        """
        Handle the rocket launch once the required number of reps is reached.
        """
        self.rocket_ready = True
        self.launch_flames = True  # Display flames during launch
        self.engine.say("Lift off! The rocket is launching!")
        self.engine.runAndWait()

    def visualize_rocket(self):
        """
        Display the rocket progress visually on the screen.
        """
        img = np.zeros((500, 500, 3), dtype=np.uint8)  # Create black background

        # Display rocket
        rocket_color = (255, 255, 255)  # White rocket
        if self.rocket_launched:
            self.rocket_position -= self.rocket_speed  # Rocket ascends
            if self.rocket_position <= 0:
                self.rocket_position = 0
        else:
            # Rocket at initial position until launch
            self.rocket_position = 400 - int(350 * (self.rep_count / self.max_reps))  # Move rocket up gradually

        cv2.rectangle(img, (220, self.rocket_position), (280, self.rocket_position + 50), rocket_color, -1)  # Draw rocket

        # Display flames during launch
        if self.launch_flames and not self.rocket_launched:
            for i in range(3):
                flame_x = random.randint(220, 280)
                flame_y = self.rocket_position + 50 + random.randint(5, 20)
                cv2.circle(img, (flame_x, flame_y), 5, (0, 0, 255), -1)  # Red flames

        # Show the countdown on screen when close to launch
        if self.rep_count >= self.max_reps - 3 and not self.rocket_launched:
            cv2.putText(img, f'Countdown: {self.max_reps - self.rep_count}', (100, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        # Show "Launch" when the rocket is in flight
        if self.rocket_position <= 0:
            self.rocket_launched = True
            cv2.putText(img, 'Launch!', (150, 250), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4, cv2.LINE_AA)

        cv2.putText(img, f'Reps: {self.rep_count}', (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow('Rocket Launch', img)
        cv2.waitKey(1)

    def provide_feedback(self, decision, frame, joints, angle):
        """
        Displays feedback for both arm and leg exercises.
        
        :param decision: The current state.
        :param frame: The current video frame.
        :param joints: The detected pose joints.
        :param angle: The moving average of the elbow/knee angle.
        """
        # Draw the skeleton on the frame
        mp.solutions.drawing_utils.draw_landmarks(frame, joints.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS)

        # Set up text to display based on the state
        text = f"State: {decision} (Angle: {angle:.2f})"

        # Define font properties
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.9
        font_color = (0, 255, 0)  # Green color for text
        thickness = 2

        # Add text to the frame
        cv2.putText(frame, text, (50, 50), font, font_scale, font_color, thickness)

        # Display the frame with feedback
        cv2.imshow('Rehabilitation Feedback', frame)

    def visual_feedback(self, message):
        """
        Provides simple visual feedback (text-based) to the user based on the current action.

        :param message: The message to display (e.g., "Flexing", "Extending").
        """
        print(f"Feedback: {message}")  # For now, print to console, can be extended with GUI feedback.
