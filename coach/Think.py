from transitions import Machine

# Think Component: Decision Making for rehabilitation exercises

class Think(object):

    def __init__(self, act_component, exercise_type='arm', flexion_threshold=90, extension_threshold=120):
        """
        Initializes a state machine based on the exercise type (arm, leg, or sit-stand).
        """
        # Define thresholds based on exercise type
        self.flexion_threshold = flexion_threshold  # Flexion threshold for arm
        self.extension_threshold = extension_threshold  # Extension threshold for arm

        # Act component for visual feedback and game interaction (rocket launch)
        self.act_component = act_component

        # Define states
        if exercise_type == 'sit-stand':
            states = ['sitting', 'standing']
        else:
            states = ['neutral', 'flexion', 'extension']

        # Initialize the state machine
        self.machine = Machine(model=self, states=states, initial='neutral' if exercise_type != 'sit-stand' else 'standing')

        # Define transitions for arm and leg
        self.machine.add_transition(trigger='flex', source='neutral', dest='flexion',
                                    after='handle_flexion')
        self.machine.add_transition(trigger='extend', source='flexion', dest='extension',
                                    after='handle_extension')
        self.machine.add_transition(trigger='return_to_neutral', source='extension', dest='neutral')

        # Define transitions for sit-stand
        self.machine.add_transition(trigger='sit', source='standing', dest='sitting',
                                    after='handle_sit')
        self.machine.add_transition(trigger='stand', source='sitting', dest='standing',
                                    after='handle_stand')

    # Callbacks for movements
    def handle_flexion(self):
        """Handles actions when flexion occurs."""
        self.act_component.visual_feedback('Flexing!')
        # Update the rocket and reps when the user flexes
        self.act_component.handle_rep_increase()

    def handle_extension(self):
        """Handles actions when extension occurs."""
        self.act_component.visual_feedback('Extending!')
        # Update the rocket and reps when the user extends
        self.act_component.handle_rep_increase()

    def handle_sit(self):
        """Handles actions when sitting occurs."""
        self.act_component.visual_feedback('Sitting!')
        print("Sitting detected!")  # Debugging print
        # Update the rocket and reps when the user sits
        self.act_component.handle_rep_increase()

    def handle_stand(self):
        """Handles actions when standing occurs."""
        self.act_component.visual_feedback('Standing!')
        print("Standing detected!")  # Debugging print
        # Update the rocket and reps when the user stands
        self.act_component.handle_rep_increase()

    # Method to update the state based on arm or leg angle
    def update_state(self, current_angle):
        if current_angle < self.flexion_threshold and self.state == 'neutral':
            self.flex()  # Move to flexion state
        elif current_angle > self.extension_threshold and self.state == 'flexion':
            self.extend()  # Move to extension state
        elif current_angle < self.flexion_threshold and self.state == 'extension':
            self.return_to_neutral()  # Return to neutral state

    # Method to update state based on sit-stand motion
    def update_state_sit_stand(self, hip_angle, knee_angle):
        print(f"Debug: hip_angle={hip_angle}, knee_angle={knee_angle}, current state={self.state}")  # Debugging
        if hip_angle > self.extension_threshold and knee_angle > self.extension_threshold:
            if self.state == 'sitting':
                self.stand()  # Move to standing state
        elif hip_angle < self.flexion_threshold and knee_angle < self.flexion_threshold:
            if self.state == 'standing':
                self.sit()  # Move to sitting state
