class ControlFlowTransitionManager:
    """
    Manages the smooth transition of control flow states in a hybrid system.

    This class provides a framework for defining and executing transitions
    between different states in a complex system, ensuring that the system
    moves from one state to another in a controlled and predictable manner.
    """

    def __init__(self, initial_state, state_machine):
        """
        Initializes the ControlFlowTransitionManager.

        Args:
            initial_state: The initial state of the system.
            state_machine: A dictionary representing the state machine,
                           where keys are states and values are dictionaries
                           mapping events to next states and actions.
        """
        self.current_state = initial_state
        self.state_machine = state_machine
        self.history = [initial_state]

    def get_current_state(self):
        """
        Returns the current state of the system.

        Returns:
            The current state.
        """
        return self.current_state

    def transition(self, event, *args, **kwargs):
        """
        Transitions the system to a new state based on the given event.

        Args:
            event: The event that triggers the transition.
            *args: Positional arguments to be passed to the action function.
            **kwargs: Keyword arguments to be passed to the action function.

        Returns:
            True if the transition was successful, False otherwise.
        """
        if self.current_state not in self.state_machine:
            print(f"Error: Current state '{self.current_state}' not found in state machine.")
            return False

        if event not in self.state_machine[self.current_state]:
            print(f"Error: Event '{event}' not valid for current state '{self.current_state}'.")
            return False

        next_state_info = self.state_machine[self.current_state][event]

        if isinstance(next_state_info, tuple):
            next_state, action = next_state_info
            if action is not None:
                try:
                    action_result = action(*args, **kwargs)
                    if action_result is False:  # Allow actions to veto the transition
                        print(f"Action vetoed transition from '{self.current_state}' to '{next_state}' on event '{event}'.")
                        return False
                except Exception as e:
                    print(f"Error executing action for event '{event}': {e}")
                    return False
        else:
            next_state = next_state_info
            action = None

        self.current_state = next_state
        self.history.append(next_state)
        print(f"Transitioned from '{self.history[-2]}' to '{self.current_state}' on event '{event}'.")
        return True

    def get_history(self):
        """
        Returns the history of states visited.

        Returns:
            A list of states visited in order.
        """
        return self.history

    def reset(self, initial_state=None):
        """
        Resets the state machine to the initial state.

        Args:
            initial_state: The state to reset to. If None, uses the original initial state.
        """
        if initial_state is None:
            initial_state = self.history[0]  # Reset to the original initial state
        self.current_state = initial_state
        self.history = [initial_state]
        print(f"State machine reset to state '{initial_state}'.")

    def add_state(self, state, transitions=None):
        """
        Adds a new state to the state machine.

        Args:
            state: The name of the new state.
            transitions: A dictionary of transitions from this state,
                         mapping events to next states and actions.
        """
        if state in self.state_machine:
            print(f"Warning: State '{state}' already exists in the state machine.")
            return

        self.state_machine[state] = transitions if transitions is not None else {}
        print(f"Added state '{state}' to the state machine.")

    def add_transition(self, state, event, next_state, action=None):
        """
        Adds a new transition to an existing state.

        Args:
            state: The state to add the transition to.
            event: The event that triggers the transition.
            next_state: The state to transition to.
            action: An optional function to execute during the transition.
        """
        if state not in self.state_machine:
            print(f"Error: State '{state}' not found in state machine.")
            return

        if event in self.state_machine[state]:
            print(f"Warning: Event '{event}' already exists for state '{state}'. Overwriting.")

        self.state_machine[state][event] = (next_state, action) if action else next_state
        print(f"Added transition from '{state}' to '{next_state}' on event '{event}'.")

    def remove_state(self, state):
        """
        Removes a state from the state machine.

        Args:
            state: The state to remove.
        """
        if state not in self.state_machine:
            print(f"Error: State '{state}' not found in state machine.")
            return

        del self.state_machine[state]

        # Remove transitions to the deleted state from other states
        for s in self.state_machine:
            for event, next_state_info in list(self.state_machine[s].items()): # Iterate over a copy to allow deletion
                next_state = next_state_info[0] if isinstance(next_state_info, tuple) else next_state_info
                if next_state == state:
                    del self.state_machine[s][event]

        print(f"Removed state '{state}' from the state machine.")

    def remove_transition(self, state, event):
        """
        Removes a transition from a state.

        Args:
            state: The state to remove the transition from.
            event: The event to remove.
        """
        if state not in self.state_machine:
            print(f"Error: State '{state}' not found in state machine.")
            return

        if event not in self.state_machine[state]:
            print(f"Error: Event '{event}' not found for state '{state}'.")
            return

        del self.state_machine[state][event]
        print(f"Removed transition on event '{event}' from state '{state}'.")

    def visualize(self):
        """
        Prints a simple text-based visualization of the state machine.
        """
        print("State Machine Visualization:")
        for state, transitions in self.state_machine.items():
            print(f"  State: {state}")
            for event, next_state_info in transitions.items():
                if isinstance(next_state_info, tuple):
                    next_state, action = next_state_info
                    action_name = action.__name__ if action else "None"
                    print(f"    - Event: {event} -> State: {next_state}, Action: {action_name}")
                else:
                    print(f"    - Event: {event} -> State: {next_state_info}")