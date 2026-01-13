import random
import time
import hashlib
import os
import subprocess
import threading
from typing import List, Callable, Any, Dict, Tuple

class TimeEntangledBuilder:
    """
    A build system that executes build scripts with forward and backward time components.
    This allows for simulating dependencies and effects that propagate both forward and backward in time,
    potentially useful for complex simulations, AI training, or advanced software development.
    """

    def __init__(self, build_scripts: Dict[str, Callable[[Dict[str, Any]], bool]], initial_state: Dict[str, Any] = None, time_dilation_factor: float = 1.0):
        """
        Initializes the TimeEntangledBuilder.

        Args:
            build_scripts: A dictionary mapping script names to callable functions.
                           Each function takes the current state as input and returns True if successful, False otherwise.
            initial_state: The initial state of the system.
            time_dilation_factor: A factor to adjust the perceived passage of time.  Values > 1 speed up time, < 1 slow it down.
        """
        self.build_scripts = build_scripts
        self.state = initial_state or {}
        self.history = []  # List of (timestamp, script_name, state) tuples
        self.time = 0.0
        self.time_dilation_factor = time_dilation_factor
        self.lock = threading.Lock() # Ensure thread safety

    def execute_script(self, script_name: str) -> bool:
        """
        Executes a single build script.

        Args:
            script_name: The name of the script to execute.

        Returns:
            True if the script executed successfully, False otherwise.
        """
        if script_name not in self.build_scripts:
            print(f"Error: Script '{script_name}' not found.")
            return False

        with self.lock:
            start_time = time.time()
            try:
                script_result = self.build_scripts[script_name](self.state)
                end_time = time.time()
                execution_time = (end_time - start_time) * self.time_dilation_factor
                self.time += execution_time
                self.history.append((self.time, script_name, self.state.copy()))  # Store a copy of the state
                return script_result
            except Exception as e:
                print(f"Error executing script '{script_name}': {e}")
                return False

    def run_build_sequence(self, script_sequence: List[str]) -> bool:
        """
        Executes a sequence of build scripts in the given order.

        Args:
            script_sequence: A list of script names to execute.

        Returns:
            True if all scripts executed successfully, False otherwise.
        """
        for script_name in script_sequence:
            if not self.execute_script(script_name):
                return False
        return True

    def rewind_time(self, target_time: float) -> None:
        """
        Rewinds the system to a previous state in time.

        Args:
            target_time: The time to rewind to.
        """
        with self.lock:
            if target_time >= self.time:
                print("Cannot rewind to a time in the future or the present.")
                return

            # Find the closest state in history before the target time
            closest_state = None
            closest_time = -1.0
            for timestamp, _, state in self.history:
                if timestamp <= target_time and timestamp > closest_time:
                    closest_time = timestamp
                    closest_state = state

            if closest_state is None:
                print("No state found before the target time. Resetting to initial state.")
                self.state = {}  # Reset to initial state
                self.time = 0.0
                self.history = []
            else:
                self.state = closest_state.copy()  # Restore the state
                self.time = closest_time
                # Remove history entries after the target time
                self.history = [(t, s, st) for t, s, st in self.history if t <= target_time]

            print(f"Rewound to time: {self.time}")

    def get_current_state(self) -> Dict[str, Any]:
        """
        Returns a copy of the current state of the system.
        """
        with self.lock:
            return self.state.copy()

    def get_history(self) -> List[Tuple[float, str, Dict[str, Any]]]:
        """
        Returns a copy of the build history.
        """
        with self.lock:
            return [(t, s, st.copy()) for t, s, st in self.history]

    def simulate_forward(self, duration: float, script_selection_strategy: Callable[[Dict[str, Callable[[Dict[str, Any]], bool]], Dict[str, Any]], str]) -> None:
        """
        Simulates the system forward in time for a given duration, selecting scripts based on a provided strategy.

        Args:
            duration: The duration to simulate for.
            script_selection_strategy: A function that takes the available scripts and the current state, and returns the name of the script to execute.
        """
        start_time = self.time
        while self.time - start_time < duration:
            script_name = script_selection_strategy(self.build_scripts, self.state)
            if not script_name:
                print("No script selected. Simulation halted.")
                break
            if not self.execute_script(script_name):
                print(f"Script '{script_name}' failed. Simulation halted.")
                break

    @staticmethod
    def create_random_script_selection_strategy(probability_map: Dict[str, float]) -> Callable[[Dict[str, Callable[[Dict[str, Any]], bool]], Dict[str, Any]], str]:
        """
        Creates a script selection strategy that randomly selects scripts based on a probability map.

        Args:
            probability_map: A dictionary mapping script names to their selection probabilities.  Probabilities should sum to 1.0.

        Returns:
            A script selection strategy function.
        """
        def random_script_selection(scripts: Dict[str, Callable[[Dict[str, Any]], bool]], state: Dict[str, Any]) -> str:
            script_names = list(probability_map.keys())
            probabilities = list(probability_map.values())
            return random.choices(script_names, weights=probabilities, k=1)[0]

        return random_script_selection

    @staticmethod
    def create_state_dependent_script_selection_strategy(dependency_map: Dict[str, Callable[[Dict[str, Any]], bool]], default_script: str) -> Callable[[Dict[str, Callable[[Dict[str, Any]], bool]], Dict[str, Any]], str]:
        """
        Creates a script selection strategy that selects scripts based on the current state.

        Args:
            dependency_map: A dictionary mapping script names to functions that evaluate the state and return True if the script should be executed.
            default_script: The script to execute if no other conditions are met.

        Returns:
            A script selection strategy function.
        """
        def state_dependent_script_selection(scripts: Dict[str, Callable[[Dict[str, Any]], bool]], state: Dict[str, Any]) -> str:
            for script_name, condition in dependency_map.items():
                if condition(state):
                    return script_name
            return default_script

        return state_dependent_script_selection

if __name__ == '__main__':
    # Example usage:

    def script_a(state: Dict[str, Any]) -> bool:
        print("Executing script A")
        state['a'] = True
        return True

    def script_b(state: Dict[str, Any]) -> bool:
        print("Executing script B")
        if 'a' in state and state['a']:
            state['b'] = True
            return True
        else:
            print("Script B requires script A to have been executed first.")
            return False

    def script_c(state: Dict[str, Any]) -> bool:
        print("Executing script C")
        state['c'] = random.random()
        return True

    build_scripts = {
        'script_a': script_a,
        'script_b': script_b,
        'script_c': script_c,
    }

    builder = TimeEntangledBuilder(build_scripts)

    # Run a simple sequence
    builder.run_build_sequence(['script_a', 'script_b'])
    print("Current state:", builder.get_current_state())

    # Rewind time
    builder.rewind_time(0.5)
    print("Current state after rewind:", builder.get_current_state())

    # Simulate forward with a random strategy
    random_strategy = TimeEntangledBuilder.create_random_script_selection_strategy({'script_a': 0.2, 'script_b': 0.3, 'script_c': 0.5})
    builder.simulate_forward(5.0, random_strategy)
    print("Current state after simulation:", builder.get_current_state())

    # Simulate forward with a state-dependent strategy
    def condition_for_c(state: Dict[str, Any]) -> bool:
        return 'b' in state and state['b']

    state_dependent_strategy = TimeEntangledBuilder.create_state_dependent_script_selection_strategy({'script_c': condition_for_c}, 'script_a')
    builder.simulate_forward(3.0, state_dependent_strategy)
    print("Current state after state-dependent simulation:", builder.get_current_state())

    print("Build history:", builder.get_history())